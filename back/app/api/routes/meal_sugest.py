from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user_data
from app.services.meal_suggest import suggest_meal_for_user

router = APIRouter(prefix="/api/v1/meals",  tags=["meals"])

@router.get("/")
async def get_meal_suggestion(db: Session = Depends(get_database), count: int = 6, user = Depends(get_current_user_data)):
    results = await suggest_meal_for_user(db, user["user_id"], number_of_meals = count)
    return {"results": [r.model_dump() for r in results]}