from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import NotificationService
import logging

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)

@router.get("/me", response_model=List[NotificationResponse])
def get_my_notifications(
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    try:
        service = NotificationService(db=db)
        notifications = service.get_user_notification(carrer_id=user.id)
        return notifications
    except Exception as e:
        logging.error(f"Error fetching notifications: {e}")
        db.rollback()
        return []

@router.patch("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def mark_as_read(notification_id: int,
                 user: dict = Depends(get_current_user),
                 db: Session = Depends(get_database),
                 ):
    service = NotificationService(db=db)
    success = service.mark_as_read(notification_id=notification_id, 
                                  carrer_id=user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you do not have permission to read it."
        )
