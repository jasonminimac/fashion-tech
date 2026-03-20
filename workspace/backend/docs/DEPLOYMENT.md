# Deployment Guide

## Docker (recommended)

### Build the image

```bash
cd backend/
docker build -t fashion-tech-backend:latest .
```

### Run locally

```bash
docker run -d \
  --name fashion-tech-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="<secure-random>" \
  -e AWS_ACCESS_KEY_ID="..." \
  -e AWS_SECRET_ACCESS_KEY="..." \
  -e S3_BUCKET="fashion-tech-storage" \
  -e ENVIRONMENT="production" \
  fashion-tech-backend:latest
```

### Verify health

```bash
curl http://localhost:8000/health
# → {"status":"ok","version":"0.1.0","environment":"production"}
```

---

## Docker Compose (full stack)

```bash
docker compose up -d
```

Services started:
- `api` — FastAPI on port 8000
- `postgres` — PostgreSQL 15 on port 5432
- `minio` — S3-compatible storage on port 9000

---

## Production checklist

- [ ] `JWT_SECRET_KEY` is a cryptographically random 32+ byte value
- [ ] `DEBUG=false`, `ENVIRONMENT=production`
- [ ] `CORS_ORIGINS` restricted to your frontend domain(s)
- [ ] Database uses SSL (`?sslmode=require`)
- [ ] Secrets managed via environment variables or a secrets manager (not `.env` files)
- [ ] Non-root user in Docker image ✅ (already configured)
- [ ] Health check configured ✅
- [ ] HTTPS termination at load balancer / reverse proxy
- [ ] Container registry credentials set in GitHub Actions secrets

---

## CI/CD via GitHub Actions

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `lint.yml` | Every push | flake8, black, mypy |
| `test.yml` | Every PR | pytest with live PostgreSQL |
| `deploy.yml` | Push to `main` or version tag | Build + push Docker image |

### Required GitHub secrets (for deploy):
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`

### Required GitHub variables:
- `REGISTRY` — e.g. `ghcr.io/your-org`

---

## Running migrations in production

```bash
# Via Docker exec
docker exec fashion-tech-api alembic upgrade head

# Via script
./scripts/migrate.sh
```

Always run migrations **before** deploying new application code.

---

## Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL DSN (asyncpg) |
| `JWT_SECRET_KEY` | ✅ | — | Token signing secret |
| `AWS_ACCESS_KEY_ID` | ✅ | — | S3 / MinIO key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | — | S3 / MinIO secret |
| `S3_BUCKET` | ✅ | `fashion-tech-storage` | Storage bucket name |
| `S3_ENDPOINT_URL` | | `None` (use AWS) | Override for MinIO |
| `ENVIRONMENT` | | `development` | `development`/`test`/`production` |
| `DEBUG` | | `false` | Enable debug mode |
| `CORS_ORIGINS` | | `localhost:3000,5173` | Comma-separated origins |
| `LOG_LEVEL` | | `INFO` | Python log level |
| `PORT` | | `8000` | Server port (scripts/run.sh) |
| `WORKERS` | | `1` | Uvicorn worker count (production) |
