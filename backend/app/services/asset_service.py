from __future__ import annotations

from collections import defaultdict

from app.filters import AnalyticsFilters
from app.services.analytics_service import apply_filters, as_float, count_by, rows


ASSET_TYPES = ["Site", "BTS", "OLT", "ODP", "Router", "Switch", "Transmission"]
ASSET_STATUSES = ["Active", "Maintenance", "Faulty", "Decommissioned"]


def asset_inventory(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Compute network asset inventory analytics.

    Provides asset count by type/status, health metrics, warranty tracking,
    and per-region distribution for operational visibility.
    """
    asset_rows = apply_filters(rows("network_assets"), filters)

    total_assets = len(asset_rows)
    by_type = count_by(asset_rows, "asset_type")
    by_status = count_by(asset_rows, "status")
    by_ownership = count_by(asset_rows, "ownership")
    by_region = count_by(asset_rows, "region")

    faulty = [r for r in asset_rows if r.get("status") == "Faulty"]
    maintenance = [r for r in asset_rows if r.get("status") == "Maintenance"]
    active = [r for r in asset_rows if r.get("status") == "Active"]

    status_breakdown = {status: 0 for status in ASSET_STATUSES}
    for row in asset_rows:
        status = str(row.get("status", "Active"))
        if status in status_breakdown:
            status_breakdown[status] += 1

    type_breakdown = {asset_type: 0 for asset_type in ASSET_TYPES}
    for row in asset_rows:
        asset_type = str(row.get("asset_type", ""))
        if asset_type in type_breakdown:
            type_breakdown[asset_type] += 1

    warranty_expiring = [
        {
            "asset_id": row.get("asset_id"),
            "asset_type": row.get("asset_type"),
            "asset_name": row.get("asset_name"),
            "region": row.get("region"),
            "vendor": row.get("vendor"),
            "warranty_until": row.get("warranty_until"),
            "status": row.get("status"),
        }
        for row in asset_rows
        if str(row.get("warranty_until", "")) != ""
    ]
    warranty_expiring.sort(key=lambda r: str(r["warranty_until"]))

    due_maintenance = [
        {
            "asset_id": row.get("asset_id"),
            "asset_type": row.get("asset_type"),
            "asset_name": row.get("asset_name"),
            "region": row.get("region"),
            "next_maintenance": row.get("next_maintenance"),
            "last_maintenance": row.get("last_maintenance"),
            "status": row.get("status"),
        }
        for row in asset_rows
        if str(row.get("next_maintenance", "")) != ""
    ]
    due_maintenance.sort(key=lambda r: str(r["next_maintenance"]))

    health_score = (
        round((len(active) / total_assets) * 100, 3) if total_assets else 0.0
    )

    return {
        "total_assets": total_assets,
        "asset_types": by_type,
        "asset_statuses": by_status,
        "ownership": by_ownership,
        "region_distribution": by_region,
        "active_count": len(active),
        "faulty_count": len(faulty),
        "maintenance_count": len(maintenance),
        "faulty_assets": faulty[:50],
        "status_breakdown": status_breakdown,
        "type_breakdown": type_breakdown,
        "warranty_expiring": warranty_expiring[:20],
        "due_maintenance": due_maintenance[:20],
        "health_score": health_score,
    }


def asset_detail(filters: AnalyticsFilters | None = None) -> dict[str, object]:
    """Provide detailed asset list with filter support."""
    asset_rows = apply_filters(rows("network_assets"), filters)
    assets = sorted(
        [
            {
                "asset_id": row.get("asset_id"),
                "asset_type": row.get("asset_type"),
                "asset_name": row.get("asset_name"),
                "site_id": row.get("site_id"),
                "region": row.get("region"),
                "vendor": row.get("vendor"),
                "model": row.get("model"),
                "status": row.get("status"),
                "ownership": row.get("ownership"),
                "capacity": row.get("capacity"),
                "install_date": row.get("install_date"),
                "warranty_until": row.get("warranty_until"),
                "last_maintenance": row.get("last_maintenance"),
                "next_maintenance": row.get("next_maintenance"),
            }
            for row in asset_rows
        ],
        key=lambda r: str(r["asset_id"]),
    )
    return {
        "assets": assets,
        "total": len(assets),
    }
