# TOI-0002 Manual QA Checklist

Use this checklist after starting the backend and frontend locally.

## Backend

- [ ] Generate dataset with `python3 scripts/generate_synthetic_telco_dataset.py`.
- [ ] Validate dataset with `python3 scripts/validate_telco_dataset.py`.
- [ ] Start backend with `uvicorn app.main:app --reload`.
- [ ] Open `/health`.
- [ ] Open `/docs`.
- [ ] Login as `noc_manager`.
- [ ] Seed sample data with bearer token.
- [ ] Check filtered overview with `region=Jakarta`.
- [ ] Check invalid date range returns HTTP 422.
- [ ] Check JSON executive report with bearer token.
- [ ] Check HTML executive report with bearer token.

## Frontend

- [ ] Start frontend with `npm run dev`.
- [ ] Login as `noc_manager`.
- [ ] Open Executive Overview.
- [ ] Apply region filter.
- [ ] Apply service type filter.
- [ ] Apply date range filter.
- [ ] Verify KPI cards update.
- [ ] Open Network Health and verify trends update.
- [ ] Open Incident Monitoring and verify severity, table, and drilldown.
- [ ] Open SLA Assurance and verify breaches, MTTR, and drilldown table.
- [ ] Open Customer Tickets and verify backlog/category drilldown.
- [ ] Open Field Technician Dispatch and verify workload/first-time fix drilldown.
- [ ] Open Recommendations and verify trigger condition, supporting metric, owner, and action.
- [ ] Upload valid CSV as preview.
- [ ] Persist valid CSV as NOC Manager.
- [ ] Upload invalid CSV with persist enabled and verify rejection.
- [ ] Load Import History and verify records.
- [ ] Login as Viewer and verify restricted seed/import/history controls are disabled or denied.
- [ ] Open Report and use the authenticated HTML report button.
- [ ] Check browser console for major errors.
- [ ] Check desktop, laptop, and narrow mobile widths.

## Automated Smoke

- [ ] Run `python3 scripts/smoke_toi_0002.py`.

Expected result: `TOI-0002 smoke flow: PASS`.
