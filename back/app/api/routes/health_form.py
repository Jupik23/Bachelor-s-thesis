from app.schemas.health_form import HealthFormCreate, HealthFormUpdate, HealthFormResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.services.health_form import HealthFormService
from app.utils.jwt import get_current_user
from app.services.calculator import CalculatorService
from app.schemas.health_form import CalorieTargetResponse

router = APIRouter(prefix="/api/v1/health-form",tags=["health-form"])

@router.get("/me")
def get_user_form(db: Session = Depends(get_database), 
                  user: dict = Depends(get_current_user)):
    form = HealthFormService(db)
    if not form:
        raise HTTPException(status_code=404, detail="Health form not found")
    return form.get_health_form(user_id = user.id)

@router.put("/", response_model=HealthFormResponse)
def upsert_health_form(input: HealthFormCreate, 
                       db: Session = Depends(get_database), 
                       user: dict = Depends(get_current_user)
                       ):
    try:
        service = HealthFormService(db=db)
        existing_form = service.get_health_form( user_id=user.id)

        if existing_form:
            update_data = HealthFormUpdate(**input.dict())
            form = service.update_health_form(user_id=user.id, new_input_data=update_data)
        else:
            form = service.create_health_form(user_id=user.id, health_form_input=input)
        return form
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/calories", response_model=CalorieTargetResponse)
def count_calories(db: Session = Depends(get_database), user: dict = Depends(get_current_user)):
    health_form = HealthFormService(db)
    user_health_form = health_form.get_health_form(user_id=user.id)
    

    if not user_health_form:
        HTTPException(status_code=404,
                      detail="No Health form found in db"
                      )
    try:
        calculate = CalculatorService()
        result = calculate.get_result_for_user(health_form=user_health_form)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    