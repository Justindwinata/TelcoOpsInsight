from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, rows, as_float


ASSET_LIFECYCLE_STAGES = ["Procurement", "Installation", "Active", "Maintenance", "Retirement"]


def get_asset_lifecycle(asset: dict) -> dict[str, object]:
    """Compute lifecycle stage for a single asset."""
    status = str(asset.get("status", "Active"))
    install_date = asset.get("install_date", "")
    warranty_until = asset.get("warranty_until", "")
    
    lifecycle = {
        "current_stage": "Active",
        "days_since_install": 0,
        "days_until_warranty_expires": 0,
        "days_until_next_maintenance": 0,
        "warranty_status": "Active" if warranty_until else "Unknown",
        "is_warranty_expiring_soon": False,
        "is_overdue_for_maintenance": False,
    }
    
    if install_date:
        try:
            install = datetime.fromisoformat(str(install_date)[:10])
            today = datetime.now()
            lifecycle["days_since_install"] = (today - install).days
        except ValueError:
            pass
    
    if warranty_until:
        try:
            warranty = datetime.fromisoformat(str(warranty_until)[:10])
            today = datetime.now()
            days_left = (warranty - today).days
            lifecycle["days_until_warranty_expires"] = days_left
            lifecycle["warranty_status"] = "Expired" if days_left < 0 else "Active"
            lifecycle["is_warranty_expiring_soon"] = 0 <= days_left <= 30
        except ValueError:
            pass
    
    next_maint = asset.get("next_maintenance", "")
    if next_maint:
        try:
            maint = datetime.fromisoformat(str(next_maint)[:10])
            today = datetime.now()
            days_until = (maint - today).days
            lifecycle["days_until_next_maintenance"] = days_until
            lifecycle["is_overdue_for_maintenance"] = days_until < 0
        except ValueError:
            pass
    
    # Determine lifecycle stage
    if status == "Decommissioned":
        lifecycle["current_stage"] = "Retirement"
    elif status == "Maintenance":
        lifecycle["current_stage"] = "Maintenance"
    elif lifecycle["is_overdue_for_maintenance"]:
        lifecycle["current_stage"] = "Maintenance"
    elif lifecycle["is_warranty_expiring_soon"]:
        lifecycle["current_stage"] = "Active"
        lifecycle["attention_needed"] = "Warranty expiring soon"
    else:
        lifecycle["current_stage"] = "Active"
    
    return lifecycle


def asset_lifecycle_analysis(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Analyze asset lifecycle across all assets."""
    asset_rows = apply_filters(rows("network_assets"), filters)
    
    lifecycle_data = []
    by_stage = defaultdict(int)
    warranty_expiring_soon = []
    overdue_maintenance = []
    
    for asset in asset_rows:
        lifecycle = get_asset_lifecycle(asset)
        lifecycle_data.append({**asset, **lifecycle})
        by_stage[lifecycle["current_stage"]] += 1
        
        if lifecycle["is_warranty_expiring_soon"]:
            warranty_expiring_soon.append({
                "asset_id": asset.get("asset_id"),
                "asset_name": asset.get("asset_name"),
                "vendor": asset.get("vendor"),
                "warranty_until": asset.get("warranty_until"),
                "days_until_expires": lifecycle["days_until_warranty_expires"],
            })
        
        if lifecycle["is_overdue_for_maintenance"]:
            overdue_maintenance.append({
                "asset_id": asset.get("asset_id"),
                "asset_name": asset.get("asset_name"),
                "next_maintenance": asset.get("next_maintenance"),
                "days_overdue": abs(lifecycle["days_until_next_maintenance"]),
            })
    
    total = len(lifecycle_data)
    
    return {
        "by_stage": dict(by_stage),
        "total_assets": total,
        "active_assets": by_stage.get("Active", 0),
        "maintenance_assets": by_stage.get("Maintenance", 0) + by_stage.get("Retirement", 0),
        "warranty_expiring_soon": warranty_expiring_soon[:20],
        "overdue_maintenance": overdue_maintenance[:20],
        "average_days_since_install": round(
            sum(d["days_since_install"] for d in lifecycle_data) / total, 2
        ) if total else 0,
        "lifecycle_data": lifecycle_data[:100],
    }


def asset_detail(asset_id: str) -> dict[str, object] | None:
    """Get detailed information for a single asset."""
    asset_rows = rows("network_assets")
    asset = next((a for a in asset_rows if a.get("asset_id") == asset_id), None)
    
    if not asset:
        return None
    
    lifecycle = get_asset_lifecycle(asset)
    
    return {
        "asset": asset,
        "lifecycle": lifecycle,
        "vendor_info": {
            "name": asset.get("vendor"),
            "model": asset.get("model"),
            "capacity": asset.get("capacity"),
        },
        "maintenance_info": {
            "last_maintenance": asset.get("last_maintenance"),
            "next_maintenance": asset.get("next_maintenance"),
            "is_overdue": lifecycle["is_overdue_for_maintenance"],
            "days_until_maintenance": lifecycle["days_until_next_maintenance"],
        },
        "warranty_info": {
            "install_date": asset.get("install_date"),
            "warranty_until": asset.get("warranty_until"),
            "days_since_install": lifecycle["days_since_install"],
            "days_until_expires": lifecycle["days_until_warranty_expires"],
            "status": lifecycle["warranty_status"],
        },
    }


def search_assets(query: str, filters: AnalyticsFilters | None = None) -> list[dict[str, object]]:
    """Search assets by ID, name, vendor, or model."""
    asset_rows = apply_filters(rows("network_assets"), filters)
    
    query_lower = query.lower()
    results = []
    
    for asset in asset_rows:
        asset_id = str(asset.get("asset_id", "")).lower()
        asset_name = str(asset.get("asset_name", "")).lower()
        vendor = str(asset.get("vendor", "")).lower()
        model = str(asset.get("model", "")).lower()
        
        if (query_lower in asset_id or
            query_lower in asset_name or
            query_lower in vendor or
            query_lower in model):
            results.append(asset)
    
    return results[:50]


def maintenance_scheduling() -> dict[str, object]:
    """Generate preventive maintenance schedule."""
    asset_rows = rows("network_assets")
    
    # Group by next_maintenance date
    by_date = defaultdict(list)
    for asset in asset_rows:
        next_maint = asset.get("next_maintenance", "")
        if next_maint:
            by_date[next_maint].append(asset)
    
    upcoming = sorted(by_date.keys())[:30]
    
    return {
        "upcoming_dates": upcoming,
        "assets_by_date": {k: v[:50] for k, v in by_date.items() if k in upcoming},
        "total_upcoming": sum(len(v) for v in by_date.values() if v[0].get("next_maintenance") in upcoming),
        "by_type": {k: len(v) for k, v in by_date.items() if v},
        "overdue_count": sum(1 for v in by_date.values() if v and v[0].get("next_maintenance") < "2026-08-04"),
    }
