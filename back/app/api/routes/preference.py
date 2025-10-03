from sqlalchemy.orm import Session
from app.crud.preferences import get_all_preferences
from app.schemas.preference import PrecefenceResponce  
from app.database.database import get_database
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix = "/api/v1/preferences")

@router.get("/", response_model = List[PrecefenceResponce])
def read_preferences(db: Session = Depends(get_database)):
    return get_all_preferences(db=db)