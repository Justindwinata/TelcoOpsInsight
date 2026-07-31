from __future__ import annotations

from html import escape

from app.config import settings
from app.services.analytics_service import incident_analytics, overview_metrics, region_analytics
from app.services.recommendation_service import rule_based_recommendations


def executive_summary() -> dict[str, object]:
    overview = overview_metrics()
    incidents = incident_analytics()
    regions = region_analytics()
    recommendations = rule_based_recommendations()
    return {
        "title": "TelcoOps Insight Executive Summary",
        "company": settings.company_name,
        "synthetic_data_only": True,
        "period": "2026-01-01 to 2026-12-31",
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


def executive_summary_html() -> str:
    report = executive_summary()
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
