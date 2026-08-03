# Demo Script

1. Start with the README and state that TelcoOps Insight uses synthetic data for a fictional company, NusaTel Digital Network.
2. Run `python3 scripts/generate_synthetic_telco_dataset.py`.
3. Run `python3 scripts/validate_telco_dataset.py` and show the PASS summary.
4. Start the FastAPI backend and open `/health`.
5. Open `/docs` and show the dashboard, dataset, report, asset, maintenance, change, RCA, and timeline endpoints.
6. Login as `noc_manager` and run `POST /api/datasets/seed`.
7. Start the frontend and login as `noc_manager`.
8. Open Executive Overview and apply region, service, and date/month filters.
9. Point out network uptime, SLA achievement, active incidents, ticket backlog, affected customers, MTTR, latency, and recommendations.
10. Navigate through Network Health, Incident Monitoring, SLA Assurance, Customer Tickets, Field Technician Dispatch, Region Performance, Recommendations.
11. Open the new Enterprise sections: Asset Management, Maintenance Schedule, Change Management, Root Cause Analysis, Incident Timeline.
12. In Asset Management, show the 7 asset types (Site, BTS, OLT, ODP, Router, Switch, Transmission) with status breakdown, health score, faulty assets, and maintenance due.
13. In Maintenance Schedule, show preventive vs corrective jobs, upcoming vs completed, first-time fix rate, and region distribution.
14. In Change Management, show planned vs emergency changes, approval workflow, status transitions, and rollback tracking.
15. In Root Cause Analysis, show RCA records with categories (5 Whys, Fishbone, Barrier Analysis), status progression, and lessons learned.
16. In Incident Timeline, show chronological event reconstruction (detected → assigned → escalated → investigating → resolved → closed) with actor tracking.
17. Validate a correct CSV from `datasets/sample/`.
18. Persist a valid CSV import only as NOC Manager.
19. Validate an intentionally invalid CSV and show that the existing table remains safe.
20. Open import history and show recorded actor/status.
21. Login as Viewer and show restricted seed/import/history controls are denied or disabled.
22. Open the JSON and HTML executive report.
23. Close by stating limitations: synthetic data, fictional company, no live NOC integration, prototype auth only, no OSS/BSS integration, and rule-based recommendations only.
