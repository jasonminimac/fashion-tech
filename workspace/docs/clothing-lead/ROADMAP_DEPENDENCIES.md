# Implementation Roadmap & Dependency Map

**Document Owner:** Clothing & Physics Lead  
**Date:** 2026-03-17  
**Phase 1 Duration:** 6-8 weeks  

---

## Overview

This document maps out the work breakdown, critical dependencies, and integration points between the Clothing Lead and other team members.

---

## Phase 1 Detailed Breakdown

### Week 1: Kickoff & Architecture Setup

#### Goals
- Confirm team alignment on garment data model
- Coordinate with Blender Lead on reference body + animation export
- Set up infrastructure (databases, S3, git repos)
- Finalize fabric parameter lookup table

#### Deliverables

**Clothing Lead:**
- [ ] Garment database schema finalized (PostgreSQL)
- [ ] Fabric property lookup table (cotton, silk, denim, etc.)
- [ ] S3 bucket structure + access policies
- [ ] Garment import skeleton (Python scripts for CLI usage)

**Coordinator:**
- [ ] Dep: Confirm Blender Lead can export reference T-pose body
- [ ] Dep: Backend Lead commits to garment API endpoint
- [ ] Decision: Which manufacturers/brands for first 10 garments?

#### Blockers
- **If:** Blender reference body not ready → Delay fitting algorithm start (Week 2)
- **If:** S3 setup delayed → Use local disk temporarily

---

### Week 2: Garment Import Pipeline + First Sample

#### Goals
- Import 5 sample garments (test CLO3D, MD, generic OBJ)
- Validate import pipeline (parse → cleanup → validate)
- Begin static fitting algorithm design

#### Deliverables

**Clothing Lead:**
- [ ] `import_clo3d.py` — CLO3D file parser
- [ ] `import_marvelous_designer.py` — MD file parser
- [ ] `cleanup_mesh.py` — Mesh decimation, manifold check
- [ ] Test import 5 sample garments (document issues found)
- [ ] Fitting algorithm pseudocode + design doc

**Blender Lead (Dependency):**
- [ ] Provide reference T-pose body (rigged, weight-painted)
- [ ] Export as FBX + Blender `.blend` file

**Backend Lead (Dependency):**
- [ ] Schema review (garment metadata structure)
- [ ] Confirm S3 bucket access

#### Key Milestones
- ✅ Import 1 CLO3D file successfully
- ✅ Parse metadata (brand, size, color)
- ✅ Store in PostgreSQL + S3

---

### Week 3: Static Fitting Algorithm

#### Goals
- Implement shrinkwrap-based fitting
- Test fitting on reference body (T-pose)
- Validate size scaling (XS-XL)
- Begin real-time animation skeleton binding

#### Deliverables

**Clothing Lead:**
- [ ] `fit_garment_to_body.py` — Core fitting logic
  - Shrinkwrap modifier application
  - Size scaling (scale factors per size)
  - Collision detection/resolution
  - Unit tests
- [ ] Fitting test suite (T-pose on reference body, all sizes)
- [ ] Collision detection report (any clipping?)
- [ ] Performance baseline (fitting speed in seconds)

**Blender Lead (Dependency):**
- [ ] Confirm shrinkwrap modifier works as expected
- [ ] Provide animation skeleton structure (bone names, hierarchy)

**Integration Notes:**
- Test fitting with 10 diverse test body scans (from 3D Scanning Lead)
- Iterate fitting parameters based on visual feedback

#### Key Milestones
- ✅ Fit garment to reference body in <1 second
- ✅ No visible clipping in T-pose
- ✅ Size scaling tested (M→XL look proportional)

---

### Week 4: Diverse Body Type Validation

#### Goals
- Test fitting on 10+ different body scans
- Identify edge cases (very tall, very wide, irregular proportions)
- Iterate fitting algorithm if needed
- Begin B2B onboarding workflow design

#### Deliverables

**Clothing Lead:**
- [ ] Test harness (batch fit 10 garments × 10 body types)
- [ ] Validation report (fit quality per body type, clipping issues)
- [ ] Iteration log (parameter tweaks, what helped)
- [ ] Edge case documentation (bodies that break fitting)

**3D Scanning Lead (Dependency):**
- [ ] Provide 10 normalized test body scans (diverse sizes/proportions)
- [ ] Ensure bodies are rigged and animation-ready

**Decision Points:**
- Fitting quality good enough for all 10 bodies? (Threshold: >80%)
- If no, adjust shrinkwrap parameters or add manual lattice tweaking

#### Key Milestones
- ✅ 50+ body types tested (if available)
- ✅ Identify worst-case bodies, document workarounds
- ✅ No critical failures blocking production

---

### Week 5: Animation Integration + Web Viewer Prep

#### Goals
- Bind fitted garments to animation skeleton (bones)
- Test garment animation in Blender
- Prepare garments for web viewer (export to GLB, optimize)
- Coordinate with Frontend Engineer on viewer integration

#### Deliverables

**Clothing Lead:**
- [ ] `bind_garment_to_skeleton.py` — Attach garment to body bones
- [ ] Animation test (walk cycle, idle pose with garment fitted)
- [ ] Performance profiling (animation smoothness, frame rate)
- [ ] `export_to_glb.py` — Optimize + compress for web

**Blender Lead (Dependency):**
- [ ] Confirm animation skeleton + bindings work
- [ ] Provide animation library (walk, idle, run animations)
- [ ] Test export GLB format (compatibility with Three.js/Babylon.js)

**Frontend Engineer (Dependency):**
- [ ] Confirm GLB format works in viewer
- [ ] Size/performance targets (max mesh complexity, load time)

**Integration Notes:**
- Generate LOD (level-of-detail) variants for low-end devices
- Test on slow network (compressed sizes)

#### Key Milestones
- ✅ Garment animates smoothly with body
- ✅ GLB export validated by Frontend Engineer
- ✅ Web viewer can load and display garment

---

### Week 6: B2B Onboarding + Garment Sourcing

#### Goals
- Design partner submission workflow (API endpoint)
- Create onboarding documentation for manufacturers
- Recruit and onboard first 5-10 garment partners
- Establish QA review process

#### Deliverables

**Clothing Lead:**
- [ ] Partner submission API spec (document format, required metadata)
- [ ] Onboarding guide for manufacturers (how to submit garments)
- [ ] `validate_submission.py` — Auto-check partner submissions
- [ ] QA checklist template (visual inspection, fit validation)
- [ ] Contact 10 manufacturers, negotiate first garments

**Backend Engineer (Dependency):**
- [ ] Implement partner submission endpoint
  - File upload, metadata validation, status tracking
  - Return validation report (errors, warnings)
- [ ] Partner portal (track submission status, communicate QA feedback)

**Product/CEO (Dependency):**
- [ ] Help identify manufacturers to approach
- [ ] Frame value proposition (easy integration, big reach)

**Integration Notes:**
- Establish SLA: response to partner within 24-48 hours
- Auto-generate validation report on submission

#### Key Milestones
- ✅ API endpoint works (test with 1 real partner submission)
- ✅ 5 manufacturers recruited, submission timeline confirmed
- ✅ QA process documented

---

### Week 7: Garment Catalogue Build-Out

#### Goals
- Import first 20-30 garments from partners
- Fit and validate each garment across sizes/body types
- Prepare for Phase 2 (cloth sim pre-baking)
- Final integration testing with Frontend Engineer

#### Deliverables

**Clothing Lead:**
- [ ] Batch import 20-30 garments
- [ ] Fit each to reference body (XS-XL)
- [ ] Validation report (quality per garment, any issues)
- [ ] Documentation of quirky garments (oversized, unusual fit)

**Frontend Engineer (Dependency):**
- [ ] Integrate 20+ garments into web viewer
- [ ] Test performance (load time, animation smoothness)
- [ ] Feedback on fit quality, any visual issues

**Backend Engineer (Dependency):**
- [ ] Ensure database + S3 scale to 30+ garments
- [ ] API performance check (metadata queries fast)

#### Key Milestones
- ✅ 20+ garments in catalogue, searchable
- ✅ All garments test on web viewer
- ✅ Zero critical bugs blocking user try-on

---

### Week 8: Polish, Testing, Final Push to 50+

#### Goals
- Add final 15-20 garments to reach 50+ target
- Comprehensive testing and bug fixes
- Documentation and handoff to Phase 2
- Internal demo + feedback

#### Deliverables

**Clothing Lead:**
- [ ] Complete garment catalogue (50+ items)
- [ ] Final QA sweep (visual inspection, fit validation)
- [ ] Known issues + workarounds document
- [ ] Handoff doc for Phase 2 (cloth sim priorities)

**All Teams:**
- [ ] Integration testing (end-to-end: user scans body → tries on garment)
- [ ] Performance profiling
- [ ] Bug fixes and polish

#### Key Milestones
- ✅ 50+ garments in live catalogue
- ✅ Demo works smoothly (no crashes, good UX)
- ✅ Ready for Phase 2 planning

---

## Dependency Matrix

### Clothing Lead Dependencies

| Dependency | Provider | Timing | Risk | Mitigation |
|------------|----------|--------|------|-----------|
| **Reference T-pose body** | Blender Lead | Week 1-2 | High | Start with placeholder body if delayed |
| **Animation skeleton** | Blender Lead | Week 3-4 | High | Use simple IK skeleton temporarily |
| **Test body scans** | 3D Scanning Lead | Week 4 | Medium | Request early, use synthetic bodies if needed |
| **Animation library** | Blender Lead | Week 5 | Low | Start with walk cycle only |
| **Partner portal API** | Backend Lead | Week 6 | High | Implement simple endpoint early, iterate |
| **S3 + PostgreSQL** | Backend/DevOps | Week 1 | Medium | Use local disk + SQLite if cloud delayed |
| **Garment sourcing** | CEO/Product | Week 6+ | High | Personal outreach, offer early-access deals |

### Clothing Lead Provides To Others

| Team | Dependency | Timing | Notes |
|------|------------|--------|-------|
| **Blender Lead** | Fitted garment meshes | Week 5+ | Pre-fitted, ready to bind to skeleton |
| **Frontend Engineer** | GLB files, LOD variants | Week 5+ | Optimized for web, tested in viewer |
| **Backend Engineer** | Garment metadata schema | Week 1 | JSON schema for database |
| **3D Scanning Lead** | Fitting test feedback | Week 4+ | How fits look on diverse bodies |

---

## Critical Path Analysis

**Critical Path (longest dependency chain):**

1. **Week 1:** Garment data model finalized
2. **Week 1-2:** Reference body from Blender Lead ← **DEPENDENCY BLOCKER**
3. **Week 2-3:** Fitting algorithm development
4. **Week 3-4:** Fitting validation on diverse bodies ← **Needs scanning lead**
5. **Week 5:** Animation integration ← **Needs animation library**
6. **Week 5-6:** Web viewer integration ← **Needs frontend**
7. **Week 6+:** B2B onboarding ← **Needs backend API**
8. **Week 6-8:** Garment catalogue build (parallel with B2B)

**Slack (non-critical, can delay without blocking MVP):**
- Cloth simulation (Phase 2)
- Advanced animations (Phase 2)
- Performance optimization beyond MVP targets

---

## Risk Register

### Risk 1: Reference Body Not Ready by Week 2

**Probability:** Medium  
**Impact:** High (blocks fitting)

**Mitigation:**
- Start with synthetic placeholder body
- Coordinate with Blender Lead early (Week 1 kickoff)
- If delayed, use simple T-pose mesh + manual rigging

---

### Risk 2: Partner Sourcing Slow

**Probability:** Medium  
**Impact:** Medium (delays garment sourcing)

**Mitigation:**
- Start recruitment early (Week 5, not Week 6)
- Prepare 3-5 prospect brands in Week 1
- Offer incentives (free integration, early-access platform)
- Use internal design team to create test garments if needed

---

### Risk 3: Fitting Algorithm Doesn't Work Well on Diverse Bodies

**Probability:** Medium  
**Impact:** High (may require algorithm redesign)

**Mitigation:**
- Test extensively in Week 4 (10+ body types)
- Have fallback: manual lattice adjustment per garment
- Plan for iteration loop (Week 4-5)
- If critical, escalate to design review

---

### Risk 4: Web Viewer Integration Slower Than Expected

**Probability:** Low  
**Impact:** Medium (delays launch)

**Mitigation:**
- Coordinate with Frontend Engineer early (Week 2-3)
- Provide test GLB files for validation
- Batch testing (5 garments, then 20, then full set)

---

### Risk 5: Cloth Simulation Too Complex for Phase 2

**Probability:** Low  
**Impact:** Low (not in MVP scope)

**Mitigation:**
- Phase 1 launches without cloth sim
- Keep static fitting as production path
- Phase 2 can be optional enhancement

---

## Success Metrics (End of Week 8)

| Metric | Target | Status |
|--------|--------|--------|
| Garment catalogue size | 50+ garments | Measure at Week 8 |
| Import success rate | >95% of submissions | Auto-validated |
| Fitting quality | <10% clipping | Visual QA |
| Fit accuracy | ±1 size category | Test on diverse bodies |
| Processing time | <5 min per garment | Benchmark |
| Partner onboarding | <30 min per brand | Time from contact to submission |
| Documentation | >90% complete | API, schema, tuning guide |
| Integration test | End-to-end demo works | Scan → try-on → success |

---

## Phase 2 Planning (Weeks 9-12, future)

**If Phase 1 succeeds and user feedback is positive:**

- [ ] Add cloth simulation (pre-baked, pose-space blending)
- [ ] Fabric parameter tuning for 50+ garments
- [ ] Performance profiling and optimization
- [ ] Partner feedback loop (QA improvements)

**If Phase 1 needs rework:**

- [ ] Focus on fixing critical bugs
- [ ] Delay Phase 2 until Phase 1 stable
- [ ] Replan roadmap with CEO

---

## Communication Plan

### Weekly Sync (Mondays 10 AM)

**Attendees:** Clothing Lead + Blender Lead + Backend Lead + Frontend Lead + CEO

**Agenda (30 min):**
1. Status updates (blockers, progress)
2. Dependency check (anyone waiting on someone else?)
3. Risk review (any new risks?)
4. Decisions needed (from CEO)

### Ad-Hoc Dependencies

**If Clothing Lead needs:**
- Reference body → **Message Blender Lead directly, same day**
- API endpoint → **Message Backend Lead, provide spec, agree on deadline**
- Test bodies → **Message 3D Scanning Lead, provide format**
- Viewer integration → **Message Frontend Lead, provide test GLB + expected perf**

### Status Reporting

**Friday 4 PM:** Clothing Lead sends status to CEO
- What got done this week
- Blockers (if any)
- Next week plan
- Metrics (garments imported, fit quality, etc.)

---

## Hand-Off to Phase 2

**When Phase 1 is Complete (Week 8+):**

1. **Handoff Document:**
   - 50+ garment catalogue (metadata + 3D models)
   - Known issues + workarounds
   - Fitting algorithm performance baseline
   - Partner feedback summary

2. **Code Repository:**
   - Import scripts (CLO3D, MD, OBJ)
   - Fitting algorithm + tests
   - Validation harness
   - Documentation + examples

3. **Phase 2 Priorities (to CEO):**
   - Cloth simulation worth doing? (user feedback)
   - Partner feedback on garment quality
   - Technical debt to address
   - Recommended next steps

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Review:** Weekly during Phase 1 execution
