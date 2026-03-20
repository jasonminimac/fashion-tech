# Fashion Tech — Complete Product Roadmap

**Version:** 1.0  
**Date:** 2026-03-17  
**Author:** Fashion Tech CEO  
**Status:** Pre-execution — Founder Review Required  
**Horizon:** Week 1 → Week 52 (Month 1 → Month 12)

---

## Table of Contents

1. [Vision & Success Criteria](#1-vision--success-criteria)
2. [Full Phase Plan](#2-full-phase-plan)
3. [Technical Architecture Timeline](#3-technical-architecture-timeline)
4. [AR Go/No-Go Milestone](#4-ar-gono-go-milestone)
5. [Retail Partnership Timeline](#5-retail-partnership-timeline)
6. [Go-to-Market Plan](#6-go-to-market-plan)
7. [Risk Register](#7-risk-register)
8. [Full Sprint List](#8-full-sprint-list)

---

## 1. Vision & Success Criteria

### The Big Picture

Fashion Tech delivers a 3D body scanning and virtual try-on platform. Users scan their body with their iPhone, generate a photorealistic 3D avatar, and try on garments from major retail partners — in AR or a 3D web viewer. The platform is the data layer: we own the body scan. Retailers access fit recommendations via API. Revenue comes from both sides: consumers pay for the app experience; retailers pay for the integration.

### What "Done" Looks Like at Each Milestone

| Milestone | Week | "Done" Looks Like |
|-----------|------|-------------------|
| Pipeline Skeleton | Week 2 | Scan → rigged `.glb` → browser viewer works end-to-end; ARKit body tracking live |
| AR Go/No-Go | Week 6 | AR either passes quality bar (proceed) or fallback formally decided |
| Internal MVP | Week 8 | Full try-on loop: scan → AR (or 3D viewer) → one garment from each category |
| B2B Pilot Readiness | Week 14 | Retailer API live; first partner pilot garment catalogue loaded |
| Public Beta | Week 16 | App live on TestFlight; 200 beta users; feedback loop running |
| B2C Launch | Week 20 | App Store approved; US/UK public launch; press coverage |
| B2B Launch | Week 24 | First paid retailer contract signed; SDK embed live in one partner app |
| Scale & Expand | Week 32+ | 10,000+ active users; 3+ retailer partners; global expansion underway |

### Success Metrics by Phase

**Phase 1 (Weeks 1-8 — Foundation & MVP):**
- Scan → try-on pipeline completes in <5 minutes end-to-end
- Body scan accuracy: <5mm error vs. tape measure on 10 test subjects
- Rigging: no deformation artifacts on 10 body types (diverse BMI, height, gender)
- AR (if pass): ≥24fps, <200ms tracking lag, occlusion working
- 3D viewer (fallback): 60fps desktop, 30fps mobile, `.glb` loads in <3s
- At least 3 garment types (structured / draped / stretch) rendering correctly

**Phase 2 (Weeks 9-16 — Retailer Pipeline & Beta):**
- Garment catalogue: 50+ garments from 2+ brands
- Retailer API: <200ms p95 response on `/fit-profile` endpoint
- CLO3D import pipeline: garment `.zprj` → try-on ready in <30 minutes automated
- Beta cohort: 200 invited users, 60% week-2 retention
- NPS from beta: ≥40

**Phase 3 (Weeks 17-24 — Public Launch):**
- App Store rating: ≥4.3
- B2C: 2,000 active users at 30 days post-launch
- B2B: First retailer contract signed (Zara or H&M pilot deal)
- Return rate signal: pilot retailer reports ≥10% reduction in returns for try-on users
- Press: coverage in at least 2 tier-1 fashion/tech outlets (Vogue Business, TechCrunch)

**Phase 4 (Weeks 25-52 — Scale):**
- 10,000+ MAU (B2C)
- 3+ paying B2B retailer partners
- EU/APAC expansion underway
- Recommendation engine live (body type + preference → garment suggestions)
- Social sharing: 20%+ of outfits shared externally

---

## 2. Full Phase Plan

---

### Phase 1: Foundation & MVP (Weeks 1–8)

**Duration:** 8 weeks (4 sprints × 2 weeks)  
**Goal:** Build the complete pipeline skeleton. Prove scan → rig → garment → AR/3D viewer works end-to-end. Ship an internal demo-ready build.

**Objectives:**
1. iOS scan app capturing body geometry via LiDAR + photogrammetry fallback
2. Automated rigging pipeline: mesh → animated rigged character
3. Garment simulation: CLO3D baked cloth → `.usdz` AR asset
4. AR try-on prototype (go/no-go at Week 6)
5. Platform backend: DB, API, S3 storage — data architecture locked in
6. Internal demo build ready at Week 8

---

#### Sprint 1 (Weeks 1–2): Pipeline Skeleton

**Theme:** Prove every pipeline stage has a working stub. Nothing polished. Everything connected.

**Objectives:**
- iOS LiDAR scan → `.obj` mesh + `measurements.json`
- Blender auto-rig: `.obj` → `.glb` with walk cycle
- CLO3D: one garment baked, exported as `.obj` sequence
- ARKit body tracking proof-of-concept on device
- Backend skeleton: DB schema + FastAPI stubs + `<model-viewer>` in browser

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| iOS scan app v0.1: LiDAR → `.ply` export | `.ply` file | `fashion-scanning` | App builds, scans capture depth, file exports |
| Open3D cleanup script: `.ply` → `.obj` + measurements | `.obj`, `measurements.json` | `fashion-scanning` | Runs on 3 test scans; chest/waist/hip within 10mm |
| MediaPipe joint detection on mesh | `joints.json` (33 landmarks) | `fashion-scanning` | Joint positions output on 3 diverse body types |
| Blender Rigify auto-rig script: `.obj` + `joints.json` → rigged `.blend` | `.blend` | `fashion-rigging` | Skeleton auto-placed; no manual joint editing needed |
| Blender walk cycle bake + `.glb` export | `.glb` | `fashion-rigging` | Walk cycle plays in `<model-viewer>`; no artifacts on 3 meshes |
| CLO3D: t-shirt sim baked (A-pose + 30-frame walk cycle) | `.obj` sequence (30 frames) | `fashion-garments` | Cloth drapes, no clipping, fabric weight = 150g/m² cotton |
| `garment_metadata.json` schema draft | `.json` schema | `fashion-garments` | Fields: id, name, brand, category, fabric_weight, clo3d_file, obj_sequence_path, sizes[] |
| ARKit Body Tracking prototype: 91 joints live in console | Swift Xcode project | `fashion-ar` | Console logs joint positions at ≥30fps on iPhone 12 |
| DB schema v1: `schema.sql` committed | `.sql` | `fashion-platform` | Tables: users, body_scans, garments, garment_assets, fit_profiles, outfits, retailer_access |
| FastAPI skeleton: `/health`, `/scan` (stub), `/garments` (stub) | Python FastAPI | `fashion-platform` | All endpoints return 200; OpenAPI spec auto-generated at `/docs` |
| `<model-viewer>` renders test `.glb` in browser | React component | `fashion-platform` | Loads, spins, zooms in Chrome/Safari; 60fps on M1 MacBook |
| Sprint 2 plan | `SPRINT-2.md` | CEO | Committed to `docs/` |
| Zara/H&M asset recon report | `docs/partner-asset-recon.md` | CEO | Findings on whether they have CLO3D/MD files and contact pathway |

**Dependencies:** CLO3D licence acquired before Week 1 Day 1. Apple developer account active.  
**Done-when:** All 12 deliverables checked off. End-to-end loop: iPhone scan → `.obj` → `.glb` plays in browser.

---

#### Sprint 2 (Weeks 3–4): Pipeline Integration

**Theme:** Connect the stubs. First full pass of the pipeline. Three garment categories started.

**Objectives:**
- Full auto-rig pipeline: scan in → `.glb` + `.usdz` out, no manual intervention
- Garment pipeline: CLO3D sim → `.usdz` with animation
- ARKit: first garment (t-shirt `.usdz`) rendering on body skeleton
- Platform: scan upload → S3 → signed URL working; `/garments` API returns real data
- Photogrammetry path: COLMAP pipeline working as LiDAR fallback

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Blender pipeline: auto weight painting + `.glb` export in <60s | Python script + `.glb` | `fashion-rigging` | Full pipeline runs headless on CI in <60s on 3 body types |
| `.usdz` T-pose body export | `.usdz` | `fashion-rigging` | Loads in AR Quick Look on iPhone without error |
| COLMAP photogrammetry pipeline: 20-photo set → `.obj` | Python wrapper + `.obj` | `fashion-scanning` | Runs in <10 min on 20 images; mesh comparable to LiDAR quality |
| Scan accuracy test: 10 subjects, LiDAR vs tape measure | `accuracy-report.md` | `fashion-scanning` | Mean error <5mm on chest, waist, hip on ≥8/10 subjects |
| CLO3D: draped garment (silk dress) baked — 30 frames | `.obj` sequence | `fashion-garments` | Fabric drape visually convincing; no mesh interpenetration |
| CLO3D: stretch garment (leggings) baked — 30 frames | `.obj` sequence | `fashion-garments` | Stretch deformation correct; 90% coverage of body silhouette |
| `.usdz` t-shirt with animation (walk cycle) | `.usdz` | `fashion-garments` | Converts from `.obj` sequence via `usdz_converter`; animation plays |
| ARKit v2: t-shirt `.usdz` anchored to body skeleton | Xcode project | `fashion-ar` | T-shirt tracks body at 30fps; basic occlusion active (arms over shirt) |
| POST `/scan` → S3 upload → signed URL response | FastAPI endpoint | `fashion-platform` | iOS app sends `.obj`, gets back signed S3 URL; stored in DB |
| GET `/garments` returns real data from DB | FastAPI endpoint | `fashion-platform` | Returns array with t-shirt metadata + asset URL |
| Retailer API v0 spec | `retailer-api-spec.yaml` (OpenAPI) | `fashion-platform` | Draft spec: `/fit-profile`, OAuth 2.0 flow, response schema (NO raw mesh) |
| Sprint 3 plan | `SPRINT-3.md` | CEO | Committed to `docs/` |

**Dependencies:** Sprint 1 complete. CLO3D licence active. 10 volunteer scan subjects arranged (Week 2 action).  
**Done-when:** LiDAR scan → auto-rig → `.usdz` → visible on ARKit body skeleton in <10 minutes end-to-end. All three garment categories have at least one baked asset.

---

#### Sprint 3 (Weeks 5–6): AR Quality Push + Go/No-Go

**Theme:** Maximum effort on AR quality. By end of Week 6: AR milestone decision made. Simultaneously harden the 3D viewer fallback so it's truly compelling regardless of AR outcome.

**Objectives:**
- AR: achieve go/no-go pass criteria OR formally move to 3D viewer path
- 3D viewer: photorealistic quality, pose controls, outfit comparison
- Garment fitting: size scaling logic across S/M/L/XL mapped to measurements
- Performance profiling on target devices

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| ARKit: people occlusion fully working (arm crossing body) | Xcode project | `fashion-ar` | Demonstrated on video, arm occludes garment correctly in 3/3 test scenarios |
| AR performance benchmark: fps + lag on iPhone 12/13/14 | `ar-performance-report.md` | `fashion-ar` | Instruments trace: fps and tracking lag measurements for each device |
| AR: 2nd garment type working (draped dress `.usdz`) | `.usdz` + Xcode | `fashion-ar` | Dress renders on body skeleton, reasonable drape simulation at runtime |
| AR garment size scaling: S/M/L/XL from `measurements.json` | Swift scaling logic | `fashion-ar` | Garment scales correctly to ≥3 body types without clipping |
| 3D viewer: Three.js integration (lighting, shadows, reflections) | React + Three.js component | `fashion-platform` | Photorealistic garment render with IBL lighting, normal maps, PBR materials |
| 3D viewer: pose controls (idle / walk / turn) | React component | `fashion-platform` | Three pose buttons swap animation; transition is smooth |
| 3D viewer: outfit comparison (side-by-side or toggle) | React component | `fashion-platform` | User can add 2 garments to comparison; switch between them |
| Garment fitting algorithm v1: measurement → recommended size | Python service | `fashion-garments` | Given `measurements.json` + garment sizing chart → returns recommended size with confidence score |
| CLO3D: structured garment (blazer) baked — 30 frames | `.obj` sequence | `fashion-garments` | Lapels, structure hold shape; shoulder fit correct on 3 body sizes |
| Scan processing hardened: diverse body types (10 more subjects) | Test results + bugfixes | `fashion-scanning` | Pipeline passes on 18/20 subjects (90%); failure modes documented |
| **AR GO/NO-GO DECISION** | `AR-DECISION.md` | CEO + Founder | Document records pass/fail assessment and chosen path |
| Sprint 4 plan (reflects AR decision) | `SPRINT-4.md` | CEO | Committed to `docs/` |

**Dependencies:** Sprint 2 complete. Performance testing requires physical iPhone 12+ devices.  
**Done-when:** AR go/no-go decision made and documented. 3D viewer is demo-quality regardless of AR outcome. Three garment categories (structured/draped/stretch) all rendering in either path.

---

#### Sprint 4 (Weeks 7–8): Internal MVP

**Theme:** Polish the end-to-end experience into a demo-ready internal build. CEO uses this to pitch retail partners.

**Objectives:**
- Full try-on loop: scan → garment selection → AR/3D viewer → outfit save
- User auth + scan storage (privacy-compliant)
- Internal demo build on TestFlight
- CEO uses demo in first Zara/H&M outreach meeting

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| iOS app: scan → upload → garment selection → try-on full loop | iOS app | `fashion-ar` + `fashion-platform` | Full flow completes without engineer intervention in <5 minutes |
| User auth: Sign In with Apple + email/password | iOS app + FastAPI | `fashion-platform` | Auth flow works; JWT issued; user tied to scan in DB |
| Scan storage: GDPR-compliant S3 (encrypted at rest, user-deletable) | AWS S3 + FastAPI | `fashion-platform` | User can delete their scan; confirmed absent from S3; GDPR deletion endpoint documented |
| Outfit save + history: save look, retrieve across sessions | FastAPI + iOS | `fashion-platform` | User saves outfit; logs out; logs back in; outfit still present |
| Garment catalogue UI: browseable by category, brand, size | React web + iOS | `fashion-platform` | 9 garments (3 per category) visible; filterable; tapping loads try-on |
| Try-on quality: all 9 garments rendering correctly on 5 body types | QA report | CEO | Manual QA pass: <5% body interpenetration across all tests |
| TestFlight build submitted | `.ipa` + TestFlight | `fashion-ar` | CEO + 5 internal testers can install and run full flow |
| Demo script written for Zara/H&M pitch | `docs/retail-pitch-deck.md` | CEO | Script covers: platform value prop, data ownership model, CLO3D asset pipeline, API |
| Sprint 5 plan | `SPRINT-5.md` | CEO | Committed |

**Phase 1 Exit Criteria:**  
✅ End-to-end try-on demo works on TestFlight  
✅ 9 garments in catalogue (3 categories × 3 each)  
✅ AR decision made and documented (pass or formal fallback)  
✅ Body scan accuracy <5mm on 80%+ of test subjects  
✅ CEO has first retail partner meeting booked

---

### Phase 2: Retailer Pipeline & Public Beta (Weeks 9–16)

**Duration:** 8 weeks (4 sprints × 2 weeks)  
**Goal:** Build the B2B integration layer. Scale the garment catalogue. Launch public beta to 200 users.

**Objectives:**
1. Retailer API live (OAuth 2.0, fit-profile endpoint)
2. CLO3D garment onboarding pipeline automated (import → QA → catalogue)
3. 50+ garments live (from 2+ brands or internal library)
4. Public beta: 200 invited users, feedback loop, NPS measurement
5. First retailer pilot agreement in principle

---

#### Sprint 5 (Weeks 9–10): Retailer API & Garment Pipeline Automation

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Retailer API: OAuth 2.0 flow (authorization code grant) | FastAPI + Postgres | `fashion-platform` | Token flow works; scope: `fit_profile:read`; no raw mesh accessible |
| `/v1/fit-profile` endpoint: returns measurements + size mapping | FastAPI | `fashion-platform` | Returns `{ chest, waist, hip, inseam, recommended_sizes: { brand_id: { top: "M" } } }` in <200ms |
| Retailer sandbox environment | Docker compose stack | `fashion-platform` | Retailer dev can hit sandbox API without affecting production data |
| CLO3D garment ingestion script: `.zprj` → validated → sim baked → `.obj` sequence | Python CLI | `fashion-garments` | Runs unattended on any valid `.zprj` file; outputs baked `.obj` sequence in <30 min |
| Garment QA pipeline: automated geometry checks (clipping, UV issues, size coverage) | Python test suite | `fashion-garments` | Catches: intersecting faces, missing UVs, missing size variants; outputs pass/fail JSON |
| Garment catalogue scale: 20 garments (5 per category + extras) | DB + assets | `fashion-garments` | 20 garments queryable via API; all have `.usdz` + `.glb` + `.obj` sequence |
| Retailer garment submission form (web) | React form | `fashion-platform` | Brand can upload `.zprj` or photos; metadata fields; triggers ingestion pipeline |

---

#### Sprint 6 (Weeks 11–12): Beta Prep & Advanced Features

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Photogrammetry garment scanning: physical garment → 3D asset | Python + COLMAP pipeline | `fashion-scanning` | Physical garment photographed from 36 angles → clean `.obj` → passes QA |
| AI texture enhancement: ControlNet upscale on low-res garment textures | Python + Stable Diffusion pipeline | `fashion-garments` | 512×512 input → 2048×2048 enhanced output; visual QA pass |
| Body scan diversity hardening: extended test set (50 subjects, synthetic augmentation) | Updated pipeline | `fashion-scanning` | Pipeline passes on 47/50 diverse body types |
| Outfit recommendation engine v1: body type + preferences → garment suggestions | Python ML service | `fashion-platform` | Given body measurements + saved outfit history → returns ranked suggestions; evaluated offline |
| Social share: outfit link generates shareable image | FastAPI + Sharp (image gen) | `fashion-platform` | Outfit share URL generates OG image with garment on avatar; works in iMessage/Twitter preview |
| Beta invite system: invite codes, onboarding flow | iOS + FastAPI | `fashion-platform` | 200 invite codes generated; onboarding guides user through first scan in <3 min |
| App Store submission prep: screenshots, app description, privacy manifest | App Store assets | CEO + `fashion-ar` | Ready for review submission; privacy nutrition label complete |

---

#### Sprint 7 (Weeks 13–14): Beta Launch & Retailer Pilot

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Public beta live: 200 users on TestFlight | TestFlight | `fashion-ar` | 200 invite codes sent; ≥150 users complete first scan |
| In-app feedback: NPS survey at day 7 | iOS + FastAPI | `fashion-platform` | Survey fires at Day 7 post-scan; responses stored; CEO gets weekly summary |
| Crash monitoring: Sentry integration (iOS + backend) | Sentry | `fashion-ar` + `fashion-platform` | Crashes surface in Sentry with stack trace; CEO alerted on P0 within 15 min |
| Performance dashboard: scan conversion, try-on rate, session length | Internal dashboard | `fashion-platform` | Posthog or Mixpanel events firing; CEO has live dashboard |
| Retailer pilot: CLO3D garment catalogue from Zara OR H&M loaded | 10+ garments | `fashion-garments` + CEO | At least 10 real partner garments live in catalogue (or placeholder with partner agreement signed) |
| B2B pilot agreement: LOI or pilot contract in principle | `docs/partner-loi.md` | CEO | Signed letter of intent or verbal commitment from 1 retail partner to run pilot |
| Garment catalogue: 50 garments total | DB | `fashion-garments` | 50 garments queryable; all categories represented; ≥10 from real brand or licensable source |

---

#### Sprint 8 (Weeks 15–16): Beta Feedback Integration & Scale Hardening

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Beta feedback synthesis: top 5 issues prioritised | `docs/beta-feedback.md` | CEO | Report written; issues triaged; top 5 in Sprint 9 backlog |
| Scan re-scan flow: user can update their body scan | iOS + FastAPI | `fashion-ar` + `fashion-platform` | User can trigger new scan; old scan archived; fit profiles updated |
| Multi-size try-on: user can toggle between recommended and adjacent sizes | iOS + AR/3D viewer | `fashion-ar` + `fashion-platform` | Size toggle UI live; garment re-fits to selected size in <2s |
| Backend load testing: 500 concurrent users simulation | k6 test suite | `fashion-platform` | API handles 500 concurrent requests at p95 <500ms; no errors |
| CDN for garment assets: CloudFront distribution | AWS CloudFront | `fashion-platform` | `.glb` and `.usdz` served via CDN; p95 load time <1s globally |
| iOS app: deep link from retailer product page → try-on | Universal link handler | `fashion-ar` | Tap "Try On" on mock retailer page → app opens to that garment loaded |

**Phase 2 Exit Criteria:**  
✅ 200+ beta users active  
✅ NPS ≥40 from beta cohort  
✅ 50+ garments in catalogue  
✅ Retailer API live (sandbox + production)  
✅ First retailer pilot agreement in principle  
✅ App Store submission ready

---

### Phase 3: Public Launch (Weeks 17–24)

**Duration:** 8 weeks (4 sprints × 2 weeks)  
**Goal:** App Store launch (US + UK). First paid B2B contract. PR campaign.

---

#### Sprint 9 (Weeks 17–18): Pre-Launch Polish

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| App Store review submission | App Store | CEO + `fashion-ar` | Submitted; no rejection flags expected |
| Beta issue fixes: top 5 from beta feedback | iOS + backend | All agents | All 5 issues resolved; regression tested |
| Press kit: product video, screenshots, founder quote | `docs/press-kit/` | CEO | 60-second product demo video; 5 App Store screenshots; 3 PR-ready images |
| Influencer outreach: 10 fashion-forward creators (UK + US) | Outreach tracker | CEO | 10 DMs sent; ≥3 responses; 2 agreed to early access + post at launch |
| Pricing model finalised: B2C tier structure | `docs/pricing.md` | CEO | Free tier (1 scan, 5 try-ons/month), Pro £9.99/mo (unlimited), defined |
| B2B pricing: retailer API tiers | `docs/b2b-pricing.md` | CEO | Tiers: Starter (1,000 API calls/mo, £500/mo), Growth, Enterprise |

---

#### Sprint 10 (Weeks 19–20): Launch Week

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| **App Store approval + public launch (US + UK)** | Live on App Store | CEO | App live, downloadable in US + UK App Store |
| Launch PR: Vogue Business + TechCrunch pitches | Email pitches | CEO | Pitches sent; at least 1 confirmed piece at launch |
| Launch day influencer posts live | Social | CEO | ≥2 influencer posts day of launch |
| Stripe payment integration: Pro subscription live | iOS + FastAPI + Stripe | `fashion-platform` | User can subscribe to Pro; charged correctly; webhook updates DB |
| B2B sales outreach: formal proposal to Zara + H&M partnership teams | Proposal docs | CEO | Formal proposals sent to identified contacts at both brands |
| Launch day monitoring: Sentry + Posthog on war room | Live dashboard | CEO + all agents | All agents on standby; CEO triages issues; P0 SLA = 30 min response |

---

#### Sprint 11 (Weeks 21–22): Post-Launch Iteration

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| Launch metrics report | `docs/launch-metrics.md` | CEO | Downloads, DAU, scan completion rate, NPS at 7 days post-launch |
| Top crash/UX issues from launch week | Sentry + NPS | All agents | Top 3 issues fixed and shipped in hotfix |
| B2C: Android web app (Progressive Web App) | React PWA | `fashion-platform` | PWA installable on Android; `<model-viewer>` 3D try-on works; scan via photogrammetry |
| Garment catalogue expansion: 100 garments | DB + assets | `fashion-garments` | 100 garments live; 30+ from real brand sources |
| B2B: retailer SDK v1 (JS embed) | NPM package | `fashion-platform` | `<script>` embed shows "Try On" button on product page; opens app deeplink or web viewer |

---

#### Sprint 12 (Weeks 23–24): First B2B Contract

| Deliverable | Format | Owner | Done When |
|-------------|--------|-------|-----------|
| **First paid B2B contract signed** | Signed contract | CEO | Legal executed; first invoice issued |
| Retailer SDK embed live in partner app/site | Partner integration | `fashion-platform` + CEO | "Try On" button live on partner product pages in production |
| Partner garment catalogue: 50 garments from first paid retailer | DB + assets | `fashion-garments` | First retailer's garments live in catalogue with brand attribution |
| Return rate tracking: partner integration for order data | Retailer API extension | `fashion-platform` | Partner sends order + return events; we correlate with try-on usage |
| US/UK user metrics at 30 days | `docs/metrics-30d.md` | CEO | 2,000+ active users; cohort analysis written |

**Phase 3 Exit Criteria:**  
✅ App live on App Store (US + UK)  
✅ 2,000+ active B2C users at 30 days  
✅ First B2B contract signed  
✅ 100+ garments in catalogue  
✅ Return rate reduction signal from pilot partner

---

### Phase 4: Scale & Expand (Weeks 25–52)

**Duration:** 28 weeks  
**Goal:** Scale to 10,000+ MAU, 3+ B2B partners, EU/APAC expansion, social features, recommendation engine, marketing renders via Unreal Engine.

#### Key Milestones in Phase 4

| Week | Milestone |
|------|-----------|
| Week 28 | EU expansion (GDPR data residency in AWS eu-west-1) |
| Week 30 | Social features: outfit sharing, explore feed, trend discovery |
| Week 32 | Second B2B retailer contract signed |
| Week 36 | Android native app (Kotlin + AR Core for Android AR) |
| Week 40 | APAC expansion (Japan, South Korea — fashion-forward markets) |
| Week 44 | Recommendation engine v2: collaborative filtering + body type clustering |
| Week 48 | Manufacturer self-service garment upload portal |
| Week 52 | Third B2B retailer contract; Series A preparation materials |

---

## 3. Technical Architecture Timeline

### When Each Component Gets Built

```
Week:  1    2    3    4    5    6    7    8    9    10   11   12   13   14   15   16   20   24
       |----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|

SCANNING
LiDAR iOS capture      [====]
Open3D cleanup         [====]
Photogrammetry COLMAP       [====]
Diversity hardening                              [====]

RIGGING
Blender Rigify script  [====]
MediaPipe joints       [====]
.glb + .usdz export         [====]
Headless CI pipeline        [====]

GARMENT SIM (CLO3D)
T-shirt (structured)   [====]
Draped dress                [====]
Stretch leggings            [====]
Blazer (advanced struct.)        [====]
Garment QA pipeline                         [====]
Auto-ingestion (zprj→usdz)                  [====]
50 garments                                           [====]
100 garments                                                              [====]

AR PIPELINE
ARKit body tracking    [====]
First garment in AR         [====]
Occlusion + perf push            [====]
GO/NO-GO DECISION                     [**WEEK 6**]
AR: pass → full AR MVP                     [====]
AR: fail → 3D viewer polish              [====]

WEB PLATFORM
FastAPI skeleton       [====]
S3 scan storage             [====]
model-viewer component [====]
Three.js photorealistic            [====]
Auth + outfit save               [====]
Full iOS app loop                          [====]

RETAILER API
OAuth 2.0 + spec                            [====]
Sandbox environment                         [====]
Production API                                        [====]
Retailer SDK (JS embed)                                         [====]

BETA / LAUNCH
TestFlight (internal)                          [W8]
Public beta (200 users)                                    [W13]
App Store submission                                              [W17-19]
App Store live (US+UK)                                                       [W20]
First B2B contract                                                                    [W24]
```

### Component Ownership Matrix

| Component | Owner | Live By |
|-----------|-------|---------|
| LiDAR scan app (`apps/ios-ar/scanner/`) | `fashion-scanning` | Week 2 |
| Open3D processing pipeline (`pipeline/scanning/`) | `fashion-scanning` | Week 2 |
| COLMAP photogrammetry (`pipeline/scanning/photogrammetry/`) | `fashion-scanning` | Week 4 |
| Blender rigging scripts (`pipeline/rigging/`) | `fashion-rigging` | Week 2 |
| `.glb`/`.usdz` export pipeline | `fashion-rigging` | Week 4 |
| CLO3D garment sim pipeline (`pipeline/garments/`) | `fashion-garments` | Week 2 (first garment) |
| Garment QA automation | `fashion-garments` | Week 10 |
| ARKit/RealityKit app (`apps/ios-ar/`) | `fashion-ar` | Prototype Week 2, MVP Week 8 |
| FastAPI backend (`apps/api/`) | `fashion-platform` | Skeleton Week 2, full Week 8 |
| React web viewer (`apps/web/`) | `fashion-platform` | Week 2 (`model-viewer`), Week 6 (Three.js) |
| Retailer API (`apps/api/v1/retailer/`) | `fashion-platform` | Week 10 |
| Retailer JS SDK (`packages/retailer-sdk/`) | `fashion-platform` | Week 22 |

---

## 4. AR Go/No-Go Milestone

### Decision Point: End of Week 6 (2026-04-28)

This is the most important single decision in Phase 1. It determines the product experience at MVP.

### Pass Criteria (ALL must be met)

| Criterion | Measurement Method | Threshold |
|-----------|--------------------|-----------|
| Frame rate | Xcode Instruments — GPU frame rate | ≥24fps sustained over 60s test |
| Body tracking lag | Manual measurement: time between movement and garment response | <200ms |
| People occlusion | Manual QA: arm crossing body test, 3 test subjects | Pass in ≥3/3 tests |
| Garment types working | Manual QA: structured + draped both rendered | Both render without blowout/z-fighting |
| Indoor lighting robustness | Test in 3 lighting conditions: bright, dim, mixed | Garment anchors correctly in 3/3 |
| Device compatibility | Test on iPhone 12, 13, 14 | Pass on all 3 devices |

### Fail Criteria (any ONE triggers fallback)

- FPS <20 on iPhone 12 (our minimum supported device)
- Tracking lag >500ms sustained (looks uncanny/broken)
- Occlusion broken: garment floats in front of arm in >50% of frames
- Garment drape visually unconvincing (CEO judgment call + founder sign-off)

### Decision Authority

- CEO makes pass/fail call based on above criteria
- Founder sign-off required if CEO calls it a borderline pass
- Documented in `docs/AR-DECISION.md` within 24h of assessment

### If AR Passes

Roadmap continues as written. Sprint 4 proceeds with full AR MVP build.

Additional AR investment in Phase 2:
- Real-time cloth physics (replace baked sim) — Sprints 9-10
- Unreal Engine cinematic renders for retail pitch materials — Sprint 11-12
- Android AR (ARCore) — Week 36+

### If AR Fails (Fallback Plan)

1. **Immediate:** CEO communicates decision to all agents + founder within 48h
2. **Sprint 4 replanned:** AR effort redirected to 3D viewer quality (Three.js, lighting, poses)
3. **3D viewer becomes the flagship experience:**
   - Photorealistic lighting (IBL, PBR materials)
   - Full pose library (idle, walk, run, turn, sit)
   - Outfit comparison (side-by-side)
   - Virtual catwalk view (animated turntable)
4. **Marketing repositioned:** "Photorealistic 3D try-on" rather than "AR try-on" — still genuinely compelling
5. **AR moved to Phase 3 roadmap** (Weeks 17-24): revisited with more engineering time and potentially custom rendering approach (WebXR, Unity AR Foundation)
6. **No delay to beta or launch** — 3D viewer is production-quality and shippable on the same timeline

### What Does NOT Change If AR Fails

- Launch date unchanged
- Retailer API unchanged
- B2C/B2B business model unchanged
- All scanning + rigging pipeline unchanged
- Garment catalogue unchanged

---

## 5. Retail Partnership Timeline

### What We Need to Show Retailers Before Approaching

Before asking Zara or H&M to sign anything, we need:
1. A working demo of the scan → try-on loop (internal MVP, Week 8)
2. A garment from their brand rendered in our platform (even if using publicly available product images)
3. The data architecture story (CEO-level: "your CLO3D files stay yours; we own the scan data; you get fit profiles via API")
4. A return reduction hypothesis with supporting data from beta

### Timeline

| Week | Action | Owner | Output |
|------|--------|-------|--------|
| Week 1-2 | Research: Zara (Inditex) + H&M digital asset pipeline. Do they use CLO3D? Contact pathway? | CEO | `docs/partner-asset-recon.md` |
| Week 3-4 | Warm outreach: LinkedIn/email to digital innovation teams at both brands | CEO | Initial contact established |
| Week 6 | AR decision made — shapes what demo we show retailers | CEO | `docs/AR-DECISION.md` |
| Week 8 | First informal demo meeting: show internal MVP to one contact at Zara or H&M | CEO | Meeting notes; asset format confirmed (do they have CLO3D files?) |
| Week 10-12 | If CLO3D assets available: request 10 sample garments for pilot pipeline test | CEO + `fashion-garments` | 10 garments ingested into catalogue |
| Week 12-13 | If no CLO3D assets: offer to photogrammetry scan 10 physical garments as pilot | `fashion-scanning` | Garment scanning service proposal |
| Week 13-14 | First pilot LOI: Letter of Intent for unpaid pilot (we build, they provide garments + data access) | CEO | Signed LOI |
| Week 16-18 | Pilot garments live in catalogue: partner can see their products on our platform | `fashion-garments` | Partner-branded garments in catalogue |
| Week 20 | B2C public launch — now we have real user data to show partners | CEO | Launch metrics deck |
| Week 22-24 | Return rate data from beta: present to retailer as ROI case | CEO | `docs/roi-case.md` |
| Week 24 | **First paid B2B contract target: Zara or H&M** | CEO | Signed commercial agreement |
| Week 32 | Second retailer contract | CEO | Second signed contract |

### What We Ask Retailers For (Sequenced)

1. **Week 8 ask:** "Do you have CLO3D or Marvelous Designer files? Can we use 10 for a pilot?"
2. **Week 13 ask:** "Sign an LOI — we'll show your garments on our platform for free; you give us permission and raw assets"
3. **Week 20 ask:** "Here's our launch data and beta return reduction signal — ready to talk commercial terms?"
4. **Week 24 ask:** "Sign here" — commercial agreement with API access fee + revenue share on referral purchases

### Partner Garment Catalogue Go-Live

| Phase | Garment Source | Count | Go-Live |
|-------|---------------|-------|---------|
| Internal (Weeks 1-8) | CEO-sourced / Marvelous Designer marketplace / CC0 | 9 | Week 8 |
| Expanded internal (Weeks 9-16) | Expanded sourcing + photogrammetry | 50 | Week 14 |
| Beta catalogue | Mix of internal + partner pilot assets | 100 | Week 22 |
| Launch catalogue | 2+ brands contributing | 200+ | Week 24 |

---

## 6. Go-to-Market Plan

### B2C Launch

**Target user (Phase 1-2):** Fashion-forward early adopters. Female-skewing 25-35. Follows fashion accounts on Instagram. Early iPhone adopter. Cares about fit and sustainability. Has returned clothing online.

**Launch sequence:**
1. **Soft beta (Week 13):** 200 invite-only users. Personal outreach to fashion communities (r/femalefashionadvice, fashion Discord servers, style influencer followers). No press.
2. **Influencer pre-seeding (Week 18-19):** 5-10 fashion creators with working builds. Content ready for launch day.
3. **Hard launch (Week 20):** App Store go-live. Press drops. Influencer posts go live simultaneously.
4. **Growth loop (Week 20+):** Shareable outfit links as organic acquisition. "Try this on me" social mechanic.

**B2C launch criteria (must all be true before launch):**
- App Store approved
- Crash-free rate ≥99.5% from 200-person beta
- Scan completion rate ≥70% (users who start a scan finish it)
- ≥100 garments in catalogue
- Stripe payments live + tested
- GDPR/CCPA privacy policy reviewed by lawyer
- Support system live (Intercom or equivalent)

**B2C pricing:**
- Free tier: 1 body scan, 5 garment try-ons/month, web viewer only
- Pro (£9.99/$12.99/month): unlimited scans, unlimited try-ons, AR mode, outfit history, priority new garments
- Annual Pro (£89/$99/year): 30% discount

**US/UK sequencing:**
- Launch simultaneously in US and UK App Store (same binary, geo-targeted pricing)
- UK first for press: stronger fashion identity, London fashion week angle
- US is larger market — growth engine once UK establishes brand credibility

**Early adopter → mass market transition (Week 30+):**
- Trigger: 5,000 MAU in early adopter cohort + strong NPS (≥50)
- Mass market signal: onboarding time <2 minutes; scan success rate ≥85% on non-LiDAR devices
- Mass market requires: Android native app + photogrammetry quality parity with LiDAR
- Marketing shift: from "tech-forward fashion" to "always buy the right size" — utility positioning

### B2B Launch

**Target:** Zara, H&M — both have stated digital product strategies. Both likely have CLO3D assets.

**B2B value proposition:**
1. Reduce returns (average fashion return rate is 30-40% online — we target >10% reduction for try-on users)
2. Zero lift to integrate: SDK embed = 2 lines of code on their product page
3. They never touch body scan data — GDPR liability stays with us

**B2B launch criteria (must all be true):**
- Retailer API at 99.9% uptime over 30 days (staging)
- `/fit-profile` endpoint p95 <200ms under 100 concurrent requests
- ≥50 garments from partner brand in catalogue
- Return rate reduction demonstrated in our beta data (even if directional)
- Legal: API terms of service + data processing agreement (DPA) reviewed

**B2B pricing (initial):**
- Pilot (free, 3 months): retailer gets API access + catalogue ingestion for up to 50 garments
- Starter: £500/$650/month — 1,000 fit recommendation API calls, 50 garments
- Growth: £2,000/$2,600/month — 10,000 calls, 200 garments, deep-link try-on
- Enterprise: custom — full SDK embed, unlimited calls, dedicated support, co-marketing

**First B2B contract target:** Week 24. Either Zara or H&M. Even a Starter tier pilot deal validates the business model.

---

## 7. Risk Register

### Risk 1: AR Quality Fails Go/No-Go

**Probability:** Medium (40%)  
**Impact:** High — changes MVP experience  
**Mitigation:**
- Parallel 3D viewer development throughout Phase 1 (it's a first-class path, not an afterthought)
- Three.js photorealistic viewer is demo-quality regardless
- AR go/no-go decision at Week 6 gives 2 weeks to redirect Sprint 4 effort
**Contingency:** Full fallback plan documented in Section 4. Launch date unchanged. 3D viewer is a compelling product.

---

### Risk 2: LiDAR Accuracy Insufficient (<5mm threshold not met)

**Probability:** Medium (35%)  
**Impact:** High — body scan is the product's core data asset  
**Mitigation:**
- Photogrammetry path developed in parallel (Sprint 2)
- Accuracy tests with 10 subjects in Sprint 2, 50 subjects in Sprint 6
- COLMAP + neural reconstruction (Instant NGP) as enhanced photogrammetry fallback
- User-supplied measurements as a backup (enter chest/waist/hip manually)
**Contingency:** If LiDAR misses bar and photogrammetry does too — launch with manual measurements as primary (less magical but functional). AR/3D viewer still works.

---

### Risk 3: Zara/H&M Have No CLO3D Assets (or Won't Share Them)

**Probability:** Low for "no assets" (both are digitally mature), Medium for "won't share" (IP concerns)  
**Impact:** Medium — slows garment catalogue, changes pipeline design  
**Mitigation:**
- Early asset recon in Week 1 (before we build the CLO3D import pipeline)
- Physical garment photogrammetry as fallback (scanning service we offer as part of onboarding)
- Third-party CLO3D garment marketplaces (CLO-SET, Browzwear) for catalogue seeding
- Marvelous Designer marketplace as secondary source
**Contingency:** Build photogrammetry garment scanning into standard onboarding. Offer as a service ("send us 5 garments, we'll 3D scan them for free"). Slower pipeline but same output quality.

---

### Risk 4: Cloth Simulation Too Slow / Low Quality for Real-Time

**Probability:** Low (CLO3D baked approach is proven)  
**Impact:** Medium — affects AR visual quality  
**Mitigation:**
- MVP approach is baked CLO3D animation, NOT real-time physics — explicitly de-risks this
- 30-frame walk cycle pre-computed; AR plays back the bake
- Real-time cloth physics deferred to Phase 2 (when we have compute budget and time)
**Contingency:** Increase frame count (60 frames) for smoother bake. Add secondary idle + turn animations in Sprint 5-6 for realism.

---

### Risk 5: Diverse Body Type Rigging Failures

**Probability:** Medium (45%) — auto-rigging fails on non-standard proportions  
**Impact:** High — breaks product for large portion of users  
**Mitigation:**
- Test on 10+ body types in Sprint 1-2 (diverse BMI, height, gender, age)
- Manual QA pass with Blender for outlier cases
- ML-enhanced weight painting (DensePose or similar) for challenging proportions
- Fallback: parametric avatar from measurements (not scan-derived) for cases where auto-rig fails
**Contingency:** Ship with "body type acceptance list" (95th percentile coverage) and a graceful fallback to parametric avatar for edge cases. Log failures; improve ML pipeline in Phase 2.

---

### Risk 6: GDPR/CCPA Compliance Failure (Body Scan Data)

**Probability:** Low-Medium (data architecture designed from day one, but body data is sensitive)  
**Impact:** Critical — could shut down the product in EU/UK  
**Mitigation:**
- Privacy architecture designed from day 1: platform owns scan, retailers never see raw mesh
- User-deletable scans via API (tested in Sprint 4)
- Lawyer review of privacy policy + DPA before beta launch (Week 12)
- Data residency: EU users on AWS eu-west-1, US users on us-east-1 (enforced at infra level)
- Biometric data clauses: body scan may be classified as biometric in some jurisdictions — legal review required
**Contingency:** If legal issues surface, pause EU launch (global reach less critical than core US/UK). Body scan is an opt-in consent flow with explicit purpose disclosure.

---

### Risk 7: Retailer Sales Cycle Too Long (B2B Revenue Delayed)

**Probability:** High (70%) — enterprise sales is slow  
**Impact:** Medium — business model partially affected, but B2C provides runway  
**Mitigation:**
- Start retailer conversations at Week 3-4 (before product is done) to get legal/procurement process started early
- Offer free pilot (no-cost LOI) to remove procurement friction
- Target innovation/labs teams rather than procurement for first deal (faster)
- B2C subscription revenue provides cash flow while B2B closes
**Contingency:** If no B2B deal by Week 24, extend pilot timeline and use B2C data as sales proof. Alternative: target smaller/D2C brands who move faster than Zara/H&M.

---

## 8. Full Sprint List

| Sprint | Weeks | Theme | Key Deliverables | Owner(s) | Key Dependencies |
|--------|-------|-------|-----------------|----------|-----------------|
| S1 | 1–2 | Pipeline Skeleton | iOS LiDAR scan → `.obj`; Blender auto-rig → `.glb`; CLO3D t-shirt baked; ARKit body tracking POC; FastAPI + DB skeleton; `<model-viewer>` in browser | All agents | CLO3D licence; Apple dev account |
| S2 | 3–4 | Pipeline Integration | Full auto-rig pipeline; `.usdz` body export; COLMAP photogrammetry; accuracy test (10 subjects); draped + stretch garments baked; t-shirt `.usdz` in ARKit; POST `/scan` → S3; retailer API spec draft | All agents | Sprint 1 complete; 10 test subjects; COLMAP setup |
| S3 | 5–6 | AR Quality + Go/No-Go | People occlusion; AR perf benchmarks; garment size scaling; Three.js photorealistic viewer; outfit comparison; fitting algorithm v1; blazer baked; **AR GO/NO-GO DECISION** | `fashion-ar`, `fashion-platform`, `fashion-garments`, CEO | Physical iPhone 12/13/14 for benchmarking |
| S4 | 7–8 | Internal MVP | Full iOS try-on loop; user auth (Sign In with Apple); GDPR scan deletion; outfit save; 9-garment catalogue; TestFlight build; retail pitch deck | All agents | Sprint 3 AR decision; Stripe not needed yet |
| S5 | 9–10 | Retailer API | OAuth 2.0; `/v1/fit-profile` endpoint; retailer sandbox; CLO3D auto-ingestion pipeline; garment QA automation; 20 garments; retailer submission form | `fashion-platform`, `fashion-garments`, CEO | Sprint 4 API foundation |
| S6 | 11–12 | Beta Prep | Physical garment photogrammetry; AI texture enhancement; scan diversity hardening (50 subjects); recommendation engine v1; social sharing; beta invite system; App Store prep | All agents | 50 volunteer subjects; Stable Diffusion setup |
| S7 | 13–14 | Beta Launch + Retailer Pilot | 200-user public beta live; NPS survey; Sentry crash monitoring; Posthog analytics; 50 garments; retailer pilot LOI; partner garments ingested | All agents, CEO | TestFlight approved; retailer meeting completed |
| S8 | 15–16 | Beta Feedback + Scale Hardening | Beta feedback synthesis; scan re-scan flow; multi-size toggle; backend load testing (500 concurrent); CloudFront CDN; retailer deep-link | All agents | Beta NPS data; AWS infra |
| S9 | 17–18 | Pre-Launch Polish | App Store submission; top 5 beta fixes; press kit + product video; influencer outreach (10 creators); B2C pricing finalised; B2B pricing finalised | CEO, `fashion-ar`, `fashion-platform` | App Store assets; beta retrospective |
| S10 | 19–20 | **Launch Week** | App Store approval + go-live (US+UK); launch PR (Vogue Business + TechCrunch); Stripe Pro subscription live; influencer posts; B2B formal proposals sent | CEO, all agents | App Store review window; press embargo coordination |
| S11 | 21–22 | Post-Launch Iteration | Launch metrics report; top launch issues fixed; Android PWA; 100-garment catalogue; B2B JS SDK v1 | `fashion-platform`, `fashion-garments`, CEO | Launch data; Android testing device |
| S12 | 23–24 | **First B2B Contract** | First paid retailer contract signed; SDK live on partner site; 50 partner garments in catalogue; return rate tracking integration; US/UK 30-day metrics | CEO, `fashion-platform`, `fashion-garments` | Retailer commercial negotiations |
| S13–14 | 25–28 | EU Expansion | GDPR data residency (eu-west-1); EU App Store listing (DE, FR, IT); EU privacy policy updated; EU marketing | `fashion-platform`, CEO | Legal review; AWS eu-west-1 infra |
| S15–16 | 29–32 | Social Features | Outfit sharing feed; trend discovery; "Save from brand" social mechanic; second B2B retailer pipeline | `fashion-platform`, CEO | 5,000+ MAU for social network effect |
| S17–18 | 33–36 | Android Native | Kotlin app; ARCore body tracking (Android AR); Android scan (photogrammetry); parity with iOS 3D viewer | `fashion-ar`, `fashion-scanning` | Sprint 1-8 iOS pipeline portable to Android |
| S19–20 | 37–40 | APAC Expansion | Japan + Korea App Store; Japanese/Korean localisation; APAC influencer seeding; APAC retailer conversations (Uniqlo, Cos) | CEO, `fashion-platform` | Android + iOS stable |
| S21–22 | 41–44 | Recommendation Engine v2 | Collaborative filtering; body type clustering; "Similar to your saved looks" feature; A/B test recommendation CTR | `fashion-platform` | 10,000+ outfit history records |
| S23–24 | 45–48 | Manufacturer Portal | Self-service garment upload portal (web); automated CLO3D ingestion; brand dashboard (catalogue stats, usage analytics) | `fashion-platform`, `fashion-garments` | Retailer API v1 stable |
| S25–26 | 49–52 | Series A Prep | Third B2B contract; metrics deck; investor narrative; Unreal Engine cinematic renders for pitch; 10,000 MAU milestone | CEO, all agents | All prior milestones |

---

## Appendix: Key File & Format Reference

| Format | Used For | Produced By | Consumed By |
|--------|----------|-------------|-------------|
| `.ply` | Raw LiDAR point cloud | ARKit capture | Open3D pipeline |
| `.obj` | Cleaned mesh; garment sim frames | Open3D; CLO3D | Blender; Reality Composer Pro |
| `measurements.json` | Body measurements (chest/waist/hip/inseam/height) | Open3D + ML | Rigging; fitting algo; retailer API |
| `joints.json` | 33 body landmark positions (MediaPipe) | `fashion-scanning` | Blender Rigify script |
| `.blend` | Blender working file (rigged mesh) | `fashion-rigging` | Export pipeline |
| `.glb` | Binary glTF — web viewer + Android | Blender export | `<model-viewer>`; React web |
| `.usdz` | iOS AR asset (garment + body T-pose) | Reality Composer Pro / `usdz_converter` | ARKit + RealityKit |
| `.fbx` | Archive + Unreal Engine import | Blender export | Unreal Engine (Phase 4) |
| `.bvh` | Motion capture data | Mixamo | Blender NLA retargeting |
| `.zprj` | CLO3D native garment project | Retail partners / CLO3D operator | CLO3D simulation |
| `.abc` (Alembic) | Cloth animation cache | CLO3D bake | Blender; DCC tools |
| `garment_metadata.json` | Garment catalogue record | `fashion-garments` | API; frontend |
| `.sql` | DB schema | `fashion-platform` | PostgreSQL |
| `retailer-api-spec.yaml` | OpenAPI spec for B2B API | `fashion-platform` | Retailer dev teams |

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Review:** End of Sprint 1 (Week 2)  
**Owner:** Fashion Tech CEO
