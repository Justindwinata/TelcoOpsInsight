from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from functools import lru_cache
from typing import Iterable, Any

from app.database import fetch_all
from app.filters import AnalyticsFilters
from app.services.dataset_service import database_has_seed_data, seed_sample_dataset


ACTIVE_INCIDENT_STATUSES = {"Open", "Investigating", "Escalated"}
RESOLVED_INCIDENT_STATUSES = {"Resolved", "Closed"}
BACKLOG_TICKET_STATUSES = {"Open", "In Progress", "Waiting Customer"}
COMPLETED_JOB_STATUSES = {"Resolved", "Closed"}


def ensure_seeded() -> None:
    """Ensure database has seed data before querying.
    
    Auto-seeds if missing to prevent query failures.
    """
    try:
        if not database_has_seed_data():
            seed_sample_dataset()
    except Exception as exc:
        raise RuntimeError(f"Failed to ensure seed data: {exc}") from exc


def rows(table: str) -> list[dict[str, object]]:
    """Fetch all rows from a table with error handling."""
    ensure_seeded()
    try:
        return fetch_all(f'SELECT * FROM "{table}"')
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch data from table {table}: {exc}") from exc


def fetch_rows(tables: list[str]) -> dict[str, list[dict[str, object]]]:
    """Fetch multiple tables in one call to reduce duplication."""
    result = {}
    for table in tables:
        result[table] = rows(table)
    return result


def filter_rows(data: list[dict[str, object]], query: AnalyticsFilters) -> list[dict[str, object]]:
    """Apply filters to a dataset."""
    return apply_filters(data, query)


def as_float(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_bool(value: object) -> bool:
    return str(value).lower() == "true"


def avg(values: Iterable[float]) -> float:
    clean = [value for value in values if value is not None]
    return round(sum(clean) / len(clean), 3) if clean else 0.0


def percent(part: float, total: float) -> float:
    return round((part / total) * 100, 3) if total else 0.0


def normalize_filters(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    month: str | None = None,
    region: str | None = None,
    service_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    team: str | None = None,
) -> AnalyticsFilters:
    if filters is not None:
        return filters
    return AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        service_type=service_type,
        severity=severity,
        status=status,
        team=team,
    )


def row_date(row: dict[str, object]) -> date | None:
    value = row.get("date") or str(row.get("timestamp", ""))[:10]
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def apply_filters(
    data: list[dict[str, object]],
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    month: str | None = None,
    region: str | None = None,
    service_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    team: str | None = None,
) -> list[dict[str, object]]:
    query = normalize_filters(
        filters,
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        service_type=service_type,
        severity=severity,
        status=status,
        team=team,
    )
    filtered: list[dict[str, object]] = []
    for row in data:
        date_value = row_date(row)
        if query.start_date and (date_value is None or date_value < query.start_date):
            continue
        if query.end_date and (date_value is None or date_value > query.end_date):
            continue
        if query.region and row.get("region") != query.region:
            continue
        if query.service_type and row.get("service_type") != query.service_type:
            continue
        if query.severity and row.get("severity") != query.severity and row.get("priority") != query.severity:
            continue
        if query.status and row.get("status") != query.status:
            continue
        if query.team and row.get("assigned_team") != query.team:
            continue
        if query.month and row.get("month") != query.month:
            continue
        filtered.append(row)
    return filtered


def count_by(data: Iterable[dict[str, object]], field: str) -> list[dict[str, object]]:
    counts = Counter(str(row.get(field, "Unknown")) for row in data)
    return [{"name": key, "value": value} for key, value in sorted(counts.items())]


def avg_by(data: Iterable[dict[str, object]], group_field: str, value_field: str) -> list[dict[str, object]]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in data:
        buckets[str(row.get(group_field, "Unknown"))].append(as_float(row.get(value_field)))
    return [{"name": key, "value": avg(values)} for key, values in sorted(buckets.items())]


def sum_by(data: Iterable[dict[str, object]], group_field: str, value_field: str) -> list[dict[str, object]]:
    totals: defaultdict[str, float] = defaultdict(float)
    for row in data:
        totals[str(row.get(group_field, "Unknown"))] += as_float(row.get(value_field))
    return [{"name": key, "value": round(value, 3)} for key, value in sorted(totals.items())]


def latest_by_region(data: list[dict[str, object]]) -> list[dict[str, object]]:
    latest: dict[str, dict[str, object]] = {}
    for row in sorted(data, key=lambda item: str(item.get("date", ""))):
        latest[str(row.get("region"))] = row
    return list(latest.values())


def overview_metrics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    service_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    team: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(
        filters,
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        service_type=service_type,
        severity=severity,
        status=status,
        team=team,
    )
    site_rows = apply_filters(rows("network_sites"), region=query.region, service_type=query.service_type)
    incident_rows = apply_filters(rows("network_incidents"), query)
    ticket_rows = apply_filters(rows("customer_tickets"), query)
    sla_rows = apply_filters(rows("sla_metrics"), query)
    quality_rows = apply_filters(rows("service_quality_metrics"), query)
    job_rows = apply_filters(rows("field_technician_jobs"), query)
    region_rows = apply_filters(rows("region_performance"), query)

    active_incidents = [row for row in incident_rows if row.get("status") in ACTIVE_INCIDENT_STATUSES]
    resolved_incidents = [row for row in incident_rows if row.get("status") in RESOLVED_INCIDENT_STATUSES]
    critical_active = [row for row in active_incidents if row.get("severity") == "Critical"]
    backlog_tickets = [row for row in ticket_rows if row.get("status") in BACKLOG_TICKET_STATUSES]
    completed_jobs = [row for row in job_rows if row.get("status") in COMPLETED_JOB_STATUSES]

    return {
        "total_sites": len(site_rows),
        "active_incidents": len(active_incidents),
        "critical_incidents": len(critical_active),
        "resolved_incidents": len(resolved_incidents),
        "average_mttr_minutes": avg(as_float(row.get("duration_minutes")) for row in resolved_incidents),
        "network_uptime": avg(as_float(row.get("uptime_percentage")) for row in sla_rows),
        "sla_achievement": avg(as_float(row.get("sla_actual")) for row in sla_rows),
        "sla_breach_count": int(sum(as_float(row.get("breach_count")) for row in sla_rows)),
        "average_latency_ms": avg(as_float(row.get("latency_ms")) for row in quality_rows),
        "packet_loss_rate": avg(as_float(row.get("packet_loss_rate")) for row in quality_rows),
        "high_packet_loss_regions": [
            item["name"] for item in avg_by(quality_rows, "region", "packet_loss_rate") if as_float(item["value"]) >= 1.5
        ],
        "open_ticket_backlog": len(backlog_tickets),
        "repeat_complaint_rate": percent(sum(1 for row in ticket_rows if as_bool(row.get("repeat_complaint"))), len(ticket_rows)),
        "technician_utilization": avg(as_float(row.get("technician_utilization")) for row in region_rows),
        "first_time_fix_rate": percent(sum(1 for row in completed_jobs if as_bool(row.get("first_time_fix"))), len(completed_jobs)),
        "field_job_completion_time_minutes": avg(
            as_float(row.get("completion_time_minutes")) for row in completed_jobs if row.get("completion_time_minutes") != ""
        ),
        "affected_customers": int(sum(as_float(row.get("affected_customers")) for row in active_incidents)),
        "customer_satisfaction": avg(as_float(row.get("customer_satisfaction")) for row in region_rows),
    }


def network_health(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    service_type: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(filters, start_date=start_date, end_date=end_date, month=month, region=region, service_type=service_type)
    sla_rows = apply_filters(rows("sla_metrics"), query)
    quality_rows = apply_filters(rows("service_quality_metrics"), query)
    return {
        "uptime_trend": avg_by(sla_rows, "month", "uptime_percentage"),
        "latency_trend": avg_by(quality_rows, "month", "latency_ms"),
        "packet_loss_trend": avg_by(quality_rows, "month", "packet_loss_rate"),
        "service_quality_summary": avg_by(quality_rows, "service_type", "quality_score"),
    }


def incident_analytics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    service_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    team: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(
        filters,
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        service_type=service_type,
        severity=severity,
        status=status,
        team=team,
    )
    incident_rows = apply_filters(rows("network_incidents"), query)
    latest = sorted(incident_rows, key=lambda row: (str(row.get("date", "")), str(row.get("incident_id", ""))), reverse=True)[:80]
    return {
        "incidents": latest,
        "severity_summary": count_by(incident_rows, "severity"),
        "incident_trend": count_by(incident_rows, "month"),
        "root_cause_breakdown": count_by(incident_rows, "root_cause"),
        "top_root_causes": sorted(count_by(incident_rows, "root_cause"), key=lambda item: item["value"], reverse=True)[:5],
    }


def incident_drilldown(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    incident_rows = apply_filters(rows("network_incidents"), filters)
    return {
        "by_severity": count_by(incident_rows, "severity"),
        "by_root_cause": sorted(count_by(incident_rows, "root_cause"), key=lambda item: item["value"], reverse=True),
        "by_region": sorted(count_by(incident_rows, "region"), key=lambda item: item["value"], reverse=True),
        "active_by_region": sorted(
            count_by([row for row in incident_rows if row.get("status") in ACTIVE_INCIDENT_STATUSES], "region"),
            key=lambda item: item["value"],
            reverse=True,
        ),
        "critical_incidents": [
            row for row in sorted(incident_rows, key=lambda item: str(item.get("date", "")), reverse=True) if row.get("severity") == "Critical"
        ][:40],
    }


INCIDENT_LIFECYCLE_STAGES = [
    ("Open", "Open", "Initial detection. Awaiting triage and assignment."),
    ("Investigating", "Assigned", "Assigned to a team. Active investigation underway."),
    ("Escalated", "In Progress", "Escalated to specialized response. Work in progress."),
    ("Resolved", "Monitoring", "Root cause addressed. Monitoring service recovery."),
    ("Closed", "Closed", "Resolution confirmed. Incident closed."),
]

LIFECYCLE_STAGE_ORDER = {
    "Open": 0,
    "Investigating": 1,
    "Escalated": 2,
    "Resolved": 3,
    "Closed": 4,
}


def incident_lifecycle(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute incident lifecycle stage distribution and progression analytics.

    Maps current incident status to lifecycle stages and computes
    progression indicators for executive NOC monitoring.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    total = len(incident_rows)
    by_stage = []
    for stage_key, stage_label, _description in INCIDENT_LIFECYCLE_STAGES:
        count = sum(1 for row in incident_rows if str(row.get("status", "")) == stage_key)
        by_stage.append(
            {
                "stage": stage_key,
                "label": stage_label,
                "count": count,
                "percentage": percent(count, total),
            }
        )

    active = [row for row in incident_rows if row.get("status") in ACTIVE_INCIDENT_STATUSES]
    resolved = [row for row in incident_rows if row.get("status") in RESOLVED_INCIDENT_STATUSES]

    avg_duration_active = avg(
        as_float(row.get("duration_minutes")) for row in active if str(row.get("duration_minutes", "")) not in ("", "0")
    )
    avg_duration_resolved = avg(
        as_float(row.get("duration_minutes")) for row in resolved if str(row.get("duration_minutes", "")) not in ("", "0")
    )

    severity_active = {}
    for severity in ["Critical", "High", "Medium", "Low"]:
        count = sum(1 for row in active if row.get("severity") == severity)
        severity_active[severity] = count

    oldest_active = sorted(active, key=lambda row: str(row.get("date", "")), reverse=False)[:10]

    return {
        "lifecycle_stages": by_stage,
        "total_incidents": total,
        "active_count": len(active),
        "resolved_count": len(resolved),
        "average_duration_active_minutes": round(avg_duration_active, 3),
        "average_duration_resolved_minutes": round(avg_duration_resolved, 3),
        "active_severity_breakdown": severity_active,
        "oldest_active": [
            {
                "incident_id": row.get("incident_id"),
                "date": row.get("date"),
                "severity": row.get("severity"),
                "status": row.get("status"),
                "region": row.get("region"),
                "service_type": row.get("service_type"),
                "duration_minutes": row.get("duration_minutes"),
                "assigned_team": row.get("assigned_team"),
            }
            for row in oldest_active
        ],
        "stage_progression": [
            {"stage": stage[0], "label": stage[1], "description": stage[2]}
            for stage in INCIDENT_LIFECYCLE_STAGES
        ],
    }


def ticket_analytics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    service_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(
        filters,
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        service_type=service_type,
        severity=severity,
        status=status,
    )
    ticket_rows = apply_filters(rows("customer_tickets"), query)
    backlog = [row for row in ticket_rows if row.get("status") in BACKLOG_TICKET_STATUSES]
    resolved = [row for row in ticket_rows if row.get("resolution_time_minutes") != ""]
    return {
        "ticket_volume": count_by(ticket_rows, "month"),
        "backlog": len(backlog),
        "category_breakdown": count_by(ticket_rows, "ticket_category"),
        "response_time_summary": {"average_minutes": avg(as_float(row.get("response_time_minutes")) for row in ticket_rows)},
        "resolution_time_summary": {"average_minutes": avg(as_float(row.get("resolution_time_minutes")) for row in resolved)},
        "customer_segment_summary": count_by(ticket_rows, "customer_segment"),
        "repeat_complaint_rate": percent(sum(1 for row in ticket_rows if as_bool(row.get("repeat_complaint"))), len(ticket_rows)),
    }


def ticket_drilldown(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    backlog = [row for row in ticket_rows if row.get("status") in BACKLOG_TICKET_STATUSES]
    repeat = [row for row in ticket_rows if as_bool(row.get("repeat_complaint"))]
    return {
        "backlog_by_region": sorted(count_by(backlog, "region"), key=lambda item: item["value"], reverse=True),
        "backlog_by_service": sorted(count_by(backlog, "service_type"), key=lambda item: item["value"], reverse=True),
        "category_detail": sorted(count_by(ticket_rows, "ticket_category"), key=lambda item: item["value"], reverse=True),
        "repeat_complaint_detail": repeat[:80],
    }


def sla_analytics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    service_type: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(filters, start_date=start_date, end_date=end_date, month=month, region=region, service_type=service_type)
    sla_rows = apply_filters(rows("sla_metrics"), query)
    return {
        "target_vs_actual": [
            {"name": item["name"], "target": avg(as_float(row.get("sla_target")) for row in sla_rows if row.get("month") == item["name"]), "actual": item["value"]}
            for item in avg_by(sla_rows, "month", "sla_actual")
        ],
        "breach_count": int(sum(as_float(row.get("breach_count")) for row in sla_rows)),
        "region_service_comparison": [
            {
                "region": row["region"],
                "service_type": row["service_type"],
                "sla_target": as_float(row["sla_target"]),
                "sla_actual": as_float(row["sla_actual"]),
                "breach_count": int(as_float(row["breach_count"])),
            }
            for row in sla_rows[:120]
        ],
        "mttr_trend": avg_by(sla_rows, "month", "mttr_minutes"),
    }


def sla_drilldown(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    breached = [row for row in sla_rows if as_float(row.get("sla_actual")) < as_float(row.get("sla_target"))]
    return {
        "breach_detail": [
            {
                "date": row["date"],
                "region": row["region"],
                "service_type": row["service_type"],
                "sla_target": as_float(row["sla_target"]),
                "sla_actual": as_float(row["sla_actual"]),
                "gap": round(as_float(row["sla_target"]) - as_float(row["sla_actual"]), 3),
                "mttr_minutes": as_float(row["mttr_minutes"]),
            }
            for row in breached[:120]
        ],
        "breaches_by_region": sorted(sum_by(breached, "region", "breach_count"), key=lambda item: item["value"], reverse=True),
        "breaches_by_service": sorted(sum_by(breached, "service_type", "breach_count"), key=lambda item: item["value"], reverse=True),
        "mttr_trend": avg_by(sla_rows, "month", "mttr_minutes"),
    }


SLA_ESCALATION_LEVELS = [
    ("NONE", "No breach"),
    ("WARNING", "Minor breach (<2%)"),
    ("ALERT", "Moderate breach (2-5%)"),
    ("CRITICAL", "Severe breach (>5%)"),
]


def sla_escalation(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute SLA breach escalation status and recovery tracking.

    Categorizes SLA breaches by severity, computes escalation status,
    provides recovery metrics and affected service/region breakdown.
    """
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    breached = [row for row in sla_rows if as_float(row.get("sla_actual")) < as_float(row.get("sla_target"))]

    total_sla_records = len(sla_rows)
    total_breached = len(breached)

    escalation_counts = {"NONE": 0, "WARNING": 0, "ALERT": 0, "CRITICAL": 0}
    escalation_detail: dict[str, list[dict[str, object]]] = {
        "NONE": [],
        "WARNING": [],
        "ALERT": [],
        "CRITICAL": [],
    }

    for row in sla_rows:
        target = as_float(row.get("sla_target"))
        actual = as_float(row.get("sla_actual"))
        gap_percent = round(abs(target - actual), 3) if target > 0 else 0.0

        if actual >= target:
            level = "NONE"
        elif gap_percent < 2.0:
            level = "WARNING"
        elif gap_percent < 5.0:
            level = "ALERT"
        else:
            level = "CRITICAL"

        escalation_counts[level] += 1
        escalation_detail[level].append({
            "date": row.get("date"),
            "region": row.get("region"),
            "service_type": row.get("service_type"),
            "sla_target": target,
            "sla_actual": actual,
            "gap_percent": gap_percent,
            "mttr_minutes": as_float(row.get("mttr_minutes")),
        })

    escalation_by_level = [
        {
            "level": level,
            "label": label,
            "count": escalation_counts[level],
            "percentage": percent(escalation_counts[level], total_sla_records),
        }
        for level, label in SLA_ESCALATION_LEVELS
    ]

    critical_breaches = escalation_detail["CRITICAL"][:30]
    affected_regions = sorted(
        count_by(breached, "region"),
        key=lambda item: item["value"],
        reverse=True,
    )
    affected_services = sorted(
        count_by(breached, "service_type"),
        key=lambda item: item["value"],
        reverse=True,
    )

    mttr_stats = []
    for row in breached:
        mttr = as_float(row.get("mttr_minutes"))
        if mttr > 0:
            mttr_stats.append(mttr)
    avg_mttr = avg(mttr_stats)
    max_mttr = max(mttr_stats) if mttr_stats else 0.0

    recovery_trend = avg_by(sla_rows, "month", "mttr_minutes")

    return {
        "escalation_levels": escalation_by_level,
        "total_sla_records": total_sla_records,
        "breached_records": total_breached,
        "breach_rate": percent(total_breached, total_sla_records),
        "critical_breaches": critical_breaches,
        "affected_regions": affected_regions,
        "affected_services": affected_services,
        "avg_mttr_minutes": round(avg_mttr, 3),
        "max_mttr_minutes": round(max_mttr, 3),
        "recovery_trend": recovery_trend,
    }


def technician_analytics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    team: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(
        filters,
        start_date=start_date,
        end_date=end_date,
        month=month,
        region=region,
        severity=severity,
        status=status,
        team=team,
    )
    job_rows = apply_filters(rows("field_technician_jobs"), query)
    completed = [row for row in job_rows if row.get("status") in COMPLETED_JOB_STATUSES]
    workload = sorted(count_by(job_rows, "technician_id"), key=lambda item: item["value"], reverse=True)[:20]
    return {
        "technician_workload": workload,
        "dispatch_time": {"average_minutes": avg(as_float(row.get("dispatch_time_minutes")) for row in job_rows)},
        "completion_time": {"average_minutes": avg(as_float(row.get("completion_time_minutes")) for row in completed if row.get("completion_time_minutes") != "")},
        "first_time_fix_rate": percent(sum(1 for row in completed if as_bool(row.get("first_time_fix"))), len(completed)),
        "job_status_summary": count_by(job_rows, "status"),
    }


def technician_drilldown(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    completed = [row for row in job_rows if row.get("status") in COMPLETED_JOB_STATUSES]
    return {
        "workload_by_region": sorted(count_by(job_rows, "region"), key=lambda item: item["value"], reverse=True),
        "workload_by_team": sorted(count_by(job_rows, "assigned_team"), key=lambda item: item["value"], reverse=True),
        "first_time_fix_by_priority": [
            {
                "name": priority,
                "value": percent(
                    sum(1 for row in completed if row.get("priority") == priority and as_bool(row.get("first_time_fix"))),
                    sum(1 for row in completed if row.get("priority") == priority),
                ),
            }
            for priority in ["Low", "Medium", "High", "Critical"]
        ],
        "workload_detail": sorted(job_rows, key=lambda row: (str(row.get("date", "")), str(row.get("job_id", ""))), reverse=True)[:80],
    }


def technician_assignment(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute technician assignment and workload balancing analytics.

    Provides per-technician capacity metrics, assignment status breakdown,
    team capacity distribution, and workload imbalance indicators.
    """
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    total_jobs = len(job_rows)
    active_statuses = {"Open", "In Progress"}
    completed_statuses = COMPLETED_JOB_STATUSES

    tech_stats: dict[str, dict[str, object]] = {}
    for row in job_rows:
        tech_id = str(row.get("technician_id", "Unknown"))
        team = str(row.get("assigned_team", "Unknown"))
        status = str(row.get("status", ""))
        priority = str(row.get("priority", ""))
        region = str(row.get("region", ""))
        completion = as_float(row.get("completion_time_minutes"))
        dispatch = as_float(row.get("dispatch_time_minutes"))
        first_fix = as_bool(row.get("first_time_fix"))

        if tech_id not in tech_stats:
            tech_stats[tech_id] = {
                "technician_id": tech_id,
                "assigned_team": team,
                "total_jobs": 0,
                "active_jobs": 0,
                "completed_jobs": 0,
                "total_completion_time": 0.0,
                "total_dispatch_time": 0.0,
                "completed_with_time": 0,
                "first_time_fixes": 0,
                "critical_jobs": 0,
                "regions": set(),
            }
        ts = tech_stats[tech_id]
        ts["total_jobs"] = int(ts["total_jobs"]) + 1
        if status in active_statuses:
            ts["active_jobs"] = int(ts["active_jobs"]) + 1
        if status in completed_statuses:
            ts["completed_jobs"] = int(ts["completed_jobs"]) + 1
            if completion > 0:
                ts["total_completion_time"] = float(ts["total_completion_time"]) + completion
                ts["completed_with_time"] = int(ts["completed_with_time"]) + 1
            if first_fix:
                ts["first_time_fixes"] = int(ts["first_time_fixes"]) + 1
        if dispatch > 0:
            ts["total_dispatch_time"] = float(ts["total_dispatch_time"]) + dispatch
        if priority == "Critical":
            ts["critical_jobs"] = int(ts["critical_jobs"]) + 1
        ts["regions"].add(region)  # type: ignore[union-attr]

    technicians = []
    for ts in tech_stats.values():
        avg_completion = (
            float(ts["total_completion_time"]) / int(ts["completed_with_time"])
            if int(ts["completed_with_time"]) > 0
            else 0.0
        )
        avg_dispatch = (
            float(ts["total_dispatch_time"]) / max(int(ts["total_jobs"]), 1)
        )
        technicians.append({
            "technician_id": ts["technician_id"],
            "assigned_team": ts["assigned_team"],
            "total_jobs": ts["total_jobs"],
            "active_jobs": ts["active_jobs"],
            "completed_jobs": ts["completed_jobs"],
            "capacity_ratio": round(int(ts["active_jobs"]) / max(int(ts["total_jobs"]), 1), 3),
            "avg_completion_minutes": round(avg_completion, 3),
            "avg_dispatch_minutes": round(avg_dispatch, 3),
            "first_time_fix_rate": percent(int(ts["first_time_fixes"]), int(ts["completed_jobs"])),
            "critical_jobs": ts["critical_jobs"],
            "regions": sorted(ts["regions"]),
        })

    technicians.sort(key=lambda t: int(t["active_jobs"]), reverse=True)

    team_capacity = defaultdict(lambda: {"total_jobs": 0, "active_jobs": 0, "completed_jobs": 0, "technicians": 0})
    team_tech_set: dict[str, set[str]] = defaultdict(set)
    for t in technicians:
        team = t["assigned_team"]
        tc = team_capacity[team]
        tc["total_jobs"] = int(tc["total_jobs"]) + int(t["total_jobs"])
        tc["active_jobs"] = int(tc["active_jobs"]) + int(t["active_jobs"])
        tc["completed_jobs"] = int(tc["completed_jobs"]) + int(t["completed_jobs"])
        team_tech_set[team].add(t["technician_id"])
    team_list = []
    for team_name, tc in sorted(team_capacity.items()):
        tc["technicians"] = len(team_tech_set[team_name])
        tc["avg_jobs_per_technician"] = round(int(tc["total_jobs"]) / max(int(tc["technicians"]), 1), 3)
        team_list.append(tc)

    overloaded = [t for t in technicians if int(t["active_jobs"]) > int(t["total_jobs"]) * 0.6]
    understaffed_teams = [tc for tc in team_list if int(tc["active_jobs"]) > int(tc["total_jobs"]) * 0.5]

    return {
        "technicians": technicians,
        "team_capacity": team_list,
        "total_technicians": len(technicians),
        "total_jobs": total_jobs,
        "active_jobs": sum(1 for row in job_rows if str(row.get("status", "")) in active_statuses),
        "completed_jobs": sum(1 for row in job_rows if str(row.get("status", "")) in completed_statuses),
        "overloaded_technicians": overloaded,
        "understaffed_teams": understaffed_teams,
    }


def region_analytics(
    filters: AnalyticsFilters | None = None,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    month: str | None = None,
) -> dict[str, object]:
    query = normalize_filters(filters, start_date=start_date, end_date=end_date, month=month, region=region)
    region_rows = apply_filters(rows("region_performance"), query)
    latest = latest_by_region(region_rows)
    ranking = []
    for row in latest:
        score = (
            as_float(row.get("sla_achievement"))
            + as_float(row.get("customer_satisfaction")) * 12
            - as_float(row.get("packet_loss_rate")) * 5
            - as_float(row.get("avg_latency_ms")) * 0.18
            - as_float(row.get("critical_incidents")) * 1.5
        )
        ranking.append({**row, "health_score": round(max(0, min(100, score)), 3)})
    return {
        "region_performance_ranking": sorted(ranking, key=lambda item: item["health_score"], reverse=True),
        "region_health_metrics": latest,
    }


def outage_impact(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute outage impact analysis across regions, services, and customer segments.

    Aggregates incident impact data to provide multi-dimensional outage
    impact visibility for executive decision support.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    active_incidents = [row for row in incident_rows if row.get("status") in ACTIVE_INCIDENT_STATUSES]

    by_region_impact = defaultdict(lambda: {"active_incidents": 0, "affected_customers": 0.0, "services_impacted": set()})
    by_service_impact = defaultdict(lambda: {"active_incidents": 0, "affected_customers": 0.0, "regions_impacted": set()})
    severity_impact = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for incident in active_incidents:
        region = str(incident.get("region", "Unknown"))
        service = str(incident.get("service_type", "Unknown"))
        severity = str(incident.get("severity", "Medium"))
        affected = as_float(incident.get("affected_customers"))

        by_region_impact[region]["active_incidents"] += 1
        by_region_impact[region]["affected_customers"] += affected
        by_region_impact[region]["services_impacted"].add(service)

        by_service_impact[service]["active_incidents"] += 1
        by_service_impact[service]["affected_customers"] += affected
        by_service_impact[service]["regions_impacted"].add(region)

        if severity in severity_impact:
            severity_impact[severity] += 1

    region_impact_list = [
        {
            "region": region,
            "active_incidents": data["active_incidents"],
            "affected_customers": round(data["affected_customers"], 0),
            "services_impacted": len(data["services_impacted"]),
            "impact_score": round(
                data["active_incidents"] * 10 + data["affected_customers"] * 0.1,
                3
            ),
        }
        for region, data in by_region_impact.items()
    ]
    region_impact_list.sort(key=lambda x: x["impact_score"], reverse=True)

    service_impact_list = [
        {
            "service_type": service,
            "active_incidents": data["active_incidents"],
            "affected_customers": round(data["affected_customers"], 0),
            "regions_impacted": len(data["regions_impacted"]),
            "impact_score": round(
                data["active_incidents"] * 10 + data["affected_customers"] * 0.1,
                3
            ),
        }
        for service, data in by_service_impact.items()
    ]
    service_impact_list.sort(key=lambda x: x["impact_score"], reverse=True)

    total_affected = sum(as_float(inc.get("affected_customers")) for inc in active_incidents)
    avg_affected_per_incident = total_affected / len(active_incidents) if active_incidents else 0.0

    worst_case_region = region_impact_list[0] if region_impact_list else None
    worst_case_service = service_impact_list[0] if service_impact_list else None

    return {
        "total_active_incidents": len(active_incidents),
        "total_affected_customers": round(total_affected, 0),
        "avg_affected_per_incident": round(avg_affected_per_incident, 3),
        "severity_breakdown": severity_impact,
        "region_impact": region_impact_list,
        "service_impact": service_impact_list,
        "worst_case_region": worst_case_region,
        "worst_case_service": worst_case_service,
        "multi_region_incidents": sum(1 for inc in active_incidents if str(inc.get("region")) != "Unknown"),
        "multi_service_incidents": sum(1 for inc in active_incidents if str(inc.get("service_type")) != "Unknown"),
    }
