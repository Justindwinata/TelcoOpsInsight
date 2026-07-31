# Filtering Guide

TOI-0002 adds shared filter handling across backend analytics and frontend dashboard views.

## Supported Filters

- `start_date`: inclusive `YYYY-MM-DD`
- `end_date`: inclusive `YYYY-MM-DD`
- `month`: `YYYY-MM`
- `region`
- `service_type`
- `severity`
- `status`
- `team`

`month` cannot be combined with `start_date` or `end_date`. Invalid date ranges return HTTP 422 with a readable error.

## Dataset Behavior

- Incidents: date, month, region, service type, severity, status, team.
- Tickets: date, month, region, service type, priority as severity, status.
- SLA metrics: date, month, region, service type.
- Technician jobs: date, month, region, priority as severity, status, team.
- Region performance: date, month, region.
- Service quality metrics: date, month, region, service type.

## Frontend Behavior

The global filter panel persists filter choices in `localStorage`. Changing filters updates dashboard API requests and loading states. Reset clears local filter preferences.
