from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.common import MealType
from datetime import time
from app.models.meal import Meal
from app.schemas.plan import MealStatusUpdate

def create_meal(db: Session, plan_id: int, meal_type: MealType, time: time, description: str, spoonacular_recipe_id: int = None) -> Meal:
    meal_data = Meal(
        plan_id=plan_id,
        meal_type=meal_type,
        time=time,
        description=description,
        eaten=False,
        comment=None,
        spoonacular_recipe_id=spoonacular_recipe_id
    )
    db.add(meal_data)
    db.commit()
    db.refresh(meal_data)
    return meal_data

def get_meal_by_id(db:Session, meal_id: int):
    return db.query(Meal).filter(Meal.id==meal_id).first()

def change_meal_status(db: Session, meal_id: int, updated_data: MealStatusUpdate):
    db_meal = get_meal_by_id(db, meal_id)

    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal {meal_id} not found"
        )
    db_meal.eaten = updated_data.eaten
    if updated_data.comment is not None:
         db_meal.comment = updated_data.comment
    elif updated_data.eaten is False: 
          db_meal.comment = None
    db.commit()
    db.refresh(db_meal)
    return db_meal