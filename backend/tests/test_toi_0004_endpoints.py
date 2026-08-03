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


def test_asset_inventory_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get("/api/assets/inventory", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_assets" in data
    assert data["total_assets"] > 0
    assert "asset_types" in data
    assert "asset_statuses" in data
    assert "health_score" in data
    assert "faulty_count" in data


def test_asset_detail_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get("/api/assets/detail", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert "total" in data
    assert data["total"] > 0
    first = data["assets"][0]
    assert "asset_id" in first
    assert "asset_type" in first
    assert "status" in first
    assert "ownership" in first


def test_asset_inventory_with_filter(manager_headers):
    client = TestClient(app)
    response = client.get("/api/assets/inventory", params={"region": "Jakarta"}, headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_assets" in data
    assert "filter_metadata" in data


def test_maintenance_schedule_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get("/api/maintenance/schedule", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "preventive_count" in data
    assert "corrective_count" in data
    assert "upcoming_count" in data
    assert "completed_count" in data
    assert "job_type_breakdown" in data
    assert "upcoming_jobs" in data
    assert "completed_jobs" in data
    assert data["total_jobs"] > 0


def test_change_management_create_and_transition(manager_headers):
    client = TestClient(app)
    create = client.post(
        "/api/changes",
        headers=manager_headers,
        json={
            "title": "Test Change TOI-0004",
            "change_type": "Planned Change",
            "risk_level": "Medium",
            "region": "Jakarta",
            "service_type": "Fiber Internet",
            "description": "Testing change management workflow",
            "rollback_plan": "Rollback config to previous version",
        },
    )
    assert create.status_code == 200
    change = create.json()
    assert change["change_id"].startswith("CHG-")
    assert change["status"] == "Draft"

    transition = client.post(
        f"/api/changes/{change['change_id']}/transition",
        headers=manager_headers,
        json={"new_status": "Pending Approval"},
    )
    assert transition.status_code == 200
    assert transition.json()["status"] == "Pending Approval"


def test_change_management_summary(manager_headers):
    client = TestClient(app)
    response = client.get("/api/changes/summary", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_changes" in data
    assert "by_status" in data
    assert "by_type" in data
    assert "recent_changes" in data
    assert "approval_rate" in data


def test_rca_create_and_summary(manager_headers):
    client = TestClient(app)
    create = client.post(
        "/api/rca",
        headers=manager_headers,
        json={
            "incident_id": "INC-0001",
            "title": "Test RCA TOI-0004",
            "root_cause_category": "Equipment Failure",
            "root_cause_description": "Test description",
            "resolution": "Replaced faulty module",
            "lessons_learned": "Add monitoring",
            "method": "5 Whys",
            "status": "Draft",
            "severity": "High",
            "region": "Jakarta",
            "service_type": "Fiber Internet",
        },
    )
    assert create.status_code == 200
    rca = create.json()
    assert rca["rca_id"].startswith("RCA-")
    assert rca["root_cause_category"] == "Equipment Failure"

    summary = client.get("/api/rca/summary", headers=manager_headers)
    assert summary.status_code == 200
    assert "total_rcas" in summary.json()


def test_rca_invalid_category_rejected(manager_headers):
    client = TestClient(app)
    response = client.post(
        "/api/rca",
        headers=manager_headers,
        json={
            "root_cause_category": "Invalid Category",
            "method": "5 Whys",
        },
    )
    assert response.status_code == 422


def test_incident_timeline_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get("/api/timeline/incidents", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_incidents" in data
    assert "timelines" in data
    assert "with_escalation" in data
    assert data["total_incidents"] > 0


def test_executive_summary_endpoint(manager_headers):
    client = TestClient(app)
    response = client.get("/api/reports/executive/summary", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert "kpi_comparison" in data
    assert "monthly_trend" in data
    assert "region_comparison" in data
    assert "service_trend" in data
    assert "period" in data
