from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.jwt import get_current_user
from app.crud.medication import *
from app.crud.care_relation import check_relation
from app.database.database import get_database
from app.schemas.medication import (MedicationCreate, MedicationListResponse,
                                    DrugValidationRequest, DrugValidationResponse,
                                    MedicationResponse, MedicationStatusUpdate,
                                    MedicationDashboardUpdate)
from app.services.medication_service import MedicationService
from app.services.notification import NotificationService
from app.schemas.notification import NotificationCreate
from app.crud.care_relation import get_carer_by_patient_id
from app.crud.notification import create_new_notification
from typing import List
import logging

router = APIRouter(prefix="/api/v1/medications", tags=["medications"])

@router.post(
    "/validate", 
    response_model=DrugValidationResponse,
    status_code=status.HTTP_200_OK
)
async def validate_new_drug(request: DrugValidationRequest, db: Session = Depends(get_database)):
    medication_service = MedicationService(db)
    return await medication_service.validate_drug(request.drug_name)


@router.post(
    "/{plan_id}", 
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

@router.patch("/{medication_id}", response_model=MedicationResponse)
async def edit_medication_details(
    medication_id: int,
    medication_data: MedicationDashboardUpdate,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):

    db_med = get_medication_by_id(db, medication_id)

    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    is_owner = db_med.plan.user_id == current_user.id
    is_carer = False
    if not is_owner:
        is_carer = check_relation(db=db, carer_id=current_user.id, patient_id=db_med.plan.user_id)
    if not is_owner and not is_carer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this medication"
        )

    updated_med = update_medication_dashboard(
        db, med_id=medication_id, update_data=medication_data
    )
    return updated_med

@router.patch("/{medication_id}/medication", response_model=MedicationResponse)
async def update_medication_status_endpoint(
    medication_id: int,
    update_data: MedicationStatusUpdate,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    db_medication = get_medication_by_id(db, medication_id)
    if not db_medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication with id {medication_id} not found"
        )
    is_owner = db_medication.plan.user_id == current_user.id
    is_carer = False
    if not is_owner:
        is_carer = check_relation(db=db, carer_id=current_user.id, patient_id=db_medication.plan.user_id)
    if not is_owner and not is_carer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this medication"
        )
    updated_medication =update_medication_status(
        db=db, 
        med_id=medication_id, 
        updated_data=update_data
    )
    if is_owner:
        try:
            carrer = get_carer_by_patient_id(db=db, patient_id=current_user.id)
            if carrer:
                status_text = "taken" if update_data.taken else "marked as not taken"
                patient_name = current_user.name
                message = f"{patient_name} {status_text} - {db_medication.name}"
                notification_data = NotificationCreate(
                    user_id = carrer.id,
                    related_user_id=current_user.id,
                    type="medication_status_update",
                    message=message
                )
                create_new_notification(db, notification_data)
        except Exception as e:
            logging.error(f"Failed to create notification {e}")
    return updated_medication