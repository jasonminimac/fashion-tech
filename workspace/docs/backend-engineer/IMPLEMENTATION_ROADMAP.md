# Backend Implementation Roadmap & Project Structure

**Date:** 2026-03-17  
**Version:** 1.0  
**Timeline:** 8 weeks (Phase 1 MVP)  

---

## Project Structure

### Repository Layout

```
fashion-tech-backend/
├── pyproject.toml                  # Poetry dependencies
├── Dockerfile                      # Container image
├── docker-compose.yml              # Local dev environment
├── .env.example                    # Environment variables template
├── pytest.ini                      # Testing config
├── .github/
│   └── workflows/
│       ├── test.yml               # Run tests on push
│       ├── lint.yml               # Code quality checks
│       └── deploy.yml             # Deploy to production
│
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                # FastAPI app initialization
│       ├── config.py              # Settings (Pydantic)
│       ├── dependencies.py        # Shared dependencies (auth, DB)
│       │
│       ├── routers/               # API route handlers
│       │   ├── __init__.py
│       │   ├── auth.py            # /auth endpoints
│       │   ├── users.py           # /users endpoints
│       │   ├── scans.py           # /scans endpoints
│       │   ├── garments.py        # /garments endpoints
│       │   ├── outfits.py         # /outfits endpoints
│       │   ├── recommendations.py # /recommendations endpoints
│       │   └── health.py          # /health endpoints
│       │
│       ├── models/                # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── scan.py
│       │   ├── garment.py
│       │   ├── outfit.py
│       │   └── auth_audit.py
│       │
│       ├── schemas/               # Pydantic request/response schemas
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── auth.py
│       │   ├── scan.py
│       │   ├── garment.py
│       │   └── outfit.py
│       │
│       ├── services/              # Business logic
│       │   ├── __init__.py
│       │   ├── auth_service.py    # Password hashing, JWT tokens
│       │   ├── scan_service.py    # Scan upload/processing logic
│       │   ├── s3_service.py      # S3 operations (upload, download, signed URLs)
│       │   ├── garment_service.py # Garment catalogue logic
│       │   └── recommendation_service.py
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── session.py         # SQLAlchemy session factory
│       │   ├── base.py            # Base model, declarative_base
│       │   └── migrations/        # Alembic migration scripts
│       │       ├── env.py
│       │       ├── script.py.mako
│       │       └── versions/
│       │           ├── 001_initial.py
│       │           └── ...
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logger.py          # Structured logging
│       │   ├── validators.py      # Custom Pydantic validators
│       │   ├── errors.py          # Custom exception classes
│       │   └── security.py        # Security utilities
│       │
│       └── middleware/            # Custom middleware
│           ├── __init__.py
│           ├── security_headers.py
│           └── request_logging.py
│
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_auth.py              # Auth endpoint tests
│   ├── test_users.py             # User endpoint tests
│   ├── test_scans.py             # Scan endpoint tests
│   ├── test_garments.py          # Garment endpoint tests
│   ├── test_outfits.py           # Outfit endpoint tests
│   ├── integration/
│   │   ├── test_auth_flow.py     # Full auth flow tests
│   │   ├── test_scan_upload.py   # Full scan upload tests
│   │   └── test_outfit_builder.py
│   └── unit/
│       ├── test_services.py      # Service unit tests
│       └── test_validators.py    # Validator unit tests
│
├── migrations/                   # Database migrations (Alembic)
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_indices.py
│       └── ...
│
└── docs/
    ├── SETUP.md                 # Local dev setup guide
    ├── API.md                   # API documentation (auto-generated)
    ├── DATABASE.md              # Database schema reference
    └── DEPLOYMENT.md            # Production deployment guide
```

---

## Phase 1 Timeline (8 Weeks)

### Week 1: Foundation & Auth
**Goal:** Set up project structure, database, and authentication  
**Deliverables:**
- [ ] FastAPI project scaffold + Docker setup
- [ ] PostgreSQL connection + SQLAlchemy ORM
- [ ] User model + schema
- [ ] Auth service (password hashing, JWT tokens)
- [ ] `/auth/register`, `/auth/login`, `/auth/refresh` endpoints
- [ ] Auth tests (unit + integration)
- [ ] `GET /users/me` endpoint

**Tasks:**
1. Create FastAPI app with proper structure
2. Set up PostgreSQL locally (Docker)
3. Write User SQLAlchemy model
4. Implement password hashing (bcrypt)
5. Implement JWT token generation/validation
6. Write auth endpoints (register, login, refresh)
7. Add pytest fixtures and write tests
8. Document API in `/docs`

**Estimation:** 40 hours

---

### Week 2: Database Schema & Scans
**Goal:** Complete database schema, implement scan upload pipeline  
**Deliverables:**
- [ ] All SQLAlchemy models (Scan, Garment, Outfit, etc.)
- [ ] Alembic migrations
- [ ] S3 integration (boto3)
- [ ] Signed URL generation
- [ ] Scan upload endpoints (multipart)
- [ ] Scan listing/retrieval endpoints
- [ ] Integration with 3D Scanning Lead (glTF input spec)

**Tasks:**
1. Write remaining SQLAlchemy models
2. Create Alembic migrations
3. Set up S3 client (AWS or MinIO)
4. Implement multipart upload logic
5. Implement signed URL generation
6. Write scan routers
7. Integration tests for upload flow
8. API documentation

**Estimation:** 45 hours

---

### Week 3: Garment Catalogue
**Goal:** Build garment database and API, design B2B onboarding  
**Deliverables:**
- [ ] Garment + GarmentSize models
- [ ] Garment catalogue endpoints (list, search, filter)
- [ ] Category browsing
- [ ] B2B garment upload flow (admin panel)
- [ ] Size recommendation algorithm (basic)
- [ ] Tests

**Tasks:**
1. Implement garment routers (GET, POST for admin)
2. Add full-text search (PostgreSQL)
3. Implement filtering (category, brand, price, color)
4. Add pagination
5. Design B2B intake (manual + API, Phase 2)
6. Size recommendation service
7. Tests and documentation

**Estimation:** 40 hours

---

### Week 4: Outfits & Saving
**Goal:** Implement outfit creation, saving, and management  
**Deliverables:**
- [ ] Outfit + OutfitItem models
- [ ] Create/update/delete outfit endpoints
- [ ] Add/remove garment from outfit
- [ ] Outfit listing + retrieval
- [ ] Basic outfit preview (metadata only, no rendering yet)

**Tasks:**
1. Implement outfit routers
2. Add display_order logic (layering)
3. Support outfit metadata (occasion, season, color palette)
4. Implement outfit copying/sharing (basic, Phase 2)
5. Tests and documentation

**Estimation:** 30 hours

---

### Week 5: S3 & Storage Integration
**Goal:** Complete S3 integration, signed URL service, storage monitoring  
**Deliverables:**
- [ ] Avatar upload/download
- [ ] Scan file storage (upload + retrieval)
- [ ] Garment model + texture storage
- [ ] Outfit preview storage
- [ ] Signed URL service with expiration
- [ ] Lifecycle policies (archive after 1 year)
- [ ] Storage monitoring + cost tracking

**Tasks:**
1. Implement avatar upload endpoints
2. Complete scan upload integration
3. Implement S3 cleanup service (old scans, failed uploads)
4. Add CloudWatch metrics (Phase 2)
5. Document S3 structure
6. Load test: upload large files

**Estimation:** 35 hours

---

### Week 6: Testing & Polish
**Goal:** Comprehensive testing, documentation, bug fixes  
**Deliverables:**
- [ ] Unit tests for all services (>80% coverage)
- [ ] Integration tests for full flows (auth, scan, outfit)
- [ ] Load testing (1,000 concurrent users)
- [ ] Security audit (OWASP top 10)
- [ ] Documentation (setup, API, deployment)
- [ ] Performance optimization

**Tasks:**
1. Write comprehensive test suite
2. Load test with locust/k6
3. Security review (rate limiting, CORS, headers)
4. Code review + cleanup
5. Performance profiling
6. API documentation review
7. Deployment guide

**Estimation:** 40 hours

---

### Week 7: Integration with Other Teams
**Goal:** Test integration with 3D Scanning, Blender, Frontend leads  
**Deliverables:**
- [ ] Documented glTF import format (from Blender Lead)
- [ ] Scan upload format spec (from 3D Scanning Lead)
- [ ] Garment model format spec (from Clothing Lead)
- [ ] API integration tests with mock data
- [ ] Sample data + test fixtures

**Tasks:**
1. Coordinate with Blender Lead on glTF export format
2. Coordinate with 3D Scanning Lead on scan input format
3. Prepare sample garment data
4. Write integration tests using mocked dependencies
5. Test API with Frontend Engineer's 3D viewer
6. Iterate on any issues

**Estimation:** 30 hours

---

### Week 8: Launch Prep & Deployment
**Goal:** Final polish, deployment to staging, team training  
**Deliverables:**
- [ ] Staging environment set up (AWS)
- [ ] Database backups + recovery tested
- [ ] Monitoring + alerting configured
- [ ] Team documentation + training
- [ ] Launch checklist completed

**Tasks:**
1. Set up production AWS infrastructure (RDS, S3, ALB, Kubernetes)
2. Configure CI/CD pipeline
3. Deploy to staging environment
4. Final smoke tests
5. Team documentation + training session
6. On-call runbook
7. Post-launch monitoring plan

**Estimation:** 35 hours

---

## Technology Stack (Dependencies)

### Core
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {version = "^0.24.0", extras = ["standard"]}
sqlalchemy = "^2.0.0"
asyncpg = "^0.28.0"        # Async PostgreSQL driver
psycopg2-binary = "^2.9.0" # Sync driver (migrations)
alembic = "^1.13.0"        # Database migrations
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# Authentication & Security
python-jose = {version = "^3.3.0", extras = ["cryptography"]}
passlib = {version = "^1.7.4", extras = ["bcrypt"]}
python-multipart = "^0.0.6"  # For form data

# AWS
boto3 = "^1.28.0"
botocore = "^1.31.0"

# Logging & Monitoring
python-json-logger = "^2.0.0"

# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
httpx = "^0.25.0"          # Async HTTP client for testing

# Linting & Formatting
black = "^23.0.0"
ruff = "^0.1.0"
mypy = "^1.7.0"
```

---

## Environment Variables

```bash
# .env.example
ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fashion_tech_db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
AWS_S3_BUCKET=fashion-tech-storage
AWS_S3_ENDPOINT_URL=http://localhost:9000  # MinIO for dev

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

---

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Copy source code
COPY src ./src
COPY migrations ./migrations

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.9'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@postgres:5432/fashion_tech_db
      AWS_S3_ENDPOINT_URL: http://minio:9000
    depends_on:
      - postgres
      - minio

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: fashion_tech_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"

volumes:
  postgres_data:
  minio_data:
```

---

## Key Decisions & Trade-offs

| Decision | Trade-off | Rationale |
|----------|-----------|-----------|
| **FastAPI over Django** | Less batteries-included | Async, lightweight, perfect for APIs |
| **PostgreSQL over MongoDB** | Less flexible schema | Relational data fits better, JSONB for flexibility |
| **JWT over sessions** | Can't revoke immediately | Scales horizontally, simpler deployment |
| **S3 over DB blobs** | Two-system complexity | Cheaper, scalable, industry standard |
| **Alembic migrations** | Extra tooling | Version-controlled schema changes |
| **Multipart uploads** | More complexity | Resume capability, better for large files |

---

## Success Metrics (EOW 8)

- ✅ All MVP endpoints implemented and tested
- ✅ <200ms API response times (p95)
- ✅ >80% test coverage
- ✅ Full API documentation (`/docs`)
- ✅ Database schema versioned and migrated
- ✅ S3 integration working (dev + staging)
- ✅ Integration tests passing with other teams' mocks
- ✅ Team trained on codebase and deployment

---

## Next Phases

### Phase 2 (Weeks 9-16)
- OAuth2 SSO (Google, Apple, Facebook)
- Redis caching
- Recommendation engine (ML-based)
- Background job workers (Celery)
- WebSocket for real-time updates
- Analytics tracking

### Phase 3 (Weeks 17+)
- Mobile app backend APIs
- Subscription/billing (Stripe integration)
- Social features (outfit sharing, trends)
- Advanced recommendation engine
- Microservices architecture

---

## References

- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://www.sqlalchemy.org/
- **Pydantic:** https://docs.pydantic.dev/
- **Alembic:** https://alembic.sqlalchemy.org/
- **AWS S3:** https://docs.aws.amazon.com/s3/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Pytest:** https://docs.pytest.org/

---

**Status:** Ready for Development  
**Last Updated:** 2026-03-17  
**Next Review:** After Week 1 completion
