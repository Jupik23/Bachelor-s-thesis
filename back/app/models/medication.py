from sqlalchemy import Column, Integer, Time, ForeignKey, Boolean, String
from sqlalchemy import Enum as SAEnum
from app.models.common import WithMealRelation
from app.database.database import Base
from sqlalchemy.orm import relationship

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="Cascade"), nullable=False)
    time = Column(Time, nullable=False)
    name = Column(String, nullable=False)
    taken = Column(Boolean, default=False)
    with_meal_relation = Column(SAEnum(WithMealRelation), default=WithMealRelation.empty_stomach) 
    description = Column(String, nullable=True)
    rxnorm_id = Column(String, nullable=True)

    plan = relationship("Plan", back_populates="medications")