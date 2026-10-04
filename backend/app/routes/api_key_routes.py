"""
API Key management routes.
"""
from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from backend.app.authentication.rbac import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.api_key_schema import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse
from backend.app.services.api_key_service import ApiKeyService
from backend.app.services.audit_service import log_audit_event

router = APIRouter()


@router.post("/", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED, summary="Create new API key")
def create_api_key(
    key_in: ApiKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ApiKeyService(db)
    api_key, raw_key = svc.create_key(current_user.id, key_in.name)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        action="API_KEY_CREATE",
        resource="api_key",
        resource_id=str(api_key.id),
        user=current_user,
        client_ip=client_ip,
        metadata={"name": api_key.name, "prefix": api_key.key_prefix},
    )

    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key=raw_key,
        key_prefix=api_key.key_prefix,
        created_at=api_key.created_at,
    )


@router.get("/", response_model=List[ApiKeyResponse], summary="List API keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ApiKeyService(db)
    # Admin can see all keys or own keys; ML_ENGINEER / VIEWER sees own keys
    user_id_filter = None if current_user.role.value == "ADMIN" else current_user.id
    return svc.list_keys(user_id=user_id_filter)


@router.delete("/{key_id}", response_model=ApiKeyResponse, summary="Revoke API key")
def revoke_api_key(
    key_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ApiKeyService(db)
    revoked = svc.revoke_key(key_id, current_user)

    client_ip = request.client.host if request.client else "unknown"
    log_audit_event(
        db=db,
        action="API_KEY_REVOKE",
        resource="api_key",
        resource_id=str(key_id),
        user=current_user,
        client_ip=client_ip,
        metadata={"name": revoked.name},
    )

    return revoked
