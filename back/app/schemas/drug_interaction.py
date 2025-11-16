from pydantic import BaseModel
from typing import Optional

class DrugInteractionBase(BaseModel):
    drug1: str
    drug2: str
    description: Optional[str] = None
    severity: str

class DrugInteractionCreate(DrugInteractionBase):
    pass

class DrugInteractionResponse(DrugInteractionBase):
    id: int
    class Config:
        from_atributes = True