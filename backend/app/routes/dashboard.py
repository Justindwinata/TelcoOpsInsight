from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.analytics_service import (
    incident_analytics,
    incident_drilldown,
    incident_lifecycle,
    network_health,
    outage_impact,
    overview_metrics,
    region_analytics,
    sla_analytics,
    sla_drilldown,
    sla_escalation,
    technician_analytics,
    technician_assignment,
    technician_drilldown,
    ticket_drilldown,
    ticket_analytics,
)
from app.services.notification_service import generate_notifications
from app.services.recommendation_service import rule_based_recommendations
from app.services.advanced_analytics import (
    predictive_incident_scoring,
    network_health_index,
    capacity_utilization,
    kpi_comparison,
)
from app.services.intelligence_service import generate_operational_insights
from app.services.brief_service import generate_executive_brief
from app.services.trend_service import incident_trend_analysis
from app.services.ranking_service import regional_performance_ranking
from app.services.tech_performance_service import technician_performance_scoring
from app.services.operational_timeline_service import operational_timeline
from app.services.simulation_service import simulate_kpi_changes


router = APIRouter(prefix=f"{settings.api_prefix}/dashboard", tags=["dashboard"])


def with_filter_metadata(payload: dict[str, object], filters: AnalyticsFilters) -> dict[str, object]:
    return {**payload, "filter_metadata": filters.metadata()}


@router.get("/overview")
def dashboard_overview(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(overview_metrics(filters=filters), filters)


@router.get("/network-health")
def dashboard_network_health(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(network_health(filters=filters), filters)


@router.get("/incidents")
def dashboard_incidents(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(incident_analytics(filters=filters), filters)


@router.get("/incidents/drilldown")
def dashboard_incidents_drilldown(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(incident_drilldown(filters=filters), filters)


@router.get("/incidents/lifecycle")
def dashboard_incidents_lifecycle(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(incident_lifecycle(filters=filters), filters)


@router.get("/incidents/outage-impact")
def dashboard_incidents_outage_impact(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(outage_impact(filters=filters), filters)


@router.get("/tickets")
def dashboard_tickets(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(ticket_analytics(filters=filters), filters)


@router.get("/tickets/drilldown")
def dashboard_tickets_drilldown(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(ticket_drilldown(filters=filters), filters)


@router.get("/sla")
def dashboard_sla(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(sla_analytics(filters=filters), filters)


@router.get("/sla/drilldown")
def dashboard_sla_drilldown(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(sla_drilldown(filters=filters), filters)


@router.get("/sla/escalation")
def dashboard_sla_escalation(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(sla_escalation(filters=filters), filters)


@router.get("/technicians")
def dashboard_technicians(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(technician_analytics(filters=filters), filters)


@router.get("/technicians/drilldown")
def dashboard_technicians_drilldown(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(technician_drilldown(filters=filters), filters)


@router.get("/technicians/assignment")
def dashboard_technicians_assignment(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(technician_assignment(filters=filters), filters)


@router.get("/regions")
def dashboard_regions(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(region_analytics(filters=filters), filters)


@router.get("/recommendations")
def dashboard_recommendations(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(rule_based_recommendations(filters=filters), filters)


@router.get("/notifications")
def dashboard_notifications(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(generate_notifications(filters=filters), filters)


@router.get("/predictive/incident-risk")
def dashboard_incident_risk(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(predictive_incident_scoring(filters=filters), filters)


@router.get("/health-index")
def dashboard_health_index(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(network_health_index(filters=filters), filters)


@router.get("/capacity")
def dashboard_capacity(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(capacity_utilization(filters=filters), filters)


@router.get("/kpi-comparison")
def dashboard_kpi_comparison(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(kpi_comparison(filters=filters), filters)


@router.get("/intelligence")
def dashboard_intelligence(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(generate_operational_insights(filters=filters), filters)


@router.get("/brief")
def dashboard_brief(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(generate_executive_brief(filters=filters), filters)


@router.get("/trends")
def dashboard_trends(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(incident_trend_analysis(filters=filters), filters)


@router.get("/ranking/regions")
def dashboard_region_ranking(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(regional_performance_ranking(filters=filters), filters)


@router.get("/ranking/technicians")
def dashboard_tech_ranking(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(technician_performance_scoring(filters=filters), filters)


@router.get("/operational-timeline")
def dashboard_operational_timeline(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(operational_timeline(filters=filters), filters)


@router.get("/what-if")
def dashboard_what_if_simulation(
    filters: AnalyticsFilters = Depends(build_filters),
    technician_change: int | None = None,
    response_time_change_pct: float | None = None,
    sla_target_change: float | None = None,
    ticket_reduction_pct: float | None = None,
    replace_faulty_assets: bool | None = None,
) -> dict[str, object]:
    params = {}
    if technician_change is not None:
        params["technician_change"] = technician_change
    if response_time_change_pct is not None:
        params["response_time_change_pct"] = response_time_change_pct
    if sla_target_change is not None:
        params["sla_target_change"] = sla_target_change
    if ticket_reduction_pct is not None:
        params["ticket_reduction_pct"] = ticket_reduction_pct
    if replace_faulty_assets is not None:
        params["replace_faulty_assets"] = replace_faulty_assets
    return with_filter_metadata(simulate_kpi_changes(params=params, filters=filters), filters)
