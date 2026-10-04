"""
Audit log API routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.authentication.rbac import require_roles
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.audit_schema import AuditLogResponse
from backend.app.services.audit_service import AuditService

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse], summary="List audit logs", operation_id="list_audit_logs")
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.ML_ENGINEER])),
):
    svc = AuditService(db)
    return svc.list_logs(skip=skip, limit=limit, action=action, resource=resource, user_email=user_email)
