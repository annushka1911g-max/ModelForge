"""
User management API routes (Admin only).
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.user_schema import UserResponse, UserUpdate
from backend.app.authentication.rbac import require_roles
from backend.app.models.user import UserRole, User

router = APIRouter()


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(require_roles([UserRole.ADMIN]))])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all registered users (Admin only).
    """
    raise NotImplementedError("List users endpoint to be implemented")


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_roles([UserRole.ADMIN]))])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's role or active status (Admin only).
    """
    raise NotImplementedError("Update user endpoint to be implemented")
