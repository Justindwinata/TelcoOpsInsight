from __future__ import annotations

import sys
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


import pytest
from fastapi.testclient import TestClient

from app.main import app

DEMO_PASSWORD = "telco-demo-2026"


@pytest.fixture()
def manager_headers():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "noc_manager", "password": DEMO_PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_incident_lifecycle_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/incidents/lifecycle",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "lifecycle_stages" in data
    assert "total_incidents" in data
    assert "active_count" in data
    assert "resolved_count" in data
    assert "active_severity_breakdown" in data
    assert "oldest_active" in data
    stages = data["lifecycle_stages"]
    assert isinstance(stages, list)
    assert len(stages) == 5
    stage_names = [s["stage"] for s in stages]
    assert "Open" in stage_names
    assert "Closed" in stage_names
    assert data["total_incidents"] > 0


def test_incident_lifecycle_with_filter(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/incidents/lifecycle",
        params={"region": "Jakarta", "month": "2026-03"},
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "lifecycle_stages" in data
    assert "filter_metadata" in data


def test_technician_assignment_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/technicians/assignment",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "technicians" in data
    assert "team_capacity" in data
    assert "total_technicians" in data
    assert "active_jobs" in data
    assert data["total_technicians"] > 0
    techs = data["technicians"]
    assert isinstance(techs, list)
    assert len(techs) > 0
    first_tech = techs[0]
    assert "technician_id" in first_tech
    assert "capacity_ratio" in first_tech
    assert "first_time_fix_rate" in first_tech
    teams = data["team_capacity"]
    assert isinstance(teams, list)
    assert len(teams) > 0


def test_sla_escalation_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/sla/escalation",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "escalation_levels" in data
    assert "total_sla_records" in data
    assert "breached_records" in data
    assert "breach_rate" in data
    assert "avg_mttr_minutes" in data
    assert data["total_sla_records"] > 0
    levels = data["escalation_levels"]
    assert isinstance(levels, list)
    assert len(levels) == 4
    level_names = [l["level"] for l in levels]
    assert "NONE" in level_names
    assert "CRITICAL" in level_names


def test_outage_impact_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/incidents/outage-impact",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_active_incidents" in data
    assert "total_affected_customers" in data
    assert "severity_breakdown" in data
    assert "region_impact" in data
    assert "service_impact" in data
    assert isinstance(data["region_impact"], list)
    assert isinstance(data["service_impact"], list)


def test_notifications_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/notifications",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "total_count" in data
    assert "critical_count" in data
    assert "categories" in data
    assert isinstance(data["notifications"], list)
    if data["total_count"] > 0:
        first = data["notifications"][0]
        assert "id" in first
        assert "severity" in first
        assert "title" in first
        assert "category" in first
        assert "action_url" in first


def test_notifications_with_filter(manager_headers):
    client = TestClient(app)
    response = client.get(
        "/api/dashboard/notifications",
        params={"region": "Jakarta"},
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "filter_metadata" in data


def test_incident_lifecycle_viewer_access(manager_headers):
    client = TestClient(app)
    viewer_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": DEMO_PASSWORD},
    )
    viewer_headers = {"Authorization": f"Bearer {viewer_response.json()['access_token']}"}
    response = client.get(
        "/api/dashboard/incidents/lifecycle",
        headers=viewer_headers,
    )
    assert response.status_code == 200


def test_outage_impact_viewer_access(manager_headers):
    client = TestClient(app)
    viewer_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": DEMO_PASSWORD},
    )
    viewer_headers = {"Authorization": f"Bearer {viewer_response.json()['access_token']}"}
    response = client.get(
        "/api/dashboard/incidents/outage-impact",
        headers=viewer_headers,
    )
    assert response.status_code == 200
