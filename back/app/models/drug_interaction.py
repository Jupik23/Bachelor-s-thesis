from sqlalchemy import Column, Integer, String, DateTime, func
from app.database.database import Base


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer ,primary_key=True, index = True)
    drug1 = Column(String, nullable=False, index = True)
    drug2 = Column(String, nullable=False, index = True)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="None")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())