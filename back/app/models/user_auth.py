from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
from datetime import datetime

class UserAuth(Base):
    __tablename__ = 'user_auth'

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index = True)
    password = Column(String, nullable = False)
    email = Column(String, index = True, nullable= False, unique=True)
    last_login = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="auth")
