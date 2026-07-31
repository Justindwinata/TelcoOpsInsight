# Demo Script

1. Start with the README and state that TelcoOps Insight uses synthetic data for a fictional company, NusaTel Digital Network.
2. Run `python3 scripts/generate_synthetic_telco_dataset.py`.
3. Run `python3 scripts/validate_telco_dataset.py` and show the PASS summary.
4. Start the FastAPI backend and open `/health`.
5. Open `/docs` and show the dashboard, dataset, and report endpoints.
6. Login as `noc_manager` and run `POST /api/datasets/seed`.
7. Start the frontend and login as `noc_manager`.
8. Open Executive Overview and apply region, service, and date/month filters.
9. Point out network uptime, SLA achievement, active incidents, ticket backlog, affected customers, MTTR, latency, and recommendations.
10. Navigate through Network Health, Incident Monitoring, SLA Assurance, Customer Tickets, Field Technician Dispatch, Region Performance, Recommendations, Data Upload, and Report.
11. Show incident/SLA/ticket/technician drilldowns.
12. Validate a correct CSV from `datasets/sample/`.
13. Persist a valid CSV import only as NOC Manager.
14. Validate an intentionally invalid CSV and show that the existing table remains safe.
15. Open import history and show recorded actor/status.
16. Login as Viewer and show restricted seed/import/history controls are denied or disabled.
17. Open the JSON and HTML executive report.
18. Close by stating limitations: synthetic data, fictional company, no live NOC integration, prototype auth only, no OSS/BSS integration, and rule-based recommendations only.
