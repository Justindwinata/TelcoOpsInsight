# TOI-0002 Implementation Plan

## Objectives

Strengthen TelcoOps Insight as a reliable service assurance prototype with metric correctness, safer import workflows, role-aware access, interactive filters, drilldowns, recommendation hardening, and stronger QA.

## Sequence

1. Document audit and implementation plan.
2. Add metric consistency regression tests.
3. Introduce shared backend filter model.
4. Refactor analytics services to consume the shared filter object.
5. Update dashboard/report endpoints to accept validated filters.
6. Add safe persisted imports that replace only the accepted dataset table.
7. Add persisted import history endpoints.
8. Add prototype authentication with hashed demo users and bearer tokens.
9. Enforce server-side role permissions.
10. Add frontend login/logout and role-aware controls.
11. Add global frontend filter panel.
12. Add incident and SLA drilldowns.
13. Add ticket and technician drilldowns.
14. Harden rule-based recommendations.
15. Polish dashboard UX and state handling.
16. Add frontend and smoke coverage.
17. Update docs for auth, filters, governance, APIs, and limitations.
18. Run full validation and finalize QA report.

## Design Decisions

- Keep SQLite local persistence for TOI-0002.
- Keep authentication prototype-level with local demo users; do not claim enterprise SSO.
- Use server-side role checks for protected actions even when frontend hides controls.
- Reuse deterministic analytics and validation logic.
- Return filter metadata in API responses where useful without breaking existing core payload keys.
- Keep imports table-scoped and transactional to avoid partial data corruption.

## Role Model

- NOC Manager: full prototype access.
- Service Assurance Lead: dashboard, SLA, tickets, reports, recommendations.
- Field Operations Lead: dashboard, incidents, technicians, reports.
- Analyst: dashboard, upload validation, reports.
- Viewer: read-only dashboard and report access.

## Validation Plan

- Run dataset generation and validation after data/script changes.
- Run backend `pytest -q` after backend changes.
- Run frontend `npm run build` and `npm test` after frontend changes.
- Run `git diff --check` before commits.
- Push every commit to `origin/main`.

## Explicit Non-Goals

- No real telecom company data.
- No Telkom branding.
- No real-time monitoring.
- No OSS/BSS integration.
- No production-grade authentication.
- No enterprise SSO.
- No AI or ML prediction.
- No cloud deployment in this milestone.
