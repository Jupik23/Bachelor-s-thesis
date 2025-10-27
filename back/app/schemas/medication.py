from pydantic import BaseModel
from typing import Optional, List
from datetime import time
from app.models.common import WithMealRelation

class MedicationCreate(BaseModel):
    name: str
    time: time
    with_meal_relation: WithMealRelation
    description: str

class MedicationResponse(MedicationCreate):
    id: int
    taken: bool

    class Config:
        from_attributes = True

class DrugInteractionResponse(BaseModel):
    medication_1: str
    medication_2: str
    severity: str
    description: str

class MedicationListResponse(BaseModel):
    medications: List[MedicationResponse]
    interactions: Optional[List[DrugInteractionResponse]] = None

class DrugValidationRequest(BaseModel):
    drug_name: str

class DrugValidationResponse(DrugValidationRequest):
    is_valid: bool = False
    rxnorm_id: Optional[str] = None