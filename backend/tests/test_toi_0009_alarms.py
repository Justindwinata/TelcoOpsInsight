import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as c:
        login = c.post("/api/auth/login", json={"username": "admin", "password": "password"})
    c.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
    yield c

def test_alarm_duplicate_detection(client: TestClient) -> None:
    payload = {"severity": "Major", "category": "Network", "site_id": "SITE-001", "description": "Duplicate test"}
    r1 = client.post("/api/alarms", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/alarms", json=payload)
    assert r2.status_code == 200
    assert r1.json()["alarm_id"] != r2.json()["alarm_id"]

def test_alarm_acknowledge_flow(client: TestClient) -> None:
    r = client.post("/api/alarms", json={"severity": "Critical", "category": "Equipment", "description": "Test ack"})
    alarm_id = r.json()["alarm_id"]
    ack = client.post(f"/api/alarms/{alarm_id}/acknowledge")
    assert ack.status_code == 200
    assert ack.json()["status"] == "Acknowledged"

def test_alarm_resolve_flow(client: TestClient) -> None:
    r = client.post("/api/alarms", json={"severity": "Minor", "category": "Performance", "description": "Test resolve"})
    alarm_id = r.json()["alarm_id"]
    res = client.post(f"/api/alarms/{alarm_id}/resolve", json={"notes": "Fixed by restart"})
    assert res.status_code == 200
    assert res.json()["status"] == "Resolved"
