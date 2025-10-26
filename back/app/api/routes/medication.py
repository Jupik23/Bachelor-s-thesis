from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.medication import MedicationCreate, MedicationListResponse
from app.services.medication_service import MedicationService
from typing import List

router = APIRouter(prefix="/api/v1/plans", tags=["medications"])

@router.post(
    "/{plan_id}/medications", 
    response_model=MedicationListResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_medications_to_plan(
    plan_id: int,
    medications: List[MedicationCreate],
    db: Session = Depends(get_database),
):
    if not medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista leków nie może być pusta."
        )

    medication_service = MedicationService(db)
    
    try:
        result = await medication_service.add_medications_to_plan(plan_id, medications)
        return result
        
    except Exception as e:
        print(f"CRITICAL ERROR in add_medications_to_plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while adding meds: {e}"
        )