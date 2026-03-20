# ARKit Setup & Quick-Start Guide

**Date:** 2026-03-18  
**Status:** Practical Week 1 Reference  
**Audience:** AR & Mobile team starting Xcode project

---

## Quick Start (First 2 Hours)

### 1. Create Xcode Project

```bash
# Command line (recommended)
cd ~/Projects
mkdir FashionTryOn-iOS
cd FashionTryOn-iOS

# Then in Xcode:
# File → New → Project
# iOS → App
# Project name: FashionTryOn
# Organization identifier: com.fashiontech
# Interface: SwiftUI
# Life Cycle: SwiftUI App
# Minimum deployment: iOS 16
```

### 2. Add Frameworks

**In Xcode:**
1. Select `FashionTryOn` target
2. Build Phases → Link Binary With Libraries
3. Add:
   - ARKit.framework (iOS 11+)
   - RealityKit.framework (iOS 15+)
   - SceneKit.framework (for fallback)

**In Package.swift (optional, for SPM):**
```swift
// No external dependencies in Week 1
// Use only Apple frameworks
```

### 3. Check Device Capability

**Before building:**
```swift
// In DeviceCheck.swift
import ARKit

func checkARSupport() {
    if ARBodyTrackingConfiguration.isSupported {
        print("✅ Device supports body tracking (A12+)")
    } else {
        print("❌ Device does not support body tracking")
        print("   Requires: iPhone XS, XS Max, or later (A12 Bionic+)")
    }
}
```

### 4. Build & Run on Device

```bash
# Terminal
cd ~/Projects/FashionTryOn-iOS
xcodebuild -scheme FashionTryOn -destination 'platform=iOS,name=iPhone 14 Pro' build

# Or use Xcode UI:
# Select device → Run (Cmd+R)
```

**Expected output:** App launches, no crashes, ARKit session initializes.

---

## ARKit Initialization (Copy-Paste Ready)

### FashionTryOnApp.swift

```swift
import SwiftUI

@main
struct FashionTryOnApp: App {
    @StateObject private var coordinator = ARCoordinator()
    
    var body: some Scene {
        WindowGroup {
            MainView()
                .environmentObject(coordinator)
        }
    }
}
```

### MainView.swift

```swift
import SwiftUI

struct MainView: View {
    @EnvironmentObject var coordinator: ARCoordinator
    
    var body: some View {
        if coordinator.isSupported {
            ARViewContainer()
                .environmentObject(coordinator)
        } else {
            Text("AR not supported on this device")
                .font(.headline)
        }
    }
}
```

### ARViewContainer.swift

```swift
import SwiftUI
import RealityKit
import ARKit

struct ARViewContainer: UIViewControllerRepresentable {
    @EnvironmentObject var coordinator: ARCoordinator
    
    func makeUIViewController(context: Context) -> ARViewController {
        return ARViewController(coordinator: coordinator)
    }
    
    func updateUIViewController(_ controller: ARViewController, context: Context) {
        // Update if needed
    }
}

class ARViewController: UIViewController, ARSessionDelegate {
    let coordinator: ARCoordinator
    var arView: ARView?
    
    init(coordinator: ARCoordinator) {
        self.coordinator = coordinator
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Create ARView
        arView = ARView(frame: view.bounds)
        guard let arView = arView else { return }
        view.addSubview(arView)
        
        // Configure ARKit
        let configuration = ARBodyTrackingConfiguration()
        if ARWorldTrackingConfiguration.isSupported {
            configuration.frameSemantics.insert(.personSegmentationWithDepth)
        }
        
        // Run session
        arView.session.run(configuration)
        
        print("✅ AR session started successfully")
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        arView?.session.pause()
    }
}
```

---

## Frame-by-Frame ARKit Flow

```
viewDidLoad()
    ↓
ARBodyTrackingConfiguration created
    ↓
arView.session.run(configuration)
    ↓
Every 16ms (60fps):
    ├── ARFrame captured from camera + IMU
    ├── ARBodyAnchor extracted (skeleton joints)
    ├── BodyTracker.extractSkeleton(anchor) → [SkeletonJoint]
    ├── GarmentAnchor.calculateGarmentPosition(skeleton) → transform
    ├── GarmentRenderer.updateGarmentTransform(entity, skeleton)
    ├── PerformanceMonitor.log(frameTime, skeletonLag)
    └── RealityKit renders frame to screen
```

---

## Debugging: Print Skeleton Data

**In your session delegate:**

```swift
class ARViewController: UIViewController, ARSessionDelegate {
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        // Extract body anchor
        guard let bodyAnchor = frame.anchors.compactMap({ $0 as? ARBodyAnchor }).first else {
            return
        }
        
        let skeleton = BodyTracker.extractSkeleton(from: bodyAnchor)
        
        // Print joints (at 10fps to avoid spam; 1/6 frames)
        if Int(Date().timeIntervalSince1970 * 10) % 6 == 0 {
            for joint in skeleton.prefix(5) {  // Print first 5 joints
                print("📍 \(joint.name): pos=\(joint.position), conf=\(joint.confidence)")
            }
        }
    }
}
```

**Expected output:**
```
📍 root: pos=SIMD3(0.05, 0.3, -1.2), conf=0.95
📍 left_shoulder: pos=SIMD3(-0.15, 0.8, -1.1), conf=0.92
📍 right_shoulder: pos=SIMD3(0.15, 0.8, -1.1), conf=0.93
... (etc)
```

---

## Performance Profiling (Instruments)

### Measure Frame Rate

1. **Build on device**
2. **Xcode → Product → Profile (Cmd+I)**
3. **Select "System Trace"**
4. **Hit "Record"**
5. **Wait 30 seconds**
6. **Stop**
7. **Look at track:**
   - **FPS counter:** 60fps? 55fps? 50fps?
   - **GPU utilization:** <80%?
   - **CPU utilization:** <60%?

### Measure Skeleton Lag

1. **Enable telemetry logging in PerformanceMonitor**
2. **Export metrics CSV**
3. **Plot frame_time + skeleton_lag in Excel**
4. **Check p95 values**

**Target:** skeleton_lag <150ms (p95)

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Module not found: RealityKit" | iOS target <15 | Set min deployment to 16+ |
| "ARBodyTrackingConfiguration unsupported" | Device too old | Test on iPhone 12+ only |
| App crashes on `arView.session.run()` | Camera permission denied | Request permissions in Info.plist |
| ARView is black/empty | No anchors found | Move camera around; ensure good lighting |
| Frame rate drops to 30fps | GPU overload | Reduce mesh complexity; enable LOD |

---

## Git Workflow (Week 1)

```bash
# Initialize repo
git init
git add .
git commit -m "Initial ARKit scaffold"

# Create main branch (protected)
git branch -M main
git remote add origin https://github.com/fashiontech/ios-ar.git
git push -u origin main

# Daily commits (end of day)
git add .
git commit -m "Day X: [feature] - details"
git push
```

---

## Info.plist Permissions

**Required for ARKit + camera access:**

```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to scan your body and show virtual try-ons in real-time.</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Location helps us provide better light estimation for realistic AR.</string>

<key>UIRequiredDeviceCapabilities</key>
<array>
    <string>arkit</string>
    <string>front-facing-camera</string>
</array>

<key>MinimumOSVersion</key>
<string>16.0</string>
```

---

## Next Steps (Week 1 → Week 2)

- [ ] Xcode project builds without warnings
- [ ] ARKit session runs on device without crashes
- [ ] Frame profiler shows 60fps capture
- [ ] Skeleton data printing to console
- [ ] Performance monitor logging frame times
- [ ] Commit all code to Git

**Blockers (escalate >2h):**
- ARKit initialization fails (permission, device, framework)
- Frame rate <50fps (GPU/CPU bottleneck)
- Skeleton data missing (ARBodyAnchor not found)

---

## Useful Xcode Shortcuts

| Action | Shortcut |
|--------|----------|
| Build | Cmd+B |
| Build + Run | Cmd+R |
| Stop | Cmd+. |
| Profile | Cmd+I |
| Console Output | Cmd+Shift+C |
| Debug View Hierarchy | Debug → View Hierarchy |
| Pause Execution | Debug → Pause |
| Frame Debugger | Debug → Metal Frame Capture |

---

## Resources

- **ARKit Documentation:** https://developer.apple.com/arkit/
- **RealityKit Guide:** https://developer.apple.com/realitykit/
- **WWDC 2022 "Detect Body Pose with Vision":** https://developer.apple.com/videos/play/wwdc2022/10069
- **Xcode Profiling Guide:** https://developer.apple.com/videos/play/wwdc2021/10211/

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-18  
**Next Update:** End of Week 1
