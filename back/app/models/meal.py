from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from .common import MealType
from app.database.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(SAEnum(MealType), nullable=True)
    time = Column(Time, nullable=False)
    description = Column(String, nullable=True)
    eaten = Column(Boolean, default=False, nullable=False)
    comment = Column(String, nullable=True)

    plan = relationship("Plan", back_populates="meals")