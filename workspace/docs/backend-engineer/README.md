# Fashion Tech Backend - Documentation Index

**Date:** 2026-03-17  
**Workspace:** `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/docs/backend-engineer/`  
**Status:** Phase 1 MVP (Foundation Design Complete)  

---

## 📋 Document Roadmap

### Core Architecture & Strategy

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** ⭐ START HERE
   - High-level system design
   - Technology stack (FastAPI, PostgreSQL, S3, Redis)
   - API response patterns
   - Performance targets
   - Scaling strategy
   - Data governance & privacy

2. **[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)**
   - 8-week Phase 1 timeline
   - Week-by-week deliverables
   - Project structure (code organization)
   - Docker & local dev setup
   - Technology dependencies
   - Success metrics & next phases

### Database & Data

3. **[schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md)**
   - Complete SQL schema (10 tables)
   - Relationships & constraints
   - Soft deletes & data retention
   - Indices for performance
   - Query patterns & optimization
   - Alembic migration strategy

### API Design

4. **[api/API_BLUEPRINT.md](api/API_BLUEPRINT.md)**
   - All Phase 1 endpoints (7 categories)
   - Request/response schemas
   - Authentication flow
   - Error codes & rate limiting
   - Versioning strategy
   - Example responses (complete)

### Security & Authentication

5. **[AUTHENTICATION.md](AUTHENTICATION.md)**
   - JWT token architecture
   - Password hashing (bcrypt)
   - Token generation & validation
   - FastAPI security dependencies
   - OAuth2 planning (Phase 2)
   - Audit logging
   - Best practices checklist

### Storage & Infrastructure

6. **[S3_STORAGE.md](S3_STORAGE.md)**
   - AWS S3 bucket structure
   - File organization & path conventions
   - Upload strategies (direct + multipart)
   - Download with signed URLs
   - Access control & bucket policies
   - Local MinIO setup for dev
   - Cost estimation & optimization
   - Monitoring & alerts

---

## 🎯 Quick Reference

### API Endpoints by Category

**Authentication** `/auth`
- `POST /auth/register` - Create account
- `POST /auth/login` - Authenticate
- `POST /auth/refresh` - Get new access token
- `POST /auth/logout` - Invalidate token

**User Profile** `/users`
- `GET /users/me` - Get current user
- `PATCH /users/me` - Update profile
- `PATCH /users/me/password` - Change password

**Body Scans** `/scans`
- `POST /scans/upload-initiate` - Start multipart upload
- `POST /scans/{scan_id}/complete` - Finish upload & process
- `GET /scans` - List user's scans
- `GET /scans/{scan_id}` - Get scan details
- `DELETE /scans/{scan_id}` - Delete scan

**Garment Catalogue** `/garments`
- `GET /garments` - Search & browse
- `GET /garments/{garment_id}` - Get details
- `GET /garments/categories` - Browse categories

**Outfits** `/outfits`
- `POST /outfits` - Create outfit
- `GET /outfits` - List user's outfits
- `GET /outfits/{outfit_id}` - Get outfit details
- `PATCH /outfits/{outfit_id}` - Update outfit
- `POST /outfits/{outfit_id}/items` - Add garment
- `DELETE /outfits/{outfit_id}/items/{item_id}` - Remove garment
- `DELETE /outfits/{outfit_id}` - Delete outfit

**Recommendations** `/recommendations`
- `POST /recommendations/fit` - Get size recommendations

**Health** `/health`
- `GET /health` - Liveness check
- `GET /health/ready` - Readiness check

---

## 📊 Database Tables

| Table | Purpose | Key Columns |
|-------|---------|------------|
| **users** | User accounts & profiles | email, password_hash, height_cm, gender |
| **scans** | 3D body scans | user_id, scan_file_key, rigged_file_key, status |
| **scan_measurements** | Body dimensions | scan_id, chest_cm, waist_cm, hips_cm, body_shape |
| **garments** | Clothing catalogue | sku, brand_name, model_file_key, price |
| **garment_sizes** | Size options & fit | garment_id, size_label, chest_cm_min/max, fabric_stretch |
| **garment_categories** | Browse taxonomy | name, slug, parent_id |
| **outfits** | Saved looks | user_id, scan_id, name, is_private |
| **outfit_items** | Garments in outfit | outfit_id, garment_id, size_id, display_order |
| **retail_partners** | Brand partnerships | name, api_endpoint, api_key |
| **saved_favourite_garments** | User bookmarks | user_id, garment_id |

---

## 🔐 Authentication Flow

```
1. POST /auth/register
   → Hash password (bcrypt)
   → Create user in DB
   → Return success

2. POST /auth/login
   → Verify credentials
   → Generate JWT tokens (access + refresh)
   → Store refresh token family (Phase 2)
   → Return tokens to client

3. Client stores:
   → access_token in memory
   → refresh_token in httpOnly cookie

4. Protected request:
   → Include: Authorization: Bearer <access_token>
   → FastAPI validates token signature & expiry
   → Extract user_id from token
   → Proceed if valid

5. POST /auth/refresh (when access token expires)
   → Validate refresh token
   → Generate new access token
   → Optionally rotate refresh token (Phase 2)
```

---

## 📁 Storage Structure

```
S3 Bucket: fashion-tech-storage/

scans/
  {user_id}/
    {scan_id}/
      scan_original.glTF       (raw from scanner)
      rigged.glTF              (after Blender pipeline)
      measurements.json        (body dimensions)
      thumbnail.jpg

garments/
  {brand_slug}/
    {sku}/
      model.fbx                (3D model)
      textures/
        diffuse.png
        normal.png
        roughness.png

outfits/
  {user_id}/
    {outfit_id}/
      preview_front.png        (rendered preview)
      preview_side.png
      preview_back.png

avatars/
  {user_id}.jpg                (user profile picture)
```

---

## 🚀 Deployment Checklist

### Week 1 (Development)
- [ ] Clone repo, set up local environment
- [ ] `docker-compose up` for PostgreSQL + MinIO
- [ ] Install dependencies: `poetry install`
- [ ] Run tests: `pytest`
- [ ] Start dev server: `uvicorn app.main:app --reload`
- [ ] Check API docs: `http://localhost:8000/docs`

### Week 8 (Production)
- [ ] AWS RDS PostgreSQL instance
- [ ] AWS S3 bucket with encryption + policies
- [ ] Application Load Balancer
- [ ] Kubernetes cluster (or Fly.io/Railway)
- [ ] GitHub Actions CI/CD pipeline
- [ ] CloudWatch monitoring + alarms
- [ ] Database backups + recovery tested
- [ ] Load test: 1,000 concurrent users
- [ ] Security audit: OWASP top 10

---

## 📈 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API response time | <200ms p95 | Excluding file uploads |
| Scan upload | 50MB in <10s | Multipart, parallel chunks |
| Garment search | <100ms (100k items) | Full-text indexed, cached |
| Outfit fetch | <50ms | Cached + in-memory |
| Concurrent users | 1,000 (MVP) → 10,000 (Phase 2) | Load balanced |
| Uptime | 99.5% (MVP) → 99.9% (Phase 2) | Monitoring, alerting, rollbacks |

---

## 🔗 Dependencies Between Teams

### What Backend Receives From Other Teams

| From Team | What | Format | Use Case |
|-----------|------|--------|----------|
| **3D Scanning Lead** | Raw body scans | glTF + metadata | Store in S3, queue for Blender pipeline |
| **Blender Lead** | Rigged, animated models | glTF exports | Store in S3, serve to frontend |
| **Clothing Lead** | Garment 3D models | FBX, CLO3D | Import into catalogue, store textures |
| **Frontend Engineer** | API calls | REST + JSON | Return outfit data, recommendations |

### What Backend Provides to Other Teams

| To Team | What | Format | Use Case |
|---------|------|--------|----------|
| **3D Scanning Lead** | Upload endpoint | `/scans/upload-initiate` | Upload raw scans |
| **Blender Lead** | Fetch & download | `/scans/{scan_id}` + signed URL | Download rigged scans |
| **Frontend Engineer** | All data APIs | REST + JSON | Render 3D viewer, outfit builder |

---

## 🎓 Knowledge Base

### For New Backend Team Members

1. **Start:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Understand:** Review [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md)
3. **Learn:** Study [api/API_BLUEPRINT.md](api/API_BLUEPRINT.md)
4. **Implement:** Follow [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) week by week
5. **Security:** Refresh on [AUTHENTICATION.md](AUTHENTICATION.md)
6. **Deploy:** Use [S3_STORAGE.md](S3_STORAGE.md) for file handling

### Common Questions

**Q: Why FastAPI instead of Django?**  
A: Async by default, lightweight, perfect for high-traffic APIs. See [ARCHITECTURE.md](ARCHITECTURE.md) rationale.

**Q: How do scans get rigged?**  
A: User uploads raw glTF → Backend queues job → Blender Lead processes → Backend stores rigged file. See [S3_STORAGE.md](S3_STORAGE.md#large-files---multipart-upload).

**Q: How do users authenticate?**  
A: Email/password → JWT token → stateless requests. See [AUTHENTICATION.md](AUTHENTICATION.md).

**Q: Can users delete their scans?**  
A: Yes, soft delete (30-day recovery window). See [schemas/DATABASE_SCHEMA.md](schemas/DATABASE_SCHEMA.md#soft-deletes).

---

## 📞 Support & Communication

### Architecture Review
- Owner: Backend Engineer (this role)
- Review cadence: End of Week 2, Week 4, Week 8
- Stakeholders: CEO, 3D Scanning Lead, Blender Lead, Frontend Engineer

### Integration Testing
- Test scans from 3D Scanning Lead: Week 2
- Test glTF imports from Blender Lead: Week 4
- Test with Frontend Engineer's viewer: Week 7

### Deployment Gate
- All tests passing: Required
- Load test results: Required
- Security audit: Required
- Team training complete: Required

---

## 📚 External Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **PostgreSQL Manual:** https://www.postgresql.org/docs/
- **AWS S3 Guide:** https://docs.aws.amazon.com/s3/
- **SQLAlchemy ORM:** https://docs.sqlalchemy.org/
- **JWT Best Practices:** https://tools.ietf.org/html/rfc7519
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

## 🔄 Next Steps

1. **This Sprint:** Share docs with team, discuss decisions, get buy-in
2. **Week 1:** Start implementation following [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
3. **Weekly:** Update progress in daily standup
4. **Week 2:** First integration checkpoint with other teams
5. **Week 8:** Launch preparation & team training

---

**Document Version:** 1.0  
**Created:** 2026-03-17  
**Last Updated:** 2026-03-17  
**Status:** Ready for Implementation  

**👤 Backend Engineer Signature:**  
This document represents foundational work for Phase 1 MVP. All major architectural decisions, schema designs, API blueprints, and security strategies are documented. Implementation begins Week 1.
