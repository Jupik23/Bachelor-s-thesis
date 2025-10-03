from pydantic import BaseModel

class PreferenceBase(BaseModel):
    preference: str

class PreferenceCreate(PreferenceBase):
    pass

class PrecefenceResponce(PreferenceBase):
    id: int 

    class Config:
        from_attributes = True