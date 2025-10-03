from app.models.preferences import DietPreferences
from sqlalchemy.orm import Session

def create_preference(db:Session, preference:str):
    new_preference = DietPreferences(
        name = preference
    )
    db.add(new_preference)
    db.commit()
    db.refresh()

def get_all_preferences(db: Session):
    return db.query(DietPreferences).all()