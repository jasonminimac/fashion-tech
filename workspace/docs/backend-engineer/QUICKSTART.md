# Backend Quick-Start Guide

**For:** First developer joining the team  
**Read Time:** 15 minutes  
**Next:** Follow [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) Week 1

---

## TL;DR

Fashion Tech Backend is a FastAPI server that:
- Manages user accounts (email/password auth with JWT tokens)
- Stores 3D body scans on AWS S3 (100-200MB files)
- Maintains a garment catalogue (5-50MB model files)
- Lets users save outfits (combinations of garments on their body scans)
- Recommends sizes based on body measurements

**Stack:** FastAPI + PostgreSQL + AWS S3 + Pydantic  
**Timeline:** 8 weeks to MVP  
**Endpoints:** 25+ RESTful APIs (documented at `/docs`)  

---

## The Mental Model

```
User                Frontend (React)      Backend (FastAPI)         Database           S3 Storage
 │                      │                     │                       │                   │
 ├─ scans body ────────→ │                     │                       │                   │
 │                       │                     │                       │                   │
 │                       ├─ POST /scans/upload─→ Multipart handler    │                   │
 │                       │                     │                       │                   │
 │                       │                     ├─ Get presigned URLs   │                   │
 │                       │                     │◄─────────────────────────────────────────│
 │                       │◄─ Return URLs ──────┤                       │                   │
 │                       │                     │                       │                   │
 │                       ├─ Upload to S3 directly (parts)              │◄──────────────────┤
 │                       │                     │                       │         (store file)
 │                       │                     │                       │                   │
 │                       ├─ POST /scans/complete                        │                   │
 │                       │                     │                       │                   │
 │                       │                     ├─ Queue Blender job                       │
 │                       │                     ├─ Update DB: "processing"                  │
 │                       │                     │                       │                   │
 │ [Blender pipeline]    │                     │ ← triggers background job                │
 │ ├─ Load glTF from S3  │                     │                       │                   │
 │ ├─ Rig + animate      │                     │                       │                   │
 │ ├─ Export rigged glTF │                     │                       │                   │
 │ └─ Upload to S3       │                     │                       │                   │
 │                       │                     ├─ Mark DB: "completed"                     │
 │                       │                     │                       │                   │
 │                       ├─ GET /scans ────────→ Query DB              │                   │
 │                       │◄──────────────────── List recent scans      │                   │
 │                       │                     │                       │                   │
 │  picks outfit         │                     │                       │                   │
 │  (dress + shoes)      ├─ POST /outfits ────→ Create outfit          │                   │
 │                       │  /items: [...]      │                       │                   │
 │                       │                     ├─ Insert into DB                          │
 │                       │◄─────────────────── Return outfit_id        │                   │
 │                       │                     │                       │                   │
 │  clicks "Download"    ├─ GET /outfits/{id}─→ Join garments table   │                   │
 │                       │                     │                       │                   │
 │                       │                     ├─ Get signed URLs      │                   │
 │                       │                     │ for 3D models         │                   │
 │                       │◄───────────────────── Return outfit data    │                   │
 │                       │                     │                       │                   │
 │                       ├─ Fetch models from S3 with signed URLs ────────────────────────→
 │                       │                     │                       │                   │
 │ [3D Viewer opens]     │                     │                       │                   │
 │ ├─ Display body       │                     │                       │                   │
 │ ├─ Layer garments     │                     │                       │                   │
 │ ├─ Play animation     │                     │                       │                   │
 └─ Done ✓              │                     │                       │                   │
```

---

## Key Concepts

### 1. Authentication
- User registers with email + password
- Password hashed with bcrypt (never stored in plain text)
- Login returns JWT tokens (access + refresh)
- Subsequent requests include access token in `Authorization: Bearer <token>` header
- See [AUTHENTICATION.md](AUTHENTICATION.md) for details

### 2. Scans
- Users upload 3D body scans (glTF files, 50-200MB)
- Uploaded to S3 via presigned URLs (client uploads directly, backend verifies)
- Backend queues Blender pipeline to rig the model
- Rigged model stored in S3
- Frontend downloads via signed URLs (time-limited, secure access)

### 3. Garments
- Manufacturers submit 3D models (FBX, 5-50MB) and textures (PNGs)
- Admin imports into catalogue with metadata (size ranges, price, brand)
- Users browse/search catalogue via API
- Garments stored in S3, served to frontend

### 4. Outfits
- User selects body scan + garment combination
- Backend creates "outfit" record linking scan + garments
- Outfit stored in DB with metadata (occasion, season)
- User can save multiple outfits, each tied to a specific scan

### 5. Size Recommendations
- When user views garment, backend calculates recommended size
- Based on user's body measurements (from scan) vs. garment size ranges
- Simple algorithm in Phase 1 (improved with ML in Phase 2)

---

## File Organization

```
backend/
├── README.md ..................... you are here
├── ARCHITECTURE.md ............... system design (read first)
├── AUTHENTICATION.md ............. JWT + security
├── S3_STORAGE.md ................. file storage details
├── IMPLEMENTATION_ROADMAP.md ..... week-by-week plan
│
├── api/
│   └── API_BLUEPRINT.md .......... all endpoints (reference)
│
└── schemas/
    └── DATABASE_SCHEMA.md ........ tables + fields (reference)
```

**Starting point:** Read docs in this order:
1. [ARCHITECTURE.md](ARCHITECTURE.md) (30 min)
2. [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) (20 min)
3. [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md) (20 min)
4. [api/API_BLUEPRINT.md](api/API_BLUEPRINT.md) (reference, don't memorize)

---

## Core API Endpoints (Cheat Sheet)

### Authentication
```
POST /auth/register               Create account
POST /auth/login                  Get tokens
POST /auth/refresh                Refresh access token
```

### Scans
```
POST /scans/upload-initiate       Start upload (get presigned URLs)
POST /scans/{scan_id}/complete    Finish upload, queue processing
GET  /scans                       List my scans
GET  /scans/{scan_id}             Get scan details + download URLs
DELETE /scans/{scan_id}           Delete scan
```

### Garments
```
GET  /garments                    Search garments
GET  /garments/{garment_id}       Get garment details
GET  /garments/categories         Browse categories
```

### Outfits
```
POST   /outfits                   Create outfit
GET    /outfits                   List my outfits
GET    /outfits/{outfit_id}       Get outfit details
PATCH  /outfits/{outfit_id}       Update outfit
POST   /outfits/{outfit_id}/items Add garment to outfit
DELETE /outfits/{outfit_id}       Delete outfit
```

**See [api/API_BLUEPRINT.md](api/API_BLUEPRINT.md) for full details + examples.**

---

## Database Tables at a Glance

| Table | Stores | Key Fields |
|-------|--------|-----------|
| **users** | Accounts | email, password_hash, height, gender |
| **scans** | 3D body files | user_id, s3_file_path, status |
| **garments** | Clothing models | brand, sku, s3_model_path, price |
| **garment_sizes** | Size options | garment_id, size_label, chest_min/max |
| **outfits** | Saved looks | user_id, scan_id, name |
| **outfit_items** | Garments in outfit | outfit_id, garment_id, size |

**See [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md) for complete schema.**

---

## S3 Storage Structure

```
S3 Bucket
├── scans/{user_id}/{scan_id}/
│   ├── scan_original.glTF       ← User uploads
│   ├── rigged.glTF              ← Blender pipeline outputs
│   └── thumbnail.jpg
│
├── garments/{brand}/{sku}/
│   ├── model.fbx                ← Admin uploads
│   └── textures/*.png           ← Admin uploads
│
└── avatars/{user_id}.jpg        ← User uploads
```

**See [S3_STORAGE.md](S3_STORAGE.md) for details on uploads, downloads, security.**

---

## Week 1 Checklist (Your First Week)

- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Read [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
- [ ] Clone backend repo (git clone ...)
- [ ] Run `docker-compose up` (starts PostgreSQL + MinIO)
- [ ] Run `poetry install` (install Python dependencies)
- [ ] Run `pytest` (should pass)
- [ ] Start dev server: `uvicorn app.main:app --reload`
- [ ] Open http://localhost:8000/docs (API docs)
- [ ] Try `/auth/register` endpoint
- [ ] Try `/auth/login` endpoint
- [ ] Ask questions in Slack if stuck

**Deliverable:** First auth endpoint working locally

---

## Common First Tasks

### Task 1: Understand Auth Flow
1. Open [AUTHENTICATION.md](AUTHENTICATION.md)
2. Find the "JWT Token Structure" section
3. Trace a token from generation → validation
4. Run `/auth/login` endpoint, inspect the JWT at jwt.io

### Task 2: Understand Database
1. Open [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md)
2. Read the "tables" section
3. Look at the relationships diagram
4. Connect to local PostgreSQL: `psql -U user -d fashion_tech_db`
5. Run `\dt` to list tables, `\d users` to view schema

### Task 3: Make an API Call
1. Register a user: `POST /auth/register`
2. Save the access_token from response
3. Call `GET /users/me` with `Authorization: Bearer <token>`
4. Should return your user data

### Task 4: Upload a Scan (Simulation)
1. Generate a dummy 10MB file: `dd if=/dev/zero of=test_scan.glTF bs=1M count=10`
2. Call `POST /scans/upload-initiate`
3. Receive presigned URLs
4. (In real scenario: upload chunks via URLs)
5. Call `POST /scans/{scan_id}/complete`
6. Verify scan appears in DB

---

## Troubleshooting

**"Can't connect to PostgreSQL"**
- Run `docker-compose up`
- Check Docker is running: `docker ps`
- Verify connection: `psql -U user -h localhost -d fashion_tech_db`

**"Import errors in Python"**
- Run `poetry install`
- Activate venv: `poetry shell`
- Check Python version: `python --version` (should be 3.11+)

**"API won't start"**
- Check port 8000 is free: `lsof -i :8000`
- Check env vars: `echo $DATABASE_URL`
- Run in debug mode: `uvicorn app.main:app --reload --log-level debug`

**"Tests fail"**
- Run single test: `pytest tests/test_auth.py::test_register`
- Check DB migrated: `alembic upgrade head`
- Check fixtures: `pytest --fixtures`

---

## Glossary

| Term | Meaning |
|------|---------|
| **FastAPI** | Python web framework for building APIs (async, fast) |
| **JWT** | JSON Web Token (stateless authentication token) |
| **Signed URL** | Time-limited S3 URL (user can download without AWS credentials) |
| **Multipart Upload** | Upload large file in chunks (resume-able) |
| **Alembic** | Database migration tool (version control for schema changes) |
| **ORM** | Object-Relational Mapping (SQLAlchemy makes DB rows into Python objects) |
| **Pydantic** | Schema validation (ensures request/response data shape) |
| **S3** | AWS Simple Storage Service (file storage) |
| **glTF** | GL Transmission Format (3D model file, what Blender outputs) |
| **FBX** | Autodesk format (3D model file, industry standard) |

---

## Getting Help

**Stuck on implementation?**
- Check [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) week-by-week breakdown
- Find your task, read the details

**Need API endpoint details?**
- Check [api/API_BLUEPRINT.md](api/API_BLUEPRINT.md)
- Copy example request/response

**Database schema questions?**
- Check [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md)
- Look at table definitions, constraints, indices

**Security/Auth questions?**
- Check [AUTHENTICATION.md](AUTHENTICATION.md)

**File storage questions?**
- Check [S3_STORAGE.md](S3_STORAGE.md)

**Architecture decisions?**
- Check [ARCHITECTURE.md](ARCHITECTURE.md) "Key Decisions" section

---

## Next Steps

1. **Now:** Read [ARCHITECTURE.md](ARCHITECTURE.md) (takes 30 min)
2. **Then:** Follow Week 1 checklist above (takes 2 hours)
3. **Then:** Start with [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) Week 1 tasks
4. **Daily:** Standup with team on progress
5. **End of Week 1:** First endpoints working, tests passing

---

**Questions?** Reach out to the Backend Engineer or post in #fashion-tech-backend Slack channel.

**Good luck! 🚀**

---

**Last Updated:** 2026-03-17
