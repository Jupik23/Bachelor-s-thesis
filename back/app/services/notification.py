from sqlalchemy.orm import Session
from typing import List
from app.schemas.notification import NotificationResponse
from app.crud.notification import (create_new_notification,
                                   get_unread_notification,
                                   mark_as_read_notification)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_notification(self, carrer_id: int):
        db_notifications = get_unread_notification(db=self.db, user_id=carrer_id)
        response_list = []
        for notification in db_notifications:
            response_list.append(notification)

        return response_list
    
    def mark_as_read(self, notification_id: int, carrer_id: int):
        updated = mark_as_read_notification(db=self.db, notification_id=notification_id,
                                               user_id = carrer_id)
        return updated is not None