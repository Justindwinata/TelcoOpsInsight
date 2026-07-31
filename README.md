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

## Product Truth

Allowed positioning: synthetic telecom operations dataset, network operations dashboard, service assurance dashboard, local SQLite persistence, CSV upload validation, rule-based recommendations, and decision-support prototype.

Not implemented or claimed: real-time NOC monitoring, real Telkom/company data, AI/ML prediction, OSS/BSS integration, CRM/ERP integration, enterprise SSO, production-grade enterprise security, or guaranteed operational improvement.
