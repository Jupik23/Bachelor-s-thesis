from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DietPreferences(BaseModel):
    diets: List[str]
    target_calories = int
    

class HealthFormCreate(BaseModel):
    height = Optional[int]
    weight = Optional[int]
    number_of_meals_per_day = Optional[int]
    diet_preferences = Optional[str]
    allergies = Optional[str]
    medicament_usage = Optional[str]

class HealthFormResponse(HealthFormCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True