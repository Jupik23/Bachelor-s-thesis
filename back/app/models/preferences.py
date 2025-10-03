from sqlalchemy import Column, String, Integer
from app.database.database import Base

class DietPreferences(Base):
    __tablename__ = "diet_preferences"

    id = Column(Integer, primary_key=True, index=True)
    preference = Column(String, index=True, nullable=False, unique=True)