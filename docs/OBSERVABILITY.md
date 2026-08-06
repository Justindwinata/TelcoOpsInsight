# Observability Guide

## Health Monitoring

### Health Check Endpoint
- `GET /api/health` - Basic health status
- `GET /api/noc/command-center` - Comprehensive health dashboard

### System Health Page
- Real-time backend status
- API latency tracking
- Database connection status
- Dataset information

### Metrics Tracked
- API response times
- Database query duration
- Cache hit/miss ratio
- Active connections

## Logging

### Error Handling
- Client-side error boundaries
- Retry mechanism for transient failures
- Offline detection with notification
- Graceful degradation

### Notifications
- Toast notifications for all user actions
- Success, error, warning, info levels
- Auto-dismiss with option to manually dismiss

## Alerts

### Automatic Alerts
- Network offline detection
- Backend connection errors
- API rate limiting warnings
- Health check failures

## Metrics Dashboard

Use the System Health page to monitor:
- Backend health
- Database status
- Cache statistics
- Performance metrics
