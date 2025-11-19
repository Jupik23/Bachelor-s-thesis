from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict

class Ingredient(BaseModel):
    id: int
    aisle: Optional[str] = None
    name: str
    original: Optional[str] = None
    amount: float
    unit: str
    class Config:
        from_atributes=True

class Nutrients(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float
class Recipe(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    imageType: Optional[str] = None
    readyInMinutes: Optional[int] = None
    servings: Optional[int] = None
    sourceUrl: Optional[str] = None
    class Config:
        from_atributes=True

class ComplexSearchResponse(BaseModel):
    results: List[Recipe]
    totalResults: int
    offset: Optional[int] = 0
    number: Optional[int] = 0
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class RecipeResponse(Recipe):
    summary: Optional[str] = None
    instructions: Optional[str] = None
    extendedIngredients: Optional[List[Ingredient]] = []
    vegan: bool = False
    glutenFree: bool = False
    dairyFree: bool = False
    class Config:
        from_atributes=True
class DailyPlanResponse(BaseModel):
    meals: List[Recipe]
    nutrients: Nutrients
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_fat: Optional[float] = None
    total_carbohydrates: Optional[float] = None
    class Config:
        from_atributes=True

class WeeklyPlanResponse(BaseModel):
    week: Dict[str, DailyPlanResponse]
    class Config:
        from_atributes=True