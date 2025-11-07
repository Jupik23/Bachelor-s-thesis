from app.models.plan import Plan
from app.schemas.plan import PlanCreate
from datetime import date
from sqlalchemy.orm import Session, joinedload

def create_plan(db: Session, plan_data: PlanCreate):
    new_plan = Plan(**plan_data.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

def get_plan_by_id(db: Session, plan_id:int):
    return db.query(Plan).filter(Plan.id == plan_id).first()

def get_plan_with_meals_by_user_id_and_date(db: Session, user_id: int, plan_date: date = date.today()):
    return (
        db.query(Plan).options(joinedload(Plan.meals),
                               joinedload(Plan.medications))
        .filter(Plan.user_id == user_id)
        .filter(Plan.day_start == plan_date)
        .order_by(Plan.created_at.desc())
        .first()
    )