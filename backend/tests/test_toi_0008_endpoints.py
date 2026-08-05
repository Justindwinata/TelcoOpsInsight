from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        login = test_client.post("/api/auth/login", json={"username": "admin", "password": "password"})
        token = login.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client


def test_workforce_summary(client: TestClient) -> None:
    response = client.get("/api/workforce/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_technicians" in data
    assert "available" in data
    assert "on_job" in data
    assert "avg_utilization_rate" in data


def test_list_technicians(client: TestClient) -> None:
    response = client.get("/api/workforce/technicians")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_technician_status_validation(client: TestClient) -> None:
    payload = {
        "name": "Invalid Status Tech",
        "employee_id": "INVALIDS",
        "region": "Jakarta",
        "assigned_team": "Field Ops",
        "status": "Invalid",
    }
    response = client.post("/api/workforce/technicians", json=payload)
    assert response.status_code == 422
    assert "Invalid status" in response.json()["detail"]


def test_workforce_skill_flow(client: TestClient) -> None:
    tech_payload = {
        "name": "Test Technician",
        "employee_id": "TD-100",
        "region": "Jakarta",
        "assigned_team": "Field Ops",
        "status": "Available",
    }
    tech_response = client.post("/api/workforce/technicians", json=tech_payload)
    assert tech_response.status_code == 200
    tech_id = tech_response.json()["technician_id"]

    skill_payload = {"skill_name": "Fiber Splicing", "skill_level": "Expert"}
    skill_response = client.post(f"/api/workforce/technicians/{tech_id}/skills", json=skill_payload)
    assert skill_response.status_code == 200

    skills_response = client.get(f"/api/workforce/technicians/{tech_id}/skills")
    assert skills_response.status_code == 200
    skills = skills_response.json()
    assert len(skills) >= 1


def test_workforce_leave_flow(client: TestClient) -> None:
    leave_payload = {
        "technician_id": "TECH-0001",
        "leave_type": "Annual",
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
        "days_requested": 5,
        "reason": "Vacation",
    }
    response = client.post("/api/workforce/leave-requests", json=leave_payload)
    if response.status_code == 200:
        leave_id = response.json()["leave_id"]
        approve_response = client.post(f"/api/workforce/leave-requests/{leave_id}/approve")
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "Approved"


def test_shifts_enpoint(client: TestClient) -> None:
    response = client.get("/api/workforce/shifts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dispatch_summary(client: TestClient) -> None:
    response = client.get("/api/dispatch/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_work_orders" in data
    assert "pending" in data
    assert "orders_by_priority" in data


def test_dispatch_work_orders(client: TestClient) -> None:
    response = client.get("/api/dispatch/work-orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_service_request_flow(client: TestClient) -> None:
    payload = {
        "customer_id": "CUST-100",
        "customer_name": "Test Customer",
        "service_type": "Installation",
        "description": "Install fiber connection",
        "priority": "High",
        "region": "Jakarta",
        "requested_date": "2026-08-01",
    }
    response = client.post("/api/service-requests", json=payload)
    if response.status_code == 200:
        request_id = response.json()["request_id"]
        submit_response = client.post(f"/api/service-requests/{request_id}/submit")
        assert submit_response.status_code == 200
        history_response = client.get(f"/api/service-requests/{request_id}/history")
        assert history_response.status_code == 200
        assert isinstance(history_response.json(), list)


def test_sla_monitoring_summary(client: TestClient) -> None:
    response = client.get("/api/sla-monitoring/summary")
    assert response.status_code == 200
    data = response.json()
    assert "breached_records" in data
    assert "breach_rate" in data
    assert "avg_mttr_minutes" in data


def test_sla_heatmap(client: TestClient) -> None:
    response = client.get("/api/sla-monitoring/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "heatmap" in data


def test_capacity_summary(client: TestClient) -> None:
    response = client.get("/api/capacity/summary")
    assert response.status_code == 200
    data = response.json()
    assert data is not None


def test_executive_decision_center(client: TestClient) -> None:
    response = client.get("/api/executive/decision-center")
    assert response.status_code == 200
    data = response.json()
    assert "top_priorities" in data
    assert "highest_risks" in data
    assert "recommended_actions" in data


def test_workforce_and_dispatch_integration(client: TestClient) -> None:
    workforce_response = client.get("/api/workforce/technicians")
    dispatch_response = client.get("/api/dispatch/work-orders")
    assert workforce_response.status_code == 200
    assert dispatch_response.status_code == 200