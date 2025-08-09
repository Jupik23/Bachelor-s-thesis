from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class OAuth2Account(Base):
    __tablename__ = 'oauth2_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  
    provider_id = Column(String, nullable=False)  
    provider_email = Column(String, nullable=True)
    access_token = Column(String, nullable=True)  
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="oauth2_accounts")

    class Config:
        from_attributes = True