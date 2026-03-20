# DEVICE_LOG.md — iPhone LiDAR Hardware Test Log

**Project:** Fashion Tech 3D Scanning  
**Sprint:** 1 | **Week:** 2 (Mar 25–29, 2026)  
**Author:** 3D Scanning Lead  
**Status:** ⚠️ AWAITING REAL DEVICE — Synthetic validation complete

---

## Hardware Provisioning Status

| Device | Status | Notes |
|--------|--------|-------|
| iPhone 12 Pro (A2341) | ⏳ Pending founder provision | Required for real LiDAR capture |
| iPhone 13 Pro (A2483) | ⏳ Optional stretch | Higher quality LiDAR sensor |
| iPhone 14 Pro (A2650) | ⏳ Optional stretch | Best LiDAR depth accuracy |

**Blocker:** Founder (Seb) must provision iPhone 12 Pro+ with LiDAR before real capture sessions begin.  
**Risk Level:** P1 — blocks real scan capture; pipeline validated on synthetic data pending resolution.

---

## LiDAR Hardware Specifications (Reference)

### iPhone 12 Pro — Minimum Supported
- **LiDAR Scanner:** Time-of-Flight (ToF), 15cm–5m range
- **Point Cloud Density:** ~35,000 pts/frame at 1m distance
- **Depth Accuracy:** ±3mm at 1m, ±8mm at 3m (Apple spec)
- **Frame Rate:** 30fps (depth + RGB fused)
- **iOS Minimum:** iOS 14.0+

### iPhone 13 Pro
- **LiDAR Scanner:** Improved ToF, same range spec
- **Point Cloud Density:** ~45,000 pts/frame at 1m distance
- **Depth Accuracy:** ±2.5mm at 1m (improved sensor)
- **Frame Rate:** 30fps + ProMotion RGB (120Hz)

### iPhone 14 Pro / 15 Pro
- **LiDAR Scanner:** Latest ToF generation
- **Depth Accuracy:** ±2mm at 1m
- **Additional:** Better noise floor in low-light

---

## iOS Version Requirements

| iOS Version | ARKit Version | LiDAR Support | Recommended |
|-------------|---------------|----------------|------------|
| iOS 14.0–14.x | ARKit 4 | ✅ Basic | Minimum |
| iOS 15.0–15.x | ARKit 5 | ✅ Improved | Good |
| iOS 16.0–16.x | ARKit 6 | ✅ Scene Reconstruction | Better |
| iOS 17.x+ | ARKit 6.x | ✅ Full | Recommended |
| iOS 18.x | ARKit 6.x | ✅ Full | Best |

**Required APIs:**
- `ARWorldTrackingConfiguration` with `sceneReconstruction: .meshWithClassification`
- `ARDepthData` (LiDAR only, not available on non-LiDAR devices)
- `ARFrame.capturedDepthData` — fused depth map
- `ARFrame.capturedImage` — RGB reference

---

## Real Device Testing Protocol (Ready to Execute)

When iPhone is provisioned, follow this protocol:

### Pre-Capture Checklist
- [ ] iPhone charged >80%
- [ ] iOS version ≥ iOS 16.0
- [ ] App installed via TestFlight or Xcode direct
- [ ] Permissions granted: Camera, Motion
- [ ] Scanning area: 4m × 4m clear space, no glass/mirrors nearby
- [ ] Lighting: Diffuse ambient, ≥300 lux (no harsh directional light)

### Capture Protocol Per Subject
1. Subject stands in T-pose, arms at ~45° from body
2. Operator circles at 1.5m–2.0m distance
3. Start: head level, move slowly clockwise (1 revolution = ~15 seconds)
4. Capture 3 passes: head level, chest level, hip level
5. Total capture time: 30–45 seconds
6. Export .ply immediately after capture

### Manual Measurement (Ground Truth)
Take with cloth tape measure, subject in same T-pose:
- **Chest:** Fullest point, under arms, horizontal
- **Waist:** Narrowest point, typically 2–3cm above navel
- **Hip:** Fullest point, typically 20cm below waist
- **Shoulder Width:** Acromion to acromion, across upper back

---

## Planned Test Subjects

| ID | Gender | Size Est. | Chest (manual) | Waist (manual) | Hip (manual) | Scheduled |
|----|--------|-----------|----------------|----------------|--------------|-----------|
| subject_001 | M | L | TBD | TBD | TBD | Day 1 — Seb (founder) |
| subject_002 | TBD | M | TBD | TBD | TBD | Day 2 |
| subject_003 | TBD | S | TBD | TBD | TBD | Day 2 |
| subject_004 | TBD | XL | TBD | TBD | TBD | Day 3 |
| subject_005 | TBD | XS | TBD | TBD | TBD | Day 3 |

*(Subject rows populated when real sessions occur)*

---

## Capture Condition Documentation Template

```
Session ID: scan_YYYYMMDD_NNN
Date/Time: 
Device: iPhone [model] | iOS [version]
Operator: 
Subject ID: 

Environment:
  Location: [indoor/outdoor]
  Lighting: [approx lux, type]
  Temperature: [°C]
  Clearance: [meters available around subject]

Capture:
  Distance: [m]
  Speed: [fast/normal/slow]
  Passes: [1/2/3]
  Duration: [seconds]
  Anomalies: [any issues during capture]

Export:
  File: [filename.ply]
  Size: [MB]
  Point count: [approx]
  Export time: [seconds]
```

---

## Synthetic Test Environment (Current — Week 2 Pre-Device)

Used for pipeline validation until real device provisioned:

| Scan ID | Source | Description | Points |
|---------|--------|-------------|--------|
| synthetic_subject_001.ply | Generated | Male L body approximation | 89,420 |
| synthetic_subject_002.ply | Generated | Female M body approximation | 76,315 |
| synthetic_subject_003.ply | Generated | Male XL body approximation | 94,882 |

**Generator:** Python + NumPy parametric body model (cylinder approximations for torso segments)  
**Purpose:** Validate measurement extraction pipeline before real hardware is available  
**Limitation:** Smooth geometry, no real-world noise; accuracy numbers not representative of real LiDAR performance

---

## Known LiDAR Failure Modes (Documented for Sprint 3 AR Planning)

1. **Specular surfaces:** Glass, mirrors, metallic fabric → depth dropout
2. **Black/dark fabrics:** Light absorption → sparse point cloud
3. **Hair:** Fine structure below LiDAR resolution → mesh artifacts
4. **Thin limbs (wrists, ankles):** May be truncated at low point density
5. **Low lighting (<200 lux):** Increased depth noise → higher MAE
6. **Subject movement:** Drift accumulation → frame misalignment
7. **Distance >3m:** Accuracy degrades to ±8mm+ (exceeds gate threshold)

---

*Last updated: 2026-03-19 | Status: Awaiting device provisioning from founder*
