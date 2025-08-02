from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.schemas.user_auth import UserAuthCreate, UserWithAuth, PasswordUpdateRequest, PasswordUpdateResponse
from app.crud.user import create_user as crud_create_user, get_user_info_by_id, update_user_password
from app.crud.user_auth import (create_new_user_auth as crud_create_new_user_auth,
                                get_user_auth_by_id, 
                                get_user_auth_by_email)
from app.utils.jwt import generate_access_token
from app.schemas.token import Token

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
    def verify_password(password: str, hashed_password: str):
        if len(hashed_password) < 32:
            return False
        
        salt = hashed_password[-32:]
        original_hash = hashed_password[:-32]
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
        return original_hash == new_hash
    
    # @staticmethod
    # def update_last_login_status():
    #     pass

    @staticmethod
    def change_password(db:Session, change_password_data: PasswordUpdateRequest, user_id:int):
        user_auth = get_user_auth_by_id(db, user_id=user_id)

        if not user_auth:
            raise ValueError("User not found")
        
        if not UserService.verify_password(change_password_data.current_password, user_auth.password):
            raise ValueError("Current password is incorect")
        
        new_hashed_password = UserService.hash_password(change_password_data.new_password)
        return  update_user_password(db, user_id, new_hashed_password)
    
    @staticmethod
    def delete_user():
        pass

    @staticmethod
    def authenticate_user(db: Session, login_data: UserAuthCreate):

        user_auth = get_user_auth_by_email(db, login_data.email)
        print(login_data.email)
        if not user_auth:
            raise ValueError("Invalid password or email")
        
        if not UserService.verify_password(login_data.password, user_auth.password):
            raise ValueError("Invalid password or email1")
        
        token_payload = {
        "email": user_auth.email,
        "user_id": user_auth.user_id
        }
        print(token_payload)
        token = generate_access_token(token_payload)

        return Token(
            access_token=token,
            token_type="bearer"
        )
    
    @staticmethod
    def get_user_info(db:Session, login_id:int):
        user_info = get_user_info_by_id(db,login_id)
        if not user_info:
            raise ValueError("User not found")
        return user_info
        