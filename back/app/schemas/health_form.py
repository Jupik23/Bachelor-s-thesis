from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.common import ActivityLevel, CalorieGoal, Gender

class HealthFormCreate(BaseModel):
    height: int
    weight: int
    age: int
    gender: Gender
    activity_level: ActivityLevel
    calorie_goal: CalorieGoal
    number_of_meals_per_day: int
    diet_preferences: List[str]
    intolerances: List[str]
    medicament_usage: str
    
class HealthFormUpdate(BaseModel):
    height: Optional[int] = None
    weight: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    activity_level: Optional[ActivityLevel] = None
    calorie_goal: Optional[CalorieGoal] = None
    number_of_meals_per_day: Optional[int] = None
    diet_preferences: Optional[List[str]] = None
    intolerances: Optional[List[str]] = None
    medicament_usage: Optional[str] = None

class HealthFormResponse(HealthFormCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CalorieTargetResponse(BaseModel):
    bmr: float
    target_calories: float