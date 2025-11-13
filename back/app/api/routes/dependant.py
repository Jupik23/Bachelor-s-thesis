from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.dependant import DependentService
from app.schemas.dependent import DependentCreateRequest
from app.schemas.user import User as UserSchema
from app.schemas.plan import PlanResponse

router = APIRouter(
    prefix="/api/v1/dependents",
    tags=["Dependents"],
    responses={404: {"description": "Not found"}},
)

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

@router.get("/{dependent_id}/plan/today", response_model=PlanResponse)
async def get_dependent_plan_today(
    dependent_id: int,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    service = DependentService(db)
    
    return await service.get_dependent_plan(
        carer_id=current_user.id,
        dependent_id=dependent_id
    )

@router.post("/{dependent_id}/plan/generate", response_model=PlanResponse)
async def generate_dependent_plan(
    dependent_id: int,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    service = DependentService(db)
    return await service.generate_dependent_plan(
        carer_id=current_user.id,
        dependent_id=dependent_id
    )