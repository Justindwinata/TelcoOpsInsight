# Deployment Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- SQLite 3

## Backend Deployment

### Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Initialization
```bash
# Seed database
python -c "from app.services.dataset_service import seed_sample_dataset; seed_sample_dataset()"
```

## Frontend Deployment

### Development
```bash
cd frontend
npm install
npm run dev
```

### Production Build
```bash
npm install
npm run build
# Output in dist/
```

### Serve with Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /var/www/telcoops/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./telco_ops.db
CORS_ORIGINS=http://localhost:5173
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
TOKEN_EXPIRY=24h
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Docker Deployment

### Dockerfile (Backend)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Frontend)
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## Database Backup

```bash
# Backup
sqlite3 telco_ops.db ".backup '/path/to/backup.db'"

# Restore
cp /path/to/backup.db telco_ops.db
```

## Monitoring

### Health Checks
- `GET /api/health` - Liveness probe
- `GET /api/cache/stats` - Cache health
- `GET /api/noc/command-center` - System health

### Logging
- Backend logs to stdout
- Use external log aggregation
- Log retention policy: 30 days

## Scaling Considerations

### Horizontal Scaling
- Backend is stateless - can run multiple instances
- Use external database (PostgreSQL) for multi-instance
- Cache layer per instance (or external Redis)

### Vertical Scaling
- Increase CPU/RAM based on analytics workload
- Database optimization critical
- Connection pooling

## Security

### SSL/TLS
- Use HTTPS in production
- Configure reverse proxy (Nginx/Caddy)
- Update CORS origins

### Authentication
- JWT tokens with expiration
- Secure secret key management
- Rate limiting (recommended)

### Data Protection
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS prevention (React's built-in)

## Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok",
  "service": "TelcoOps Insight API",
  "company": "NusaTel Digital Network",
  "synthetic_data_only": true
}
```
