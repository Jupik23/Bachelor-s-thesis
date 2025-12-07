from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    surname: str
    login: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    login: Optional[str] = None

class User(UserBase):
    id: int
    is_patient: bool = False

    class Config:
        from_attributes = True