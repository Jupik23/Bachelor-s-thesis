from typing import List, Optional;
from sqlalchemy.orm import Session
from app.crud.healthform import create_health_form_crud, get_health_form_by_user_id
from app.schemas.health_form import HealthFormCreate

class HealthFormService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_health_form(self,health_form_input: HealthFormCreate, user_id: int):
        return create_health_form_crud(db=self.db, health_care_input=health_form_input, user_id=user_id)
    
    def get_health_form(self, user_id: int):
        return get_health_form_by_user_id(self.db, user_id=user_id)