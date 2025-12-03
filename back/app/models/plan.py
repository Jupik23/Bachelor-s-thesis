from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
from datetime import datetime

class Plan(Base):
    __tablename__ ="plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    day_start = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    total_calories = Column(Float)
    total_protein = Column(Float)
    total_fat = Column(Float)
    total_carbohydrates = Column(Float)

    user = relationship(
        "User",
        back_populates="plans",
        foreign_keys="[Plan.user_id]"
    )

    meals = relationship("Meal", back_populates="plan", cascade="all, delete-orphan")
    creator = relationship(
        "User",
        back_populates="created_plans", 
        foreign_keys=[created_by] 
    )
    medications = relationship("Medication", back_populates="plan", cascade="all, delete-orphan")
