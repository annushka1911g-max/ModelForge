"""
Integration tests for Batch Prediction Jobs.
Tests: batch job creation, processing, completion, failure on schema mismatch,
non-csv rejection, job status query, and results CSV download.
"""
import io
import pytest


def _get_auth_headers(client, email="batch_tester@test.com", role="ML_ENGINEER"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": "Batch Tester",
        "password": "Password123!",
        "role": role,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_batch_prediction_success(client):
    headers = _get_auth_headers(client, email="batch_success@test.com")

    # Sample Iris CSV
    csv_data = b"sepal_length,sepal_width,petal_length,petal_width\n5.1,3.5,1.4,0.2\n4.9,3.0,1.4,0.2\n"
    file = io.BytesIO(csv_data)

    resp = client.post(
        "/api/v1/batch/1/predict-batch",
        files={"file": ("test_batch.csv", file, "text/csv")},
        headers=headers,
    )
    assert resp.status_code == 202
    job = resp.json()
    assert job["deployment_id"] == 1
    assert job["total_records"] == 2
    assert job["status"] == "COMPLETED"
    assert job["processed_records"] == 2
    assert job["output_file_url"] is not None

    # Test download results
    job_id = job["id"]
    dl_resp = client.get(f"/api/v1/batch/jobs/{job_id}/download", headers=headers)
    assert dl_resp.status_code == 200
    assert "prediction" in dl_resp.text


def test_batch_prediction_schema_mismatch_fails(client):
    headers = _get_auth_headers(client, email="batch_mismatch@test.com")

    # Wrong schema: churn features instead of iris
    csv_data = b"age,tenure,monthly_charges\n45,3,75.5\n"
    file = io.BytesIO(csv_data)

    resp = client.post(
        "/api/v1/batch/1/predict-batch",
        files={"file": ("mismatched.csv", file, "text/csv")},
        headers=headers,
    )
    assert resp.status_code == 202
    job = resp.json()
    assert job["status"] == "FAILED"
    assert "Feature schema validation failed" in job["error_message"]


def test_batch_prediction_rejects_non_csv(client):
    headers = _get_auth_headers(client, email="batch_noncsv@test.com")
    file = io.BytesIO(b'{"key": "value"}')

    resp = client.post(
        "/api/v1/batch/1/predict-batch",
        files={"file": ("data.json", file, "application/json")},
        headers=headers,
    )
    assert resp.status_code == 400


def test_list_batch_jobs(client):
    headers = _get_auth_headers(client, email="batch_list_user@test.com")
    resp = client.get("/api/v1/batch/jobs", headers=headers)
    assert resp.status_code == 200
    jobs = resp.json()
    assert isinstance(jobs, list)
