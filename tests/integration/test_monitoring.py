"""
Integration tests for Monitoring, Health, and Telemetry routes.
"""
import pytest


def test_monitoring_stats_extended(client):
    resp = client.get("/api/v1/monitoring/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_models" in data
    assert "total_deployments" in data
    assert "active_deployments" in data
    assert "total_predictions" in data
    assert "successful_predictions" in data
    assert "failed_predictions" in data
    assert "avg_latency_ms" in data
    assert "total_batch_jobs" in data


def test_monitoring_logs(client):
    resp = client.get("/api/v1/monitoring/logs?limit=10")
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)


def test_prometheus_metrics_endpoint(client):
    resp = client.get("/api/v1/monitoring/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
