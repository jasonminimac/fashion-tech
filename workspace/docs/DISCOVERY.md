# Fashion Tech Discovery & Architecture Document

**Date:** 2026-03-17  
**Status:** Discovery Phase — Updated Post-Founder Decisions  
**Document Owner:** Fashion Tech CEO  
**Last Updated:** 2026-03-18 (v2.1 — reflects dual-track scanning + AI enhancement decisions from 2026-03-18)

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-17 | Initial discovery document |
| 2.0 | 2026-03-17 | Updated to reflect all founder decisions: B2C+B2B, US/UK first, AR in MVP, platform-owned data, Zara/H&M targets, tooling = best tool wins, mixed garment categories from launch |
| 2.1 | 2026-03-18 | Dual-track scanning (iPhone + in-store kiosk), AI enhancement tools, Zara/H&M prepare-only outreach locked in |

---

## Executive Summary

Fashion Tech is building a 3D body scanning and virtual fashion try-on platform. Users scan their bodies using mobile devices (iPhone LiDAR or photogrammetry), generate a realistic 3D model, and try on garments from a curated catalogue — including from major retail partners (Zara, H&M). The platform serves both B2C consumers and B2B retailers.

**Key decisions locked in as of 2026-03-17:**
- Revenue model: **Both B2C and B2B**
- Launch markets: **US and UK first**, then global
- Target retail partners: **Zara, H&M** and major consumer chains
- AR try-on: **In MVP scope** (with defined go/no-go milestone)
- Body scan data: **Platform-owned** — retailers access via API only
- Garment categories: **Mixed from day one** (structured, draped, stretch)
- Tooling: **Best tool wins** — Blender, Unreal Engine, CLO3D, AI enhancement — whatever produces most realistic output
- First users: **Fashion-forward early adopters** to generate buzz, then broader market

---

## 1. Product Vision & Requirements

### Core Functionality

**User Journey:**
1. **Body Capture:** User scans their body using iPhone LiDAR or photogrammetry on mobile
2. **3D Model Generation:** Scanned geometry is processed, rigged, and stored on platform
3. **Garment Selection:** User browses the Fashion Tech garment catalogue (Zara, H&M, others)
4. **Virtual Try-On (AR or 3D):** Selected garments applied to body model — AR camera overlay in MVP or 3D viewer fallback
5. **Outfit Building:** User creates complete looks, saves them, compares options
6. **Purchase Decision:** Buy via retailer link; user's body scan stored on platform, usable across any partner retailer

### Dual Revenue Model

**B2C:**
- Subscription or freemium app (users pay for premium scanning, outfit history, advanced features)
- Fashion-forward early adopters — they generate buzz, social sharing, influencer pull

**B2B:**
- Retailers (Zara, H&M, etc.) pay for API access to the virtual try-on platform
- Integration into retailer's own app/web via our SDK
- Retailers reduce returns; users get consistent sizing across brands
- Platform data moat: body scan data owned by us — retailers never own the underlying scan

### Product Scope (REVISED)

**MVP (Months 1-2):**
- Body scanning via iPhone LiDAR AND photogrammetry (evaluate realism, pick winner at MVP)
- Automated rigging (best tool: Blender Rigify, MetaHuman, or ML pipeline)
- Garment fitting with mixed categories (structured + draped + stretch)
- **Real-time AR try-on** (camera overlay — go/no-go milestone at Week 6)
- Fallback: high-quality 3D viewer if AR doesn't meet quality bar
- Web/mobile interface for outfit visualization
- Platform data architecture: user scans owned by platform, retailers read-only via API

**Phase 2 (Months 3-4):**
- B2B retailer API (Zara/H&M integration SDK)
- Advanced cloth physics (full CLO3D-quality simulation)
- Expanded animation library
- Multi-device scanning (photogrammetry studio setup)

**Phase 3 (Months 5-6):**
- Global rollout (EU, APAC)
- Social features (outfit sharing, trend discovery)
- Recommendation engine (body type + preference based)
- Manufacturer self-service garment upload portal

---

## 2. Technical Architecture

### High-Level System Design

```
[Mobile Device: LiDAR / Photogrammetry]
          ↓
[Body Scan Processing: Open3D + ML cleanup]
          ↓
[Rigging Pipeline: best-tool (Blender Rigify / MetaHuman / custom)]
          ↓
[Platform Body Data Store — user-owned, platform-managed]
          ↓ (API)                              ↓ (retailer API)
[Consumer App: AR Try-On]            [B2B Retailer SDK / API]
          ↓
[Garment Engine: CLO3D / Blender cloth sim]
          ↓
[Purchase: Retailer deep-link]
```

### 2.1 Body Scanning Pipeline

**Capture Methods (DUAL TRACK — both supported, evaluate trade-offs at MVP milestone):**

**Consumer Path (Home):**
- **iPhone LiDAR:** ARKit 5+ depth capture, iPhone 12 Pro+
- **Photogrammetry:** Multi-angle image capture on any smartphone (fallback for non-LiDAR devices)
- **Timeline:** Primary MVP path (Weeks 1–4)
- **Success metric:** <5mm reconstruction error vs. manual measurement

**In-Store Path (Retail Locations — PARALLEL WORKSTREAM):**
- **Method:** Structured light or depth camera kiosk installed in flagship retail stores (Zara, H&M, boutiques, NYC/London/LA)
- **Timeline:** Parallel development starting Week 3–4
- **Success criteria:** **Accuracy should exceed iPhone LiDAR** (target <3mm error) if feasible. If not materially better, defer kiosk to Phase 2.
- **User journey:** Scan in-store → instant recommendations → AR try-on at home → purchase
- **Why this:** Solves chicken-and-egg (scan available in-store for new users), premium experience, B2B credibility, rich data (full-body + texture + posture)

**Processing Steps (Both Tracks):**
1. Raw depth/image capture (ARKit, photogrammetry, or kiosk)
2. Point cloud cleanup (Open3D: noise removal, gap fill, denoise)
3. Mesh generation (Poisson reconstruction or Ball Pivoting)
4. Body segmentation (semantic ML — head/torso/arms/legs)
5. **AI Enhancement** (NEW): Apply neural reconstruction + mesh refinement
   - NeRF-style reconstruction (novel view synthesis to improve from sparse angles)
   - AI super-resolution + texture upsampling (e.g., Stable Diffusion ControlNet)
   - Artifact removal and mesh optimization
6. Symmetry enforcement + artifact cleanup
7. Pose normalization (A-pose for consistent rigging)
8. Output: clean `.obj` or `.glb` mesh, stored on platform

**Technology Stack:**
- ARKit (iOS) for LiDAR; photogrammetry via RealityCapture (Epic, free tier) or COLMAP
- Open3D / PyVista for mesh processing
- TensorFlow or PyTorch for segmentation
- **AI tools** for enhancement: NeRF frameworks (e.g., Instant NGP, Nerfstudio), Stable Diffusion for texture upsampling
- **In-store kiosk:** RealSense depth cameras or structured light (Intel/Basler/IFM) or Kinect Azure (high accuracy, mature ecosystem)

### 2.2 Rigging & Animation (Best Tool Wins)

See full tooling assessment in TEAM-PROPOSAL.md. Summary:
- **Recommended primary:** CLO3D for garment sim + Blender for rigging/export
- **AR pipeline:** ARKit + RealityKit (native iOS) for real-time AR overlay
- **Unreal MetaHuman:** Evaluated but too heavy for MVP; revisit Phase 2 for cinematic previews

**Rigging Pipeline:**
1. Import cleaned mesh to Blender (or MetaHuman Animator if going UE5 route)
2. Automated skeleton via Rigify + MediaPipe joint detection
3. Weight painting (automated + manual QA pass)
4. Export: `.glb` (web viewer), `.usdz` (iOS AR), `.fbx` (Unreal/game engines)

**Animation:**
- Mixamo base animations (walk, idle, turn) retargeted to custom skeleton
- Blender NLA for animation blending
- `.bvh` for motion data exchange

### 2.3 Garment Scanning & Cloth Simulation

**Garment Sources:**
- CLO3D or Marvelous Designer `.zprj`/`.zpac` files (request from Zara/H&M early — they likely have these)
- Photogrammetry scans of physical garments (fallback for brands without 3D assets)
- 2D pattern → 3D conversion (CLO3D)

**Garment Categories (MVP — mixed from day one):**
- Structured (blazers, denim jackets): rigid-ish, minimal drape
- Draped (silk dresses, blouses): high drape, fabric-weight dependent
- Stretch (leggings, fitted tops): requires elastic simulation

**Cloth Simulation Stack:**
- **CLO3D** for garment authoring + high-quality baked simulation (export `.obj` animation sequences)
- **Blender Cloth Sim** for real-time preview in web viewer (lower fidelity but free/fast)
- **Physics parameters per fabric type:** weight (g/m²), stretch %, bend resistance — stored per garment in DB

### 2.4 AR Try-On (In MVP — with go/no-go milestone)

**Approach:**
- Native iOS: ARKit + RealityKit — render `.usdz` garment model anchored to body pose
- Body tracking: ARKit Body Tracking (available iOS 13+, iPhone XS+)
- Garment draping: pre-baked cloth sim (CLO3D) played back on ARKit skeleton, not real-time physics
- This is the realistic MVP path — "baked AR" not "real-time physics AR"

**Go/No-Go Milestone (Week 6):**
- Criterion: AR garment overlay on live camera at ≥24fps, occlusion handling on arms/body, <200ms tracking lag
- If not met → descope to high-quality 3D viewer (Three.js / model-viewer web component)
- 3D viewer is NOT a failure — it's still a compelling product

**Technology Stack:**
- ARKit + RealityKit (iOS Swift)
- `.usdz` format for AR assets
- SceneKit fallback for non-AR devices
- Web: `<model-viewer>` web component (Google) for 3D preview on desktop/Android

### 2.5 Data Architecture (Platform-Owned Scans)

**Core principle:** Body scan data belongs to the platform. Retailers get a read-only API window.

**Data Model:**
```
User {
  id, auth, preferences
  body_scans: [BodyScan]
  fit_profiles: [FitProfile]   ← derived measurements
  outfit_history: [Outfit]
}

BodyScan {
  id, user_id, created_at
  mesh_url (S3, encrypted)     ← raw scan — NEVER exposed to retailers
  measurements: { chest, waist, hips, inseam, ... }
  scan_method: lidar | photogrammetry
}

FitProfile {
  user_id, brand_id
  size_mapping: { top: M, pants: 32/30, dress: 10 }
  fit_preferences: { fit: slim | regular | relaxed }
}

RetailerAPIAccess {
  retailer_id, user_consent
  readable: [FitProfile]       ← measurements + size mapping only
  NOT accessible: raw mesh, full scan data
}
```

**Retailer API:**
- OAuth 2.0 with user consent per retailer
- Returns: fit profile, size recommendations, fit preference
- Never returns: raw mesh, point cloud, body images
- GDPR/CCPA compliant by design (EU + US data residency)

### 2.6 B2B Retailer Integration

**Target Partners (initial outreach):**
- Zara (Inditex): Check if they have CLO3D files for catalogue — likely yes, they're digitally mature
- H&M: Similar — digitally progressive, likely have 3D assets or can provide them
- Approach: Early conversations to understand their 3D asset pipeline before we build our import tooling

**Integration Options:**
1. **SDK embed:** Retailer drops our JS/Swift/Kotlin SDK into their app → "Try On" button appears on product pages
2. **Standalone app:** Consumer uses our app independently, saves outfits, links to retailer checkout
3. **API-only:** Retailer calls our `/fit-recommendation` endpoint for size suggestions (lowest lift for B2B)

**Garment Onboarding:**
1. Brand submits CLO3D `.zprj` file OR photogrammetry scan
2. Our pipeline validates geometry, extracts fit parameters
3. QA pass (manual + automated): garment renders correctly on 3 body types
4. Published to catalogue with brand metadata

---

## 3. Tooling Assessment (REVISED — Best Tool Wins, AI Enhancement Added)

_Full assessment in TEAM-PROPOSAL.md. Summary here._

**Blender:** Strong for rigging, scripting, export pipeline. Free. Use for body rigging + web/glTF export. **Keep.**  
**CLO3D:** Industry-standard for garment simulation. Zara/H&M likely already use it. Best cloth output. **Adopt as primary garment tool.**  
**Unreal Engine / MetaHuman:** Excellent realism, too heavy for MVP. Consider for marketing renders / cinematic previews. **Defer to Phase 2.**  
**ARKit + RealityKit:** Best-in-class for iOS AR. Free with Apple dev account. **Primary AR stack.**  
**AI Enhancement (NEW):** Apply super-resolution / neural reconstruction to improve scan quality on both iPhone + in-store paths.
- NeRF-style reconstruction (novel view synthesis, e.g., Instant NGP, Nerfstudio)
- Texture super-resolution (Stable Diffusion + ControlNet for upsampling)
- Mesh refinement (artifact removal, symmetry enforcement)
- **Timeline:** Integration begins Week 4–5 (after initial scans generated)
- **Success metric:** Measurable improvement in user fit satisfaction (NPS +1–2 points)
- **Founder note:** Tools like "nanobabana" — AI mesh enhancement frameworks

---

## 4. Open Questions (RESOLVED)

| Question | Decision |
|----------|----------|
| Revenue model | B2C + B2B both |
| Geographic focus | US + UK first |
| Brand partnerships | Zara + H&M as initial targets (prepare outreach, approve before send) |
| Timeline/budget | 6 months, lean/solo build |
| Scanning approach | **DUAL TRACK:** iPhone LiDAR + photogrammetry (MVP) + in-store kiosk (parallel, if accuracy > iPhone) |
| AI enhancement | Apply NeRF + super-resolution to improve both paths |
| Target user | Fashion-forward early adopters first (founder reaches out to TikTok influencers + online community) |
| Garment variety | Mixed categories from day one |
| Blender requirement | NOT a requirement — best tool wins |
| Real-time AR | In MVP scope (with Week 6 go/no-go milestone) |
| Data ownership | Platform owns scan data; retailers get read-only API |
| Zara/H&M outreach | PREPARE ONLY (no sends until founder approval) — develop full comms plan, talking points, deck outline |
| Test user recruitment | DUAL APPROACH: Founder TikTok contacts + online communities (Reddit, Discord) + paid ads (contingent) |

---

## 5. Technical Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| iPhone LiDAR insufficient accuracy | High | Parallel photogrammetry path; quality bar test with 20+ users at Sprint 1 |
| AR try-on fails quality bar | High | Clear go/no-go at Week 6; 3D viewer fallback is compelling on its own |
| Cloth sim too slow for real-time | Medium | Baked CLO3D animation sequences in MVP; real-time physics in Phase 2 |
| Zara/H&M have no 3D assets | Medium | Photogrammetry fallback; offer scanning service as part of partnership |
| Diverse body type rigging failures | High | Test on 10+ body types week 1-2; Rigify + manual QA pass |
| GDPR/CCPA for body scan data | High | Privacy architecture from day one — no raw mesh to retailers, consent model |

---

## 6. Success Metrics

**MVP (Month 2):**
- ✅ End-to-end demo: scan → rigged 3D → AR try-on (or 3D viewer)
- ✅ Scan accuracy: <5mm error vs manual measurement (iPhone path)
- ✅ In-store kiosk evaluation: Compare accuracy vs. iPhone; proceed if >2mm better, otherwise defer to Phase 2
- ✅ AI enhancement: Demonstrate improved scan quality (visual comparison)
- ✅ Pipeline speed: scan → try-on in <5 minutes
- ✅ AR milestone: 24fps+ overlay, <200ms lag (or graceful fallback decision made)
- ✅ Garment types: at least 3 categories (structured, draped, stretch) working
- ✅ Data architecture: body scan stored on platform, retailer API returns fit profile only

**Phase 2 (Month 4):**
- ✅ B2B API live with at least one retailer pilot
- ✅ 50+ garments in catalogue
- ✅ Real-time cloth sim for web viewer

---

**Document Version:** 2.0  
**Last Updated:** 2026-03-17  
**Next Review:** End of Sprint 1 (Week 2)
