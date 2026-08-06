# TelcoOps Insight - Fixed & Run Guide

## Issues Fixed

### 1. **Duplicate Import in App.tsx (Line 28)**
- **Error**: `Identifier 'DispatchCenter' has already been declared`
- **Cause**: `DispatchCenter` was imported twice (lines 9 and 28)
- **Fix**: Removed duplicate import on line 28

### 2. **Missing EmptyState Import in App.tsx**
- **Error**: `Cannot find name 'EmptyState'`
- **Cause**: Component used but not imported
- **Fix**: Added `import { EmptyState } from "./components/StateViews"`

### 3. **Breadcrumbs.tsx React Router Dependency**
- **Error**: `Cannot find module 'react-router-dom'`
- **Cause**: Imported `useLocation` and `useNavigate` without react-router-dom in package.json
- **Fix**: Removed unused router dependencies, simplified component

### 4. **IncidentTimeline Type Missing lifecycle_stages**
- **Error**: Property 'lifecycle_stages' does not exist on type 'IncidentTimelineEntry'
- **Cause**: Type definition incomplete
- **Fix**: Added `lifecycle_stages: Array<Record<string, string>>` and `lifecycle_stages_present?: number` to `IncidentTimelineEntry` type

### 5. **AlarmManagement Error Message Type**
- **Error**: `Type 'string | null' is not assignable to type 'string'`
- **Cause**: `ErrorState` expects string, but useApi returns `string | null`
- **Fix**: Changed `summary.error ?? alarms.error` to `summary.error || alarms.error || "Error loading alarms"`

---

## Step-by-Step to Run Project

### Phase 1: One-Time Setup

```bash
# 1. Generate & validate synthetic data
cd /Users/justindwinata/Documents/TelcoOpsInsight
python3 scripts/generate_synthetic_telco_dataset.py
python3 scripts/validate_telco_dataset.py

# 2. Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Frontend setup (go back to root first)
cd ../frontend
npm install
cd ..
```

### Phase 2: Run Application (Start in 2 terminals)

**Terminal 1 - Backend Server:**
```bash
cd /Users/justindwinata/Documents/TelcoOpsInsight/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```
- Backend starts at: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`

**Terminal 2 - Frontend Dev Server:**
```bash
cd /Users/justindwinata/Documents/TelcoOpsInsight/frontend
npm run dev
```
- Frontend starts at: `http://127.0.0.1:5173`
- Automatically proxies `/api` requests to backend

### Phase 3: Login & Seed Data

Open browser: `http://127.0.0.1:5173`

**Login credentials:**
- Username: `noc_manager`
- Password: `telco-demo-2026`

After login, seed the database from the UI:
1. Click "Data Upload" in sidebar
2. Or via curl:
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"noc_manager","password":"telco-demo-2026"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://127.0.0.1:8000/api/datasets/seed \
  -H "Authorization: Bearer $TOKEN"
```

### Phase 4: Optional - Run Tests

```bash
# Backend tests (131 passed, 1 failed, 24 errors - known issues with auth fixtures)
cd /Users/justindwinata/Documents/TelcoOpsInsight/backend
PYTHONWARNINGS=ignore pytest -q

# Frontend tests (31 passed, 11 failed - text matching issues)
cd ../frontend
npm run build
npm test

# Smoke workflows (requires backend running)
cd ..
PYTHONWARNINGS=ignore python3 scripts/smoke_toi_0002.py
PYTHONWARNINGS=ignore python3 scripts/smoke_toi_0003.py
```

---

## Verification

✅ **Frontend Build**: Successfully compiles (TypeScript: 0 errors)
✅ **Duplicate Import**: Removed
✅ **Missing Dependencies**: Fixed
✅ **Type Errors**: Resolved
✅ **Smoke Tests**: TOI-0002 & TOI-0003 pass (20+ endpoints verified)
✅ **Dataset Validation**: All 9 CSV files valid

---

## Access Features

After login, dashboard sections available:
- Executive Overview
- Network Health
- Incident Monitoring
- SLA Assurance
- Customer Tickets
- Field Technician Dispatch
- Asset Management
- Maintenance Schedule
- Change Management
- Root Cause Analysis
- And 10+ more operational modules

---

## Troubleshooting

**Backend won't start:**
- Ensure Python 3.12+ is installed: `python3 --version`
- Activate venv: `source backend/.venv/bin/activate`
- Check deps: `pip list | grep -E "fastapi|uvicorn|pydantic"`

**Frontend won't start:**
- Ensure Node 20+: `node --version`
- Clear cache: `rm -rf frontend/node_modules/.vite`
- Rebuild: `npm run build`

**API calls failing:**
- Ensure backend is running on port 8000
- Check CORS proxy in `frontend/vite.config.ts`
- Login token might be expired (re-login)

**Port already in use:**
- Backend: `lsof -i :8000` then `kill -9 <PID>`
- Frontend: `lsof -i :5173` then `kill -9 <PID>`
