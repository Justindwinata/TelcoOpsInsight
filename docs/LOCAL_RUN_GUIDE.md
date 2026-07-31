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
curl -X POST http://127.0.0.1:8000/api/datasets/seed
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The Vite dev server proxies `/api` and `/health` to the backend at `http://127.0.0.1:8000`.

## Tests And Build

```bash
cd backend
pytest -q

cd ../frontend
npm run build
npm test
```
