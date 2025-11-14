from pydantic import BaseModel
from typing import Optional, List, Dict

class Ingredient(BaseModel):
    id: int
    aisle: Optional[str] = None
    name: str
    original: str
    amount: float
    unit: str

class Recipe(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    imageType: Optional[str] = None

class ComplexSearchResponse(BaseModel):
    results: List[Recipe]
    offset: int
    number: int
    totalResults: int

class RecipeResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    instructions: Optional[str] = None
    readyInMinutes: Optional[int] = None
    # class Config:
    #     from_attributes = True
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