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
    assert payload["filter_metadata"]["applied_filters"] == {"month": "2026-03", "region": "Jakarta"}


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


def test_incidents_drilldown_endpoint() -> None:
    response = client.get("/api/dashboard/incidents/drilldown", params={"region": "Jakarta"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["by_severity"]
    assert payload["by_root_cause"]
    assert payload["by_region"]
    assert payload["filter_metadata"]["applied_filters"]["region"] == "Jakarta"


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


def test_sla_drilldown_endpoint() -> None:
    response = client.get("/api/dashboard/sla/drilldown", params={"service_type": "Enterprise VPN"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["breach_detail"]
    assert payload["breaches_by_region"]
    assert payload["breaches_by_service"]


def test_technicians_endpoint() -> None:
    response = client.get("/api/dashboard/technicians")

    assert response.status_code == 200
    payload = response.json()
    assert payload["technician_workload"]
    assert payload["job_status_summary"]
    assert payload["first_time_fix_rate"] >= 0


def test_regions_endpoint() -> None:
    response = client.get("/api/dashboard/regions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["region_performance_ranking"]
    assert payload["region_health_metrics"]


def test_recommendations_endpoint() -> None:
    response = client.get("/api/dashboard/recommendations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["method"] == "deterministic_rule_based"
    assert payload["rules_evaluated"] >= 30
    assert "recommendations" in payload


def test_dashboard_endpoint_rejects_invalid_filter_value() -> None:
    response = client.get("/api/dashboard/overview", params={"region": "Invalid"})

    assert response.status_code == 422
    assert "Unsupported region" in response.text


def test_dashboard_endpoint_rejects_invalid_date_range() -> None:
    response = client.get("/api/dashboard/incidents", params={"start_date": "2026-03-02", "end_date": "2026-03-01"})

    assert response.status_code == 422
    assert "start_date must be before" in response.text
