from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from app.models.common import ActivityLevel, CalorieGoal, Gender
from sqlalchemy import Enum 
class HealthForm(Base):
    __tablename__ = 'health_forms'

    id = Column(Integer, nullable = False, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    height = Column(Integer)
    weight = Column(Integer)  
    age = Column(Integer, nullable = True) #need to change in future cuz age can change in time :) we will count current age 
    gender = Column(Enum(Gender), nullable = True)
    activity_level = Column(Enum(ActivityLevel), default=ActivityLevel.sedentary)
    calorie_goal = Column(Enum(CalorieGoal), default=CalorieGoal.maintain)
    number_of_meals_per_day = Column(Integer)
    diet_preferences = Column(JSON, nullable=True)
    intolerances = Column(JSON, nullable=True)
    medicament_usage = Column(JSON, nullable=True)

    user = relationship("User", back_populates="health_forms")