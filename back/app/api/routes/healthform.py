from app.schemas.health_form import HealthFormCreate, HealthFormResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.services.healthform import HealthFormService

router = APIRouter(prefix="/api/v1/health-form",tags=["health-form"])

# @router.get("/")
# def get_users_form(db: Session = Depends(get_database)):
#     return HealthFormService(db)

@router.post("/", response_model= HealthFormResponse)
def create_health_form(input: HealthFormCreate, db:Session = Depends(get_database), user_id: int = 1):
    try:
        service = HealthFormService(db)
        form = service.create_health_form(input, user_id=user_id)
        return form
    except Exception as e:
        raise HTTPException(status_code = 400, detail=str(e))
        