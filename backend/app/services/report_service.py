from __future__ import annotations

from html import escape

from app.config import settings
from app.filters import AnalyticsFilters
from app.services.analytics_service import incident_analytics, overview_metrics, region_analytics
from app.services.recommendation_service import rule_based_recommendations


def executive_summary(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    overview = overview_metrics(filters=filters)
    incidents = incident_analytics(filters=filters)
    regions = region_analytics(filters=filters)
    recommendations = rule_based_recommendations(filters=filters)
    return {
        "title": "TelcoOps Insight Executive Summary",
        "company": settings.company_name,
        "synthetic_data_only": True,
        "period": "2026-01-01 to 2026-12-31",
        "filter_metadata": filters.metadata() if filters else AnalyticsFilters().metadata(),
        "overview": overview,
        "top_root_causes": incidents["top_root_causes"],
        "top_regions": regions["region_performance_ranking"][:5],
        "recommendations": recommendations["recommendations"][:8],
        "limitations": [
            "Synthetic dataset only",
            "Fictional company context",
            "Rule-based recommendations, not AI or machine-learning predictions",
            "No live network, OSS/BSS, CRM, ERP, authentication, or cloud deployment integration in TOI-0001",
        ],
    }


def comparison_report(current_filters: AnalyticsFilters | None = None, previous_filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate comparative report across two time periods."""
    current = overview_metrics(filters=current_filters)
    previous = overview_metrics(filters=previous_filters)
    
    def delta(curr, prev):
        if prev == 0:
            return 0 if curr == 0 else 100
        return round(((curr - prev) / prev) * 100, 2)
    
    return {
        "title": "TelcoOps Insight Comparison Report",
        "company": settings.company_name,
        "synthetic_data_only": True,
        "report_type": "comparison",
        "current_period": current_filters.metadata() if current_filters else {},
        "previous_period": previous_filters.metadata() if previous_filters else {},
        "current_metrics": current,
        "previous_metrics": previous,
        "deltas": {
            "network_uptime": delta(current["network_uptime"], previous["network_uptime"]),
            "sla_achievement": delta(current["sla_achievement"], previous["sla_achievement"]),
            "active_incidents": delta(current["active_incidents"], previous["active_incidents"]),
            "open_tickets": delta(current["open_ticket_backlog"], previous["open_ticket_backlog"]),
            "avg_mttr": delta(current["average_mttr_minutes"], previous["average_mttr_minutes"]),
            "customer_satisfaction": delta(current["customer_satisfaction"], previous["customer_satisfaction"]),
        },
        "improvements": [k for k, v in {
            "network_uptime": current["network_uptime"] > previous["network_uptime"],
            "sla_achievement": current["sla_achievement"] > previous["sla_achievement"],
            "incident_reduction": current["active_incidents"] < previous["active_incidents"],
            "ticket_reduction": current["open_ticket_backlog"] < previous["open_ticket_backlog"],
            "mttr_improvement": current["average_mttr_minutes"] < previous["average_mttr_minutes"],
            "satisfaction_improvement": current["customer_satisfaction"] > previous["customer_satisfaction"],
        }.items() if v],
    }


def filtered_report(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate report with specific filters applied."""
    overview = overview_metrics(filters=filters)
    incidents = incident_analytics(filters=filters)
    regions = region_analytics(filters=filters)
    recommendations = rule_based_recommendations(filters=filters)
    
    return {
        "title": "TelcoOps Insight Filtered Report",
        "company": settings.company_name,
        "synthetic_data_only": True,
        "report_type": "filtered",
        "filter_metadata": filters.metadata() if filters else {},
        "overview": overview,
        "incidents": incidents,
        "regions": regions,
        "recommendations": recommendations["recommendations"][:8],
    }


def executive_summary_html(filters: AnalyticsFilters | None = None) -> str:
    report = executive_summary(filters=filters)
    overview = report["overview"]
    recommendations = report["recommendations"]
    top_regions = report["top_regions"]
    root_causes = report["top_root_causes"]

    def metric(label: str, value: object) -> str:
        return f"<div class='metric'><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>"

    recommendation_items = "".join(
        f"<li><strong>{escape(str(item['severity']))}</strong> {escape(str(item['recommendation_title']))} - {escape(str(item['recommended_owner']))}</li>"
        for item in recommendations
    )
    region_rows = "".join(
        f"<tr><td>{escape(str(item['region']))}</td><td>{escape(str(item['health_score']))}</td><td>{escape(str(item['sla_achievement']))}%</td><td>{escape(str(item['customer_satisfaction']))}</td></tr>"
        for item in top_regions
    )
    cause_rows = "".join(
        f"<tr><td>{escape(str(item['name']))}</td><td>{escape(str(item['value']))}</td></tr>"
        for item in root_causes
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(str(report['title']))}</title>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; margin: 0; background: #f6f8fb; color: #152033; }}
    header {{ background: #0f2438; color: white; padding: 28px 40px; }}
    main {{ padding: 32px 40px; max-width: 1120px; margin: auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .metric, section {{ background: white; border: 1px solid #d9e2ec; border-radius: 8px; padding: 16px; }}
    .metric span {{ display: block; color: #5b6b7f; font-size: 12px; text-transform: uppercase; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 24px; }}
    section {{ margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #e4ebf2; padding: 10px; text-align: left; }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(str(report['title']))}</h1>
    <p>{escape(str(report['company']))} - synthetic portfolio/demo data only</p>
  </header>
  <main>
    <div class="grid">
      {metric("Network uptime", overview["network_uptime"])}
      {metric("SLA achievement", overview["sla_achievement"])}
      {metric("Active incidents", overview["active_incidents"])}
      {metric("Open ticket backlog", overview["open_ticket_backlog"])}
      {metric("Affected customers", overview["affected_customers"])}
      {metric("Average MTTR minutes", overview["average_mttr_minutes"])}
      {metric("Average latency ms", overview["average_latency_ms"])}
      {metric("Technician utilization", overview["technician_utilization"])}
    </div>
    <section>
      <h2>Top Regions</h2>
      <table><thead><tr><th>Region</th><th>Health Score</th><th>SLA</th><th>Customer Satisfaction</th></tr></thead><tbody>{region_rows}</tbody></table>
    </section>
    <section>
      <h2>Top Root Causes</h2>
      <table><thead><tr><th>Root Cause</th><th>Incidents</th></tr></thead><tbody>{cause_rows}</tbody></table>
    </section>
    <section>
      <h2>Rule-Based Recommendations</h2>
      <ul>{recommendation_items}</ul>
    </section>
  </main>
</body>
</html>"""
