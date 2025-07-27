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

    class Config:
        from_attributes = True