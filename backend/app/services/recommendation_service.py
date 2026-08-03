from __future__ import annotations

from datetime import datetime, timedelta
from collections import defaultdict

from app.filters import AnalyticsFilters
from app.services.analytics_service import as_float, overview_metrics, region_analytics, rows


SEVERITY_BASE_SCORE = {"Critical": 100, "High": 70, "Medium": 40, "Low": 20}
URGENCY_WINDOWS = {
    "Critical": {"min_hours": 1, "max_hours": 4, "default_hours": 2},
    "High": {"min_hours": 4, "max_hours": 12, "default_hours": 8},
    "Medium": {"min_hours": 12, "max_hours": 48, "default_hours": 24},
    "Low": {"min_hours": 24, "max_hours": 168, "default_hours": 72},
}


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


def priority_score(severity: str, observed: float, threshold: float) -> float:
    base = SEVERITY_BASE_SCORE.get(severity, 40)
    if threshold == 0:
        gap_factor = 0.5 if observed > 0 else 0.0
    else:
        ratio = observed / abs(threshold)
        gap_factor = min(2.0, max(0.0, ratio - 1.0)) if ratio >= 0 else 0.0
    return round(base * (1.0 + gap_factor), 3)


def confidence_level(observed: float, threshold: float) -> str:
    if threshold == 0:
        return "High" if observed > 0 else "Medium"
    ratio = observed / abs(threshold)
    if ratio >= 1.5 or ratio <= 0.5:
        return "High"
    if ratio >= 1.2 or ratio <= 0.8:
        return "Medium"
    return "Low"


def business_impact_text(metric: str, observed: float, threshold: float, severity: str, affected_region: str, affected_service: str) -> str:
    delta = abs(observed - threshold)
    unit = "%" if "uptime" in metric or "sla" in metric or "achievement" in metric or "fix" in metric or "utilization" in metric or "satisfaction" in metric else " units" if "latency" in metric or "mttr" in metric or "time" in metric or "duration" in metric else " counts"
    severity_tone = {
        "Critical": "immediate executive attention",
        "High": "priority operational response",
        "Medium": "scheduled operational review",
        "Low": "monitoring and observation",
    }.get(severity, "review")
    return f"Observed {metric} at {round(observed, 2)}{unit} vs {round(threshold, 2)}{unit} across {affected_region}/{affected_service}. Requires {severity_tone}. Current deviation of {round(delta, 2)}{unit} indicates a measurable impact on service delivery."


def technical_impact_text(metric: str, observed: float, threshold: float, affected_region: str) -> str:
    delta = observed - threshold
    if "uptime" in metric or "sla" in metric:
        return f"Network availability degradation in {affected_region} may cause service outages affecting SLA commitments."
    if "latency" in metric or "mttr" in metric or "duration" in metric or "time" in metric:
        return f"Increased response/resolution times in {affected_region} degrade user experience and operational efficiency."
    if "packet_loss" in metric or "quality" in metric:
        return f"Service quality degradation in {affected_region} increases churn risk and customer complaints."
    if "incident" in metric or "backlog" in metric or "ticket" in metric:
        return f"Growing incident/ticket volume in {affected_region} strains NOC capacity and delays resolution."
    return f"Operational metric {metric} in {affected_region} deviates from target, impacting system stability."


def estimated_resolution_priority(metric: str, severity: str) -> str:
    if severity == "Critical":
        return "P1 - Resolve within 2 hours"
    if severity == "High":
        return "P2 - Resolve within 8 hours"
    if severity == "Medium":
        return "P3 - Resolve within 24 hours"
    return "P4 - Resolve within 72 hours"


def estimated_urgency_window(severity: str, observed: float, threshold: float) -> dict[str, object]:
    """Calculate urgency window based on severity and deviation magnitude."""
    window = URGENCY_WINDOWS.get(severity, URGENCY_WINDOWS["Medium"])
    base_hours = window["default_hours"]
    
    if threshold != 0:
        deviation_ratio = abs(observed - threshold) / abs(threshold)
        if deviation_ratio > 2.0:
            adjusted_hours = window["min_hours"]
        elif deviation_ratio > 1.5:
            adjusted_hours = base_hours * 0.5
        elif deviation_ratio > 1.0:
            adjusted_hours = base_hours * 0.75
        else:
            adjusted_hours = base_hours
    else:
        adjusted_hours = base_hours
    
    deadline = datetime.utcnow() + timedelta(hours=adjusted_hours)
    
    return {
        "urgency_level": "Immediate" if adjusted_hours <= 4 else "High" if adjusted_hours <= 24 else "Medium" if adjusted_hours <= 72 else "Low",
        "recommended_hours": round(adjusted_hours, 1),
        "deadline": deadline.strftime("%Y-%m-%d %H:%M UTC"),
    }


def actionability_score(metric: str, severity: str, has_owner: bool, has_region: bool) -> dict[str, object]:
    """Score how actionable a recommendation is."""
    score = 0
    factors = []
    
    if has_owner:
        score += 40
        factors.append("Owner assigned")
    else:
        factors.append("No owner assigned")
    
    if has_region:
        score += 30
        factors.append("Region identified")
    else:
        factors.append("Region unknown")
    
    if severity in ("Critical", "High"):
        score += 20
        factors.append("High priority")
    
    if metric in ("network_uptime", "sla_achievement", "avg_latency"):
        score += 10
        factors.append("Clear metric")
    
    return {
        "score": min(100, score),
        "factors": factors,
        "actionability": "High" if score >= 70 else "Medium" if score >= 40 else "Low",
    }


def estimated_completion_hours(severity: str, observed: float, threshold: float) -> float:
    """Compute estimated completion time based on severity and magnitude of deviation."""
    base_hours = {"Critical": 2.0, "High": 8.0, "Medium": 24.0, "Low": 72.0}.get(severity, 24.0)
    if threshold == 0:
        return base_hours
    deviation = abs(observed - threshold) / max(abs(threshold), 1)
    multiplier = min(1.5, max(0.5, deviation))
    return round(base_hours * multiplier, 2)


def completion_time_label(hours: float) -> str:
    if hours <= 2:
        return "Within 2 hours"
    if hours <= 8:
        return "Within 8 hours"
    if hours <= 24:
        return "Within 24 hours"
    if hours <= 72:
        return "Within 72 hours"
    return "Within 1 week"


def enhanced_owner_assignment(rule_recommended_owner: str, severity: str, affected_region: str) -> dict[str, object]:
    """Refine owner assignment with role-based escalation."""
    primary = rule_recommended_owner or "NOC Manager"
    backup = "Network Operations Director" if severity in ("Critical", "High") else "NOC Manager"
    escalation_path = [
        primary,
        backup,
        "VP Operations" if severity == "Critical" else backup,
    ]
    return {
        "primary_owner": primary,
        "backup_owner": backup,
        "escalation_path": escalation_path,
        "assignee_role": severity,
        "region_focus": affected_region,
    }


def recommendation_owner_pool() -> dict[str, list[str]]:
    """Available owners grouped by recommendation type."""
    return {
        "infrastructure": ["Network Operations Director", "Infrastructure Engineering", "Capacity Planning"],
        "service_quality": ["Service Quality Manager", "NOC Manager", "Customer Assurance"],
        "incident": ["Incident Response Lead", "NOC Manager", "On-call Engineer"],
        "customer": ["Customer Assurance Lead", "Service Quality Manager", "Account Manager"],
        "compliance": ["Compliance Officer", "VP Operations", "Audit Team"],
    }


def rule_based_recommendations(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    rules = rows("recommendation_rules")
    overview = overview_metrics(filters=filters)
    regions = {str(row["region"]): row for row in region_analytics(filters=filters)["region_performance_ranking"]}
    recommendations: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    for rule in rules:
        metric = str(rule.get("metric", ""))
        title = str(rule.get("recommendation_title", ""))
        threshold = float(rule.get("threshold", 0))
        condition = str(rule.get("condition", ""))
        severity = str(rule.get("severity", "Medium"))
        target_region = str(title).rsplit(" in ", 1)[-1] if " in " in title else None
        source = regions.get(target_region, {}) if target_region else overview
        observed = float(source.get(metric, 0))
        if not _compare(observed, condition, threshold):
            continue
        affected_region = target_region or (filters.region if filters and filters.region else target_region) or "All Regions"
        affected_service = filters.service_type if filters and filters.service_type else "All Services"
        dedupe_key = (metric, str(affected_region), title)
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
                "business_impact": business_impact_text(metric, observed, threshold, severity, affected_region, affected_service),
                "technical_impact": technical_impact_text(metric, observed, threshold, affected_region),
                "expected_impact": f"Without action, the observed degradation may persist or worsen.",
                "resolution_priority": estimated_resolution_priority(metric, severity),
                "estimated_completion_hours": estimated_completion_hours(severity, observed, threshold),
                "completion_time_label": completion_time_label(estimated_completion_hours(severity, observed, threshold)),
                "owner_assignment": enhanced_owner_assignment(rule["recommended_owner"], severity, affected_region),
                "urgency_window": estimated_urgency_window(severity, observed, threshold),
                "actionability": actionability_score(metric, severity, bool(rule.get("recommended_owner")), bool(target_region)),
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


def _compare(value: float, condition: str, threshold: float) -> bool:
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