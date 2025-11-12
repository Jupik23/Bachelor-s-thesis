from pydantic import BaseModel
from app.schemas.user import UserCreate
from app.schemas.user_auth import UserAuthCreate

class DependentCreateRequest(BaseModel):
    user_data: UserCreate
    user_auth_data: UserAuthCreate