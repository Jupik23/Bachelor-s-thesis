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
        self.rxnav_base = "https://rxnav.nlm.nih.gov/REST"
        self.opnefda_base = "https://api.fda.gov/drug/event.json"
        self.api_key = fda_api_key

    async def _make_request(self, url: str, params: Dict[str, Any] = None):
        if params is None:
            params = {}
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP Error {e.response.status_code} dla {url}: {e.response.text}")
                return None
            except Exception as e:
                logging.error(f"Request error: {str(e)}")
                raise 

    async def get_rxnorm_id(self, drug_name: str):
        endpoint = f"{self.rxnav_base}/rxcui.json"
        data = await self._make_request(endpoint, params={"name": drug_name})

        if (data and data.get('idGroup') and 
            data['idGroup'].get('rxnormId') and 
            data['idGroup']['rxnormId']):

            return str(data['idGroup']['rxnormId'][0])
        
        logging.error(f"No rxcui for: {drug_name}")
        return None
    
    async def check_drug_interaction(self, rxnorm_ids: List[str]):
        if len(rxnorm_ids)<2:
            return []
        
        rxcui_list = "+".join(rxnorm_ids)
        endpoint = f"{self.rxnav_base}/interaction/list.json"
        params = {"rxcuis": rxcui_list, "allSources": 1}
        data = await self._make_request(endpoint, params=params)
        
        interactions_list = []

        if data and data.get('fullInteractionTypeGroup'):
            
            for group in data.get('fullInteractionTypeGroup', []):
                for interaction_type in group.get('fullInteractionType', []):
                    for pair in interaction_type.get('interactionPair', []):

                        drug1_name = pair['interactionConcept'][0]['minConceptItem']['name']
                        drug2_name = pair['interactionConcept'][1]['minConceptItem']['name']

                        interactions_list.append(DrugInteractionResponse(
                            medication_1=drug1_name,
                            medication_2=drug2_name,
                            severity=pair.get('severity', 'Unknown'),
                            description=pair.get('description', 'Brak szczegółowego opisu.')
                        ))
                        
        return interactions_list
    

class MedicationService:
    def __init__(self, db: Session):
        self.db = db
        fda_key = os.getenv("OPEN_FDA_API_KEY")
        self.interaction_checker = DrugInteractionService(fda_api_key=fda_key)

    async def add_medications_to_plan(
            self, 
            plan_id:int,
            medications_data: List[MedicationCreate]
    ):
        
        saved_medications: List[MedicationResponse] = []
        medication_names: List[str] = []
        rxnorm_ids: List[str] = []

        for med_data in medications_data:
            rx_id = await self.interaction_checker.get_rxnorm_id(med_data.name)
            db_med = create_medication(self.db, plan_id=plan_id,
                                        medication_data=med_data,
                                        rxnorm_id = rx_id)
            saved_medications.append(MedicationResponse.model_validate(db_med))
            medication_names.append(med_data.name)
            if rx_id:
                rxnorm_ids.append(rx_id)

        all_meds_in_plan = get_medications_by_plan_id(self.db, plan_id)
        all_rxnorm_ids_in_plan = [m.rxnorm_id for m in all_meds_in_plan if m.rxnorm_id]
        
        interactions = await self.interaction_checker.check_drug_interaction(
            list(set(all_rxnorm_ids_in_plan))
        )
        
        self.db.commit() 
        
        return MedicationListResponse(
            medications=saved_medications, 
            interactions=interactions
        )
    
    async def validate_drug(self, drug_name):
        try:
            rx_id = await self.interaction_checker.get_rxnorm_id(drug_name)
            is_valid  = rx_id is not None
            return DrugValidationResponse(
                drug_name=drug_name,
                is_valid=is_valid,
                rxnorm_id=rx_id
            )
        except Exception as e:
            logging.error(f"Drug validation failed due to API error: {e}")
            return DrugValidationResponse(
                drug_name=drug_name,
                is_valid=False,
                rxnorm_id=None
            )