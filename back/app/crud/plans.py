from app.models.plan import Plan
from app.schemas.plan import PlanCreate
from app.models.meal import Meal
from app.models.common import MealType
from datetime import time
from sqlalchemy.orm import Session

def create_plan(db: Session, plan_data: PlanCreate):
    new_plan = Plan(**plan_data.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

def create_meal(db: Session, plan_id: int, meal_type: MealType, time: time, description: str, spoonacular_recipe_id: int = None):
    db_meal = Meal(
        plan_id=plan_id,
        meal_type=meal_type,
        time=time,
        description=description,
        eaten=False, 
        comment=None,
        spoonacular_recipe_id=spoonacular_recipe_id 
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal