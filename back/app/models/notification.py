from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key = True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now()) 
    message = Column(String, nullable=False) 
    is_read = Column(Boolean, default=False)

    recipient = relationship("User", foreign_keys=[user_id], back_populates="notifications_received")
    subject = relationship("User", foreign_keys=[related_user_id], back_populates="notifications_about")