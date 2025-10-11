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

class WeeklyPlanResponse(BaseModel):
    week: Optional[Dict[str, DailyPlanResponse]] = None