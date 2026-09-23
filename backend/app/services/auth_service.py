"""
Service layer for user registration, authentication, and token management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.schemas.user_schema import UserCreate, Token
from backend.app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_in: UserCreate) -> User:
        """
        Registers a new user after checking email uniqueness.
        """
        raise NotImplementedError("AuthService.register_user to be implemented")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Verifies credentials and returns User if valid.
        """
        raise NotImplementedError("AuthService.authenticate_user to be implemented")

    def create_user_token(self, user: User) -> Token:
        """
        Generates JWT token response for authenticated user.
        """
        raise NotImplementedError("AuthService.create_user_token to be implemented")
