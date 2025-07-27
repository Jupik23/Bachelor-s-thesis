from pydantic import BaseModel, EmailStr
from app.schemas.user import User
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

class UserWithAuth(User):
    auth: Optional[UserAuth] = None