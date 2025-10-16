from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Plan(Base):
    __tablename__ ="plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    day_start = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) 
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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
    # medications = relationship("Medication", back_populates="plan", cascade="all, delete-orphan")
