"""
Integration tests for Model Catalog and Model Versioning.
Tests: model registration, listing, retrieval, update, version upload, and RBAC.
"""
import io
import json
import pytest

from backend.app.models.user import UserRole


def _get_auth_headers(client, email="modeller@test.com", role=UserRole.ML_ENGINEER.value):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Test Modeller",
        "password": "Password123!",
        "role": role,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_model_success(client):
    headers = _get_auth_headers(client, email="create_model_user@test.com", role="ML_ENGINEER")
    resp = client.post("/api/v1/models/", json={
        "name": "test-iris-model",
        "display_name": "Test Iris Classifier",
        "description": "Test model for pytest suite",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-iris-model"
    assert data["display_name"] == "Test Iris Classifier"
    assert data["framework"] == "SCIKIT_LEARN"
    assert data["task_type"] == "CLASSIFICATION"


def test_create_model_viewer_forbidden(client):
    headers = _get_auth_headers(client, email="viewer_model@test.com", role="VIEWER")
    resp = client.post("/api/v1/models/", json={
        "name": "forbidden-model",
        "display_name": "Forbidden Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    assert resp.status_code == 403


def test_create_duplicate_model_name_fails(client):
    headers = _get_auth_headers(client, email="dup_model_user@test.com", role="ML_ENGINEER")
    client.post("/api/v1/models/", json={
        "name": "unique-model-name",
        "display_name": "First Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)

    resp = client.post("/api/v1/models/", json={
        "name": "unique-model-name",
        "display_name": "Duplicate Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    assert resp.status_code == 400


def test_list_and_get_models(client):
    headers = _get_auth_headers(client, email="list_model_user@test.com", role="ML_ENGINEER")
    # List models (public / authenticated)
    resp = client.get("/api/v1/models/")
    assert resp.status_code == 200
    models = resp.json()
    assert isinstance(models, list)
    assert len(models) >= 1

    # Get specific model
    first_model = models[0]
    get_resp = client.get(f"/api/v1/models/{first_model['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == first_model["id"]


def test_upload_model_version(client):
    headers = _get_auth_headers(client, email="version_user@test.com", role="ML_ENGINEER")
    # Create model first
    model_resp = client.post("/api/v1/models/", json={
        "name": "version-test-model",
        "display_name": "Version Test Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    model_id = model_resp.json()["id"]

    # Upload mock model binary
    mock_file = io.BytesIO(b"fake-model-binary-weights-12345")
    feature_schema = json.dumps({
        "features": [
            {"name": "f1", "type": "float"},
            {"name": "f2", "type": "float"},
        ]
    })
    training_metrics = json.dumps({"accuracy": 0.98})

    resp = client.post(
        f"/api/v1/models/{model_id}/versions",
        data={
            "feature_schema": feature_schema,
            "training_metrics": training_metrics,
            "changelog": "Initial test version",
        },
        files={"file": ("model.pkl", mock_file, "application/octet-stream")},
        headers=headers,
    )
    assert resp.status_code == 201
    ver = resp.json()
    assert ver["model_id"] == model_id
    assert ver["version_number"] == 1
    assert ver["status"] == "READY"
    assert "file_hash" in ver
    assert ver["file_size_bytes"] == len(b"fake-model-binary-weights-12345")


def test_upload_version_invalid_json_schema(client):
    headers = _get_auth_headers(client, email="schema_err_user@test.com", role="ML_ENGINEER")
    model_resp = client.post("/api/v1/models/", json={
        "name": "bad-schema-model",
        "display_name": "Bad Schema Model",
        "framework": "SCIKIT_LEARN",
        "task_type": "CLASSIFICATION",
    }, headers=headers)
    model_id = model_resp.json()["id"]

    mock_file = io.BytesIO(b"dummy")
    resp = client.post(
        f"/api/v1/models/{model_id}/versions",
        data={
            "feature_schema": "not-valid-json-{{{",
        },
        files={"file": ("model.pkl", mock_file, "application/octet-stream")},
        headers=headers,
    )
    assert resp.status_code == 422
