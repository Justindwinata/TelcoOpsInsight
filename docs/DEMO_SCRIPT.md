# Demo Script

1. Start with the README and state that TelcoOps Insight uses synthetic data for a fictional company, NusaTel Digital Network.
2. Run `python3 scripts/generate_synthetic_telco_dataset.py`.
3. Run `python3 scripts/validate_telco_dataset.py` and show the PASS summary.
4. Start the FastAPI backend and open `/health`.
5. Open `/docs` and show the dashboard, dataset, and report endpoints.
6. Run `POST /api/datasets/seed`.
7. Start the frontend and open the Executive Overview.
8. Point out network uptime, SLA achievement, active incidents, ticket backlog, affected customers, MTTR, latency, and recommendations.
9. Navigate through Network Health, Incident Monitoring, SLA Assurance, Customer Tickets, Field Technician Dispatch, Region Performance, Recommendations, Data Upload, and Report.
10. Validate a correct CSV from `datasets/sample/`.
11. Validate an intentionally invalid CSV and show the structured rejection.
12. Open the HTML executive report.
13. Close by stating limitations: synthetic data, fictional company, no live NOC integration, no authentication, no OSS/BSS integration, and rule-based recommendations only.
