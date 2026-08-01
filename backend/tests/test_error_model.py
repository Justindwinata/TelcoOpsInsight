from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import auth_headers


client = TestClient(app)


def test_auth_failure_uses_consistent_error_model() -> None:
    response = client.post("/api/auth/login", json={"username": "noc_manager", "password": "wrong"})

    assert response.status_code == 401
    payload = response.json()
    assert payload["detail"] == "Invalid username or password"
    assert payload["error"]["code"] == "auth_failed"
    assert payload["error"]["message"] == "Invalid username or password"


def test_permission_denied_uses_consistent_error_model() -> None:
    response = client.post("/api/datasets/seed", headers=auth_headers(client, "viewer"))

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "permission_denied"
    assert "datasets:seed" in payload["error"]["message"]


def test_invalid_filter_uses_consistent_error_model() -> None:
    response = client.get(
        "/api/dashboard/overview",
        params={"start_date": "2026-02-01", "end_date": "2026-01-01"},
        headers=auth_headers(client, "noc_manager"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["message"] == "start_date must be before or equal to end_date"


def test_missing_import_rollback_uses_consistent_error_model() -> None:
    response = client.post("/api/datasets/import-history/IMP-MISSING/rollback", headers=auth_headers(client, "noc_manager"))

    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Import history record not found"


def test_invalid_request_shape_uses_consistent_error_model() -> None:
    response = client.post("/api/auth/login", json={"username": "noc_manager"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
