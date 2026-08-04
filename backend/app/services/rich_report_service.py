from __future__ import annotations

from datetime import date, timedelta
from html import escape
from collections import defaultdict

from app.config import settings
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg, count_by


def generate_rich_executive_report(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate rich executive report with charts, findings, and summaries."""
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    # Executive summary
    active_incidents = sum(1 for i in incident_rows if i.get("status") in ("Open", "Investigating", "Escalated"))
    critical_incidents = sum(1 for i in incident_rows if i.get("severity") == "Critical")
    sla_achievement = avg([as_float(s.get("sla_actual")) for s in sla_rows]) if sla_rows else 100
    open_tickets = sum(1 for t in ticket_rows if t.get("status") in ("Open", "In Progress"))
    
    summary = f"Network operating with {active_incidents} active incidents ({critical_incidents} critical). SLA at {sla_achievement:.1f}% with {open_tickets} open tickets."
    
    # Key findings
    findings = generate_key_findings(incident_rows, sla_rows, ticket_rows, asset_rows, job_rows)
    
    # KPI scorecards
    kpi_scorecards = generate_kpi_data(incident_rows, sla_rows, ticket_rows, asset_rows, job_rows)
    
    # Regional comparison
    regional = generate_regional_comparison(sla_rows, incident_rows, quality_rows=[])
    
    # Risk summary
    risks = summarize_risks(incident_rows, sla_rows, ticket_rows)
    
    # Recommendations
    recommendations = [
        {
            "title": "Address critical incidents immediately",
            "description": f"{critical_incidents} critical incidents require immediate action",
            "priority": "Critical",
            "owner": "NOC Director",
        },
        {
            "title": "Review SLA performance",
            "description": f"SLA at {sla_achievement:.1f}%, assess service delivery gaps",
            "priority": "High",
            "owner": "Service Quality Manager",
        },
        {
            "title": "Reduce ticket backlog",
            "description": f"{open_tickets} open tickets, improve resolution efficiency",
            "priority": "Medium",
            "owner": "Customer Assurance",
        },
    ]
    
    # Chart data
    charts = {
        "incident_trend": count_by(incident_rows, "month")[-6:],
        "sla_trend": [{"name": s.get("month", s.get("date", "")), "value": round(sla_achievement, 2)} for s in sla_rows[:6]],
        "severity_distribution": count_by(incident_rows, "severity"),
        "status_distribution": count_by(incident_rows, "status"),
    }
    
    return {
        "title": "TelcoOps Insight Executive Report",
        "company": settings.company_name,
        "generated_at": date.today().isoformat(),
        "synthetic_data_only": True,
        "period": "Current reporting period",
        "filter_metadata": filters.metadata() if filters else {},
        "executive_summary": summary,
        "key_findings": findings,
        "kpi_scorecards": kpi_scorecards,
        "recommendations": recommendations,
        "risk_summary": risks,
        "regional_comparison": regional,
        "asset_summary": summarize_assets(asset_rows),
        "maintenance_summary": summarize_maintenance(job_rows),
        "charts": charts,
    }


def generate_key_findings(incidents, slas, tickets, assets, jobs):
    """Generate key findings from the data."""
    findings = []
    
    active = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    if active > 10:
        findings.append(f"Elevated incident activity: {active} active incidents could strain NOC resources.")
    else:
        findings.append(f"Incident load manageable at {active} active incidents.")
    
    sla_breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    if sla_breaches > len(slas) * 0.1:
        findings.append(f"SLA breach rate elevated: {sla_breaches} breaches detected.")
    else:
        findings.append(f"SLA performance stable with {sla_breaches} breaches.")
    
    repeat_tickets = sum(1 for t in tickets if str(t.get("repeat_complaint", "")).lower() == "true")
    if repeat_tickets:
        findings.append(f"{repeat_tickets} repeat complaints suggest systemic issues.")
    
    faulty_assets = sum(1 for a in assets if a.get("status") == "Faulty")
    if faulty_assets > 5:
        findings.append(f"{faulty_assets} faulty assets require attention.")
    
    return findings[:6]


def generate_kpi_data(incidents, slas, tickets, assets, jobs):
    """Generate KPI scorecard data."""
    resolved = [i for i in incidents if i.get("status") in ("Resolved", "Closed")]
    mttr = avg([as_float(i.get("duration_minutes")) for i in resolved]) if resolved else 0
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    resolved_tickets = sum(1 for t in tickets if t.get("status") == "Resolved")
    resolution_rate = (resolved_tickets / len(tickets) * 100) if tickets else 0
    
    return [
        {"name": "Availability", "value": round(sla_achievement_for(slas), 2), "change": 0.5, "unit": "%"},
        {"name": "SLA Achievement", "value": round(sla_achievement_for(slas), 2), "change": 0.3, "unit": "%"},
        {"name": "MTTR", "value": round(mttr, 0), "change": -5, "unit": "min"},
        {"name": "Ticket Resolution", "value": round(resolution_rate, 1), "change": 2, "unit": "%"},
        {"name": "Open Tickets", "value": open_tickets, "change": 10, "unit": ""},
    ]


def sla_achievement_for(slas):
    return avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 100


def generate_regional_comparison(slas, incidents, quality_rows):
    """Generate regional performance comparison."""
    regional = defaultdict(lambda: {"incidents": 0, "sla": [], "critical": 0})
    
    for sla in slas:
        reg = str(sla.get("region", "Unknown"))
        regional[reg]["sla"].append(as_float(sla.get("sla_actual", 100)))
    
    for inc in incidents:
        reg = str(inc.get("region", "Unknown"))
        regional[reg]["incidents"] += 1
        if inc.get("severity") == "Critical":
            regional[reg]["critical"] += 1
    
    result = []
    for reg, data in regional.items():
        result.append({
            "region": reg,
            "incidents": data["incidents"],
            "critical": data["critical"],
            "sla_achievement": round(avg(data["sla"]), 2) if data["sla"] else 100,
        })
    
    result.sort(key=lambda r: r["sla_achievement"], reverse=True)
    return result[:10]


def summarize_risks(incidents, slas, tickets):
    """Summarize operational risks."""
    risks = []
    critical = sum(1 for i in incidents if i.get("severity") == "Critical")
    if critical > 3:
        risks.append({"risk": "Critical incident concentration", "level": "High"})
    
    breach_rate = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target"))) / max(len(slas), 1)
    if breach_rate > 0.1:
        risks.append({"risk": "SLA breach risk elevated", "level": "High"})
    
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    if open_tickets > 100:
        risks.append({"risk": "Ticket backlog growing", "level": "Medium"})
    
    return risks[:5]


def summarize_assets(assets):
    """Summarize asset inventory."""
    active = sum(1 for a in assets if a.get("status") == "Active")
    faulty = sum(1 for a in assets if a.get("status") == "Faulty")
    maintenance = sum(1 for a in assets if a.get("status") == "Maintenance")
    
    return {
        "total": len(assets),
        "active": active,
        "faulty": faulty,
        "maintenance": maintenance,
        "health": round(active / max(len(assets), 1) * 100, 2),
    }


def summarize_maintenance(jobs):
    """Summarize maintenance workload."""
    upcoming = sum(1 for j in jobs if j.get("status") == "Open")
    completed = sum(1 for j in jobs if j.get("status") in ("Resolved", "Closed"))
    pm = sum(1 for j in jobs if j.get("job_type") == "Preventive Maintenance")
    cm = sum(1 for j in jobs if j.get("job_type") == "Corrective Maintenance")
    
    return {
        "total_jobs": len(jobs),
        "upcoming": upcoming,
        "completed": completed,
        "preventive": pm,
        "corrective": cm,
    }


def generate_rich_report_html(filters: AnalyticsFilters | None = None) -> str:
    """Generate HTML version of rich executive report."""
    report = generate_rich_executive_report(filters)
    
    finding_items = "".join(f"<li>{escape(str(f))}</li>" for f in report["key_findings"])
    reco_items = "".join(
        f"<li><strong>{escape(str(r['priority']))}</strong> {escape(str(r['title']))} - {escape(str(r['owner']))}</li>"
        for r in report["recommendations"]
    )
    region_rows = "".join(
        f"<tr><td>{escape(str(r['region']))}</td><td>{escape(str(r['sla_achievement']))}%</td><td>{escape(str(r['incidents']))}</td><td>{escape(str(r['critical']))}</td></tr>"
        for r in report["regional_comparison"]
    )
    kpi_cards = "".join(
        f"<div class='metric'><span>{escape(str(k['name']))}</span><strong>{escape(str(k['value']))}{escape(str(k['unit']))}</strong></div>"
        for k in report["kpi_scorecards"]
    )
    
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(str(report['title']))}</title>
  <style>
    body {{ font-family: Inter, sans-serif; margin: 0; background: #f6f8fb; color: #152033; }}
    header {{ background: #0f2438; color: white; padding: 28px 40px; }}
    main {{ padding: 32px 40px; max-width: 1120px; margin: auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }}
    .metric, section {{ background: white; border: 1px solid #d9e2ec; border-radius: 8px; padding: 16px; margin-top: 16px; }}
    .metric span {{ display: block; color: #5b6b7f; font-size: 12px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 20px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #e4ebf2; padding: 10px; text-align: left; }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(str(report['title']))}</h1>
    <p>{escape(str(report['company']))} - synthetic data only</p>
  </header>
  <main>
    <p style="font-size:16px"><strong>Executive Summary:</strong> {escape(str(report['executive_summary']))}</p>
    <div class="grid">{kpi_cards}</div>
    <section><h2>Key Findings</h2><ul>{finding_items}</ul></section>
    <section><h2>Regional Comparison</h2><table><thead><tr><th>Region</th><th>SLA</th><th>Incidents</th><th>Critical</th></tr></thead><tbody>{region_rows}</tbody></table></section>
    <section><h2>Recommendations</h2><ul>{reco_items}</ul></section>
  </main>
</body>
</html>"""