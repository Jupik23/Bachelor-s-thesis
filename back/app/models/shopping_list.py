# app/models/shopping_list.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    include_dependents = Column(Boolean, default=False)
    content = Column(JSON, nullable=False)
    user = relationship("User", back_populates="shopping_lists")