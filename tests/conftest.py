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

        # Remove models created by integration test suite (keep demo models)
        test_models = db.query(Model).filter(
            Model.name.notin_(["iris_classifier", "iris-classifier"])
        ).all()
        for model in test_models:
            db.delete(model)

        # Remove users created by the integration test suite.
        users = db.query(User).filter(
            User.email.like("%@test.com")
        ).all()

        for user in users:
            db.delete(user)

        db.commit()

    finally:
        db.close()

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client