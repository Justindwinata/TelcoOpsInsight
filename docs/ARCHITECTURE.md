# Architecture

## Overview

TelcoOps Insight follows a service-oriented architecture with clear separation between presentation, business logic, and data layers.

## Layers

### Frontend (Presentation)
- React + TypeScript
- Vite for build tooling
- Recharts for data visualization
- Component-based architecture
- State management via React Context

### Backend (API)
- FastAPI framework
- RESTful API design
- JWT authentication
- Role-based access control
- Service-oriented business logic

### Data (Storage)
- SQLite database
- WAL mode for concurrent access
- Indexed queries for performance
- Synthetic seed data for demo

## Service Architecture

### Analytics Services
All analytics services follow the pattern:
```
def analytics_function(filters):
    rows = apply_filters(fetch(table), filters)
    # aggregation logic
    return computed_metrics
```

### Cache Layer
- In-memory cache with TTL
- Read-heavy analytics endpoints cached
- Cache invalidation on data changes
- Stats endpoint for monitoring

### Auth Layer
- JWT-based stateless auth
- Demo user with fixed credentials
- Permission-based access control
- Token expiration handling

## API Design

### Conventions
- Plural resource names: `/api/alarms`
- RESTful verbs: GET, POST, PUT, DELETE
- Consistent error responses
- Filter parameters in query string

### Response Format
```json
{
  "data": {...},
  "metadata": {...},
  "timestamp": "..."
}
```

## Component Architecture (Frontend)

```
App
├── NotificationProvider
│   └── ErrorBoundary
│       ├── OfflineDetector
│       ├── SkipLink
│       └── AuthProvider
│           └── FilterProvider
│               └── AppContent
│                   ├── Sidebar
│                   ├── Topbar
│                   ├── FilterPanel
│                   ├── CommandPalette
│                   ├── PerformanceMonitor
│                   └── PageRenderer
└── (Page Components)
```

## Data Flow

1. User interacts with UI component
2. Component calls API endpoint via `apiGet`/`apiPost`
3. API route validates input and auth
4. Service layer processes request
5. Cache checked, fallback to database
6. Response returned with metadata
7. UI component updates with data

## Error Handling

### Backend
- Validation via Pydantic models
- HTTPException for known errors
- Global error handlers for unexpected errors
- Logging for debugging

### Frontend
- Error boundary catches React errors
- Toast notifications for user feedback
- Retry mechanism for transient failures
- Offline detection for network issues

## Performance Optimizations

### Backend
- Connection pooling
- Query optimization with indexes
- Response caching layer
- Pagination for large datasets

### Frontend
- React.memo for expensive components
- useMemo for computed values
- Code splitting (future)
- Virtual scrolling for tables (future)
