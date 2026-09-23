"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.user_schema import UserCreate, UserResponse, Token
from backend.app.authentication.rbac import get_current_user
from backend.app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    raise NotImplementedError("Register endpoint to be implemented")


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    """
    raise NotImplementedError("Login endpoint to be implemented")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user details.
    """
    return current_user
