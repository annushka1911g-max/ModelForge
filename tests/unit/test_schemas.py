"""
Unit tests — Pydantic Schemas (Phase 1)
"""
from backend.app.schemas.user_schema import UserBase, UserCreate
from backend.app.models.user import UserRole


def test_user_base_schema_defaults():
    """UserBase must have correct role and is_active defaults."""
    user = UserBase(email="test@modelforge.example", full_name="Test User")
    assert user.role == UserRole.VIEWER
    assert user.is_active is True


def test_user_create_schema():
    """UserCreate should accept password field."""
    user = UserCreate(
        email="admin@modelforge.example",
        full_name="Admin User",
        password="supersecret",
        role=UserRole.ADMIN,
    )
    assert user.email == "admin@modelforge.example"
    assert user.role == UserRole.ADMIN
    assert user.password == "supersecret"


def test_user_base_email_format():
    """Invalid email should raise a Pydantic validation error."""
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UserBase(email="not-an-email", full_name="Test")
