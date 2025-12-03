import httpx
import logging
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.schemas.medication import (MedicationCreate, MedicationResponse,
                                    MedicationListResponse, DrugValidationResponse)
from app.schemas.drug_interaction import (DrugInteractionCreate, DrugInteractionResponse)
from app.crud.medication import create_medication
from app.crud.drug_interaction import get_interaction, create_new_drug_interaction
from app.models.common import WithMealRelation
from app.services.rpl_service import RPLService

class DrugInteractionService:
    def __init__(self, db: Session, fda_api_key: Optional[str]):
        self.db = db
        self.openfda_base = "https://api.fda.gov/drug"
        self.api_key = fda_api_key

    async def _make_request(self, url: str, params: Dict[str, Any] = None):
        if params is None:
            params = {}
        if self.api_key and 'api_key' not in params:
            params['api_key'] = self.api_key
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                logging.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
                return None
            except Exception as e:
                logging.error(f"Request error: {str(e)}")
                return None

    async def validate_drug_name(self, drug_name: str) -> bool:
        endpoint = f"{self.openfda_base}/label.json"
        search_queries = [
            f'openfda.brand_name:"{drug_name}"', f'openfda.generic_name:"{drug_name}"',
            f'openfda.brand_name:{drug_name}', f'openfda.generic_name:{drug_name}'
        ]
        
        for search_query in search_queries:
            data = await self._make_request(endpoint, params={"search": search_query, "limit": 1})
            if data and data.get('results'):
                return True
        return False
    
    async def _get_drug_label_info(self, drug_name: str) -> Optional[Dict]:
        endpoint = f"{self.openfda_base}/label.json"
        search_queries = [
            f'openfda.brand_name:"{drug_name}"', f'openfda.generic_name:"{drug_name}"',
            f'openfda.brand_name:{drug_name}', f'openfda.generic_name:{drug_name}'
        ]
        
        for search_query in search_queries:
            data = await self._make_request(endpoint, params={"search": search_query, "limit": 1})
            if data and data.get('results'):
                return data['results'][0]
        return None
    
    async def _check_interaction_in_label(self, drug_name: str, other_drug_name: str) -> Optional[str]:
        label_data = await self._get_drug_label_info(drug_name)
        if not label_data:
            return None
        
        sections = ['drug_interactions', 'warnings', 'precautions', 'boxed_warning', 'warnings_and_cautions']
        other_drug_lower = other_drug_name.lower()
        
        for section in sections:
            if section in label_data:
                content = label_data[section]
                if isinstance(content, list):
                    content = ' '.join(content)
                
                if isinstance(content, str) and other_drug_lower in content.lower():
                    sentences = content.split('.')
                    for sentence in sentences:
                        if other_drug_lower in sentence.lower():
                            return sentence.strip()[:300]
        return None

    async def check_drug_interaction(self, drug_names: List[str]) -> List[DrugInteractionResponse]:
        if len(drug_names) < 2:
            return []
        
        interactions_list = []
        checked_pairs = set()
        
        for i in range(len(drug_names)):
            for j in range(i + 1, len(drug_names)):
                drug1, drug2 = drug_names[i], drug_names[j]
                pair_key = tuple(sorted([drug1.lower(), drug2.lower()]))
                
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                db_interaction = get_interaction(db=self.db, drug1=drug1, drug2=drug2)
                if not db_interaction:
                    try:
                        api_result = await self._fetch_interaction_from_api(drug1=drug1, drug2=drug2)
                        db_interaction = create_new_drug_interaction(db=self.db, interaction_data=api_result)
                        self.db.flush()
                    except Exception as e:
                        logging.error(f"Failed to fetch interaction: {e}")
                        continue
                
                if db_interaction and db_interaction.description:
                    interactions_list.append(DrugInteractionResponse(
                        medication_1=db_interaction.drug1,
                        medication_2=db_interaction.drug2,
                        severity=db_interaction.severity,
                        description=db_interaction.description
                    ))
        return interactions_list
    
    def _analyze_meal_timing(self, description: str) -> WithMealRelation:
        if not description or len(description.strip()) < 5:
            return WithMealRelation.unknown
        
        desc = description.lower()
        timing_scores = {'empty_stomach': 0, 'before': 0, 'during': 0, 'after': 0}
        
        empty_stomach_patterns = {
            'on an empty stomach': 100, 'empty stomach': 100, 'do not take with food': 100,
            'must not be taken with food': 95, 'food decreases absorption': 80, 'fasting': 70,
            'absorption decreased by food': 80, 'take on empty': 60, 'without food': 85
        }
        before_patterns = {
            '1 hour before meals': 100, 'one hour before meals': 100, '30 minutes before meals': 95,
            'at least 1 hour before': 95, 'before meals': 80, 'before eating': 80, 'prior to meals': 75,
            'morning before breakfast': 80, 'take before': 70
        }
        during_patterns = {
            'with food': 100, 'with meals': 100, 'take with food': 95, 'should be taken with food': 95,
            'during meals': 85, 'with breakfast': 85, 'with dinner': 85, 'food increases absorption': 75,
            'to minimize stomach upset': 65, 'with fatty meal': 80
        }
        after_patterns = {
            '2 hours after meals': 100, 'two hours after meals': 100, '1 hour after meals': 95,
            'after meals': 80, 'after eating': 80, 'following meals': 75, 'post-meal': 70
        }
        
        all_patterns = [
            (empty_stomach_patterns, 'empty_stomach'), (before_patterns, 'before'),
            (during_patterns, 'during'), (after_patterns, 'after')
        ]
        
        for patterns_dict, category in all_patterns:
            sorted_patterns = sorted(patterns_dict.items(), key=lambda x: len(x[0]), reverse=True)
            for pattern, points in sorted_patterns:
                if pattern in desc:
                    timing_scores[category] += points

        if 'do not take with food' in desc or 'avoid taking with food' in desc:
            timing_scores['during'] = 0
            timing_scores['after'] = 0
        if timing_scores['empty_stomach'] >= 80:
            timing_scores['before'] = 0

        context_bonuses = [
            (['absorption', 'decreased', 'food'], 'empty_stomach', 30),
            (['absorption', 'increased', 'food'], 'during', 30),
            (['stomach', 'upset'], 'during', 20),
            (['hour', 'before'], 'before', 15),
            (['hour', 'after'], 'after', 15),
        ]
        for keywords, category, bonus in context_bonuses:
            if all(kw in desc for kw in keywords):
                timing_scores[category] += bonus

        max_score = max(timing_scores.values())
        if max_score < 50:
            return WithMealRelation.unknown
            
        winner = max(timing_scores.items(), key=lambda x: x[1])[0]
        mapping = {
            'empty_stomach': WithMealRelation.empty_stomach, 'before': WithMealRelation.before,
            'during': WithMealRelation.during, 'after': WithMealRelation.after
        }
        return mapping.get(winner, WithMealRelation.unknown)

    async def get_medication_timing(self, med_name: str) -> WithMealRelation:
        label_data = await self._get_drug_label_info(drug_name=med_name)
        if not label_data:
            return WithMealRelation.unknown
            
        priority_sections = [
            'dosage_and_administration', 'patient_counseling_information', 
            'instructions_for_use', 'how_supplied', 'clinical_pharmacology'
        ]
        description_parts = []
        for section in priority_sections:
            if section in label_data:
                content = label_data[section]
                if isinstance(content, list):
                    description_parts.extend(content)
                elif isinstance(content, str):
                    description_parts.append(content)
                    
        return self._analyze_meal_timing(" ".join(description_parts))
        
    def _determine_severity(self, description: str) -> str:
        if not description or len(description.strip()) < 10:
            return "Unknown"
        
        description_lower = description.lower()
        risk_score = 0
        
        critical_patterns = {
            'contraindicated': 100, 'do not use together': 100, 'must not be used': 100,
            'life-threatening': 100, 'fatal': 90, 'death': 90, 'cardiac arrest': 100,
            'anaphylaxis': 90, 'severe bleeding': 85, 'hemorrhage': 80, 'stroke': 80
        }
        high_risk_patterns = {
            'significant interaction': 60, 'serious': 65, 'severe': 70, 'avoid': 60,
            'should not': 55, 'increased bleeding': 70, 'seizure': 65, 'liver damage': 70,
            'kidney damage': 70, 'renal failure': 75, 'significantly increases': 55
        }
        moderate_risk_patterns = {
            'monitor': 30, 'caution': 25, 'use with caution': 30, 'may increase': 25,
            'may decrease': 25, 'dose adjustment': 35, 'reduced effectiveness': 30
        }
        low_risk_patterns = {'minor': 10, 'mild': 10, 'unlikely': 5, 'possible': 10}
        
        all_patterns = {**critical_patterns, **high_risk_patterns, **moderate_risk_patterns, **low_risk_patterns}
        sorted_patterns = sorted(all_patterns.items(), key=lambda x: len(x[0]), reverse=True)
        
        for pattern, points in sorted_patterns:
            if pattern in description_lower:
                risk_score += points
                
        danger_combinations = [
            (['bleeding', 'anticoagulant'], 30), (['bleeding', 'nsaid'], 25),
            (['prolonged', 'qt'], 40), (['serotonin', 'syndrome'], 50)
        ]
        for keywords, bonus in danger_combinations:
            if all(k in description_lower for k in keywords):
                risk_score += bonus
                
        if risk_score >= 100: return "Critical"
        if risk_score >= 50: return "High"
        if risk_score >= 20: return "Moderate"
        if risk_score >= 1: return "Low"
        return "Unknown"
    
    async def _fetch_interaction_from_api(self, drug1: str, drug2: str):
        desc1 = await self._check_interaction_in_label(drug1, drug2)
        desc2 = await self._check_interaction_in_label(drug2, drug1)
        description = desc1 or desc2

        if description:
            return DrugInteractionCreate(
                drug1=drug1, drug2=drug2, 
                severity=self._determine_severity(description), description=description
            )
        return DrugInteractionCreate(
            drug1=drug1, drug2=drug2, severity="None", description=None
        )
        
    async def search_medications(self, query: str, limit: int = 5):
        if not query or len(query) < 2:
            return []
        
        endpoint = f"{self.openfda_base}/label.json"
        search_query = f'(openfda.brand_name:"{query}*" OR openfda.generic_name:{query}*)'
        data = await self._make_request(endpoint, {"search": search_query, "limit": limit})
        
        results = []
        if data and "results" in data:
            for item in data['results']:
                if 'openfda' in item:
                    results.extend(item['openfda'].get('brand_name', []))
                    results.extend(item['openfda'].get('generic_name', []))
                    
        clean_result = sorted(list(set(
            [r.title() for r in results if r.lower().startswith(query.lower())]
        )))[:limit]
        return clean_result

class MedicationService:
    def __init__(self, db: Session):
        self.db = db 
        self.interaction_checker = DrugInteractionService(db=self.db, fda_api_key=os.getenv("OPEN_FDA_API_KEY"))
        self.rpl_service = RPLService(db=self.db)

    async def add_medications_to_plan(self, plan_id: int, medications_data: List[MedicationCreate]):
        saved_medications = []
        interaction_check_names = []
        substance_to_trade_name = {}

        for med_data in medications_data:
            active_substance = self.rpl_service.get_active_substance(med_data.name) 
            api_search_name = active_substance if active_substance else med_data.name
            
            substance_to_trade_name[api_search_name] = med_data.name
            interaction_check_names.append(api_search_name)
            
            timing = await self.interaction_checker.get_medication_timing(api_search_name)
            
            med_dict = med_data.model_dump()
            if med_dict.get('with_meal_relation') == WithMealRelation.unknown and timing != WithMealRelation.unknown:
                med_dict['with_meal_relation'] = timing
            
            if not med_dict.get('description') and active_substance:
                med_dict['description'] = f"Substancja czynna: {active_substance}"

            db_med = create_medication(
                self.db, plan_id=plan_id, medication_data=MedicationCreate(**med_dict)
            )
            saved_medications.append(MedicationResponse.model_validate(db_med))
            
        self.db.flush()

        interactions_response = await self.interaction_checker.check_drug_interaction(drug_names=interaction_check_names)
        
        for interaction in interactions_response:
            trade1 = substance_to_trade_name.get(interaction.medication_1, interaction.medication_1)
            trade2 = substance_to_trade_name.get(interaction.medication_2, interaction.medication_2)
            
            note = ""
            if trade1 != interaction.medication_1:
                note += f" ({trade1} zawiera {interaction.medication_1})"
            if trade2 != interaction.medication_2:
                note += f" ({trade2} zawiera {interaction.medication_2})"
            
            if note:
                interaction.description = (interaction.description or "") + f" [Dotyczy: {note}]"

        self.db.commit() 
        
        return MedicationListResponse(medications=saved_medications, interactions=interactions_response)
    
    async def validate_drug(self, drug_name: str):
        if self.rpl_service.get_exact_medication(drug_name):
            return DrugValidationResponse(drug_name=drug_name, is_valid=True)

        try:
            is_valid = await self.interaction_checker.validate_drug_name(drug_name)
            return DrugValidationResponse(drug_name=drug_name, is_valid=is_valid)
        except Exception as e:
            logging.error(f"Drug validation failed: {e}")
            return DrugValidationResponse(drug_name=drug_name, is_valid=False)

    async def search_drug(self, query: str):
        rpl_results = self.rpl_service.search_polish_medications(query, limit=10)
        clean_rpl = [r.split(" || ")[0] for r in rpl_results]
        
        fda_results = await self.interaction_checker.search_medications(query, limit=5)
        
        combined = sorted(list(set(clean_rpl + fda_results)))
        return combined[:15]