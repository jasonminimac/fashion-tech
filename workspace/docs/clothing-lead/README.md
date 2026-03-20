# Clothing & Physics Lead — Phase 1 Summary & Kickoff Guide

**Document Owner:** Clothing & Physics Lead  
**Date:** 2026-03-17  
**Phase 1 Duration:** 6-8 weeks  
**Status:** Ready for Execution  

---

## Welcome to Fashion Tech 🎭

You are the **Clothing & Physics Lead** — the person responsible for making garments work beautifully on Fashion Tech's virtual try-on platform.

Your mission: **Design and build the garment scanning, fitting, and simulation systems that let users try on realistic clothes before buying.**

---

## What You're Building

### Phase 1 Goals (MVP)

| Goal | Target | Success Metric |
|------|--------|-----------------|
| **Garment Catalogue** | 50+ garments | Diverse mix (shirts, dresses, pants, jackets) |
| **Import Pipeline** | >95% success | Auto-import from CLO3D, MD, OBJ files |
| **Fitting Algorithm** | <1 sec per garment | Shrinkwrap-based, no clipping |
| **Web Viewer Integration** | 60fps animation | Garments animate smoothly on user bodies |
| **B2B Onboarding** | <30 min per partner | Simple API submission + QA process |
| **Quality Assurance** | ±1 size accuracy | Users wearing M see M-sized garments |

### What Phase 1 Does NOT Include

- ❌ Real-time cloth simulation (Phase 2)
- ❌ AR try-on (Phase 3)
- ❌ Mobile native app (Phase 3)
- ❌ Advanced animations (Phase 2+)

---

## Your Workspace

```
/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/docs/clothing-lead/
  ├─ TECHNICAL_ARCHITECTURE.md       ← Start here! Core design docs
  ├─ CLOTH_SIMULATION_STRATEGY.md     ← Why Phase 1 skips cloth sim
  ├─ ROADMAP_DEPENDENCIES.md          ← Week-by-week plan + dependencies
  ├─ GARMENT_API_REFERENCE.md         ← API, database schema, examples
  └─ [this file]
```

**Key Files to Read First:**
1. **TECHNICAL_ARCHITECTURE.md** — Complete system design
2. **ROADMAP_DEPENDENCIES.md** — Your 8-week plan
3. **CLOTH_SIMULATION_STRATEGY.md** — Why we're doing static fitting first

---

## Critical Dependencies & Blockers

### Must-Have (Week 1)

| Item | Provider | Risk | Mitigation |
|------|----------|------|-----------|
| **Reference T-pose body** | Blender Lead | High | Follow up Day 1, have placeholder ready |
| **Database + S3 access** | Backend/DevOps | Medium | Request immediately, use local disk if delayed |
| **Garment sample files** | CEO/Product | Low | Use publicly available garments (CLO3D demo files) |

### Week 3-4 Dependent

| Item | Provider | Risk |
|------|----------|------|
| **Test body scans** | 3D Scanning Lead | Medium |
| **Animation skeleton** | Blender Lead | Low |

### Week 5+ Dependent

| Item | Provider | Risk |
|------|----------|------|
| **Web viewer integration** | Frontend Engineer | Low |
| **Partner submission API** | Backend Engineer | Medium |
| **Partner outreach & sourcing** | CEO/Product | High |

---

## Success Criteria for Week 8

**You've succeeded if:**

1. ✅ **50+ garments imported** (mix of categories)
2. ✅ **Fitting validated** on 10+ diverse body types (no clipping)
3. ✅ **Web viewer integration** works (garments animate smoothly)
4. ✅ **B2B pipeline established** (5+ partners recruited, 1 full submission tested)
5. ✅ **Zero critical bugs** blocking user try-on
6. ✅ **Documentation complete** (API, schema, tuning guide)

---

## Quick Start Checklist (Week 1)

### Day 1: Kickoff

- [ ] Read TECHNICAL_ARCHITECTURE.md fully (1 hour)
- [ ] Read ROADMAP_DEPENDENCIES.md (30 min)
- [ ] Schedule 1:1s with:
  - Blender Lead (get reference body status)
  - Backend Lead (database + S3 setup)
  - Frontend Lead (viewer requirements)
- [ ] Set up workspace (git repo, local development environment)

### Day 2-3: Schema & Infrastructure

- [ ] Finalize garment database schema (review with Backend Lead)
- [ ] Set up PostgreSQL local development
- [ ] Configure S3 bucket (test upload/download)
- [ ] Create sample garment records (in database and S3)

### Day 4-5: Import Pipeline

- [ ] Review existing CLO3D/MD import tools (if any available)
- [ ] Start Python script for CLO3D file parsing (`import_clo3d.py`)
- [ ] Start Python script for mesh cleanup (`cleanup_mesh.py`)
- [ ] Test on 1 sample garment (end-to-end)

### Week 1 Deliverables

- [ ] Garment database schema finalized + committed to git
- [ ] S3 bucket configured + tested
- [ ] `import_*.py` scripts skeleton written
- [ ] 1 sample garment imported successfully
- [ ] Fabric parameter lookup table created
- [ ] Weekly status sent to CEO

---

## Decision Checklist (Before Week 2)

### Technical Decisions

- [ ] **Which Blender version?** (3.6 vs. 4.0 for cloth sim stability)
- [ ] **Shrinkwrap offset defaults?** (how far garment from body: 3-5 cm typically)
- [ ] **Size scaling strategy:** Uniform scale + per-dimension offsets? ✅ Decided: YES
- [ ] **Web mesh format:** GLB vs. FBX? ✅ Decided: GLB (industry standard)

### Integration Decisions

- [ ] **Who recruits manufacturers?** (Clothing Lead or CEO/Product?)
- [ ] **QA approval process:** Single sign-off (Clothing Lead) or multiple reviewers?
- [ ] **Partner communication:** Direct or through backend API?

### Risk Decisions

- [ ] **If Blender reference body delayed:** Use synthetic placeholder? ✅ YES
- [ ] **If garment sourcing slow:** Create internal test garments? ✅ YES
- [ ] **If fitting algorithm struggles:** Accept manual tweaking? ✅ YES, for Phase 1

---

## Key Technical Insights (From Architecture Docs)

### Garment Data Model

Every garment has:
- **Metadata:** name, brand, category, color, price, retail link
- **Geometry:** 3D mesh (GLB), textures, normals
- **Sizing:** Size chart (XS-XL) with scale factors per size
- **Cloth Physics:** Fabric params (weight, damping, elasticity)
- **Fitting Parameters:** Offsets from body (chest, waist, hip clearance)

### Static Fitting Algorithm (Phase 1)

```
1. Load garment (size M)
2. Scale garment for target size (XS = 0.85×, L = 1.08×)
3. Apply shrinkwrap modifier to fit to body
4. Check for clipping, adjust if needed
5. Export to GLB for web viewer
→ Result: Properly fitted garment, no cloth sim needed
```

### Why No Real-Time Cloth Sim in Phase 1?

1. **Time:** Tuning cloth sim for 50+ garments = 3+ extra weeks
2. **Complexity:** Blender cloth sim is powerful but needs parameter tuning per garment
3. **MVP Goal:** Prove core loop works (scan → try-on → buy), not perfect physics
4. **Risk:** One fewer complex system to debug before launch

**Phase 2 Plan:** Add pre-baked cloth simulation + pose-space blending (still fast, more realistic).

---

## Collaboration Patterns

### With Blender Lead

**Weekly Sync:** Mondays 10 AM  
**Ask for:** Reference body, animation data, Blender export format

### With Backend Engineer

**Weekly Sync:** Mondays 10 AM  
**Ask for:** Database schema review, S3 setup, partner API endpoint

### With Frontend Engineer

**When:** Week 5+ (viewer integration)  
**Ask for:** GLB format compatibility, performance targets, UI for garment selection

### With 3D Scanning Lead

**When:** Week 4 (fitting validation)  
**Ask for:** Diverse test body scans (10+ different sizes/proportions)

### With CEO/Product

**Weekly Status:** Friday 4 PM  
**Discuss:** Partner sourcing, roadmap adjustments, blocking issues

---

## Common Pitfalls to Avoid

### 🚫 Pitfall 1: Over-Engineering Phase 1

**Risk:** Spend weeks perfecting cloth sim before MVP launches.  
**Mitigation:** **Phase 1 = static fitting only.** Cloth sim is Phase 2. Stick to the plan.

### 🚫 Pitfall 2: Assuming All Garments Fit the Same Way

**Risk:** One fitting algorithm doesn't work for dresses + pants + jackets.  
**Mitigation:** Test fitting heavily (Week 4), iterate on algorithm, accept category-specific tweaks.

### 🚫 Pitfall 3: Waiting for Perfect Partner Sourcing

**Risk:** Recruiting 50 manufacturers takes months.  
**Mitigation:** Start with 5-10 partners, use internal test garments, iterate with real partners in Phase 2.

### 🚫 Pitfall 4: Ignoring Performance Targets

**Risk:** Garments take 30+ seconds to import/fit, slow down everything else.  
**Mitigation:** Profile early (Week 2), optimize mesh complexity, set hard performance budgets.

### 🚫 Pitfall 5: Losing Scope Creep

**Risk:** CEO asks for AR try-on, real-time cloth sim, etc. in Phase 1.  
**Mitigation:** Have this roadmap handy, remind team Phase 1 = MVP scope, Phase 2+ = upgrades.

---

## Tools & Technologies You'll Use

### Core Technologies

- **Blender** (3.6+) — 3D modeling, cloth sim engine
- **Python** — Scripting, import/export, automation
- **PostgreSQL** — Garment metadata storage
- **AWS S3** — 3D model and texture storage
- **Git** — Version control

### Python Libraries

- **bpy** — Blender Python API (scripting inside Blender)
- **trimesh** — Mesh processing (simplification, validation)
- **pyvista** — Point cloud / mesh operations
- **numpy** — Numerical computing
- **pillow** — Image processing (texture optimization)
- **boto3** — AWS S3 interaction
- **sqlalchemy** — Database ORM

### File Formats

- **.zprj** — CLO3D garment files (proprietary)
- **.md** — Marvelous Designer files (proprietary)
- **.obj** — Standard 3D geometry (open)
- **.fbx** — Industry-standard 3D exchange (Autodesk)
- **.glb** — Binary glTF (web-optimized)
- **.blend** — Blender native format (for source storage)

---

## Communication Cadence

### Daily (Async)

- Slack/Discord for quick questions
- GitHub issues for bugs/blockers
- Ad-hoc 1:1s if dependencies blocked

### Weekly (Sync)

- **Monday 10 AM:** Team standup (5 leads + CEO)
  - Status, blockers, decisions
  - 30 minutes

- **Friday 4 PM:** Status to CEO
  - Written update (what got done, next week plan, metrics)
  - Ad-hoc calls if issues

### Bi-Weekly (Extended)

- **Every 2 weeks:** Technical deep-dives with Blender + Backend leads
  - Design reviews, API changes, integration planning
  - 1 hour

---

## Emergency Escalation

**If you're blocked (can't proceed for >1 hour):**

1. **Slack/message** the blocking person immediately
2. **Tag CEO** if it's still unresolved after 1 hour
3. **Document in GitHub issue** (for post-mortem)

**Examples of blockers:**
- Reference body not exported from Blender
- S3 bucket credentials missing
- Database schema rejected
- Partner files can't be parsed

---

## Learning Resources

### Blender Python API

- **Official Docs:** https://docs.blender.org/api/current/
- **Cloth Sim Docs:** https://docs.blender.org/manual/en/latest/physics/cloth/index.html
- **Shrinkwrap Modifier:** Search "bpy shrinkwrap" in docs

### 3D Mesh Processing

- **trimesh tutorial:** https://trimesh.org/
- **pyvista docs:** https://docs.pyvista.org/
- **Point cloud processing:** CloudCompare or Open3D tutorials

### Garment Design Tools

- **CLO3D:** Free trial + docs (https://www.clo3d.com/)
- **Marvelous Designer:** Free trial + docs (https://marvelousdesigner.com/)

---

## Phase 1 Success Story

**Week 8, End of Phase 1:**

You've successfully:

1. ✅ Built and tested the import pipeline
   - Auto-import from CLO3D, MD, and OBJ files
   - Comprehensive geometry cleanup
2. ✅ Developed a robust fitting algorithm
   - Shrinkwrap-based, tested on 20+ diverse bodies
   - Fits accurately (no clipping) at XS-XL sizes
3. ✅ Recruited 5+ manufacturer partners
   - Simple submission process (API upload + metadata)
   - QA checklist + feedback loop established
4. ✅ Built a 50+ garment catalogue
   - Shirts, dresses, pants, jackets (diverse mix)
   - All validated, all searchable in web viewer
5. ✅ Integrated with web viewer
   - Garments load quickly, animate smoothly
   - Users can scan, select size, try on garments
6. ✅ Documented everything
   - API reference, technical architecture, tuning guide
   - Ready for Phase 2 + external partners

**Demo:**
> User scans their body → selects M-sized shirt → sees it fitted on their scanned body → watches it animate → sees "looks good!" and buys. **MVP success.** 🎉

---

## Next Steps

### Today (2026-03-17)

1. **Read the 4 key documents** (TECHNICAL_ARCHITECTURE, CLOTH_SIMULATION_STRATEGY, ROADMAP_DEPENDENCIES, API_REFERENCE)
2. **Schedule 1:1s** with Blender Lead, Backend Lead, Frontend Lead
3. **Set up workspace** (git, local dev environment)

### This Week (Week 1)

1. **Finalize database schema** with Backend Lead
2. **Set up S3 + PostgreSQL** with DevOps
3. **Start import pipeline** scripts (at least CLO3D and OBJ)
4. **Create fabric parameter lookup table**
5. **Send Friday status** to CEO

### Next Week (Week 2)

1. **Import first 5 sample garments** (end-to-end test)
2. **Begin fitting algorithm development**
3. **Validate against reference body** (from Blender Lead)

---

## Questions? Blockers?

- **Quick questions:** Slack the relevant lead
- **Design decisions:** Schedule 1:1 with CEO
- **Technical blockers:** Post GitHub issue, tag relevant team member
- **Documentation unclear:** Add questions to this guide (iterate)

---

## Parting Wisdom

> Building a fashion tech system is hard. Cloth simulation is *really* hard. You're doing the right thing by focusing Phase 1 on **getting the core loop working** (scan → try-on → buy) instead of chasing photorealism. 
>
> Your job is to make garments look good enough that users trust the fit. Perfect physics comes later.
>
> You've got a solid team. Lean on them. Communicate early, iterate often. Make 2026-03-17 the start of something cool.

**Let's build.** 🚀

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Review:** After Week 1 kickoff
