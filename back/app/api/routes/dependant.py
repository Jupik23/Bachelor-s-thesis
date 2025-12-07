from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.dependant import DependentService
from app.schemas.dependent import DependentCreateRequest
from app.schemas.user import User as UserSchema
from app.schemas.plan import PlanResponse
from pydantic import BaseModel
from app.crud.care_relation import get_dependents_by_carer_id
from app.crud.plans import get_plan_with_meals_by_user_id_and_date

router = APIRouter(
    prefix="/api/v1/dependents",
    tags=["Dependents"],
    responses={404: {"description": "Not found"}},
)

class DependentStatus(BaseModel):
    id: int
    name: str
    surname: str
    plan_status: str 
    meals_done: int
    meals_total: int
    meds_taken: int
    meds_total: int

@router.post("/create", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_dependent_account(
    request: DependentCreateRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    service = DependentService(db)
    try:
        new_dependent = service.create_dependent_account(
            carer_id=current_user.id,
            request=request
        )
        return new_dependent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wystąpił nieoczekiwany błąd: {e}"
        )

@router.get("/my", response_model=List[UserSchema])
async def get_my_dependents(
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    service = DependentService(db)
    dependents = service.get_my_dependents(carer_id=current_user.id)
    return dependents

@router.get("/{dependent_id}/plan/date/{date_str}", response_model=PlanResponse)
async def get_dependent_plan_by_date(
    dependent_id: int,
    date_str: date,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    service = DependentService(db)
    
    return await service.get_dependent_plan(
        carer_id=current_user.id,
        dependent_id=dependent_id,
        plan_date=date_str
    )

@router.post("/{dependent_id}/plan/generate", response_model=PlanResponse)
async def generate_dependent_plan(
    dependent_id: int,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    plan_date: date = Query(default_factory=date.today)
):
    service = DependentService(db)
    return await service.generate_dependent_plan(
        carer_id=current_user.id,
        dependent_id=dependent_id,
        plan_date=plan_date
    )

@router.get("/dashboard-summary", response_model=List[DependentStatus])
def get_dependents_summary(
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    dependents = get_dependents_by_carer_id(db, current_user.id)
    summary = []
    today = date.today()

    for dep in dependents:
        plan = get_plan_with_meals_by_user_id_and_date(db, dep.id, today)
        status_data = {
            "id": dep.id,
            "name": dep.name,
            "surname": dep.surname,
            "meals_done": 0,
            "meals_total": 0,
            "meds_taken": 0,
            "meds_total": 0,
            "plan_status": "No Plan"
        }
        if plan:
            meals = plan.meals
            status_data["meals_total"] = len(meals)
            status_data["meals_done"] = sum(1 for m in meals if m.eaten)
            
            meds = plan.medications
            status_data["meds_total"] = len(meds)
            status_data["meds_taken"] = sum(1 for m in meds if m.taken)
            
            if status_data["meals_total"] == 0 and status_data["meds_total"] == 0:
                status_data["plan_status"] = "Empty"
            elif (status_data["meals_done"] == status_data["meals_total"] and 
                  status_data["meds_taken"] == status_data["meds_total"]):
                status_data["plan_status"] = "Completed"
            else:
                status_data["plan_status"] = "In Progress"
        summary.append(status_data)

    return summary