from __future__ import annotations

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


def rule_based_recommendations() -> dict[str, object]:
    rules = rows("recommendation_rules")
    overview = overview_metrics()
    regions = {str(row["region"]): row for row in region_analytics()["region_performance_ranking"]}
    recommendations: list[dict[str, object]] = []

    for rule in rules:
        metric = str(rule.get("metric", ""))
        title = str(rule.get("recommendation_title", ""))
        threshold = as_float(rule.get("threshold"))
        condition = str(rule.get("condition", ""))
        target_region = region_from_title(title)
        source = regions.get(target_region, {}) if target_region else overview
        observed = as_float(source.get(metric))
        if compare(observed, condition, threshold):
            recommendations.append(
                {
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "metric": metric,
                    "condition": condition,
                    "threshold": threshold,
                    "observed_value": observed,
                    "recommendation_title": title,
                    "recommendation_text": rule["recommendation_text"],
                    "recommended_owner": rule["recommended_owner"],
                    "region": target_region or "All Regions",
                }
            )

    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    recommendations.sort(key=lambda item: (severity_order.get(str(item["severity"]), 9), str(item["region"])))
    return {
        "recommendations": recommendations[:24],
        "triggered_count": len(recommendations),
        "rules_evaluated": len(rules),
        "method": "deterministic_rule_based",
    }
