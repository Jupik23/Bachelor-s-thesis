from pydantic import BaseModel, EmailStr
from typing import Optional 

class Token(BaseModel):
    access_token: str
    token_type: str

class OAuth2LoginRequest(BaseModel):
    user_name: str
    password: str
    grant_type: Optional[str] = "password"
    scope: Optional[str] = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None