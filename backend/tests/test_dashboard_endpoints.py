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
