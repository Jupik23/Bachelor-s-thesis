from sqlalchemy import Column, Integer, String
from app.database.database import Base

class DietIntolerances(Base):
    __tablename__ = "diet_intolerances"

    id = Column(Integer, primary_key=True, index=True)
    intolerance = Column(String(100), unique=True, nullable=False, index=True)