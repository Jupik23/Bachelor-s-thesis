from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user import User
from app.models.care_relation import CareRelation

def create_care_relation(db: Session, carer_id: int, patient_id: int):
    db_relation = CareRelation(carer_id=carer_id, patient_id=patient_id)
    db.add(db_relation)
    return db_relation

def get_dependents_by_carer_id(db: Session, carer_id: int):
    relations = db.query(CareRelation).filter(CareRelation.carer_id == carer_id).all()
    return [relation.patient for relation in relations]

def get_carer_by_patient_id(db: Session, patient_id: int):
    relation = db.query(CareRelation).filter(CareRelation.patient_id == patient_id).first()
    if relation:
        return relation.carer
    return None

def check_relation(db: Session, carer_id: int, patient_id: int) -> bool:
    relation = db.query(CareRelation).filter(
        CareRelation.carer_id == carer_id,
        CareRelation.patient_id == patient_id
    ).first()
    return relation is not None

def is_user_patient(db: Session, user_id: int) -> bool:
    return db.query(CareRelation).filter(CareRelation.patient_id == user_id).count() > 0