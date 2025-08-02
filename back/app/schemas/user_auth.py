from pydantic import BaseModel, EmailStr
from app.schemas.user import User, UserCreate
from typing import Optional

class UserAuthBase(BaseModel):
    email: EmailStr

class UserAuthCreate(UserAuthBase):
    password: str

class UserAuthUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_passoword: str
    confirm_password: str

    def password_match(self):
        return self.new_passoword == self.current_password

class PasswordUpdateResponse(BaseModel):
    message: str 
    updated_at: Optional[str] = None

class UserAuth(UserAuthBase):
    user_id: int

    class Config:
        from_attributes = True

class UserWithEmail(BaseModel):
    user_data: UserCreate
    user_auth_email: UserAuthBase

class RegisterRequest(BaseModel):
    user_data: UserCreate
    user_auth_data: UserAuthCreate

class UserWithAuth(User):
    auth: Optional[UserAuth] = None