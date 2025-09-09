from sqlalchemy.orm import Session
from typing import List, Any
from app.models.health_form import HealthForm
from app.schemas.health_form import HealthFormCreate

def create_health_form(db:Session, health_care_input: HealthFormCreate):
    new_health_form = HealthForm(**health_care_input.dict())
    db.add(new_health_form)
    db.commit()
    db.close()