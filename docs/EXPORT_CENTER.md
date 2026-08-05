# Export Center

Multi-format data export hub for operational reporting.

## Supported Formats

- **CSV** - Comma-separated values
- **JSON** - Structured data
- **HTML** - Formatted reports (planned)
- **Excel (.xlsx)** - Spreadsheet format (planned)

## Exportable Data

- Dashboard snapshots
- Incident history
- Alarm history
- Maintenance history
- SLA metrics
- Analytics results

## API Endpoints

- `GET /api/exports/{data_type}/json` - JSON export
- `GET /api/exports/{data_type}/csv` - CSV export

Supported data types: incidents, alarms, major_incidents, maintenance, sla
