from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RelatedUserResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    user_id: int
    related_user_id: int
    type: str
    message: str

class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    sent_at: datetime
    is_read: bool
    subject: Optional[RelatedUserResponse] = None
    class Config:
        from_attributes = True