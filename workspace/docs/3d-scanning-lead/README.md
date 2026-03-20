# Fashion Tech - 3D Scanning Lead Documentation

**Last Updated:** 2026-03-17  
**Status:** MVP Phase (Weeks 1–8)

---

## 👋 Welcome

This is the technical documentation for **Fashion Tech's 3D body scanning pipeline**. I'm the 3D Scanning Lead, and this folder contains everything you need to understand:

1. **Architecture:** How the scanning pipeline works end-to-end
2. **iOS App:** How users capture body scans (20–30 seconds)
3. **Processing:** How raw point clouds become rigged 3D meshes
4. **Roadmap:** Week-by-week plan, dependencies, and success metrics

---

## 📚 Documentation Map

Start here:

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| **QUICK_REFERENCE.md** | Cheat sheet, glossary, quick lookup | Everyone | 5 min |
| **SCANNING_ARCHITECTURE.md** | System design, all components | Engineers, PM | 20 min |
| **IOS_APP_DESIGN.md** | iPhone app UI/UX, implementation | iOS engineer | 30 min |
| **POINT_CLOUD_PIPELINE.md** | Processing algorithms, code samples | Backend engineer | 40 min |
| **ROADMAP_AND_DEPENDENCIES.md** | Week-by-week plan, team handoffs | PM, leads | 15 min |

---

## 🎯 Quick TL;DR

**What do we build?**
- iPhone app that captures LiDAR body scans (20–30 sec)
- Python backend that processes point clouds → rigged 3D mesh (60–120 sec)
- APIs for upload, processing, status polling, and results download

**Who's involved?**
- Me: 3D Scanning Lead (this folder)
- Blender Integration Lead: Takes my FBX meshes, rigs them in Blender
- Frontend Engineer: Takes my glTF meshes, renders in web viewer
- Backend Engineer: Manages S3 storage, API server, processing infrastructure
- CEO: Product vision, strategy, unblocking

**Success looks like:**
- User scans body in <30 seconds
- Mesh generated in <2 minutes
- <5mm reconstruction error
- 90% success rate across diverse body types
- Ready for Blender rigging + web viewer

---

## 🗂️ Folder Structure

```
3d-scanning-lead/
├── README.md (this file)
├── QUICK_REFERENCE.md (glossary, cheat sheet)
├── SCANNING_ARCHITECTURE.md (system design)
├── IOS_APP_DESIGN.md (app UI/UX + code)
├── POINT_CLOUD_PIPELINE.md (algorithms + code)
├── ROADMAP_AND_DEPENDENCIES.md (timeline, handoffs)
│
└── (future: code repositories, test data)
    ├── ../fashion-tech-ios/ (Swift, ARKit)
    ├── ../fashion-tech-processing/ (Python, Open3D)
    └── ../test-data/ (synthetic + real scans)
```

---

## 🚀 Getting Started (Week 1)

### If you're the iOS engineer:
1. Read `QUICK_REFERENCE.md` (5 min)
2. Read `SCANNING_ARCHITECTURE.md` section 3 (iOS) (10 min)
3. Read `IOS_APP_DESIGN.md` thoroughly (30 min)
4. Start Xcode project ✓

### If you're the backend engineer:
1. Read `QUICK_REFERENCE.md` (5 min)
2. Read `SCANNING_ARCHITECTURE.md` section 2 (architecture) (15 min)
3. Read `POINT_CLOUD_PIPELINE.md` sections 1–3 (20 min)
4. Start Python + FastAPI project ✓

### If you're a lead (Blender, Frontend, Backend):
1. Read `QUICK_REFERENCE.md` (5 min)
2. Read `ROADMAP_AND_DEPENDENCIES.md` (15 min)
3. Identify your team's dependencies (handoff points)
4. Schedule weekly sync with me ✓

### If you're the CEO:
1. Read `SCANNING_ARCHITECTURE.md` section 1 (executive summary) (5 min)
2. Read `ROADMAP_AND_DEPENDENCIES.md` (15 min)
3. You're good! ✓

---

## 📅 Timeline at a Glance

```
Week 1–2: iOS App + Capture
  ✓ Goal: User scans in 30 seconds, stores .ply locally
  
Week 2–3: Point Cloud Processing
  ✓ Goal: Raw cloud → clean mesh in <2 minutes
  
Week 3–4: Body Segmentation + Normalization
  ✓ Goal: Label body parts, standardize pose
  
Week 4–5: Export + API Integration
  ✓ Goal: FBX + glTF ready, API responding
  
Week 5–6: Quality Assurance
  ✓ Goal: Validate <5mm error on diverse body types
  
Week 6–7: Integration Testing
  ✓ Goal: E2E test with Blender, web viewer
  
Week 7–8: Polish + Release
  ✓ Goal: MVP ready for external demo
```

---

## 🔄 Key Handoff Points

**Week 4 → Blender Lead:**
- FBX files with mesh + segmentation labels
- Check: "Can you import and auto-rig these?"

**Week 4 → Frontend:**
- glTF files + preview images
- Check: "Can you render these in Three.js?"

**Week 4 → Backend:**
- API design + processing status schema
- Check: "Can you orchestrate processing jobs?"

---

## ✅ Success Criteria (MVP)

By Week 8, we win if:

- [x] iPhone app captures scans in <30 seconds
- [x] Point cloud pipeline produces <5mm error meshes
- [x] Body segmentation works on 90% of scans
- [x] FBX exports are importable by Blender
- [x] glTF exports render in web viewer
- [x] API handles concurrent processing
- [x] <3 minute end-to-end latency
- [x] 90% success rate across diverse body types
- [x] Documentation is complete & team aligned

---

## 🙋 Questions?

### Common Questions

**Q: What's the difference between FBX and glTF?**  
A: FBX is for Blender (desktop), glTF is for web viewers. Both export the same mesh, just different formats.

**Q: Can I test the pipeline without a real iPhone?**  
A: Yes! See POINT_CLOUD_PIPELINE.md for synthetic point cloud generation & testing.

**Q: What happens if a scan fails?**  
A: The app will notify the user to retry. The backend logs the error for debugging.

**Q: How do we validate <5mm error?**  
A: We measure Chamfer distance against ground truth meshes. See POINT_CLOUD_PIPELINE.md section 6.

**Q: What's the cost per scan?**  
A: Target <$0.10 (compute + storage). Mostly compute (S3 is cheap, EC2/Lambda is the cost).

### For more details:
- **Architecture questions** → Read SCANNING_ARCHITECTURE.md
- **Implementation questions** → Read POINT_CLOUD_PIPELINE.md or IOS_APP_DESIGN.md
- **Timeline/blocking** → Read ROADMAP_AND_DEPENDENCIES.md
- **Quick lookups** → Read QUICK_REFERENCE.md

---

## 📞 Communication

**Slack Channel:** `#fashion-tech-scanning`  
**Weekly Sync:** Monday 10am (all teams)  
**1:1s:** As needed, just DM

---

## 🎓 Resources

**Key Libraries:**
- [Open3D Docs](http://www.open3d.org/) — Point cloud processing
- [ARKit Docs](https://developer.apple.com/arkit/) — LiDAR capture
- [Blender Python API](https://docs.blender.org/api/current/) — Mesh import
- [Three.js Docs](https://threejs.org/) — Web 3D viewer
- [FastAPI Docs](https://fastapi.tiangolo.com/) — API framework

**Papers (optional, for deep dives):**
- Poisson Surface Reconstruction ([Kazhdan et al.](https://www.cs.jhu.edu/~misha/MyPapers/SGP06.pdf))
- PointNet++ ([Qi et al.](https://arxiv.org/abs/1706.02413)) — Semantic segmentation

---

## 🚩 Red Flags & Mitigations

| Red Flag | What to Do |
|----------|-----------|
| LiDAR scans look noisy | Check outlier removal settings, voxel size. May need tighter filtering. |
| Mesh generation is slow | Reduce voxel size (10mm default), check Poisson octree depth. |
| Segmentation fails on edge cases | Document constraints (e.g., "works best for BMI 15–45"). Phase 2: ML upgrade. |
| Blender import fails | Validate FBX format early. Work with Blender Lead to debug. |
| Processing takes >2 min | Profile each stage, parallelize with Celery. Reduce quality if needed. |

---

## 💡 Pro Tips

1. **Visualize early & often.** Use Open3D's visualizer (`pcd.paint_uniform_color([0.1, 0.1, 0.1])` → `o3d.visualization.draw_geometries([pcd])`) to debug at each pipeline stage.

2. **Test with synthetic data first.** Generate point clouds from 3D body models before testing with real scans.

3. **Instrument your code.** Log processing times at each stage. Use CloudWatch or similar for production monitoring.

4. **Talk to the other teams early.** Don't wait until Week 6 to discover Blender doesn't like your FBX format.

5. **Save intermediate results.** After each pipeline stage, save the mesh/point cloud. Makes debugging 10x easier.

---

## 📝 How to Use This Documentation

- **First time?** Start with QUICK_REFERENCE.md, then read SCANNING_ARCHITECTURE.md
- **Deep dive?** Read the subsystem docs (IOS_APP_DESIGN.md, POINT_CLOUD_PIPELINE.md)
- **Status tracking?** Check ROADMAP_AND_DEPENDENCIES.md weekly
- **Quick lookup?** Use QUICK_REFERENCE.md for glossary, tech stack, success metrics

---

## 🎉 What's Next?

Once you've read the relevant docs:

1. **Schedule a kickoff call** (30 min) to align on architecture
2. **Set up your environment** (git, dependencies, test data)
3. **Build the first prototype** (Week 1–2)
4. **Get feedback from other teams** (Week 4 handoff point)
5. **Iterate to MVP** (Weeks 5–8)

---

## 📋 Document Versions

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial MVP documentation |

---

**Made with ❤️ by the 3D Scanning Lead**

Questions? Suggestions? Improvements? Let's sync!

---

*Last updated 2026-03-17. Next review after Week 1 prototype.*
