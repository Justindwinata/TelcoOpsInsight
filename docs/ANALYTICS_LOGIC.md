# Analytics Logic

Analytics are implemented in `backend/app/services/analytics_service.py`.

## Data Loading

The analytics service reads SQLite tables. If the database has not been seeded, it loads the deterministic sample dataset before calculation.

## Filtering

Filters are applied in memory after loading rows through the shared `AnalyticsFilters` model:

- `start_date`
- `end_date`
- `month`
- `region`
- `service_type`
- `severity`
- `status`
- `team`

Date ranges are inclusive. `month` cannot be mixed with `start_date` or `end_date`. Severity applies to incident `severity` and job/ticket `priority` where relevant. Team maps to `assigned_team` where the dataset has that field.

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

Rules come from `recommendation_rules.csv` and are evaluated with deterministic comparisons: `>`, `>=`, `<`, `<=`, and `==`. Rules are filter-aware where practical, deduplicated by metric/region/title, sorted by severity, and returned with observed value, trigger condition, owner, affected region/service, explanation, and recommended action.

This is rule-based decision support. It is not AI, machine learning, or forecasting.
