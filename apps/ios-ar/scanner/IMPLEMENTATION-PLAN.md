# iOS Scan App v0.1 — Implementation Plan
**Author:** fashion-scanning  
**Sprint:** 1  
**Date:** 2026-03-18  
**Status:** Stub ready — full Xcode build pending Apple dev account + physical LiDAR device

---

## Overview

The app captures a full-body LiDAR point cloud using ARKit on iPhone 12 Pro+ / iPad Pro (2020+),
exports a `.ply` file to local storage, and surfaces a share sheet for transfer to the backend pipeline.

---

## Architecture

```
ScanViewController         — ARKit session management, depth frame capture, UI
  └─ PointCloudAccumulator — merges ARFrame depth maps into a unified point set
  └─ PointCloudExporter    — serialises accumulated points → .ply (ASCII or binary)
  └─ ScanSessionManager    — manages start/pause/stop lifecycle, writes metadata
```

---

## Key Files

| File | Purpose |
|------|---------|
| `ScanViewController.swift` | Root view controller — starts ARSession, handles UI |
| `PointCloudAccumulator.swift` | Accumulates simd_float3 points from ARFrame.sceneDepth |
| `PointCloudExporter.swift` | Writes accumulated cloud to ASCII PLY on disk |
| `ScanSessionManager.swift` | Lifecycle controller — sceneDepth guard, file naming |
| `ScanApp.swift` | @main entry point, scene delegate |
| `Info.plist` | Privacy – Camera Usage, Privacy – Motion Usage |

---

## ARKit LiDAR Session Setup

```swift
let config = ARWorldTrackingConfiguration()
// Require LiDAR depth
guard ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) else {
    fatalError("LiDAR not available on this device")
}
config.sceneReconstruction = .meshWithClassification
config.frameSemantics = [.sceneDepth, .smoothedSceneDepth]
session.run(config)
```

### Minimum deployment target
- iOS 14.0+
- Requires device: iPhone 12 Pro, 13/14/15 Pro, iPad Pro 2020+

---

## ARFrame Depth Capture

Each frame delivers `ARFrame.sceneDepth?.depthMap` (CVPixelBuffer, float32 metres).  
We also use `ARFrame.camera.transform` to project depth pixels into world space:

```swift
func extractPoints(from frame: ARFrame) -> [simd_float3] {
    guard let depthMap = frame.sceneDepth?.depthMap else { return [] }
    let intrinsics = frame.camera.intrinsics          // 3×3 matrix
    let viewTransform = frame.camera.transform        // 4×4 world transform
    // Iterate depth pixels at stride (e.g. every 4th px for perf)
    // For each pixel (u,v) with depth d:
    //   local = simd_float3((u - cx)/fx, (v - cy)/fy, 1) * d
    //   world = (viewTransform * simd_float4(local, 1)).xyz
    // Append world point
}
```

**Capture strategy:** accumulate frames while user slowly rotates 360° around subject.  
Target: ~60–120 frames → ~200k–500k points before downsampling.

---

## PLY Export

Binary little-endian PLY keeps file sizes manageable (~5–15 MB for 200k points).

### PLY Header (ASCII)
```
ply
format binary_little_endian 1.0
element vertex N
property float x
property float y
property float z
end_header
[binary data]
```

`PointCloudExporter` writes this header then appends raw `Float32 × 3` per point.

---

## File Naming & Storage

```
Documents/Scans/
  scan-{UUID}-{ISO8601}.ply
  scan-{UUID}-{ISO8601}-meta.json   ← { device, ios_version, capture_duration_s, point_count }
```

On export complete, `UIActivityViewController` is presented so the user can AirDrop / Files / share.

---

## Sprint 2 Handoffs

- `.ply` file produced here feeds directly into `pipeline/scanning/process_scan.py`
- `scan_id` = UUID string shared between iOS metadata JSON and `measurements.json` / `joints.json`
- Sprint 2 / 3: add direct HTTPS upload to FastAPI `/scans/upload` endpoint

---

## Blockers

1. **Apple Developer Account** — required to sign and deploy to a physical LiDAR device.  
   Simulator does not support ARKit depth — can't test on sim.
2. **Physical LiDAR device** — iPhone 12 Pro or later / iPad Pro 2020+.
3. **Xcode 15+** — required for RealityKit / ARKit LiDAR APIs at target iOS 16+.

No CLO3D dependency at this stage.
