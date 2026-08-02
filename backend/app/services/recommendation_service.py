from __future__ import annotations

from app.filters import AnalyticsFilters
from app.services.analytics_service import as_float, overview_metrics, region_analytics, rows


def compare(value: float, condition: str, threshold: float) -> bool:
    if condition == ">":
        return value > threshold
    if condition == ">=":
        return value >= threshold
    if condition == "<":
        return value < threshold
    if condition == "<=":
        return value <= threshold
    if condition == "==":
        return value == threshold
    return False


def region_from_title(title: str) -> str | None:
    marker = " in "
    if marker not in title:
        return None
    return title.rsplit(marker, 1)[-1]


SEVERITY_BASE_SCORE = {"Critical": 100, "High": 70, "Medium": 40, "Low": 20}


def priority_score(severity: str, observed: float, threshold: float) -> float:
    """Compute a priority score from severity weight plus breach magnitude.

    The severity provides the base score; the gap between observed and
    threshold adds urgency in proportion to how far the metric diverges.
    """
    base = SEVERITY_BASE_SCORE.get(severity, 40)
    if threshold == 0:
        gap_factor = 0.5 if observed > 0 else 0.0
    else:
        ratio = observed / abs(threshold)
        gap_factor = min(2.0, max(0.0, ratio - 1.0)) if ratio >= 0 else 0.0
    return round(base * (1.0 + gap_factor), 3)


def confidence_level(observed: float, threshold: float) -> str:
    """Estimate confidence that the trigger is a genuine operational issue."""
    if threshold == 0:
        return "High" if observed > 0 else "Medium"
    ratio = observed / abs(threshold)
    if ratio >= 1.5 or ratio <= 0.5:
        return "High"
    if ratio >= 1.2 or ratio <= 0.8:
        return "Medium"
    return "Low"


def business_impact_text(metric: str, observed: float, threshold: float, severity: str, affected_region: str, affected_service: str) -> str:
    """Explain the business impact of a triggered recommendation."""
    delta = abs(observed - threshold)
    unit = ""
    if "uptime" in metric or "sla" in metric or "achievement" in metric or "fix" in metric or "utilization" in metric or "satisfaction" in metric:
        unit = "%"
    elif "latency" in metric or "mttr" in metric or "time" in metric or "duration" in metric:
        unit = " units"
    elif "breach" in metric or "incident" in metric or "ticket" in metric or "backlog" in metric:
        unit = " counts"

    severity_tone = {
        "Critical": "immediate executive attention",
        "High": "priority operational response",
        "Medium": "scheduled operational review",
        "Low": "monitoring and observation",
    }.get(severity, "review")

    return (
        f"Observed {metric} at {round(observed, 2)}{unit} vs {round(threshold, 2)}{unit} "
        f"across {affected_region}/{affected_service}. Requires {severity_tone}. "
        f"Current deviation of {round(delta, 2)}{unit} indicates a measurable impact on service delivery."
    )


def expected_impact_text(metric: str, severity: str, observed: float) -> str:
    """Describe the expected impact if the recommendation is not acted upon."""
    if "uptime" in metric or "sla" in metric:
        return "Without action, service availability degradation may continue and breach committed SLAs."
    if "incident" in metric or "backlog" in metric or "ticket" in metric:
        return "Without action, incident/ticket backlog may grow and delay service restoration."
    if "latency" in metric or "mttr" in metric or "duration" in metric or "time" in metric:
        return "Without action, response and resolution times may worsen, raising customer dissatisfaction."
    if "packet_loss" in metric or "quality" in metric:
        return "Without action, service quality may degrade further, increasing churn risk."
    return "Without action, the observed degradation may persist or worsen."


def rule_based_recommendations(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    rules = rows("recommendation_rules")
    overview = overview_metrics(filters=filters)
    regions = {str(row["region"]): row for row in region_analytics(filters=filters)["region_performance_ranking"]}
    recommendations: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    for rule in rules:
        metric = str(rule.get("metric", ""))
        title = str(rule.get("recommendation_title", ""))
        threshold = as_float(rule.get("threshold"))
        condition = str(rule.get("condition", ""))
        severity = str(rule.get("severity", "Medium"))
        target_region = region_from_title(title)
        source = regions.get(target_region, {}) if target_region else overview
        observed = as_float(source.get(metric))
        if compare(observed, condition, threshold):
            affected_region = target_region or filters.region if filters and filters.region else target_region or "All Regions"
            affected_service = filters.service_type if filters and filters.service_type else "All Services"
            dedupe_key = (metric, str(affected_region), str(rule.get("recommendation_title", "")))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            priority = priority_score(severity, observed, threshold)
            confidence = confidence_level(observed, threshold)
            recommendations.append(
                {
                    "rule_id": rule["rule_id"],
                    "severity": severity,
                    "metric": metric,
                    "condition": condition,
                    "threshold": threshold,
                    "observed_value": observed,
                    "supporting_metric_value": observed,
                    "trigger_condition": f"{metric} {condition} {threshold}",
                    "affected_region": affected_region,
                    "affected_service": affected_service,
                    "recommendation_title": title,
                    "recommendation_text": rule["recommendation_text"],
                    "explanation": f"Observed {metric} is {round(observed, 3)}, which triggered rule {condition} {threshold}.",
                    "recommended_action": rule["recommendation_text"],
                    "recommended_owner": rule["recommended_owner"],
                    "priority_score": priority,
                    "confidence": confidence,
                    "business_impact": business_impact_text(
                        metric, observed, threshold, severity, affected_region, affected_service
                    ),
                    "expected_impact": expected_impact_text(metric, severity, observed),
                    "region": affected_region,
                }
            )

    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    recommendations.sort(
        key=lambda item: (
            -float(item.get("priority_score", 0)),
            severity_order.get(str(item["severity"]), 9),
            str(item["region"]),
        )
    )
    return {
        "recommendations": recommendations[:24],
        "triggered_count": len(recommendations),
        "rules_evaluated": len(rules),
        "method": "deterministic_rule_based",
        "scoring": {
            "model": "priority_score",
            "description": "Priority computed from severity base weight plus magnitude of deviation from threshold.",
        },
    }
