from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import auth_headers


client = TestClient(app)


def test_audit_logs_capture_login_seed_and_report() -> None:
    manager = auth_headers(client, "noc_manager")
    client.post("/api/datasets/seed", headers=manager)
    client.get("/api/reports/executive-summary", headers=manager)

    response = client.get("/api/audit-logs", headers=manager)
    payload = response.json()
    actions = {row["action"] for row in payload["audit_logs"]}

    assert response.status_code == 200
    assert "auth.login" in actions
    assert "datasets.seed" in actions
    assert "reports.generate" in actions


def test_audit_logs_capture_permission_denied() -> None:
    viewer = auth_headers(client, "viewer")
    client.post("/api/datasets/seed", headers=viewer)

    manager = auth_headers(client, "noc_manager")
    response = client.get("/api/audit-logs", params={"action": "permission.denied"}, headers=manager)

    assert response.status_code == 200
    assert response.json()["count"] > 0


def test_viewer_cannot_read_audit_logs() -> None:
    response = client.get("/api/audit-logs", headers=auth_headers(client, "viewer"))

    assert response.status_code == 403
