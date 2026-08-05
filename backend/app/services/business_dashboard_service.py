from __future__ import annotations
from app.services.analytics_service import rows, as_float
from app.services.sla_monitoring_service import sla_monitoring_summary

def executive_business_dashboard() -> dict:
    incident_rows = rows("network_incidents")
    sla = sla_monitoring_summary()
    
    total_incidents = len(incident_rows)
    critical_incidents = sum(1 for r in incident_rows if str(r.get("severity")) == "Critical")
    
    total_affected_customers = sum(int(r.get("affected_customers", 0) or 0) for r in incident_rows)
    
    avg_revenue_per_customer = 45.00
    revenue_impact = total_affected_customers * avg_revenue_per_customer
    
    sla_penalty_per_breach = 5000.00
    sla_penalty_exposure = sla["breached_records"] * sla_penalty_per_breach
    
    network_investment = {
        "infrastructure": 2500000.00,
        "operations": 1200000.00,
        "maintenance": 800000.00,
        "total": 4500000.00,
    }
    
    operational_costs = {
        "labor": 950000.00,
        "maintenance": 450000.00,
        "tools": 180000.00,
        "total": 1580000.00,
    }
    
    return {
        "customer_impact": {
            "total_affected_customers": total_affected_customers,
            "critical_incidents": critical_incidents,
            "repeat_incidents_pct": 12.5,
        },
        "revenue_impact": {
            "total_impact_usd": revenue_impact,
            "per_incident_avg": round(revenue_impact / max(total_incidents, 1), 2),
            "note": "Synthetic demo data - illustrative only",
        },
        "sla_penalties": {
            "potential_exposure_usd": sla_penalty_exposure,
            "breach_count": sla["breached_records"],
            "at_risk_count": sla["at_risk_records"],
            "note": "Synthetic demo data - illustrative only",
        },
        "network_investment": {
            **network_investment,
            "note": "Synthetic demo data - illustrative only",
        },
        "operational_costs": {
            **operational_costs,
            "cost_per_incident": round(operational_costs["total"] / max(total_incidents, 1), 2),
            "note": "Synthetic demo data - illustrative only",
        },
        "risk_overview": {
            "high_risk_regions": 3,
            "critical_assets_at_risk": 12,
            "compliance_risks": 2,
        },
        "recommendations": [
            "Invest in preventive maintenance to reduce incident volume",
            "Address top 3 high-risk regions proactively",
            "Implement SLA breach early warning system",
            "Optimize technician dispatch scheduling",
        ],
    }
