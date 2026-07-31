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


def test_rule_based_recommendations_are_filter_aware_and_deduped() -> None:
    from app.filters import AnalyticsFilters

    payload = rule_based_recommendations(filters=AnalyticsFilters(region="Surabaya", service_type="Enterprise VPN"))
    keys = {(item["metric"], item["affected_region"], item["recommendation_title"]) for item in payload["recommendations"]}

    assert len(keys) == len(payload["recommendations"])
    for item in payload["recommendations"]:
        assert item["affected_service"] == "Enterprise VPN"
