"""
Pydantic schemas for User entity — request/response contracts.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from backend.app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: Optional[UserRole] = UserRole.VIEWER
    is_active: Optional[bool] = True


class UserCreate(BaseModel):
    """Schema for user registration. Password must be at least 8 characters."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[UserRole] = UserRole.VIEWER

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Password must not be blank")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name must not be blank")
        return v


class UserUpdate(BaseModel):
    """Schema for admin user updates."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema returned to clients — never exposes hashed_password."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Email + password login (JSON body alternative to OAuth2 form)."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """JWT token response envelope."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Decoded JWT payload claims."""
    sub: Optional[str] = None   # email address
    role: Optional[str] = None  # UserRole value
