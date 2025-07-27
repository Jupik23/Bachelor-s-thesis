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

class UserAuth(UserAuthBase):
    user_id: int

    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    user_data: UserCreate
    user_auth_data: UserAuthCreate

class UserWithAuth(User):
    auth: Optional[UserAuth] = None