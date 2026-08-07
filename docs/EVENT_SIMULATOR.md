# Event Simulator Guide (TOI-0011)

## Overview

The Event Simulator generates synthetic network events for real-time dashboard testing and demonstration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Event Simulator                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Background asyncio task (simulator_loop)               │ │
│  │  • Runs every N seconds (configurable 1-60s)           │ │
│  │  • Picks random event template                          │ │
│  │  • Fills template with random region/service/site       │ │
│  │  • Calls publish_event()                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Event Service       │
                  │  • In-memory buffer   │
                  │  • SQLite persistence │
                  │  • SSE broadcasting   │
                  └───────────────────────┘
```

## Event Templates

The simulator uses 18 templates covering realistic telecom scenarios:

| Template | Type | Severity | Description |
|----------|------|----------|-------------|
| Link Down | link_down | Major | Network link failure |
| Link Up | link_up | Info | Link recovery |
| High Latency | high_latency | Warning | Latency threshold exceeded |
| Packet Loss | packet_loss | Warning | Packet loss detected |
| Fiber Cut | fiber_cut | Critical | Physical fiber damage |
| Device Offline | device_offline | Major | Device unreachable |
| Device Recovery | device_recovery | Info | Device back online |
| Power Failure | power_failure | Critical | Power outage |
| Maintenance Started | maintenance_started | Info | Scheduled maintenance |
| Maintenance Completed | maintenance_completed | Info | Maintenance done |
| Incident Detected | incident_detected | Major | New incident |
| Alarm Raised | alarm_raised | Warning | Performance alarm |
| SLA Threshold Warning | sla_threshold_warning | Warning | SLA approaching breach |
| SLA Breach | sla_breach | Critical | SLA breached |
| Escalation | escalation | Major | Incident escalation |

## Configuration

### Region Pool
- Jakarta, Surabaya, Bandung, Medan, Makassar, Denpasar

### Service Pool
- Mobile, Fiber, Broadband, Enterprise, Backbone

### Site Pool
- SITE-001 through SITE-005

### Severity Distribution
Based on template definitions (Critical=4, Major=3, Warning=5, Minor=2, Info=4 templates)

## API Endpoints

### Status
```bash
GET /api/events/simulator/status
```
Response:
```json
{
  "running": true,
  "interval_seconds": 5.0,
  "events_generated": 123,
  "started_at": "2026-08-06T12:00:00",
  "last_event_at": "2026-08-06T12:34:56"
}
```

### Start Simulator
```bash
POST /api/events/simulator/start?interval_seconds=5.0
```

### Stop Simulator
```bash
POST /api/events/simulator/stop
```

### Update Interval
```bash
POST /api/events/simulator/interval?interval_seconds=10.0
```

### Generate Single Event
```bash
POST /api/events/simulator/generate
```

## Event Generation Logic

```python
def generate_random_event():
    template = random.choice(EVENT_TEMPLATES)
    region = random.choice(SIMULATOR_REGIONS)
    service = random.choice(SIMULATOR_SERVICES)
    site = random.choice(SIMULATOR_SITES)
    
    title = template["title_template"].format(site=site, region=region, service=service)
    detail = template["detail_template"].format(site=site, region=region, service=service)
    
    return publish_event(
        event_type=template["type"],
        severity=template["severity"],
        title=title,
        detail=detail,
        region=region,
        service_type=service,
        site_id=site,
    )
```

## Event Template Structure

```python
{
    "type": "link_down",
    "severity": "Major",
    "title_template": "Link down at {site}",
    "detail_template": "Network link {site} in {region} has gone down. Service {service} affected.",
}
```

## Statistics Tracking

The simulator tracks:
- `running`: Boolean
- `interval_seconds`: Current interval (1-60s)
- `events_generated`: Counter
- `started_at`: ISO timestamp
- `last_event_at`: ISO timestamp

## Integration with Event Service

The simulator calls `publish_event()` which:
1. Validates event type/severity
2. Creates event object with UUID
2. Persists to SQLite
3. Adds to in-memory buffer (500 max)
4. Broadcasts to SSE subscribers
5. Updates statistics

## Usage Examples

### Start Simulator (5 second interval)
```bash
curl -X POST "http://localhost:8000/api/events/simulator/start?interval_seconds=5" \
  -H "Authorization: Bearer $TOKEN"
```

### Generate Single Event for Testing
```bash
curl -X POST "http://localhost:8000/api/events/simulator/generate" \
  -H "Authorization: Bearer $TOKEN"
```

### Change Interval to 10 seconds
```bash
curl -X POST "http://localhost:8000/api/events/simulator/interval?interval_seconds=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Stop Simulator
```bash
curl -X POST "http://localhost:8000/api/events/simulator/stop" \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Integration

### Start Simulator on Page Load
```tsx
useEffect(() => {
  fetch("/api/events/simulator/start?interval_seconds=5", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => setSimRunning(true));
  
  return () => {
    fetch("/api/events/simulator/stop", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  }, []);
```

### Stream Status Display
```tsx
const { status } = useEventStream(true);
// status: "connected" | "paused" | "disconnected"
```

### Stream Control
```tsx
const { pauseStream, resumeStream, clearFeed } = useEventStream(true);
// pauseStream() / resumeStream() / clearFeed()
```

## Best Practices

1. **Start simulator on NOC page load**, stop on unmount
2. **Use 5-10 second intervals** for demo (not too aggressive)
3. **Pause stream** when tab is hidden to save resources
4. **Clear feed periodically** to prevent memory growth
5. **Monitor event rate** via `connectionInfo.eventRate`

## Event Distribution

With 5 second interval:
- ~12 events/minute
- ~720 events/hour
- Buffer holds 500 events (last ~41 minutes at 5s interval)

With 10 second interval:
- ~6 events/minute
- ~360 events/hour
- Buffer holds 500 events (last ~83 minutes)

## Testing

```bash
# Start simulator
curl -X POST "http://localhost:8000/api/events/simulator/start?interval_seconds=5" \
  -H "Authorization: Bearer $TOKEN"

# Check status
curl "http://localhost:8000/api/events/simulator/status" \
  -H "Authorization: Bearer $TOKEN"

# Generate test event
curl -X POST "http://localhost:8000/api/events/simulator/generate" \
  -H "Authorization: Bearer $TOKEN"

# Check recent events
curl "http://localhost:8000/api/events/recent?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## Production Considerations

1. **In production**, replace simulator with real data sources (syslog, SNMP traps, etc.)
2. **Scale** using Redis pub/sub for multi-instance
3. **Persist** events to TimescaleDB or similar
3. **Add** alerting rules based on event patterns
4. **Monitor** simulator health via `/api/events/simulator/status`