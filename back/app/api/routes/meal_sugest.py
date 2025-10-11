from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.spoonacular import Spoonacular
from app.services.health_form import HealthFormService
from app.schemas.spoonacular import DailyPlanResponse, WeeklyPlanResponse

router = APIRouter(prefix="/api/v1/meals",  tags=["meals"])

@router.get("/", response_model=DailyPlanResponse | WeeklyPlanResponse)
async def generate_plan(db: Session = Depends(get_database), 
                        user: Session = Depends(get_current_user),
                        range: str = "day"):
    health_form = HealthFormService(db)
    user_form = health_form.get_health_form(user_id = user.id)
    service = Spoonacular()
    suggested_plan = await service.generate_meal_plan(health_form=user_form, time_frame=range)
    return suggested_plan