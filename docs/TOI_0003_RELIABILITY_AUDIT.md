# TOI-0003 Reliability Audit

Audit date: 2026-08-02 Asia/Jakarta.

## Working Baseline

- TOI-0001 and TOI-0002 are complete and pushed to `origin/main`.
- Synthetic telecom datasets generate and validate successfully.
- FastAPI, SQLite, dashboard analytics, filters, safe imports, import history, role permissions, and reports exist.
- React dashboard has login, role-aware controls, global filters, drilldowns, upload/import history, recommendations, and reports.
- Backend tests, frontend build/tests, and TOI-0002 smoke script pass.

## Reliability Gaps

- Authentication still uses in-memory bearer tokens and static demo user objects.
- Session expiration and revoked-token behavior need persistent tests and clearer frontend handling.
- Audit logs do not yet persist login, seed, import, report, permission denied, or export activity.
- Import history records accepted/rejected uploads, but there is no rollback/snapshot workflow.
- Database backup/restore tooling does not exist.
- Error responses are useful but not standardized into a shared model.
- Browser E2E and screenshot capture workflows are not yet present.
- Performance benchmark coverage does not exist.

## Session Persistence Plan

- Add SQLite `users` and `sessions` tables.
- Seed demo users into SQLite with PBKDF2 password hashes and active flags.
- Store bearer tokens by SHA-256 token hash, not plaintext token.
- Add expiration and revocation checks in `get_current_user`.
- Preserve current demo account convenience and frontend login flow.

## Audit And Export Plan

- Add `audit_logs` table and service.
- Record login success/failure, logout, seed, CSV validation/import, rejected import, reports, permission denials, and export activity.
- Add role-protected audit listing and CSV export endpoints.

## Rollback Plan

- Snapshot a dataset table before a persisted import.
- Attach snapshot metadata to import history.
- Add rollback endpoint for imported records with snapshots.
- Keep invalid import behavior unchanged: invalid uploads do not replace existing data.

## Performance Strategy

- Add `scripts/benchmark_telco_analytics.py`.
- Use FastAPI TestClient to benchmark seed and key analytics/report endpoints with reasonable local thresholds.
- Print timings and avoid production performance claims.

## E2E And Screenshot Strategy

- Prefer Playwright if available through existing frontend dependencies.
- Add an E2E workflow that starts backend/frontend, logs in, navigates views, applies filters, and checks visible content.
- Add screenshot capture workflow that captures real runtime pages when browser tooling is available.
- If runtime capture cannot execute in a sandbox, document the exact limitation.
