# NOC Command Center

The Network Operations Center Command Center is a unified dashboard providing real-time visibility into the entire network operational state.

## Features

- **Live Network Overview**: Uptime, site status, latency, packet loss
- **Regional Health Matrix**: Per-region health scores and incident counts
- **Critical Incidents Feed**: Real-time critical incident display
- **Active Alarms Panel**: Filterable alarm queue with severity
- **SLA Compliance Summary**: Breach rates and MTTR metrics
- **Technician Availability**: Workforce status and utilization
- **Dispatch Status**: Work order pipeline view
- **Maintenance Today**: Scheduled maintenance operations

## API

`GET /api/noc/command-center` - Aggregated NOC data with filter support

## Filters

Supports all standard AnalyticsFilters: region, service_type, date range
