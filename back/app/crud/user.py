from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User

def create_user(db: Session, acount_data: UserCreate):
    new_user = User(**acount_data.dict())
    db.add(new_user)
    db.commit()
    return new_user
