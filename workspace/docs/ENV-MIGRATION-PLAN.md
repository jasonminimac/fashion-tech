# Environment Migration Plan: Dev ↔ Production Floor Separation
**Status:** DRAFT — For Founder Review  
**Date:** 2026-03-19  
**Prepared by:** Fashion Tech CEO (Subagent)  

---

## Executive Summary

**Current State:** Misaligned environments
- **Dev environment** (`/Users/Jason/.openclaw/workspace/projects/fashion-tech/`) — skeleton structure, 100 files, mostly source code
- **Production floor** (`/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`) — sprawling, 6000+ files, mixed content (agent work, team notes, implementations, docs)

**Core Problem:** Active development has been happening directly in production floor workspace. Dev environment has the correct structure (per PROJECT-PATHS.md) but lacks the actual work.

**Goal:** Establish clean separation where:
- **Dev** = all active development, git-tracked source, pipeline code, frameworks
- **Production floor workspace** = team notes, agent task outputs, sprint docs, decision records (ephemeral)

---

## Audit Results

### 1. Development Environment (`/Users/Jason/.openclaw/workspace/projects/fashion-tech/`)

**Structure:** Well-organized, 100 files across 9 top-level directories

```
fashion-tech/
├── apps/                 (3 applications)
│   ├── api/             FastAPI backend skeleton (~18 files)
│   ├── ios-ar/          iOS AR app Swift code (~12 files)
│   └── web/             React frontend (~7 files)
├── pipeline/            (4 pipelines)
│   ├── scanning/        COLMAP, Open3D setup (~15 files)
│   ├── rigging/         Blender automation (~10 files)
│   ├── garments/        CLO3D workflow (~10 files)
│   └── ar/              (empty stub)
├── assets/              (4 subdirs, 31 garment OBJ files)
│   ├── garments/        Baked T-shirt sequences
│   ├── meshes/          (empty stub)
│   ├── textures/        (empty stub)
│   └── animations/      (empty stub)
├── data/                (3 subdirs, mostly empty stubs)
│   ├── scans/
│   ├── test-subjects/
│   └── benchmarks/
├── infrastructure/      (3 subdirs, mostly stubs)
│   ├── db/              schema-v1.sql
│   ├── s3/              (empty stub)
│   └── cdn/             (empty stub)
├── packages/            (stub)
│   └── retailer-sdk/
├── docs/                (docs & decisions)
│   ├── sprints/         (empty stub)
│   ├── decisions/       (empty stub)
│   └── research/        (empty stub)
├── output/              (2 binary files: body.glb, body_rigged.blend)
├── PROJECT-PATHS.md     (path reference & role mapping)
└── AR-DECISION.md       (Sprint 2 technical decision — critical keeper)
```

**Git Status:**
- 1 commit: "Sprint 1: Pipeline Skeleton — initial commit"
- 10 untracked files (mostly new work from Sprint 2)
- Modified tracked files: 3 (api requirements, web components, iOS router)

**Key files in dev:**
- ✅ `PROJECT-PATHS.md` — authoritative structure reference
- ✅ `AR-DECISION.md` — founder decision document
- ✅ `pipeline/scanning/`, `pipeline/rigging/`, `pipeline/garments/` — process documentation
- ✅ `apps/api/`, `apps/ios-ar/`, `apps/web/` — application skeletons
- ⚠️ Sprint 2 work (SPRINT-2-NOTES.md files, new services) — untracked, needs to be committed

---

### 2. Production Floor Workspace (`/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`)

**Structure:** Large, 6000+ files across 11 top-level directories

```
workspace/
├── backend/             (Full FastAPI implementation, 600+ files)
│   ├── src/app/         (14 routes, services, models)
│   ├── tests/
│   ├── alembic/         (database migrations)
│   ├── scripts/
│   └── docs/
├── rigging-engine/      (Major codebase, 800+ files)
│   ├── framework/
│   ├── rigging/
│   ├── export/
│   ├── scripts/
│   ├── tests/
│   └── week2/, archive/, output/
├── projects/            (CI/CD + sample code)
│   ├── ios/             (project config, not actual source)
│   └── python/
├── docs/                (27 team member directories!)
│   ├── backend-engineer/
│   ├── 3d-scanning-lead/
│   ├── blender-lead/
│   ├── rigging/
│   ├── garments/
│   ├── platform/
│   ├── reviewer/        (31 review/inbox files)
│   ├── ar/, frontend-engineer/, clothing-lead/, brand-outreach/
│   ├── ceo/, seb-reviews/, shared/
│   └── (root docs: DISCOVERY.md, ROADMAP.md, FOUNDER-DECISIONS.md, SPRINT-1.md, etc.)
├── assets/              (scans/ directory, 100+ files)
├── sprints/             (sprint tracking, 20+ files)
├── reports/             (empty)
├── archive/             (old work)
├── memory/              (team memory/notes)
└── .github/workflows/
```

**Critical Issue:**
This is a **working environment**, not a "production live" in the traditional sense. It contains:
- ✅ **Important:** Team deliverables, sprint docs, agent work outputs, team memory
- ❌ **Misplaced:** Full `backend/` codebase (should be in dev)
- ❌ **Misplaced:** `rigging-engine/` (should be in dev)
- ⚠️ **Confused:** `projects/` folder (only config, not the actual app source)

---

## Root Cause Analysis

1. **No git history in production floor** — unclear when code was placed there
2. **PROJECT-PATHS.md created after the fact** — skeleton in dev doesn't match actual work
3. **Agent task outputs went to production floor** — natural, but created accumulation
4. **No clear promotion workflow** — no distinction between dev work and floor workspace outputs

---

## The Correct Model

### Environments & Their Purpose

| Location | Purpose | Content | Git? | Lifespan |
|----------|---------|---------|------|----------|
| **Dev** (`/Users/Jason/.openclaw/workspace/projects/fashion-tech/`) | Active development | Source code, pipeline scripts, configs, binaries | ✅ Yes | Permanent |
| **Floor workspace** (`/.../company/floors/fashion-tech/workspace/`) | Team coordination & decision records | Sprint docs, role outputs, team memory, agent deliverables | ❌ No (ephemeral) | Per-phase |

### Content Classification

**Should be in dev:**
- Application source: `backend/`, `ios-ar/`, `web/`
- Pipeline scripts: COLMAP, Blender, CLO3D automation
- Test data & assets: scans, meshes, garments
- Infrastructure configs: schema.sql, S3 policies, CDN configs
- Decision documents: AR-DECISION.md, architecture ADRs

**Should be in production floor workspace:**
- Team task outputs: agent-produced docs, role-specific work summaries
- Ephemeral: sprint briefs, meeting notes, weekly summaries
- Team memory: ongoing notes per role
- Reviewer outputs: code review logs, quality gates

---

## Proposed Target Structure

### Dev Environment: `/Users/Jason/.openclaw/workspace/projects/fashion-tech/`

```
fashion-tech/                      ← Permanent, git-tracked
├── .git/
├── .gitignore
├── README.md                       ← Overall project guide
├── ARCHITECTURE.md                 ← System design overview
├── AR-DECISION.md                  ← Keep: founder decision
│
├── apps/
│   ├── api/                        ← Backend (Python/FastAPI)
│   │   ├── src/
│   │   │   └── app/
│   │   │       ├── models/
│   │   │       ├── routers/
│   │   │       ├── services/
│   │   │       └── core/
│   │   ├── tests/
│   │   ├── alembic/                ← Migrations
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── ios-ar/                     ← iOS AR app (Swift/Xcode)
│   │   ├── Sources/
│   │   │   ├── AR/
│   │   │   ├── Scanning/
│   │   │   ├── Garments/
│   │   │   └── Utils/
│   │   ├── Resources/
│   │   ├── Tests/
│   │   ├── Package.swift
│   │   └── README.md
│   │
│   └── web/                        ← React web UI
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   └── main.tsx
│       ├── public/
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── README.md
│
├── pipeline/                       ← Processing pipelines
│   ├── scanning/
│   │   ├── colmap_pipeline.py
│   │   ├── colmap_to_measurements.py
│   │   ├── process_scan.py
│   │   ├── tests/
│   │   ├── COLMAP-SETUP.md
│   │   └── README.md
│   │
│   ├── rigging/
│   │   ├── auto_rig.py
│   │   ├── export_glb.py
│   │   ├── scripts/
│   │   ├── tests/
│   │   ├── IMPLEMENTATION-PLAN.md
│   │   └── README.md
│   │
│   ├── garments/
│   │   ├── blender_cloth_sim.py
│   │   ├── obj_to_usdz.py
│   │   ├── fabric_library.json
│   │   ├── garment_metadata_schema.json
│   │   ├── CLO3D-WORKFLOW.md
│   │   └── README.md
│   │
│   └── ar/
│       ├── usdz_pipeline.py
│       ├── animation_export.py
│       └── README.md
│
├── assets/                         ← Asset data
│   ├── garments/
│   │   ├── tshirt-sprint1/         ← OBJ sequences
│   │   ├── tshirt-sprint2/
│   │   └── ...
│   │
│   ├── meshes/                     ← Test body scans (.ply, .obj)
│   ├── textures/                   ← PBR maps
│   └── animations/                 ← BVH, motion capture
│
├── data/                           ← Test/benchmark data
│   ├── scans/                      ← Body scan outputs
│   ├── test-subjects/              ← Subject archives
│   └── benchmarks/                 ← Performance traces, reports
│
├── infrastructure/                 ← Config as code
│   ├── db/
│   │   ├── schema.sql              ← Current schema
│   │   ├── migrations/
│   │   └── seed.sql
│   │
│   ├── s3/
│   │   ├── bucket-policy.json
│   │   ├── lifecycle-rules.json
│   │   └── README.md
│   │
│   └── cdn/
│       ├── cloudfront-config.json
│       └── README.md
│
├── packages/                       ← SDK & libraries
│   └── retailer-sdk/               ← Phase 2: JS embed SDK
│       ├── src/
│       ├── dist/
│       ├── package.json
│       └── README.md
│
├── docs/
│   ├── DESIGN.md                   ← System design
│   ├── ROADMAP.md                  ← Technical roadmap
│   │
│   ├── decisions/                  ← Architecture Decision Records
│   │   ├── ADR-001-AR-RENDERER.md  ← AR decision moved here
│   │   ├── ADR-002-*.md
│   │   └── INDEX.md
│   │
│   ├── research/
│   │   ├── MARKET-RESEARCH.md
│   │   ├── COMPETITOR-ANALYSIS.md
│   │   └── PARTNER-RECON.md
│   │
│   ├── api/
│   │   └── RETAILER-API-SPEC.md    ← OpenAPI spec
│   │
│   └── sprints/                    ← Tech-focused sprint summaries (not team notes)
│       ├── SPRINT-1-SUMMARY.md
│       ├── SPRINT-2-SUMMARY.md
│       └── README.md
│
├── output/                         ← Build outputs (CI/CD generated)
│   ├── builds/
│   ├── releases/
│   └── .gitignore
│
├── .env.example
├── Makefile                        ← Common tasks
├── docker-compose.yml              ← Local dev environment (optional)
└── PROJECT-PATHS.md                ← Move here or update
```

**Notes:**
- All code under version control
- Clear per-app, per-pipeline separation
- Tests colocated with source
- Infrastructure as code
- Docs include ADRs and decisions

---

### Production Floor Workspace: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`

```
workspace/                         ← Ephemeral, NO git
├── docs/
│   ├── DISCOVERY.md                ← Initial project discovery
│   ├── KICKOFF-SUMMARY.md          ← Team kickoff output
│   ├── ROADMAP.md                  ← Business/product roadmap
│   ├── FOUNDER-DECISIONS.md        ← Founder decisions & approvals
│   │
│   ├── {role}/                     ← Per-role task outputs
│   │   ├── backend-engineer/
│   │   ├── 3d-scanning-lead/
│   │   ├── blender-lead/
│   │   ├── rigging/
│   │   ├── garments/
│   │   ├── platform/
│   │   ├── ar/
│   │   ├── frontend-engineer/
│   │   ├── clothing-lead/
│   │   ├── brand-outreach/
│   │   └── (etc.)
│   │
│   ├── reviewer/                   ← Quality gate outputs
│   │   ├── INBOX-{task-id}.md
│   │   ├── REVIEW-LOG.md
│   │   └── PASS-LOG.md
│   │
│   ├── ceo/                        ← CEO decisions & memos
│   ├── seb-reviews/                ← Founder review notes
│   └── shared/                     ← Team reference docs (not in dev)
│
├── sprints/
│   ├── SPRINT-1-BRIEF.md           ← Task assignments
│   ├── SPRINT-1-SUMMARY.md         ← Outcome summary
│   ├── SPRINT-2-BRIEF.md
│   ├── SPRINT-2-SUMMARY.md
│   └── README.md
│
├── memory/
│   ├── YYYY-MM-DD.md               ← Daily team notes
│   └── long-term-insights.md       ← Persisted learnings
│
├── assets/
│   ├── scans/                      ← Test scan data (ephemeral, not in dev)
│   └── work-in-progress/           ← Temporary assets
│
├── reports/
│   ├── WEEK-1-SUMMARY.md
│   ├── WEEK-2-SUMMARY.md
│   └── performance-metrics.md
│
├── archive/
│   └── (old sprints, deprecated docs)
│
└── .floor-metadata.md              ← Floor-specific info
```

**Notes:**
- NO version control (ephemeral)
- Centered on team coordination
- Role-specific outputs
- Sprint tracking
- Decision records

---

## Migration Plan: Step-by-Step

### Phase 1: Prepare & Validate (No changes to production)

**Step 1.1:** Audit current state ✅ DONE
- Inventory both locations
- Understand current file structure
- Identify what's where

**Step 1.2:** Commit Sprint 2 work to dev git
```bash
cd /Users/Jason/.openclaw/workspace/projects/fashion-tech/
git add -A
git commit -m "Sprint 2: Backend services, iOS AR components, garment pipeline additions"
git log --oneline  # Verify
```
**Owner:** Dev team  
**Risk:** Low (new commit, no history rewrite)  
**Reversibility:** High (can be reverted with `git reset`)

**Step 1.3:** Create `.gitignore` for dev repo
```
# Dev environment
*.DS_Store
.venv/
__pycache__/
dist/
build/
*.egg-info/
node_modules/
.env
output/*.glb
output/*.blend
data/scans/*
data/test-subjects/*
```

**Step 1.4:** Validate PROJECT-PATHS.md matches dev structure
- Read PROJECT-PATHS.md
- Cross-check against actual directory layout
- Flag any inconsistencies
- Update as needed

**Owner:** Fashion Tech CEO  
**Risk:** Low (review only)

---

### Phase 2: Copy & Restructure (Strategic moves)

**Step 2.1:** Copy `backend/` from floor to dev

```bash
# From production floor's backend/ to dev's apps/api/
# The floor's backend/ is a full implementation; dev's apps/api/ is a skeleton

# Option A (recommended): Keep dev's structure, port floor's production code into it
cp -r /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/src/app/* \
      /Users/Jason/.openclaw/workspace/projects/fashion-tech/apps/api/src/app/
cp -r /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/alembic/* \
      /Users/Jason/.openclaw/workspace/projects/fashion-tech/apps/api/alembic/
cp /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/requirements.txt \
   /Users/Jason/.openclaw/workspace/projects/fashion-tech/apps/api/

# Option B (if floor structure is superior): restructure dev to match
# [Manual decision needed from founder]
```

**Owner:** Backend lead + CEO  
**Risk:** Medium (code merge complexity)  
**Reversibility:** High (can restore from floor copy)  
**Decision point:** Founder must confirm which structure to keep

---

**Step 2.2:** Copy `rigging-engine/` from floor to dev

```bash
# Floor's rigging-engine/ is a major codebase; likely should be in dev under pipeline/rigging/
# OR as a separate pkg (decision: is it part of pipeline or standalone?)

# Proposed: Merge into dev/pipeline/rigging/ or keep as separate tracked module
# [Manual decision needed from founder]
```

**Owner:** Rigging lead + CEO  
**Risk:** High (large codebase, unclear scope)  
**Reversibility:** Medium (folder move is safe, but integration risk)  
**Decision point:** Founder must define: is rigging-engine a sub-pipeline or separate project?

---

**Step 2.3:** Move scanner assets & test data to dev

```bash
# Floor has test scan data in assets/scans/
cp -r /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/assets/scans \
      /Users/Jason/.openclaw/workspace/projects/fashion-tech/data/test-scans/
```

**Owner:** Data/scanning lead  
**Risk:** Low (data only)  
**Reversibility:** High (copy, can be reverted)

---

**Step 2.4:** Move decision documents to dev/docs/decisions/

```bash
# From production floor
cp /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/docs/FOUNDER-DECISIONS.md \
   /Users/Jason/.openclaw/workspace/projects/fashion-tech/docs/decisions/DECISIONS.md

# AR-DECISION.md is already in dev — rename to ADR-001-AR-RENDERER.md
mv /Users/Jason/.openclaw/workspace/projects/fashion-tech/AR-DECISION.md \
   /Users/Jason/.openclaw/workspace/projects/fashion-tech/docs/decisions/ADR-001-AR-RENDERER.md
```

**Owner:** CEO  
**Risk:** Low (documentation only)  
**Reversibility:** High (can be moved back)

---

### Phase 3: Clean Production Floor Workspace

**Step 3.1:** Archive old implementations
```bash
# Move full backend/ → archive/
mv /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/ \
   /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/archive/backend-moved-2026-03-19/

# Move rigging-engine/ → archive/
mv /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine/ \
   /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/archive/rigging-engine-moved-2026-03-19/

# Move projects/ (config only) → archive/
mv /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/projects/ \
   /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/archive/ci-config-moved-2026-03-19/
```

**Owner:** Floor admin  
**Risk:** MEDIUM (destructive moves, though kept in archive)  
**Reversibility:** High (archive is preserved; can restore if needed)  
**Approval:** **FOUNDER REQUIRED**

---

**Step 3.2:** Reorganize remaining floor workspace
```bash
# Keep: docs/, sprints/, memory/, assets/, reports/
# Remove: backend/, rigging-engine/, projects/, .github/

# Restructure docs/ to match the proposed floor template
# (...details in Phase 4 below)
```

**Owner:** Floor admin  
**Risk:** Low (reorganization, archive preserved)

---

**Step 3.3:** Create .floor-metadata.md
```bash
cat > /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/.floor-metadata.md << 'EOF'
# Fashion Tech Floor Metadata

**Purpose:** Team coordination, task outputs, decision records, and sprint tracking

**Not stored here:** Source code (in dev), version control (dev uses git)

**Archive locations:** See `archive/` for moved code/configs

**When to add content:**
- Team task outputs → role-specific docs/ folder
- Sprint planning → sprints/ folder
- Team learnings → memory/ folder
- Decisions from founder → FOUNDER-DECISIONS.md
- Review gates → reviewer/ folder

**When NOT to add:**
- Source code (use dev environment)
- Production deployments (use separate deployment system)
EOF
```

**Owner:** CEO  
**Risk:** Low (documentation)

---

### Phase 4: Finalize & Document

**Step 4.1:** Update PROJECT-PATHS.md or create ENV-REFERENCE.md

```bash
cat > /Users/Jason/.openclaw/workspace/projects/fashion-tech/ENV-REFERENCE.md << 'EOF'
# Environment Reference

## Dev Environment: `/Users/Jason/.openclaw/workspace/projects/fashion-tech/`
- **Purpose:** All active development, source control, pipelines
- **Git:** Yes, commits required
- **Lifespan:** Permanent
- **Who:** Developers, engineers, tech leads

## Production Floor Workspace: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`
- **Purpose:** Team coordination, task outputs, ephemeral notes
- **Git:** No (not version controlled)
- **Lifespan:** Per phase (can be archived between projects)
- **Who:** All team members, agents, CEO

## Migration History
- **2026-03-19:** Initial environment separation audit
- [future migrations logged here]
EOF
```

**Step 4.2:** Create MIGRATION-COMPLETE.md (timestamp)
```bash
cat > /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/MIGRATION-COMPLETE.md << 'EOF'
# Migration Complete: Dev/Prod Separation

**Date:** 2026-03-19 (TO BE CONFIRMED AFTER EXECUTION)
**Phase:** Completed ✅ or Pending ⏳

- [ ] Code moved to dev
- [ ] Git repos initialized
- [ ] Archive preserved
- [ ] Floor workspace cleaned
- [ ] All teams notified

See ENV-MIGRATION-PLAN.md for full details.
EOF
```

---

## What Moves, What Stays, What Gets Restructured

| Item | Location | Target | Action | Risk |
|------|----------|--------|--------|------|
| **Backend code** | Floor: `backend/` | Dev: `apps/api/` | Copy + integrate | Medium |
| **Rigging engine** | Floor: `rigging-engine/` | Dev: `pipeline/rigging/` or separate | Decision required | High |
| **iOS AR code** | Floor: ??? (not found) | Dev: `apps/ios-ar/` | Already in dev ✓ | Low |
| **Web code** | Floor: ??? (not found) | Dev: `apps/web/` | Already in dev ✓ | Low |
| **Test scans** | Floor: `assets/scans/` | Dev: `data/test-scans/` | Copy | Low |
| **Garment assets** | Floor: ??? (needs audit) | Dev: `assets/garments/` | Copy | Low |
| **AR decision** | Dev: `AR-DECISION.md` | Dev: `docs/decisions/ADR-001-*.md` | Move + rename | Low |
| **Sprint docs** | Floor: `docs/` (various) | Floor: `docs/` (keep) | Reorganize only | Low |
| **Team notes** | Floor: `memory/`, role docs | Floor: keep | Clean up old | Low |
| **Projects folder** | Floor: `projects/` (CI config) | Archive | Move → archive | Low |
| **Rigging from floor** | Floor: full Blender work | Floor: → archive | Archive for ref | Low |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Code merge conflicts between floor & dev | Medium | High | Test imports locally before committing; have backend lead review |
| Lost work during archive moves | Low | Critical | Preserve archive folder; verify copies before deletion |
| Team doesn't know where to put new work | Medium | Medium | Create CHECKLISTS in each floor role folder; update onboarding |
| Git history lost if floor had undocumented changes | Low | Medium | Check floor for git history (none found in audit); document any missing commits |
| Pipeline/rigging scope unclear | High | High | **FOUNDER DECISION REQUIRED** — is rigging-engine standalone or part of pipeline? |
| Test data/assets get out of sync | Medium | Medium | Document asset ownership; use `.gitignore` rules consistently |

---

## Decision Points Requiring Founder Approval

### 🔴 CRITICAL DECISIONS

1. **Backend structure:** Keep dev's apps/api/ layout or restructure to match floor's backend/?
2. **Rigging engine scope:** Is it a standalone project or part of pipeline/rigging/?
3. **Execute timeline:** Now vs. after current sprint completes?
4. **Archive strategy:** Archive to `archive/` (as proposed) or delete?

### 🟡 RECOMMENDED DECISIONS

5. **Retailer SDK (phase 2):** Keep in dev packages/ or separate repo?
6. **CI/CD:** Migrate GitHub workflows from floor `.github/` to dev repo?

---

## Pre-Execution Checklist

- [ ] Founder reviews this plan
- [ ] Founder approves all critical decisions
- [ ] Backend lead validates code merge strategy
- [ ] Rigging scope decision clarified (ADR or separate?)
- [ ] Full copy/backup created before any moves
- [ ] Team notified of migration timeline
- [ ] All git commits pushed to safe location
- [ ] Archive folder prepared and tested

---

## Rollback Plan

If migration encounters issues:

1. **Before starting:** Create full backup
   ```bash
   cp -r /Users/Jason/.openclaw/workspace/projects/fashion-tech/ \
         /Users/Jason/.openclaw/workspace/backups/fashion-tech-pre-migration-$(date +%Y%m%d).bak/
   ```

2. **If dev code lost:** Restore from backup or floor copy

3. **If floor workspace corrupted:** Restore from archive

4. **If git history lost:** Recreate from floor copies (risky; avoid if possible)

---

## Post-Migration Steps

Once approved and executed:

1. Update all team member onboarding docs to reference new paths
2. Create README.md files in both locations with environment guides
3. Set up CI/CD to pull from dev repo only
4. Archive this migration plan at `docs/archive/MIGRATION-2026-03-19.md`
5. Schedule post-migration review (1 week) to catch any issues

---

## Appendix: File Inventory (Detailed)

### Dev Environment: 100 Files

**By Type:**
- Python: 28 files
- Swift: 12 files  
- TypeScript/React: 7 files
- Config: 5 files (JSON, SQL, YAML)
- Markdown docs: 7 files
- Binary assets: 33 files (OBJ meshes, GLB, Blend)
- Other: 1 (shell script)

**By directory:**
```
apps/api/               18 files (Python backend skeleton)
apps/ios-ar/            12 files (Swift AR code)
apps/web/               7 files (React frontend)
pipeline/               ~30 files (scripts, configs, docs)
  ├── scanning/         15 files
  ├── rigging/          10 files
  ├── garments/         10 files
  └── ar/               (stub)
assets/                 31 files (garment OBJ sequences)
infrastructure/         3 files (schema, configs)
docs/                   8 files (design, API spec)
output/                 2 files (binary test files)
root/                   2 files (PROJECT-PATHS.md, AR-DECISION.md)
```

### Production Floor: 6000+ Files

**By directory:**
```
backend/                ~600 files (full FastAPI implementation)
rigging-engine/         ~800 files (Blender rigging automation)
docs/                   ~2000 files (team outputs, role folders, reviewer)
sprints/                ~20 files
reports/                ~50 files
assets/                 ~100 files (scans, work-in-progress)
memory/                 ~20 files
projects/               ~50 files (CI config)
archive/                ~100 files (old work)
.github/                ~10 files (workflows)
```

---

## Conclusion

This migration plan establishes the correct environment separation:
- **Dev** = permanent, version-controlled, source-of-truth for code
- **Floor workspace** = ephemeral, team coordination hub, no source control

**Next steps:** Founder review and approval before execution begins.

---

*For questions or clarifications: contact Fashion Tech CEO*
