# Authorization Model

TOI-0002 adds a local authentication and role-aware access prototype. It is not enterprise SSO and is not production-grade security.

## Demo Roles

- NOC Manager: full prototype access.
- Service Assurance Lead: dashboard, reports, recommendations, import history.
- Field Operations Lead: dashboard, reports, recommendations.
- Analyst: dashboard, CSV validation, reports.
- Viewer: read-only dashboard and reports.

## Protected Backend Operations

- `POST /api/datasets/seed`: requires `datasets:seed`.
- `POST /api/datasets/upload`: requires `datasets:validate`; persisted import additionally requires `datasets:import`.
- `GET /api/datasets/import-history`: requires `imports:read`.
- `GET /api/reports/executive-summary`: requires `reports:read`.
- `GET /api/reports/executive-summary.html`: requires `reports:read`.

Dashboard analytics remain readable for the prototype dashboard flow.

## Demo Credentials

Demo users are `noc_manager`, `service_assurance`, `field_ops`, `analyst`, and `viewer`.

The local demo password used by tests and manual QA is `telco-demo-2026`. The backend stores PBKDF2 password hashes and salts for demo users, not plaintext password records.
