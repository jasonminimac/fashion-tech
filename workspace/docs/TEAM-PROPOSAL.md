# Fashion Tech — Team Proposal, Tooling Assessment & Sprint 1 Plan

**Date:** 2026-03-17  
**Author:** Fashion Tech CEO  
**Status:** Ready for founder review  

---

## Part 1: Tooling Assessment

### The Question

Founder decision: tooling = best tool wins. No Blender lock-in. Evaluate Blender, Unreal Engine (MetaHuman), and CLO3D for our three core needs:
1. Body scanning + mesh processing
2. Cloth simulation + garment fitting
3. Real-time AR try-on

---

### Tool Evaluation Matrix

#### 1. Blender

**What it is:** Open-source 3D DCC (Digital Content Creation) tool. Fully scriptable via Python (`bpy`). GPL v2 licensed.

**Body scanning:**
- Not a scanning tool — but excellent for mesh cleanup, rigging, and export
- Rigify addon automates humanoid skeleton generation from placed joints
- Python API allows full pipeline automation (import scan → rig → export)
- Output formats: `.glb`, `.fbx`, `.usdz`, `.obj`, `.abc`

**Cloth simulation:**
- Built-in cloth sim: Decent for static drape previews; too slow for real-time
- Baking cloth to keyframes is feasible (bake once, export as animation)
- Not CLO3D quality — wrinkle/drape realism is noticeably inferior on complex fabrics
- Marvelous Designer import (.obj sequences) works, then render in Blender

**AR try-on:**
- Not an AR tool. Export to `.usdz` for ARKit, but the AR rendering is done elsewhere
- Blender = upstream pipeline, not the AR runtime

**Cost:** Free (GPL — note: if we ship Blender as part of a binary, GPL applies; if we use it as a standalone processing tool on our servers, we're fine)

**Verdict:** ✅ Keep for body rigging + export pipeline. Not for cloth sim or AR.

---

#### 2. Unreal Engine 5 / MetaHuman

**What it is:** Epic's real-time 3D engine. MetaHuman is a hyper-realistic digital human framework (facial rigs, body mesh, hair, skin). Used in film/games.

**Body scanning:**
- MetaHuman Creator accepts photogrammetry input (MetaHuman Animator)
- Can take a video scan → high-quality mesh with facial rigging baked in
- Body rigging quality is exceptional — but designed for standard human proportions
- Custom body scans (non-standard proportions) require significant manual work to integrate

**Cloth simulation:**
- Chaos Cloth (UE5 built-in): Real-time cloth, excellent for games/film
- Can achieve real-time cloth simulation on high-end hardware
- NOT suitable for mobile AR (too compute-heavy for iPhone)
- Excellent for cinematic product visualisation (marketing renders, lookbooks)

**AR try-on:**
- Not a mobile AR framework — UE5 can run on mobile but it's overkill and large binary size
- ARKit integration possible but roundabout; native ARKit/RealityKit is far more appropriate

**Cost:** Free up to $1M revenue, then 5% royalty. Runtime fees changed in 2024 — worth watching.

**Verdict:** ⚠️ Defer to Phase 2. Use case: **high-quality cinematic preview renders** and **marketing assets** for Zara/H&M partnership pitches. Too heavy for MVP AR pipeline.

---

#### 3. CLO3D

**What it is:** Industry-standard garment design and simulation software. Used by Zara, H&M, Nike, and most major fashion houses for virtual sampling.

**Body scanning:**
- CLO3D has its own avatar editor (CLO Avatar) — parametric body sizing
- Can import custom OBJ/FBX body meshes for garment fitting
- NOT a body capture tool — pairs with our ARKit/photogrammetry pipeline

**Cloth simulation:**
- **Best-in-class for fashion.** Fabric physics are physically accurate: weight, stretch, shear, bending
- Handles all garment types: structured (denim, blazers), draped (silk, chiffon), stretch (jersey, spandex)
- Can bake simulation to `.obj` sequence or `.abc` (Alembic) for export
- Native `.zprj` format — Zara/H&M almost certainly have their catalogue in CLO3D already
- This is the key insight: **if our retail partners already use CLO3D, we get their garment assets for free**

**AR try-on:**
- Not an AR tool. Export baked sim as `.abc` → convert to `.usdz` → deploy in ARKit
- CLO3D has a web viewer plugin (CLO-SET Connect) — potential shortcut for web try-on

**Cost:** ~$75/month per seat (subscription). Commercial license required for production use.

**Verdict:** ✅ **Adopt as primary garment simulation tool.** The Zara/H&M native format compatibility alone makes this the right call.

---

#### 4. ARKit + RealityKit (iOS Native)

**What it is:** Apple's AR framework. ARKit handles tracking; RealityKit handles rendering of 3D content in AR.

**AR try-on:**
- ARKit Body Tracking: tracks 91 body joints in real-time on device, iPhone XS+ / iOS 13+
- RealityKit renders `.usdz` or `.reality` assets anchored to body joints
- This is the correct and pragmatic path for MVP iOS AR
- Performance: runs at 30-60fps on iPhone 12+ with simple meshes

**Pipeline:**
1. CLO3D bakes cloth sim → exports `.obj` sequence (e.g., 30 frames of walk cycle)
2. Convert to `.usdz` with animation (Reality Composer Pro or `usdz_converter`)
3. ARKit Body Tracking detects body skeleton
4. RealityKit plays `.usdz` animation anchored to skeleton joints
5. Occlusion handled by ARKit's people occlusion feature

**Cost:** Free (Apple developer account required, $99/year)

**Verdict:** ✅ **Primary AR runtime for MVP.** Best performance, best integration, best tooling on iOS.

---

### Final Tooling Recommendation

| Need | Tool | Rationale |
|------|------|-----------|
| Body scanning capture | ARKit (LiDAR) + COLMAP (photogrammetry) | Native iOS quality, COLMAP for fallback |
| Mesh cleanup + rigging | **Blender** (Python automated) | Free, scriptable, excellent Rigify pipeline |
| Cloth simulation (high quality) | **CLO3D** | Industry standard, Zara/H&M native format |
| Real-time cloth (web preview) | Blender cloth sim (baked) | Fast enough for 3D viewer preview |
| AR try-on runtime | **ARKit + RealityKit** | Native iOS, body tracking, 30-60fps |
| AR asset format | `.usdz` (via Reality Composer Pro) | Apple standard, works in AR Quick Look too |
| Web 3D viewer | `<model-viewer>` web component | Google-backed, works on all platforms |
| Cinematic renders (Phase 2) | Unreal Engine 5 | For marketing, lookbooks, pitch materials |
| Texture enhancement (as needed) | Stable Diffusion / ControlNet | Upscale/enhance low-quality garment textures |

**Pipeline flow:**
```
[iPhone] → ARKit/COLMAP → Open3D cleanup → Blender rigging
                                                    ↓
                                    CLO3D garment sim (→ .obj sequence)
                                                    ↓
                                    Reality Composer Pro → .usdz
                                                    ↓
                                    RealityKit AR overlay on device
                                    OR
                                    model-viewer web component (3D fallback)
```

---

## Part 2: Agent Team Structure

### Philosophy

Lean team for a 6-month solo build. Each agent owns a clear domain. No overlap except at defined handoff points. CEO coordinates; agents execute.

---

### Team Roster

#### 1. CEO / Product Lead
**Session label:** `fashion-tech-ceo`  
**This agent (me)**

**Responsibilities:**
- Strategy, roadmap, founder comms
- Cross-agent coordination and unblocking
- Architecture decisions at integration points
- Sprint planning and milestone tracking
- External: Zara/H&M early conversations (what 3D assets do they have?)

**Deliverables:**
- DISCOVERY.md, TEAM-PROPOSAL.md, sprint plans
- Weekly status to founder
- Go/no-go decisions (AR milestone, tooling pivots)

---

#### 2. Body Scanning Engineer
**Session label:** `fashion-scanning`

**Responsibilities:**
- iOS LiDAR capture app (Swift + ARKit)
- Photogrammetry pipeline (COLMAP integration)
- Point cloud → mesh processing (Open3D, Python)
- Body segmentation (ML: MediaPipe or custom)
- Pose normalization to A-pose
- Output: clean `.obj` mesh + measurements JSON

**Key files/formats:** `.ply` (raw point cloud), `.obj` (processed mesh), `measurements.json`

**Week 1-2 deliverable:** Working iOS app that captures LiDAR scan, exports `.obj` + basic measurements (chest, waist, hip, height)

**Handoff to:** Rigging Engineer (passes `.obj` mesh)

---

#### 3. Rigging & Animation Engineer
**Session label:** `fashion-rigging`

**Responsibilities:**
- Blender automation scripts (Python/`bpy`)
- MediaPipe pose detection → joint positions
- Rigify skeleton generation + weight painting
- Mixamo animation retargeting
- Export: `.glb` (web), `.usdz` (iOS AR), `.fbx` (archive)

**Key files/formats:** `.blend` (working file), `.glb` (web viewer), `.usdz` (AR), `.bvh` (motion data)

**Week 1-2 deliverable:** Script that takes `.obj` body scan → outputs rigged, animated `.glb` in <60 seconds, validated on 3 test body types

**Handoff to:** AR Engineer (`.usdz`), Frontend Engineer (`.glb`)

---

#### 4. Garment & Cloth Simulation Engineer
**Session label:** `fashion-garments`

**Responsibilities:**
- CLO3D garment pipeline (import `.zprj`, run sim, export `.obj` sequence)
- Garment database schema and metadata
- Fabric physics parameters (per garment type)
- `.obj` sequence → `.usdz` animation conversion
- Fitting logic: scale garment to body measurements across sizes
- Initial catalogue: 3 garments (one per category: structured, draped, stretch)

**Key files/formats:** `.zprj` (CLO3D native), `.obj` sequence, `.abc` (Alembic), `garment_metadata.json`

**Week 1-2 deliverable:** One complete garment (t-shirt as structured baseline): CLO3D sim baked, exported as `.obj` sequence, importable into Blender viewer. Garment DB schema drafted.

**Handoff to:** AR Engineer (`.obj` sequence → `.usdz`), Frontend Engineer (garment metadata API)

---

#### 5. AR & Mobile Engineer
**Session label:** `fashion-ar`

**Responsibilities:**
- iOS AR app (Swift, ARKit + RealityKit)
- ARKit Body Tracking integration
- `.usdz` garment placement on body skeleton
- Occlusion handling (people occlusion)
- Performance profiling (60fps target on iPhone 12+)
- **Go/no-go AR milestone at Week 6**
- Fallback: 3D viewer integration if AR doesn't pass milestone

**Key files/formats:** `.usdz`, `.reality` (Reality Composer Pro), Swift source

**Week 1-2 deliverable:** ARKit prototype showing body tracking active, a test cube anchored to hip joint at 30fps+ — proof of concept only, not garment yet

**Handoff to:** CEO for go/no-go decision at Week 6

---

#### 6. Frontend & Backend Engineer
**Session label:** `fashion-platform`

**Responsibilities:**
- Web viewer (`<model-viewer>` component, React wrapper)
- Outfit builder UI (add/remove garments, compare looks)
- Backend API (FastAPI / Node.js): user auth, scan storage, garment catalogue, fit profile
- Database schema (PostgreSQL): users, scans, garments, outfits, retailer access
- S3 storage for scan meshes (encrypted, private by default)
- Retailer API: OAuth 2.0, returns fit profile only (never raw mesh)

**Key files/formats:** TypeScript/React, Python FastAPI, PostgreSQL schema `.sql`, OpenAPI spec `.yaml`

**Week 1-2 deliverable:** Database schema v1 committed. FastAPI skeleton with `/scan`, `/garments`, `/fit-profile` endpoints stubbed. `<model-viewer>` rendering a test `.glb` in browser.

**Handoff points:** Receives `.glb` from Rigging Engineer; receives garment metadata from Garment Engineer; feeds fit profile to AR Engineer

---

### Team Coordination

**Shared repo structure:**
```
fashion-tech/
  pipeline/
    scanning/       ← Body Scanning Engineer
    rigging/        ← Rigging Engineer
    garments/       ← Garment Engineer
  apps/
    ios-ar/         ← AR & Mobile Engineer
    web/            ← Frontend & Backend Engineer
  docs/
    DISCOVERY.md
    TEAM-PROPOSAL.md
    SPRINT-1.md
  assets/
    test-scans/     ← shared test data
    test-garments/  ← shared garment assets
```

**Daily sync:** CEO reviews progress via session check-ins; no standups needed for agent team  
**Milestone reviews:** CEO + relevant agent at end of each sprint week

---

## Part 3: Sprint 1 Plan (Weeks 1-2)

### Goal

Prove the skeleton of the pipeline works, end-to-end. Not polished — functional. By end of Week 2, we should be able to:
1. Scan a body (LiDAR) → get a `.obj` mesh
2. Rig that mesh in Blender → get a `.glb` with walk animation
3. View the `.glb` in a browser
4. See ARKit Body Tracking working on device (placeholder, no garment yet)
5. Have one garment baked in CLO3D, exported, ready to attach

This is the foundation sprint. Every subsequent sprint stacks on this.

---

### Sprint 1 Deliverables

#### Week 1 — Pipeline Foundation

| Agent | Deliverable | Format | Done When |
|-------|-------------|--------|-----------|
| Body Scanning | iOS app v0.1: LiDAR scan → export `.ply` point cloud | `.ply` file | App builds, scans author, exports file |
| Body Scanning | Open3D script: `.ply` → cleaned `.obj` mesh | `.obj` + `measurements.json` | Script runs on 3 test scans without crash |
| Rigging | Blender Python script: `.obj` → rigged skeleton | `.blend` working file | Rigify skeleton auto-placed on scan mesh |
| Garments | CLO3D: baseline t-shirt sim baked (A-pose + walk cycle frames) | `.obj` sequence (30 frames) | Cloth drapes realistically, no clipping |
| AR | ARKit BodyTracking prototype: live camera, 91 joints detected | Swift Xcode project | Console prints joint positions at 30fps |
| Platform | DB schema v1 committed | `schema.sql` | Tables: users, body_scans, garments, fit_profiles, retailer_access |
| Platform | FastAPI skeleton with stubbed endpoints | Python FastAPI | `/health`, `/scan` (POST stub), `/garments` (GET stub) return 200 |

#### Week 2 — Integration & First Loop

| Agent | Deliverable | Format | Done When |
|-------|-------------|--------|-----------|
| Body Scanning | MediaPipe pose detection on mesh: extract 33 joint positions | `joints.json` | Joint positions within 3cm of manual measurement on 3 body types |
| Rigging | Full auto-rig: `.obj` + `joints.json` → rigged + animated `.glb` | `.glb` | Walk cycle plays in model-viewer, no deformation artifacts |
| Rigging | `.usdz` export of rigged body (T-pose, no animation) | `.usdz` | Loads in AR Quick Look on iPhone |
| Garments | Garment DB schema populated: 1 garment (t-shirt) with metadata | DB row + `.obj` sequence stored | Queryable via `/garments` API endpoint |
| Garments | Convert t-shirt `.obj` sequence → `.usdz` with animation | `.usdz` | Loads in Reality Composer Pro without error |
| AR | ARKit prototype v2: render `.usdz` cube anchored to hip joint | Xcode project | Cube tracks hip in real-time at 30fps, people occlusion active |
| Platform | `<model-viewer>` web component renders body `.glb` | React component | Loads `.glb` in browser, spin/zoom works, 60fps on laptop |
| Platform | S3 scan storage: POST `/scan` uploads mesh to S3 | Working endpoint | End-to-end: iOS app → API → S3 → signed URL returned |
| CEO | Sprint 1 retrospective + Sprint 2 plan | `SPRINT-2.md` | Committed to docs/ |

---

### AR Go/No-Go Milestone (Week 6)

**Date:** End of Week 6 (approx 2026-04-28)

**Pass criteria (ALL must be met):**
- [ ] AR garment overlay renders on live camera feed on iPhone 12+
- [ ] ≥24fps sustained (measured with Instruments, not eyeballed)
- [ ] Body tracking lag <200ms (garment follows body movement)
- [ ] People occlusion working (garment goes behind arm when arm crosses body)
- [ ] At least 2 garment types working in AR (one structured, one draped)
- [ ] No major z-fighting or garment blowout on standard indoor lighting

**Fail criteria (any one fails = go to 3D viewer):**
- AR runs at <20fps on iPhone 12+
- Occlusion handling broken or too glitchy for demo
- Garment tracking lag >500ms (looks unnatural)
- Cloth bake looks unrealistic (breaks immersion)

**Fallback plan if AR fails go/no-go:**
- Pivot to high-quality 3D viewer (`<model-viewer>` + Three.js)
- Add manual pose controls (rotate, walk, run)
- This is not a demotion — a photorealistic 3D try-on viewer is still a compelling MVP
- AR moves to Phase 2 roadmap

**Decision authority:** CEO (me) + Founder sign-off required to proceed with AR or formally descope

---

### Sprint 1 Risks

| Risk | Mitigation |
|------|-----------|
| LiDAR scan quality too low for automated rigging | Have photogrammetry path ready by Week 2; test both |
| CLO3D seat not available / license delay | Request trial license immediately; use Blender cloth sim as temporary fallback |
| Mixamo retargeting fails on custom skeleton | Manual bone mapping fallback; CEO to unblock with Rigging agent |
| ARKit Body Tracking not accurate enough on thin/tall bodies | Test on 5 body types Week 1-2; log failure modes |
| Zara/H&M have no CLO3D files | Early recon call; if no 3D assets, plan photogrammetry of physical garments |

---

### Early Partnership Recon (CEO Action — Week 1)

Before we build the garment import pipeline, I need to answer: do Zara and H&M already have CLO3D assets?

**Action items:**
- Research Inditex (Zara parent) and H&M Group digital supply chain tooling
- Both companies have announced digital fashion / virtual sampling initiatives (H&M has used CLO3D publicly)
- Identify contact pathway: API/tech partnerships team at each
- Initial ask: "Do you have CLO3D or Marvelous Designer files for your catalogue? We're building a virtual try-on platform and would like to run a pilot."
- This shapes whether Week 3-4 is "import their CLO3D files" or "photogrammetry their garments"

---

### Sprint 1 Definition of Done

Sprint 1 is complete when:
1. ✅ iOS scan app exports `.obj` mesh (even if messy)
2. ✅ Blender script auto-rigs a scan and exports `.glb` with walk cycle
3. ✅ `.glb` loads and plays in browser (`<model-viewer>`)
4. ✅ ARKit body tracking prototype runs at 30fps on device
5. ✅ One garment in CLO3D sim, baked, exported as `.obj` sequence
6. ✅ DB schema and FastAPI skeleton committed
7. ✅ Sprint 2 plan written

---

**Document Version:** 1.0  
**Date:** 2026-03-17  
**Next update:** End of Sprint 1 (Week 2)
