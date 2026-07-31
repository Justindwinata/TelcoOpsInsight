from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_overview_endpoint() -> None:
    response = client.get("/api/dashboard/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_sites"] == 250
    assert "network_uptime" in payload
    assert payload["affected_customers"] >= 0


def test_dashboard_overview_filter_endpoint() -> None:
    response = client.get("/api/dashboard/overview", params={"region": "Jakarta", "month": "2026-03"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_sites"] == 25
    assert payload["network_uptime"] > 0


def test_network_health_endpoint() -> None:
    response = client.get("/api/dashboard/network-health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["uptime_trend"]
    assert payload["latency_trend"]
    assert payload["packet_loss_trend"]
    assert payload["service_quality_summary"]


def test_incidents_endpoint() -> None:
    response = client.get("/api/dashboard/incidents", params={"severity": "Critical"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["incidents"]
    assert payload["severity_summary"]
    assert payload["root_cause_breakdown"]


def test_tickets_endpoint() -> None:
    response = client.get("/api/dashboard/tickets")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticket_volume"]
    assert payload["category_breakdown"]
    assert payload["backlog"] > 0


def test_sla_endpoint() -> None:
    response = client.get("/api/dashboard/sla", params={"service_type": "Enterprise VPN"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_vs_actual"]
    assert payload["breach_count"] >= 0
    assert payload["mttr_trend"]
