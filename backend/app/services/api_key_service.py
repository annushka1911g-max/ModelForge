"""
Service layer for API Key generation, verification, and revocation.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.api_key import ApiKey
from backend.app.models.user import User

logger = logging.getLogger("modelforge.services.api_key")


class ApiKeyService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def create_key(self, user_id: int, name: str) -> Tuple[ApiKey, str]:
        # Generate high-entropy API key
        random_token = secrets.token_urlsafe(32)
        raw_key = f"mf_live_{random_token}"
        key_prefix = raw_key[:12] + "..."
        hashed_key = self.hash_key(raw_key)

        api_key = ApiKey(
            user_id=user_id,
            name=name.strip(),
            key_prefix=key_prefix,
            hashed_key=hashed_key,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        logger.info("API key created: id=%d, user_id=%d, prefix=%s", api_key.id, user_id, key_prefix)
        return api_key, raw_key

    def list_keys(self, user_id: Optional[int] = None) -> List[ApiKey]:
        query = self.db.query(ApiKey)
        if user_id is not None:
            query = query.filter(ApiKey.user_id == user_id)
        return query.order_by(ApiKey.created_at.desc()).all()

    def revoke_key(self, key_id: int, user: User) -> ApiKey:
        api_key = self.db.query(ApiKey).filter(ApiKey.id == key_id).first()
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        # Non-admins can only revoke their own keys
        if user.role.value != "ADMIN" and api_key.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to revoke this API key")

        api_key.is_active = False
        self.db.commit()
        self.db.refresh(api_key)
        logger.info("API key revoked: id=%d", key_id)
        return api_key

    def verify_key(self, raw_key: str) -> Optional[User]:
        if not raw_key.startswith("mf_"):
            return None
        hashed = self.hash_key(raw_key)
        api_key = (
            self.db.query(ApiKey)
            .filter(ApiKey.hashed_key == hashed, ApiKey.is_active.is_(True))
            .first()
        )
        if not api_key:
            return None

        # Update last used timestamp
        try:
            api_key.last_used_at = datetime.now(timezone.utc)
            self.db.commit()
        except Exception:
            self.db.rollback()

        return api_key.user
