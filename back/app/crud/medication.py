from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.medication import Medication
from app.models.common import WithMealRelation
from app.schemas.medication import MedicationCreate, MedicationStatusUpdate, MedicationDashboardUpdate
from typing import Optional

def create_medication(db: Session, plan_id: int, medication_data: MedicationCreate):
    new_med = Medication(
        plan_id=plan_id,
        time=medication_data.time,
        name=medication_data.name,
        with_meal_relation=medication_data.with_meal_relation,
        description=medication_data.description,
    )
    db.add(new_med)
    db.flush()
    return new_med

def get_medications_by_plan_id(db: Session, plan_id: int):
    return db.query(Medication).filter(Medication.plan_id == plan_id).all()

def get_medication_by_id(db: Session, med_id: int):
    return db.query(Medication).filter(Medication.id == med_id).first()

def update_medication_status(db: Session, med_id:int, updated_data: MedicationStatusUpdate):
    db_med = get_medication_by_id(db, med_id)
    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Med with {med_id} not found"
        )
    db_med.taken = updated_data.taken   
    db.commit()
    db.refresh(db_med)
    return db_med

def update_medication_dashboard(db: Session, med_id: int, update_data: MedicationDashboardUpdate):
    medication_to_change = get_medication_by_id(db=db, med_id=med_id)
    if not medication_to_change:
        return None
    update_dict = update_data.model_dump(exclude_unset=True)
    if "with_meal_relation" in update_dict:
        new_relation_enum = update_dict["with_meal_relation"]
        relation_map = {
            WithMealRelation.empty_stomach: "on an empty stomach",
            WithMealRelation.before: "before meal",
            WithMealRelation.during: "during meal",
            WithMealRelation.after: "after meal",
        }
        new_desc_text = relation_map.get(new_relation_enum, str(new_relation_enum.value).replace('_', ' '))
        medication_to_change.description = f"Take: {new_desc_text}. Please verify dose."
    for key, value in update_dict.items():
        setattr(medication_to_change, key, value)
    db.commit()
    db.refresh(medication_to_change)
    return medication_to_change