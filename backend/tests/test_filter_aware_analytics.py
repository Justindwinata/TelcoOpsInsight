from datetime import date

from app.filters import AnalyticsFilters
from app.services.analytics_service import incident_analytics, network_health, overview_metrics, rows
from app.services.dataset_service import seed_sample_dataset


def test_date_range_filter_reduces_incident_scope() -> None:
    seed_sample_dataset()

    unfiltered = incident_analytics()
    filtered = incident_analytics(filters=AnalyticsFilters(start_date=date(2026, 3, 1), end_date=date(2026, 3, 31)))

    assert len(filtered["incidents"]) <= len(unfiltered["incidents"])
    assert all(str(row["date"]).startswith("2026-03") for row in filtered["incidents"])


def test_status_and_team_filters_apply_to_relevant_datasets() -> None:
    seed_sample_dataset()

    incidents = incident_analytics(filters=AnalyticsFilters(status="Escalated", team="NOC Core"))

    assert incidents["incidents"]
    assert all(row["status"] == "Escalated" for row in incidents["incidents"])
    assert all(row["assigned_team"] == "NOC Core" for row in incidents["incidents"])


def test_service_type_filter_applies_to_quality_and_sla_metrics() -> None:
    seed_sample_dataset()

    health = network_health(filters=AnalyticsFilters(service_type="Enterprise VPN"))

    assert len(health["service_quality_summary"]) == 1
    assert health["service_quality_summary"][0]["name"] == "Enterprise VPN"


def test_filtered_overview_matches_filtered_source_rows() -> None:
    seed_sample_dataset()
    filters = AnalyticsFilters(region="Jakarta", month="2026-03")
    metrics = overview_metrics(filters=filters)
    expected_active = [
        row
        for row in rows("network_incidents")
        if row["region"] == "Jakarta" and row["month"] == "2026-03" and row["status"] in {"Open", "Investigating", "Escalated"}
    ]

    assert metrics["total_sites"] == 25
    assert metrics["active_incidents"] == len(expected_active)
