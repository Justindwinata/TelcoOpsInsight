# TOI-0006 Manual QA Report

## Execution Date
August 4, 2026

## Test Environment
- Backend: Python 3.12, FastAPI, SQLite
- Frontend: React 18, Vite 7, TypeScript
- Dataset: Synthetic 2026 telecom operations data

## Test Coverage

### 1. Authentication & Authorization
- [x] Login with noc_manager / telco-demo-2026 works
- [x] Invalid credentials rejected
- [x] Role-based access maintained
- [x] Protected endpoints require valid token

### 2. Executive Overview
- [x] KPI cards display correctly
- [x] Charts render (uptime trend, service quality)
- [x] Notifications strip shows alerts
- [x] Recommendations panel works
- [x] Filters apply correctly

### 3. Executive Intelligence (NEW)
- [x] Operational Health score displays (e.g., 75.5)
- [x] Health status (Good/Fair/Poor) shown
- [x] Critical Alerts list populated
- [x] Top Risks list populated
- [x] Opportunities list populated
- [x] Recommended Actions with priority/owner/deadline
- [x] Health components breakdown (incident, SLA, asset)

### 4. Network Health & Health Index
- [x] Network Health charts render
- [x] Health Index shows composite score (75.5)
- [x] 4 components: Availability, Reliability, Performance, Capacity
- [x] Sub-scores displayed

### 5. Capacity Utilization
- [x] Services table with congestion levels
- [x] Regions table with utilization
- [x] Monthly trend chart

### 6. KPI Comparison
- [x] Week/Month/Quarter/Year periods
- [x] Delta percentages shown
- [x] Color-coded positive/negative deltas

### 7. Incident Monitoring
- [x] Incident table with all columns
- [x] Severity color-coding
- [x] Status badges
- [x] Drilldowns work

### 8. SLA Assurance
- [x] SLA achievement metrics
- [x] Breach analysis
- [x] Region/service comparison

### 9. Customer Tickets
- [x] Backlog counts
- [x] Category breakdown
- [x] Response/resolution times

### 10. Technician Dispatch
- [x] Utilization metrics
- [x] Workload distribution
- [x] Overload detection

### 11. Region Performance
- [x] Ranking table with health scores
- [x] SLA achievement by region
- [x] Customer satisfaction

### 12. Recommendations
- [x] Priority scoring (P1-P4)
- [x] Business/technical impact text
- [x] NEW: Urgency window with deadline
- [x] NEW: Actionability score
- [x] NEW: Enhanced owner assignment with escalation path
- [x] Severity color-coding

### 13. Asset Management
- [x] 7 asset types shown
- [x] Status breakdown
- [x] Faulty assets list
- [x] Maintenance due

### 14. Maintenance Schedule
- [x] Job type breakdown
- [x] Upcoming/completed tables
- [x] First-time fix rate

### 15. Change Management
- [x] Planned vs Emergency changes
- [x] Approval workflow status
- [x] Rollback tracking

### 16. Root Cause Analysis
- [x] RCA records with categories
- [x] Method (5 Whys, Fishbone, etc.)
- [x] Status progression

### 17. Incident Timeline
- [x] Chronological event list
- [x] Event reconstruction
- [x] Actor tracking

### 18. Data Upload
- [x] File selection
- [x] Validation results
- [x] Import history

### 19. Report
- [x] JSON download
- [x] HTML report
- [x] Filter metadata included

### 20. New API Endpoints Verified
- [x] GET /api/dashboard/intelligence - 200
- [x] GET /api/dashboard/brief - 200
- [x] GET /api/dashboard/trends - 200
- [x] GET /api/dashboard/ranking/regions - 200
- [x] GET /api/dashboard/ranking/technicians - 200
- [x] GET /api/dashboard/operational-timeline - 200
- [x] GET /api/dashboard/what-if?technician_change=5 - 200

### 21. Responsive Design
- [x] Mobile viewport (390x844) renders correctly
- [x] Sidebar collapses appropriately
- [x] Charts remain readable
- [x] Tables scroll horizontally

## Screenshots Captured

20 real runtime screenshots captured via Playwright:

| # | File | Section |
|---|------|---------|
| 1 | toi6-01-login.png | Login |
| 2 | 02-executive-overview.png | Executive Overview |
| 3 | 03-executive-intelligence.png | **Executive Intelligence (NEW)** |
| 4 | 04-network-health.png | Network Health |
| 5 | 05-network-health-index.png | Network Health Index |
| 6 | 06-capacity-utilization.png | Capacity Utilization |
| 7 | 07-kpi-comparison.png | KPI Comparison |
| 8 | 08-incident-monitoring.png | Incident Monitoring |
| 9 | 09-sla-assurance.png | SLA Assurance |
| 10 | 10-customer-tickets.png | Customer Tickets |
| 11 | 11-technician-dispatch.png | Technician Dispatch |
| 12 | 12-region-performance.png | Region Performance |
| 13 | 13-recommendations.png | Recommendations |
| 14 | 14-asset-management.png | Asset Management |
| 15 | 15-maintenance-schedule.png | Maintenance Schedule |
| 16 | 16-change-management.png | Change Management |
| 17 | 17-root-cause-analysis.png | Root Cause Analysis |
| 18 | 18-incident-timeline.png | Incident Timeline |
| 19 | 19-data-upload.png | Data Upload |
| 20 | 20-report.png | Report |

All screenshots saved to `docs/evidence/screenshots/` as valid PNG images (1440x960).

## Regression Verification

- [x] All 114 backend tests pass
- [x] All 23 frontend tests pass
- [x] Frontend build succeeds
- [x] Smoke test passes
- [x] Dataset validation passes (0 errors)
- [x] git diff --check clean

## Summary

**Overall: ✓ PASS** - All TOI-0006 features verified working correctly.