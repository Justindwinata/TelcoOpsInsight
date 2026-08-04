from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows, avg, as_float, count_by


def operational_forecasting(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate deterministic forecasts for operational metrics.
    
    Forecasts based on:
    - Historical incident trends (30-day moving average, growth rate)
    - SLA trend analysis
    - Ticket volume patterns
    - Maintenance workload
    
    Does NOT use AI/ML - uses deterministic trend extrapolation.
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    all_dates = []
    for row in incident_rows + sla_rows + ticket_rows + job_rows:
        d = row.get("date") or row.get("timestamp", "")
        if d:
            try:
                all_dates.append(date.fromisoformat(str(d)[:10]))
            except ValueError:
                continue
    
    if not all_dates:
        return {"error": "No data available for forecasting"}
    
    max_date = max(all_dates)
    min_date = min(all_dates)
    total_days = (max_date - min_date).days + 1
    
    # Forecast incident volume
    incident_forecast = forecast_incidents(incident_rows, min_date, max_date)
    
    # Forecast SLA trend
    sla_forecast = forecast_sla(sla_rows, min_date, max_date)
    
    # Forecast ticket growth
    ticket_forecast = forecast_tickets(ticket_rows, min_date, max_date)
    
    # Forecast maintenance workload
    maintenance_forecast = forecast_maintenance(job_rows, min_date, max_date)
    
    return {
        "forecast_date": max_date.isoformat(),
        "historical_period": {
            "start": min_date.isoformat(),
            "end": max_date.isoformat(),
            "days": total_days,
        },
        "assumptions": [
            "Historical trends will continue at similar rates",
            "No major operational changes expected in forecast period",
            "Seasonal factors not considered (deterministic projection only)",
            "Based on actual data patterns, not ML/AI prediction",
        ],
        "forecasts": {
            "incident_volume": incident_forecast,
            "sla_trend": sla_forecast,
            "ticket_growth": ticket_forecast,
            "maintenance_workload": maintenance_forecast,
        },
    }


def forecast_incidents(incidents: list, start: date, end: date) -> dict[str, object]:
    """Forecast incident volume with confidence label."""
    # Group by week for trend analysis
    by_week: defaultdict[str, int] = defaultdict(int)
    for inc in incidents:
        d = str(inc.get("date", ""))[:10]
        try:
            dt = date.fromisoformat(d)
            week_key = dt.strftime("%Y-W%V")
            by_week[week_key] += 1
        except ValueError:
            continue
    
    weeks = sorted(by_week.keys())
    if len(weeks) < 2:
        return {
            "confident": False,
            "message": "Insufficient historical data for reliable forecast",
        }
    
    # Calculate growth rate
    weekly_counts = [by_week[w] for w in weeks]
    recent_avg = avg(weekly_counts[-4:]) if len(weekly_counts) >= 4 else avg(weekly_counts)
    previous_avg = avg(weekly_counts[:-4]) if len(weekly_counts) >= 4 else recent_avg
    growth_rate = ((recent_avg - previous_avg) / max(previous_avg, 1)) * 100
    
    # Forecast next 7 days
    daily_rate = recent_avg / 7
    forecast_7d = round(daily_rate * 7, 0)
    
    # Confidence based on data quality
    confidence = "High" if len(weeks) >= 8 and growth_rate > -20 and growth_rate < 20 else "Medium" if len(weeks) >= 4 else "Low"
    
    return {
        "forecast_7d": int(forecast_7d),
        "recent_weekly_avg": round(recent_avg, 2),
        "growth_rate_pct": round(growth_rate, 2),
        "confidence": confidence,
        "confidence_label": "Trend stable - reliable forecast" if confidence == "High" else "Trend volatile - forecast uncertain",
        "explanation": f"Based on {len(weeks)} weeks of data, incidents trend at {growth_rate:.1f}% vs previous period.",
    }


def forecast_sla(sla_rows: list, start: date, end: date) -> dict[str, object]:
    """Forecast SLA achievement trend."""
    sla_by_date = defaultdict(list)
    for sla in sla_rows:
        d = str(sla.get("date", ""))[:10]
        try:
            dt = date.fromisoformat(d)
            sla_by_date[d].append(as_float(sla.get("sla_actual", 100)))
        except ValueError:
            continue
    
    dates = sorted(sla_by_date.keys())
    if len(dates) < 7:
        return {
            "confident": False,
            "message": "Insufficient SLA data for reliable forecast",
        }
    
    # Calculate recent average
    recent_dates = dates[-7:]
    recent_avg = avg([avg(sla_by_date[d]) for d in recent_dates])
    
    # Calculate trend
    previous_dates = dates[-14:-7]
    previous_avg = avg([avg(sla_by_date[d]) for d in previous_dates])
    trend = recent_avg - previous_avg
    
    # Forecast next 30 days
    forecast_30d = recent_avg + (trend * 30 / 7) * 0.5  # Reduce trend impact for longer period
    
    confidence = "High" if abs(trend) < 1 and recent_avg > 97 else "Medium" if abs(trend) < 2 else "Low"
    
    return {
        "current_avg": round(recent_avg, 2),
        "trend_per_day": round(trend, 3),
        "forecast_30d": round(max(0, min(100, forecast_30d)), 2),
        "confidence": confidence,
        "confidence_label": "SLA stable - forecast reliable" if confidence == "High" else "SLA volatile - forecast uncertain",
        "explanation": f"SLA changed by {trend:+.2f}% per day recently, projected to {forecast_30d:.1f}% in 30 days.",
    }


def forecast_tickets(tickets: list, start: date, end: date) -> dict[str, object]:
    """Forecast ticket volume growth."""
    ticket_by_date = defaultdict(int)
    for tkt in tickets:
        d = str(tkt.get("date", ""))[:10]
        ticket_by_date[d] += 1
    
    dates = sorted(ticket_by_date.keys())
    if len(dates) < 7:
        return {
            "confident": False,
            "message": "Insufficient ticket data for reliable forecast",
        }
    
    # Calculate growth rate
    recent = sum(ticket_by_date[d] for d in dates[-7:])
    previous = sum(ticket_by_date[d] for d in dates[-14:-7])
    growth_rate = ((recent - previous) / max(previous, 1)) * 100
    
    # Forecast next 7 days
    daily_rate = recent / 7
    forecast_7d = round(daily_rate * 7, 0)
    
    confidence = "High" if growth_rate > -30 and growth_rate < 30 else "Medium" if growth_rate > -50 and growth_rate < 50 else "Low"
    
    return {
        "forecast_7d": int(forecast_7d),
        "recent_7d_total": recent,
        "growth_rate_pct": round(growth_rate, 2),
        "confidence": confidence,
        "confidence_label": "Ticket volume stable" if confidence == "High" else "Ticket volume increasing/decreasing",
        "explanation": f"Ticket volume changed by {growth_rate:+.1f}% over last 14 days.",
    }


def forecast_maintenance(jobs: list, start: date, end: date) -> dict[str, object]:
    """Forecast maintenance workload."""
    upcoming_jobs = [j for j in jobs if j.get("status") == "Open"]
    
    # Group by region
    by_region = defaultdict(int)
    for job in upcoming_jobs:
        reg = str(job.get("region", "Unknown"))
        by_region[reg] += 1
    
    # Calculate total
    total_upcoming = len(upcoming_jobs)
    
    # Estimate completion time
    avg_completion = 2  # days per job estimate
    estimated_completion_days = total_upcoming * avg_completion
    
    # High utilization regions
    high_util = [r for r, count in by_region.items() if count > 10]
    
    return {
        "total_upcoming_jobs": total_upcoming,
        "by_region": dict(by_region),
        "estimated_completion_days": estimated_completion_days,
        "high_utilization_regions": high_util[:5],
        "confidence": "Medium",
        "confidence_label": "Based on scheduled maintenance jobs",
        "explanation": f"{total_upcoming} maintenance jobs scheduled, estimated {estimated_completion_days} days to complete.",
    }
