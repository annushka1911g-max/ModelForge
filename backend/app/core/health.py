"""
Database health check utilities.
"""
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("modelforge.database")


def check_db_connection(db: Session) -> dict:
    """
    Performs a lightweight connectivity check to PostgreSQL.
    Returns a dict with status and postgres server version.
    """
    try:
        result = db.execute(text("SELECT version()")).scalar()
        return {"status": "connected", "version": result}
    except Exception as exc:
        logger.error("Database health check failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
