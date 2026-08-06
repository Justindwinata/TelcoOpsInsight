# API Documentation

## Authentication

All endpoints require authentication via Bearer token.

```http
POST /api/auth/login
Content-Type: application/json

{"username": "noc_manager", "password": "telco-demo-2026"}
```

Response:
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_at": "...",
  "user": {...}
}
```

## Core Endpoints

### Health
- `GET /api/health` - Basic health status

### Dashboard
- `GET /api/dashboard/overview` - Key metrics
- `GET /api/dashboard/network-health` - Network metrics
- `GET /api/dashboard/incidents` - Incident analytics
- `GET /api/dashboard/technicians` - Workforce analytics
- `GET /api/dashboard/sla` - SLA metrics

### NOC Command Center
- `GET /api/noc/command-center` - Live network overview

### Alarms
- `GET /api/alarms/summary` - Alarm counts by severity/status
- `GET /api/alarms` - List alarms with filters
- `POST /api/alarms` - Create alarm
- `POST /api/alarms/{id}/acknowledge` - Acknowledge alarm
- `POST /api/alarms/{id}/assign` - Assign alarm
- `POST /api/alarms/{id}/resolve` - Resolve alarm

### Major Incidents
- `GET /api/major-incidents` - List major incidents
- `POST /api/major-incidents` - Create MI
- `GET /api/major-incidents/{id}` - MI details
- `PUT /api/major-incidents/{id}/status` - Update status
- `POST /api/major-incidents/{id}/stakeholders` - Add stakeholder
- `GET /api/major-incidents/{id}/timeline` - Event timeline

### Calendar
- `GET /api/calendar` - Maintenance calendar

### Business Dashboard
- `GET /api/business/dashboard` - Business KPIs

### Exports
- `GET /api/exports/{data_type}/json` - JSON export
- `GET /api/exports/{data_type}/csv` - CSV export

### Cache Management
- `GET /api/cache/stats` - Cache statistics
- `POST /api/cache/invalidate` - Invalidate cache
- `POST /api/cache/clear` - Clear all cache

## Filter Parameters

Most analytics endpoints accept:
- `start_date` - ISO date string
- `end_date` - ISO date string
- `region` - Region name
- `service_type` - Service category
- `severity` - Severity level
- `status` - Status filter

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Standard HTTP status codes:
- 400 - Bad request
- 401 - Unauthorized
- 403 - Forbidden
- 404 - Not found
- 422 - Validation error
- 500 - Internal server error
