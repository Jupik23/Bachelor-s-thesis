from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DietPreferences(BaseModel):
    diets: List[str]
 
class HealthFormCreate(BaseModel):
    height: int
    weight: int
    number_of_meals_per_day: int
    diet_preferences: List[str]
    intolerances: List[str]
    medicament_usage: str

class HealthFormUpdate(BaseModel):
    height: Optional[int] = None
    weight: Optional[int] = None
    number_of_meals_per_day: Optional[int] = None
    diet_preferences: Optional[List[str]] = None
    intolerances: Optional[List[str]] = None
    medicament_usage: Optional[str] = None

class HealthFormResponse(HealthFormCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True