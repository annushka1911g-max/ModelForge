"""
Authentication API routes — register, login, current-user.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.user_schema import UserCreate, UserResponse, Token
from backend.app.services.auth_service import AuthService
from backend.app.authentication.rbac import get_current_user
from backend.app.models.user import User

router = APIRouter()
logger = logging.getLogger("modelforge.routes.auth")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    operation_id="auth_register",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user. Hashes the password with bcrypt.
    Returns 400 if the email is already registered.
    """
    auth_service = AuthService(db)
    return auth_service.register_user(user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and obtain JWT access token",
    operation_id="auth_login",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2-compatible login endpoint.
    Accepts `username` (email) and `password` as form fields.
    Returns a Bearer JWT access token on success, 401 on failure.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )
    if user is None:
        logger.warning("Failed login attempt for: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_token_for_user(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    operation_id="auth_me",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    Requires a valid Bearer JWT in the Authorization header.
    """
    return current_user
