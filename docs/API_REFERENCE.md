# API Reference

Base URL for local development: `http://127.0.0.1:8000`.

## Health

`GET /health`

Returns service status and synthetic-data-only flag.

## Datasets

Dataset write and governance endpoints require bearer authentication.

`POST /api/datasets/seed`

Loads sample CSV files from `datasets/sample/` into local SQLite and returns row counts per table.

`POST /api/datasets/upload`

Accepts a CSV multipart upload, detects the dataset type from headers, validates the file, and returns:

- `accepted`
- `dataset_type`
- `rows`
- `errors`
- `warnings`
- `imported`
- `import_id`

Use `persist=true` to replace the corresponding SQLite dataset table after validation passes.

`GET /api/datasets/import-history`

Returns persisted upload/import audit records. Requires `imports:read`.

`GET /api/datasets/import-history/{import_id}`

Returns a single import history record.

## Auth

`POST /api/auth/login`

Returns a bearer token and user profile for a demo user.

`GET /api/auth/me`

Returns the current authenticated user.

`POST /api/auth/logout`

Invalidates the current in-memory token.

## Dashboard

All dashboard endpoints are deterministic and null-safe. Filters are supported where practical: `start_date`, `end_date`, `month`, `region`, `service_type`, `severity`, `status`, and `team`.

`GET /api/dashboard/overview`

Returns total sites, active incidents, critical incidents, resolved incidents, MTTR, uptime, SLA achievement, breaches, latency, packet loss, ticket backlog, repeat complaints, technician utilization, first-time fix rate, affected customers, and satisfaction.

`GET /api/dashboard/network-health`

Returns uptime trend, latency trend, packet loss trend, and service quality summary.

`GET /api/dashboard/incidents`

Returns recent incidents, severity summary, monthly incident trend, root cause breakdown, and top root causes.

`GET /api/dashboard/incidents/drilldown`

Returns incident drilldown by severity, root cause, region, active region, and critical incident detail.

`GET /api/dashboard/incidents/lifecycle`

Returns incident lifecycle stage progression (Open → Investigating → Escalated → Resolved → Closed), active vs resolved breakdown, oldest active incidents, and severity distribution.

`GET /api/dashboard/incidents/outage-impact`

Returns multi-dimensional outage impact analysis including region impact scoring, service impact scoring, severity breakdown, worst-case region/service identification, and total affected customers.

`GET /api/dashboard/tickets`

Returns ticket volume, backlog, category breakdown, response/resolution summary, customer segment summary, and repeat complaint rate.

`GET /api/dashboard/tickets/drilldown`

Returns backlog by region/service, category detail, and repeat complaint detail.

`GET /api/dashboard/sla`

Returns SLA target vs actual, breach count, region/service comparison, and MTTR trend.

`GET /api/dashboard/sla/drilldown`

Returns breached SLA detail, breach breakdown by region/service, and MTTR trend.

`GET /api/dashboard/sla/escalation`

Returns SLA breach escalation tracking with severity levels (NONE, WARNING, ALERT, CRITICAL), breach categorization by gap percentage, affected regions/services, average/max MTTR, and recovery trend.

`GET /api/dashboard/technicians`

Returns technician workload, dispatch time, completion time, first-time fix rate, and job status summary.

`GET /api/dashboard/technicians/drilldown`

Returns workload by region/team, first-time fix by priority, and job detail.

`GET /api/dashboard/technicians/assignment`

Returns technician assignment and workload balancing analytics including per-technician capacity metrics, team capacity distribution, overloaded technician detection, and workload imbalance indicators.

`GET /api/dashboard/regions`

Returns region ranking and latest region health metrics.

`GET /api/dashboard/recommendations`

Returns deterministic rule-based operational recommendations with priority scoring, confidence levels, business impact explanation, and expected impact analysis.

`GET /api/dashboard/notifications`

Returns categorized operational notifications (incident, SLA, technician, ticket, recommendation) with severity-based prioritization, action links, and severity counts.

## Reports

`GET /api/reports/executive-summary`

Returns a JSON executive summary assembled from analytics services.

`GET /api/reports/executive-summary.html`

Returns an HTML executive summary report.
