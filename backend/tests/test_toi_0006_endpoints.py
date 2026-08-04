import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.intelligence_service import (
    compute_operational_health,
    identify_critical_alerts,
    detect_risk_indicators,
    identify_opportunities,
)
from app.services.brief_service import (
    compute_key_metrics,
    generate_recommended_actions,
    compute_daily_comparison,
)
from app.services.trend_service import (
    detect_recurring_incidents,
    detect_increasing_failures,
    detect_stable_services,
)
from app.services.ranking_service import (
    compute_region_scores,
    generate_regional_insights,
)
from app.services.tech_performance_service import (
    compute_technician_scores,
)
from app.services.operational_timeline_service import (
    operational_timeline,
)
from app.services.simulation_service import (
    simulate_technician_change,
    simulate_response_time_change,
    compute_baseline,
)
from app.services.recommendation_service import (
    priority_score,
    confidence_level,
    estimated_urgency_window,
    actionability_score,
)


client = TestClient(app)


def test_intelligence_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/intelligence", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "operational_health" in data
    assert "critical_alerts" in data
    assert "risk_indicators" in data


def test_brief_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/brief", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "executive_summary" in data
    assert "recommended_actions" in data


def test_trends_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/trends", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "recurring_incidents" in data
    assert "increasing_failures" in data
    assert "stable_services" in data


def test_region_ranking_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/ranking/regions", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "rankings" in data
    assert len(data["rankings"]) > 0
    assert "rank" in data["rankings"][0]


def test_tech_ranking_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/ranking/technicians", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "rankings" in data
    assert "team_summary" in data


def test_timeline_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/operational-timeline", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "timeline" in data
    assert "summary" in data


def test_what_if_endpoint():
    from tests.auth_helpers import auth_headers
    h = auth_headers(client)
    
    r = client.get("/api/dashboard/what-if?technician_change=5", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "baseline" in data
    assert "scenarios" in data


def test_priority_score():
    assert priority_score("Critical", 10, 5) == 200.0
    assert priority_score("Medium", 10, 5) == 80.0


def test_confidence_level():
    assert confidence_level(10, 5) == "High"
    assert confidence_level(6, 5) == "Medium"
    assert confidence_level(4, 5) == "Medium"


def test_urgency_window():
    result = estimated_urgency_window("Critical", 10, 5)
    assert "deadline" in result
    assert result["urgency_level"] in ("Immediate", "High", "Medium", "Low")


def test_actionability():
    result = actionability_score("network_uptime", "Critical", True, True)
    assert result["score"] >= 70
    assert result["actionability"] in ("High", "Medium", "Low")


def test_compute_operational_health():
    incidents = [
        {"status": "Open", "severity": "Critical"},
        {"status": "Resolved", "severity": "Medium"},
    ]
    slas = [{"sla_actual": 98, "sla_target": 99}]
    assets = [{"status": "Active"}, {"status": "Faulty"}]
    
    result = compute_operational_health(incidents, slas, assets)
    assert "overall_score" in result
    assert "status" in result


def test_critical_alerts():
    incidents = [{"status": "Open", "severity": "Critical"}]
    slas = [{"sla_actual": 90, "sla_target": 99}]
    assets = [{"status": "Faulty"}]
    
    alerts = identify_critical_alerts(incidents, slas, assets)
    assert len(alerts) >= 2


def test_risk_indicators():
    incidents = [{"status": "Open", "severity": "Critical"}] * 5
    slas = [{"sla_actual": 90, "sla_target": 99}] * 20
    tickets = [{"status": "Open"}] * 150
    
    risks = detect_risk_indicators(incidents, slas, tickets)
    assert len(risks) >= 2


def test_recurring_incidents():
    incidents = [
        {"region": "Jakarta", "service_type": "Mobile", "root_cause": "Equipment Failure", "date": "2026-01-01"},
        {"region": "Jakarta", "service_type": "Mobile", "root_cause": "Equipment Failure", "date": "2026-02-01"},
        {"region": "Jakarta", "service_type": "Mobile", "root_cause": "Equipment Failure", "date": "2026-03-01"},
    ]
    
    recurring = detect_recurring_incidents(incidents)
    assert len(recurring) == 1
    assert recurring[0]["occurrence_count"] == 3


def test_increasing_failures():
    by_month = {
        "2026-01": {("Jakarta", "Mobile"): 2},
        "2026-02": {("Jakarta", "Mobile"): 5},
    }
    
    increasing = detect_increasing_failures(by_month)
    assert len(increasing) == 1
    assert increasing[0]["growth_percent"] > 0


def test_stable_services():
    incidents = [{"service_type": "Fixed"}]
    
    stable = detect_stable_services(incidents)
    assert len(stable) == 1


def test_region_scores():
    data = {
        "incidents": 2, "critical": 0, "resolved_incidents": 2, "mttr_values": [30],
        "sla_actual": [99], "sla_target": [99], "breaches": 0,
        "open_tickets": 5, "satisfaction": [4.5],
        "assets_active": 100, "assets_faulty": 0,
        "jobs_completed": 50, "jobs_total": 50, "ftf_count": 40,
    }
    
    scores = compute_region_scores("Jakarta", data)
    assert "composite" in scores
    assert scores["composite"] > 0


def test_tech_scores():
    data = {
        "total_jobs": 100, "completed_jobs": 95, "ftf_count": 80,
        "completion_times": [30, 45, 60], "dispatch_times": [10, 15],
        "active_jobs": 5, "critical_jobs": 5, "critical_completed": 5,
    }
    
    scores = compute_technician_scores(data)
    assert "composite" in scores
    assert scores["resolution_rate"] == 95


def test_baseline():
    incidents = [{"status": "Open"}, {"status": "Resolved", "duration_minutes": 30}]
    slas = [{"sla_actual": 99, "sla_target": 99}]
    tickets = [{"status": "Open"}]
    assets = [{"status": "Active"}]
    jobs = [{"status": "Open"}]
    
    baseline = compute_baseline(incidents, slas, tickets, assets, jobs)
    assert baseline["active_incidents"] == 1
    assert baseline["sla_achievement"] == 99


def test_simulation_tech():
    jobs = [{"status": "Open", "technician_id": "T1"}, {"status": "Resolved"}]
    incidents = [{"status": "Open"}]
    
    result = simulate_technician_change(jobs, incidents, 5)
    assert "projected_active_jobs" in result


def test_simulation_response():
    incidents = [{"status": "Resolved", "duration_minutes": 60}]
    
    result = simulate_response_time_change(incidents, -20)
    assert result["projected_mttr_minutes"] < 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])