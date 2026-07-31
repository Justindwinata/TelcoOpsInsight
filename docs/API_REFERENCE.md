# API Reference

Base URL for local development: `http://127.0.0.1:8000`.

## Health

`GET /health`

Returns service status and synthetic-data-only flag.

## Datasets

`POST /api/datasets/seed`

Loads sample CSV files from `datasets/sample/` into local SQLite and returns row counts per table.

`POST /api/datasets/upload`

Accepts a CSV multipart upload, detects the dataset type from headers, validates the file, and returns:

- `accepted`
- `dataset_type`
- `rows`
- `errors`
- `warnings`

## Dashboard

All dashboard endpoints are deterministic and null-safe. Basic filters are supported where practical: `region`, `service_type`, `severity`, and `month`.

`GET /api/dashboard/overview`

Returns total sites, active incidents, critical incidents, resolved incidents, MTTR, uptime, SLA achievement, breaches, latency, packet loss, ticket backlog, repeat complaints, technician utilization, first-time fix rate, affected customers, and satisfaction.

`GET /api/dashboard/network-health`

Returns uptime trend, latency trend, packet loss trend, and service quality summary.

`GET /api/dashboard/incidents`

Returns recent incidents, severity summary, monthly incident trend, root cause breakdown, and top root causes.

`GET /api/dashboard/tickets`

Returns ticket volume, backlog, category breakdown, response/resolution summary, customer segment summary, and repeat complaint rate.

`GET /api/dashboard/sla`

Returns SLA target vs actual, breach count, region/service comparison, and MTTR trend.

`GET /api/dashboard/technicians`

Returns technician workload, dispatch time, completion time, first-time fix rate, and job status summary.

`GET /api/dashboard/regions`

Returns region ranking and latest region health metrics.

`GET /api/dashboard/recommendations`

Returns deterministic rule-based operational recommendations.

## Reports

`GET /api/reports/executive-summary`

Returns a JSON executive summary assembled from analytics services.

`GET /api/reports/executive-summary.html`

Returns an HTML executive summary report.
