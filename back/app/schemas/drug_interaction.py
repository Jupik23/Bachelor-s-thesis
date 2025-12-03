from pydantic import BaseModel
from typing import Optional

class DrugInteractionBase(BaseModel):
    drug1: str
    drug2: str
    description: Optional[str] = None
    severity: str

class DrugInteractionCreate(DrugInteractionBase):
    pass

class DrugInteractionResponse(BaseModel):
    medication_1: str
    medication_2: str
    description: str
    severity: str
class DrugInDB(DrugInteractionBase):
    id: int
    class Config:
        from_attributes = True