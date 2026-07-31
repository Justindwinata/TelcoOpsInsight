# TOI-0002 Final Validation

Validation date: 2026-08-01 Asia/Jakarta.

## Pre-Check

- Branch: `main`
- Initial working tree: clean
- Initial divergence: `origin/main...main = 0 0`
- TOI-0001 baseline was present and pushed before TOI-0002 work started.

## Commits

TOI-0002 created 18 meaningful commits and pushed each commit to `origin/main`.

## Commands Run

`python3 scripts/generate_synthetic_telco_dataset.py`

Result: PASS. Generated deterministic seed `20260001` with row counts:

- `network_sites.csv`: 250
- `network_incidents.csv`: 2200
- `customer_tickets.csv`: 5400
- `sla_metrics.csv`: 1440
- `field_technician_jobs.csv`: 1800
- `region_performance.csv`: 530
- `service_quality_metrics.csv`: 2650
- `recommendation_rules.csv`: 44

`python3 scripts/validate_telco_dataset.py`

Result: PASS for all required dataset files.

`pytest -q` from `backend/`

Result: `53 passed, 1 warning`.

`npm run build` from `frontend/`

Result: PASS. Vite production build completed.

`npm test` from `frontend/`

Result: `5 passed` test files, `8 passed` tests.

`python3 scripts/smoke_toi_0002.py`

Result: PASS.

Smoke flow covered health, auth login, seed, filtered overview, incidents, incident drilldown, SLA drilldown, tickets drilldown, technicians drilldown, JSON report, HTML report, viewer denied seed, valid upload preview, invalid persisted import rejection, and import history.

`git diff --check`

Result: PASS with no whitespace errors.

## Implemented Scope

- Metric consistency tests.
- Shared backend filter model.
- Filter-aware analytics and endpoint metadata.
- Safe persisted CSV import replacement.
- Import history and local governance records.
- Local authentication prototype.
- Server-side role permissions.
- Frontend login/logout and role-aware controls.
- Global frontend filter panel.
- Incident, SLA, ticket, and technician drilldowns.
- Hardened rule-based recommendations with supporting metrics and trigger explanations.
- Stronger frontend tests and smoke flow.
- Updated documentation for auth, filtering, governance, APIs, run guide, demo, analytics, and limitations.

## Remaining Limitations

- Data is synthetic.
- NusaTel Digital Network is fictional.
- No real Telkom data or branding is included.
- No real NOC integration exists.
- No real-time streaming exists.
- No OSS/BSS integration exists.
- Authentication is prototype-level.
- There is no enterprise SSO.
- There is no cloud deployment yet.
- Recommendations are rule-based, not AI/ML predictions.
- This is a portfolio/demo prototype, not production telecom software.

## Next Recommended Milestone

TOI-0003 should focus on persisted user/session storage, finer audit exports, browser-based Playwright coverage, dashboard performance tuning, richer upload rollback tools, and deployment preparation if cloud hosting is actually implemented.
