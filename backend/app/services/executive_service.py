from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, avg, count_by, rows


def executive_summary(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate comprehensive executive summary with multiple time windows and comparisons.

    Includes monthly and weekly summaries, KPI comparison across periods,
    region/service trend analysis, and SLA trend tracking.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    region_rows = apply_filters(rows("region_performance"), filters)

    # Get date range for comparison
    all_dates = []
    for row in incident_rows + sla_rows + ticket_rows + region_rows:
        d = row.get("date") or row.get("timestamp", "")
        if d:
            try:
                all_dates.append(date.fromisoformat(str(d)[:10]))
            except ValueError:
                continue

    if not all_dates:
        return {"error": "No data available", "summary": None}

    min_date = min(all_dates)
    max_date = max(all_dates)
    total_days = (max_date - min_date).days + 1

    # Current period (last 30 days)
    current_end = max_date
    current_start = current_end - timedelta(days=30)
    current_period = {
        "start": current_start.isoformat(),
        "end": current_end.isoformat(),
        "days": 30,
    }

    # Previous period (30 days before current)
    prev_end = current_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=29)
    prev_period = {
        "start": prev_start.isoformat(),
        "end": prev_end.isoformat(),
        "days": 30,
    }

    # Calculate metrics for both periods
    def filter_by_date_range(rows, start, end):
        return [
            r for r in rows
            if str(r.get("date", "")[:10]) >= str(start) and str(r.get("date", "")[:10]) <= str(end)
        ]

    current_incidents = filter_by_date_range(incident_rows, current_start, current_end)
    prev_incidents = filter_by_date_range(incident_rows, prev_start, prev_end)
    current_sla = filter_by_date_range(sla_rows, current_start, current_end)
    prev_sla = filter_by_date_range(sla_rows, prev_start, prev_end)
    current_tickets = filter_by_date_range(ticket_rows, current_start, current_end)
    prev_tickets = filter_by_date_range(ticket_rows, prev_start, prev_end)

    # Calculate summary metrics
    def calc_kpi(rows, field, start, end):
        filtered = filter_by_date_range(rows, start, end)
        return len(filtered) if field in ("incident", "ticket") else None

    summary = {
        "period": {
            "current": current_period,
            "previous": prev_period,
        },
        "kpi_comparison": {
            "incidents": {
                "current_count": len(current_incidents),
                "prev_count": len(prev_incidents),
                "change": len(current_incidents) - len(prev_incidents),
                "change_pct": round(
                    ((len(current_incidents) - len(prev_incidents)) / max(len(prev_incidents), 1)) * 100, 2
                ),
            },
            "active_incidents": {
                "current": sum(1 for r in current_incidents if r.get("status") in ("Open", "Investigating", "Escalated")),
                "prev": sum(1 for r in prev_incidents if r.get("status") in ("Open", "Investigating", "Escalated")),
            },
            "critical_incidents": {
                "current": sum(1 for r in current_incidents if r.get("severity") == "Critical"),
                "prev": sum(1 for r in prev_incidents if r.get("severity") == "Critical"),
            },
            "sla_breaches": {
                "current": sum(1 for r in current_sla if float(r.get("sla_actual", 100)) < float(r.get("sla_target", 99))),
                "prev": sum(1 for r in prev_sla if float(r.get("sla_actual", 100)) < float(r.get("sla_target", 99))),
            },
            "open_tickets": {
                "current": sum(1 for r in current_tickets if r.get("status") in ("Open", "In Progress", "Waiting Customer")),
                "prev": sum(1 for r in prev_tickets if r.get("status") in ("Open", "In Progress", "Waiting Customer")),
            },
        },
        "monthly_trend": {
            "incidents": count_by(current_incidents, "month"),
            "sla_breaches": count_by([r for r in current_sla if float(r.get("sla_actual", 100)) < float(r.get("sla_target", 99))], "month"),
            "tickets": count_by(current_tickets, "month"),
        },
        "region_comparison": {
            "current_ranking": region_comparison_summary(current_incidents, current_sla, region_rows, current_start, current_end),
            "previous_ranking": region_comparison_summary(prev_incidents, prev_sla, region_rows, prev_start, prev_end),
        },
        "service_trend": {
            "incident_by_service": count_by(current_incidents, "service_type"),
            "sla_by_service": sla_trend_by_service(current_sla),
            "ticket_by_service": count_by(current_tickets, "service_type"),
        },
        "summary": {
            "date_range": f"{min_date.isoformat()} to {max_date.isoformat()}",
            "total_days": total_days,
            "total_incidents": len(incident_rows),
            "total_sla_records": len(sla_rows),
            "total_tickets": len(ticket_rows),
            "active_regions": len(set(r.get("region") for r in region_rows)),
        },
    }

    return summary


def region_comparison_summary(incidents, sla, regions, start, end):
    """Generate region comparison metrics."""
    region_data: dict[str, dict] = defaultdict(lambda: {
        "incidents": 0,
        "critical": 0,
        "sla_achieved": 0,
        "sla_total": 0,
        "satisfaction": [],
    })

    for r in incidents:
        reg = str(r.get("region", "Unknown"))
        region_data[reg]["incidents"] += 1
        if r.get("severity") == "Critical":
            region_data[reg]["critical"] += 1

    for r in sla:
        reg = str(r.get("region", "Unknown"))
        region_data[reg]["sla_total"] += 1
        actual = float(r.get("sla_actual", 0))
        target = float(r.get("sla_target", 100))
        if actual >= target:
            region_data[reg]["sla_achieved"] += 1

    for r in regions:
        reg = str(r.get("region", "Unknown"))
        sat = float(r.get("customer_satisfaction", 0))
        if sat > 0:
            region_data[reg]["satisfaction"].append(sat)

    result = []
    for reg, data in region_data.items():
        avg_sla = (data["sla_achieved"] / data["sla_total"] * 100) if data["sla_total"] > 0 else 0
        avg_sat = avg(data["satisfaction"]) if data["satisfaction"] else 0
        result.append({
            "region": reg,
            "incident_count": data["incidents"],
            "critical_count": data["critical"],
            "sla_achievement": round(avg_sla, 3),
            "avg_satisfaction": round(avg_sat, 2),
        })

    result.sort(key=lambda r: (r["incident_count"], -r["sla_achievement"]), reverse=True)
    return result[:10]


def sla_trend_by_service(sla_rows):
    """Calculate SLA trend by service type."""
    service_data: dict[str, list[float]] = defaultdict(list)
    for r in sla_rows:
        service = str(r.get("service_type", "Unknown"))
        actual = float(r.get("sla_actual", 0))
        if actual > 0:
            service_data[service].append(actual)

    result = []
    for service, values in service_data.items():
        avg_value = avg(values)
        target = avg([float(r.get("sla_target", 99)) for r in sla_rows if str(r.get("service_type")) == service])
        result.append({
            "service_type": service,
            "avg_actual": round(avg_value, 3),
            "avg_target": round(target, 3),
            "performance": round(avg_value - target, 3),
        })

    result.sort(key=lambda r: r["avg_actual"])
    return result[:6]
