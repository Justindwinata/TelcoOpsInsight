# Event Streaming Guide (TOI-0011)

## Overview

This document describes the event streaming implementation in TelcoOps Insight using Server-Sent Events (SSE).

## Connecting to the Stream

### From Browser (JavaScript)

```javascript
const token = localStorage.getItem("telcoops_auth_token");
const eventSource = new EventSource(`/api/events/stream?token=${token}`);

eventSource.addEventListener("event", (message) => {
  const event = JSON.parse(message.data);
  console.log("New event:", event);
});

eventSource.addEventListener("heartbeat", () => {
  console.log("Heartbeat received");
});

eventSource.addEventListener("connected", (msg) => {
  console.log("Connected:", msg.data);
});

eventSource.onerror = () => {
  console.log("Disconnected, retrying...");
};
```

### From Python

```python
import requests
import json

token = "your-jwt-token"
url = f"http://localhost:8000/api/events/stream?token={token}"

with requests.get(url, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode())
```

## Event Format

Each event has the structure:

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

## Special Events

| Event Type | Description |
|------------|-------------|
| `connected` | Sent on connection |
| `heartbeat` | Every 30s (keep-alive) |
| `event` | Regular network event |

## Stream Control

The stream supports these controls via React hooks:

```typescript
const { status, pauseStream, resumeStream, clearFeed } = useEventStream(true);

pauseStream();      // Pause incoming events
resumeStream();     // Resume events
clearFeed();        // Clear event buffer
```

### Stream Status Values

| Status | Meaning |
|--------|---------|
| `connected` | Actively receiving events |
| `connecting` | Establishing connection |
| `disconnected` | Connection lost, retrying |
| `paused` | User paused stream |

## Heartbeat & Reconnection

- **Heartbeat**: Sent every 30s (server timeout)
- **Reconnection**: Automatic via EventSource API
- **Connection info**: Tracked via `useEventStream` hook

```typescript
const { connectionInfo } = useEventStream(true);
// connectionInfo: { lastUpdate, eventRate, totalEvents, connectedAt }
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/events/stream` | GET | SSE stream |
| `/api/events/recent` | GET | Recent events |
| `/api/events/history` | GET | Event history |
| `/api/events/summary/type` | GET | Events by type |
| `/api/events/summary/severity` | GET | Events by severity |
| `/api/events/stats` | GET | Statistics |
| `/api/events/publish` | POST | Create event |
| `/api/events/{id}/acknowledge` | POST | Acknowledge |
| `/api/events/{id}/resolve` | POST | Resolve |
| `/api/events/simulator/status` | GET | Simulator status |
| `/api/events/simulator/start` | POST | Start simulator |
| `/api/events/simulator/stop` | POST | Stop simulator |
| `/api/events/simulator/interval` | POST | Set interval |
| `/api/events/simulator/generate` | POST | Generate single event |

## Export Event History

```bash
# JSON
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/events/history?format=json" \
  -o events.json

# CSV
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/events/history?format=csv" \
  -o events.csv

# HTML
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/events/history?format=html" \
  -o events.html
```

## React Integration

```tsx
import { useEventStream } from "./hooks/useEventStream";

function MyComponent() {
  const { events, status, connectionInfo, pauseStream, resumeStream } = useEventStream(true);
  
  return (
    <div>
      <div>Status: {status}</div>
      <div>Events: {totalEvents}</div>
      <button onClick={pauseStream}>Pause</button>
      <button onClick={resumeStream}>Resume</button>
      <div>
        {events.map(e => <EventItem key={e.event_id} event={e} />)}
      </div>
    </div>
  );
}
```

## Live Notifications

```tsx
import { useLiveNotifications } from "./hooks/useLiveNotifications";
import { useEventStream } from "./hooks/useEventStream";

function Notifications() {
  const { events } = useEventStream(true);
  useLiveNotifications(events, true);
  
  return null; // Notifications render via NotificationManager
}
```

## Simulator Control

```bash
# Start simulator
curl -X POST "http://localhost:8000/api/events/simulator/start?interval_seconds=10" \
  -H "Authorization: Bearer $TOKEN"

# Stop simulator
curl -X POST "http://localhost:8000/api/events/simulator/stop" \
  -H "Authorization: Bearer $TOKEN"

# Change interval
curl -X POST "http://localhost:8000/api/events/simulator/interval?interval_seconds=5" \
  -H "Authorization: Bearer $TOKEN"

# Generate single event
curl -X POST "http://localhost:8000/api/events/simulator/generate" \
  -H "Authorization: Bearer $TOKEN"
```

## Best Practices

1. **Always provide token** in query param for SSE
2. **Pause stream** when tab is hidden to save resources
3. **Clear feed** periodically to prevent memory growth
4. **Handle reconnection** gracefully (EventSource does this)
5. **Use REST for actions** (acknowledge, resolve) - SSE is one-way
6. **Monitor connection** via `connectionInfo` for UI indicators

## Error Handling

```javascript
eventSource.onerror = () => {
  if (eventSource.readyState === EventSource.CLOSED) {
    console.log("Connection closed, will retry...");
  }
};
```

## Performance Tips

1. Limit buffer size: 500 events max in memory
2. Pause stream when tab hidden: `document.hidden` check
3. Use `pauseStream()` during heavy UI interactions
4. Clear feed periodically: `clearFeed()` 
5. Monitor `connectionInfo.eventRate` for load

## Live Monitoring Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/live-status/regions` | Regional health |
| `/api/live-status/kpi` | KPI metrics |
| `/api/live-status/sla` | SLA compliance |
| `/api/live-status/operators` | Active operators |

## Event Types

| Type | Severity | Description |
|------|----------|-------------|
| `link_down` | Major | Network link failure |
| `link_up` | Info | Link recovered |
| `high_latency` | Warning | High latency |
| `packet_loss` | Warning | Packet loss |
| `fiber_cut` | Critical | Fiber damage |
| `device_offline` | Major | Device down |
| `device_recovery` | Info | Device up |
| `power_failure` | Critical | Power outage |
| `maintenance_started` | Info | Maintenance |
| `maintenance_completed` | Info | Done |
| `incident_detected` | Major | New incident |
| `alarm_raised` | Warning | Alarm |
| `sla_threshold_warning` | Warning | SLA warning |
| `sla_breach` | Critical | SLA breach |
| `escalation` | Major | Escalation |

## Severity Levels

| Level | Color | Priority |
|-------|-------|----------|
| Info | Blue | Low |
| Warning | Amber | Medium |
| Minor | Green | Low-Medium |
| Major | Orange | High |
| Critical | Red | Critical |

## Security Notes

- Token passed in query param for SSE (EventSource limitation)
- JWT authentication for all endpoints
- Role-based access control
- Rate limiting recommended for production