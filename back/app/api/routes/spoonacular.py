from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.schemas.health_form import HealthFormCreate
from app.services.spoonacular import Spoonacular

router = APIRouter(prefix="/api/v1/mealplan", tags=["mealplan"])

@router.post("/")
async def get_meal_plan(health_form: HealthFormCreate, input_days: int=1):
    pass


    