# Alarm Management

Enterprise alarm handling system for telecom network operations.

## Alarm Lifecycle

1. **Active** - New alarm created
2. **Acknowledged** - Operator acknowledges receipt
3. **Assigned** - Assigned to technician/team
4. **Resolved** - Root cause addressed
5. **Cleared** - Verified and closed

## Severity Levels

- **Critical** - Service affecting, immediate response required
- **Major** - Significant degradation, urgent attention
- **Minor** - Limited impact, scheduled resolution
- **Warning** - Potential issue, monitoring
- **Info** - Informational, no action required

## Categories

- Network, Performance, Equipment, Security, Application

## API Endpoints

- `GET /api/alarms/summary` - Aggregate counts by severity/status
- `GET /api/alarms` - List with filters (status, severity)
- `POST /api/alarms` - Create alarm
- `POST /api/alarms/{id}/acknowledge` - Acknowledge
- `POST /api/alarms/{id}/assign` - Assign to operator
- `POST /api/alarms/{id}/resolve` - Resolve with notes
