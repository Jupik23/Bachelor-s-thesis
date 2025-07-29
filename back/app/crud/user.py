from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User

def create_user(db: Session, acount_data: UserCreate):
    new_user = User(**acount_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_info_by_id(db: Session, account_id: int):
    return db.query(User).filter(User.id == account_id).first()
