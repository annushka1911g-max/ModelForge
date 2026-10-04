"""
Database seed script for default users and demo resources.
Ensures standard demo credentials exist for ADMIN, ML_ENGINEER, and VIEWER roles.
"""
import logging
from backend.app.database.session import SessionLocal
from backend.app.models.user import User, UserRole
from backend.app.authentication.hashing import PasswordHasher

logger = logging.getLogger("modelforge.seed")

DEFAULT_USERS = [
    {
        "email": "admin@modelforge.io",
        "full_name": "Platform Administrator",
        "password": "AdminPassword123!",
        "role": UserRole.ADMIN,
    },
    {
        "email": "engineer@modelforge.io",
        "full_name": "ML Engineer",
        "password": "EngineerPassword123!",
        "role": UserRole.ML_ENGINEER,
    },
    {
        "email": "viewer@modelforge.io",
        "full_name": "Viewer User",
        "password": "ViewerPassword123!",
        "role": UserRole.VIEWER,
    },
]


def seed_database():
    db = SessionLocal()
    try:
        for user_data in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=PasswordHasher.get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                )
                db.add(user)
                logger.info("Created seed user: %s (%s)", user_data["email"], user_data["role"].value)
            else:
                # Ensure user is active
                existing.is_active = True
                logger.info("Seed user already exists: %s", user_data["email"])
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to seed database: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
