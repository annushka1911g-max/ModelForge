"""
Pytest global fixtures and configuration.
Uses httpx AsyncClient with a real test database session.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    """
    Creates a synchronous TestClient for the FastAPI application.
    Uses a real DB connection (modelforge_db must exist locally).
    """
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
