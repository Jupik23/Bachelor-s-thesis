from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.plan import PlanCreationService
from app.schemas.plan import PlanResponse, MealResponse, ManualMealAddRequest, MealStatusUpdate
from app.crud.meals import *
from typing import Optional

router = APIRouter(prefix="/api/v1/meals",  tags=["meals"])

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(db: Session = Depends(get_database), 
                        user: Session = Depends(get_current_user),
                        range: str = "day"):
    if range != "day":
         raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="In progress..."
        )

    plan_service = PlanCreationService(db)
    
    try:
        new_plan = await plan_service.generate_and_save_plan(
            user_id=user.id, 
            created_by_id=user.id, 
            time_frame=range
        )
        return new_plan
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error: {e}"
        )
    
@router.get('/today', response_model=PlanResponse) 
async def get_todays_plan(
    db:Session = Depends(get_database),
    user: Session = Depends(get_current_user)
):
    plan_service = PlanCreationService(db)
    try:
        plan_data = await plan_service.get_todays_plan_for_user(user_id=user.id)
        return plan_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while geting plan: {e}"
            )
    
@router.post(
    "/{plan_id}/meals", 
    response_model=MealResponse, 
    status_code=status.HTTP_201_CREATED,
)
async def add_meal_to_plan_manually(
    plan_id: int,
    meal_data: ManualMealAddRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user) 
):
    plan_service = PlanCreationService(db)
    
    try:
        new_meal = await plan_service.add_meal_manually(plan_id, meal_data)
        return new_meal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Błąd dodawania posiłku: {e}")
    
@router.patch("/{meal_id}", response_model=MealResponse)
async def meal_status_update(meal_id: int, updated_data: MealStatusUpdate,  
                             currtent_user: dict = Depends(get_current_user), 
                             db: Session = Depends(get_database)):
    db_meal = get_meal_by_id(db, meal_id)
    
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found"
        )
    if db_meal.plan.user_id != currtent_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this meal"
        )
    updated_meal = change_meal_status(
        db=db, 
        meal_id=meal_id, 
        updated_data=updated_data
    )
    return updated_meal