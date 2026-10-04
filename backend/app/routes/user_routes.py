"""
User management API routes (Admin only).
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.user_schema import UserResponse, UserUpdate
from backend.app.authentication.rbac import require_roles, get_current_user
from backend.app.models.user import UserRole, User
from backend.app.repositories.user_repository import UserRepository

router = APIRouter()
logger = logging.getLogger("modelforge.routes.users")


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users (Admin only)",
    operation_id="users_list",
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Returns a paginated list of all registered users."""
    repo = UserRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user's role or status (Admin only)",
    operation_id="users_update",
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """
    Update a user's role or active status. Admin-only.
    Returns 404 if the user does not exist.
    """
    repo = UserRepository(db)
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    updated_user = repo.update(user)
    logger.info(
        "Admin %s updated user %d (role=%s, active=%s)",
        current_user.email,
        user_id,
        updated_user.role.value,
        updated_user.is_active,
    )
    return updated_user
