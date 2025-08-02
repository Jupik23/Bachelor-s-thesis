from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User
from app.crud.user_auth import get_user_auth_by_id

def create_user(db: Session, acount_data: UserCreate):
    new_user = User(**acount_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_info_by_id(db: Session, account_id: int):
    return db.query(User).filter(User.id == account_id).first()

def update_user_password(db: Session, account_id: int, new_password):
    user = get_user_auth_by_id(db, account_id)
    if user:
        user.password = new_password
        db.commit()
        db.refresh(user)
        return user
    return None