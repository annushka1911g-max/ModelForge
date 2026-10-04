"""
Role-Based Access Control (RBAC) dependencies and guards.
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.repositories.user_repository import UserRepository
from backend.app.models.user import User, UserRole
from backend.app.authentication.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: validates JWT token or API key and returns the current user.
    Supports Authorization: Bearer <JWT> and Authorization: Bearer <API_KEY>.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check for ModelForge API Key (mf_live_...)
    if token.startswith("mf_"):
        from backend.app.services.api_key_service import ApiKeyService
        key_svc = ApiKeyService(db)
        user = key_svc.verify_key(token)
        if user is None or not user.is_active:
            raise credentials_exception
        return user

    # 2. Check for standard JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory to restrict endpoint access by UserRole.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
