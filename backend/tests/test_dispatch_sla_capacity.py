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


def test_dispatch_assignment_lifecycle(client: TestClient) -> None:
    wo_payload = {
        "job_type": "Repair",
        "priority": "High",
        "region": "Jakarta",
        "service_type": "Mobile",
        "site_id": "SITE-001",
        "description": "Urgent repair needed",
        "estimated_duration_minutes": 120,
        "scheduled_start": "2026-08-06T10:00:00",
    }
    wo_response = client.post("/api/dispatch/work-orders", json=wo_payload)
    assert wo_response.status_code == 200
    work_order_id = wo_response.json()["work_order_id"]

    assign_response = client.post(f"/api/dispatch/work-orders/{work_order_id}/assign", json={"technician_id": "TECH-0001", "notes": "Urgent dispatch"})
    assert assign_response.status_code == 200
    assignment_id = assign_response.json()["assignment_id"]

    ack_response = client.post(f"/api/dispatch/assignments/{assignment_id}/acknowledge")
    assert ack_response.status_code == 200
    assert ack_response.json()["status"] == "In Progress"

    start_response = client.post(f"/api/dispatch/assignments/{assignment_id}/start")
    assert start_response.status_code == 200

    complete_response = client.post(f"/api/dispatch/assignments/{assignment_id}/complete", json={"notes": "Repaired successfully"})
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "Completed"

    wo_check = client.get(f"/api/work-orders")
    assert wo_response.status_code == 200


def test_dispatch_route_management(client: TestClient) -> None:
    wo_payload = {
        "job_type": "Maintenance",
        "priority": "Normal",
        "region": "Surabaya",
        "service_type": "Fiber",
        "site_id": "SITE-002",
        "description": "Routine maintenance",
        "estimated_duration_minutes": 240,
        "scheduled_start": "2026-08-10T08:00:00",
    }
    wo_response = client.post("/api/dispatch/work-orders", json=wo_payload)
    assert wo_response.status_code == 200
    work_order_id = wo_response.json()["work_order_id"]

    route_payload = {
        "route_json": '{"distance": 45.2, "points": ["SITE-001", "SITE-002", "SITE-003"]}',
        "distance_km": 45.2,
        "estimated_duration_minutes": 90,
        "eta_timestamp": "2026-08-10T09:30:00",
    }
    route_response = client.post(f"/api/dispatch/work-orders/{work_order_id}/route", json=route_payload)
    assert route_response.status_code == 200
    assert route_response.json()["route_status"] == "Active"

    get_route = client.get(f"/api/dispatch/work-orders/{work_order_id}/route")
    assert get_route.status_code == 200
    assert "eta_timestamp" in get_route.json()

    status_response = client.post(f"/api/dispatch/routes/{get_route.json()['route_id']}/status", json={"status": "Completed"})
    assert status_response.status_code == 200


def test_dispatch_invalid_work_order(client: TestClient) -> None:
    response = client.get("/api/dispatch/work-orders/NONEXISTENT")
    assert response.status_code == 404


def test_dispatch_invalid_priority_validation(client: TestClient) -> None:
    payload = {
        "job_type": "Installation",
        "priority": "InvalidPriority",
        "region": "Bandung",
        "service_type": "Fiber",
    }
    response = client.post("/api/dispatch/work-orders", json=payload)
    assert response.status_code == 422


def test_sla_monitoring_breach_alerts(client: TestClient) -> None:
    response = client.get("/api/sla-monitoring/breaches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    breach_payload = {
        "incident_id": "INC-TEST",
        "region": "Jakarta",
        "service_type": "Mobile",
        "sla_target": 99.0,
        "sla_actual": 95.5,
        "breach_gap": 3.5,
        "severity": "High",
        "mttr_minutes": 120,
    }
    create_response = client.post("/api/sla-monitoring/breaches", json=breach_payload)
    assert create_response.status_code == 200
    alert_id = create_response.json()["alert_id"]

    ack_response = client.post(f"/api/sla-monitoring/breaches/{alert_id}/acknowledge")
    assert ack_response.status_code == 200

    resolve_response = client.post(f"/api/sla-monitoring/breaches/{alert_id}/resolve")
    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "Resolved"


def test_sla_monitoring_invalid_breach(client: TestClient) -> None:
    response = client.get("/api/sla-monitoring/breaches/INVALID-ID")
    assert response.status_code == 404


def test_capacity_planning_metrics(client: TestClient) -> None:
    response = client.get("/api/capacity/utilization")
    assert response.status_code == 200
    data = response.json()
    assert "by_service" in data
    assert "by_region" in data

    site_response = client.get("/api/capacity/sites")
    assert site_response.status_code == 200
    assert "sites" in site_response.json()
    assert "upgrade_recommendations" in site_response.json()

    backbone_response = client.get("/api/capacity/backbone")
    assert backbone_response.status_code == 200
    assert "avg_utilization_pct" in backbone_response.json()


def test_capacity_planning_summary(client: TestClient) -> None:
    response = client.get("/api/capacity/summary")
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert isinstance(data, dict)


def test_executive_decision_center_data(client: TestClient) -> None:
    response = client.get("/api/executive/decision-center")
    assert response.status_code == 200
    data = response.json()
    assert "top_priorities" in data
    assert len(data["top_priorities"]) >= 10
    assert "highest_risks" in data
    assert "critical_incidents" in data
    assert "network_health" in data
    assert "recommended_actions" in data


def test_workforce_and_dispatch_integration(client: TestClient) -> None:
    wf = client.get("/api/workforce/summary")
    dp = client.get("/api/dispatch/summary")
    assert wf.status_code == 200
    assert dp.status_code == 200