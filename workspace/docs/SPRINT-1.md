# SPRINT-1.md — Week 1 Kickoff (Mar 18-22, 2026)

**Sprint:** Week 1 MVP Foundation  
**Status:** 🟢 **APPROVED** — All 5 teams GREEN, no blockers  
**Duration:** Mar 18-22, 2026 (5 business days)  
**Standup:** Daily 10:00 AM GMT (sync-first culture)  
**Review:** Friday 16:00 GMT with CEO (all teams present)  
**Escalation Rule:** Any blocker >2h → CEO immediately (no delays)

---

## 📊 Sprint Snapshot

| Team | Role | Lead | Tasks | Status | Dependencies | Deliverable |
|------|------|------|-------|--------|--------------|-------------|
| **Scanning** | iOS LiDAR Capture | 3D Scanning Engineer | 5 | 🟢 GREEN | None | `/workspace/docs/scanning/WEEK1_IMPLEMENTATION.md` |
| **Rigging** | Blender Automation | Blender Lead | 8 | 🟢 GREEN | Blender 3.6, MediaPipe | `/workspace/docs/rigging/WEEK1_IMPLEMENTATION.md` |
| **Garments** | Garment Pipeline & Outreach | Garments Lead | 6 | 🟢 GREEN | Partner responses (async) | `/workspace/docs/garments/WEEK1_IMPLEMENTATION.md` |
| **Platform** | Backend + Frontend | Platform Engineer | 12 | 🟢 GREEN | PostgreSQL, S3 bucket | `/workspace/docs/platform/WEEK1_IMPLEMENTATION.md` |
| **AR** | ARKit Implementation | AR Lead | 4 | 🟢 GREEN | iPhone 12 Pro+ for testing | `/workspace/docs/ar/WEEK1_IMPLEMENTATION.md` |

---

## 🎯 Sprint Goals (MVP Foundation)

By **Friday EOD (Mar 22)**:

1. ✅ **iOS body capture working** — LiDAR scan → PLY file, 30fps streaming
2. ✅ **Rigging pipeline ready** — Python scripts for Blender automation (Rigify + MediaPipe)
3. ✅ **Garment pipeline initialized** — Partner outreach materials sent; 5 sample garments defined
4. ✅ **Backend + Frontend skeleton live** — FastAPI + React projects bootstrapped, 3D viewer rendering
5. ✅ **AR foundation set** — ARKit body tracking, garment anchoring proof-of-concept
6. ✅ **CI/CD pipeline running** — Tests passing, deployments automated

**Non-goal:** Ship finished product. Ship *working infrastructure* that unblocks Weeks 2-8.

---

## 📋 Detailed Task Breakdown by Team

### 1️⃣ SCANNING LEAD (3D Scanning Engineer)
**Docs:** `/workspace/docs/scanning/WEEK1_IMPLEMENTATION.md`

**5-Day Schedule:**

| Day | Task | Deliverable | Owner |
|-----|------|-------------|-------|
| **Mon** | iOS project setup (Xcode template) | `ARKitCapture` Xcode project | Scanning Lead |
| **Tue** | ARKit LiDAR integration + depth capture | Swift code: `ARKitDepthCapture.swift` (30fps) | Scanning Lead |
| **Wed** | Point cloud export (PLY) + local storage | `PointCloudWriter.swift` + test data | Scanning Lead |
| **Thu** | Python pipeline env setup (Open3D) | Environment config + skeleton scripts | Scanning Lead |
| **Fri** | Testing + documentation | 5-day schedule complete, test data ready | Scanning Lead |

**Key Metrics:**
- ✅ 30fps depth streaming from iPhone LiDAR
- ✅ Point cloud accuracy: <10mm error
- ✅ Pipeline latency: <2s per frame
- ✅ No external blockers

**Dependencies:**
- Xcode 15+
- iPhone 12 Pro+ with LiDAR (testing device)
- S3 bucket (setup by Platform team, **Week 2** use)

---

### 2️⃣ RIGGING LEAD (Blender & Animation Engineer)
**Docs:** `/workspace/docs/rigging/WEEK1_IMPLEMENTATION.md`  
**Test Framework:** `/workspace/docs/rigging/WEEK1_TEST_FRAMEWORK.md`

**3-Day Execution (Mon-Wed), 2-Day Testing + Docs (Thu-Fri):**

| Day | Task | Deliverable | Owner |
|-----|------|-------------|-------|
| **Mon** | Rigify + MediaPipe environment setup | `requirements.txt`, Blender 3.6 config | Rigging Lead |
| **Tue** | Python modules (4: import, skeleton, weight paint, export) | 500 lines of production Python | Rigging Lead |
| **Wed** | Mesh import pipeline implementation | Blender script: automated mesh → rigged skeleton | Rigging Lead |
| **Thu** | Test framework execution (18 test cases) | 80%+ code coverage achieved | Rigging Lead |
| **Fri** | Documentation + CI/CD setup | README + GitHub Actions workflow | Rigging Lead |

**Key Deliverables:**
- 4 Python modules (~500 lines, tested)
- 18 test cases (unit + integration + performance)
- <500ms mesh import time
- GitHub Actions CI/CD working

**Success Criteria:**
- ✅ All 18 tests passing
- ✅ 80%+ code coverage
- ✅ Zero linting errors
- ✅ <500ms FBX import (typical 245ms)

**Dependencies:**
- Blender 3.6+ (free)
- Python 3.9+
- MediaPipe (pip install)

---

### 3️⃣ GARMENTS LEAD (Garment & Cloth Simulation Engineer)
**Docs:** `/workspace/docs/garments/WEEK1_IMPLEMENTATION.md`  
**Partner Outreach:** `/workspace/docs/garments/PARTNER_OUTREACH_STRATEGY.md`

**5-Day Split: Mon-Tue Outreach, Wed-Fri Technical:**

| Day | Task | Deliverable | Owner |
|-----|------|-------------|-------|
| **Mon** | Zara/H&M discovery call prep | Call script (15+ Q's), email templates x5 | Garments Lead |
| **Tue** | Outreach + initial partner contact | Emails sent; discovery calls scheduled | Garments Lead |
| **Wed** | CLO3D integration architecture | 9-step pipeline spec + Python import skeleton | Garments Lead |
| **Thu** | Garment database schema design | PostgreSQL schema (4 tables, Alembic migrations) | Garments Lead |
| **Fri** | MVP garment specs + fitting pipeline | 5 sample garments (shirt, dress, jeans, t-shirt, blazer) | Garments Lead |

**Partner Outreach Materials Ready (send Monday AM):**
- ✅ 5 email templates (discovery, submission, validation, contingency x2)
- ✅ CLO3D maturity assessment framework (3-level rubric)
- ✅ 30-45 min call script
- ✅ Garment intake checklist
- ✅ SLA proposal (4-week pilot)

**Technical Deliverables:**
- ✅ PostgreSQL schema (garments, garment_sizes, garment_partners, validation_log tables)
- ✅ Fabric physics lookup table (7 fabrics × 9 parameters)
- ✅ CLO3D import pipeline (draft architecture)
- ✅ 5 MVP garment specs (structured, draped, stretch categories)

**Dependencies:**
- Partner responses (async; no blocker for Week 1 tech work)
- CLO3D license (TBD if partners have it; fallback: photogrammetry)

---

### 4️⃣ PLATFORM LEAD (Backend + Frontend Engineer)
**Docs:** `/workspace/docs/platform/WEEK1_IMPLEMENTATION.md`  
**Tech Stack:** FastAPI (backend) + React + Three.js (frontend)

**Parallel Work (Mon-Fri):**

| Day | Backend Task | Frontend Task | DevOps Task |
|-----|--------------|---------------|------------|
| **Mon** | FastAPI scaffold + models | React + Vite setup | Docker dev env |
| **Tue** | Auth (JWT/bcrypt) + 10 endpoints | 3D Viewer component | S3 integration |
| **Wed** | User/Scan/Garment endpoints | Outfit Builder UI stub | CI/CD pipeline setup |
| **Thu** | Retailer API skeleton | State management (Zustand) | GitHub Actions config |
| **Fri** | Docs + integration testing | Component testing | Full stack test |

**Backend Deliverables:**
- ✅ FastAPI project scaffold (complete folder structure)
- ✅ 5 SQLAlchemy ORM models (User, Scan, Garment, Outfit, RetailerAPIAccess)
- ✅ 25+ API endpoints with full code examples
- ✅ PostgreSQL schema (10 tables + Alembic migrations)
- ✅ JWT auth + bcrypt password hashing
- ✅ S3 integration service

**Frontend Deliverables:**
- ✅ React + Vite + TypeScript project
- ✅ Three.js SceneManager class (150+ lines)
- ✅ Viewport3D component (3D rendering)
- ✅ Outfit Builder UI (5 components with wireframes)
- ✅ Zustand store (state management)
- ✅ API client (axios + TypeScript)

**DevOps Deliverables:**
- ✅ Docker Compose (local dev + production)
- ✅ S3 bucket configuration
- ✅ GitHub Actions CI/CD workflows
- ✅ Environment variables template

**Success Criteria:**
- ✅ FastAPI server running on `localhost:8000` with `/docs` working
- ✅ React dev server running on `localhost:3000`
- ✅ 3D viewer renders at 60fps
- ✅ All tests passing
- ✅ CI/CD pipeline deployed

**Dependencies:**
- PostgreSQL (local Docker instance)
- S3 bucket (AWS setup)
- Docker + Docker Compose

**Estimated Effort:** ~19 engineer-days (plan for 2-3 engineers or staggered timeline)

---

### 5️⃣ AR LEAD (iOS ARKit Specialist)
**Docs:** `/workspace/docs/ar/WEEK1_IMPLEMENTATION.md`

**5-Day Schedule:**

| Day | Task | Deliverable | Owner |
|-----|------|-------------|-------|
| **Mon** | ARKit + RealityKit project scaffold | Xcode project (13 core modules) | AR Lead |
| **Tue** | Body tracking integration (ARKit Body Tracking API) | `BodyTracker.swift` (real-time skeleton) | AR Lead |
| **Wed** | Garment anchoring POC | `GarmentAnchor.swift` (joint-based positioning) | AR Lead |
| **Thu** | Occlusion handling + performance profiling | Occlusion detection with hand/arm tests | AR Lead |
| **Fri** | Week 6 quality gate checklist + fallback plan | Go/no-go metrics defined (24fps, <200ms lag) | AR Lead |

**Key Deliverables:**
- ✅ Xcode project with 13 core modules
- ✅ ARKit body tracking (real-time skeleton detection)
- ✅ USDZ garment model rendering
- ✅ Occlusion handling (arms/body collision)
- ✅ Week 6 quality gate checklist (formal go/no-go criteria)
- ✅ 8 Swift code scaffolds (runnable examples)

**Week 6 Go/No-Go Metrics:**
- Frame rate: ≥24fps sustained (p95: ≥20fps)
- Tracking lag: <200ms (p95)
- Occlusion accuracy: ≥85% correct pixels
- Stability: <0.1% crash rate
- Device support: ≥iPhone 12 Pro (A14+)

**If AR fails quality bar:** Graceful fallback to high-quality 3D viewer (Three.js web component)

**Dependencies:**
- Xcode 15+
- iPhone 12 Pro+ (testing device)
- RealityKit framework (built-in)

---

## 🔗 Cross-Team Dependencies

```
┌─────────────────────────────────────────┐
│         SPRINT DEPENDENCIES             │
└─────────────────────────────────────────┘

Scanning → Rigging → Platform (Backend)
    ↓        ↓            ↓
  LiDAR   Blender      FastAPI
  .obj    Rigify       Models
   ↓        ↓            ↓
   ├────────┴────────────┤
   │                     │
Platform (Frontend) ← Platform (Backend)
   ↓
React + Three.js
   3D Viewer

AR ← Rigging (export targets: USDZ)
     Platform (garment/user API)
```

**Critical Path (longest chains):**
1. Scanning (Day 1-5) → Rigging (Day 1-3) → Platform (Day 1-5) → AR (Day 4-5)
2. Garments (Monday outreach) → Partner response (async) → Week 2+ integration

**Parallel Workstreams:**
- **Scanning + Rigging** (data capture & processing)
- **Platform + AR** (UI + mobile interface)
- **Garments** (partner outreach, independent timeline)

---

## 📈 Success Metrics (Friday Review)

**By End of Day Friday (Mar 22):**

| Team | Success Metric | Status |
|------|----------------|--------|
| **Scanning** | iOS LiDAR capture at 30fps ✅ | TBD |
| **Rigging** | 18/18 tests passing, 80%+ coverage | TBD |
| **Garments** | Partner outreach sent, CLO3D pipeline drafted | TBD |
| **Platform** | Both servers running, 3D viewer at 60fps, CI/CD working | TBD |
| **AR** | ARKit body tracking + garment anchoring POC | TBD |

**Global MVP Foundation Goal:**
- ✅ End-to-end pipeline sketched (capture → process → render)
- ✅ All infrastructure (backend, frontend, AR, tooling) bootstrapped
- ✅ Zero critical blockers for Week 2+
- ✅ Team communication + escalation protocols proven

---

## 🚨 Escalation Protocol

**Blocker Definition:** Any issue blocking >2 hours of work for 1+ team members

**Escalation Path:**
1. Team lead → CEO (immediate message, no delays)
2. CEO triages (remote help, resource reallocation, etc.)
3. If unresolvable: Pivot task, document decision in `decisions/`

**Examples of >2h blockers:**
- External API/service down (AWS, GitHub, etc.)
- Hardware issue (LiDAR device failure, etc.)
- Major library incompatibility
- Unexpected dependency conflict

**Examples of handled locally (<2h):**
- Code bug or missing edge case → debug/fix
- Documentation unclear → ask in Slack
- Small design adjustment → make decision locally

---

## 📅 Weekly Cadence

**Daily (10:00 AM GMT):**
- Standup: 3-5 min per team, blockers only

**Wednesday (14:00 GMT):**
- Mid-sprint sync: progress check, dependency resolution

**Friday (16:00 GMT):**
- Sprint review: all teams present, demo, metrics, next sprint planning

**Friday (17:00 GMT EOD):**
- Status report to Founder (CEO sends 3-line summary + key blockers)

---

## 📁 Artifact Location

All team docs live in `/workspace/docs/`:

```
/workspace/docs/
├── SPRINT-1.md (← this file)
├── DISCOVERY.md (strategy)
├── scanning/WEEK1_IMPLEMENTATION.md
├── rigging/WEEK1_IMPLEMENTATION.md
├── garments/WEEK1_IMPLEMENTATION.md
├── garments/PARTNER_OUTREACH_STRATEGY.md
├── platform/WEEK1_IMPLEMENTATION.md
└── ar/WEEK1_IMPLEMENTATION.md
```

---

## 🎬 Next Steps

**Monday 09:00 AM GMT (Start of Sprint):**
1. CEO sends sprint board to all 5 team leads
2. Each lead reads their own WEEK1_IMPLEMENTATION.md (30 min)
3. Garments Lead sends partner outreach emails (Zara/H&M)
4. All teams begin their Day 1 tasks

**Ongoing:**
- Daily 10:00 AM standup
- Escalate >2h blockers immediately
- Track progress in team-specific status files

**Friday 16:00 GMT:**
- All teams demo their Week 1 output
- CEO reviews metrics
- Plan Week 2 sprint

---

**Sprint Status:** 🟢 **READY TO LAUNCH**  
**Last Updated:** 2026-03-18 16:53 GMT  
**Sprint Lead:** CEO (fashion-tech-ceo)
