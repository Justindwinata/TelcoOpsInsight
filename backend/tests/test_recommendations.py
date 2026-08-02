from app.services.recommendation_service import compare, rule_based_recommendations


def test_rule_comparison() -> None:
    assert compare(2.0, ">", 1.0) is True
    assert compare(2.0, "<", 1.0) is False


def test_rule_based_recommendations_shape() -> None:
    payload = rule_based_recommendations()

    assert payload["rules_evaluated"] >= 30
    assert payload["method"] == "deterministic_rule_based"
    if payload["recommendations"]:
        first = payload["recommendations"][0]
        assert "recommended_owner" in first
        assert "observed_value" in first
        assert "trigger_condition" in first
        assert "recommended_action" in first
        assert "supporting_metric_value" in first
        assert "priority_score" in first
        assert "confidence" in first
        assert "business_impact" in first
        assert "expected_impact" in first


def test_rule_based_recommendations_are_filter_aware_and_deduped() -> None:
    from app.filters import AnalyticsFilters

    payload = rule_based_recommendations(filters=AnalyticsFilters(region="Surabaya", service_type="Enterprise VPN"))
    keys = {(item["metric"], item["affected_region"], item["recommendation_title"]) for item in payload["recommendations"]}

    assert len(keys) == len(payload["recommendations"])
    for item in payload["recommendations"]:
        assert item["affected_service"] == "Enterprise VPN"


def test_priority_score_is_positive() -> None:
    payload = rule_based_recommendations()
    for rec in payload["recommendations"]:
        assert rec["priority_score"] > 0


def test_confidence_level_is_valid() -> None:
    payload = rule_based_recommendations()
    valid_levels = {"High", "Medium", "Low"}
    for rec in payload["recommendations"]:
        assert rec["confidence"] in valid_levels


def test_business_impact_is_descriptive() -> None:
    payload = rule_based_recommendations()
    for rec in payload["recommendations"]:
        assert len(rec["business_impact"]) > 20
        assert rec["affected_region"] in rec["business_impact"]
