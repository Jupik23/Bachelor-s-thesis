from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class HealthForm(Base):
    __tablename__ = 'health_forms'

    id = Column(Integer, nullable = False, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    height = Column(Integer)
    weight = Column(Integer)  
    number_of_meals_per_day = Column(Integer)
    diet_preferences = Column(JSON, nullable=True)
    intolerances = Column(JSON, nullable=True)
    medicament_usage = Column(JSON, nullable=True)

    user = relationship("User", back_populates="health_forms")