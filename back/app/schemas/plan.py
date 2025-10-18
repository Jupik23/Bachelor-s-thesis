from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime
from app.models.common import MealType, WithMealRelation

class MealCreate(BaseModel):
    meal_type: MealType
    description: Optional[str] = None
    time: time

class MedicationCreate(BaseModel):
    pass

class MealResponse(MealCreate):
    id: int 
    eaten: bool
    comment: Optional[str]
    class Config:
        from_attributes = True

class PlanCreate(BaseModel):
    user_id: int
    created_by: int
    #medications: Optional[List[MedicationCreate]] = None # need to change in future
    day_start: datetime
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_fat: Optional[float] = None
    total_carbohydrates: Optional[float] = None

class MedicationResponse(MedicationCreate):
    class Config:
        from_atributes = True
    pass

class PlanResponse(PlanCreate):
    meals: List[MealResponse]
    class Config:
        from_attributes = True