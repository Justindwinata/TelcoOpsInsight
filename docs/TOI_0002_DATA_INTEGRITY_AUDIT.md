# TOI-0002 Data Integrity Audit

Audit date: 2026-08-01 Asia/Jakarta.

## Completed TOI-0001 Baseline

- Synthetic telecom operations dataset exists under `datasets/sample/`.
- Dataset generator and validator exist and pass.
- FastAPI backend exposes health, dataset seed/upload validation, dashboard analytics, recommendations, and report endpoints.
- SQLite local persistence exists for seeded sample data.
- React + Vite + TypeScript frontend exposes 10 dashboard sections.
- Backend tests and frontend build/tests pass.
- Repository is clean and synced with `origin/main`.

## Data Integrity Risks

- CSV upload currently validates files but does not safely persist accepted imports.
- Dataset replacement has no transaction-level workflow for individual table replacement.
- Import attempts are not recorded, so there is no audit trail for governance.
- Validation context for uploaded files depends on sample dataset relationships rather than current database state.
- Metric tests cover main outcomes, but do not independently verify every telecom definition.

## Metric Risks

- Filter handling is implemented as loose function arguments and is not shared across routes.
- Date-range filtering does not exist.
- Status and team filters do not exist.
- Recommendations are evaluated on unfiltered global data.
- Reports do not accept filters.
- Drilldowns are limited to aggregate views and recent tables.

## Access Control Gaps

- No authentication exists.
- No demo users or roles exist.
- Protected write operations such as seed/import are public.
- Report generation and import history have no permission checks.
- Frontend cannot show role-aware controls because no auth context exists.

## Frontend Workflow Gaps

- No global filter panel exists.
- Filter state is not shared across dashboard sections.
- Upload UI validates CSV but does not show import history.
- No login/logout flow exists.
- Some views have basic loading/error/empty states but no permission-denied state.

## QA Gaps

- Browser smoke QA was limited in TOI-0001.
- No scripted E2E/browser smoke test exists.
- Frontend tests do not cover auth, filters, API query params, or recommendation severity rendering.
- Backend tests do not yet cover role-denied actions or import history.

## Test Strategy For TOI-0002

- Add independent metric consistency tests using controlled rows.
- Add filter model validation tests.
- Add filtered endpoint tests.
- Add safe import transaction tests.
- Add import history tests.
- Add auth and role permission tests.
- Add frontend tests for API query params, auth token behavior, filters, and severity rendering.
- Add a stable smoke test script using backend TestClient plus frontend build where browser automation is not reliable.
