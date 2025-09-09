from app.models.plan import Plan
from app.schemas.plan import PlanCreate
from datetime import date
from sqlalchemy.orm import Session

def create_plan(db: Session, plan_data: PlanCreate):
    new_plan = Plan(**plan_data.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan