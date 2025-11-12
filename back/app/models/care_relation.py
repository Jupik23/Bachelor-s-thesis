from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class CareRelation(Base):
    __tablename__ = "care_relations"
    id = Column(Integer, primary_key=True, index=True)
    carer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    carer = relationship("User", foreign_keys=[carer_id], back_populates="caring_for")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="cared_by")