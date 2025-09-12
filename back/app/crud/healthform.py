from sqlalchemy.orm import Session
from typing import List, Any
from app.models.health_form import HealthForm
from app.schemas.health_form import HealthFormCreate, HealthFormUpdate

def create_health_form_crud(db:Session, health_care_input: HealthFormCreate, user_id: int):
    new_health_form = HealthForm(user_id = user_id,
                                 **health_care_input.dict())
    db.add(new_health_form)
    db.commit()
    db.refresh(new_health_form)
    return new_health_form

def get_health_form_by_user_id(db: Session, user_id: int):
    return db.query(HealthForm).filter(user_id == HealthForm.user_id).first()

def update_healt_form_crud(db:Session, user_id: int, update_data: HealthFormUpdate):
    user_health_form = get_health_form_by_user_id(db, user_id=user_id)
    if not user_health_form:
        return None

    new_data = update_data.dict(exclude_unset=True)
    for field, value in new_data.items():
        setattr(user_health_form, field, value)
    db.commit()
    db.refresh(user_health_form)  