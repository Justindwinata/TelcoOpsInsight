from __future__ import annotations

from datetime import date, timedelta
from collections import defaultdict

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg
from app.services.intelligence_service import (
    compute_operational_health,
    identify_critical_alerts,
    detect_risk_indicators,
    identify_opportunities,
)


def generate_executive_brief(filters: AnalyticsFilters | None = None, brief_date: date | None = None) -> dict[str, object]:
    """Generate daily executive brief with prioritized insights and actions.
    
    Provides:
    - Executive summary
    - Key metrics
    - Critical issues
    - Top risks
    - Opportunities
    - Recommended actions
    """
    target_date = brief_date or date.today()
    
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    region_rows = apply_filters(rows("region_performance"), filters)
    
    # Executive summary
    operational_health = compute_operational_health(incident_rows, sla_rows, asset_rows)
    
    # Key metrics
    key_metrics = compute_key_metrics(incident_rows, sla_rows, ticket_rows, asset_rows, job_rows)
    
    # Critical issues
    critical_issues = identify_critical_alerts(incident_rows, sla_rows, asset_rows)
    
    # Top risks
    top_risks = detect_risk_indicators(incident_rows, sla_rows, ticket_rows)
    
    # Opportunities
    opportunities = identify_opportunities(incident_rows, job_rows, region_rows)
    
    # Recommended actions
    recommended_actions = generate_recommended_actions(critical_issues, top_risks, opportunities)
    
    # Day-over-day comparison
    comparison = compute_daily_comparison(incident_rows, sla_rows, ticket_rows, target_date)
    
    # Executive tone
    tone = determine_executive_tone(operational_health["overall_score"], len(critical_issues), len(top_risks))
    
    return {
        "brief_date": target_date.isoformat(),
        "generated_at": date.today().isoformat(),
        "tone": tone,
        "executive_summary": {
            "overall_health": operational_health["overall_score"],
            "status": operational_health["status"],
            "summary": generate_summary_text(operational_health, key_metrics, critical_issues),
        },
        "key_metrics": key_metrics,
        "critical_issues": critical_issues[:5],
        "top_risks": top_risks[:5],
        "opportunities": opportunities[:3],
        "recommended_actions": recommended_actions[:5],
        "day_over_day": comparison,
        "sections": {
            "incidents": summarize_incidents(incident_rows),
            "sla_performance": summarize_sla(sla_rows),
            "customer_experience": summarize_tickets(ticket_rows),
            "asset_status": summarize_assets(asset_rows),
            "field_operations": summarize_jobs(job_rows),
        },
    }


def compute_key_metrics(incidents: list, slas: list, tickets: list, assets: list, jobs: list) -> dict[str, object]:
    """Compute key executive metrics."""
    active_incidents = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    critical_incidents = sum(1 for i in incidents if i.get("severity") == "Critical")
    
    sla_achievement = avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 100
    sla_breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    affected_customers = sum(as_float(i.get("affected_customers")) for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    
    asset_health = (sum(1 for a in assets if a.get("status") == "Active") / len(assets) * 100) if assets else 0
    
    completed_jobs = sum(1 for j in jobs if j.get("status") in ("Resolved", "Closed"))
    ftf_rate = (sum(1 for j in jobs if j.get("status") in ("Resolved", "Closed") and str(j.get("first_time_fix", "")).lower() == "true") / completed_jobs * 100) if completed_jobs else 0
    
    return {
        "active_incidents": active_incidents,
        "critical_incidents": critical_incidents,
        "sla_achievement": round(sla_achievement, 2),
        "sla_breaches": sla_breaches,
        "open_tickets": open_tickets,
        "affected_customers": int(affected_customers),
        "asset_health": round(asset_health, 2),
        "first_time_fix_rate": round(ftf_rate, 2),
    }


def generate_recommended_actions(issues: list, risks: list, opportunities: list) -> list[dict[str, object]]:
    """Generate prioritized recommended actions for executives."""
    actions = []
    
    # Actions from critical issues
    for issue in issues[:2]:
        actions.append({
            "priority": "Critical",
            "action": issue.get("action", "Review and escalate"),
            "reason": issue.get("summary", ""),
            "owner": "NOC Director",
            "deadline": "Today",
        })
    
    # Actions from risks
    for risk in risks[:2]:
        actions.append({
            "priority": "High",
            "action": risk.get("mitigation", "Monitor and report"),
            "reason": risk.get("indicator", ""),
            "owner": "Operations Manager",
            "deadline": "This week",
        })
    
    # Actions from opportunities
    for opp in opportunities[:1]:
        actions.append({
            "priority": "Medium",
            "action": f"Evaluate: {opp.get('title', '')}",
            "reason": opp.get("description", ""),
            "owner": "Strategy Team",
            "deadline": "This month",
        })
    
    return actions


def compute_daily_comparison(incidents: list, slas: list, tickets: list, target_date: date) -> dict[str, object]:
    """Compare today vs yesterday metrics."""
    today_str = target_date.isoformat()
    yesterday_str = (target_date - timedelta(days=1)).isoformat()
    
    today_incidents = sum(1 for i in incidents if str(i.get("date", ""))[:10] == today_str)
    yesterday_incidents = sum(1 for i in incidents if str(i.get("date", ""))[:10] == yesterday_str)
    
    today_breaches = sum(1 for s in slas if str(s.get("date", ""))[:10] == today_str and as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    yesterday_breaches = sum(1 for s in slas if str(s.get("date", ""))[:10] == yesterday_str and as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    
    today_tickets = sum(1 for t in tickets if str(t.get("date", ""))[:10] == today_str)
    yesterday_tickets = sum(1 for t in tickets if str(t.get("date", ""))[:10] == yesterday_str)
    
    return {
        "incidents": {"today": today_incidents, "yesterday": yesterday_incidents, "change": today_incidents - yesterday_incidents},
        "sla_breaches": {"today": today_breaches, "yesterday": yesterday_breaches, "change": today_breaches - yesterday_breaches},
        "tickets": {"today": today_tickets, "yesterday": yesterday_tickets, "change": today_tickets - yesterday_tickets},
    }


def determine_executive_tone(health_score: float, critical_count: int, risk_count: int) -> str:
    """Determine appropriate executive tone based on operational state."""
    if critical_count > 0 or health_score < 60:
        return "Urgent"
    elif risk_count > 2 or health_score < 75:
        return "Cautious"
    elif health_score >= 90:
        return "Positive"
    else:
        return "Neutral"


def generate_summary_text(health: dict, metrics: dict, issues: list) -> str:
    """Generate executive summary text."""
    status = health["status"]
    score = health["overall_score"]
    active = metrics["active_incidents"]
    critical = metrics["critical_incidents"]
    
    if critical > 0:
        return f"Network status: {status} ({score}/100). {critical} critical incident(s) and {active} total active incidents require immediate attention."
    elif active > 10:
        return f"Network status: {status} ({score}/100). Elevated incident activity with {active} active incidents. Operational resources engaged."
    elif score >= 90:
        return f"Network status: {status} ({score}/100). Operations running smoothly with {active} active incidents under normal management."
    else:
        return f"Network status: {status} ({score}/100). {active} active incidents being managed. No critical issues at this time."


def summarize_incidents(incidents: list) -> dict[str, object]:
    """Summarize incident data for brief."""
    active = [i for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated")]
    by_severity = defaultdict(int)
    by_region = defaultdict(int)
    
    for inc in active:
        by_severity[str(inc.get("severity", "Unknown"))] += 1
        by_region[str(inc.get("region", "Unknown"))] += 1
    
    return {
        "active_count": len(active),
        "by_severity": dict(by_severity),
        "top_impacted_region": max(by_region.items(), key=lambda x: x[1])[0] if by_region else "None",
    }


def summarize_sla(slas: list) -> dict[str, object]:
    """Summarize SLA performance for brief."""
    breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    achievement = avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 100
    
    return {
        "achievement": round(achievement, 2),
        "breaches": breaches,
        "status": "At Risk" if breaches > len(slas) * 0.1 else "On Track",
    }


def summarize_tickets(tickets: list) -> dict[str, object]:
    """Summarize customer tickets for brief."""
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    repeat = sum(1 for t in tickets if str(t.get("repeat_complaint", "")).lower() == "true")
    
    return {
        "open_count": open_tickets,
        "repeat_complaints": repeat,
        "status": "Needs Attention" if open_tickets > 100 else "Manageable",
    }


def summarize_assets(assets: list) -> dict[str, object]:
    """Summarize asset status for brief."""
    faulty = sum(1 for a in assets if a.get("status") == "Faulty")
    active = sum(1 for a in assets if a.get("status") == "Active")
    health = (active / len(assets) * 100) if assets else 0
    
    return {
        "health_score": round(health, 2),
        "faulty_count": faulty,
        "status": "Healthy" if health > 95 else "Monitor",
    }


def summarize_jobs(jobs: list) -> dict[str, object]:
    """Summarize field operations for brief."""
    active = sum(1 for j in jobs if j.get("status") not in ("Resolved", "Closed"))
    completed = sum(1 for j in jobs if j.get("status") in ("Resolved", "Closed"))
    
    return {
        "active_jobs": active,
        "completed_jobs": completed,
        "status": "On Track",
    }
