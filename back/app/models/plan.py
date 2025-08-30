from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Plan(Base):
    __tablename__ ="plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    day_start = Column(Date, nullable=False)

    user = relationship(
        "User",
        back_populates="plans",
        foreign_keys="[Plan.user_id]"
    )

    meals = relationship("Meal", back_populates="plan", cascade="all, delete-orphan")
    # medications = relationship("Medication", back_populates="plan", cascade="all, delete-orphan")
