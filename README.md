# TelcoOps Insight

TelcoOps Insight is a portfolio/demo prototype for a fictional telecom operator scenario: **NusaTel Digital Network**. It provides a Network Operations and Service Assurance Dashboard foundation for monitoring synthetic network incidents, SLA achievement, service quality, customer tickets, technician workload, regional performance, and rule-based operational recommendations.

This project uses synthetic data only. It does not use Telkom branding, real company data, live network integrations, OSS/BSS integrations, SSO, or production telecom operations infrastructure.

## Milestone Scope

TOI-0001 delivers:

- deterministic synthetic telecom operations dataset generation
- strict CSV dataset validation
- FastAPI backend with SQLite local persistence
- dashboard analytics endpoints
- rule-based operational recommendations
- JSON and HTML executive summary reports
- React + Vite + TypeScript dashboard frontend
- documentation for metrics, architecture, APIs, and local operation

## Tech Stack

- Backend: Python, FastAPI, SQLite, Pydantic, pytest
- Frontend: React, Vite, TypeScript, Recharts, Vitest
- Data: deterministic synthetic CSV files under `datasets/sample/`

## Quick Start

Generate and validate the sample dataset:

```bash
python3 scripts/generate_synthetic_telco_dataset.py
python3 scripts/validate_telco_dataset.py
```

Run the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://127.0.0.1:5173` and proxy API calls to the backend at `http://127.0.0.1:8000`.

## API And Dashboard

Core backend endpoints:

**Authentication & Data Management:**
- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/datasets/seed`
- `POST /api/datasets/upload`
- `GET /api/datasets/import-history`

**Operations Dashboards:**
- `GET /api/dashboard/overview`
- `GET /api/dashboard/network-health`
- `GET /api/dashboard/incidents`
- `GET /api/dashboard/tickets`
- `GET /api/dashboard/sla`
- `GET /api/dashboard/technicians`
- `GET /api/dashboard/regions`
- `GET /api/dashboard/recommendations`
- `GET /api/dashboard/notifications`

**Enterprise Modules:**
- `GET /api/assets/inventory` - Network asset management
- `GET /api/assets/detail` - Asset detail view
- `GET /api/maintenance/schedule` - Maintenance jobs and scheduling
- `GET /api/changes` - Change management records
- `POST /api/changes` - Create change record
- `POST /api/changes/{id}/transition` - Change status workflow
- `GET /api/rca` - Root cause analysis records
- `POST /api/rca` - Create RCA
- `PUT /api/rca/{id}` - Update RCA
- `GET /api/timeline/incidents` - Incident timeline with events

**Reporting:**
- `GET /api/reports/executive-summary` - JSON report
- `GET /api/reports/executive-summary.html` - HTML report
- `GET /api/reports/executive/summary` - Executive summary metrics
- `GET /api/reports/executive/monthly` - Monthly summary
- `GET /api/reports/executive/weekly` - Weekly summary
- `GET /api/reports/executive/trend` - Trend analysis

**Audit & Admin:**
- `GET /api/audit` - Audit log records

Frontend sections:

- Executive Overview
- Network Health
- Incident Monitoring
- SLA Assurance
- Customer Tickets
- Field Technician Dispatch
- Region Performance
- Recommendations
- Asset Management
- Maintenance Schedule
- Change Management
- Root Cause Analysis
- Incident Timeline
- Data Upload
- Audit Logs
- Report

## Validation

```bash
# Dataset validation
python3 scripts/validate_telco_dataset.py

# Backend tests (100+ tests covering all modules)
cd backend && pytest -q

# Frontend tests (18+ component tests)
cd ../frontend && npm run build && npm test

# Smoke tests
cd .. && python3 scripts/smoke_toi_0003.py

# Manual QA checklist
# See docs/TOI_0004_MANUAL_QA_REPORT.md
```

## TOI-0002 Additions

- Local authentication prototype with role-aware UI.
- Server-side permission checks for seed, persisted import, import history, and reports.
- Shared analytics filters and global frontend filter panel.
- Safe CSV import replacement and persisted import history.
- Incident, SLA, ticket, and technician drilldowns.

## TOI-0003 Additions

- Incident lifecycle workflow with stage progression tracking (Open → Investigating → Escalated → Resolved → Closed).
- Technician assignment and workload balancing analytics with capacity metrics and overload detection.
- SLA breach escalation tracking with severity levels (NONE, WARNING, ALERT, CRITICAL) and recovery indicators.
- Outage impact analytics across regions, services, and customer segments with impact scoring.
- Enhanced recommendation engine with priority scoring, confidence levels, and business impact explanation.
- Operational notification center with categorized alerts and severity-based prioritization.
- Executive dashboard enhanced with notification strip, data-driven KPI thresholds, and trend indicators.
- Enterprise UI polish with loading spinners, error/empty state icons, table hover, and responsive design.
- Backend validation utilities and error handling improvements.
- Expanded regression tests (82 backend, 18 frontend) covering all new operational workflows.

## TOI-0004 Additions (Enterprise Operations Platform)

**New Operational Modules:**

- **Network Asset Management**: 7 asset types (Site, BTS, OLT, ODP, Router, Switch, Transmission) with status tracking, ownership, capacity planning, warranty monitoring, and maintenance scheduling.
- **Maintenance Scheduling**: Preventive/corrective/emergency maintenance workflows with job tracking, first-time-fix metrics, dispatch optimization, and completion verification.
- **Change Management**: Planned/Emergency/Standard change workflow with approval gates, risk assessment, rollback tracking, and completion audit trails.
- **Root Cause Analysis**: Structured RCA with 5 Whys/Fishbone/Barrier/Change Analysis methods, category tracking, lessons learned capture, and preventive action planning.
- **Incident Timeline**: Chronological incident reconstruction with event sequencing (detected → assigned → escalated → investigating → resolved → closed), actor tracking, and resolution history.

**Enhanced Reporting:**

- Executive monthly/weekly/trend summaries with KPI comparisons across periods.
- Region performance ranking with incident counts, critical incidents, SLA achievement, and customer satisfaction.
- Service-type trend analysis with SLA performance tracking.
- Enhanced recommendation engine with priority scoring (P1-P4), business impact, technical impact, and estimated resolution priority.

**Dashboard & UX Improvements:**

- KPI hierarchy and drill-through capabilities.
- Advanced filter combinations (region + service + date + severity).
- Responsive layout optimizations for desktop/tablet/mobile.
- Loading and empty state enhancements.
- Enterprise-grade charts and notifications.

**Backend Reliability:**

- Standardized API response contracts.
- Input validation at all trust boundaries.
- Consistent error handling with proper HTTP status codes.
- Pagination for large datasets.
- Permission checks on sensitive endpoints.

**Testing & Validation:**

- 186-test comprehensive manual QA covering all modules.
- Backend regression tests covering assets, maintenance, changes, RCA, reports, and recommendations.
- Data consistency verification across all views.
- Performance validation (dashboard <3s, asset/incident pages <2s).
- 15+ meaningful commits with incremental feature delivery.

## Product Truth

Allowed positioning: synthetic telecom operations dataset, network operations dashboard, service assurance dashboard, local SQLite persistence, CSV upload validation, rule-based recommendations, decision-support prototype, network asset management, maintenance scheduling, change management workflow, root cause analysis, incident timeline reconstruction, and enterprise operations platform demonstration.

Not implemented or claimed: real-time NOC monitoring, real Telkom/company data, AI/ML prediction, OSS/BSS integration, CRM/ERP integration, enterprise SSO, production-grade enterprise security, multi-tenancy, live network device integration, automated remediation, or guaranteed operational improvement.

## Documentation

- `docs/SYSTEM_ARCHITECTURE.md` - Architecture overview and design decisions
- `docs/METRIC_DEFINITIONS.md` - Analytics metric formulas and calculation logic
- `docs/LOCAL_RUN_GUIDE.md` - Step-by-step local setup and operation
- `docs/DEMO_SCRIPT.md` - Guided demo walkthrough
- `docs/TOI_0004_ENTERPRISE_READINESS_AUDIT.md` - Enterprise capability assessment
- `docs/TOI_0004_MANUAL_QA_REPORT.md` - Comprehensive manual QA results (186 tests)
- `docs/KNOWN_LIMITATIONS.md` - System constraints and future roadmap

## License

Private portfolio/demo prototype. Not for redistribution or commercial use.
