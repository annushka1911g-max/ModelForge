"""
Authentication and RBAC Package.
"""
from backend.app.authentication.hashing import PasswordHasher
from backend.app.authentication.jwt import create_access_token, decode_access_token
from backend.app.authentication.rbac import get_current_user, require_roles, oauth2_scheme

__all__ = [
    "PasswordHasher",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "require_roles",
    "oauth2_scheme",
]
