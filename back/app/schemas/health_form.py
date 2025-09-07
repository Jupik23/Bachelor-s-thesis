from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DietPreferences(BaseModel):
    diets: List[str]
 
class HealthFormCreate(BaseModel):
    height: Optional[int] = None
    weight: Optional[int] = None
    number_of_meals_per_day: Optional[int] = None
    diet_preferences: Optional[str] = None
    intolerances: Optional[str] = None
    medicament_usage: Optional[str] = None

class HealthFormResponse(HealthFormCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True