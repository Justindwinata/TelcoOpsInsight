from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from typing import Iterable

from app.database import fetch_all
from app.filters import AnalyticsFilters
from app.services.dataset_service import database_has_seed_data, seed_sample_dataset


ACTIVE_INCIDENT_STATUSES = {"Open", "Investigating", "Escalated"}
RESOLVED_INCIDENT_STATUSES = {"Resolved", "Closed"}
BACKLOG_TICKET_STATUSES = {"Open", "In Progress", "Waiting Customer"}
COMPLETED_JOB_STATUSES = {"Resolved", "Closed"}


def ensure_seeded() -> None:
    if not database_has_seed_data():
        seed_sample_dataset()


def rows(table: str) -> list[dict[str, object]]:
    ensure_seeded()
    return fetch_all(f'SELECT * FROM "{table}"')


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
