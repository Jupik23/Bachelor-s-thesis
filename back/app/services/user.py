from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.schemas.user_auth import UserAuthCreate, UserWithAuth
from app.crud.user import create_user as crud_create_user
from app.crud.user_auth import create_new_user_auth as crud_create_new_user_auth

import hashlib
import secrets

class UserService:

    @staticmethod
    def register_new_user(db:Session, user_data: UserCreate, auth_data: UserAuthCreate):
        try:
            new_user = crud_create_user(db, user_data)

            hashed_password = UserService.hash_password(auth_data.password)
           
            auth = crud_create_new_user_auth(
                db,
                UserAuthCreate(email=auth_data.email, password = hashed_password),
                user_id = new_user.id
            )

            return UserWithAuth(
                id = new_user.id,
                name = new_user.name,
                surname = new_user.surname,
                login = new_user.login,
                auth = auth
            )
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def hash_password(password:str):
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex() + salt

    @staticmethod
    def verify_password():
        pass
    
    @staticmethod
    def update_last_login_status():
        pass

    @staticmethod
    def change_password():
        pass

    @staticmethod
    def delete_user():
        pass