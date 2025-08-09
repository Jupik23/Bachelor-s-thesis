from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthFormBase(BaseModel):
    height = Optional[int]
    weight = Optional[int]
    number_of_meals_per_day = Optional[int]
    diet_preferences = Optional[str]
    allergies = Optional[str]
    medicament_usage = Optional[str]

class HealtFormCreate(HealthFormBase):
    pass

class HeathFormEdit(HealthFormBase):
    pass

class HealthFormResponse(HealthFormBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True