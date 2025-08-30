from pydantic import BaseModel, EmailStr
from typing import Optional

class OAuth2UserInfo(BaseModel):   
    provider: str
    provider_id: int
    email: EmailStr
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

class OAuth2CallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class OAuth2LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    is_new_user: bool = False