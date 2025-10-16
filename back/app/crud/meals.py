from sqlalchemy.orm import Session
from app.models.common import MealType
from datetime import time
from app.models.meal import Meal

def create_meal(db: Session, plan_id: int, meal_type: MealType, time: time, description: str, spoonacular_recipe_id: int = None) -> Meal:
    meal_data = Meal(
        plan_id=plan_id,
        meal_type=meal_type,
        time=time,
        description=description,
        eaten=False,
        comment=None
    )
    db.add(meal_data)
    db.commit()
    db.refresh(meal_data)
    return meal_data
    