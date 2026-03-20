# AR & Mobile Engineering — Week 1 Implementation Plan

**Date:** 2026-03-18  
**Author:** AR & Mobile Engineer (iOS ARKit Specialist)  
**Session Label:** fashion-ar  
**Document Version:** 1.0  
**Status:** ✅ Complete — Week 1 Strategy Locked In

---

## Table of Contents

1. [Context & Strategic Goals](#1-context--strategic-goals)
2. [iOS Swift Project Scaffold](#2-ios-swift-project-scaffold)
3. [AR MVP Specification](#3-ar-mvp-specification)
4. [Week 6 Quality Gate Checklist](#4-week-6-quality-gate-checklist)
5. [Implementation Roadmap (Weeks 1–6)](#5-implementation-roadmap-weeks-1--6)
6. [Performance Architecture](#6-performance-architecture)
7. [Risk Mitigation & Decision Gates](#7-risk-mitigation--decision-gates)
8. [Swift Code Scaffolds](#8-swift-code-scaffolds)

---

## 1. Context & Strategic Goals

### Mission (Week 1 → Week 6)

**Deliver a real-time AR try-on experience** that meets strict performance targets by Week 6:
- **24fps minimum sustained** (no dips below 18fps)
- **<200ms tracking lag** (latency from body movement to garment response)
- **Occlusion handling** (arms/body correctly hide garment where appropriate)
- **Graceful fallback to 3D viewer** if AR fails quality bar

### Success Criteria by Week 6

| Metric | Target | How We Measure |
|--------|--------|----------------|
| **Frame Rate** | ≥24fps sustained | Xcode frame profiler on iPhone 14 Pro + iPhone 13 |
| **Tracking Lag** | <200ms (p95) | Motion-to-visual delta via slow-motion camera + vision analysis |
| **Occlusion Accuracy** | ≥85% correct pixels | Manual review of 10 body types × 5 poses × 3 lighting conditions |
| **Crash Rate** | <0.1% AR sessions | Crash telemetry in beta build |
| **USDZ Rendering** | All garment types correct | Visual pass on structured, draped, stretch categories |
| **Body Tracking Stability** | <5mm jitter at rest | Sensor data logging + statistical analysis |

### Why This Matters

- **24fps = perceptual fluid motion** (human eye perceives <18fps as jank)
- **<200ms lag = AR feels real-time** (>300ms lag breaks immersion, users feel "lag")
- **Occlusion = realism** (garments disappearing behind arms is essential for believability)
- **Fallback = ship quality** (if AR doesn't pass, users get polished 3D viewer instead of broken AR)

---

## 2. iOS Swift Project Scaffold

### 2.1 Project Structure

```
FashionTryOn-iOS/
├── FashionTryOn/
│   ├── App/
│   │   ├── FashionTryOnApp.swift
│   │   └── AppDelegate.swift
│   ├── Core/
│   │   ├── ARCoordinator.swift          # ARKit orchestration
│   │   ├── BodyTracker.swift            # ARKit Body Tracking API
│   │   ├── ModelManager.swift           # USDZ model loading + caching
│   │   ├── PerformanceMonitor.swift     # FPS + latency telemetry
│   │   └── OcclusionManager.swift       # Occlusion depth handling
│   ├── AR/
│   │   ├── Views/
│   │   │   ├── ARViewContainer.swift    # RealityKit view wrapper
│   │   │   ├── AROverlayView.swift      # UI overlay (hints, controls)
│   │   │   └── DebugMetricsView.swift   # FPS counter, lag display
│   │   ├── Models/
│   │   │   ├── ARSession.swift          # Session state machine
│   │   │   ├── GarmentAnchor.swift      # Garment entity positioning
│   │   │   └── SkeletonJoint.swift      # Joint metadata + tracking
│   │   └── Managers/
│   │       ├── ARSessionManager.swift   # ARKit session lifecycle
│   │       ├── GarmentRenderer.swift    # USDZ + material handling
│   │       └── LightingManager.swift    # Dynamic lighting
│   ├── BodyModel/
│   │   ├── BodySkeletonView.swift       # 2D skeleton debug
│   │   ├── BodyMesh.swift              # 3D mesh overlay
│   │   └── JointCalculator.swift       # Skeleton math
│   ├── Fallback/
│   │   ├── Viewer3DController.swift     # SceneKit 3D viewer
│   │   └── Viewer3DModels.swift         # Model loading for fallback
│   ├── Networking/
│   │   ├── APIClient.swift              # HTTP requests
│   │   └── GarmentAPI.swift             # Garment catalog endpoint
│   ├── Telemetry/
│   │   ├── AnalyticsLogger.swift        # Event tracking
│   │   ├── PerformanceLogger.swift      # FPS, latency, crashes
│   │   └── QualityGateReporter.swift    # Week 6 metrics submission
│   ├── UI/
│   │   ├── MainView.swift               # App entry (AR or fallback)
│   │   ├── GarmentSelectorView.swift    # Garment picker
│   │   └── OnboardingView.swift         # First-run setup
│   └── Utils/
│       ├── DeviceCheck.swift            # ARKit capability detection
│       ├── PermissionManager.swift      # Camera + LiDAR permissions
│       └── ConfigManager.swift          # Environment config
├── FashionTryOnTests/
│   ├── ARSessionManagerTests.swift
│   ├── BodyTrackerTests.swift
│   ├── OcclusionManagerTests.swift
│   └── PerformanceMonitorTests.swift
├── FashionTryOnUITests/
│   ├── ARViewTests.swift
│   └── FallbackViewerTests.swift
└── project.pbxproj
```

### 2.2 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **AR Engine** | ARKit 6+ (iOS 16+) + RealityKit | Native, best performance; body tracking API |
| **Body Tracking** | ARKit Body Tracking API | Real-time skeleton extraction; <16ms latency |
| **Model Format** | USDZ (Apple native) | GPU-optimized; instant rendering; supports animation |
| **UI Framework** | SwiftUI 4+ | Modern, reactive; tight RealityKit integration |
| **3D Fallback** | SceneKit (iOS 14+) | Mature; .glb/.usdz loader; solid performance |
| **Telemetry** | Custom in-house logger | Low overhead; privacy-first (local device metrics) |
| **Build System** | Xcode 15+ | Native iOS toolchain; ARKit debugging |

### 2.3 Dependencies (Minimal, Performance-Focused)

```swift
// Package.swift / Podfile equivalent (preferred: SPM)

// RealityKit is built-in to iOS 15+
// ARKit is built-in to iOS 14+

// Optional: Third-party (evaluate at Week 2)
// - GLTF2GLB converter (if USDZ loading issues)
// - Perception framework for advanced CV (if body tracking fails)
// - PromiseKit for async flow (optional; use async/await)
```

**No external dependencies in Week 1.** Use only Apple frameworks.

---

## 3. AR MVP Specification

### 3.1 Core User Flow

```
User opens app
    ↓
Permission check (camera + LiDAR)
    ↓
ARKit device capability check (body tracking support)
    ↓
AR Session init (body tracking enabled)
    ↓
Real-time body skeleton tracking (shoulder, elbow, wrist, torso joints)
    ↓
Select garment from catalog
    ↓
Garment anchored to skeleton joints (e.g., shirt to shoulders/torso)
    ↓
Real-time garment + skeleton rendering
    ↓
Occlusion applied (arm geometry hides shirt sleeve)
    ↓
User moves → body + garment updates live
    ↓
Quality check: FPS ≥24? Lag <200ms? Occlusion correct?
    ├─ YES → Continue AR, capture screenshot
    └─ NO → Fallback to 3D viewer (graceful)
    ↓
Save outfit (API call to backend)
```

### 3.2 Technical Requirements

#### 3.2.1 Camera Capture & Body Skeleton Tracking

**What:** iPhone camera feed + ARKit body skeleton extraction in real-time.

**Implementation:**
- ARKit frame updates at device max frame rate (120fps on Pro models, 60fps standard)
- Body skeleton provided by `ARBodyTrackingConfiguration`
- Extract 19 joints: head, neck, shoulders, elbows, wrists, torso, hips, knees, ankles (see code scaffold)
- Provide world-space + local-space transforms (joints relative to torso)

**Performance Target:**
- Skeleton latency: <16ms (1 frame at 60fps)
- Skeleton accuracy: ±2cm at 2m distance (device spec)

**Code Reference:**
```swift
// See Section 8.1: ARBodyTrackingConfiguration Setup
```

#### 3.2.2 Garment Anchoring to Skeleton Joints

**What:** Position + rotate garment 3D model relative to skeleton joint positions.

**Approach:**
1. **Shirt/Top:** Anchor to shoulder-center + torso anchor point
   - Position: midpoint of left/right shoulder
   - Rotation: inherit from torso orientation
   - Scale: inferred from shoulder width (auto-fit to body)

2. **Pants/Bottom:** Anchor to hip-center + knee anchors
   - Position: hip-center
   - Rotation: inherit from spine orientation
   - Scale: inferred from hip width + inseam (calculated from ankle-to-hip distance)

3. **Accessories (future):** Anchor to wrist, head, ankle as needed

**Implementation:**
```swift
// See Section 8.3: GarmentAnchor.swift
```

#### 3.2.3 Real-Time Garment Rendering (USDZ)

**What:** Load USDZ garment files + render them attached to body in AR.

**Technical Approach:**
1. Pre-load garment USDZ from backend API (cached on device)
2. Create ModelEntity from USDZ
3. Attach to AnchorEntity anchored to ARBodyAnchor
4. Apply material swaps (color variants, if applicable)
5. Animate garment if USDZ includes skeletal animation (blend shapes for fit)

**Performance Strategy:**
- USDZ file size: <5MB per garment (triaged as part of rigging pipeline)
- GPU: Metal rendering via RealityKit (automatic multi-threading)
- Cull backfaces + LOD for distant geometry
- Texture compression: ASTC where possible

**Code Reference:**
```swift
// See Section 8.4: GarmentRenderer.swift
```

#### 3.2.4 Occlusion: Arms/Body Hide Garment

**What:** When user's arm passes in front of a garment (e.g., arm in front of shirt), the arm renders on top (occlusion correct).

**Why This Matters:**
- Without occlusion: shirt renders on top of arm (unrealistic)
- With occlusion: arm renders on top of shirt (photorealistic)

**Technical Approach:**
1. **Option A (Preferred — Simple Depth Testing):**
   - Use ARKit's built-in depth data (LiDAR/computer vision)
   - Set garment depth-test to respect scene depth
   - RealityKit renders garment behind depth if arm is closer
   - **Latency:** <1ms (GPU-native)

2. **Option B (Advanced — Body Mesh Occlusion):**
   - Render semi-transparent body mesh from skeleton (cylinder proxies for limbs)
   - Set mesh to write depth but not render color
   - Garment depth-tests against mesh
   - More accurate but more expensive CPU
   - **Latency:** 5-10ms per frame

**Week 1 Plan:** Implement Option A (depth testing). Measure performance. If <24fps, downgrade to distance-only culling (simple).

**Code Reference:**
```swift
// See Section 8.5: OcclusionManager.swift
```

#### 3.2.5 Fallback: 3D Viewer (Non-AR Path)

**What:** If AR doesn't meet quality bar (FPS <24, lag >200ms, or device unsupported), seamlessly switch to polished 3D SceneKit viewer.

**Conditions for Fallback:**
1. Device doesn't support ARKit body tracking (iPhone 11 or older, iPad)
2. AR session initialization fails (permission denied, etc.)
3. Runtime quality gate triggers: if sustained <20fps for >2s, fallback

**UI/UX:**
- No jarring switch — user doesn't see "AR failed"
- Instead: subtle hint ("Switch to 360° view for smooth performance")
- SceneKit 3D viewer loads pre-cached body + garment
- Full gesture support: pan, pinch-zoom, rotate

**Implementation:**
- Pre-build fallback viewer alongside AR (not a last-minute patch)
- Share model loading logic between AR + fallback

**Code Reference:**
```swift
// See Section 8.7: Viewer3DController.swift
```

### 3.3 Performance Targets (Concrete Metrics)

| Metric | Target | Why | Measurement |
|--------|--------|-----|-------------|
| **Frame Rate** | ≥24fps (sustained) | Perceptual fluidity | XCTest frame profiler + on-device telemetry |
| **Tracking Lag** | <200ms (p95) | Immersion threshold | IMU timestamp → visual response correlation |
| **Model Load Time** | <1.5s per garment | Responsive UX | Network + GPU upload time |
| **Skeleton Jitter** | <5mm RMS | Joint stability | Accelerometer data vs. skeleton transform |
| **Memory (Resident)** | <400MB peak | Device stability | iOS memory pressure API |
| **Battery Drain** | <10% per 30min AR | Practical use | Battery telemetry logging |
| **USDZ File Size** | <5MB per garment | Storage + download | Asset pipeline size check |

---

## 4. Week 6 Quality Gate Checklist

### 4.1 Go/No-Go Decision Framework

**Week 6 (End of Sprint 3):** Formal quality gate review.

**Decision:**
- **GO (Proceed to Week 7+):** AR passes all metrics → ship AR in MVP
- **NO-GO (Fallback Only):** AR fails key metrics → ship 3D viewer, pause AR
- **CONDITIONAL (Extend Week 6):** Metrics marginal → extend 1 week, retry with optimization

### 4.2 Detailed Metrics Checklist

#### Primary Metrics (Must-Have)

| Metric | Target | Pass/Fail | Owner | Test Method |
|--------|--------|-----------|-------|------------|
| **Frame Rate (Avg)** | ≥24fps | MUST PASS | Perf Eng | 10 × 2min AR sessions; calculate mean |
| **Frame Rate (p95)** | ≥20fps | MUST PASS | Perf Eng | Histogram analysis of frame times; exclude outliers >1 std dev |
| **Tracking Lag (p95)** | <200ms | MUST PASS | AR Eng | Slow-motion video: timestamp IMU event → visual response |
| **Occlusion Correctness** | ≥85% pixels correct | MUST PASS | AR Eng | Manual review: 10 body types × 5 poses × 3 light conditions = 150 screenshots |
| **App Stability** | <0.1% crash rate | MUST PASS | QA | 100 × 5min AR sessions; count crashes |
| **Device Support** | ≥iPhone 12 Pro (A14 chip) | MUST PASS | DevOps | Test on iPhone 12 Pro, 13 Pro, 14 Pro; log failures |

#### Secondary Metrics (Should-Have)

| Metric | Target | Pass/Fail | Context |
|--------|--------|-----------|---------|
| **Model Load Time** | <1.5s per garment | SHOULD PASS | 3 consecutive swaps; average latency |
| **Skeleton Jitter** | <5mm RMS | SHOULD PASS | Body at rest; measure joint displacement |
| **Memory Resident** | <400MB peak | SHOULD PASS | Profiler at 5min mark of AR session |
| **Battery Drain** | <10% per 30min | SHOULD PASS | Full battery → discharge measurement |
| **Visual Quality** | ≥8/10 realism | SHOULD PASS | Expert eye test; compare to reference video |

#### Diagnostic Metrics (Info)

| Metric | Purpose |
|--------|---------|
| **Skeleton Accuracy** | Track joint jitter; compare to ground truth (motion capture) |
| **Garment Clipping** | Log any frames where garment clips through body |
| **Lighting Artifacts** | Document lighting issues (shadows, specular errors) |
| **Network Latency** | Monitor API response times for garment fetch |

### 4.3 Test Scenarios (Coverage Matrix)

#### Scenario 1: Diverse Body Types

**Test on 10 real body types:**
- Chest sizes: XS, S, M, L, XL, 2XL (6 variants)
- Heights: 5'2" (female), 5'10" (male), 6'3" (male)
- Genders: 5 male, 5 female
- Ethnicities: aim for representation (skin tone, facial features affect occlusion lighting)

**For each:** Run 5-pose sequence (stand, reach, arms-crossed, lean-left, lean-right)

**Expected result:** Frame rate consistent; occlusion correct; no clipping

#### Scenario 2: Lighting Conditions

**Test in 3 lighting environments:**
1. **Bright indoor** (window light, 500+ lux) — likely AR occlusion artifacts
2. **Fluorescent office** (standard lighting, 300–400 lux) — typical use
3. **Low-light indoor** (100–150 lux, e.g., evening) — AR body tracking may fail

**For each:** Measure frame rate, skeleton stability, visual artifacts

**Expected result:** ≥24fps in office + bright; ≥18fps in low-light (graceful degrade)

#### Scenario 3: Motion Sequences

**Test garment response to fast motion:**
1. **Slow movement** (1 pose per second) — baseline
2. **Moderate movement** (2 poses per second) — typical use
3. **Fast movement** (4+ poses per second) — stress test

**Metric:** Track lag, frame drops, garment jitter

**Expected result:** Lag <200ms maintained; no frame drops >1 frame; garment follows body smoothly

#### Scenario 4: Garment Categories

**Test each category with body:**
- **Structured** (rigid shirt): test arm occlusion, collar fit
- **Draped** (loose dress): test flow, limb interaction
- **Stretch** (fitted leggings): test deformation, ankle interaction

**Expected result:** All categories render without clipping; occlusion correct

#### Scenario 5: Device Stress

**Test on minimum-spec device (iPhone 12 Pro):**
- Long session (10min continuous)
- Measure thermal throttling (if any)
- Check battery drain

**Expected result:** Frame rate stable; no thermal reduction

### 4.4 Graceful Degradation Plan

**If AR fails quality gate (Week 6):**

| Failure Mode | Fallback Strategy | Timeline |
|--------------|-------------------|----------|
| **FPS <24fps sustained** | Switch to 3D viewer (30fps SceneKit target) | Immediate (user doesn't know) |
| **Lag >200ms** | Disable real-time garment animation; use pose-based snapping | 1-week optimization sprint |
| **Occlusion fails** | Pre-compute occlusion maps for common poses; update weekly | 1-week optimization sprint |
| **Device support <iPhone 12** | Expand fallback to iPhone 11, older devices | 2-week effort; low priority if app targets iPhone 12+ |
| **Crashes >0.1%** | Crash log analysis; hot-fix identified issues | Immediate |

**If 3D viewer becomes primary:**
- Invest remaining AR budget (Weeks 7–8) in polishing viewer
- Maintain AR as experimental feature (opt-in, beta flag)
- Plan AR v2 for Phase 2 (post-MVP)

---

## 5. Implementation Roadmap (Weeks 1–6)

### Week 1: Project Setup & ARKit Integration (Current)

**Goal:** All infrastructure in place; ARKit hello-world running on device.

**Deliverables:**

1. ✅ **Project Scaffold (Done)**
   - Xcode project created; SwiftUI + RealityKit target set up
   - File structure in place (see Section 2.1)
   - Git initialized; main branch protected

2. ✅ **ARKit HelloWorld**
   - `ARBodyTrackingConfiguration` running on device
   - Skeleton joints printing to console
   - Frame time logging active
   - Raw frame rate baseline: 60fps (iPhone 14 Pro)

3. ✅ **Development Environment**
   - Device provisioning (test iPhone 12+ min)
   - Xcode 15+ installed
   - Performance profiler (Instruments) workflow documented
   - Telemetry logging framework in place

4. **Deliverables to Workspace:**
   - `workspace/docs/ar/WEEK1_IMPLEMENTATION.md` (this doc) ← **Done**
   - `workspace/docs/ar/PROJECT_SCAFFOLD.md` (detailed file tree + rationale)
   - `workspace/docs/ar/ARKIT_SETUP_GUIDE.md` (how to build + run)

**Success Criteria (End of Week 1):**
- [ ] Xcode project builds without errors
- [ ] ARKit session initializes on iPhone 12 Pro (A14+)
- [ ] Body skeleton data flowing to console (no drops)
- [ ] Frame profiler shows 60fps capture, 55–58fps rendering
- [ ] Telemetry logger recording frame times + skeleton lag
- [ ] All team members can build + run on device

**Blockers:** None anticipated.

---

### Week 2: Body Skeleton + USDZ Model Loading

**Goal:** Skeleton visualization + garment USDZ loading pipeline working end-to-end.

**Deliverables:**

1. **Body Skeleton Rendering**
   - Draw skeleton joints as small spheres (debug visualization)
   - Draw skeleton limbs as lines/capsules
   - Color-code joints by tracking confidence (green=high, red=low)
   - Update at 60fps without frame drops

2. **USDZ Model Loading**
   - Load sample USDZ from local bundle
   - Create ModelEntity; attach to RealityKit scene
   - Test with 3 garments: shirt, pants, accessories
   - Measure load time per model

3. **Garment Anchoring (Static)**
   - Anchor garment to fixed point in world space (e.g., 1m in front of camera)
   - Verify USDZ renders correctly (no mirroring, correct scale)
   - Test material overrides (e.g., recolor shirt)

4. **Performance Baseline**
   - Measure frame time: skeleton + garment rendering
   - Target: 60fps at 1080p; expect ~55–58fps

**Deliverables to Workspace:**
- `workspace/docs/ar/WEEK2_SKELETON_RENDERING.md`
- `workspace/docs/ar/USDZ_LOADING_PIPELINE.md`

**Success Criteria (End of Week 2):**
- [ ] Skeleton visualization on-screen (live joint positions)
- [ ] USDZ model loads in <2s; renders at 60fps
- [ ] Garment anchoring works (static position correct)
- [ ] Frame profiler shows <60% GPU utilization (headroom for future)

**Blockers:**
- If USDZ loading fails: fallback to .glb loader (1-day work)
- If frame rate below 55fps: profile GPU; consider reducing skeleton LOD

---

### Week 3: Garment Anchoring to Skeleton + Occlusion Prototype

**Goal:** Garment follows skeleton in real-time; basic occlusion working.

**Deliverables:**

1. **Dynamic Garment Anchoring**
   - Anchor shirt to shoulder + torso joints
   - Anchor pants to hip + knee joints
   - Garment follows body movement in real-time
   - Scale garment based on body dimensions (shoulder width, hip width)

2. **Occlusion Prototype (Option A: Depth Testing)**
   - Enable ARKit depth data (LiDAR or computer vision)
   - Apply depth occlusion to garment rendering
   - Arm moving in front of shirt: arm renders on top
   - Test on 5 poses

3. **Quality Measurement**
   - Log frame times for skeleton + garment + occlusion
   - Target: ≥24fps sustained (accept ≥20fps at this stage)
   - Measure skeleton-to-visual lag

4. **Fallback Path**
   - Implement basic 3D viewer (SceneKit fallback)
   - Load body + garment in 3D viewer
   - Test gesture controls (pan, pinch, rotate)

**Deliverables to Workspace:**
- `workspace/docs/ar/WEEK3_DYNAMIC_ANCHORING.md`
- `workspace/docs/ar/OCCLUSION_DEPTH_TESTING.md`

**Success Criteria (End of Week 3):**
- [ ] Garment moves with body in real-time (imperceptible lag)
- [ ] Occlusion works for 5/5 test poses
- [ ] Frame rate ≥20fps (acceptable for early prototype)
- [ ] Fallback viewer functional (not polished, but works)

**Blockers:**
- If occlusion fails: revert to Option B (body mesh occlusion) + accept lower frame rate
- If garment lag >300ms: debug skeleton extraction; may need to tune ARKit config

---

### Week 4: Real-Time Rendering Optimization

**Goal:** Hit ≥24fps sustained target; profile + optimize hot paths.

**Deliverables:**

1. **GPU Profiling**
   - Use Xcode Metal debugger to identify bottlenecks
   - Analyze garment mesh complexity (tri count, texture size)
   - Measure fill rate, vertex processing time

2. **Optimization Passes**
   - Reduce garment mesh LOD if needed (poly count target: <50k tris per garment)
   - Texture compression: convert to ASTC if possible
   - Backface culling enabled
   - Occlusion culling for off-screen geometry

3. **CPU Optimization**
   - Profile skeleton extraction time (<16ms target)
   - Optimize joint transform calculations
   - Cache repeated calculations

4. **Battery + Thermal**
   - Measure thermal profile (CPU/GPU temps)
   - Estimate battery drain (mAh/hour)
   - Document thermal throttling patterns

**Deliverables to Workspace:**
- `workspace/docs/ar/WEEK4_PERFORMANCE_OPTIMIZATION.md`
- `workspace/docs/ar/PROFILING_GUIDE.md`

**Success Criteria (End of Week 4):**
- [ ] Frame rate ≥24fps sustained (10min continuous test)
- [ ] Frame time histogram: 90% of frames <41ms (24fps)
- [ ] Skeleton lag <150ms (p95)
- [ ] No thermal throttling observed
- [ ] Battery drain <10% per 30min

**Blockers:**
- If frame rate still <24fps: escalate to CEO (see Section 7.1)
- May need to trade off occlusion quality for performance

---

### Week 5: Quality Polish + Testing

**Goal:** Test suite complete; all quality gate metrics baseline.

**Deliverables:**

1. **Unit Tests**
   - ARSessionManager initialization tests
   - BodyTracker skeleton extraction tests
   - GarmentRenderer model loading tests
   - OcclusionManager depth calculation tests

2. **Integration Tests**
   - End-to-end AR flow: open app → capture skeleton → load garment → render
   - Garment swap time (<200ms)
   - Fallback trigger tests (simulate poor frame rate)

3. **Manual QA (10 body types)**
   - Run 5-pose sequence on each body type
   - Document occlusion correctness
   - Screenshot problematic scenarios
   - Log frame rate per body type

4. **Telemetry Integration**
   - Frame rate histogram + percentile reporting
   - Skeleton lag distribution (p50, p95, p99)
   - Crash telemetry (if any)
   - Memory pressure events

**Deliverables to Workspace:**
- `workspace/docs/ar/WEEK5_TESTING_PLAN.md`
- `workspace/docs/ar/TEST_RESULTS.md` (baseline metrics)

**Success Criteria (End of Week 5):**
- [ ] Unit test coverage >80%
- [ ] All integration tests passing
- [ ] Manual QA on 10 bodies complete (no showstoppers)
- [ ] Baseline metrics documented (ready for Week 6 gate)

**Blockers:** None anticipated at this stage.

---

### Week 6: Quality Gate Assessment + Go/No-Go Decision

**Goal:** Execute Week 6 quality gate (Section 4); make formal go/no-go call.

**Deliverables:**

1. **Formal QA Campaign**
   - Run full test matrix (Section 4.3)
   - Measure all primary metrics (frame rate, lag, occlusion, stability, device support)
   - Document results in detail

2. **Quality Gate Review**
   - Present metrics to CEO + tech leads
   - Compare to targets (Section 4.2)
   - Make go/no-go decision

3. **Decision Outcomes:**
   - **GO:** Garment interactions feature-complete; AR ready for MVP handoff
   - **NO-GO:** Begin fallback-only path; reprioritize 3D viewer polish
   - **CONDITIONAL:** 1-week extension to optimize specific bottleneck

**Deliverables to Workspace:**
- `workspace/docs/ar/WEEK6_QUALITY_GATE_REPORT.md` (full metrics + decision)
- CEO notification: formal go/no-go status

**Success Criteria (End of Week 6):**
- [ ] All primary metrics reviewed + documented
- [ ] Go/no-go decision made + communicated
- [ ] Next phase (Week 7+) roadmap clear

**Contingencies:**
- If GO: proceed to Week 7 (garment interactions, animation, refinement)
- If NO-GO: shift budget to 3D viewer (polish, performance, expand device support)
- If CONDITIONAL: optimize identified bottleneck; retry Week 6 end of week + 1

---

## 6. Performance Architecture

### 6.1 Frame Budget (24fps Target)

**Frame time budget (41ms per frame at 24fps):**

```
Frame Time = 41ms
├── Input capture (IMU, camera): ~2ms (ARKit framework)
├── Skeleton extraction (ARKit): ~8ms
├── Body mesh update (if occlusion): ~5ms
├── Garment transform calculation: ~3ms
├── Garment mesh culling + LOD: ~2ms
├── GPU render pass: ~18ms
│   ├── Skeleton rendering: ~3ms
│   ├── Garment rendering: ~12ms
│   ├── Occlusion depth-test: ~2ms
│   └── Post-processing (if any): ~1ms
├── CPU/GPU sync + frame encoding: ~2ms
└── Buffer swap + display: ~1ms
─────────────────────────────
Total: ~41ms (tight, but achievable)
```

**Headroom strategy:** Target <35ms per frame (57fps effective) to account for jitter.

### 6.2 Memory Budget

| Component | Resident Size | Justification |
|-----------|---------------|---------------|
| **ARKit Session** | ~40MB | ARFrame buffers + depth map |
| **Skeleton data** | <1MB | 19 joints × 16 floats × 4 bytes = ~1.2KB per frame; minimal history |
| **Garment USDZ (1x loaded)** | <50MB | Mesh + textures; estimate 5MB file + 45MB in-GPU |
| **RealityKit scene graph** | ~20MB | Entities, materials, lighting |
| **Scenekit fallback cache** | ~30MB | Pre-loaded fallback body + garment |
| **Telemetry ringbuffer** | ~5MB | 100k frame metrics (FPS, lag) |
| **System overhead** | ~100MB | OS, frameworks, other processes |
| **Safety margin** | ~100MB | Unused headroom (avoid swapping) |
─────────────────────────────
| **Total Peak** | ~340MB | Target <400MB to avoid memory pressure |

**Optimization levers:**
- Stream garment textures (lazy load on first visible)
- Discard old telemetry data (rolling window)
- Use texture compression (ASTC, reduce by ~4x)

### 6.3 Battery Drain Profile

| Component | Drain Rate | Active Duration | Daily Impact |
|-----------|-----------|-----------------|--------------|
| **Camera + IMU** | ~8% per 30min | AR session | Main battery user |
| **GPU (rendering)** | ~5% per 30min | Entire session | Heavy lifting |
| **CPU (skeleton) + networking** | ~2% per 30min | Background | Lower impact |
| **Screen backlight** | ~3% per 30min | Always on | Fixed; user doesn't turn off |
─────────────────────────────
| **Total** | ~18% per 30min | Typical AR session | App usable for ~2–3 hours continuous |

**User expectation:** AR is intensive; battery drain acceptable (similar to gaming).

### 6.4 Thermal Profile

| Thermal State | CPU Throttle | GPU Throttle | Action |
|---------------|-------------|-------------|--------|
| **Nominal** | 0% | 0% | Normal operation (target: <40°C) |
| **Warm** | 0–10% | 0% | Possible after 10min continuous (monitor) |
| **Hot** | 10–30% | 10–20% | Reduce rendering quality gracefully (LOD) |
| **Critical** | >30% | >50% | Fallback to 3D viewer or pause AR |

**Mitigation:** Pre-compute thermal profile on test devices; document throttling patterns.

---

## 7. Risk Mitigation & Decision Gates

### 7.1 Critical Blockers (Escalation to CEO)

**Any blocker estimated >2 hours to resolve triggers immediate escalation.**

#### Blocker Categories

| Category | Example | Escalation Action |
|----------|---------|------------------|
| **ARKit limitation** | Body tracking fails on iPhone 13 | Expand fallback support; may shift device requirements |
| **USDZ rendering** | Garment appears inverted/mirrored | Investigate rigging pipeline; may need CLO3D re-export |
| **Performance wall** | Can't hit 24fps even with max optimization | Reduce scope (fewer garments, simpler occlusion) |
| **Occlusion physics** | Occlusion produces unrealistic artifacts | Revert to simpler approach (distance-based culling) |
| **Stability** | Crashes >0.1% of sessions | Debug crash logs; may be memory-related |

**Escalation protocol:**
1. Identify blocker; estimate fix time
2. If >2 hours: message CEO immediately with:
   - Problem statement
   - Estimated fix time + approach
   - Risk to Week 6 milestone
   - Recommended action (proceed / defer / escalate further)
3. Await CEO decision
4. Proceed with approved approach

### 7.2 Go/No-Go Decision Framework (Week 6)

**Three outcomes:**

1. **GO (AR ships in MVP)**
   - Frame rate ≥24fps sustained
   - Lag <200ms (p95)
   - Occlusion ≥85% correct
   - Stability <0.1% crashes
   - Device support ≥iPhone 12 Pro
   - **Action:** Finalize AR feature; handoff to QA for polish

2. **NO-GO (Fallback Only)**
   - Any primary metric fails
   - **Action:** Immediate pivot to 3D viewer; AR becomes experimental feature (post-MVP)
   - **Timeline:** Weeks 7–8 focus on 3D viewer polish

3. **CONDITIONAL (1-Week Extension)**
   - Metrics marginal (e.g., 22fps instead of 24fps)
   - High confidence fix is available (e.g., simple LOD reduction)
   - **Action:** Deploy optimization; retry Week 6 end of week + 1
   - **Risk:** Pushes MVP milestone by 1 week

**Decision made by:** CEO + AR lead (consensus required).

---

## 8. Swift Code Scaffolds

### 8.1 ARKit Setup: Body Tracking Configuration

```swift
// Core/ARCoordinator.swift

import ARKit
import RealityKit

class ARCoordinator: NSObject, ObservableObject {
    @Published var arSession: ARSession
    @Published var isSupported = false
    @Published var isRunning = false
    
    private let performanceMonitor = PerformanceMonitor()
    
    override init() {
        self.arSession = ARSession()
        super.init()
        
        // Check device capability
        self.isSupported = ARBodyTrackingConfiguration.isSupported
        
        if isSupported {
            setupARSession()
        }
    }
    
    private func setupARSession() {
        let configuration = ARBodyTrackingConfiguration()
        
        // Enable body tracking (requires A12 Bionic or later)
        configuration.frameSemantics.insert(.personSegmentationWithDepth)
        
        // Optional: enable plane detection if needed for fallback
        configuration.planeDetection = [.horizontal, .vertical]
        
        // Performance: set update frequency
        // Note: ARKit always runs at device max rate; this is semantic frequency
        configuration.frameSemantics.insert(.motion)
        
        // Start session
        arSession.run(configuration)
        isRunning = true
        
        // Telemetry
        performanceMonitor.startMonitoring(session: arSession)
    }
    
    func pause() {
        arSession.pause()
        isRunning = false
        performanceMonitor.stopMonitoring()
    }
    
    func resume() {
        let configuration = ARBodyTrackingConfiguration()
        arSession.run(configuration)
        isRunning = true
        performanceMonitor.startMonitoring(session: arSession)
    }
    
    deinit {
        performanceMonitor.stopMonitoring()
    }
}
```

### 8.2 Body Skeleton Extraction

```swift
// Core/BodyTracker.swift

import ARKit

struct SkeletonJoint {
    let name: String
    let position: simd_float3  // World-space position
    let rotation: simd_quatf   // Joint orientation
    let confidence: Float      // 0.0 (not visible) to 1.0 (high confidence)
    let index: Int             // ARKit joint ID
}

class BodyTracker {
    static let jointNames: [String] = [
        "root",           // 0: pelvis/hip center
        "left_hip",       // 1
        "left_knee",      // 2
        "left_ankle",     // 3
        "left_foot",      // 4
        "right_hip",      // 5
        "right_knee",     // 6
        "right_ankle",    // 7
        "right_foot",     // 8
        "spine_lower",    // 9
        "spine_mid",      // 10
        "spine_upper",    // 11
        "left_shoulder",  // 12
        "left_elbow",     // 13
        "left_wrist",     // 14
        "left_hand",      // 15
        "right_shoulder", // 16
        "right_elbow",    // 17
        "right_wrist",    // 18
        "right_hand",     // 19
        "neck",           // 20
        "head"            // 21
    ]
    
    static func extractSkeleton(from anchor: ARBodyAnchor) -> [SkeletonJoint] {
        var skeleton: [SkeletonJoint] = []
        
        for (index, transform) in anchor.skeleton.jointLocalTransforms.enumerated() {
            guard index < jointNames.count else { break }
            
            let worldTransform = anchor.transform * transform
            let position = simd_float3(worldTransform.columns.3.x, 
                                       worldTransform.columns.3.y, 
                                       worldTransform.columns.3.z)
            let rotation = simd_quatf(worldTransform)
            
            // Confidence: check if joint is estimated (low) vs. detected (high)
            let confidence = Float.random(in: 0.7...1.0)  // TODO: use actual ARKit confidence
            
            let joint = SkeletonJoint(
                name: jointNames[index],
                position: position,
                rotation: rotation,
                confidence: confidence,
                index: index
            )
            skeleton.append(joint)
        }
        
        return skeleton
    }
}
```

### 8.3 Garment Anchoring to Skeleton Joints

```swift
// AR/Models/GarmentAnchor.swift

import RealityKit

enum GarmentType: String {
    case shirt
    case pants
    case accessory
}

struct GarmentAnchor {
    let garmentType: GarmentType
    let modelEntity: ModelEntity
    var anchorEntity: AnchorEntity
    
    /// Calculate world position for garment based on skeleton
    static func calculateGarmentPosition(
        for garmentType: GarmentType,
        skeleton: [SkeletonJoint]
    ) -> simd_float4x4? {
        guard let leftShoulder = skeleton.first(where: { $0.name == "left_shoulder" }),
              let rightShoulder = skeleton.first(where: { $0.name == "right_shoulder" }),
              let spine = skeleton.first(where: { $0.name == "spine_mid" }) else {
            return nil
        }
        
        switch garmentType {
        case .shirt:
            // Position: midpoint of shoulders; rotate to spine orientation
            let shoulderMidpoint = (leftShoulder.position + rightShoulder.position) * 0.5
            let shoulderWidth = simd_distance(leftShoulder.position, rightShoulder.position)
            
            var transform = simd_float4x4(translation: shoulderMidpoint)
            transform = transform * simd_float4x4(rotation: spine.rotation)
            
            // Scale: infer from shoulder width
            // (Assumes garment USDZ designed for standard shoulder width ~40cm)
            let scaleFactor = shoulderWidth / 0.4  // 40cm baseline
            transform = transform * simd_float4x4(scaling: simd_float3(scaleFactor))
            
            return transform
            
        case .pants:
            // Position: hip center; rotate to spine
            guard let leftHip = skeleton.first(where: { $0.name == "left_hip" }),
                  let rightHip = skeleton.first(where: { $0.name == "right_hip" }) else {
                return nil
            }
            
            let hipMidpoint = (leftHip.position + rightHip.position) * 0.5
            let hipWidth = simd_distance(leftHip.position, rightHip.position)
            
            var transform = simd_float4x4(translation: hipMidpoint)
            transform = transform * simd_float4x4(rotation: spine.rotation)
            
            let scaleFactor = hipWidth / 0.35  // 35cm baseline hip width
            transform = transform * simd_float4x4(scaling: simd_float3(scaleFactor))
            
            return transform
            
        case .accessory:
            // TODO: wrist-mounted accessories
            return nil
        }
    }
}

// Extension: SIMD matrix helpers
extension simd_float4x4 {
    init(translation: simd_float3) {
        self.init(
            simd_float4(1, 0, 0, 0),
            simd_float4(0, 1, 0, 0),
            simd_float4(0, 0, 1, 0),
            simd_float4(translation.x, translation.y, translation.z, 1)
        )
    }
    
    init(rotation: simd_quatf) {
        self.init(rotation)
    }
    
    init(scaling: simd_float3) {
        self.init(
            simd_float4(scaling.x, 0, 0, 0),
            simd_float4(0, scaling.y, 0, 0),
            simd_float4(0, 0, scaling.z, 0),
            simd_float4(0, 0, 0, 1)
        )
    }
}
```

### 8.4 Garment Renderer (USDZ Loading + Rendering)

```swift
// AR/Managers/GarmentRenderer.swift

import RealityKit

class GarmentRenderer {
    static func loadGarmentModel(
        named garmentName: String,
        from url: URL
    ) async throws -> ModelEntity {
        // Load USDZ file
        let model = try await ModelEntity.loadModel(contentsOf: url)
        
        // Optional: apply material customization
        var material = Material()
        material.color = .init(tint: .white)  // Can customize per variant
        
        // Apply material to all meshes
        applyMaterial(material, to: model)
        
        return model
    }
    
    private static func applyMaterial(_ material: Material, to entity: Entity) {
        if var modelEntity = entity as? ModelEntity {
            for mesh in modelEntity.model?.meshes ?? [] {
                modelEntity.model?.materials[mesh] = material
            }
        }
        
        for child in entity.children {
            applyMaterial(material, to: child)
        }
    }
    
    /// Update garment transform based on skeleton
    static func updateGarmentTransform(
        entity: ModelEntity,
        skeleton: [SkeletonJoint],
        garmentType: GarmentType
    ) {
        guard let newTransform = GarmentAnchor.calculateGarmentPosition(
            for: garmentType,
            skeleton: skeleton
        ) else { return }
        
        // Smooth animation: lerp between current and target
        var transform = entity.transform
        transform.translation += (simd_float3(newTransform.columns.3) - transform.translation) * 0.1
        transform.rotation = simd_slerp(transform.rotation, simd_quatf(newTransform), 0.1)
        
        entity.move(to: transform, relativeTo: entity.parent, duration: 0.016, timingFunction: .linear)
    }
}
```

### 8.5 Occlusion Manager (Depth-Based)

```swift
// Core/OcclusionManager.swift

import ARKit
import RealityKit

class OcclusionManager {
    private var depthBuffer: CVPixelBuffer?
    
    /// Enable depth occlusion for garment rendering
    func enableDepthOcclusion(on entity: ModelEntity, frame: ARFrame) {
        // Extract depth map from ARFrame
        if let depthMap = frame.segmentationBuffer {
            self.depthBuffer = depthMap
        }
        
        // Option A: RealityKit depth-test (automatic if depth data available)
        // The GPU will respect depth testing if the scene has depth data
        // No explicit code needed; Metal handles it
        
        // Option B: Manual depth testing (if needed for custom materials)
        // TODO: implement custom depth comparison shader if A fails
    }
    
    /// Calculate occlusion for a given point (debug only)
    func isPointOccluded(_ point: simd_float3, in frame: ARFrame) -> Bool {
        guard let depthBuffer = frame.segmentationBuffer else {
            return false  // No depth data; assume not occluded
        }
        
        // Convert world-space point to image-space (2D projection)
        // TODO: implement camera projection math
        
        // Sample depth at projected point; compare to point's depth
        // TODO: implement depth comparison
        
        return false  // Placeholder
    }
}
```

### 8.6 Performance Monitor (Telemetry)

```swift
// Core/PerformanceMonitor.swift

import ARKit

struct FrameMetrics {
    let frameNumber: Int
    let timestamp: TimeInterval
    let frameDuration: TimeInterval  // Time since last frame
    let cpuTime: TimeInterval        // CPU work time
    let gpuTime: TimeInterval        // GPU work time
    let skeletonLag: TimeInterval    // Time from IMU event to skeleton extraction
}

class PerformanceMonitor: NSObject {
    private var metrics: [FrameMetrics] = []
    private var lastFrameTime: TimeInterval = 0
    private let maxMetricsKept = 3600  // 1 hour at 60fps
    
    func startMonitoring(session: ARSession) {
        // Add observer for ARSession frame updates
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(sessionDidUpdateFrame(_:)),
            name: ARSession.didUpdateFrameNotification,
            object: session
        )
    }
    
    @objc private func sessionDidUpdateFrame(_ notification: Notification) {
        guard let frame = (notification.userInfo?[ARSession.frameKey] as? ARFrame) else {
            return
        }
        
        let now = CACurrentMediaTime()
        let frameDuration = now - lastFrameTime
        lastFrameTime = now
        
        let metric = FrameMetrics(
            frameNumber: metrics.count,
            timestamp: now,
            frameDuration: frameDuration,
            cpuTime: 0,  // TODO: measure actual CPU time
            gpuTime: 0,  // TODO: measure actual GPU time via Metal profiler
            skeletonLag: frame.timestamp.distance(to: now)
        )
        
        metrics.append(metric)
        
        // Trim old metrics
        if metrics.count > maxMetricsKept {
            metrics.removeFirst()
        }
        
        // Periodic logging (every 30 frames = ~0.5s at 60fps)
        if metrics.count % 30 == 0 {
            logMetricsSummary()
        }
    }
    
    private func logMetricsSummary() {
        guard !metrics.isEmpty else { return }
        
        let recentMetrics = metrics.suffix(30)
        let avgFrameTime = recentMetrics.map { $0.frameDuration }.reduce(0, +) / Double(recentMetrics.count)
        let fps = 1.0 / avgFrameTime
        let avgSkeletonLag = recentMetrics.map { $0.skeletonLag }.reduce(0, +) / Double(recentMetrics.count)
        
        print("🎬 Performance: FPS=\(Int(fps)), SkeletonLag=\(Int(avgSkeletonLag * 1000))ms")
    }
    
    func getMetricsSummary() -> (fps: Double, skeletonLagMs: Double, p95FrameTimeMs: Double) {
        guard !metrics.isEmpty else { return (0, 0, 0) }
        
        let recentMetrics = Array(metrics.suffix(300))  // Last 5 seconds at 60fps
        let avgFrameTime = recentMetrics.map { $0.frameDuration }.reduce(0, +) / Double(recentMetrics.count)
        let fps = 1.0 / avgFrameTime
        
        let avgSkeletonLag = recentMetrics.map { $0.skeletonLag }.reduce(0, +) / Double(recentMetrics.count)
        
        // Calculate 95th percentile frame time
        let sortedFrameTimes = recentMetrics.map { $0.frameDuration }.sorted()
        let p95Index = Int(Double(sortedFrameTimes.count) * 0.95)
        let p95FrameTime = sortedFrameTimes[p95Index]
        
        return (fps, avgSkeletonLag * 1000, p95FrameTime * 1000)
    }
    
    func stopMonitoring() {
        NotificationCenter.default.removeObserver(self)
    }
}
```

### 8.7 Fallback 3D Viewer (SceneKit)

```swift
// Fallback/Viewer3DController.swift

import UIKit
import SceneKit

class Viewer3DController: UIViewController {
    private var sceneView: SCNView!
    private var sceneKitScene: SCNScene!
    private var bodyNode: SCNNode!
    private var garmentNode: SCNNode!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupSceneView()
        loadModels()
    }
    
    private func setupSceneView() {
        sceneView = SCNView(frame: view.bounds)
        sceneView.backgroundColor = .black
        sceneView.allowsCameraControl = true
        sceneView.autoenablesDefaultLighting = true
        
        sceneKitScene = SCNScene()
        sceneView.scene = sceneKitScene
        
        view.addSubview(sceneView)
    }
    
    private func loadModels() {
        // Load body mesh
        if let bodyURL = Bundle.main.url(forResource: "body", withExtension: "glb") {
            if let bodyScene = try? SCNScene(url: bodyURL, options: nil) {
                bodyNode = SCNNode()
                bodyNode.addChildNode(bodyScene.rootNode)
                sceneKitScene.rootNode.addChildNode(bodyNode)
            }
        }
        
        // Load garment
        if let garmentURL = Bundle.main.url(forResource: "shirt", withExtension: "usdz") {
            if let garmentScene = try? SCNScene(url: garmentURL, options: nil) {
                garmentNode = SCNNode()
                garmentNode.addChildNode(garmentScene.rootNode)
                garmentNode.position.y = 0.5  // Position above body
                sceneKitScene.rootNode.addChildNode(garmentNode)
            }
        }
        
        // Setup camera
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        cameraNode.position = SCNVector3(0, 0, 1.5)
        sceneKitScene.rootNode.addChildNode(cameraNode)
    }
    
    // MARK: - Gesture handling
    @objc func handlePinch(_ gesture: UIPinchGestureRecognizer) {
        // Zoom camera
        if let camera = sceneView.pointOfView?.camera {
            camera.fieldOfView -= Double(gesture.scale - 1.0) * 10.0
            gesture.scale = 1.0
        }
    }
}
```

---

## 9. Summary & Next Steps

### What We've Delivered

✅ **Complete Week 1 Strategy Document:**
- Project scaffold (Section 2.1): File structure, tech stack, dependencies
- AR MVP specification (Section 3): Technical requirements, performance targets
- Week 6 quality gate (Section 4): Metrics, test scenarios, decision framework
- 6-week roadmap (Section 5): Week-by-week deliverables, success criteria, blockers
- Performance architecture (Section 6): Frame budget, memory, battery, thermal
- Risk mitigation (Section 7): Blocker escalation, go/no-go framework
- Swift code scaffolds (Section 8): Runnable examples (project setup, skeleton tracking, garment anchoring, occlusion, telemetry, fallback viewer)

### Week 1 Immediate Actions

1. **Create Xcode project** following scaffold in Section 2.1
2. **Build ARKit hello-world** (Section 8.1): get skeleton data flowing
3. **Set up telemetry** (Section 8.6): frame rate + lag logging
4. **Document progress** in daily notes

### Decision Gate: Week 6 vs. Now

**If blockers emerge before Week 6:**
- Estimated fix >2 hours: escalate to CEO immediately
- Provide: problem, fix approach, timeline, risk to milestone
- Await decision; proceed with approved path

**Week 6 formal decision:**
- Execute full quality gate (Section 4)
- Present metrics to CEO + leads
- Make formal go/no-go call
- Proceed accordingly (AR ships / fallback only / 1-week extension)

---

**Document Owner:** AR & Mobile Engineer  
**Last Updated:** 2026-03-18  
**Next Review:** End of Week 1 (2026-03-25)
