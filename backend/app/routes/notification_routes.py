"""
Platform notification API routes.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.authentication.rbac import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.notification_schema import NotificationResponse, NotificationUnreadCountResponse
from backend.app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse], summary="List user notifications")
def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(db)
    return svc.list_notifications(user_id=current_user.id, unread_only=unread_only, limit=limit)


@router.get("/unread-count", response_model=NotificationUnreadCountResponse, summary="Get unread notifications count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(db)
    return NotificationUnreadCountResponse(unread_count=svc.get_unread_count(user_id=current_user.id))


@router.post("/{notification_id}/read", summary="Mark notification as read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(db)
    success = svc.mark_as_read(notification_id, user_id=current_user.id)
    return {"success": success}


@router.post("/read-all", summary="Mark all notifications as read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NotificationService(db)
    count = svc.mark_all_as_read(user_id=current_user.id)
    return {"marked_count": count}
