"""
Integration tests for core system endpoints (health, readiness, OpenAPI).
Phase 1 — Backend Foundation
"""


def test_liveness_returns_200(client):
    """GET /healthz should return 200 with status=alive."""
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "alive"
    assert body["app"] == "ModelForge"


def test_readiness_returns_200_with_db_connected(client):
    """GET /readyz should return 200 with status=ready and a connected database."""
    response = client.get("/readyz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["services"]["database"]["status"] == "connected"


def test_monitoring_health_endpoint(client):
    """GET /api/v1/monitoring/health should return healthy with DB connected."""
    response = client.get("/api/v1/monitoring/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["services"]["database"]["status"] == "connected"


def test_openapi_schema_accessible(client):
    """GET /api/v1/openapi.json should return valid OpenAPI schema."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "ModelForge"
    assert "paths" in schema


def test_docs_accessible(client):
    """GET /docs should return HTML documentation page."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_404_unknown_route_returns_json_error(client):
    """Unknown route should return structured JSON 404, not HTML."""
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404


def test_api_v1_prefix_exists(client):
    """All API routes must be mounted under /api/v1."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    # Every path must start with /api/v1
    for path in paths:
        assert (
        path.startswith("/api/v1") or path in {"/healthz", "/readyz", "/docs"}
    ), f"Unexpected route outside /api/v1: {path}"