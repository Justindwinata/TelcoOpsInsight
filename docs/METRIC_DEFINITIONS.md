# Metric Definitions

These definitions are used by the backend analytics service and report endpoints.

## Incident Metrics

Active incidents are incidents with status `Open`, `Investigating`, or `Escalated`.

Resolved incidents are incidents with status `Resolved` or `Closed`.

Critical incidents are incidents whose severity is `Critical`. In overview calculations, critical active incidents count only active critical incidents.

MTTR is the average `duration_minutes` for resolved and closed incidents only. Unresolved incidents are excluded.

Affected customers in the overview is the sum of `affected_customers` for active incidents. Historical charts may use daily incident totals.

## SLA Metrics

SLA achievement is the arithmetic average of `sla_actual` across the filtered SLA rows. This prototype does not apply revenue, customer, or traffic weighting.

SLA breach count is the sum of `breach_count` plus any row where `sla_actual < sla_target`; generated rows already align both values.

Network uptime is the average `uptime_percentage` across the filtered SLA rows.

## Service Quality Metrics

Average latency is the arithmetic average of `latency_ms` across the filtered service-quality rows.

Packet loss rate is the arithmetic average of `packet_loss_rate` across the filtered service-quality rows.

High packet-loss regions are regions whose average packet loss is at least 1.5%.

Quality score is a generated synthetic score from latency, packet loss, jitter, bandwidth utilization, and availability. It is bounded from 0 to 100.

## Ticket Metrics

Ticket backlog is tickets with status `Open`, `In Progress`, or `Waiting Customer`.

Repeat complaint rate is repeat complaints divided by total tickets, expressed as a percentage.

Average response time and resolution time are arithmetic averages over non-empty numeric values.

## Field Operations Metrics

First-time fix rate is completed or resolved jobs with `first_time_fix = true` divided by completed or resolved jobs, expressed as a percentage.

Technician utilization is the average `technician_utilization` from regional performance rows. It is documented as a generated workload score, not payroll utilization.

Field job completion time is the average `completion_time_minutes` over completed or resolved jobs only.

## Regional Metrics

Region performance ranking uses a health score derived from SLA achievement, customer satisfaction, latency, packet loss, active incidents, and critical incidents. Higher is better.

Critical sites are sites with criticality `Critical` plus sites with active critical incidents. The analytics service reports the deduplicated count when needed.

## Safety Rules

Analytics functions must avoid division by zero and return `0`, empty lists, or clear default values instead of `null`, `undefined`, or invalid numbers.

## Filtered Calculations

TOI-0002 applies filters before metric aggregation. Date filters are inclusive. `month` cannot be combined with a date range. Severity maps to incident severity and ticket/job priority where practical.
