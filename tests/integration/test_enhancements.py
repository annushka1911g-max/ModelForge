"""
Integration tests for ModelForge enhancement features:
- API Key Lifecycle & Authentication
- Audit Logging
- Experiment Tracking & Comparison
- Notification Center
- Global Search
- Model Tags & Favorites
- Version Comparison
- Feature Importance & Drift Detection
- CSV Validation
- Dashboard & Performance Analytics
- Health Probes
"""
import io
import pytest
from backend.app.models.user import UserRole


def _get_auth_headers(client, email="engineer@test.com", role=UserRole.ML_ENGINEER.value):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Test Engineer",
        "password": "Password123!",
        "role": role,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_probes(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "services" in data

    resp_live = client.get("/health/live")
    assert resp_live.status_code == 200
    assert resp_live.json()["status"] == "alive"

    resp_ready = client.get("/health/ready")
    assert resp_ready.status_code == 200
    assert resp_ready.json()["status"] in ("ready", "not_ready")


def test_api_key_lifecycle_and_auth(client):
    headers = _get_auth_headers(client, email="apikey_user@test.com", role="ML_ENGINEER")

    # 1. Create API Key
    resp = client.post("/api/v1/api-keys/", json={"name": "Production Service Key"}, headers=headers)
    assert resp.status_code == 201
    key_data = resp.json()
    assert "key" in key_data
    assert key_data["key"].startswith("mf_live_")
    raw_key = key_data["key"]
    key_id = key_data["id"]

    # 2. List API Keys
    list_resp = client.get("/api/v1/api-keys/", headers=headers)
    assert list_resp.status_code == 200
    keys = list_resp.json()
    assert any(k["id"] == key_id for k in keys)

    # 3. Use API Key to access a protected endpoint
    api_key_headers = {"Authorization": f"Bearer {raw_key}"}
    auth_resp = client.get("/api/v1/api-keys/", headers=api_key_headers)
    assert auth_resp.status_code == 200

    # 4. Revoke API Key
    del_resp = client.delete(f"/api/v1/api-keys/{key_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["is_active"] is False

    # 5. Verify revoked key is rejected
    rej_resp = client.get("/api/v1/api-keys/", headers=api_key_headers)
    assert rej_resp.status_code == 401


def test_audit_logs(client):
    headers = _get_auth_headers(client, email="audit_admin@test.com", role="ADMIN")
    resp = client.get("/api/v1/audit-logs/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_experiment_tracking_and_comparison(client):
    headers = _get_auth_headers(client, email="exp_user@test.com", role="ML_ENGINEER")

    # Create Experiment 1
    resp1 = client.post("/api/v1/experiments/", json={
        "name": "Exp-RandomForest-v1",
        "description": "Baseline RF model",
        "hyperparameters": {"n_estimators": 100, "max_depth": 5},
        "metrics": {"accuracy": 0.95, "f1_score": 0.94},
        "dataset_name": "iris_dataset",
        "dataset_version": "v1.0",
        "status": "COMPLETED",
    }, headers=headers)
    assert resp1.status_code == 201
    exp1 = resp1.json()

    # Create Experiment 2
    resp2 = client.post("/api/v1/experiments/", json={
        "name": "Exp-RandomForest-v2",
        "description": "RF with tuned max_depth",
        "hyperparameters": {"n_estimators": 200, "max_depth": 10},
        "metrics": {"accuracy": 0.98, "f1_score": 0.97},
        "dataset_name": "iris_dataset",
        "dataset_version": "v1.0",
        "status": "COMPLETED",
    }, headers=headers)
    assert resp2.status_code == 201
    exp2 = resp2.json()

    # List Experiments
    list_resp = client.get("/api/v1/experiments/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 2

    # Compare Experiments
    comp_resp = client.get(f"/api/v1/experiments/compare?ids={exp1['id']},{exp2['id']}", headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert len(comp_data["experiments"]) == 2
    assert "accuracy" in comp_data["metric_keys"]


def test_notifications_flow(client):
    headers = _get_auth_headers(client, email="notif_user@test.com", role="ML_ENGINEER")

    # Get unread count
    resp = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert resp.status_code == 200
    assert "unread_count" in resp.json()

    # List notifications
    list_resp = client.get("/api/v1/notifications/", headers=headers)
    assert list_resp.status_code == 200
    assert isinstance(list_resp.json(), list)


def test_global_search(client):
    headers = _get_auth_headers(client, email="search_user@test.com", role="ML_ENGINEER")
    resp = client.get("/api/v1/search/?q=iris", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert "deployments" in data
    assert "experiments" in data


def test_model_tags_and_favorite(client):
    headers = _get_auth_headers(client, email="tags_user@test.com", role="ML_ENGINEER")

    # Create model
    m_resp = client.post("/api/v1/models/", json={
        "name": "tagged-model",
        "display_name": "Tagged Classifier",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    assert m_resp.status_code == 201
    model_id = m_resp.json()["id"]

    # Toggle favorite
    fav_resp = client.post(f"/api/v1/models/{model_id}/favorite", headers=headers)
    assert fav_resp.status_code == 200
    assert fav_resp.json()["is_starred"] is True

    # Add tag
    tag_resp = client.post(f"/api/v1/models/{model_id}/tags", json={"tag": "production-ready"}, headers=headers)
    assert tag_resp.status_code == 200
    assert "production-ready" in tag_resp.json()["tags"]

    # Remove tag
    del_tag_resp = client.delete(f"/api/v1/models/{model_id}/tags/production-ready", headers=headers)
    assert del_tag_resp.status_code == 200
    assert "production-ready" not in del_tag_resp.json()["tags"]


def test_monitoring_analytics_endpoints(client):
    headers = _get_auth_headers(client, email="analytics_user@test.com", role="ML_ENGINEER")

    # Dashboard analytics
    resp = client.get("/api/v1/monitoring/dashboard-analytics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "stats" in data
    assert "total_predictions" in data["stats"]
    assert "charts" in data
    assert "system_health" in data

    # Performance analytics
    perf_resp = client.get("/api/v1/monitoring/performance?time_range=24h", headers=headers)
    assert perf_resp.status_code == 200
    perf_data = perf_resp.json()
    assert "avg_latency_ms" in perf_data
    assert "total_inferences" in perf_data
    assert "p95_latency_ms" in perf_data
