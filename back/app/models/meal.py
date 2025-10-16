from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from datetime import datetime
from .common import MealType
from app.database.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(SAEnum(MealType), nullable=True)
    time = Column(Time, nullable=False)
    description = Column(String, nullable=True)
    spoonacular_recipe_id = Column(Integer, nullable=True)
    eaten = Column(Boolean, default=False, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    plan = relationship("Plan", back_populates="meals")