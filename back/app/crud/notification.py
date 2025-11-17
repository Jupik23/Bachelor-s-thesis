from app.schemas.notification import NotificationCreate
from app.models.notification import Notification
from app.models.user import User
from sqlalchemy.orm import Session, joinloaded

def create_new_notification(db: Session, data: NotificationCreate):
    new_notification = Notification(
        user_id = data.user_id,
        related_user_id = data.related_user_id,
        type = data.type,
        message = data.message,
        is_read = False
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

def get_unread_notification(db: Session, user_id: int):
    return db.query(Notification).options(
        joinloaded(Notification.subject)
    ).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).order_by(Notification.sent_at.desc()).all()

def mark_as_read_notification(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification