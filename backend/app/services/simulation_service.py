from __future__ import annotations

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, rows, avg


def simulate_kpi_changes(params: dict | None = None, filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Simulate the impact of operational changes on KPIs.
    
    Supports simulating:
    - Adding/reducing technicians
    - Changing incident response time
    - Improving SLA target
    - Reducing ticket volume
    - Asset replacement
    """
    incident_rows = apply_filters(rows("network_incidents"), filters)
    sla_rows = apply_filters(rows("sla_metrics"), filters)
    ticket_rows = apply_filters(rows("customer_tickets"), filters)
    asset_rows = apply_filters(rows("network_assets"), filters)
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    sim_params = params or {}
    
    # Baseline metrics
    baseline = compute_baseline(incident_rows, sla_rows, ticket_rows, asset_rows, job_rows)
    
    # Apply simulations
    scenarios = {}
    
    # Scenario 1: Change technician count
    if "technician_change" in sim_params:
        scenarios["technician_adjustment"] = simulate_technician_change(job_rows, incident_rows, sim_params["technician_change"])
    
    # Scenario 2: Change response time
    if "response_time_change_pct" in sim_params:
        scenarios["response_time_improvement"] = simulate_response_time_change(incident_rows, sim_params["response_time_change_pct"])
    
    # Scenario 3: Change SLA target
    if "sla_target_change" in sim_params:
        scenarios["sla_target_change"] = simulate_sla_change(sla_rows, sim_params["sla_target_change"])
    
    # Scenario 4: Change ticket volume
    if "ticket_reduction_pct" in sim_params:
        scenarios["ticket_reduction"] = simulate_ticket_reduction(ticket_rows, sim_params["ticket_reduction_pct"])
    
    # Scenario 5: Replace faulty assets
    if "replace_faulty_assets" in sim_params and sim_params["replace_faulty_assets"]:
        scenarios["asset_replacement"] = simulate_asset_replacement(asset_rows, incident_rows)
    
    # Scenario 6: Combined improvement
    if "combined_improvement" in sim_params:
        scenarios["combined"] = simulate_combined_improvement(baseline, sim_params["combined_improvement"])
    
    return {
        "baseline": baseline,
        "scenarios": scenarios,
        "parameters_tested": list(sim_params.keys()),
        "note": "All simulations are deterministic projections based on historical patterns, not ML predictions.",
    }


def compute_baseline(incidents: list, slas: list, tickets: list, assets: list, jobs: list) -> dict[str, object]:
    """Compute baseline operational metrics."""
    active_incidents = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    resolved_incidents = sum(1 for i in incidents if i.get("status") in ("Resolved", "Closed"))
    mttr = avg([as_float(i.get("duration_minutes")) for i in incidents if as_float(i.get("duration_minutes")) > 0])
    sla_achievement = avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 0
    sla_breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    faulty_assets = sum(1 for a in assets if a.get("status") == "Faulty")
    active_jobs = sum(1 for j in jobs if j.get("status") not in ("Resolved", "Closed"))
    
    return {
        "active_incidents": active_incidents,
        "resolved_incidents": resolved_incidents,
        "avg_mttr_minutes": round(mttr, 2),
        "sla_achievement": round(sla_achievement, 2),
        "sla_breaches": sla_breaches,
        "open_tickets": open_tickets,
        "faulty_assets": faulty_assets,
        "active_field_jobs": active_jobs,
    }


def simulate_technician_change(jobs: list, incidents: list, technician_change: int) -> dict[str, object]:
    """Simulate impact of adding or removing technicians."""
    active_jobs = sum(1 for j in jobs if j.get("status") not in ("Resolved", "Closed"))
    completed = [j for j in jobs if j.get("status") in ("Resolved", "Closed")]
    avg_per_tech = len(jobs) / max(len(set(str(j.get("technician_id")) for j in jobs if j.get("technician_id"))), 1)
    
    if technician_change > 0:
        # Adding technicians
        new_capacity = technician_change * avg_per_tech
        projected_completion = len(completed) + new_capacity * 0.8
        backlog_reduction = min(active_jobs, int(new_capacity * 0.5))
        projected_active = active_jobs - backlog_reduction
        active_incidents = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
        projected_mttr = active_incidents * 30 / max(projected_completion, 1) * 60 if projected_completion > 0 else 0
    else:
        # Removing technicians
        reduction = abs(technician_change)
        capacity_loss = reduction * avg_per_tech
        projected_completion = max(0, len(completed) - int(capacity_loss * 0.5))
        backlog_increase = min(active_jobs, int(capacity_loss * 0.3))
        projected_active = active_jobs + backlog_increase
        projected_mttr = len(incidents) * 30 / max(projected_completion, 1) * 60 if projected_completion > 0 else 0
    
    current_mttr = avg([as_float(i.get("duration_minutes")) for i in incidents if as_float(i.get("duration_minutes")) > 0])
    
    return {
        "change": f"{'+' if technician_change > 0 else ''}{technician_change} technician(s)",
        "current_active_jobs": active_jobs,
        "projected_active_jobs": projected_active,
        "current_mttr_minutes": round(current_mttr, 2),
        "projected_mttr_minutes": round(projected_mttr, 2),
        "mttr_improvement_pct": round((1 - projected_mttr / max(current_mttr, 1)) * 100, 2) if current_mttr > 0 else 0,
        "backlog_reduction": backlog_reduction if technician_change > 0 else -backlog_increase,
    }


def simulate_response_time_change(incidents: list, change_pct: float) -> dict[str, object]:
    """Simulate impact of changing response time."""
    current_mttr = avg([as_float(i.get("duration_minutes")) for i in incidents if as_float(i.get("duration_minutes")) > 0])
    active_incidents = sum(1 for i in incidents if i.get("status") in ("Open", "Investigating", "Escalated"))
    
    projected_mttr = current_mttr * (1 + change_pct / 100)
    sla_impact = max(-10, min(10, change_pct * 0.3))
    
    return {
        "change": f"{'+' if change_pct > 0 else ''}{change_pct}% response time change",
        "current_mttr_minutes": round(current_mttr, 2),
        "projected_mttr_minutes": round(projected_mttr, 2),
        "projected_sla_change_pct": round(sla_impact, 2),
        "active_incidents": active_incidents,
    }


def simulate_sla_change(slas: list, sla_change_pct: float) -> dict[str, object]:
    """Simulate impact of changing SLA target."""
    current_achievement = avg([as_float(s.get("sla_actual")) for s in slas]) if slas else 0
    breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < as_float(s.get("sla_target")))
    total = len(slas)
    
    new_target = 100 + sla_change_pct
    new_breaches = sum(1 for s in slas if as_float(s.get("sla_actual")) < new_target)
    
    return {
        "change": f"{'+' if sla_change_pct > 0 else ''}{sla_change_pct}% SLA adjustment",
        "current_achievement": round(current_achievement, 2),
        "current_breaches": breaches,
        "current_breach_rate": round(breaches / total * 100, 2) if total else 0,
        "projected_breaches": new_breaches,
        "projected_breach_rate": round(new_breaches / total * 100, 2) if total else 0,
    }


def simulate_ticket_reduction(tickets: list, reduction_pct: float) -> dict[str, object]:
    """Simulate impact of reducing ticket volume."""
    open_tickets = sum(1 for t in tickets if t.get("status") in ("Open", "In Progress"))
    repeat = sum(1 for t in tickets if str(t.get("repeat_complaint", "")).lower() == "true")
    total = len(tickets)
    
    projected_open = int(open_tickets * (1 - reduction_pct / 100))
    projected_repeat = int(repeat * (1 - reduction_pct / 100))
    
    return {
        "change": f"{reduction_pct}% ticket reduction",
        "current_open_tickets": open_tickets,
        "projected_open_tickets": projected_open,
        "current_repeat_complaints": repeat,
        "projected_repeat_complaints": projected_repeat,
        "open_ticket_reduction": open_tickets - projected_open,
    }


def simulate_asset_replacement(assets: list, incidents: list) -> dict[str, object]:
    """Simulate impact of replacing all faulty assets."""
    faulty = sum(1 for a in assets if a.get("status") == "Faulty")
    active = sum(1 for a in assets if a.get("status") == "Active")
    total = len(assets)
    
    projected_active = active + faulty
    projected_health = projected_active / max(total, 1) * 100
    
    # Estimate incident reduction from faulty assets
    current_health = active / max(total, 1) * 100
    health_improvement = projected_health - current_health
    
    return {
        "change": f"Replace {faulty} faulty assets",
        "current_asset_health": round(current_health, 2),
        "projected_asset_health": round(projected_health, 2),
        "health_improvement_pct": round(health_improvement, 2),
        "faulty_assets_replaced": faulty,
    }


def simulate_combined_improvement(baseline: dict, improvements: dict) -> dict[str, object]:
    """Simulate combined impact of multiple improvements."""
    projected = dict(baseline)
    
    # Apply technician improvements
    tech_change = improvements.get("technicians", 0)
    if tech_change:
        projected["active_field_jobs"] = max(0, baseline["active_field_jobs"] - int(tech_change * 5))
        projected["avg_mttr_minutes"] = max(5, baseline["avg_mttr_minutes"] * (1 - min(tech_change, 10) * 0.05))
    
    # Apply SLA improvements
    sla_improve = improvements.get("sla_improvement_pct", 0)
    if sla_improve:
        projected["sla_achievement"] = min(100, baseline["sla_achievement"] + sla_improve)
        projected["sla_breaches"] = max(0, baseline["sla_breaches"] - int(sla_improve / 5 * max(baseline["sla_breaches"], 1)))
    
    # Apply ticket reduction
    ticket_red = improvements.get("ticket_reduction_pct", 0)
    if ticket_red:
        projected["open_tickets"] = max(0, baseline["open_tickets"] * (1 - ticket_red / 100))
    
    # Apply asset improvements
    asset_fix = improvements.get("replace_assets", False)
    if asset_fix:
        projected["faulty_assets"] = 0
    
    return {
        "change": [
            f"{'+' + str(tech_change) + ' technicians' if tech_change else ''}",
            f"SLA +{sla_improve}%" if sla_improve else "",
            f"Tickets -{ticket_red}%" if ticket_red else "",
            "Replace faulty assets" if asset_fix else "",
        ],
        "projected_metrics": projected,
        "baseline_metrics": baseline,
    }