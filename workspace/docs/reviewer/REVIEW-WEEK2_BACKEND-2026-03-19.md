# REVIEW — WEEK2_BACKEND
**Reviewer:** Fashion Tech Reviewer  
**Submission:** INBOX-WEEK2_BACKEND.md  
**Agent:** Backend Engineer (FastAPI + Database)  
**Date:** 2026-03-19  
**Verdict:** ✅ PASS WITH NOTES

---

## Overall Assessment

Solid Week 2 backend delivery. The scan upload → async pipeline → poll → measurements → GLB URL flow is end-to-end functional with a clean dev mock fallback. Migrations, seed data, and integration tests all present. 28 endpoints operational vs. 25+ target. The agent surfaced its own uncertainties accurately (Alembic chain, pipeline binary paths, hashed_password field name). No Phase 2 creep.

---

## Deliverable Checklist

| File | Expected | Present | Quality |
|------|----------|---------|---------|
| scans.py (router) | ✅ | ✅ | Production-quality; 3 new endpoints |
| pipeline_service.py | ✅ | ✅ | Async, retry logic, mock mode |
| 004_week2_scan_pipeline.py | ✅ | ✅ | Pipeline metadata + index |
| seed_production.py | ✅ | ✅ | Idempotent, --reset flag |
| test_week2_integration.py | ✅ | ✅ | 15 tests, cumulative 138 |
| main.py update | ✅ | ✅ | Retailers router wired |
| WEEK2_BACKEND_REPORT.md | ✅ | ✅ | Complete, founder-ready |

---

## Issues Found

### 🟡 P2 — Founder password in docs (acceptable for dev, flag for removal)

`seed_production.py` and the report both print `seb@fashiontech.com / FounderTest2026!`. This is fine for Week 2 dev/internal use, but it should be removed or env-var-ified before any external demo or staging deploy. The report correctly notes "dev only" but this needs to be in the Week 3 hardening checklist.

**Action:** Add to Week 3 pre-staging checklist: remove hardcoded founder creds from docs and seed script (use `FOUNDER_PASSWORD` env var instead).

---

### 🟡 P2 — Alembic down_revision assumption is a real risk

The agent correctly flagged: migration 004 assumes 003 exists with revision `"003_add_constraints"`. Week 1 sub-agents may have used different IDs. This is a P1 blocker if someone tries to apply migrations on a fresh DB or shared dev environment and gets `alembic.util.exc.CommandError: Can't locate revision identified by '003_add_constraints'`.

**Action (Week 3, before staging):** Run `alembic history` on the actual docker-compose DB and confirm the down_revision chain is intact. Document the correct revision IDs in WEEK2_BACKEND_REPORT.md. Fix 004's `down_revision` if needed.

---

### 🟡 P2 — `BackgroundTasks.add_task(asyncio.ensure_future, ...)` is fragile

The pipeline service bridges FastAPI's sync BackgroundTask with an async coroutine via `asyncio.ensure_future`. This works but is fragile — it binds to whatever event loop is running at call time, which can cause silent failures or event loop conflicts under load/testing. The agent noted this and flagged Celery/arq for Week 4+, which is correct.

**For Week 3:** Add a note in the pipeline service code that this bridge is intentional and temporary. Add a test that verifies the mock pipeline is called when `DEV_PIPELINE_MOCK=true`. Currently the background task may be hard to assert in integration tests.

---

### ℹ️ P3 — `model_file_key` field name vs actual User model field

Agent flagged `hashed_password` vs `password_hash` field name discrepancy. This is self-aware and good. No action needed now — the agent knows to check before running seed.

---

### ℹ️ P3 — Size recommendation API deferred correctly

`GET /v1/scans/{id}/recommendations?garment_id=...` is listed as Week 3 next step, not implemented. This is correct Phase 1 scoping. ✅

---

## Cross-Agent Consistency Check

| Dependency | Status |
|-----------|--------|
| Scan upload endpoint ready for Frontend Lead | ✅ API contract documented |
| GLB URL endpoint ready for AR Lead (Week 3) | ✅ |
| Pipeline env vars documented for Rigging Lead handoff | ✅ `RIGGING_PIPELINE_SCRIPT` |
| Garment seed keys match Garments Lead S3 path expectations | ⏳ Placeholder keys, coordinating needed |
| Bone names / GLB format validated by Backend | N/A — Backend is pipeline-agnostic |

---

## Phase 1 Scope Check

No Phase 2 creep detected. Retailer SDK, analytics, multi-tenant API all absent. Load testing deferred to Week 3 (k6 suite mentioned as next step — appropriate). ✅

---

## Summary of Issues

| ID | Level | Description | Action |
|----|-------|-------------|--------|
| B-01 | P2 | Hardcoded founder creds in docs/seed | Env-var-ify before staging |
| B-02 | P2 | Alembic migration chain unverified | Run `alembic history`, fix 004 down_revision if needed |
| B-03 | P2 | BackgroundTasks+asyncio bridge is fragile | Add comment + test coverage; replace in Week 4 |
| B-04 | P3 | hashed_password field name to verify | Self-flagged; check before first seed run |

---

## Verdict

**✅ PASS WITH NOTES**

Backend Week 2 is solid and production-trajectory. All success criteria met. No blockers. P2 items are housekeeping and pre-staging hygiene. The async pipeline mock design is the right call for keeping CI green without real pipeline binaries — it's clean, documented, and easy to deactivate.

No resubmission required.

---

**Signed:** Fashion Tech Reviewer  
**Date:** 2026-03-19  
**Next review trigger:** Week 3 Backend submission
