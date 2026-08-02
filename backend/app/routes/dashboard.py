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
from app.services.recommendation_service import rule_based_recommendations


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
