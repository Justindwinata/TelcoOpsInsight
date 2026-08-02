#!/usr/bin/env python3
"""Generate deterministic synthetic telecom operations data for TelcoOps Insight."""

from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path


SEED = 20260001
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 12, 31)
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "datasets" / "sample"

REGIONS = [
    "Jakarta",
    "Bandung",
    "Surabaya",
    "Medan",
    "Makassar",
    "Semarang",
    "Yogyakarta",
    "Denpasar",
    "Palembang",
    "Balikpapan",
]
REGION_COORDS = {
    "Jakarta": (-6.2088, 106.8456),
    "Bandung": (-6.9175, 107.6191),
    "Surabaya": (-7.2575, 112.7521),
    "Medan": (3.5952, 98.6722),
    "Makassar": (-5.1477, 119.4327),
    "Semarang": (-6.9667, 110.4167),
    "Yogyakarta": (-7.7956, 110.3695),
    "Denpasar": (-8.6705, 115.2126),
    "Palembang": (-2.9761, 104.7754),
    "Balikpapan": (-1.2379, 116.8529),
}
SERVICES = [
    "Fiber Internet",
    "Mobile Broadband",
    "Enterprise VPN",
    "IPTV",
    "Voice",
    "Cloud Connectivity",
]
TEAMS = [
    "NOC Core",
    "Field Operations",
    "Customer Assurance",
    "Fiber Maintenance",
    "Enterprise Support",
]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
INCIDENT_STATUSES = ["Open", "Investigating", "Escalated", "Resolved", "Closed"]
TICKET_STATUSES = ["Open", "In Progress", "Waiting Customer", "Resolved", "Closed"]
TICKET_CATEGORIES = [
    "Internet Down",
    "Slow Connection",
    "Intermittent Connection",
    "Billing Related",
    "Installation Delay",
    "Router ONT Issue",
    "Enterprise SLA Complaint",
]
ROOT_CAUSES = [
    "Fiber cut",
    "Power outage",
    "Core router instability",
    "Access node congestion",
    "Customer premises equipment",
    "Planned maintenance overrun",
    "Backhaul packet loss",
    "Configuration drift",
]
SITE_TYPES = ["Core", "Aggregation", "Access", "Edge"]
CUSTOMER_SEGMENTS = ["Residential", "SMB", "Enterprise", "Public Sector"]
JOB_TYPES = ["Corrective Maintenance", "Preventive Maintenance", "Installation", "Site Audit"]


def daterange(step_days: int = 1) -> list[date]:
    days = []
    current = START_DATE
    while current <= END_DATE:
        days.append(current)
        current += timedelta(days=step_days)
    return days


def month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def iso_dt(value: datetime | None) -> str:
    return "" if value is None else value.strftime("%Y-%m-%dT%H:%M:%S")


def weighted_choice(rng: random.Random, weighted: list[tuple[str, float]]) -> str:
    total = sum(weight for _, weight in weighted)
    point = rng.random() * total
    upto = 0.0
    for item, weight in weighted:
        upto += weight
        if upto >= point:
            return item
    return weighted[-1][0]


def is_degraded(region: str, value: date) -> bool:
    windows = {
        "Jakarta": (date(2026, 3, 10), date(2026, 3, 28)),
        "Surabaya": (date(2026, 5, 3), date(2026, 5, 22)),
        "Medan": (date(2026, 7, 8), date(2026, 7, 26)),
        "Makassar": (date(2026, 9, 4), date(2026, 9, 18)),
        "Balikpapan": (date(2026, 11, 9), date(2026, 11, 28)),
    }
    start, end = windows.get(region, (date(2020, 1, 1), date(2020, 1, 1)))
    return start <= value <= end


def write_csv(name: str, rows: list[dict[str, object]], columns: list[str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_sites(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(250):
        region = REGIONS[index % len(REGIONS)]
        service = SERVICES[(index * 3 + rng.randrange(len(SERVICES))) % len(SERVICES)]
        base_lat, base_lon = REGION_COORDS[region]
        criticality = weighted_choice(
            rng,
            [("Low", 0.25), ("Medium", 0.45), ("High", 0.22), ("Critical", 0.08)],
        )
        site_type = weighted_choice(rng, [("Access", 0.55), ("Aggregation", 0.25), ("Edge", 0.12), ("Core", 0.08)])
        capacity_base = {"Core": 10000, "Aggregation": 5000, "Edge": 2500, "Access": 1000}[site_type]
        customers = max(80, int(rng.gauss(1300 if service != "Enterprise VPN" else 450, 360)))
        activation = START_DATE - timedelta(days=rng.randint(180, 3650))
        rows.append(
            {
                "site_id": f"SITE-{index + 1:04d}",
                "site_name": f"{region[:3].upper()} {site_type} Node {index + 1:04d}",
                "region": region,
                "city": region,
                "service_type": service,
                "site_type": site_type,
                "capacity_mbps": capacity_base + rng.randrange(0, capacity_base // 2, 50),
                "active_customers": customers,
                "criticality": criticality,
                "latitude": round(base_lat + rng.uniform(-0.18, 0.18), 6),
                "longitude": round(base_lon + rng.uniform(-0.18, 0.18), 6),
                "activation_date": activation.isoformat(),
            }
        )
    return rows


def build_incidents(rng: random.Random, sites: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    days = daterange()
    for index in range(2200):
        site = rng.choice(sites)
        incident_date = rng.choice(days)
        degraded = is_degraded(str(site["region"]), incident_date)
        severity = weighted_choice(
            rng,
            [("Low", 0.42), ("Medium", 0.34), ("High", 0.18 if not degraded else 0.26), ("Critical", 0.06 if not degraded else 0.15)],
        )
        unresolved = rng.random() < (0.09 if severity in {"High", "Critical"} else 0.05)
        status = weighted_choice(
            rng,
            [("Open", 0.18), ("Investigating", 0.32), ("Escalated", 0.50)],
        ) if unresolved else weighted_choice(rng, [("Resolved", 0.62), ("Closed", 0.38)])
        start_time = datetime.combine(incident_date, datetime.min.time()) + timedelta(
            hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
        )
        duration_base = {"Low": 55, "Medium": 140, "High": 330, "Critical": 620}[severity]
        duration = max(5, int(rng.gauss(duration_base * (1.45 if degraded else 1.0), duration_base * 0.25)))
        resolved_time = None if unresolved else start_time + timedelta(minutes=duration)
        customer_multiplier = {"Low": 0.03, "Medium": 0.10, "High": 0.28, "Critical": 0.55}[severity]
        affected = int(int(site["active_customers"]) * customer_multiplier * rng.uniform(0.5, 1.4))
        rows.append(
            {
                "incident_id": f"INC-2026-{index + 1:05d}",
                "date": incident_date.isoformat(),
                "month": month_key(incident_date),
                "site_id": site["site_id"],
                "region": site["region"],
                "service_type": site["service_type"],
                "severity": severity,
                "status": status,
                "start_time": iso_dt(start_time),
                "resolved_time": iso_dt(resolved_time),
                "duration_minutes": duration,
                "affected_customers": max(0, affected),
                "root_cause": weighted_choice(rng, [(cause, 1.0) for cause in ROOT_CAUSES]),
                "assigned_team": weighted_choice(rng, [(team, 1.0) for team in TEAMS]),
                "escalation_level": {"Low": 1, "Medium": 1, "High": 2, "Critical": 3}[severity],
                "recommended_action": action_for_severity(severity),
            }
        )
    rows.sort(key=lambda item: (item["date"], item["incident_id"]))
    return rows


def action_for_severity(severity: str) -> str:
    return {
        "Low": "Monitor and resolve in standard queue",
        "Medium": "Assign service assurance follow-up",
        "High": "Escalate to regional operations lead",
        "Critical": "Open command bridge and dispatch field team",
    }[severity]


def build_tickets(rng: random.Random, incidents: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    days = daterange()
    for index in range(5400):
        related = rng.choice(incidents) if rng.random() < 0.38 else None
        ticket_date = date.fromisoformat(str(related["date"])) if related else rng.choice(days)
        priority = weighted_choice(rng, [("Low", 0.36), ("Medium", 0.38), ("High", 0.20), ("Critical", 0.06)])
        status = weighted_choice(rng, [("Open", 0.12), ("In Progress", 0.16), ("Waiting Customer", 0.10), ("Resolved", 0.38), ("Closed", 0.24)])
        unresolved = status in {"Open", "In Progress", "Waiting Customer"}
        response = max(2, int(rng.gauss({"Low": 120, "Medium": 75, "High": 35, "Critical": 15}[priority], 18)))
        resolution = "" if unresolved else max(response, int(rng.gauss({"Low": 900, "Medium": 480, "High": 240, "Critical": 120}[priority], 80)))
        segment = weighted_choice(rng, [("Residential", 0.58), ("SMB", 0.21), ("Enterprise", 0.16), ("Public Sector", 0.05)])
        satisfaction = "" if unresolved else max(1, min(5, round(rng.gauss(4.1 if priority in {"Low", "Medium"} else 3.4, 0.65), 1)))
        rows.append(
            {
                "ticket_id": f"TCK-2026-{index + 1:05d}",
                "date": ticket_date.isoformat(),
                "month": month_key(ticket_date),
                "region": related["region"] if related else rng.choice(REGIONS),
                "service_type": related["service_type"] if related else rng.choice(SERVICES),
                "ticket_category": weighted_choice(rng, [(category, 1.0) for category in TICKET_CATEGORIES]),
                "priority": priority,
                "status": status,
                "response_time_minutes": response,
                "resolution_time_minutes": resolution,
                "related_incident_id": related["incident_id"] if related else "",
                "customer_segment": segment,
                "repeat_complaint": "true" if rng.random() < (0.16 if priority in {"High", "Critical"} else 0.08) else "false",
                "satisfaction_score": satisfaction,
            }
        )
    rows.sort(key=lambda item: (item["date"], item["ticket_id"]))
    return rows


def build_sla(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for month in range(1, 13):
        for day in (1, 15):
            metric_date = date(2026, month, day)
            for region in REGIONS:
                degraded = is_degraded(region, metric_date)
                for service in SERVICES:
                    target = 99.5 if service in {"Enterprise VPN", "Cloud Connectivity"} else 98.5
                    actual = target - abs(rng.gauss(0.32 if not degraded else 1.85, 0.28))
                    actual = max(92.0, min(99.95, actual))
                    downtime = round((100 - actual) * 14.4, 2)
                    rows.append(
                        {
                            "date": metric_date.isoformat(),
                            "month": month_key(metric_date),
                            "region": region,
                            "service_type": service,
                            "sla_target": target,
                            "sla_actual": round(actual, 3),
                            "uptime_percentage": round(max(90.0, actual - rng.uniform(0.0, 0.18)), 3),
                            "downtime_minutes": downtime,
                            "mttr_minutes": max(0, int(rng.gauss(130 if not degraded else 310, 45))),
                            "breach_count": 1 if actual < target else 0,
                            "availability_score": round(min(100, actual + rng.uniform(0.0, 0.3)), 3),
                        }
                    )
    return rows


def build_jobs(rng: random.Random, incidents: list[dict[str, object]]) -> list[dict[str, object]]:
    names = ["Adit", "Bima", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hana", "Indra", "Joko", "Kirana", "Lukman"]
    rows: list[dict[str, object]] = []
    for index in range(1800):
        related = rng.choice(incidents) if rng.random() < 0.68 else None
        job_date = date.fromisoformat(str(related["date"])) if related else rng.choice(daterange())
        priority = related["severity"] if related else weighted_choice(rng, [("Low", 0.34), ("Medium", 0.40), ("High", 0.20), ("Critical", 0.06)])
        status = weighted_choice(rng, [("Open", 0.08), ("In Progress", 0.12), ("Resolved", 0.34), ("Closed", 0.46)])
        unresolved = status in {"Open", "In Progress"}
        dispatch = max(5, int(rng.gauss({"Low": 180, "Medium": 100, "High": 55, "Critical": 25}[priority], 20)))
        completion = "" if unresolved else max(dispatch, int(rng.gauss({"Low": 420, "Medium": 300, "High": 220, "Critical": 160}[priority], 55)))
        tech_number = rng.randint(1, 60)
        rows.append(
            {
                "job_id": f"JOB-2026-{index + 1:05d}",
                "date": job_date.isoformat(),
                "month": month_key(job_date),
                "technician_id": f"TECH-{tech_number:03d}",
                "technician_name": f"{rng.choice(names)} {chr(65 + tech_number % 26)}.",
                "region": related["region"] if related else rng.choice(REGIONS),
                "assigned_team": weighted_choice(rng, [(team, 1.0) for team in TEAMS]),
                "job_type": weighted_choice(rng, [(job_type, 1.0) for job_type in JOB_TYPES]),
                "status": status,
                "priority": priority,
                "dispatch_time_minutes": dispatch,
                "completion_time_minutes": completion,
                "first_time_fix": "true" if rng.random() < (0.78 if priority in {"Low", "Medium"} else 0.62) else "false",
                "related_incident_id": related["incident_id"] if related else "",
            }
        )
    rows.sort(key=lambda item: (item["date"], item["job_id"]))
    return rows


def build_region_performance(rng: random.Random, sites: list[dict[str, object]], incidents: list[dict[str, object]], tickets: list[dict[str, object]]) -> list[dict[str, object]]:
    site_counts = {region: sum(1 for site in sites if site["region"] == region) for region in REGIONS}
    rows: list[dict[str, object]] = []
    for metric_date in daterange(7):
        for region in REGIONS:
            degraded = is_degraded(region, metric_date)
            active = sum(1 for incident in incidents if incident["region"] == region and incident["date"] <= metric_date.isoformat() and incident["status"] in {"Open", "Investigating", "Escalated"})
            critical = sum(1 for incident in incidents if incident["region"] == region and incident["date"] == metric_date.isoformat() and incident["severity"] == "Critical")
            open_tickets = sum(1 for ticket in tickets if ticket["region"] == region and ticket["date"] <= metric_date.isoformat() and ticket["status"] in {"Open", "In Progress", "Waiting Customer"})
            affected = sum(int(incident["affected_customers"]) for incident in incidents if incident["region"] == region and incident["date"] == metric_date.isoformat())
            sla = max(92.0, min(99.8, rng.gauss(98.7 if not degraded else 96.1, 0.45)))
            latency = max(8.0, rng.gauss(32 if not degraded else 76, 9))
            loss = max(0.01, rng.gauss(0.45 if not degraded else 2.4, 0.35))
            rows.append(
                {
                    "date": metric_date.isoformat(),
                    "month": month_key(metric_date),
                    "region": region,
                    "total_sites": site_counts[region],
                    "active_incidents": active,
                    "critical_incidents": critical,
                    "open_tickets": open_tickets,
                    "affected_customers": affected,
                    "sla_achievement": round(sla, 3),
                    "avg_latency_ms": round(latency, 2),
                    "packet_loss_rate": round(min(8.0, loss), 3),
                    "technician_utilization": round(max(35, min(98, rng.gauss(68 if not degraded else 86, 7))), 2),
                    "customer_satisfaction": round(max(1, min(5, rng.gauss(4.15 if not degraded else 3.35, 0.35))), 2),
                }
            )
    return rows


def build_quality(rng: random.Random, sites: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sampled_sites = sites[:50]
    for metric_date in daterange(7):
        for site in sampled_sites:
            degraded = is_degraded(str(site["region"]), metric_date)
            timestamp = datetime.combine(metric_date, datetime.min.time()) + timedelta(hours=rng.choice([0, 6, 12, 18]))
            latency = max(5.0, rng.gauss(28 if not degraded else 72, 10))
            loss = max(0.0, rng.gauss(0.35 if not degraded else 2.2, 0.35))
            jitter = max(0.5, rng.gauss(5.5 if not degraded else 18.0, 3.5))
            utilization = max(20.0, min(98.0, rng.gauss(61 if not degraded else 87, 9)))
            availability = max(90.0, min(99.99, rng.gauss(99.1 if not degraded else 96.4, 0.6)))
            score = 100 - (latency * 0.18) - (loss * 8) - (jitter * 0.55) - max(0, utilization - 75) * 0.45 - max(0, 99 - availability) * 3
            rows.append(
                {
                    "timestamp": iso_dt(timestamp),
                    "date": metric_date.isoformat(),
                    "month": month_key(metric_date),
                    "region": site["region"],
                    "site_id": site["site_id"],
                    "service_type": site["service_type"],
                    "latency_ms": round(latency, 2),
                    "packet_loss_rate": round(min(10.0, loss), 3),
                    "jitter_ms": round(jitter, 2),
                    "bandwidth_utilization": round(utilization, 2),
                    "availability_percentage": round(availability, 3),
                    "quality_score": round(max(0, min(100, score)), 2),
                }
            )
    return rows


def build_rules() -> list[dict[str, object]]:
    metrics = [
        ("packet_loss_rate", ">", 1.5, "High", "Reduce packet loss hotspots", "Prioritize backhaul checks and congestion mitigation in affected regions.", "NOC Core"),
        ("sla_achievement", "<", 98.0, "High", "Recover SLA performance", "Review breached services and open a regional recovery plan.", "Customer Assurance"),
        ("active_incidents", ">", 20, "Medium", "Lower active incident queue", "Rebalance incident ownership and age unresolved incidents daily.", "NOC Core"),
        ("critical_incidents", ">", 3, "Critical", "Stabilize critical incidents", "Start executive escalation and assign command bridge ownership.", "NOC Core"),
        ("open_tickets", ">", 180, "Medium", "Reduce ticket backlog", "Add customer assurance capacity for backlog-heavy regions.", "Customer Assurance"),
        ("avg_latency_ms", ">", 55, "Medium", "Investigate latency degradation", "Inspect aggregation nodes and traffic utilization.", "Field Operations"),
        ("technician_utilization", ">", 85, "Medium", "Balance field workload", "Shift non-critical jobs across neighboring regions.", "Field Operations"),
        ("customer_satisfaction", "<", 3.7, "High", "Protect customer experience", "Prioritize repeat complaints and proactive updates.", "Customer Assurance"),
    ]
    rows: list[dict[str, object]] = []
    index = 1
    for region in REGIONS:
        for metric, condition, threshold, severity, title, text, owner in metrics[:4]:
            rows.append(
                {
                    "rule_id": f"RULE-{index:03d}",
                    "metric": metric,
                    "condition": condition,
                    "threshold": threshold,
                    "severity": severity,
                    "recommendation_title": f"{title} in {region}",
                    "recommendation_text": text,
                    "recommended_owner": owner,
                }
            )
            index += 1
    for metric, condition, threshold, severity, title, text, owner in metrics[4:]:
        rows.append(
            {
                "rule_id": f"RULE-{index:03d}",
                "metric": metric,
                "condition": condition,
                "threshold": threshold,
                "severity": severity,
                "recommendation_title": title,
                "recommendation_text": text,
                "recommended_owner": owner,
            }
        )
        index += 1
    return rows


def build_network_assets(rng: random.Random, sites: list[dict[str, object]]) -> list[dict[str, object]]:
    """Build network asset inventory: BTS, OLT, ODP, Router, Switch, Transmission."""
    rows: list[dict[str, object]] = []
    asset_types = ["BTS", "OLT", "ODP", "Router", "Switch", "Transmission"]
    vendors = ["Nokia", "Huawei", "Ericsson", "Cisco", "Juniper", "ZTE"]
    ownership_options = ["NusaTel Owned", "Leased", "Customer Premises", "Partner"]

    asset_id_counter = 1
    for site in sites:
        # Each site has multiple assets
        for asset_type in asset_types:
            count = rng.randint(1, 4)
            for _ in range(count):
                asset_id = f"AST-{asset_id_counter:05d}"
                asset_id_counter += 1
                status = weighted_choice(
                    rng,
                    [("Active", 0.82), ("Maintenance", 0.10), ("Faulty", 0.05), ("Decommissioned", 0.03)],
                )
                vendor = rng.choice(vendors)
                ownership = weighted_choice(
                    rng,
                    [("NusaTel Owned", 0.70), ("Leased", 0.15), ("Customer Premises", 0.10), ("Partner", 0.05)],
                )
                capacity = {
                    "BTS": "100 MHz",
                    "OLT": "10 Gbps",
                    "ODP": "1 Gbps",
                    "Router": "40 Gbps",
                    "Switch": "10 Gbps",
                    "Transmission": "100 Gbps",
                }.get(asset_type, "1 Gbps")
                install_date = START_DATE - timedelta(days=rng.randint(30, 3000))
                warranty_until = install_date + timedelta(days=365 * rng.randint(2, 7))
                rows.append(
                    {
                        "asset_id": asset_id,
                        "asset_type": asset_type,
                        "asset_name": f"{site['region'][:3].upper()}-{asset_type}-{asset_id_counter:03d}",
                        "site_id": site["site_id"],
                        "region": site["region"],
                        "vendor": vendor,
                        "model": f"{vendor[:3].upper()}-{asset_type}-{rng.randint(1000, 9999)}",
                        "status": status,
                        "ownership": ownership,
                        "capacity": capacity,
                        "install_date": install_date.isoformat(),
                        "warranty_until": warranty_until.isoformat(),
                        "last_maintenance": (START_DATE - timedelta(days=rng.randint(1, 180))).isoformat(),
                        "next_maintenance": (START_DATE + timedelta(days=rng.randint(1, 365))).isoformat(),
                    }
                )
    return rows


def main() -> None:
    rng = random.Random(SEED)
    sites = build_sites(rng)
    incidents = build_incidents(rng, sites)
    tickets = build_tickets(rng, incidents)
    sla = build_sla(rng)
    jobs = build_jobs(rng, incidents)
    region_performance = build_region_performance(rng, sites, incidents, tickets)
    quality = build_quality(rng, sites)
    rules = build_rules()
    assets = build_network_assets(rng, sites)

    specs = {
        "network_sites.csv": (sites, list(sites[0].keys())),
        "network_incidents.csv": (incidents, list(incidents[0].keys())),
        "customer_tickets.csv": (tickets, list(tickets[0].keys())),
        "sla_metrics.csv": (sla, list(sla[0].keys())),
        "field_technician_jobs.csv": (jobs, list(jobs[0].keys())),
        "region_performance.csv": (region_performance, list(region_performance[0].keys())),
        "service_quality_metrics.csv": (quality, list(quality[0].keys())),
        "recommendation_rules.csv": (rules, list(rules[0].keys())),
        "network_assets.csv": (assets, list(assets[0].keys())),
    }

    for name, (rows, columns) in specs.items():
        write_csv(name, rows, columns)

    bundle = {
        "project": "TelcoOps Insight",
        "company": "NusaTel Digital Network",
        "business_unit": "Network Operations Center",
        "synthetic_data": True,
        "seed": SEED,
        "period": {"start": START_DATE.isoformat(), "end": END_DATE.isoformat()},
        "regions": REGIONS,
        "service_types": SERVICES,
        "files": {name: len(rows) for name, (rows, _) in specs.items()},
        "disclaimer": "Synthetic demo data only. No real telecom operator data or branding is included.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "telco_ops_sample_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    print("TelcoOps Insight synthetic dataset generated")
    print(f"Seed: {SEED}")
    print(f"Output: {OUT_DIR}")
    for name, (rows, _) in specs.items():
        print(f"- {name}: {len(rows)} rows")
    print("- telco_ops_sample_bundle.json: 1 summary")


if __name__ == "__main__":
    main()
