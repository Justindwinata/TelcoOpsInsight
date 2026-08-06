# Performance Guide

## Backend Optimization

### Query Optimization
- Composite indexes on high-cardinality fields
- Pre-aggregated analytics where possible
- Connection pooling with SQLite WAL mode
- Caching layer with 5-minute TTL

### Response Caching
- `GET /api/cache/stats` - View cache statistics
- `POST /api/cache/invalidate` - Clear cache by pattern
- `POST /api/cache/clear` - Clear all cache

### Analytics Services
- All analytics services use `rows()` which implements caching
- Filter-aware analytics reduce redundant computations

## Frontend Optimization

### React Optimization
- React.memo on heavy components
- useMemo for expensive calculations
- useCallback for event handlers
- Virtual scrolling for large tables (future enhancement)

### Chart Rendering
- Recharts with data decimation for >1000 points
- Lazy chart loading on viewport
- Animated transitions disabled for large datasets

### Network Optimization
- API request retry mechanism (3 attempts)
- Offline detection with notification
- Debounced search inputs

## Performance Targets

- Page load < 2s
- API response < 300ms
- Chart render < 500ms
- No layout shifts

## Monitoring

Use `SystemHealth` page to monitor:
- Backend status
- API latency
- Database connection
- Cache hit rate

See `PerformanceMonitor` component for runtime metrics.
