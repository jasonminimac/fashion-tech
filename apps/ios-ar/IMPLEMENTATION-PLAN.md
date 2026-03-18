# ARKit Body Tracking — Implementation Plan
**Engineer:** Fashion Tech AR (sprint1-ar)
**Sprint:** 1 — Pipeline Skeleton
**Target:** iPhone 12, iOS 14+, ≥30fps, 91 joints logged to console

---

## 1. Requirements

| Requirement | Value |
|---|---|
| Device | iPhone 12 or later (A14 Bionic, LiDAR not required for body tracking) |
| Minimum iOS | 14.0 |
| Xcode | 13+ |
| Frameworks | ARKit, RealityKit (or SceneKit), AVFoundation |
| Privacy key | `NSCameraUsageDescription` in Info.plist |

> ⚠️ **Body tracking requires a physical device.** The simulator does NOT support `ARBodyTrackingConfiguration`.

---

## 2. Xcode Project Setup

1. Create a new iOS App project in Xcode (Swift, UIKit lifecycle)
2. Target: iPhone, iOS 14.0+
3. Add to `Info.plist`:
   - `NSCameraUsageDescription` → "Body tracking requires camera access."
4. Link frameworks: ARKit is auto-linked; no manual linking needed
5. Ensure `Capabilities → Camera` is enabled (or Privacy Manifest for iOS 17+)

---

## 3. Session Configuration

```swift
import ARKit

let configuration = ARBodyTrackingConfiguration()

// Optional tuning
configuration.frameSemantics = [] // No depth — body tracking only
configuration.videoFormat = ARBodyTrackingConfiguration.supportedVideoFormats
    .first(where: { $0.framesPerSecond >= 60 }) ?? ARBodyTrackingConfiguration.supportedVideoFormats[0]
```

Check availability before use:
```swift
guard ARBodyTrackingConfiguration.isSupported else {
    fatalError("Body tracking not supported on this device")
}
```

---

## 4. Session Delegate & Body Anchor Parsing

Implement `ARSessionDelegate` (or `ARSCNViewDelegate` which inherits it):

```swift
func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
    for anchor in anchors {
        guard let bodyAnchor = anchor as? ARBodyAnchor else { continue }
        JointLogger.log(bodyAnchor: bodyAnchor, frameIndex: frameCounter)
    }
}
```

`ARBodyAnchor.skeleton` is an `ARSkeleton3D` with:
- `.jointModelTransforms` — array of `simd_float4x4` in body-local space
- `.jointNames` — static list of all 91 joint name strings

---

## 5. Iterating All 91 Joints

```swift
let skeleton = bodyAnchor.skeleton
let jointNames = ARSkeletonDefinition.defaultBody3D.jointNames  // 91 entries

for (index, name) in jointNames.enumerated() {
    let transform = skeleton.jointModelTransforms[index]
    let position = simd_make_float3(transform.columns.3)
    print("[JOINT] frame=\(N) joint=\(name) x=\(position.x) y=\(position.y) z=\(position.z)")
}
```

**The 91 joint names** come from `ARSkeletonDefinition.defaultBody3D.jointNames`. Key joints include:
- `root`, `hips_joint`
- `left_leg_joint`, `right_leg_joint`
- `left_foot_joint`, `right_foot_joint`
- `spine_1_joint` through `spine_7_joint`
- `left_shoulder_1_joint`, `right_shoulder_1_joint`
- `left_hand_joint`, `right_hand_joint`
- `head_joint`, `neck_1_joint`
- All finger joints (left/right × 5 fingers × ~4 joints = ~40 finger joints)

---

## 6. Performance Targets

| Metric | Target | Notes |
|---|---|---|
| Frame rate | ≥30fps | ARKit body tracking runs at device camera fps (up to 60fps) |
| Tracking latency | <200ms | Measured from motion to logged position |
| Joint count | 91 | All joints from `ARSkeletonDefinition.defaultBody3D` |
| Log throughput | ~2730 lines/sec at 30fps | Buffer/throttle for production; fine for prototype |

---

## 7. Architecture

```
BodyTrackingViewController
│
├── ARSCNView (or ARView/RealityKit)
│   └── ARSession
│       └── ARBodyTrackingConfiguration
│
├── ARSCNViewDelegate / ARSessionDelegate
│   └── session(_:didUpdate anchors:)
│       └── JointLogger.log(bodyAnchor:frameIndex:)
│
└── JointLogger
    ├── Iterates ARSkeletonDefinition.defaultBody3D.jointNames
    └── Prints [JOINT] frame=N joint=X x= y= z=
```

---

## 8. File Structure (Minimal Xcode Project)

```
apps/ios-ar/
├── ios-ar.xcodeproj/          ← Xcode project (create manually in Xcode)
├── ios-ar/
│   ├── AppDelegate.swift
│   ├── SceneDelegate.swift
│   ├── BodyTrackingViewController.swift
│   ├── JointLogger.swift
│   └── Info.plist
└── IMPLEMENTATION-PLAN.md
```

---

## 9. Sprint 3 Go/No-Go Signals — Early Assessment

### ✅ Green signals
- ARKit body tracking on iPhone 12 is well-proven; Apple ships it in iOS Fitness+ and Measure app
- 91-joint skeleton (`ARSkeletonDefinition.defaultBody3D`) is stable API since iOS 14
- Achievable ≥30fps: ARKit body tracking runs at camera rate, typically 30–60fps on A14+
- <200ms latency: ARKit processes on-device; typical latency ~50–100ms

### ⚠️ Watch items for Sprint 2/3
- **People occlusion** requires `frameSemantics = [.personSegmentationWithDepth]` and costs ~3–5fps; needs profiling on device
- **Garment drape rendering** is a separate system (RealityKit physics or custom shader); not in scope Sprint 1 but plan for it early
- **Apple developer account required** to run on device — no simulator support for body tracking. If no provisioned device is available, Sprint 1 cannot be hardware-validated in CI/CD

### 🔴 Blockers to flag now
- Physical iPhone 12+ with Apple developer account provisioning is **mandatory** for any live test
- No simulator path exists for `ARBodyTrackingConfiguration`
- If garment drape needs real-time cloth simulation, consider RealityKit's `PhysicsBodyComponent` (limited) vs custom Metal shader approach — decide by Sprint 2

---

## 10. Next Steps (Sprint 2)

1. Build Xcode project, run on device, confirm 91 joints print at ≥30fps
2. Add `ARSCNView` scene node per joint for visual debug overlay
3. Integrate people occlusion (`personSegmentationWithDepth`) and profile fps cost
4. Begin garment anchor research: map `left_shoulder_1_joint` + `right_shoulder_1_joint` as garment root

---

*Plan authored by fashion-ar, 2026-03-18*
