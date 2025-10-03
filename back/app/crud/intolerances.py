from app.models.intolerances import DietIntolerances
from sqlalchemy.orm import Session

def get_all_intolerances(db: Session):
    return db.query(DietIntolerances).all()