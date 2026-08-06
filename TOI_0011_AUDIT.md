# TOI-0011 Audit: Real-Time Network Operations & Event Streaming

## Architecture Decision: SSE (Server-Sent Events)

### Why SSE over WebSocket

| Factor | SSE | WebSocket |
|--------|-----|-----------|
| Direction | Server → Client (one-way) | Bidirectional |
| Complexity | Low (native EventSource) | Medium (ws library needed) |
| Reconnection | Automatic with Retry header | Manual reconnection |
| HTTP/2 support | Yes | Optional |
| Dashboard fit | Perfect (server pushes events) | Overkill for read-only dashboards |
| Browser support | All modern browsers | All modern browsers |

**Decision: SSE** — Server pushes events to dashboard clients. Client doesn't need to send events back except via regular REST endpoints (acknowledge, assign, etc.).

## Event Flow

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│ Event Simulator │────▶│ Event Service│────▶│ SSE Stream   │───▶ Clients
│ (Timer-based)   │     │ (Publisher)  │     │ (FastAPI)    │
└─────────────────┘     └──────────────┘     └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ Event Store  │
                       │ (In-memory + │
                       │  SQLite)     │
                       └──────────────┘
```

## Components

### Backend
1. **Event Service** (`event_service.py`) — Core event store, publisher, subscriber
2. **Event Simulator** (`event_simulator.py`) — Generates synthetic network events
3. **SSE Route** (`events.py`) — Server-Sent Events endpoint
4. **Live Endpoints** — Snapshot endpoints for current state

### Frontend
1. **EventSource Client** — Connects to SSE stream
2. **Live Feed Components** — Real-time incident/alarm/KPI displays
3. **Stream Control** — Pause/resume/clear
4. **Notification System** — Toast notifications on new events

## Event Types

1. `link_down` — Network link failure
2. `link_up` — Link recovery
3. `high_latency` — Latency threshold exceeded
4. `packet_loss` — Packet loss detected
5. `fiber_cut` — Physical fiber damage
6. `device_offline` — Device unreachable
7. `device_recovery` — Device back online
8. `power_failure` — Power outage at site
9. `maintenance_started` — Scheduled maintenance begins
10. `maintenance_completed` — Maintenance done

## State Management

### Backend
- In-memory event buffer (last 500 events)
- SQLite persistence for audit trail
- Event counters and aggregates

### Frontend
- React state for live feeds
- localStorage for stream preferences
- EventSource for SSE connection
- useRef for performance optimization

## Refresh Mechanism

### SSE Stream
- Persistent connection
- Events pushed immediately
- Automatic reconnection (3s retry)
- Heartbeat every 30s

### REST Snapshots
- Full state refresh every 30s (fallback)
- Individual resource refresh on demand
- Manual refresh button

## Testing Strategy

### Backend
- SSE endpoint returns event stream
- Simulator generates events at configurable rate
- Event acknowledge works
- Event history export works

### Frontend
- EventSource connects and receives events
- Live feeds update without page refresh
- Stream control (pause/resume) works
- Notifications appear on new events
- No excessive re-renders

## Limitations

1. SSE is one-way (server → client); use REST for client → server actions
2. Single-server only (no Redis pub/sub for multi-instance)
3. In-memory event buffer (no external message queue)
4. Simulator generates synthetic events only
5. No persistent WebSocket fallback for old browsers
