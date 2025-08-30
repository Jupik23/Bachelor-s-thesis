from sqlalchemy.orm import Session
from app.models.health_form import HealthForm

def get_healthform_by_user_id(db: Session, user_id: int):
    return (db.query(HealthForm).filter(HealthForm.user_id == user_id)
            .order_by(HealthForm.created_at.desc())
            .first()
            )