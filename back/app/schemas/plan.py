from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime
from app.models.common import MealType, WithMealRelation
from app.schemas.medication import MedicationResponse

class MealCreate(BaseModel):
    meal_type: MealType
    description: Optional[str] = None
    time: time
class MealResponse(MealCreate):
    id: int 
    eaten: bool
    comment: Optional[str]
    class Config:
        from_attributes = True

class ManualMealAddRequest(BaseModel):
    spoonacular_recipe_id: int
    meal_type: MealType 
    time: time 

class PlanCreate(BaseModel):
    user_id: int
    created_by: int
    medications: Optional[List[MedicationResponse]] = None 
    day_start: datetime
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_fat: Optional[float] = None
    total_carbohydrates: Optional[float] = None

class PlanResponse(PlanCreate):
    meals: List[MealResponse]
    medications: List[MedicationResponse]
    class Config:
        from_attributes = True