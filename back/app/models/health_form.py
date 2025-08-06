from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class HealtForm(Base):
    __tablename__ = 'healt_forms'

    id = Column(Integer, nulable = False, primarykey = True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow)
    height = Column(Integer)
    weight = Column(Integer)  
    number_of_meals_per_day = Column(Integer)
    diet_preferences = Column(String)
    allergies = Column(String)
    intolerances = Column(String)
    medicament_usage = Column(String)

    user = relationship("User", back_populates="health_form")