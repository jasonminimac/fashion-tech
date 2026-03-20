# iOS Project Scaffold — Detailed Structure & Rationale

**Date:** 2026-03-18  
**Status:** Reference Document for Week 1  
**Purpose:** Xcode project setup guide for AR & Mobile team

---

## Full Project Structure

```
FashionTryOn-iOS/
│
├── FashionTryOn.xcodeproj/
│   ├── project.pbxproj
│   └── xcshareddata/
│       └── xcschemes/
│           ├── FashionTryOn.xcscheme
│           └── FashionTryOnTests.xcscheme
│
├── FashionTryOn/
│   ├── Supporting Files/
│   │   ├── Info.plist
│   │   ├── Localizable.strings
│   │   └── Config.xcconfig
│   │
│   ├── App/
│   │   ├── FashionTryOnApp.swift          # Entry point (SwiftUI)
│   │   ├── AppDelegate.swift              # Lifecycle management
│   │   ├── SceneDelegate.swift            # Scene setup
│   │   └── RootView.swift                 # Main app container
│   │
│   ├── Core/
│   │   ├── ARCoordinator.swift            # ARKit + RealityKit orchestration
│   │   │   └── Responsibilities:
│   │   │       • Initialize ARSession with body tracking
│   │       • Route frame updates to components
│   │   │       • Pause/resume session lifecycle
│   │   │
│   │   ├── BodyTracker.swift              # Skeleton extraction from ARBodyAnchor
│   │   │   └── Responsibilities:
│   │   │       • Parse ARKit skeleton joints (19 joints)
│   │   │       • Convert local → world transforms
│   │   │       • Calculate joint confidence
│   │   │
│   │   ├── ModelManager.swift             # USDZ/GLB loading + caching
│   │   │   └── Responsibilities:
│   │   │       • Load USDZ from URL (network or bundle)
│   │   │       • Cache models in memory (LRU eviction)
│   │   │       • Handle load errors gracefully
│   │   │
│   │   ├── PerformanceMonitor.swift       # Frame rate + latency telemetry
│   │   │   └── Responsibilities:
│   │   │       • Log frame times (FPS histogram)
│   │   │       • Calculate skeleton lag (IMU → visual)
│   │   │       • Periodically dump metrics to console + file
│   │   │       • Detect performance drops (trigger fallback)
│   │   │
│   │   └── OcclusionManager.swift         # Depth-based occlusion handling
│   │       └── Responsibilities:
│   │           • Enable depth occlusion on garment entities
│   │           • Manage depth buffer from ARFrame
│   │           • Debug occlusion correctness
│   │
│   ├── AR/
│   │   ├── Views/
│   │   │   ├── ARViewContainer.swift      # RealityKit ARView wrapper
│   │   │   │   └── SwiftUI bridge: embed ARView in SwiftUI
│   │   │   ├── AROverlayView.swift        # UI overlays (hints, loading)
│   │   │   │   └── FPS counter, garment picker UI, quality warnings
│   │   │   └── DebugMetricsView.swift     # On-screen FPS/lag display
│   │   │       └── Real-time telemetry overlay (optional, debug only)
│   │   │
│   │   ├── Models/
│   │   │   ├── ARSession.swift            # Session state machine
│   │   │   │   └── States: initializing, running, paused, failed
│   │   │   ├── GarmentAnchor.swift        # Garment positioning logic
│   │   │   │   └── Calculate transform based on skeleton joints
│   │   │   └── SkeletonJoint.swift        # Joint metadata + helpers
│   │   │       └── Position, rotation, confidence, name
│   │   │
│   │   └── Managers/
│   │       ├── ARSessionManager.swift     # Session lifecycle
│   │       │   └── Initialize, run, pause, resume, error handling
│   │       ├── GarmentRenderer.swift      # USDZ rendering + materials
│   │       │   └── Load, render, animate garment; apply material swaps
│   │       └── LightingManager.swift      # Scene lighting (3-point setup)
│   │           └── Key light, fill light, rim light configuration
│   │
│   ├── BodyModel/
│   │   ├── BodySkeletonView.swift         # 2D skeleton debug overlay
│   │   │   └── Draw joints/limbs on screen (debug only)
│   │   ├── BodyMesh.swift                 # 3D body mesh (optional)
│   │   │   └── Render semi-transparent body for occlusion debugging
│   │   └── JointCalculator.swift          # Skeleton math utilities
│   │       └── Distance, angle, orientation calculations
│   │
│   ├── Fallback/
│   │   ├── Viewer3DController.swift       # SceneKit 3D viewer
│   │   │   └── Gesture-based 3D model viewing (pan, pinch, rotate)
│   │   ├── Viewer3DModels.swift           # Model loading for fallback
│   │   │   └── Load GLB/USDZ for non-AR display
│   │   └── ViewerContainer.swift          # SwiftUI wrapper for UIViewController
│   │       └── Bridge SceneKit → SwiftUI
│   │
│   ├── Networking/
│   │   ├── APIClient.swift                # HTTP request layer
│   │   │   └── Generic GET/POST with error handling
│   │   └── GarmentAPI.swift               # Garment catalog endpoint
│   │       └── Fetch garments, download USDZ, post try-on data
│   │
│   ├── Telemetry/
│   │   ├── AnalyticsLogger.swift          # Event tracking (optional)
│   │   │   └── Track user actions (app open, garment selected, etc.)
│   │   ├── PerformanceLogger.swift        # FPS + latency persistent logging
│   │   │   └── Write metrics to local file for Week 6 analysis
│   │   └── QualityGateReporter.swift      # Week 6 metrics submission
│   │       └── Format + serialize metrics for CEO review
│   │
│   ├── UI/
│   │   ├── MainView.swift                 # App entry decision
│   │   │   └── Route to AR or Fallback based on capability
│   │   ├── GarmentSelectorView.swift      # Garment picker grid
│   │   │   └── Browse, filter, select garments
│   │   └── OnboardingView.swift           # First-run setup
│   │       └── Permissions request (camera, LiDAR), intro screens
│   │
│   ├── Utils/
│   │   ├── DeviceCheck.swift              # ARKit capability detection
│   │   │   └── Check A12+, ARKit version, body tracking support
│   │   ├── PermissionManager.swift        # Camera + LiDAR permissions
│   │   │   └── Request, check, handle denial
│   │   └── ConfigManager.swift            # Environment config
│   │       └── API base URL, telemetry settings, feature flags
│   │
│   ├── Assets/
│   │   ├── Assets.xcassets/
│   │   │   ├── AppIcon.appiconset/
│   │   │   ├── Colors/
│   │   │   └── Images/
│   │   └── Models/
│   │       ├── sample_shirt.usdz          # Test garment
│   │       ├── sample_pants.usdz
│   │       └── sample_body.glb            # Fallback viewer body
│   │
│   └── Localization/
│       ├── en.lproj/
│       │   └── Localizable.strings
│       └── es.lproj/ (future)
│
├── FashionTryOnTests/
│   ├── Core/
│   │   ├── ARCoordinatorTests.swift       # ARKit initialization tests
│   │   ├── BodyTrackerTests.swift         # Skeleton extraction unit tests
│   │   ├── OcclusionManagerTests.swift    # Occlusion logic tests
│   │   └── PerformanceMonitorTests.swift  # Telemetry tests
│   │
│   ├── AR/
│   │   ├── GarmentRendererTests.swift     # Model loading tests
│   │   └── LightingManagerTests.swift     # Lighting setup tests
│   │
│   ├── Networking/
│   │   └── APIClientTests.swift           # HTTP mock tests
│   │
│   └── Utils/
│       └── DeviceCheckTests.swift         # Capability detection tests
│
├── FashionTryOnUITests/
│   ├── ARViewTests.swift                  # AR view integration tests
│   ├── FallbackViewerTests.swift          # 3D viewer gesture tests
│   └── GarmentSelectionTests.swift        # UI flow tests
│
├── Fastfile (optional)                    # CI/CD build automation
├── .gitignore
├── README.md
└── LICENSE
```

---

## Module Responsibilities (One Sentence Each)

### Core Layer
- **ARCoordinator**: Manages ARKit session lifecycle and frame distribution.
- **BodyTracker**: Extracts and transforms skeleton joint data from ARBodyAnchor.
- **ModelManager**: Loads, caches, and manages 3D model entities (USDZ/GLB).
- **PerformanceMonitor**: Logs frame times, skeleton latency, and detects performance issues.
- **OcclusionManager**: Applies depth-based occlusion to garment rendering.

### AR Layer
- **ARViewContainer**: SwiftUI wrapper around RealityKit's ARView.
- **AROverlayView**: Displays UI hints, loading states, and controls over AR.
- **DebugMetricsView**: Real-time on-screen FPS and latency counter (dev only).
- **ARSession**: State machine for AR workflow (init → running → paused → error).
- **GarmentAnchor**: Calculates garment position/rotation based on skeleton joints.
- **SkeletonJoint**: Data model for individual joint (position, rotation, confidence).
- **ARSessionManager**: Handles session initialization, error recovery, permissions.
- **GarmentRenderer**: Loads USDZ, applies materials, manages rendering pipeline.
- **LightingManager**: Sets up 3-point lighting for realistic garment appearance.

### Body Model Layer
- **BodySkeletonView**: Renders 2D skeleton overlay for debugging.
- **BodyMesh**: Optional 3D semi-transparent body mesh for occlusion visualization.
- **JointCalculator**: Helper functions for skeleton math (distance, angles, etc.).

### Fallback Layer
- **Viewer3DController**: SceneKit-based 3D viewer with gesture controls.
- **Viewer3DModels**: Loads GLB/USDZ for non-AR rendering.
- **ViewerContainer**: SwiftUI bridge to UIViewController.

### Networking Layer
- **APIClient**: Generic HTTP client with retry logic and error handling.
- **GarmentAPI**: Domain-specific API methods for garment catalog.

### Telemetry Layer
- **AnalyticsLogger**: Tracks user events (optional, low priority Week 1).
- **PerformanceLogger**: Persistent logging of FPS/latency metrics.
- **QualityGateReporter**: Formats metrics for Week 6 go/no-go review.

### UI Layer
- **MainView**: Root view deciding between AR and fallback paths.
- **GarmentSelectorView**: Garment browsing and selection UI.
- **OnboardingView**: Permissions + first-run instructions.

### Utils Layer
- **DeviceCheck**: Detects ARKit capabilities (A12+, body tracking support).
- **PermissionManager**: Handles camera/LiDAR permissions.
- **ConfigManager**: Environment config (API URLs, feature flags, telemetry settings).

---

## Dependency Graph (Import Flow)

```
FashionTryOnApp.swift
    └── MainView.swift (decides AR vs. Fallback)
        ├── ARViewContainer.swift
        │   ├── ARCoordinator (manages ARKit)
        │   │   ├── BodyTracker (skeleton extraction)
        │   │   ├── PerformanceMonitor (telemetry)
        │   │   └── OcclusionManager (depth occlusion)
        │   ├── GarmentRenderer (model loading + rendering)
        │   │   └── ModelManager (caching)
        │   ├── LightingManager (scene lighting)
        │   └── AROverlayView (UI layer)
        │
        └── Viewer3DController (fallback path)
            ├── Viewer3DModels (model loading)
            └── ViewerContainer (SwiftUI bridge)

APIClient / GarmentAPI (used by GarmentSelectorView, ModelManager)
PermissionManager (used by OnboardingView, ARCoordinator)
DeviceCheck (used by MainView, ARCoordinator)
```

---

## Week 1 Build Checklist

- [ ] Create Xcode 15+ project with iOS 16+ target
- [ ] Add RealityKit framework (auto-included in iOS 15+)
- [ ] Add ARKit framework
- [ ] Create file structure (Section 1 above)
- [ ] Implement App/AppDelegate/SceneDelegate
- [ ] Implement Core/ARCoordinator with body tracking config
- [ ] Implement Core/BodyTracker skeleton extraction
- [ ] Implement Core/PerformanceMonitor with telemetry
- [ ] Create stub implementations for remaining modules
- [ ] Add sample USDZ to Assets/Models/
- [ ] Test: Build on iPhone 14 Pro (A16+), verify no crashes
- [ ] Test: ARKit session initializes, skeleton data flows
- [ ] Test: Frame profiler shows 60fps capture, >55fps rendering
- [ ] Commit all files to Git; document in daily notes

---

## Testing Strategy (Week 1)

### Unit Tests
- `ARCoordinatorTests`: Verify session init without device
- `BodyTrackerTests`: Mock ARBodyAnchor, test skeleton extraction
- `PerformanceMonitorTests`: Mock frame times, verify FPS calculation

### Integration Tests (Manual)
- Open app on iPhone → AR session starts without crash
- Move body → skeleton joints update live (console output)
- Frame profiler: confirm 60fps capture + >55fps render

### Device Coverage
- **Min:** iPhone 12 Pro (A14 Bionic)
- **Target:** iPhone 14 Pro (A16 Bionic)
- **Optional:** iPad Pro 5th gen (M1)

---

## Documentation Deliverables

1. **ARKIT_SETUP_GUIDE.md** — How to build + run the project
2. **ARKIT_DEBUGGING.md** — Xcode profiler workflows (Instruments, Metal debugger)
3. **COMPONENT_API.md** — Public API for each module (in-code comments)
4. **TELEMETRY_FORMAT.md** — JSON schema for metrics export

---

**Next Review:** End of Week 1 (2026-03-25)
