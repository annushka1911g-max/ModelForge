"""
Service layer for platform notifications and alerts.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.notification import Notification

logger = logging.getLogger("modelforge.services.notifications")


def create_notification(
    db: Session,
    title: str,
    message: str,
    notification_type: str = "INFO",
    user_id: Optional[int] = None,
    link: Optional[str] = None,
) -> Optional[Notification]:
    """
    Creates a notification safely without breaking surrounding transactions.
    """
    try:
        notif = Notification(
            title=title,
            message=message,
            notification_type=notification_type.upper(),
            user_id=user_id,
            link=link,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif
    except Exception as exc:
        logger.warning("Failed to create notification: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
        return None


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_notifications(self, user_id: Optional[int] = None, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = self.db.query(Notification)
        if user_id is not None:
            # Show user-specific or broadcast notifications (where user_id is null)
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, user_id: Optional[int] = None) -> int:
        query = self.db.query(Notification).filter(Notification.is_read.is_(False))
        if user_id is not None:
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        return query.count()

    def mark_as_read(self, notification_id: int, user_id: Optional[int] = None) -> bool:
        query = self.db.query(Notification).filter(Notification.id == notification_id)
        if user_id is not None:
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        notif = query.first()
        if notif:
            notif.is_read = True
            self.db.commit()
            return True
        return False

    def mark_all_as_read(self, user_id: Optional[int] = None) -> int:
        query = self.db.query(Notification).filter(Notification.is_read.is_(False))
        if user_id is not None:
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        updated_count = query.update({Notification.is_read: True}, synchronize_session=False)
        self.db.commit()
        return updated_count
