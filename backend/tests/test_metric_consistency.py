from __future__ import annotations

from typing import Any

from app.services.analytics_service import (
    ACTIVE_INCIDENT_STATUSES,
    BACKLOG_TICKET_STATUSES,
    COMPLETED_JOB_STATUSES,
    RESOLVED_INCIDENT_STATUSES,
    apply_filters,
    as_bool,
    as_float,
    avg,
    avg_by,
    overview_metrics,
    percent,
    rows,
)
from app.services.dataset_service import seed_sample_dataset


def assert_no_none(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            assert_no_none(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_none(child)
    else:
        assert value is not None


def test_overview_metric_consistency_against_seed_rows() -> None:
    seed_sample_dataset()
    incident_rows = rows("network_incidents")
    ticket_rows = rows("customer_tickets")
    sla_rows = rows("sla_metrics")
    quality_rows = rows("service_quality_metrics")
    job_rows = rows("field_technician_jobs")
    region_rows = rows("region_performance")

    active_incidents = [row for row in incident_rows if row["status"] in ACTIVE_INCIDENT_STATUSES]
    resolved_incidents = [row for row in incident_rows if row["status"] in RESOLVED_INCIDENT_STATUSES]
    backlog_tickets = [row for row in ticket_rows if row["status"] in BACKLOG_TICKET_STATUSES]
    completed_jobs = [row for row in job_rows if row["status"] in COMPLETED_JOB_STATUSES]

    expected = {
        "active_incidents": len(active_incidents),
        "resolved_incidents": len(resolved_incidents),
        "critical_incidents": len([row for row in active_incidents if row["severity"] == "Critical"]),
        "average_mttr_minutes": avg(as_float(row["duration_minutes"]) for row in resolved_incidents),
        "sla_achievement": avg(as_float(row["sla_actual"]) for row in sla_rows),
        "sla_breach_count": int(sum(as_float(row["breach_count"]) for row in sla_rows)),
        "open_ticket_backlog": len(backlog_tickets),
        "repeat_complaint_rate": percent(sum(1 for row in ticket_rows if as_bool(row["repeat_complaint"])), len(ticket_rows)),
        "first_time_fix_rate": percent(sum(1 for row in completed_jobs if as_bool(row["first_time_fix"])), len(completed_jobs)),
        "affected_customers": int(sum(as_float(row["affected_customers"]) for row in active_incidents)),
        "average_latency_ms": avg(as_float(row["latency_ms"]) for row in quality_rows),
        "packet_loss_rate": avg(as_float(row["packet_loss_rate"]) for row in quality_rows),
        "technician_utilization": avg(as_float(row["technician_utilization"]) for row in region_rows),
    }

    metrics = overview_metrics()

    for key, value in expected.items():
        assert metrics[key] == value
    assert_no_none(metrics)


def test_packet_loss_risk_regions_are_threshold_based() -> None:
    seed_sample_dataset()
    metrics = overview_metrics()
    expected = [
        item["name"]
        for item in avg_by(rows("service_quality_metrics"), "region", "packet_loss_rate")
        if as_float(item["value"]) >= 1.5
    ]

    assert metrics["high_packet_loss_regions"] == expected


def test_metric_helpers_handle_empty_and_zero_denominator_cases() -> None:
    assert avg([]) == 0.0
    assert percent(5, 0) == 0.0
    assert apply_filters([], region="Jakarta") == []


def test_unresolved_and_optional_relationships_do_not_break_metrics() -> None:
    seed_sample_dataset()
    incident_rows = rows("network_incidents")
    ticket_rows = rows("customer_tickets")

    assert any(row["status"] in ACTIVE_INCIDENT_STATUSES and row["resolved_time"] == "" for row in incident_rows)
    assert any(row["related_incident_id"] == "" for row in ticket_rows)
    assert overview_metrics()["active_incidents"] > 0
