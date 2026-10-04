"""
Authentication business logic — registration, login, token creation.
"""
import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.authentication.hashing import PasswordHasher
from backend.app.authentication.jwt import create_access_token
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user_schema import UserCreate, Token, UserResponse

logger = logging.getLogger("modelforge.services.auth")


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """
        Creates a new user after verifying uniqueness.
        Password is bcrypt-hashed before storage.
        """
        existing = self.user_repository.get_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        hashed_password = PasswordHasher.get_password_hash(user_data.password)

        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
        )
        created_user = self.user_repository.create(user)
        logger.info("User registered: %s (role=%s)", created_user.email, created_user.role.value)
        return created_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Verifies email exists and password matches hash.
        Returns the User on success, None on failure.
        Deliberately returns None (not an exception) to let the caller
        decide the HTTP response — avoids leaking whether an email exists.
        """
        user = self.user_repository.get_by_email(email)
        if user is None:
            return None
        if not user.is_active:
            return None
        if not PasswordHasher.verify_password(password, user.hashed_password):
            return None
        return user

    def create_token_for_user(self, user: User) -> Token:
        """
        Generates a signed JWT token embedding the user's email and role.
        Returns a Token schema with the token string and user profile.
        """
        token_data = {
            "sub": user.email,
            "role": user.role.value,
        }
        access_token = create_access_token(data=token_data)
        logger.info("JWT issued for user: %s", user.email)
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )