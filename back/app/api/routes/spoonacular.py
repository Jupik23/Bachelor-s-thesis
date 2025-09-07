from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.schemas.health_form import HealthFormCreate
from app.services.spoonacular import Spoonacular

router = APIRouter()

@router.post("/mealplan")
async def get_meal_plan(health_form: HealthFormCreate, days: int=1):
    client = Spoonacular()
    meal_plans = await client.generate_meal_plan(
        health_form=health_form,
        days = 7,
    )
    return {"meal_plans": meal_plans}