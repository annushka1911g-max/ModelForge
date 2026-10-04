"""
Service layer for recording and querying platform audit logs.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

logger = logging.getLogger("modelforge.services.audit")


def log_audit_event(
    db: Session,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    user: Optional[User] = None,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    client_ip: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[AuditLog]:
    """
    Utility function to write an audit entry safely without breaking caller transaction.
    """
    try:
        uid = user.id if user else user_id
        email = user.email if user else user_email
        log_entry = AuditLog(
            user_id=uid,
            user_email=email,
            action=action.upper(),
            resource=resource.lower(),
            resource_id=str(resource_id) if resource_id is not None else None,
            client_ip=client_ip,
            event_metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log_entry)
        db.commit()
        return log_entry
    except Exception as exc:
        logger.warning("Failed to record audit log: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
        return None


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        user: Optional[User] = None,
        client_ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AuditLog]:
        return log_audit_event(
            db=self.db,
            action=action,
            resource=resource,
            resource_id=resource_id,
            user=user,
            client_ip=client_ip,
            metadata=metadata,
        )

    def list_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action.upper())
        if resource:
            query = query.filter(AuditLog.resource == resource.lower())
        if user_email:
            query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))

        return query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
