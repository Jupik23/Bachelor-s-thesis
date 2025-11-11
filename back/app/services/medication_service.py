import httpx
import logging
from sqlalchemy.orm import Session
from app.schemas.medication import (MedicationCreate, 
                                    DrugInteractionResponse, MedicationResponse,
                                    MedicationListResponse, DrugValidationResponse)
from app.crud.medication import create_medication, get_medications_by_plan_id
from app.database.database import get_database
from typing import List, Dict, Any, Optional
import os

class DrugInteractionService:
    def __init__(self, fda_api_key: Optional[str]):
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
                    logging.debug(f"No FDA data found for query: {params.get('search', 'unknown')}")
                    return None
                logging.error(f"HTTP Error {e.response.status_code} dla {url}: {e.response.text}")
                return None
            except Exception as e:
                logging.error(f"Request error: {str(e)}")
                return None

    async def validate_drug_name(self, drug_name: str) -> bool:
        endpoint = f"{self.openfda_base}/label.json"

        search_queries = [
            f'openfda.brand_name:"{drug_name}"',
            f'openfda.generic_name:"{drug_name}"',
            f'openfda.brand_name:{drug_name}',
            f'openfda.generic_name:{drug_name}'
        ]
        
        for search_query in search_queries:
            params = {
                "search": search_query,
                "limit": 1
            }
            
            data = await self._make_request(endpoint, params=params)
            if data and data.get('results'):
                return True
        
        return False
    
    async def _get_drug_label_info(self, drug_name: str) -> Optional[Dict]:
        """Pobiera informacje o leku z OpenFDA Drug Label endpoint"""
        endpoint = f"{self.openfda_base}/label.json"
        
        search_queries = [
            f'openfda.brand_name:"{drug_name}"',
            f'openfda.generic_name:"{drug_name}"',
            f'openfda.brand_name:{drug_name}',
            f'openfda.generic_name:{drug_name}'
        ]
        
        for search_query in search_queries:
            params = {
                "search": search_query,
                "limit": 1
            }
            
            data = await self._make_request(endpoint, params=params)
            if data and data.get('results'):
                return data['results'][0]
        
        return None
    
    async def _check_interaction_in_label(self, drug_name: str, other_drug_name: str) -> Optional[str]:
        label_data = await self._get_drug_label_info(drug_name)
        
        if not label_data:
            return None
        
        sections_to_check = [
            'drug_interactions',
            'warnings',
            'precautions',
            'boxed_warning',
            'warnings_and_cautions'
        ]
        
        other_drug_lower = other_drug_name.lower()
        
        for section in sections_to_check:
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
                drug1 = drug_names[i]
                drug2 = drug_names[j]
                
                pair_key = tuple(sorted([drug1.lower(), drug2.lower()]))
                if pair_key in checked_pairs:
                    continue
                
                checked_pairs.add(pair_key)
                interaction_desc_1 = await self._check_interaction_in_label(drug1, drug2)
                interaction_desc_2 = await self._check_interaction_in_label(drug2, drug1)
                if interaction_desc_1 or interaction_desc_2:
                    description = interaction_desc_1 or interaction_desc_2
                    
                    severity = self._determine_severity(description)
                    
                    interactions_list.append(DrugInteractionResponse(
                        medication_1=drug1,
                        medication_2=drug2,
                        severity=severity,
                        description=description or 'Możliwa interakcja między lekami. Skonsultuj się z lekarzem.'
                    ))
        
        return interactions_list
    
    def _determine_severity(self, description: str) -> str:
        if not description:
            return "Unknown"
        
        description_lower = description.lower()
        
        high_risk_keywords = [
            'contraindicated', 'severe', 'serious', 'fatal', 'death',
            'life-threatening', 'emergency', 'immediately', 'avoid',
            'do not', 'should not', 'must not'
        ]
        
        moderate_risk_keywords = [
            'caution', 'monitor', 'may increase', 'may decrease',
            'adjust dose', 'careful', 'warning', 'consider'
        ]
        
        for keyword in high_risk_keywords:
            if keyword in description_lower:
                return "High"
        
        for keyword in moderate_risk_keywords:
            if keyword in description_lower:
                return "Moderate"
        
        return "Low"


class MedicationService:
    def __init__(self, db: Session):
        self.db = db
        fda_key = os.getenv("OPEN_FDA_API_KEY")
        self.interaction_checker = DrugInteractionService(fda_api_key=fda_key)

    async def add_medications_to_plan(
            self, 
            plan_id: int,
            medications_data: List[MedicationCreate]
    ):
        
        saved_medications: List[MedicationResponse] = []
        medication_names: List[str] = []

        for med_data in medications_data:
            db_med = create_medication(
                self.db, 
                plan_id=plan_id,
                medication_data=med_data,
            )
            saved_medications.append(MedicationResponse.model_validate(db_med))
            medication_names.append(med_data.name)

        interactions = await self.interaction_checker.check_drug_interaction(medication_names)
        
        self.db.commit() 
        
        return MedicationListResponse(
            medications=saved_medications, 
            interactions=interactions
        )
    
    async def validate_drug(self, drug_name: str):
        try:
            is_valid = await self.interaction_checker.validate_drug_name(drug_name)
            
            return DrugValidationResponse(
                drug_name=drug_name,
                is_valid=is_valid,
            )
        except Exception as e:
            logging.error(f"Drug validation failed due to API error: {e}")
            return DrugValidationResponse(
                drug_name=drug_name,
                is_valid=False,
            )