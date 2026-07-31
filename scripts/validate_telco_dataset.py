#!/usr/bin/env python3
"""Validate TelcoOps Insight synthetic telecom dataset files."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "datasets" / "sample"
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 12, 31)

REGIONS = {
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
}
SERVICES = {
    "Fiber Internet",
    "Mobile Broadband",
    "Enterprise VPN",
    "IPTV",
    "Voice",
    "Cloud Connectivity",
}
SEVERITIES = {"Low", "Medium", "High", "Critical"}
INCIDENT_STATUSES = {"Open", "Investigating", "Escalated", "Resolved", "Closed"}
TICKET_STATUSES = {"Open", "In Progress", "Waiting Customer", "Resolved", "Closed"}
BACKLOG_TICKET_STATUSES = {"Open", "In Progress", "Waiting Customer"}
TEAMS = {"NOC Core", "Field Operations", "Customer Assurance", "Fiber Maintenance", "Enterprise Support"}
TICKET_CATEGORIES = {
    "Internet Down",
    "Slow Connection",
    "Intermittent Connection",
    "Billing Related",
    "Installation Delay",
    "Router ONT Issue",
    "Enterprise SLA Complaint",
}
JOB_STATUSES = {"Open", "In Progress", "Resolved", "Closed"}
BOOLEAN_VALUES = {"true", "false", "True", "False", True, False}


REQUIRED_COLUMNS = {
    "network_sites.csv": [
        "site_id",
        "site_name",
        "region",
        "city",
        "service_type",
        "site_type",
        "capacity_mbps",
        "active_customers",
        "criticality",
        "latitude",
        "longitude",
        "activation_date",
    ],
    "network_incidents.csv": [
        "incident_id",
        "date",
        "month",
        "site_id",
        "region",
        "service_type",
        "severity",
        "status",
        "start_time",
        "resolved_time",
        "duration_minutes",
        "affected_customers",
        "root_cause",
        "assigned_team",
        "escalation_level",
        "recommended_action",
    ],
    "customer_tickets.csv": [
        "ticket_id",
        "date",
        "month",
        "region",
        "service_type",
        "ticket_category",
        "priority",
        "status",
        "response_time_minutes",
        "resolution_time_minutes",
        "related_incident_id",
        "customer_segment",
        "repeat_complaint",
        "satisfaction_score",
    ],
    "sla_metrics.csv": [
        "date",
        "month",
        "region",
        "service_type",
        "sla_target",
        "sla_actual",
        "uptime_percentage",
        "downtime_minutes",
        "mttr_minutes",
        "breach_count",
        "availability_score",
    ],
    "field_technician_jobs.csv": [
        "job_id",
        "date",
        "month",
        "technician_id",
        "technician_name",
        "region",
        "assigned_team",
        "job_type",
        "status",
        "priority",
        "dispatch_time_minutes",
        "completion_time_minutes",
        "first_time_fix",
        "related_incident_id",
    ],
    "region_performance.csv": [
        "date",
        "month",
        "region",
        "total_sites",
        "active_incidents",
        "critical_incidents",
        "open_tickets",
        "affected_customers",
        "sla_achievement",
        "avg_latency_ms",
        "packet_loss_rate",
        "technician_utilization",
        "customer_satisfaction",
    ],
    "service_quality_metrics.csv": [
        "timestamp",
        "date",
        "month",
        "region",
        "site_id",
        "service_type",
        "latency_ms",
        "packet_loss_rate",
        "jitter_ms",
        "bandwidth_utilization",
        "availability_percentage",
        "quality_score",
    ],
    "recommendation_rules.csv": [
        "rule_id",
        "metric",
        "condition",
        "threshold",
        "severity",
        "recommendation_title",
        "recommendation_text",
        "recommended_owner",
    ],
}

ROW_RANGES = {
    "network_sites.csv": (250, 250),
    "network_incidents.csv": (1500, 3000),
    "customer_tickets.csv": (3000, 8000),
    "sla_metrics.csv": (1000, 2000),
    "field_technician_jobs.csv": (1000, 3000),
    "region_performance.csv": (365, 1500),
    "service_quality_metrics.csv": (1000, 3000),
    "recommendation_rules.csv": (30, 80),
}


@dataclass
class ValidationResult:
    dataset_type: str
    rows: int
    passed: bool
    errors: list[str]
    warnings: list[str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_date(value: str, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{field} invalid date: {value!r}")
        return None


def parse_datetime(value: str, field: str, errors: list[str], allow_blank: bool = False) -> datetime | None:
    if allow_blank and value == "":
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{field} invalid datetime: {value!r}")
        return None


def parse_float(value: object, field: str, errors: list[str], allow_blank: bool = False) -> float | None:
    if allow_blank and value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{field} invalid number: {value!r}")
        return None


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_columns(name: str, rows: list[dict[str, str]], errors: list[str]) -> None:
    if not rows:
        errors.append(f"{name} has no rows")
        return
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in rows[0]]
    extra = [column for column in rows[0] if column not in REQUIRED_COLUMNS[name]]
    if missing:
        errors.append(f"{name} missing columns: {missing}")
    if extra:
        errors.append(f"{name} has unexpected columns: {extra}")


def check_row_count(name: str, rows: list[dict[str, str]], errors: list[str]) -> None:
    minimum, maximum = ROW_RANGES[name]
    ensure(minimum <= len(rows) <= maximum, f"{name} row count {len(rows)} outside expected range {minimum}-{maximum}", errors)


def check_unique(rows: list[dict[str, str]], field: str, errors: list[str]) -> set[str]:
    values = [row.get(field, "") for row in rows]
    blanks = sum(1 for value in values if value == "")
    if blanks:
        errors.append(f"{field} has {blanks} blank values")
    duplicates = len(values) - len(set(values))
    if duplicates:
        errors.append(f"{field} has {duplicates} duplicate values")
    return set(values)


def check_date_month(row: dict[str, str], field_prefix: str, errors: list[str]) -> date | None:
    value = parse_date(row.get("date", ""), f"{field_prefix}.date", errors)
    if value:
        ensure(START_DATE <= value <= END_DATE, f"{field_prefix}.date outside 2026 sample period: {value}", errors)
        ensure(row.get("month") == value.strftime("%Y-%m"), f"{field_prefix}.month does not match date: {row.get('month')} vs {value}", errors)
    return value


def validate_network_sites(rows: list[dict[str, str]], context: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("network_sites.csv", rows, errors)
    check_row_count("network_sites.csv", rows, errors)
    site_ids = check_unique(rows, "site_id", errors)
    for index, row in enumerate(rows, start=2):
        prefix = f"network_sites.csv:{index}"
        for field in ["site_id", "site_name", "region", "service_type", "criticality", "activation_date"]:
            ensure(row.get(field, "") != "", f"{prefix}.{field} is empty", errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("service_type") in SERVICES, f"{prefix}.service_type invalid: {row.get('service_type')}", errors)
        ensure(row.get("criticality") in SEVERITIES, f"{prefix}.criticality invalid: {row.get('criticality')}", errors)
        capacity = parse_float(row.get("capacity_mbps"), f"{prefix}.capacity_mbps", errors)
        customers = parse_float(row.get("active_customers"), f"{prefix}.active_customers", errors)
        ensure(capacity is not None and capacity > 0, f"{prefix}.capacity_mbps must be > 0", errors)
        ensure(customers is not None and customers >= 0, f"{prefix}.active_customers must be >= 0", errors)
        parse_date(row.get("activation_date", ""), f"{prefix}.activation_date", errors)
    context["site_ids"] = site_ids
    return ValidationResult("network_sites", len(rows), not errors, errors, warnings)


def validate_network_incidents(rows: list[dict[str, str]], context: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("network_incidents.csv", rows, errors)
    check_row_count("network_incidents.csv", rows, errors)
    incident_ids = check_unique(rows, "incident_id", errors)
    site_ids = context.get("site_ids", set())
    for index, row in enumerate(rows, start=2):
        prefix = f"network_incidents.csv:{index}"
        check_date_month(row, prefix, errors)
        ensure(row.get("site_id") in site_ids, f"{prefix}.site_id missing from network_sites: {row.get('site_id')}", errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("service_type") in SERVICES, f"{prefix}.service_type invalid: {row.get('service_type')}", errors)
        ensure(row.get("severity") in SEVERITIES, f"{prefix}.severity invalid: {row.get('severity')}", errors)
        ensure(row.get("status") in INCIDENT_STATUSES, f"{prefix}.status invalid: {row.get('status')}", errors)
        ensure(row.get("assigned_team") in TEAMS, f"{prefix}.assigned_team invalid: {row.get('assigned_team')}", errors)
        duration = parse_float(row.get("duration_minutes"), f"{prefix}.duration_minutes", errors)
        affected = parse_float(row.get("affected_customers"), f"{prefix}.affected_customers", errors)
        ensure(duration is not None and duration >= 0, f"{prefix}.duration_minutes must be >= 0", errors)
        ensure(affected is not None and affected >= 0, f"{prefix}.affected_customers must be >= 0", errors)
        parse_datetime(row.get("start_time", ""), f"{prefix}.start_time", errors)
        resolved = row.get("resolved_time", "")
        if row.get("status") in {"Resolved", "Closed"}:
            ensure(resolved != "", f"{prefix}.resolved_time required for resolved/closed incident", errors)
        parse_datetime(resolved, f"{prefix}.resolved_time", errors, allow_blank=True)
    context["incident_ids"] = incident_ids
    return ValidationResult("network_incidents", len(rows), not errors, errors, warnings)


def validate_customer_tickets(rows: list[dict[str, str]], context: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("customer_tickets.csv", rows, errors)
    check_row_count("customer_tickets.csv", rows, errors)
    check_unique(rows, "ticket_id", errors)
    incident_ids = context.get("incident_ids", set())
    for index, row in enumerate(rows, start=2):
        prefix = f"customer_tickets.csv:{index}"
        check_date_month(row, prefix, errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("service_type") in SERVICES, f"{prefix}.service_type invalid: {row.get('service_type')}", errors)
        ensure(row.get("ticket_category") in TICKET_CATEGORIES, f"{prefix}.ticket_category invalid: {row.get('ticket_category')}", errors)
        ensure(row.get("priority") in SEVERITIES, f"{prefix}.priority invalid: {row.get('priority')}", errors)
        ensure(row.get("status") in TICKET_STATUSES, f"{prefix}.status invalid: {row.get('status')}", errors)
        response = parse_float(row.get("response_time_minutes"), f"{prefix}.response_time_minutes", errors)
        resolution = parse_float(row.get("resolution_time_minutes"), f"{prefix}.resolution_time_minutes", errors, allow_blank=True)
        satisfaction = parse_float(row.get("satisfaction_score"), f"{prefix}.satisfaction_score", errors, allow_blank=True)
        ensure(response is not None and response >= 0, f"{prefix}.response_time_minutes must be >= 0", errors)
        ensure(resolution is None or resolution >= 0, f"{prefix}.resolution_time_minutes must be >= 0 when present", errors)
        ensure(satisfaction is None or 1 <= satisfaction <= 5, f"{prefix}.satisfaction_score must be 1-5 when present", errors)
        ensure(row.get("repeat_complaint") in BOOLEAN_VALUES, f"{prefix}.repeat_complaint must be boolean", errors)
        related = row.get("related_incident_id", "")
        ensure(related == "" or related in incident_ids, f"{prefix}.related_incident_id missing from network_incidents: {related}", errors)
        if row.get("status") not in BACKLOG_TICKET_STATUSES:
            ensure(row.get("resolution_time_minutes") != "", f"{prefix}.resolution_time_minutes required for resolved/closed ticket", errors)
    return ValidationResult("customer_tickets", len(rows), not errors, errors, warnings)


def validate_sla(rows: list[dict[str, str]], _: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("sla_metrics.csv", rows, errors)
    check_row_count("sla_metrics.csv", rows, errors)
    for index, row in enumerate(rows, start=2):
        prefix = f"sla_metrics.csv:{index}"
        check_date_month(row, prefix, errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("service_type") in SERVICES, f"{prefix}.service_type invalid: {row.get('service_type')}", errors)
        for field in ["sla_target", "sla_actual", "uptime_percentage", "availability_score"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and 0 <= value <= 100, f"{prefix}.{field} must be 0-100", errors)
        target = parse_float(row.get("sla_target"), f"{prefix}.sla_target", errors)
        ensure(target is not None and 95 <= target <= 99.9, f"{prefix}.sla_target should be 95-99.9", errors)
        for field in ["downtime_minutes", "mttr_minutes", "breach_count"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and value >= 0, f"{prefix}.{field} must be >= 0", errors)
    return ValidationResult("sla_metrics", len(rows), not errors, errors, warnings)


def validate_jobs(rows: list[dict[str, str]], context: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("field_technician_jobs.csv", rows, errors)
    check_row_count("field_technician_jobs.csv", rows, errors)
    check_unique(rows, "job_id", errors)
    incident_ids = context.get("incident_ids", set())
    for index, row in enumerate(rows, start=2):
        prefix = f"field_technician_jobs.csv:{index}"
        check_date_month(row, prefix, errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("assigned_team") in TEAMS, f"{prefix}.assigned_team invalid: {row.get('assigned_team')}", errors)
        ensure(row.get("status") in JOB_STATUSES, f"{prefix}.status invalid: {row.get('status')}", errors)
        ensure(row.get("priority") in SEVERITIES, f"{prefix}.priority invalid: {row.get('priority')}", errors)
        dispatch = parse_float(row.get("dispatch_time_minutes"), f"{prefix}.dispatch_time_minutes", errors)
        completion = parse_float(row.get("completion_time_minutes"), f"{prefix}.completion_time_minutes", errors, allow_blank=True)
        ensure(dispatch is not None and dispatch >= 0, f"{prefix}.dispatch_time_minutes must be >= 0", errors)
        ensure(completion is None or completion >= 0, f"{prefix}.completion_time_minutes must be >= 0 when present", errors)
        ensure(row.get("first_time_fix") in BOOLEAN_VALUES, f"{prefix}.first_time_fix must be boolean", errors)
        related = row.get("related_incident_id", "")
        ensure(related == "" or related in incident_ids, f"{prefix}.related_incident_id missing from network_incidents: {related}", errors)
    return ValidationResult("field_technician_jobs", len(rows), not errors, errors, warnings)


def validate_region_performance(rows: list[dict[str, str]], _: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("region_performance.csv", rows, errors)
    check_row_count("region_performance.csv", rows, errors)
    for index, row in enumerate(rows, start=2):
        prefix = f"region_performance.csv:{index}"
        check_date_month(row, prefix, errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        total_sites = parse_float(row.get("total_sites"), f"{prefix}.total_sites", errors)
        ensure(total_sites is not None and total_sites > 0, f"{prefix}.total_sites must be > 0", errors)
        for field in ["active_incidents", "critical_incidents", "open_tickets", "affected_customers", "avg_latency_ms"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and value >= 0, f"{prefix}.{field} must be >= 0", errors)
        for field in ["sla_achievement", "packet_loss_rate", "technician_utilization"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and 0 <= value <= 100, f"{prefix}.{field} must be 0-100", errors)
        satisfaction = parse_float(row.get("customer_satisfaction"), f"{prefix}.customer_satisfaction", errors)
        ensure(satisfaction is not None and 1 <= satisfaction <= 5, f"{prefix}.customer_satisfaction must be 1-5", errors)
    return ValidationResult("region_performance", len(rows), not errors, errors, warnings)


def validate_quality(rows: list[dict[str, str]], context: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("service_quality_metrics.csv", rows, errors)
    check_row_count("service_quality_metrics.csv", rows, errors)
    site_ids = context.get("site_ids", set())
    for index, row in enumerate(rows, start=2):
        prefix = f"service_quality_metrics.csv:{index}"
        check_date_month(row, prefix, errors)
        parse_datetime(row.get("timestamp", ""), f"{prefix}.timestamp", errors)
        ensure(row.get("region") in REGIONS, f"{prefix}.region invalid: {row.get('region')}", errors)
        ensure(row.get("site_id") in site_ids, f"{prefix}.site_id missing from network_sites: {row.get('site_id')}", errors)
        ensure(row.get("service_type") in SERVICES, f"{prefix}.service_type invalid: {row.get('service_type')}", errors)
        for field in ["latency_ms", "jitter_ms"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and value >= 0, f"{prefix}.{field} must be >= 0", errors)
        for field in ["packet_loss_rate", "bandwidth_utilization", "availability_percentage", "quality_score"]:
            value = parse_float(row.get(field), f"{prefix}.{field}", errors)
            ensure(value is not None and 0 <= value <= 100, f"{prefix}.{field} must be 0-100", errors)
    return ValidationResult("service_quality_metrics", len(rows), not errors, errors, warnings)


def validate_rules(rows: list[dict[str, str]], _: dict[str, set[str]]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    check_columns("recommendation_rules.csv", rows, errors)
    check_row_count("recommendation_rules.csv", rows, errors)
    check_unique(rows, "rule_id", errors)
    for index, row in enumerate(rows, start=2):
        prefix = f"recommendation_rules.csv:{index}"
        ensure(row.get("severity") in SEVERITIES, f"{prefix}.severity invalid: {row.get('severity')}", errors)
        for field in ["metric", "condition", "threshold", "recommendation_title", "recommendation_text", "recommended_owner"]:
            ensure(row.get(field, "") != "", f"{prefix}.{field} is empty", errors)
    return ValidationResult("recommendation_rules", len(rows), not errors, errors, warnings)


VALIDATORS: dict[str, Callable[[list[dict[str, str]], dict[str, set[str]]], ValidationResult]] = {
    "network_sites.csv": validate_network_sites,
    "network_incidents.csv": validate_network_incidents,
    "customer_tickets.csv": validate_customer_tickets,
    "sla_metrics.csv": validate_sla,
    "field_technician_jobs.csv": validate_jobs,
    "region_performance.csv": validate_region_performance,
    "service_quality_metrics.csv": validate_quality,
    "recommendation_rules.csv": validate_rules,
}


def detect_dataset_type(columns: list[str]) -> str | None:
    normalized = set(columns)
    for name, required in REQUIRED_COLUMNS.items():
        if normalized == set(required):
            return name
    return None


def validate_single_file(path: Path, context: dict[str, set[str]] | None = None, expected_name: str | None = None) -> ValidationResult:
    if context is None:
        context = {}
    rows = read_csv(path)
    dataset_name = expected_name or detect_dataset_type(list(rows[0].keys()) if rows else [])
    if dataset_name is None:
        return ValidationResult(path.stem, len(rows), False, ["Unknown dataset type or invalid columns"], [])
    return VALIDATORS[dataset_name](rows, context)


def validate_dataset(dataset_dir: Path = DATASET_DIR) -> dict[str, object]:
    results: list[ValidationResult] = []
    context: dict[str, set[str]] = {}
    missing = [name for name in REQUIRED_COLUMNS if not (dataset_dir / name).exists()]
    for name in missing:
        results.append(ValidationResult(name.replace(".csv", ""), 0, False, [f"Missing required file: {name}"], []))
    for name in REQUIRED_COLUMNS:
        path = dataset_dir / name
        if path.exists():
            results.append(validate_single_file(path, context, expected_name=name))
    passed = all(result.passed for result in results) and not missing
    return {
        "passed": passed,
        "dataset_dir": str(dataset_dir),
        "results": [result.__dict__ for result in results],
        "row_counts": {result.dataset_type: result.rows for result in results},
    }


def print_summary(summary: dict[str, object]) -> None:
    print(f"TelcoOps dataset validation: {'PASS' if summary['passed'] else 'FAIL'}")
    print(f"Dataset directory: {summary['dataset_dir']}")
    for result in summary["results"]:  # type: ignore[index]
        status = "PASS" if result["passed"] else "FAIL"
        print(f"- {result['dataset_type']}: {status}, rows={result['rows']}, errors={len(result['errors'])}")
        for error in result["errors"][:10]:
            print(f"  error: {error}")
        if len(result["errors"]) > 10:
            print(f"  ... {len(result['errors']) - 10} more errors")


def main() -> int:
    dataset_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DATASET_DIR
    summary = validate_dataset(dataset_dir)
    print_summary(summary)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
