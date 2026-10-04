"""
Integration tests for Real-time Inference and Validation.
Tests: Iris prediction, missing features, unexpected features, wrong types,
stopped deployments, missing deployments, and prediction logging.
"""
import pytest


def _get_auth_headers(client, email="infer_user@test.com", role="ML_ENGINEER"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Inference Tester",
        "password": "Password123!",
        "role": role,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_valid_iris_prediction(client):
    headers = _get_auth_headers(client, email="pred_valid@test.com")
    resp = client.post(
        "/api/v1/deployments/1/predict",
        json={
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        },
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data
    assert "latency_ms" in data
    assert "model_version" in data
    assert "timestamp" in data
    assert data["prediction"] == [0]


def test_prediction_missing_feature_returns_422(client):
    headers = _get_auth_headers(client, email="pred_missing@test.com")
    resp = client.post(
        "/api/v1/deployments/1/predict",
        json={
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                # petal_length is missing!
                "petal_width": 0.2,
            }
        },
        headers=headers,
    )
    assert resp.status_code == 422
    assert "petal_length" in resp.json()["detail"]


def test_prediction_unexpected_feature_returns_422(client):
    headers = _get_auth_headers(client, email="pred_extra@test.com")
    resp = client.post(
        "/api/v1/deployments/1/predict",
        json={
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
                "unknown_extra_feature": 99.9,
            }
        },
        headers=headers,
    )
    assert resp.status_code == 422
    assert "Unexpected feature" in resp.json()["detail"]


def test_prediction_wrong_type_returns_422(client):
    headers = _get_auth_headers(client, email="pred_type@test.com")
    resp = client.post(
        "/api/v1/deployments/1/predict",
        json={
            "features": {
                "sepal_length": "not_a_float",
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        },
        headers=headers,
    )
    assert resp.status_code == 422
    assert "must be a float" in resp.json()["detail"]


def test_prediction_deployment_not_found(client):
    headers = _get_auth_headers(client, email="pred_notfound@test.com")
    resp = client.post(
        "/api/v1/deployments/999999/predict",
        json={
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        },
        headers=headers,
    )
    assert resp.status_code == 404


def test_prediction_logs_endpoint(client):
    headers = _get_auth_headers(client, email="pred_log_user@test.com")
    # Make a prediction
    client.post(
        "/api/v1/deployments/1/predict",
        json={
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        },
        headers=headers,
    )

    # Check logs
    resp = client.get("/api/v1/deployments/1/logs", headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1
    assert logs[0]["deployment_id"] == 1
