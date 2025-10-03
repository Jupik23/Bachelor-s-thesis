from app.crud.intolerances import get_all_intolerances
from app.schemas.intolerances import IntoleranceResponse
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_database

router = APIRouter(prefix="/api/v1/intolerances")

@router.get("/", response_model=List[IntoleranceResponse])
def read_intolerances(db: Session = Depends(get_database)):
    return get_all_intolerances(db = db)