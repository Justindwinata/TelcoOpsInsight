# Analytics Logic

Analytics are implemented in `backend/app/services/analytics_service.py`.

## Data Loading

The analytics service reads SQLite tables. If the database has not been seeded, it loads the deterministic sample dataset before calculation.

## Filtering

Filters are applied in memory after loading rows:

- `region`
- `service_type`
- `severity`
- `month`

Severity applies to incident `severity` and job/ticket `priority` where relevant.

## Calculations

The service uses simple deterministic helpers:

- `avg(values)`: arithmetic average, returns `0.0` for empty inputs
- `percent(part, total)`: percentage, returns `0.0` when total is zero
- `count_by(rows, field)`: grouped counts for charts
- `avg_by(rows, group, value)`: grouped averages
- `sum_by(rows, group, value)`: grouped sums

Dashboard metrics follow `docs/METRIC_DEFINITIONS.md`.

## Recommendation Logic

Recommendations are implemented in `backend/app/services/recommendation_service.py`.

Rules come from `recommendation_rules.csv` and are evaluated with deterministic comparisons: `>`, `>=`, `<`, `<=`, and `==`. Rules are sorted by severity and returned with observed value, threshold, owner, metric, and region.

This is rule-based decision support. It is not AI, machine learning, or forecasting.
