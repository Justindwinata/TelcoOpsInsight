# Real-Time Architecture (TOI-0011)

## Overview

TOI-0011 introduces real-time event streaming capabilities to TelcoOps Insight using **Server-Sent Events (SSE)**.

## Architecture Overview

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Event Simulator    │────▶│  Event Service   │────▶│  SSE Stream      │
│  (Background Task)  │     │  (In-memory +    │     │  (FastAPI +      │
│                     │     │   SQLite)        │     │   sse-starlette) │
└─────────────────────┘     └──────────────────┘     └──────────────────┘
                                   │                        │
                                   ▼                        ▼
                          ┌──────────────────┐     ┌──────────────────┐
                          │  Event Store     │     │  Frontend        │
                          │  (SQLite +       │     │  (EventSource,   │
                          │   In-memory)     │     │   React Hooks)   │
                          └──────────────────┘     └──────────────────┘
```

## Core Components

### 1. Event Service (`event_service.py`)
- **In-memory buffer**: Ring buffer (500 events) for low-latency access
- **SQLite persistence**: All events persisted for audit/history
- **Publish/Subscribe**: Asyncio queues for SSE broadcasting
- **Event types**: 17 event types with 5 severity levels
- **Acknowledge/Resolve**: Event lifecycle management

### 2. Event Simulator (`event_simulator.py`)
- **Background asyncio task**: Generates synthetic network events
- **18 event templates**: Link down/up, high latency, packet loss, fiber cut, device offline/recovery, power failure, maintenance, incidents, alarms, SLA, escalation
- **Configurable interval**: 1-60 seconds
- **Manual trigger**: Single event generation endpoint

### 3. SSE Endpoint (`events.py` + `sse_starlette`)
- **Endpoint**: `/api/events/stream`
- **Protocol**: Server-Sent Events (native EventSource API)
- **Heartbeat**: 30s timeout with heartbeat events
- **Auto-reconnection**: Native EventSource reconnection
- **Auth**: JWT Bearer token via query param

### 4. Simulator Control (`event_simulator.py` router)
- `GET /api/events/simulator/status` - Status & stats
- `POST /api/events/simulator/start` - Start simulator
- `POST /api/events/simulator/stop` - Stop simulator
- `POST /api/events/simulator/interval` - Update interval
- `POST /api/events/simulator/generate` - Manual event

### 5. Live Status Aggregation (`live_status_service.py`)
- **Regional status**: Aggregated health per region
- **Live KPIs**: Event counts, health scores
- **Live SLA**: Compliance from event stream
- **Active operators**: Simulated operator dashboard

## Frontend Architecture

### SSE Client Hook (`useEventStream.ts`)
- Native EventSource connection
- Auto-reconnection via browser
- Pause/resume/clear controls
- Connection info (rate, latency, total events)
- Max 500 events in memory

### Live Notification Hook (`useLiveNotifications.ts`)
- Auto-notifies on Critical/Major events
- Deduplication via event ID tracking
- Integrates with NotificationManager toast system

### Stream Control Component (`StreamControl.tsx`)
- Pause/Resume/Resume controls
- Interval configuration
- Connection status indicator
- Event rate display

### Live Components
- `LiveEventFeed` - Real-time event cards
- `LiveRegionalStatus` - Regional health cards
- `LiveKPIMonitoring` - KPI cards
- `LiveSLAMonitoring` - SLA compliance
- `ActiveOperatorsDashboard` - Operator dashboard

### Pages
- `LiveEvents` - Full event feed page
- `RealTimeNOC` - Integrated NOC command center
- `SystemHealth` - Health monitoring page

## Event Schema

```json
{
  "event_id": "EVT-ABC12345",
  "event_type": "link_down",
  "severity": "Major",
  "title": "Link down at SITE-001",
  "detail": "Network link SITE-001 in Jakarta has gone down.",
  "region": "Jakarta",
  "service_type": "Mobile",
  "site_id": "SITE-001",
  "acknowledged": false,
  "resolved": false,
  "timestamp": "2026-08-06T12:34:56"
}
```

## Event Types

| Type | Default Severity | Description |
|------|-----------------|-------------|
| `link_down` | Major | Network link failure |
| `link_up` | Info | Link recovery |
| `high_latency` | Warning | Latency threshold exceeded |
| `packet_loss` | Warning | Packet loss detected |
| `fiber_cut` | Critical | Physical fiber damage |
| `device_offline` | Major | Device unreachable |
| `device_recovery` | Info | Device back online |
| `power_failure` | Critical | Power outage |
| `maintenance_started` | Info | Maintenance window |
| `maintenance_completed` | Info | Maintenance done |
| `incident_detected` | Major | New incident |
| `alarm_raised` | Warning | Performance alarm |
| `sla_threshold_warning` | Warning | SLA approaching threshold |
| `sla_breach` | Critical | SLA breached |
| `escalation` | Major | Incident escalation |

## Security

- JWT Bearer token authentication
- Query param token for SSE (EventSource doesn't support headers)
- Role-based access control via existing auth

## Performance

- In-memory buffer: 500 events max
- SQLite with WAL mode
- SSE connection keeps single HTTP/1.1 connection
- Frontend caches 500 events
- 30s heartbeat for connection health

## Limitations

1. **SSE is one-way**: Client→Server actions via REST
2. **Single instance**: No Redis pub/sub for multi-instance
3. **In-memory only**: Events in memory, persistent in SQLite
4. **Simulator only**: Synthetic events for demo
5. **No WebSocket fallback**: Requires EventSource support

## Testing

### Backend Tests (`test_toi_011_events.py`)
- Event publish & retrieve
- Event stats & summaries
- Simulator start/stop/interval
- Event history & export (JSON/CSV/HTML)
- Live status endpoints

### Frontend Tests
- EventSource connection
- Live notifications
- Error boundary
- Command palette
- Export center

## Future Enhancements

1. Redis pub/sub for multi-instance
2. WebSocket support for bidirectional
3. Persistent event store (TimescaleDB)
4. Advanced analytics on stream
5. Alerting rules engine
5. Mobile push notifications