from app.services.analytics_service import avg, overview_metrics, percent
from app.services.dataset_service import seed_sample_dataset


def test_no_division_by_zero_helpers() -> None:
    assert percent(10, 0) == 0.0
    assert avg([]) == 0.0


def test_overview_metrics_are_calculated_from_seed_data() -> None:
    seed_sample_dataset()

    metrics = overview_metrics()

    assert metrics["total_sites"] == 250
    assert metrics["network_uptime"] > 90
    assert metrics["sla_achievement"] > 90
    assert metrics["average_mttr_minutes"] >= 0
    assert metrics["open_ticket_backlog"] > 0


def test_overview_filter_behavior() -> None:
    seed_sample_dataset()

    jakarta = overview_metrics(region="Jakarta")
    bandung = overview_metrics(region="Bandung")

    assert jakarta["total_sites"] == 25
    assert bandung["total_sites"] == 25
    assert jakarta["active_incidents"] != bandung["active_incidents"] or jakarta["affected_customers"] != bandung["affected_customers"]
