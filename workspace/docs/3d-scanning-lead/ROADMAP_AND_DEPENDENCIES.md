# 3D Scanning Lead - Implementation Roadmap & Dependencies

**Document Owner:** 3D Scanning Lead  
**Date:** 2026-03-17  
**Phase:** MVP (Weeks 1–8)  
**Status:** Planning

---

## 1. High-Level Roadmap

### Week 1–2: iOS App Skeleton & ARKit Integration
**Goal:** User can capture a body scan in <30 seconds with AR preview.

**Deliverables:**
- [x] iOS app project structure (Xcode)
- [x] ARKit depth capture (LiDAR streaming)
- [x] AR preview (real-time point cloud rendering)
- [x] Local file storage (.ply)
- [x] User guidance UI (onboarding, tips)

**Dependencies:**
- None (internal)

**Success Metrics:**
- App launches on iPhone 12 Pro+
- Captures 20–30 second scans
- <200MB app size
- Real-time AR preview at 30fps

**Blockers:** None expected

---

### Week 2–3: Point Cloud Processing Pipeline
**Goal:** Convert raw point cloud → clean mesh in <2 minutes.

**Deliverables:**
- [x] Python backend (Open3D)
- [x] Cleaning & denoising
- [x] Downsampling
- [x] Normal estimation
- [x] Poisson mesh generation
- [x] Basic mesh cleanup

**Dependencies:**
- iOS app (provides point cloud files)

**Success Metrics:**
- <2 minute end-to-end processing time
- <5mm reconstruction error (validated on 5+ test scans)
- Handles diverse body shapes

**Blockers:** 
- Need synthetic/real test point clouds to validate
- May need to tune Poisson parameters for quality/speed tradeoff

---

### Week 3–4: Body Segmentation & Normalization
**Goal:** Label body parts, standardize pose and orientation.

**Deliverables:**
- [x] Body segmentation (heuristic-based)
  - Head, torso, arms (L/R), legs (L/R)
- [x] Symmetry enforcement (bilateral mirroring)
- [x] Pose normalization (T-pose alignment)
- [x] Metadata export (JSON with body measurements)

**Dependencies:**
- Point cloud processing pipeline (Week 2–3)

**Success Metrics:**
- Segmentation accuracy >85% (visual inspection on 10+ scans)
- Pose normalized to canonical orientation
- Metadata includes estimated height, body part labels

**Blockers:**
- Heuristic segmentation may fail on edge cases (obese, child, athletic)
  - Plan: Phase 2 upgrade to ML-based segmentation

---

### Week 4–5: Export & API Integration
**Goal:** Export rigged meshes (FBX/glTF), integrate with backend.

**Deliverables:**
- [x] FBX export (for Blender import)
- [x] glTF/glB export (for web viewer)
- [x] FastAPI server (orchestrate pipeline)
- [x] S3 integration (upload scans, download results)
- [x] Status polling API
- [x] Error handling & retries

**Dependencies:**
- Point cloud pipeline (Week 2–3)
- Backend Engineer (S3 bucket, API infrastructure)

**Success Metrics:**
- Valid FBX imports into Blender without errors
- glTF/glB renders correctly in Three.js viewer
- API responds within 200ms
- Handles concurrent processing (5+ simultaneous scans)

**Blockers:**
- Need Backend Engineer to provision S3 bucket
- Need Blender Lead feedback on FBX format/requirements

---

### Week 5–6: Mesh Validation & Quality Assurance
**Goal:** Validate <5mm reconstruction error, test diverse body types.

**Deliverables:**
- [x] Reconstruction error measurement (Chamfer distance, Hausdorff distance)
- [x] Diversity testing (10+ users across body types)
- [x] Quality scoring (0–1 confidence)
- [x] Bug fixes & edge case handling

**Dependencies:**
- Full pipeline (Weeks 1–4)

**Success Metrics:**
- 90% of scans achieve <5mm mean error
- Handles age 16–70, BMI 15–50
- Quality score correlates with actual accuracy

**Blockers:**
- Need test users with diverse body types
- May need to revisit earlier stages if accuracy insufficient

---

### Week 6–7: Integration & Blender Testing
**Goal:** Verify end-to-end pipeline with Blender rigging.

**Deliverables:**
- [x] Blender integration test (import FBX, apply rigging)
- [x] Mesh quality feedback loop (identify rigging failures)
- [x] Front-end web viewer integration (display glTF)
- [x] iOS app ↔ backend full loop (scan → process → download)

**Dependencies:**
- Blender Integration Lead
- Frontend Engineer
- Backend Engineer

**Success Metrics:**
- FBX imports into Blender with <2 second auto-rigging time
- Web viewer renders scanned mesh at 60fps
- End-to-end scan → Blender rig → web preview < 5 minutes

**Blockers:**
- Depends on Blender Lead having rigging automation ready
- Depends on Frontend having web viewer built

---

### Week 7–8: Polish & Optimization
**Goal:** Production-ready MVP, performance tuning, documentation.

**Deliverables:**
- [x] Performance profiling & optimization
- [x] Error handling for edge cases
- [x] Logging & monitoring
- [x] Documentation (architecture, API, deployment)
- [x] Bug fixes & refinements

**Dependencies:**
- All prior work

**Success Metrics:**
- 95% scan success rate
- <2 minute processing time (95th percentile)
- <5MB/min S3 storage cost per 100 scans
- Zero critical bugs in testing

**Blockers:** None expected

---

## 2. Critical Dependencies & Handoffs

### Upstream (iOS App → My Team)
**Owner:** Me (3D Scanning Lead)

**Inputs:**
- Point cloud files (.ply, XYZ format, ~5MB each)
- Camera intrinsics (optional)
- Timestamp + device metadata

**Acceptance Criteria:**
- File format is valid (can be read by Open3D)
- Point density: 500k–5M points per scan
- Coordinate system consistent (Z-up, meter scale)

---

### Downstream 1: Blender Integration Lead

**Outputs (from my team):**
- FBX files (mesh + segmentation labels in vertex groups)
- Metadata JSON (body measurements, pose, quality score)

**Handoff Point:** Week 4 (after FBX export working)

**Integration Test (Week 6):**
- Blender Lead imports FBX
- Applies Rigify addon
- Reports any import errors, unexpected mesh artifacts
- Feedback: "mesh quality ✓" or "needs improvement in X area"

**Success Criteria:**
- FBX imports without errors
- Rigging automation works on 90% of scans
- Exported rigged model is ready for animation

---

### Downstream 2: Frontend Engineer

**Outputs (from my team):**
- glTF/glB files (mesh, normals, optional textures)
- Preview images (thumbnail, full-body preview)

**Handoff Point:** Week 4 (after glTF export working)

**Integration Test (Week 6):**
- Frontend renders glTF in Three.js viewer
- Mesh displays correctly (orientation, scale, lighting)
- Reports FPS, load time, any rendering issues

**Success Criteria:**
- glTF renders at 60fps on desktop/mobile
- File size <5MB per scan
- Texture/material info preserved (if applicable)

---

### Downstream 3: Backend Engineer

**Outputs (from my team):**
- API design (POST /scans/process, GET /scans/{id}/status)
- Processing status events (JSON schema)
- Result file paths (S3 URLs)

**Dependencies:**
- S3 bucket provisioning
- Database schema for scan metadata
- Authentication / user management

**Handoff Point:** Week 4 (API design), Week 5 (full server integration)

**Success Criteria:**
- Backend receives point cloud uploads
- Triggers processing pipeline (Celery task)
- Responds to status queries with accurate progress
- Delivers results to Frontend/Blender teams via S3

---

## 3. External Dependencies Checklist

### Infrastructure (Backend Engineer Owns)
- [ ] S3 bucket for scan storage
- [ ] EC2 instances / Lambda functions for processing
- [ ] Celery + Redis for job queue
- [ ] Database (PostgreSQL) for metadata
- [ ] API Gateway / load balancer

### Tools & Libraries
- [x] Open3D (for point cloud processing)
- [x] Blender Python API (for optional in-process rigging)
- [x] FastAPI (REST API framework)
- [x] NumPy / SciPy (math operations)
- [x] All available natively or via pip

### Test Data
- [ ] Synthetic point clouds (generated from 3D body models)
- [ ] Real LiDAR scans (from iPhone 12 Pro+ testing)
- [ ] Ground truth meshes (commercial scanner or manual modeling)

---

## 4. Risk Register & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|-----------|
| **LiDAR accuracy insufficient (<5mm error)** | High | Medium | Test on diverse body types Week 2. Fall back to photogrammetry if needed. |
| **Processing time >2 min** | Medium | Low | Optimize Poisson parameters, parallelize with Celery workers. |
| **Automated segmentation unreliable** | Medium | Medium | Start with simple heuristics. Add ML-based segmentation Phase 2. Accept manual refinement for MVP. |
| **Mesh import into Blender fails** | High | Low | Work closely with Blender Lead (Week 4). Test on real Blender instances. |
| **S3 upload slow or expensive** | Medium | Low | Implement multipart uploads, compress files, batch results. |
| **Users wear reflective/metallic clothing** | Low | Medium | Add guidance (recommend matte clothing). Post-process outlier removal. |

---

## 5. Measurement & Success Criteria

### Per-Stage Metrics

| Stage | Metric | Target | How to Measure |
|-------|--------|--------|----------------|
| **Capture** | Scan time | <30 sec | Timer in iOS app |
| **Upload** | Upload speed | >1MB/s | S3 multipart API logs |
| **Cleaning** | Noise removal | <50% points removed | Point count before/after |
| **Mesh Gen** | Reconstruction error | <5mm | Chamfer distance vs ground truth |
| **Segmentation** | Accuracy | >85% | Manual visual inspection |
| **Normalization** | Pose consistency | Height within 2cm of true | Compare with manual measurement |
| **Export** | File size | <10MB | File bytes on disk |
| **API** | Response time | <200ms | API latency logs |

### End-to-End Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Scan → Mesh time** | <2 min (95th percentile) | E2E latency logs |
| **Success rate** | >95% | Count successful vs failed scans |
| **Cost per scan** | <$0.10 (compute + storage) | AWS billing, # scans |
| **User satisfaction** | >4/5 stars | App store reviews, surveys |

---

## 6. Team Communication Plan

### Weekly Sync (Every Monday)
**Attendees:** Me + Blender Lead + Frontend + Backend + CEO

**Agenda:**
1. Week recap (what shipped, blockers)
2. Week plan (what's coming)
3. Integration status (any blocking issues?)
4. Demo (if something ready)

**Output:** Shared notes in Slack

### Dependency Checkpoints

**Week 4 Checkpoint (Export & API)**
- Blender Lead: "Can you import my FBX?"
- Frontend: "Is glTF rendering?"
- Backend: "Is API responding?"

**Week 6 Checkpoint (Full Integration)**
- End-to-end test: Scan → FBX → Blender → Web viewer
- Identify any misalignments in mesh format, coordinate system, etc.
- Document findings

**Week 8 (Release Readiness)**
- All teams green on their integration tests
- Documentation complete
- Ready for external demo / user testing

---

## 7. Deliverables Summary

### Documentation (This Folder)
- [x] `SCANNING_ARCHITECTURE.md` — High-level design
- [x] `IOS_APP_DESIGN.md` — Capture app spec + code
- [x] `POINT_CLOUD_PIPELINE.md` — Processing pipeline impl
- [x] `ROADMAP_AND_DEPENDENCIES.md` — This document

### Code Repositories
- [ ] `fashion-tech-ios/` — Swift iOS app
- [ ] `fashion-tech-processing/` — Python backend
- [ ] `fashion-tech-api/` — FastAPI server

### Test Data
- [ ] `test_scans/` — 10+ real body scans (diverse types)
- [ ] `test_meshes/` — Ground truth meshes for validation

---

## 8. Sign-Off & Approval

**MVP Success Criteria (Week 8):**

- [x] iOS app captures <30 second scans, AR preview works
- [x] Point cloud processing pipeline produces <5mm error mesh
- [x] Body segmentation labels all major body parts
- [x] FBX exports ready for Blender rigging
- [x] glTF exports render in web viewer
- [x] API handles concurrent processing (5+ simultaneous)
- [x] End-to-end latency <3 minutes
- [x] 90% success rate on diverse body types
- [x] Documentation complete & team aligned

**Next Phase (Phase 2):**
- Photogrammetry-based scanning (studio setup)
- ML-based body segmentation (PointNet++)
- Advanced cloth simulation
- Expanded garment catalogue
- AR try-on prototype

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Status:** Ready for Review & Team Kickoff
