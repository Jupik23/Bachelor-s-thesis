from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.plan import PlanCreationService
from app.schemas.plan import PlanResponse, MealResponse, ManualMealAddRequest
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
def get_todays_plan(
    db:Session = Depends(get_database),
    user: Session = Depends(get_current_user)
):
    plan_service = PlanCreationService(db)
    try:
        plan_data = plan_service.get_todays_plan_for_user(user_id=user.id)
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