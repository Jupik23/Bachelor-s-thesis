import app.models.plan
from datetime import date
from sqlalchemy.orm import Session

def create_plan(db: Session, user_id: int, created_by: int, day_start: date):
    pass