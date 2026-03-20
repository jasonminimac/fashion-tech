# Fashion Tech Backend — Week 1 Implementation

## Quick Start

### Local Development Setup

```bash
cd fashion-tech-backend

# Copy environment variables
cp .env.example .env.local

# Install dependencies (requires Poetry: https://python-poetry.org/docs/#installation)
poetry install

# Start PostgreSQL + MinIO
docker-compose up -d

# Run database migrations (Week 2)
# alembic upgrade head

# Start FastAPI server
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Database

PostgreSQL runs on `localhost:5432`
- Username: `developer`
- Password: `dev_password_123`
- Database: `fashion_tech_dev`

Connect with:
```bash
psql postgresql://developer:dev_password_123@localhost:5432/fashion_tech_dev
```

### S3 / MinIO

MinIO (S3-compatible) runs on `http://localhost:9000`
Console at `http://localhost:9001`
- Username: `minioadmin`
- Password: `minioadmin123`

### Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=src tests/

# Specific test file
poetry run pytest tests/test_auth.py -v
```

## Project Structure

```
src/app/
├── main.py              # FastAPI app entry point
├── config.py            # Settings from environment
├── dependencies.py      # Shared dependencies (JWT, DB)
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── routers/             # API endpoint handlers
├── services/            # Business logic (S3, auth, etc.)
├── database/            # Database engine + migrations
└── utils/               # Security, validators, helpers
```

## API Endpoints (Week 1)

### Authentication
- `POST /v1/auth/register` — Register new user
- `POST /v1/auth/login` — Authenticate user
- `POST /v1/auth/logout` — Logout user

### Users
- `GET /v1/users/me` — Get current user profile

### Scans
- `POST /v1/scans/upload-initiate` — Start multipart upload
- `GET /v1/scans` — List user's scans
- `GET /v1/scans/{scan_id}` — Get scan details
- `DELETE /v1/scans/{scan_id}` — Soft-delete scan

### Garments
- `GET /v1/garments` — Search garments
- `GET /v1/garments/categories` — List categories
- `GET /v1/garments/{garment_id}` — Get garment details

### Outfits
- `POST /v1/outfits` — Create outfit
- `GET /v1/outfits` — List user's outfits
- `GET /v1/outfits/{outfit_id}` — Get outfit details
- `DELETE /v1/outfits/{outfit_id}` — Delete outfit

### Health
- `GET /health` — Liveness check
- `GET /health/ready` — Readiness check

## Key Models

| Model | Purpose |
|-------|---------|
| User | User account with auth & profile |
| Scan | 3D body scan metadata |
| ScanMeasurement | Body measurements from scan |
| Garment | Clothing item in catalogue |
| GarmentSize | Size variant with fit data |
| GarmentCategory | Garment taxonomy |
| Outfit | Saved outfit (body + garments) |
| OutfitItem | Individual garment in outfit |

## Week 1 Status

- ✅ FastAPI project scaffold
- ✅ SQLAlchemy models (User, Scan, Garment, Outfit)
- ✅ API endpoint stubs (auth, users, scans, garments, outfits, health)
- ✅ JWT authentication (register, login)
- ✅ S3 service integration
- ✅ Docker setup (PostgreSQL + MinIO)
- ⏳ Alembic migrations (Week 2)
- ⏳ Endpoint implementations (Week 2)
- ⏳ Tests (Week 2)

## Week 2 Tasks

1. Create Alembic migrations for all models
2. Implement scan upload endpoints (multipart)
3. Implement garment search with filtering
4. Implement outfit CRUD operations
5. Add comprehensive error handling
6. Write unit + integration tests
7. Performance optimization (pagination, caching)

## Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9
```

### PostgreSQL connection failed
```bash
# Check if Docker container is running
docker-compose ps

# Restart services
docker-compose restart postgres
```

### S3 upload errors
```bash
# Check MinIO console
http://localhost:9001

# Verify credentials in .env.local match docker-compose.yml
```

## Notes

- All passwords are automatically hashed with bcrypt (12 rounds)
- JWT tokens expire after 1 hour (configurable in .env.local)
- Soft deletes preserve data for GDPR compliance
- S3 integration supports both AWS and MinIO (local dev)

---

**Status:** Week 1 Scaffolding Complete
**Next Review:** End of Week 1 (2026-03-24)
