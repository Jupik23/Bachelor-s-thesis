from sqlalchemy.orm import Session
from app.schemas.user_auth import UserAuthCreate
from app.models.user_auth import UserAuth

def create_new_user_auth(db: Session, auth_data: UserAuthCreate, user_id : int):
    new_user_auth = UserAuth(**auth_data.dict(), user_id= user_id )
    db.add(new_user_auth)
    db.commit()
    db.refresh(new_user_auth)
    return new_user_auth