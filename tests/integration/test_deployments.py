"""
Integration tests for Deployment Lifecycle Management.
Tests: deploy, stop, restart, rollback, RBAC permissions, and state transitions.
"""
import io
import json
import pytest


def _get_auth_headers(client, email="deployer@test.com", role="ML_ENGINEER"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Deployer User",
        "password": "Password123!",
        "role": role,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_deployment_lifecycle(client):
    headers = _get_auth_headers(client, email="dep_lifecycle@test.com", role="ML_ENGINEER")

    # 1. Register a model
    m_resp = client.post("/api/v1/models/", json={
        "name": "lifecycle-model",
        "display_name": "Lifecycle Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    model_id = m_resp.json()["id"]

    # 2. Upload version 1
    mock_file1 = io.BytesIO(b"model-binary-v1")
    v1_resp = client.post(
        f"/api/v1/models/{model_id}/versions",
        data={
            "feature_schema": json.dumps({"features": [{"name": "x", "type": "float"}]}),
            "changelog": "v1 initial",
        },
        files={"file": ("model.pkl", mock_file1, "application/octet-stream")},
        headers=headers,
    )
    v1_id = v1_resp.json()["id"]

    # 3. Upload version 2
    mock_file2 = io.BytesIO(b"model-binary-v2")
    v2_resp = client.post(
        f"/api/v1/models/{model_id}/versions",
        data={
            "feature_schema": json.dumps({"features": [{"name": "x", "type": "float"}]}),
            "changelog": "v2 update",
        },
        files={"file": ("model.pkl", mock_file2, "application/octet-stream")},
        headers=headers,
    )
    v2_id = v2_resp.json()["id"]

    # 4. Deploy Version 1
    dep_resp = client.post("/api/v1/deployments/", json={
        "model_id": model_id,
        "current_version_id": v1_id,
    }, headers=headers)
    assert dep_resp.status_code == 201
    dep = dep_resp.json()
    dep_id = dep["id"]
    assert dep["status"] == "DEPLOYED"
    assert dep["current_version_id"] == v1_id

    # 5. Stop Deployment
    stop_resp = client.post(f"/api/v1/deployments/{dep_id}/stop", headers=headers)
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "STOPPED"

    # Stopping again should return 400
    stop_again = client.post(f"/api/v1/deployments/{dep_id}/stop", headers=headers)
    assert stop_again.status_code == 400

    # 6. Restart Deployment
    restart_resp = client.post(f"/api/v1/deployments/{dep_id}/restart", headers=headers)
    assert restart_resp.status_code == 200
    assert restart_resp.json()["status"] == "DEPLOYED"

    # 7. Re-deploy to Version 2
    redeploy_resp = client.post("/api/v1/deployments/", json={
        "model_id": model_id,
        "current_version_id": v2_id,
    }, headers=headers)
    assert redeploy_resp.status_code == 201
    redeploy_data = redeploy_resp.json()
    assert redeploy_data["current_version_id"] == v2_id
    assert redeploy_data["previous_version_id"] == v1_id

    # 8. Rollback to Version 1
    rollback_resp = client.post(f"/api/v1/deployments/{dep_id}/rollback", json={
        "target_version_id": v1_id,
    }, headers=headers)
    assert rollback_resp.status_code == 200
    rb_data = rollback_resp.json()
    assert rb_data["current_version_id"] == v1_id
    assert rb_data["status"] == "DEPLOYED"


def test_deployment_viewer_forbidden(client):
    viewer_headers = _get_auth_headers(client, email="viewer_dep@test.com", role="VIEWER")
    resp = client.post("/api/v1/deployments/", json={
        "model_id": 1,
        "current_version_id": 1,
    }, headers=viewer_headers)
    assert resp.status_code == 403


def test_deployment_not_found(client):
    headers = _get_auth_headers(client, email="dep_404@test.com", role="ML_ENGINEER")
    resp = client.get("/api/v1/deployments/999999", headers=headers)
    assert resp.status_code == 404
