
## TOI-0011

### Added
- Real-Time Network Operations via SSE (Server-Sent Events)
- Backend event service (publish/subscribe, in-memory buffer, SQLite persistence)
- Network event simulator (15 event types, configurable interval)
- SSE streaming endpoint with heartbeat & auto-reconnect
- Simulator control endpoints (start/stop/interval/generate)
- Auto incident escalation engine (rule-based)
- Live status aggregation (regional, KPI, SLA, operators)
- Event history export (CSV, JSON, HTML)
- Frontend SSE client hook (useEventStream)
- Live notification center hook (auto-toast on critical/major)
- Live event feed, stream control, refresh indicator
- Live regional status, KPI, SLA, operator monitoring components
- Live Events page & Real-Time NOC command center page
- Backend + frontend tests (6 backend, 48 frontend passing)

### Fixed
- Frontend TypeScript errors in CommandPalette, HealthChecker, OfflineDetector, RefreshIndicator
- Test failures requiring FilterProvider wrapper
- Dashboard load text matching
