from pydantinc import BaseModel
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
    medication2: str
    severity: str
    description: str

class MedicationListResponse(BaseModel):
    mediactions: List[MedicationResponse]
    interactions: Optional[List[DrugInteractionResponse]] = None