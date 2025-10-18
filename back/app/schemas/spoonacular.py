from pydantic import BaseModel
from typing import Optional, List, Dict

class Recipe(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    image: Optional[str] = None
    sourceUrl: Optional[str] = None
    readyInMinutes: Optional[int] = None
    servings: Optional[int] = None

class Nutrients(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float

class DailyPlanResponse(BaseModel):
    meals: List[Recipe]
    nutrients: Nutrients
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_fat: Optional[float] = None
    total_carbohydrates: Optional[float] = None

class WeeklyPlanResponse(BaseModel):
    week: Optional[Dict[str, DailyPlanResponse]] = None