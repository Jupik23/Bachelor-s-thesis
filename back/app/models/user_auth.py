from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class UserAuth(Base):
    __tablename__ = 'user_auth'

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index = True)
    password = Column(String, nullable = False)
    email = Column(String, index = True, nullable= False, unique=True)

    user = relationship("User", back_populates="auth")
