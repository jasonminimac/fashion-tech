# 3D Scanning Lead - Quick Reference

**Date:** 2026-03-17  
**Phase:** MVP (Weeks 1–8)

---

## What I Own

**3D Scanning Pipeline:** iOS LiDAR capture → Point cloud processing → Rigged mesh export

- **Input:** User scans body with iPhone 12 Pro+ (20–30 seconds)
- **Output:** FBX (for Blender) + glTF (for web) + JSON (metadata)
- **Success Metrics:** <30s capture, <5mm error, handles diverse body types

---

## The Pipeline

```
1. iOS Capture (Weeks 1–2)
   User → LiDAR → Point Cloud (.ply) → App stores locally

2. Point Cloud Processing (Weeks 2–4)
   Raw cloud → Clean → Downsample → Mesh → Segment → Normalize

3. Export (Weeks 4–5)
   Mesh → FBX + glTF + JSON metadata

4. Validation & Testing (Weeks 5–8)
   Diverse body types, <5mm error, Blender/web integration
```

---

## Key Documents

| Doc | Purpose | Read When |
|-----|---------|-----------|
| `SCANNING_ARCHITECTURE.md` | System design, all subsystems | Planning, architecture review |
| `IOS_APP_DESIGN.md` | iPhone app UI/UX, ARKit integration | Starting app dev |
| `POINT_CLOUD_PIPELINE.md` | Processing algorithms, code samples | Starting backend dev |
| `ROADMAP_AND_DEPENDENCIES.md` | Week-by-week plan, team dependencies | Status tracking, unblocking |
| `QUICK_REFERENCE.md` | This doc | Quick lookup |

---

## Week-by-Week Checklist

### Week 1–2: iOS App
- [ ] Xcode project
- [ ] ARKit LiDAR capture
- [ ] AR preview rendering
- [ ] Local file storage
- [ ] Onboarding UI
- [ ] Upload to cloud

**Deliverable:** Scan → .ply file locally, ready to upload

---

### Week 2–3: Point Cloud Processing
- [ ] Python environment (Open3D, NumPy, etc.)
- [ ] Noise removal
- [ ] Downsampling
- [ ] Normal estimation
- [ ] Poisson mesh generation
- [ ] Mesh cleanup

**Deliverable:** Raw cloud → clean mesh in <2 min

---

### Week 3–4: Segmentation & Normalization
- [ ] Body part segmentation (heuristic)
- [ ] Symmetry enforcement
- [ ] T-pose normalization
- [ ] Metadata export (JSON)

**Deliverable:** Labeled mesh, standardized pose, measurements

---

### Week 4–5: Export & API
- [ ] FBX export
- [ ] glTF export
- [ ] FastAPI server
- [ ] S3 integration
- [ ] Status polling

**Deliverable:** Working API, results in S3

---

### Week 5–6: Quality Assurance
- [ ] Test on 10+ diverse body types
- [ ] Measure reconstruction error (<5mm target)
- [ ] Fix edge cases
- [ ] Quality scoring

**Deliverable:** 90% success rate, <5mm avg error

---

### Week 6–7: Integration Testing
- [ ] Blender FBX import test
- [ ] Web glTF render test
- [ ] End-to-end scan → mesh → viewer
- [ ] Feedback from other teams

**Deliverable:** Working E2E loop

---

### Week 7–8: Polish & Release
- [ ] Performance optimization
- [ ] Documentation
- [ ] Bug fixes
- [ ] Production readiness

**Deliverable:** MVP ready for external demo

---

## Critical Handoff Points

### To Blender Lead (Week 4)
**What:** FBX files + segmentation labels  
**When:** Week 4  
**Check:** "Can you import and rig these?"

### To Frontend (Week 4)
**What:** glTF files + preview images  
**When:** Week 4  
**Check:** "Can you render these?"

### To Backend (Week 4)
**What:** API spec + processing status schema  
**When:** Week 4  
**Check:** "Can you handle concurrent jobs?"

---

## Tech Stack

**iOS:**
- Swift 5.5+, SwiftUI
- ARKit 5, RealityKit
- AWSS3 (S3 upload)

**Processing:**
- Python 3.10+
- Open3D, NumPy, SciPy
- FastAPI (API server)
- Celery + Redis (job queue)

**Output Formats:**
- FBX (Autodesk, for Blender)
- glTF/glB (web standard)
- JSON (metadata)

---

## Success Metrics

| Metric | Target | How |
|--------|--------|-----|
| Capture time | <30 sec | Timer in app |
| Processing time | <2 min | Backend latency logs |
| Reconstruction error | <5mm | Chamfer distance |
| Segmentation accuracy | >85% | Visual inspection |
| Success rate | >95% | Count successful scans |
| Mesh vertices | 100k–200k | Post-export |
| File size | <10MB | Disk size |
| API response | <200ms | Server latency |

---

## Common Pitfalls & Mitigations

| Pitfall | Fix |
|---------|-----|
| LiDAR can't see dark/reflective surfaces | Suggest matte clothing in UI |
| Poisson too slow for large point clouds | Pre-downsample to 200k points |
| Segmentation fails on edge cases (obese, child) | Document constraints, Phase 2 ML upgrade |
| FBX import fails in Blender | Validate format early, work with Blender Lead |
| Processing stalls on large scans | Implement timeouts, quality-based decimation |

---

## Important Constraints

- **Device:** iPhone 12 Pro+ only (LiDAR hardware requirement)
- **Processing:** Must complete in <2 min (user waiting for result)
- **Export:** FBX must be importable by Blender without errors
- **Quality:** <5mm reconstruction error (validates scanning & processing)
- **Diversity:** Must work for ages 16–70, BMI 15–50

---

## Questions? Check These First

**Q: How do I test my code without a real iPhone?**  
A: Use MockARFrame or synthetic point clouds. See POINT_CLOUD_PIPELINE.md for test data generation.

**Q: What if my mesh comes out weird?**  
A: Check voxel size (10mm is default), normal estimation, Poisson depth. Visualize at each stage.

**Q: How do I know if my error is <5mm?**  
A: Compute Chamfer distance against ground truth mesh. See POINT_CLOUD_PIPELINE.md for code.

**Q: Can I ship with Blender as a dependency?**  
A: No (GPL v2 issue). Export FBX and hand off to Blender. Blender Lead does rigging.

**Q: What if processing takes >2 min?**  
A: Reduce voxel size, parallelize with Celery, profile to find bottleneck.

---

## Useful Commands

**Run point cloud pipeline (dev):**
```bash
cd fashion-tech-processing
python pipeline.py --input scan.ply --scan-id test_001 --output-dir ./output
```

**Start FastAPI server (dev):**
```bash
cd fashion-tech-api
uvicorn main:app --reload --port 8000
```

**Test iOS app locally:**
```bash
cd FashionTechScan
xcode-build -scheme FashionTechScan -sdk iphonesimulator
```

---

## Slack Channel
**#fashion-tech-scanning** — Daily updates, blockers, questions

---

## CEO Context
**Product Vision:** Users scan body with iPhone → get rigged 3D model in Blender → try on garments virtually → purchase.

**My Role:** "Capture + process body scans into clean, rigged meshes."

**Success = MVP done in 8 weeks, <5mm error, ready for Blender rigging & web viewer.**

---

**Version:** 1.0  
**Status:** Ready to go!
