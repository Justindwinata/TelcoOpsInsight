from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as c:
        login = c.post("/api/auth/login", json={"username": "noc_manager", "password": "telco-demo-2026"})
        c.headers.update({"Authorization": f"Bearer {login.json()['access_token']}"})
        yield c

def test_event_publish_and_retrieve(client: TestClient) -> None:
    r = client.post("/api/events/publish", json={
        "event_type": "link_down",
        "severity": "Major",
        "title": "Test link down at SITE-001",
        "detail": "Test detail",
        "region": "Jakarta",
        "service_type": "Mobile",
        "site_id": "SITE-001"
    })
    assert r.status_code == 200
    data = r.json()
    assert "event_id" in data
    assert data["event_type"] == "link_down"
    assert data["severity"] == "Major"
    assert data["region"] == "Jakarta"

    list_r = client.get("/api/events/recent?limit=5")
    assert list_r.status_code == 200
    assert isinstance(list_r.json(), list)
    assert len(list_r.json()) > 0

def test_event_stats(client: TestClient) -> None:
    r = client.get("/api/events/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_events" in data
    assert "acknowledged" in data

def test_event_summary(client: TestClient) -> None:
    r1 = client.get("/api/events/summary/type")
    assert r1.status_code == 200
    assert isinstance(r1.json(), dict)
    
    r2 = client.get("/api/events/summary/severity")
    assert r2.status_code == 200
    assert isinstance(r2.json(), dict)

def test_simulator_start_stop(client: TestClient) -> None:
    start = client.post("/api/events/simulator/start?interval_seconds=10")
    assert start.status_code == 200
    assert start.json()["status"] in ("started", "already_running")
    
    stop = client.post("/api/events/simulator/stop")
    assert stop.status_code == 200
    assert stop.json()["status"] in ("stopped", "not_running")

def test_event_history(client: TestClient) -> None:
    r = client.get("/api/events/history?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_live_status_endpoints(client: TestClient) -> None:
    for endpoint in ["/api/live-status/regions", "/api/live-status/kpi", "/api/live-status/sla", "/api/live-status/operators"]:
        r = client.get(endpoint)
        assert r.status_code == 200
        assert isinstance(r.json(), dict)
