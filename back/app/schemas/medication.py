from pydantic import BaseModel
from typing import Optional, List
from datetime import time
from app.models.common import WithMealRelation
from app.schemas.drug_interaction import DrugInteractionResponse

class MedicationCreate(BaseModel):
    name: str
    time: time
    with_meal_relation: WithMealRelation
    description: str
    source: Optional[str] = "fda"
    active_substance: Optional[str] = None

class MedicationResponse(MedicationCreate):
    id: int
    taken: bool

    class Config:
        from_attributes = True
class MedicationDashboardUpdate(BaseModel):
    time: Optional[time] 
    with_meal_relation: Optional[WithMealRelation] = None

class MedicationStatusUpdate(BaseModel):
    taken: bool

class MedicationListResponse(BaseModel):
    medications: List[MedicationResponse]
    interactions: Optional[List[DrugInteractionResponse]] = None

class DrugValidationRequest(BaseModel):
    drug_name: str

class DrugValidationResponse(DrugValidationRequest):
    is_valid: bool = False

class RplDownloadStats(BaseModel):
    total_processed: int
    added: int
    errors: int