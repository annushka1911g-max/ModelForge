"""
Pytest global fixtures and configuration.

Uses the real local PostgreSQL database but removes test-created
users before each test so integration tests remain isolated.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal
from backend.app.models.user import User


@pytest.fixture(scope="function")
def client():
    """
    Creates a TestClient and cleans test users before each test.
    """

    db = SessionLocal()

    try:
        from backend.app.models.model import Model
        from backend.app.models.api_key import ApiKey
        from backend.app.models.audit_log import AuditLog
        from backend.app.models.experiment import Experiment
        from backend.app.models.notification import Notification

        # Remove models created by integration test suite (keep demo models)
        test_models = db.query(Model).filter(
            Model.name.notin_(["iris_classifier", "iris-classifier"])
        ).all()
        for model in test_models:
            db.delete(model)

        # Remove users created by the integration test suite and their related records
        users = db.query(User).filter(
            User.email.like("%@test.com")
        ).all()
        user_ids = [u.id for u in users]
        if user_ids:
            db.query(ApiKey).filter(ApiKey.user_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(Notification).filter(Notification.user_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(AuditLog).filter(AuditLog.user_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(Experiment).filter(Experiment.created_by.in_(user_ids)).delete(synchronize_session=False)

        for user in users:
            db.delete(user)

        db.commit()

    finally:
        db.close()

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client