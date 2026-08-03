from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, as_bool, rows, avg


def technician_performance_scoring(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Generate detailed technician performance scorecards.
    
    Scores each technician on:
    - Resolution rate (% of jobs resolved)
    - SLA success rate (% of jobs completed within SLA)
    - Average completion time
    - First-time fix rate
    - Workload balance
    """
    job_rows = apply_filters(rows("field_technician_jobs"), filters)
    
    tech_stats: dict[str, dict] = defaultdict(lambda: {
        "total_jobs": 0,
        "completed_jobs": 0,
        "active_jobs": 0,
        "ftf_count": 0,
        "completion_times": [],
        "dispatch_times": [],
        "critical_jobs": 0,
        "critical_completed": 0,
        "regions": set(),
        "teams": set(),
        "priorities": defaultdict(int),
    })
    
    for job in job_rows:
        tech_id = str(job.get("technician_id", "Unknown"))
        team = str(job.get("assigned_team", "Unknown"))
        region = str(job.get("region", "Unknown"))
        status = str(job.get("status", ""))
        priority = str(job.get("priority", "Medium"))
        completion_time = as_float(job.get("completion_time_minutes"))
        dispatch_time = as_float(job.get("dispatch_time_minutes"))
        ftf = as_bool(job.get("first_time_fix"))
        
        stats = tech_stats[tech_id]
        stats["total_jobs"] += 1
        stats["regions"].add(region)
        stats["teams"].add(team)
        stats["priorities"][priority] += 1
        
        if status in ("Resolved", "Closed"):
            stats["completed_jobs"] += 1
            if ftf:
                stats["ftf_count"] += 1
            if completion_time > 0:
                stats["completion_times"].append(completion_time)
            if priority == "Critical":
                stats["critical_completed"] += 1
        else:
            stats["active_jobs"] += 1
        
        if priority == "Critical":
            stats["critical_jobs"] += 1
        
        if dispatch_time > 0:
            stats["dispatch_times"].append(dispatch_time)
    
    # Compute scores for each technician
    rankings = []
    for tech_id, data in tech_stats.items():
        scores = compute_technician_scores(data)
        rankings.append({
            "technician_id": tech_id,
            "assigned_team": list(data["teams"])[0] if data["teams"] else "Unknown",
            "regions": sorted(data["regions"]),
            "composite_score": scores["composite"],
            "resolution_rate": scores["resolution_rate"],
            "first_time_fix_rate": scores["ftf_rate"],
            "avg_completion_time_minutes": scores["avg_completion"],
            "avg_dispatch_time_minutes": scores["avg_dispatch"],
            "workload_balance": scores["workload_balance"],
            "critical_handling": scores["critical_handling"],
            "metrics": {
                "total_jobs": data["total_jobs"],
                "completed_jobs": data["completed_jobs"],
                "active_jobs": data["active_jobs"],
                "critical_jobs": data["critical_jobs"],
                "critical_completed": data["critical_completed"],
                "priority_distribution": dict(data["priorities"]),
            },
        })
    
    rankings.sort(key=lambda r: r["composite_score"], reverse=True)
    
    for i, r in enumerate(rankings):
        r["rank"] = i + 1
    
    # Compute team aggregates
    team_summary = compute_team_summary(rankings)
    
    # Generate insights
    insights = generate_tech_insights(rankings)
    
    return {
        "rankings": rankings,
        "team_summary": team_summary,
        "insights": insights,
        "scoring_method": {
            "resolution_rate_weight": 30,
            "first_time_fix_weight": 25,
            "completion_time_weight": 20,
            "workload_balance_weight": 15,
            "critical_handling_weight": 10,
        },
    }


def compute_technician_scores(data: dict) -> dict[str, float]:
    """Compute individual technician performance scores."""
    
    # Resolution Rate (0-100)
    total = data["total_jobs"]
    completed = data["completed_jobs"]
    resolution_rate = (completed / total * 100) if total > 0 else 0
    
    # First-Time Fix Rate (0-100)
    ftf_rate = (data["ftf_count"] / completed * 100) if completed > 0 else 0
    
    # Average Completion Time (0-100, lower = better)
    avg_completion = avg(data["completion_times"]) if data["completion_times"] else 0
    if avg_completion == 0:
        completion_score = 50
    elif avg_completion < 30:
        completion_score = 100
    elif avg_completion < 60:
        completion_score = 85
    elif avg_completion < 120:
        completion_score = 70
    elif avg_completion < 240:
        completion_score = 50
    else:
        completion_score = 30
    
    # Average Dispatch Time
    avg_dispatch = avg(data["dispatch_times"]) if data["dispatch_times"] else 0
    
    # Workload Balance (0-100)
    active = data["active_jobs"]
    workload_balance = 100
    if total > 0:
        active_ratio = active / total
        if active_ratio > 0.6:
            workload_balance = 50
        elif active_ratio > 0.4:
            workload_balance = 70
        elif active_ratio > 0.2:
            workload_balance = 85
        else:
            workload_balance = 100
    
    # Critical Handling (0-100)
    critical_jobs = data["critical_jobs"]
    critical_completed = data["critical_completed"]
    critical_handling = (critical_completed / critical_jobs * 100) if critical_jobs > 0 else 100
    
    # Composite score
    composite = (
        resolution_rate * 0.30 +
        ftf_rate * 0.25 +
        completion_score * 0.20 +
        workload_balance * 0.15 +
        critical_handling * 0.10
    )
    
    return {
        "composite": round(composite, 2),
        "resolution_rate": round(resolution_rate, 2),
        "ftf_rate": round(ftf_rate, 2),
        "avg_completion": round(avg_completion, 2),
        "avg_dispatch": round(avg_dispatch, 2),
        "workload_balance": round(workload_balance, 2),
        "critical_handling": round(critical_handling, 2),
    }


def compute_team_summary(rankings: list) -> list[dict[str, object]]:
    """Compute team-level performance aggregates."""
    team_data: dict[str, list] = defaultdict(list)
    
    for r in rankings:
        team_data[r["assigned_team"]].append(r)
    
    team_summary = []
    for team, members in team_data.items():
        team_summary.append({
            "team": team,
            "member_count": len(members),
            "avg_composite_score": round(avg([m["composite_score"] for m in members]), 2),
            "avg_resolution_rate": round(avg([m["resolution_rate"] for m in members]), 2),
            "avg_ftf_rate": round(avg([m["first_time_fix_rate"] for m in members]), 2),
            "total_jobs": sum(m["metrics"]["total_jobs"] for m in members),
            "total_completed": sum(m["metrics"]["completed_jobs"] for m in members),
        })
    
    team_summary.sort(key=lambda t: t["avg_composite_score"], reverse=True)
    return team_summary


def generate_tech_insights(rankings: list) -> dict[str, Any]:
    """Generate insights about technician performance."""
    if not rankings:
        return {}
    
    top = rankings[0]
    bottom = rankings[-1]
    
    high_performers = [r for r in rankings if r["composite_score"] >= 80]
    needs_improvement = [r for r in rankings if r["composite_score"] < 50]
    overloaded = [r for r in rankings if r["metrics"]["active_jobs"] > 10]
    
    insights = {
        "top_performer": {
            "technician_id": top["technician_id"],
            "score": top["composite_score"],
            "strengths": [],
        },
        "needs_attention": [r["technician_id"] for r in needs_improvement[:3]],
        "overloaded": [r["technician_id"] for r in overloaded[:3]],
    }
    
    if top["resolution_rate"] >= 80:
        insights["top_performer"]["strengths"].append("Excellent resolution rate")
    if top["first_time_fix_rate"] >= 70:
        insights["top_performer"]["strengths"].append("High first-time fix rate")
    if top["avg_completion_time_minutes"] < 60:
        insights["top_performer"]["strengths"].append("Fast completion times")
    
    insights["summary"] = f"{len(high_performers)} high performers identified. {len(needs_improvement)} technician(s) need improvement."
    
    return insights