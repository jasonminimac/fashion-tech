# Local Development Setup

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Poetry | 1.8+ | `pip install poetry` |
| Docker Desktop | Latest | [docker.com](https://docker.com) |
| PostgreSQL | 15+ | via Docker (below) |

---

## 1. Clone & install

```bash
git clone https://github.com/your-org/fashion-tech.git
cd fashion-tech/backend

# Install all dependencies (including dev)
poetry install

# Activate the virtual environment
poetry shell
```

---

## 2. Environment configuration

```bash
cp .env.example .env.local
```

Edit `.env.local` — at minimum set:

```dotenv
DATABASE_URL=postgresql+asyncpg://developer:dev_password_123@localhost:5432/fashion_tech_dev
JWT_SECRET_KEY=<generate a secure random string>
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET=fashion-tech-storage
ENVIRONMENT=development
DEBUG=true
```

---

## 3. Start infrastructure (Docker)

```bash
docker compose up -d   # starts PostgreSQL + MinIO
```

Verify:
- PostgreSQL: `psql postgresql://developer:dev_password_123@localhost:5432/fashion_tech_dev`
- MinIO console: http://localhost:9001 (minioadmin / minioadmin123)

---

## 4. Run database migrations

```bash
./scripts/migrate.sh
# or: alembic upgrade head
```

---

## 5. Start the API server

```bash
./scripts/run.sh
# or: uvicorn app.main:app --reload
```

The API is now at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## 6. Run tests

```bash
./scripts/test.sh
# or: pytest tests/ --asyncio-mode=auto -v
```

Make sure a test database exists:

```bash
createdb fashion_tech_test  # one-time
```

Or via Docker: the `test.yml` workflow handles this automatically in CI.

---

## Code quality tools

```bash
# Lint
flake8 src/ --max-line-length=100

# Format (in-place)
black src/ --line-length=100

# Type check
mypy src/ --ignore-missing-imports
```

---

## Useful Make targets (optional)

If you add a `Makefile`:

```bash
make dev         # start server with reload
make test        # run test suite
make lint        # flake8 + black + mypy
make migrate     # alembic upgrade head
make docker-up   # docker compose up -d
```
