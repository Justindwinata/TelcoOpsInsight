# TelcoOps Insight

Network Operations and Service Assurance Dashboard for synthetic telecom operations data.

## Overview

TelcoOps Insight is an enterprise-grade OSS/NOC platform designed for telecom operators. It provides comprehensive visibility into network operations, service assurance, and business performance.

## Features

### Enterprise Modules
- **NOC Command Center** - Unified live network overview
- **Alarm Management** - Full lifecycle alarm handling
- **Major Incident Management** - ITIL-inspired incident workflow
- **Change Management** - RFC-based change control
- **Maintenance Calendar** - Operational scheduling
- **Service Request** - Customer service workflow
- **Workforce Management** - Technician scheduling
- **SLA Monitoring** - Compliance tracking
- **Capacity Planning** - Resource forecasting
- **Executive Decision Center** - Strategic KPI dashboard

### Analytics
- Regional performance ranking
- Technician performance scoring
- Incident trend analysis
- Predictive incident scoring
- Network health index
- Capacity utilization analysis
- Operational forecasting

### Export & Reporting
- CSV/JSON export
- Print-friendly reports
- Executive briefs
- Operational intelligence

## Architecture

### Backend
- FastAPI with Python
- SQLite database
- JWT authentication
- Role-based permissions

### Frontend
- React + TypeScript
- Vite build tool
- Recharts for data visualization
- Responsive design

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm run test
```

## Configuration

Environment variables (in `.env`):
- `VITE_API_BASE_URL` - Backend API URL

## Documentation

- [Performance Guide](docs/PERFORMANCE_GUIDE.md)
- [Observability Guide](docs/OBSERVABILITY.md)
- [Enterprise Readiness](docs/ENTERPRISE_READINESS.md)
- [NOC Command Center](docs/NOC_COMMAND_CENTER.md)
- [Alarm Management](docs/ALARM_MANAGEMENT.md)
- [Major Incident Management](docs/MAJOR_INCIDENT_MANAGEMENT.md)

## Version History

See [CHANGELOG](CHANGELOG.md) for full history.

## License

MIT
