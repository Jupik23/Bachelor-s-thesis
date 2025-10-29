from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationStatusUpdate
from typing import Optional

def create_medication(db: Session, plan_id: int, medication_data: MedicationCreate, rxnorm_id: Optional[str]):
    new_med = Medication(
        plan_id=plan_id,
        time=medication_data.time,
        name=medication_data.name,
        with_meal_relation=medication_data.with_meal_relation,
        description=medication_data.description,
        rxnorm_id=rxnorm_id
    )
    db.add(new_med)
    db.flush()
    return new_med

def get_medications_by_plan_id(db: Session, plan_id: int):
    return db.query(Medication).filter(Medication.plan_id == plan_id).all()

def get_medication_by_id(db: Session, med_id: int):
    return db.query(Medication).filetr(Medication.id == med_id).first()

def update_medication_status(db: Session, med_id:int, updated_data: MedicationStatusUpdate):
    db_med = get_medication_by_id(db, med_id)
    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Med with {med_id} not found"
        )
    db_med.eaten = updated_data.eaten   
    db.commit()
    db.refresh(db_med)
    return db_med