from pydantic import BaseModel

class IntoleranceBase(BaseModel):
    intolerance: str

class IntoleranceCreate(IntoleranceBase):
    pass

class IntoleranceResponse(IntoleranceBase):
    id: int

    class Config:    
        from_attributes = True