# Local Run Guide

## Generate And Validate Data

```bash
python3 scripts/generate_synthetic_telco_dataset.py
python3 scripts/validate_telco_dataset.py
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

Seed SQLite:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"noc_manager","password":"telco-demo-2026"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://127.0.0.1:8000/api/datasets/seed \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The Vite dev server proxies `/api` and `/health` to the backend at `http://127.0.0.1:8000`.

Use demo username `noc_manager` and demo password `telco-demo-2026` for full prototype access.

## Tests And Build

```bash
cd backend
pytest -q

cd ../frontend
npm run build
npm test

cd ..
python3 scripts/smoke_toi_0002.py
```
