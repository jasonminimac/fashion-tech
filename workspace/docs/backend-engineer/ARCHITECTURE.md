# Fashion Tech Backend - Technical Architecture

**Date:** 2026-03-17  
**Author:** Backend Engineer  
**Status:** MVP Phase 1 (Foundational Design)  
**Target Deployment:** Weeks 1-8  

---

## Overview

The Fashion Tech backend provides the core infrastructure for user management, 3D scan storage, garment catalogue management, and outfit persistence. It serves as the central hub connecting:

- **3D Scanning Pipeline** → Receives rigged body models (glTF exports from Blender Lead)
- **Mobile/Web Clients** → User authentication, scan uploads, outfit management
- **Garment Catalogue** → B2B onboarding, metadata, sizing, retail linking
- **Frontend Viewer** → API for 3D assets, outfit data, recommendations

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                             │
│  iOS App    │   Web Browser    │   Desktop Viewer               │
└──────┬──────────────┬────────────────┬─────────────────────────┘
       │              │                │
       └──────────────┼────────────────┘
                      │
       ┌──────────────▼──────────────┐
       │   FastAPI Backend (Async)   │
       │   - REST API endpoints      │
       │   - WebSocket (live updates)│
       │   - Rate limiting + caching │
       └──────────────┬──────────────┘
       ┌──────────────┴────────────────┐
       │                               │
  ┌────▼────────┐          ┌──────────▼──────────┐
  │ PostgreSQL  │          │ AWS S3 / Cloud      │
  │ Database    │          │ Storage             │
  │ (Users,     │          │ - Scans (glTF)      │
  │  Scans,     │          │ - Garments (FBX)    │
  │  Outfits,   │          │ - Textures (PNG/JPG)│
  │  Garments)  │          │ - Signed URLs       │
  └─────────────┘          └─────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│            EXTERNAL INTEGRATIONS (Phase 1 & 2)                   │
│  - Blender Integration Lead (glTF imports)                        │
│  - 3D Scanning Lead (scan uploads)                                │
│  - Clothing Lead (garment onboarding)                             │
│  - Retail Partners (product links, SSO)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend Framework
- **FastAPI** (Python 3.11+)
  - Async by default (uvicorn ASGI server)
  - Type hints & automatic OpenAPI documentation
  - Built-in validation (Pydantic)
  - Easy testing with `TestClient`

### Database
- **PostgreSQL 14+**
  - JSONB for flexible metadata
  - Full-text search for garment catalogue
  - Vector types (pgvector) for future ML recommendations
  - Scalable to millions of scans + outfits

### Object Storage
- **AWS S3** (or MinIO for local dev)
  - Signed URLs (secure, time-limited access)
  - Lifecycle policies (archive old scans)
  - Cross-region replication (failover)

### Authentication
- **OAuth2 (JWT tokens)** with password grant for MVP
  - Email/password registration
  - Optional: Google, Apple, Facebook SSO (Phase 2)
  - Refresh tokens for long-lived sessions

### Caching & Performance
- **Redis** (Phase 2, optional for MVP)
  - Cache garment catalogue metadata
  - Session management
  - Rate limiting

### Deployment
- **Docker** containers (reproducible environments)
- **Kubernetes** or **Railway/Fly.io** (scalable hosting)
- **CI/CD** via GitHub Actions (test + deploy)

---

## Core Design Principles

### 1. **RESTful by Default, WebSocket for Real-Time**
   - Static data (garments, user profiles) → REST HTTP
   - Real-time updates (outfit editor, recommendations) → WebSocket (Phase 2)

### 2. **Async Throughout**
   - FastAPI with async handlers
   - Background tasks for long-running ops (scan processing, garment import)
   - Non-blocking database queries (asyncpg driver)

### 3. **Separation of Concerns**
   - **Routers:** Endpoints organized by domain (users, scans, outfits, garments)
   - **Services:** Business logic (auth, scan validation, fitting algorithms)
   - **Models:** Database schemas (SQLAlchemy ORM)
   - **Schemas:** Request/response DTOs (Pydantic)

### 4. **Error Handling & Observability**
   - Structured logging (JSON format, Datadog/ELK integration)
   - Detailed HTTP error responses (4xx, 5xx)
   - Health checks (database, S3, cache connectivity)
   - Distributed tracing (OpenTelemetry, Phase 2)

### 5. **Security First**
   - HTTPS everywhere (enforce in production)
   - Input validation (Pydantic + FastAPI)
   - SQL injection prevention (SQLAlchemy parameterized queries)
   - Rate limiting (per user, per IP)
   - CORS configuration (allow only trusted domains)
   - Secrets management (environment variables, vault)

---

## API Response Patterns

### Success Response (200 OK)
```json
{
  "success": true,
  "data": { /* resource data */ },
  "meta": { "timestamp": "2026-03-17T13:44:00Z" }
}
```

### Error Response (4xx/5xx)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid scan file format",
    "details": [{"field": "file", "issue": "Expected glTF, got FBX"}]
  },
  "meta": { "timestamp": "2026-03-17T13:44:00Z", "request_id": "uuid" }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [/* items */],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 1234,
    "total_pages": 25
  }
}
```

---

## Performance Targets (Phase 1)

| Metric | Target | Notes |
|--------|--------|-------|
| **API Response Time** | <200ms p95 | Excluding file uploads; cached responses <50ms |
| **Scan Upload** | 50MB in <10s | Parallel multipart uploads to S3 |
| **Garment Search** | <100ms (100k items) | Full-text indexed, cached pagination |
| **Outfit Fetch** | <50ms | Cached + in-memory for frequent users |
| **Concurrent Users** | 1,000 (MVP) → 10,000 (Phase 2) | Load balancer + multiple API instances |
| **Uptime** | 99.5% (MVP) → 99.9% (Phase 2) | Monitoring, alerting, automated rollbacks |

---

## Scaling Strategy

### Phase 1 (MVP): Single Instance
- One FastAPI server + PostgreSQL + S3
- Redis optional (add if cache miss rate >20%)
- Monitoring via application logs

### Phase 2: Horizontal Scaling
- Load balancer (nginx, AWS ALB) → multiple FastAPI instances
- Database read replicas for high-traffic queries
- Redis for session + cache layer
- CDN for static assets (garment thumbnails, textures)

### Phase 3: Microservices (if needed)
- Separate service for recommendations (ML inference)
- Background job worker (scan processing, email notifications)
- Separate read database (optimized for analytics)

---

## Data Governance

### Data Categories

1. **User Data** (PII)
   - Email, password hash, profile (name, age, size preferences)
   - Encrypted at rest, access logs audited
   - GDPR compliance: right to delete, export, portability

2. **Scan Data** (Large Binary)
   - 3D mesh files (glTF), textures, rigged models
   - 50-200MB per scan
   - User-owned; can delete; archived after 1 year (configurable)

3. **Garment Data** (B2B)
   - Manufacturer-provided 3D models, metadata
   - Fits parameters (size scaling, stretch ranges)
   - Publicly available in catalogue (metadata only; full models with auth)

4. **Outfit Data** (User-generated)
   - Saved outfit combinations (garment IDs + body scan reference)
   - Optional: sharing settings (private, friends, public)

### Privacy & Compliance
- Body scans are encrypted in transit (HTTPS + TLS)
- At-rest encryption via S3 encryption + database encryption
- User controls: privacy settings, data retention, export
- Compliance: GDPR (EU), CCPA (US), data residency options

---

## Key Decisions

### Decision 1: Why FastAPI?
- **Async by default** → handles many concurrent requests without threads
- **Type safety** → Pydantic validates request/response shapes
- **Auto-generated docs** → `/docs` endpoint is free
- **Performance** → near-C speeds (uvicorn + async I/O)
- **Learning curve** → smaller than Django for new team members

### Decision 2: Why PostgreSQL + S3?
- **Metadata in PostgreSQL:** User profiles, garments, outfits (relational)
- **Binary files in S3:** Scans, garments (large, replicated, cheap storage)
- **Separation:** DB for queries, object store for durability + cost efficiency
- **Not a single database:** Could use MongoDB or cloud-specific DBs, but PostgreSQL + S3 is industry standard for this pattern

### Decision 3: JWT Tokens (Stateless)
- **No session table needed** → scales horizontally
- **Refresh token rotation** → security without database lookups
- **Standard adoption** → easy to add OAuth2 providers later
- **Trade-off:** Can't immediately revoke tokens (mitigate with short TTL + blacklist)

### Decision 4: Async + Background Tasks
- **Blocking I/O is slow:** File uploads, S3 operations, database queries
- **FastAPI + asyncio** → native support for async/await
- **Background jobs:** Celery + Redis for long-running tasks (scan processing, emails) in Phase 2

---

## Monitoring & Observability

### Logging
- Structured JSON logs to stdout
- Integration: Datadog, CloudWatch, or ELK stack
- Log levels: DEBUG (dev), INFO (prod), ERROR (alerts)

### Metrics
- API response times (histogram)
- Request counts by endpoint (counter)
- Database connection pool usage (gauge)
- S3 upload/download speed (histogram)
- Error rates (counter)

### Health Checks
- `GET /health` → quick liveness check
- `GET /health/ready` → deep readiness check (DB, S3 connectivity)
- Automated alerts if service is down

### Tracing
- Request IDs (correlation across logs)
- OpenTelemetry (Phase 2) for distributed tracing across services

---

## Next Steps

1. **Database Schema Design** (this sprint)
   - User, scan, outfit, garment tables
   - Relationships, constraints, indexes

2. **API Endpoints Blueprint** (this sprint)
   - List of all Phase 1 endpoints
   - Request/response shapes
   - Authentication requirements

3. **Authentication Implementation** (Week 1)
   - JWT token generation/validation
   - Password hashing (bcrypt)
   - User registration endpoint

4. **Storage Integration** (Week 1-2)
   - S3 configuration (local MinIO for dev, AWS S3 for staging/prod)
   - Signed URL generation for secure file access
   - Multipart upload handling

5. **Garment Catalogue API** (Week 2-3)
   - List, search, filter endpoints
   - Metadata schema (category, size, price, retail link)
   - B2B onboarding workflow (admin panel for intake)

---

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- AWS S3 Best Practices: https://docs.aws.amazon.com/s3/latest/userguide/
- OAuth2 + JWT: https://oauth.net/2/
- Twelve-Factor App: https://12factor.net/

---

**Status:** Ready for Database Schema Design  
**Next Review:** After Week 1 implementation
