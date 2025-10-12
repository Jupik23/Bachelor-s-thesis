from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime
from app.models.common import MealType, WithMealRelation

class MealCreate(BaseModel):
    meal_type: MealType
    description: Optional[str]
    time: time

class MedicationCreate(BaseModel):
    pass

class PlanCreate(BaseModel):
    user_id: int
    meals = List[MealCreate]
    medications = Optional[List[MedicationCreate]] = None # need to change in future
    day_start = datetime

class MealResponse(MealCreate):
    id: int 
    eaten: bool
    comment: str
    class Config:
        from_attributes = True

class MedicationResponse(MedicationCreate):
    class Config:
        from_atributes = True
    pass

class PlanResponse(PlanCreate):
    id: int 
    class Config:
        from_attributes = True