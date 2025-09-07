from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user_data
from app.services.spoonacular import Spoonacular

router = APIRouter(prefix="/suggestions",  tags=["suggestions"])

@router.get("/mealplan")
async def get_mealplan()
