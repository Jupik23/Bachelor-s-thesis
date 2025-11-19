import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.plan import PlanCreationService
from app.schemas.plan import PlanResponse, MealResponse, ManualMealAddRequest, MealStatusUpdate, MealUpdate
from app.schemas.spoonacular import ComplexSearchResponse
from app.schemas.shopping_list import ShoppingListResponse
from app.crud.care_relation import get_carer_by_patient_id
from app.crud.notification import create_new_notification
from app.schemas.notification import NotificationCreate
from app.crud.meals import get_meal_by_id, change_meal_status, change_meal_time_or_type
import logging
from datetime import date

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])

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
    try:
        carrer = get_carer_by_patient_id(db=db, patient_id=currtent_user.id)
        if carrer:
            meal_status_text = "eaten" if updated_data.eaten else "marked as not eaten"
            patient_name = currtent_user.name
            desc_preview = db_meal.description.split('.')[0] if db_meal.description else "Meal"
            message = f"{patient_name} {meal_status_text} '{desc_preview}'."
            if updated_data.comment:
                message += f" Comment: \"{updated_data.comment}\""
            notification_data = NotificationCreate(
                    user_id = carrer.id,
                    related_user_id=currtent_user.id,
                    type= "meal_status_update",
                    message=message
                )
            create_new_notification(db, notification_data)
    except Exception as e:
        logging.error(f"Failed to create notification for carrer")
            
    return updated_meal

@router.get("/shopping-list", response_model=ShoppingListResponse)
async def get_shopping_list_for_today(db: Session = Depends(get_database),
                                      current_user: dict = Depends(get_current_user)):
    plan_service = PlanCreationService(db=db)
    try:
        shopping_list = await plan_service.get_shopping_list_for_user(
            user_id=current_user.id,
            plan_date=date.today()
        )
        return shopping_list
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spoonacular error: {e.response.text}"
        )
    except Exception as e:
        logging.error(f"Error generating shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate shopping list."
        )

@router.patch("/{meal_id}/details", response_model =MealResponse)
async def edit_meal_details(
    meal_id: int,
    new_data: MealUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    meal = get_meal_by_id(db=db, meal_id=meal_id)
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    if meal.plan.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="That's not your meal!")
    updated_data = change_meal_time_or_type(db, meal_id, new_data)
    return updated_data

@router.get("/search", response_model=ComplexSearchResponse)
async def search_new_recipes_with_user_preferences(
    query:str, 
    db: Session = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    service = PlanCreationService(db)
    try:
        return await service.search_alternative_recipie(user_id = user.id, query= query) 
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put("/{meal_id}/replace", response_model=MealResponse)
async def replace_meal_in_plan(
    meal_id: int,
    request_data: ManualMealAddRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
    ):
    service = PlanCreationService(db)
    db_meal = get_meal_by_id(db, meal_id=meal_id)
    if not db_meal or db_meal.plan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized or meal not found")
    
    try:
        new_meal = await service.replace_meal(meal_id=meal_id,
                                              new_meal_id=request_data.spoonacular_recipe_id)
        return new_meal
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))