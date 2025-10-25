from sqlalchemy.orm import Session
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate
from typing import List

def create_medication(db: Session, plan_id: int, medication_data: MedicationCreate):
    new_med = Medication(
        plan_id=plan_id,
        time=medication_data.time,
        name=medication_data.name,
        with_meal_relation=medication_data.with_meal_relation,
        description=medication_data.description
    )
    db.add(new_med)
    db.flush()
    return new_med

def get_medication_by_plan_id(db: Session, plan_id: int):
    return db.querry(Medication).filter(Medication.plan_id == plan_id)
