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

def test_noc_command_center(client: TestClient) -> None:
    r = client.get("/api/noc/command-center")
    assert r.status_code == 200
    data = r.json()
    assert "network_overview" in data
    assert "regional_health" in data

def test_alarm_summary(client: TestClient) -> None:
    r = client.get("/api/alarms/summary")
    assert r.status_code == 200
    assert "total_active" in r.json()

def test_alarm_lifecycle(client: TestClient) -> None:
    create_r = client.post("/api/alarms", json={"severity": "Major", "category": "Network", "description": "Test alarm"})
    assert create_r.status_code == 200
    alarm_id = create_r.json()["alarm_id"]
    
    ack_r = client.post(f"/api/alarms/{alarm_id}/acknowledge")
    assert ack_r.status_code == 200
    assert ack_r.json()["status"] == "Acknowledged"

def test_major_incident_flow(client: TestClient) -> None:
    create_r = client.post("/api/major-incidents", json={"title": "Test MI", "severity": "High", "incident_commander": "admin"})
    assert create_r.status_code == 200
    mi_id = create_r.json()["mi_id"]
    
    timeline_r = client.get(f"/api/major-incidents/{mi_id}/timeline")
    assert timeline_r.status_code == 200

def test_calendar(client: TestClient) -> None:
    r = client.get("/api/calendar")
    assert r.status_code == 200
    assert "events" in r.json()

def test_export_json(client: TestClient) -> None:
    r = client.get("/api/exports/incidents/json")
    assert r.status_code == 200

def test_export_csv(client: TestClient) -> None:
    r = client.get("/api/exports/alarms/csv")
    assert r.status_code == 200

def test_business_dashboard(client: TestClient) -> None:
    r = client.get("/api/business/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "customer_impact" in data
    assert "revenue_impact" in data
    assert data["revenue_impact"]["note"] == "Synthetic demo data - illustrative only"
