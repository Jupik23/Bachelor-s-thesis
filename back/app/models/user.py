from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    surname = Column(String, nullable = False)
    login =  Column(String, unique = True, index= True, nullable = False)
    
    auth = relationship("UserAuth", back_populates="user", uselist=False)
    oauth2_accounts = relationship("OAuth2Account", back_populates="user")
    health_forms = relationship("HealthForm", back_populates="user",cascade="all, delete-orphan")
    plans = relationship(
        "Plan",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Plan.user_id]"
    )