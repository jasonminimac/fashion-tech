# Sprint 1 Brief — Pipeline Skeleton
**Sprint:** 1
**Weeks:** 1–2 (2026-03-18 to 2026-03-29)
**Theme:** Prove every pipeline stage has a working stub. Nothing polished. Everything connected.
**Opened by:** CEO
**Date:** 2026-03-18

---

## Sprint Goal

Build the skeleton of the entire pipeline. By end of Sprint 1, a scan captured on iPhone should produce a `.obj` mesh that flows through auto-rigging into a `.glb` that plays in a browser — and we have ARKit body tracking live on device.

---

## Context

This is Sprint 1 of Phase 1. No prior sprint. We are starting from scratch.

**Founder has approved Phase 1.** Full roadmap is at:
`/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/docs/ROADMAP.md`

**Project environment is at:**
`/Users/Jason/.openclaw/workspace/projects/fashion-tech/`

Full path documentation:
`/Users/Jason/.openclaw/workspace/projects/fashion-tech/PROJECT-PATHS.md`

---

## Assignments

### fashion-scanning
1. iOS scan app v0.1: LiDAR → `.ply` export
   - Swift Xcode project in `apps/ios-ar/scanner/`
   - App builds, scans capture depth, `.ply` file exports to local storage
2. Open3D cleanup script: `.ply` → `.obj` + `measurements.json`
   - Script in `pipeline/scanning/`
   - Runs on 3 synthetic/test scans; chest/waist/hip within 10mm
3. MediaPipe joint detection on mesh
   - Script in `pipeline/scanning/`
   - Outputs `joints.json` (33 landmarks) on 3 diverse body types

### fashion-rigging
1. Blender Rigify auto-rig script: `.obj` + `joints.json` → rigged `.blend`
   - Script in `pipeline/rigging/`
   - Skeleton auto-placed; no manual joint editing needed
2. Blender walk cycle bake + `.glb` export
   - Output `.glb` to `assets/meshes/`
   - Walk cycle plays in `<model-viewer>`; no artifacts on 3 test meshes

### fashion-garments
1. CLO3D: t-shirt sim baked (A-pose + 30-frame walk cycle)
   - `.obj` sequence (30 frames) in `assets/garments/tshirt-sprint1/`
   - Cloth drapes, no clipping, fabric weight = 150g/m² cotton
2. `garment_metadata.json` schema draft
   - File at `pipeline/garments/garment_metadata_schema.json`
   - Fields: id, name, brand, category, fabric_weight, clo3d_file, obj_sequence_path, sizes[]

### fashion-ar
1. ARKit Body Tracking prototype: 91 joints live in console
   - Swift Xcode project in `apps/ios-ar/`
   - Console logs joint positions at ≥30fps on iPhone 12

### fashion-platform
1. DB schema v1: `schema.sql` committed
   - File at `infrastructure/db/schema-v1.sql`
   - Tables: users, body_scans, garments, garment_assets, fit_profiles, outfits, retailer_access
2. FastAPI skeleton: `/health`, `/scan` (stub), `/garments` (stub)
   - App in `apps/api/`
   - All endpoints return 200; OpenAPI spec auto-generated at `/docs`
3. `<model-viewer>` renders test `.glb` in browser
   - React component in `apps/web/`
   - Loads, spins, zooms in Chrome/Safari; 60fps on M1 MacBook

### CEO
1. Sprint 2 plan → `docs/sprints/SPRINT-2-BRIEF.md`
2. Zara/H&M asset recon report → `docs/research/partner-asset-recon.md`

---

## Sprint Done-When

All 12 deliverables checked off. End-to-end loop: iPhone scan → `.obj` → `.glb` plays in browser.

---

## Open Questions

1. CLO3D licence — do we have access? (CEO to confirm)
2. Apple developer account — active? (CEO to confirm)
3. Do we have test `.ply` files or synthetic body meshes to unblock rigging before physical scanning is ready?

---

## Dependencies

- CLO3D licence acquired before Week 1 Day 1
- Apple developer account active
- Specialists should coordinate: scanning produces `.obj` + `joints.json` that rigging consumes

---

## AR Go/No-Go Reminder

The critical AR decision happens at **end of Sprint 3 (Week 6)**. Founder sign-off required. All agents should be aware this milestone is coming.
