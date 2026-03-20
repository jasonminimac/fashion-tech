# WEEK 1 IMPLEMENTATION ROADMAP

**Document Owner:** 3D Scanning Lead  
**Date:** 2026-03-18  
**Phase:** MVP Week 1 (ARKit Foundation)  
**Status:** Implementation Blueprint

---

## Executive Summary

**Founder Confirmation:** ARKit/LiDAR approach CONFIRMED. iOS dev begins immediately.

**Week 1 Goal:** Establish the iOS app foundation and point cloud processing pipeline skeleton. By EOW, the pipeline can:
- ✅ Capture LiDAR depth frames (30fps)
- ✅ Render AR preview locally
- ✅ Save point cloud (.ply) to device
- ✅ Process raw cloud → clean mesh (Python skeleton)

**Not in Week 1:** Backend API, cloud upload, quality validation, segmentation—these land in Weeks 2-4.

**Success Criteria:**
- iOS app builds on Xcode 14+, iOS 14.5+
- ARKit captures 20-30 sec scans at 30fps
- Point cloud saves to Documents folder (~5MB)
- Python pipeline processes raw cloud → mesh in <3 min (dev only)
- AR preview renders in real-time
- Zero hardware crashes during 10+ test captures

---

## 1. Architecture Overview (Week 1 Scope)

```
┌─────────────────────────────────────┐
│ iPhone 12 Pro+ User                 │
├─────────────────────────────────────┤
│
│ [ARKit LiDAR Capture Module]
│  • Depth frames (320×256, 30fps)
│  • RGB video reference
│  • Camera intrinsics + IMU data
│  • Local point cloud accumulation
│
├─────────────────────────────────────┤
│
│ [AR Preview Renderer]
│  • RealityKit visualization
│  • Real-time point cloud display
│  • Confidence heatmap (optional)
│
├─────────────────────────────────────┤
│
│ [File Export & Storage]
│  • Save .ply to Documents/
│  • Save metadata JSON
│  • Offline scan history
│
└─────────────────────────────────────┘
         ↓ (Local only, no upload Week 1)
┌─────────────────────────────────────┐
│ Python Processing Pipeline (Dev)    │
├─────────────────────────────────────┤
│
│ [Noise Removal]
│ [Downsampling]
│ [Normal Estimation]
│ [Poisson Mesh Gen]
│ → .fbx / .glb output
│
└─────────────────────────────────────┘
```

---

## 2. iOS Project Setup Guide

### 2.1 Xcode Project Structure

```
FashionTechScan.xcodeproj/
├── FashionTechScan/
│   ├── App/
│   │   ├── FashionTechScanApp.swift       ← Entry point
│   │   ├── AppDelegate.swift              ← Lifecycle
│   │   └── SceneDelegate.swift            ← Window setup
│   │
│   ├── Views/
│   │   ├── ContentView.swift              ← Main navigation
│   │   ├── OnboardingView.swift           ← Tips + video
│   │   ├── ARCaptureView.swift            ← ARKit + preview
│   │   ├── ProcessingView.swift           ← Status screen
│   │   └── ScanHistoryView.swift          ← Past scans
│   │
│   ├── ViewModels/
│   │   ├── ScanManager.swift              ← Orchestration
│   │   ├── ARKitDepthCapture.swift        ← Depth capture
│   │   └── ScanProcessor.swift            ← Upload + polling
│   │
│   ├── Models/
│   │   ├── LocalScan.swift                ← Scan metadata
│   │   ├── CaptureFrame.swift             ← Frame struct
│   │   └── ProcessingStatus.swift         ← API response
│   │
│   ├── Services/
│   │   ├── FileManager+Ext.swift          ← File I/O
│   │   ├── PointCloudWriter.swift         ← .ply export
│   │   └── S3Uploader.swift               ← (Week 2)
│   │
│   ├── Resources/
│   │   ├── Assets.xcassets/               ← Images, colors
│   │   ├── Localizable.strings            ← i18n (future)
│   │   ├── how-to-scan.mp4                ← Onboarding video
│   │   └── Info.plist                     ← Permissions, config
│   │
│   └── Preview Content/ (optional)
│
├── FashionTechScanTests/
│   ├── ARKitDepthCaptureTests.swift
│   ├── PointCloudWriterTests.swift
│   └── ScanManagerTests.swift
│
└── FashionTechScanUITests/
    └── OnboardingUITests.swift
```

### 2.2 New Xcode Project (Day 1 Morning)

```bash
# Create project
open /Applications/Xcode.app/Contents/Developer/usr/bin/xcode-select --switch /Applications/Xcode.app/Contents/Developer

# Create project interactively:
# - App name: FashionTechScan
# - Organization ID: com.fashiontech
# - Bundle ID: com.fashiontech.scan
# - Swift 5.5+
# - SwiftUI
# - iOS 14.5+ minimum deployment

# OR via command line:
mkdir -p ~/Developer/FashionTech
cd ~/Developer/FashionTech
git init FashionTechScan
cd FashionTechScan

# Create Xcode project via xcodeproj Swift Package (or use Xcode GUI)
```

### 2.3 Permissions & Entitlements

**Info.plist:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSCameraUsageDescription</key>
    <string>We need camera access to capture your 3D body scan using LiDAR.</string>
    
    <key>NSMotionUsageDescription</key>
    <string>Motion data helps improve scan alignment and accuracy.</string>
    
    <key>NSLocalNetworkUsageDescription</key>
    <string>Local network access may be needed for future processing features.</string>
    
    <key>NSBonjourServices</key>
    <array>
        <string>_fashiontech._tcp</string>
    </array>
    
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>arkit</string>
        <string>lidar</string>
    </array>
    
    <key>NSRequiresIPhoneOS</key>
    <true/>
    
    <key>UIMinimumOSVersion</key>
    <string>14.5</string>
    
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
</dict>
</plist>
```

**Xcode Signing & Capabilities:**
- ✅ Enable ARKit (Xcode: Signing & Capabilities → +Capability → ARKit)
- ✅ Enable Camera (automatically included)
- ✅ Enable Motion (automatically included)

---

## 3. Core Implementation: ARKit Depth Capture

### 3.1 ARKitDepthCapture.swift (ViewModels)

```swift
import ARKit
import Combine

class ARKitDepthCapture: NSObject, ARSessionDelegate, ObservableObject {
    @Published var isCapturing = false
    @Published var depthFrameCount = 0
    @Published var confidence: Float = 0.0
    @Published var pointCloudPoints: [SIMD3<Float>] = []
    
    var arSession: ARSession
    var depthFrames: [(frame: ARFrame, timestamp: CFTimeInterval)] = []
    var rgbFrames: [CVPixelBuffer] = []
    
    let targetDuration: TimeInterval = 25.0  // 20-30 seconds
    let targetFramerate: Float = 30.0
    
    override init() {
        arSession = ARSession()
        super.init()
        arSession.delegate = self
    }
    
    // MARK: - Capture Control
    
    func startCapture() -> Bool {
        guard ARWorldTrackingConfiguration.isSupported else {
            print("❌ ARKit not supported on this device")
            return false
        }
        
        guard ARWorldTrackingConfiguration.supportsFrameSemantics(.personSegmentationWithDepth) else {
            print("❌ Person segmentation with depth not supported (need iPhone 12 Pro+)")
            return false
        }
        
        let config = ARWorldTrackingConfiguration()
        config.frameSemantics.insert(.personSegmentationWithDepth)
        config.planeDetection = []  // Not needed for body scanning
        config.environmentTexturing = .automatic
        
        // Camera frame rate: aim for 30fps
        if #available(iOS 16.0, *) {
            config.frameSemantics.insert(.machineReadableCodeDetection)  // Optional
        }
        
        depthFrames.removeAll()
        rgbFrames.removeAll()
        pointCloudPoints.removeAll()
        depthFrameCount = 0
        isCapturing = true
        
        arSession.run(config)
        print("✅ ARKit capture started")
        
        return true
    }
    
    func stopCapture() -> (pointCloud: [SIMD3<Float>], confidence: [Float]) {
        isCapturing = false
        arSession.pause()
        
        print("⏹️ Capture stopped: \(depthFrames.count) depth frames collected")
        
        // Merge depth frames into unified point cloud
        let (cloud, confidences) = mergeDepthFrames()
        
        return (cloud, confidences)
    }
    
    // MARK: - ARSessionDelegate
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        guard isCapturing else { return }
        
        // Extract depth data
        guard let depthData = frame.capturedDepthData else {
            print("⚠️ No depth data in frame")
            return
        }
        
        depthFrameCount += 1
        depthFrames.append((frame: frame, timestamp: frame.timestamp))
        
        // Also save RGB frame for reference (optional, use for texture later)
        if let pixelBuffer = frame.capturedImage as? CVPixelBuffer {
            rgbFrames.append(pixelBuffer)
        }
        
        // Update live point cloud preview (decimated)
        if depthFrameCount % 3 == 0 {  // Every 3rd frame for performance
            updateLivePreview(frame)
        }
    }
    
    func session(_ session: ARSession, didFailWithError error: Error) {
        print("❌ ARKit session error: \(error)")
        isCapturing = false
    }
    
    func session(_ session: ARSession, cameraDidChangeTrackingState camera: ARCamera) {
        switch camera.trackingState {
        case .notAvailable:
            print("⚠️ Tracking not available")
        case .limited(let reason):
            print("⚠️ Tracking limited: \(reason)")
        case .normal:
            print("✅ Tracking normal")
        }
    }
    
    // MARK: - Depth Processing
    
    private func updateLivePreview(_ frame: ARFrame) {
        guard let depthData = frame.capturedDepthData else { return }
        
        // Convert depth map to point cloud
        let points = extractPointCloud(depthData, intrinsics: frame.camera.intrinsics)
        
        DispatchQueue.main.async {
            self.pointCloudPoints = points
            self.confidence = 0.85  // Placeholder
        }
    }
    
    private func extractPointCloud(
        _ depthData: AVDepthData,
        intrinsics: simd_float3x3
    ) -> [SIMD3<Float>] {
        let depthMap = depthData.depthDataMap
        let width = CVPixelBufferGetWidth(depthMap)
        let height = CVPixelBufferGetHeight(depthMap)
        
        CVPixelBufferLockBaseAddress(depthMap, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(depthMap, .readOnly) }
        
        guard let baseAddress = CVPixelBufferGetBaseAddress(depthMap) else {
            return []
        }
        
        let floatBuffer = baseAddress.assumingMemoryBound(to: Float32.self)
        var points: [SIMD3<Float>] = []
        
        // Camera intrinsics (from ARFrame)
        let fx = intrinsics[0, 0]
        let fy = intrinsics[1, 1]
        let cx = intrinsics[2, 0]
        let cy = intrinsics[2, 1]
        
        // Convert each depth pixel to 3D point
        for y in 0..<height {
            for x in 0..<width {
                let depth = floatBuffer[y * width + x]
                
                // Skip invalid/far depth values
                guard depth > 0 && depth < 5.0 else { continue }  // 0-5 meters
                
                // Project to 3D using camera intrinsics
                // Z = depth
                // X = (x - cx) * depth / fx
                // Y = (y - cy) * depth / fy
                let px = Float(x)
                let py = Float(y)
                
                let x3d = (px - cx) * depth / fx
                let y3d = (py - cy) * depth / fy
                let z3d = depth
                
                points.append(SIMD3(x3d, y3d, z3d))
            }
        }
        
        print("📊 Extracted \(points.count) points from depth map")
        
        return points
    }
    
    // MARK: - Frame Merging (Coarse ICP)
    
    private func mergeDepthFrames() -> (pointCloud: [SIMD3<Float>], confidence: [Float]) {
        var mergedCloud: [SIMD3<Float>] = []
        var confidences: [Float] = []
        
        // Simple approach: accumulate all points from all frames
        // TODO (Week 2): Implement proper ICP alignment
        
        for (frame, _) in depthFrames {
            guard let depthData = frame.capturedDepthData else { continue }
            
            let points = extractPointCloud(depthData, intrinsics: frame.camera.intrinsics)
            mergedCloud.append(contentsOf: points)
            
            // Placeholder confidence (all 0.9)
            confidences.append(contentsOf: Array(repeating: Float(0.9), count: points.count))
        }
        
        print("✅ Merged \(mergedCloud.count) points from \(depthFrames.count) frames")
        
        return (mergedCloud, confidences)
    }
}
```

### 3.2 PointCloudWriter.swift (Services)

```swift
import Foundation

class PointCloudWriter {
    static func savePLY(
        points: [SIMD3<Float>],
        confidences: [Float],
        scanId: String
    ) -> URL? {
        let fileManager = FileManager.default
        
        guard let documentsDir = fileManager.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first else {
            print("❌ Cannot access Documents folder")
            return nil
        }
        
        let scanDir = documentsDir.appendingPathComponent("Scans/\(scanId)", isDirectory: true)
        
        do {
            try fileManager.createDirectory(at: scanDir, withIntermediateDirectories: true)
        } catch {
            print("❌ Failed to create scan directory: \(error)")
            return nil
        }
        
        let plyURL = scanDir.appendingPathComponent("scan.ply")
        
        // Build PLY file
        var plyContent = ""
        
        // Header
        plyContent += "ply\n"
        plyContent += "format ascii 1.0\n"
        plyContent += "element vertex \(points.count)\n"
        plyContent += "property float x\n"
        plyContent += "property float y\n"
        plyContent += "property float z\n"
        plyContent += "property uchar red\n"
        plyContent += "property uchar green\n"
        plyContent += "property uchar blue\n"
        plyContent += "end_header\n"
        
        // Vertex data (XYZ + RGB based on confidence)
        for i in 0..<points.count {
            let pt = points[i]
            let conf = confidences.indices.contains(i) ? confidences[i] : 0.9
            
            // Confidence → color: high confidence = green, low = red
            let confInt = UInt8(conf * 255)
            let red = UInt8(255 - confInt)
            let green = confInt
            let blue = UInt8(127)
            
            plyContent += "\(pt.x) \(pt.y) \(pt.z) \(red) \(green) \(blue)\n"
        }
        
        // Write to file
        do {
            try plyContent.write(to: plyURL, atomically: true, encoding: .utf8)
            print("✅ Saved PLY: \(plyURL.path) (\(points.count) points)")
            return plyURL
        } catch {
            print("❌ Failed to write PLY: \(error)")
            return nil
        }
    }
    
    static func saveMetadata(
        scanId: String,
        pointCount: Int,
        duration: TimeInterval,
        deviceModel: String = "iPhone"
    ) -> URL? {
        let fileManager = FileManager.default
        
        guard let documentsDir = fileManager.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first else {
            return nil
        }
        
        let scanDir = documentsDir.appendingPathComponent("Scans/\(scanId)")
        let metadataURL = scanDir.appendingPathComponent("metadata.json")
        
        let metadata: [String: Any] = [
            "scan_id": scanId,
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "device": deviceModel,
            "point_count": pointCount,
            "capture_duration_sec": duration,
            "status": "captured_locally"
        ]
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: metadata, options: .prettyPrinted)
            try jsonData.write(to: metadataURL, options: .atomic)
            print("✅ Saved metadata: \(metadataURL.path)")
            return metadataURL
        } catch {
            print("❌ Failed to write metadata: \(error)")
            return nil
        }
    }
}
```

---

## 4. UI Implementation: ARCaptureView

### 4.1 ARCaptureView.swift

```swift
import SwiftUI
import ARKit
import RealityKit

struct ARCaptureView: UIViewControllerRepresentable {
    @ObservedObject var depthCapture: ARKitDepthCapture
    var onCapturComplete: (URL?, URL?) -> Void
    
    class Coordinator: NSObject {
        let depthCapture: ARKitDepthCapture
        
        init(depthCapture: ARKitDepthCapture) {
            self.depthCapture = depthCapture
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(depthCapture: depthCapture)
    }
    
    func makeUIViewController(context: Context) -> ARCaptureViewController {
        let vc = ARCaptureViewController(depthCapture: depthCapture, onComplete: onCapturComplete)
        return vc
    }
    
    func updateUIViewController(_ uiViewController: ARCaptureViewController, context: Context) {}
}

class ARCaptureViewController: UIViewController, ARViewDelegate {
    @IBOutlet var arView: ARView!
    
    var depthCapture: ARKitDepthCapture
    var onComplete: (URL?, URL?) -> Void
    
    var captureTimer: Timer?
    var elapsedTime: Int = 0
    let targetDuration: Int = 25
    
    var pointCloudAnchor: ModelEntity?
    var lastPointCloud: [SIMD3<Float>] = []
    
    init(depthCapture: ARKitDepthCapture, onComplete: @escaping (URL?, URL?) -> Void) {
        self.depthCapture = depthCapture
        self.onComplete = onComplete
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Create ARView if not in storyboard
        if arView == nil {
            let frame = UIScreen.main.bounds
            arView = ARView(frame: frame)
            view = arView
        }
        
        // Add UI overlays
        setupUI()
        
        // Start capture
        _ = depthCapture.startCapture()
        startCaptureTimer()
        
        // Observe depth capture updates
        depthCapture.$pointCloudPoints
            .receive(on: DispatchQueue.main)
            .sink { [weak self] points in
                self?.updatePointCloudPreview(points)
            }
            .store(in: &cancellables)
    }
    
    var cancellables = Set<AnyCancellable>()
    
    private func setupUI() {
        // Title
        let titleLabel = UILabel()
        titleLabel.text = "Body Scan in Progress"
        titleLabel.font = UIFont.systemFont(ofSize: 18, weight: .bold)
        titleLabel.textColor = .white
        titleLabel.textAlignment = .center
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(titleLabel)
        
        // Progress
        let progressLabel = UILabel()
        progressLabel.text = "0 / 25 seconds"
        progressLabel.font = UIFont.systemFont(ofSize: 14)
        progressLabel.textColor = .white
        progressLabel.textAlignment = .center
        progressLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(progressLabel)
        
        // Guidance
        let guidanceLabel = UILabel()
        guidanceLabel.text = "Circle around your body slowly..."
        guidanceLabel.font = UIFont.systemFont(ofSize: 14)
        guidanceLabel.textColor = .white
        guidanceLabel.textAlignment = .center
        guidanceLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(guidanceLabel)
        
        // Buttons
        let finishButton = UIButton(type: .system)
        finishButton.setTitle("Finish Scan", for: .normal)
        finishButton.backgroundColor = .systemGreen
        finishButton.setTitleColor(.white, for: .normal)
        finishButton.layer.cornerRadius = 8
        finishButton.translatesAutoresizingMaskIntoConstraints = false
        finishButton.addTarget(self, action: #selector(finishCapture), for: .touchUpInside)
        view.addSubview(finishButton)
        
        let cancelButton = UIButton(type: .system)
        cancelButton.setTitle("Cancel", for: .normal)
        cancelButton.backgroundColor = .systemRed
        cancelButton.setTitleColor(.white, for: .normal)
        cancelButton.layer.cornerRadius = 8
        cancelButton.translatesAutoresizingMaskIntoConstraints = false
        cancelButton.addTarget(self, action: #selector(cancelCapture), for: .touchUpInside)
        view.addSubview(cancelButton)
        
        // Layout
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            progressLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10),
            progressLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            guidanceLabel.topAnchor.constraint(equalTo: progressLabel.bottomAnchor, constant: 10),
            guidanceLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            finishButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            finishButton.rightAnchor.constraint(equalTo: view.centerXAnchor, constant: -10),
            finishButton.widthAnchor.constraint(equalToConstant: 140),
            finishButton.heightAnchor.constraint(equalToConstant: 50),
            
            cancelButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            cancelButton.leftAnchor.constraint(equalTo: view.centerXAnchor, constant: 10),
            cancelButton.widthAnchor.constraint(equalToConstant: 140),
            cancelButton.heightAnchor.constraint(equalToConstant: 50),
        ])
        
        self.progressLabel = progressLabel
        self.guidanceLabel = guidanceLabel
    }
    
    var progressLabel: UILabel?
    var guidanceLabel: UILabel?
    
    private func startCaptureTimer() {
        captureTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.elapsedTime += 1
            
            DispatchQueue.main.async {
                self?.progressLabel?.text = "\(self?.elapsedTime ?? 0) / \(self?.targetDuration ?? 25) seconds"
                
                // Update guidance
                let rotation = (self?.elapsedTime ?? 0) % 4
                let guidances = [
                    "Circle to your left...",
                    "Capture from the side...",
                    "Circle to your right...",
                    "Move to capture from above..."
                ]
                self?.guidanceLabel?.text = guidances[rotation]
            }
            
            if self?.elapsedTime ?? 0 >= self?.targetDuration ?? 25 {
                self?.finishCapture()
            }
        }
    }
    
    private func updatePointCloudPreview(_ points: [SIMD3<Float>]) {
        guard !points.isEmpty else { return }
        
        // For now, just store the points
        // TODO (Week 2): Render as 3D mesh in ARView
        lastPointCloud = points
    }
    
    @objc func finishCapture() {
        captureTimer?.invalidate()
        
        let (pointCloud, confidences) = depthCapture.stopCapture()
        
        guard !pointCloud.isEmpty else {
            print("❌ No point cloud captured")
            onComplete(nil, nil)
            return
        }
        
        // Save to disk
        let scanId = UUID().uuidString
        let plyURL = PointCloudWriter.savePLY(
            points: pointCloud,
            confidences: confidences,
            scanId: scanId
        )
        let metadataURL = PointCloudWriter.saveMetadata(
            scanId: scanId,
            pointCount: pointCloud.count,
            duration: TimeInterval(elapsedTime)
        )
        
        onComplete(plyURL, metadataURL)
    }
    
    @objc func cancelCapture() {
        captureTimer?.invalidate()
        depthCapture.stopCapture()
        onComplete(nil, nil)
    }
}
```

---

## 5. Python Point Cloud Pipeline (Development)

### 5.1 Project Structure

```
fashion-tech-processing/
├── setup.py
├── requirements.txt
├── README.md
│
├── pipeline/
│   ├── __init__.py
│   ├── pipeline.py              ← Main orchestration
│   │
│   ├── stages/
│   │   ├── __init__.py
│   │   ├── cleaning.py          ← Noise removal
│   │   ├── downsampling.py      ← Voxel grid
│   │   ├── normals.py           ← Normal estimation
│   │   ├── meshing.py           ← Poisson reconstruction
│   │   ├── cleanup.py           ← Degenerate removal
│   │   └── export.py            ← FBX/glTF output
│   │
│   └── utils/
│       ├── __init__.py
│       ├── visualization.py     ← Open3D viewer
│       └── metrics.py           ← Testing helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_pipeline.py
│   ├── test_cleaning.py
│   └── test_meshing.py
│
└── data/
    ├── test_synthetic/          ← Generated point clouds
    └── test_real/               ← Real iPhone scans (Week 2+)
```

### 5.2 requirements.txt

```
open3d>=0.15.0
numpy>=1.21.0
scipy>=1.7.0
PyVista>=0.36.0
trimesh>=3.12.0
pytest>=6.2.5
```

### 5.3 pipeline/stages/cleaning.py

```python
import open3d as o3d
import numpy as np

class PointCloudCleaner:
    def __init__(self, config: dict = None):
        self.config = config or {
            "outlier_nb_neighbors": 20,
            "outlier_std_ratio": 2.0,
            "confidence_threshold": 0.7,
        }
    
    def clean(self, pcd: o3d.geometry.PointCloud, confidences: np.ndarray = None) -> o3d.geometry.PointCloud:
        """Remove noise and outliers."""
        
        # Step 1: Statistical outlier removal
        pcd_clean, inlier_mask = pcd.remove_statistical_outliers(
            nb_neighbors=self.config["outlier_nb_neighbors"],
            std_ratio=self.config["outlier_std_ratio"]
        )
        
        print(f"✅ Outlier removal: {len(pcd.points)} → {len(pcd_clean.points)} points")
        
        # Step 2: Confidence filtering
        if confidences is not None and len(confidences) > 0:
            mask = confidences >= self.config["confidence_threshold"]
            pcd_clean = pcd_clean.select_by_index(np.where(mask)[0])
            print(f"✅ Confidence filtering: → {len(pcd_clean.points)} points")
        
        return pcd_clean
```

### 5.4 pipeline/stages/meshing.py

```python
import open3d as o3d
import numpy as np

class MeshGenerator:
    def __init__(self, depth: int = 9):
        self.depth = depth
    
    def generate_poisson(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
        """Poisson surface reconstruction."""
        
        # Ensure normals are present
        if not pcd.has_normals():
            pcd.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
            )
        
        # Poisson reconstruction
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd,
            depth=self.depth,
            width=0,
            linear_fit=False
        )
        
        # Remove low-density voxels
        vertices_to_remove = densities < np.quantile(densities, 0.1)
        mesh.remove_vertices_by_mask(vertices_to_remove)
        
        print(f"✅ Poisson mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return mesh
```

### 5.5 pipeline/pipeline.py (Main Orchestration)

```python
import open3d as o3d
import numpy as np
from pathlib import Path
import logging

from .stages.cleaning import PointCloudCleaner
from .stages.downsampling import PointCloudDownsampler
from .stages.normals import NormalEstimator
from .stages.meshing import MeshGenerator
from .stages.cleanup import MeshCleaner
from .stages.export import MeshExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScanProcessingPipeline:
    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        
        self.cleaner = PointCloudCleaner(self.config["cleaning"])
        self.downsampler = PointCloudDownsampler(self.config["voxel_size"])
        self.estimator = NormalEstimator()
        self.generator = MeshGenerator(self.config["mesh_depth"])
        self.mesh_cleaner = MeshCleaner()
        self.exporter = MeshExporter()
    
    @staticmethod
    def _default_config():
        return {
            "cleaning": {
                "outlier_nb_neighbors": 20,
                "outlier_std_ratio": 2.0,
                "confidence_threshold": 0.7,
            },
            "voxel_size": 0.01,  # 10mm
            "mesh_depth": 9,
        }
    
    def process(self, input_ply: str, scan_id: str, output_dir: str = ".") -> dict:
        """
        Full pipeline: point cloud → mesh.
        
        Args:
            input_ply: Path to input .ply file
            scan_id: Scan identifier
            output_dir: Output directory
        
        Returns:
            {
                "fbx_path": "...",
                "glb_path": "...",
                "metadata_path": "...",
            }
        """
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[{scan_id}] Starting pipeline...")
        
        # Load
        logger.info(f"[{scan_id}] Loading: {input_ply}")
        pcd = o3d.io.read_point_cloud(input_ply)
        logger.info(f"  Input: {len(pcd.points)} points")
        
        # Extract confidences from color (if present)
        confidences = None
        if pcd.has_colors():
            colors = np.asarray(pcd.colors)
            confidences = colors[:, 0]  # R channel = confidence
        
        # Stage 1: Clean
        logger.info(f"[{scan_id}] Stage 1: Noise removal...")
        pcd = self.cleaner.clean(pcd, confidences)
        
        # Stage 2: Downsample
        logger.info(f"[{scan_id}] Stage 2: Downsampling...")
        pcd = self.downsampler.downsample(pcd)
        
        # Stage 3: Estimate normals
        logger.info(f"[{scan_id}] Stage 3: Normal estimation...")
        pcd = self.estimator.estimate(pcd)
        
        # Stage 4: Generate mesh
        logger.info(f"[{scan_id}] Stage 4: Mesh generation...")
        mesh = self.generator.generate_poisson(pcd)
        
        # Stage 5: Clean mesh
        logger.info(f"[{scan_id}] Stage 5: Mesh cleanup...")
        mesh = self.mesh_cleaner.clean(mesh)
        
        # Stage 6: Export
        logger.info(f"[{scan_id}] Stage 6: Exporting...")
        fbx_path = output_dir / f"{scan_id}.fbx"
        glb_path = output_dir / f"{scan_id}.glb"
        
        self.exporter.export_fbx(mesh, str(fbx_path))
        self.exporter.export_glb(mesh, str(glb_path))
        
        logger.info(f"[{scan_id}] ✅ Pipeline complete!")
        
        return {
            "fbx_path": str(fbx_path),
            "glb_path": str(glb_path),
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.pipeline <input.ply> [scan_id] [output_dir]")
        sys.exit(1)
    
    input_ply = sys.argv[1]
    scan_id = sys.argv[2] if len(sys.argv) > 2 else "test_scan"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    
    pipeline = ScanProcessingPipeline()
    result = pipeline.process(input_ply, scan_id, output_dir)
    
    print(f"\n📊 Results:\n{result}")
```

---

## 6. Setup & Environment Instructions

### 6.1 iOS Setup (Day 1)

```bash
# 1. Clone or create project
cd ~/Developer
git clone <repo-url> FashionTechScan
cd FashionTechScan

# 2. Install dependencies (CocoaPods)
pod repo update
pod install

# 3. Open in Xcode
open FashionTechScan.xcworkspace

# 4. Build & run
#    - Select target: FashionTechScan
#    - Select device: iPhone 12 Pro+ simulator (or real device with LiDAR)
#    - Product → Run (⌘R)
```

### 6.2 Python Setup (Day 1)

```bash
# 1. Create virtual environment
cd fashion-tech-processing
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test import
python -c "import open3d; print('✅ Open3D installed')"
```

### 6.3 Verify Installation

```bash
# iOS: Build succeeds
xcode-build -scheme FashionTechScan -sdk iphonesimulator

# Python: Can process synthetic point cloud
python pipeline/pipeline.py data/test_synthetic/sphere_500k.ply test_001 ./output
```

---

## 7. Day-by-Day Implementation Schedule

### Day 1 (Monday) — Project Setup & ARKit Foundation
**Goal:** iOS project builds, ARKit capture skeleton runs.

- [ ] Create Xcode project with correct structure
- [ ] Add permissions to Info.plist
- [ ] Implement `ARKitDepthCapture` class (capture control only, no UI yet)
- [ ] Implement `PointCloudWriter` (PLY export)
- [ ] Unit test: PLY file can be read by Open3D
- **EOD:** ARKit initialization works, no crashes

### Day 2 (Tuesday) — AR Preview & UI
**Goal:** User can tap "Start Scan" and see real-time point cloud in AR.

- [ ] Implement `ARCaptureView` UI (SwiftUI)
- [ ] Implement `ARCaptureViewController` (ARView setup)
- [ ] Hook up depth capture → live preview
- [ ] Add timer + guidance text
- [ ] Test on simulator (mock depth) or device (real LiDAR)
- **EOD:** Preview renders at 30fps, no lag

### Day 3 (Wednesday) — File Management & Local Storage
**Goal:** User can scan, save locally, and view past scans.

- [ ] Implement local file storage (Documents/)
- [ ] Implement `ScanHistoryView` (list scans)
- [ ] Add metadata JSON export
- [ ] Test: Scan → File → Directory verification
- [ ] Polish: Deletion, rename, share placeholder
- **EOD:** Full capture → save → history loop works

### Day 4 (Thursday) — Python Pipeline Skeleton
**Goal:** Pipeline can process raw .ply → mesh output.

- [ ] Set up Python environment (venv, pip install)
- [ ] Implement `pipeline.py` (orchestration)
- [ ] Implement Stage 1-3 (cleaning, downsampling, normals)
- [ ] Implement Stage 4 (Poisson meshing)
- [ ] Test on synthetic point cloud
- **EOD:** Pipeline runs end-to-end, outputs valid FBX

### Day 5 (Friday) — Integration Testing & Polish
**Goal:** Week 1 complete, everything tested, blockers identified.

- [ ] Export iOS point cloud from simulator/device
- [ ] Process with Python pipeline
- [ ] Verify FBX can be opened in Blender (manual test)
- [ ] Document any issues, edge cases, or needed refinements
- [ ] Prepare demo for CEO/founder
- **EOD:** MVP skeleton complete, ready for Week 2 expansion

---

## 8. Key Metrics & Success Criteria (Week 1)

| Metric | Target | Status |
|--------|--------|--------|
| iOS app builds | ✅ No errors | TBD |
| ARKit capture starts | ✅ 30fps depth | TBD |
| Point cloud saves locally | ✅ <5MB .ply | TBD |
| Python pipeline runs | ✅ <3min (dev) | TBD |
| Mesh output (FBX/glB) | ✅ Valid format | TBD |
| Zero crashes | ✅ 10+ test runs | TBD |
| AR preview renders | ✅ 30fps minimum | TBD |

---

## 9. Dependencies & Blockers

### Required (No Blockers)
- ✅ Xcode 14+ (available)
- ✅ iOS 14.5+ SDK (built-in)
- ✅ Open3D Python (pip installable)
- ✅ Terminal/Git (available)

### External Dependency (Week 2+)
- ⏳ Backend API provisioning (Backend Engineer)
- ⏳ S3 bucket setup (Backend Engineer)
- ⏳ iPhone LiDAR device (CEO/Founder)

### Known Limitations (Week 1)
- ❌ **NO cloud upload** (Week 2) — scans saved locally only
- ❌ **NO body segmentation** (Week 3) — pipeline skeleton only
- ❌ **NO pose normalization** (Week 3)
- ❌ **NO Blender rigging integration** (Week 4)
- ❌ **NO ML-based processing** (Phase 2)

---

## 10. Escalation Path (>2h Blockers)

**If you encounter a blocker that blocks progress for >2 hours:**

1. **Document it** (what, why, impact)
2. **Escalate to CEO immediately** via message/Slack
3. **Provide:**
   - Problem statement
   - Attempted solutions
   - Recommendation (workaround vs. halt)
   - Time to resolve (estimate)

**Example blockers that warrant escalation:**
- Xcode project won't build (env issue)
- ARKit not accessible on device
- Python Open3D crashes on all inputs
- Need emergency hardware provisioning

---

## 11. Code Repository Template

### .gitignore
```
# Xcode
*.pbxuser
*.xcworkspace/xcuserdata/
DerivedData/
*.xcarchive

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Data (large files)
*.ply
*.fbx
*.glb
data/test_real/
```

### README.md (Project Root)
```markdown
# FashionTech 3D Scanning Pipeline

## Quick Start

### iOS
```bash
cd FashionTechScan
pod install
open FashionTechScan.xcworkspace
# Build & run in Xcode
```

### Python
```bash
cd fashion-tech-processing
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python pipeline/pipeline.py data/test_synthetic/example.ply test_001 ./output
```

## Architecture
See `/workspace/docs/3d-scanning-lead/` for full documentation.
```

---

## 12. Testing Strategy (Week 1)

### Unit Tests (Python)
```python
# tests/test_cleaning.py
import pytest
from pipeline.stages.cleaning import PointCloudCleaner
import open3d as o3d
import numpy as np

def test_outlier_removal():
    # Create synthetic cloud with outliers
    points = np.random.randn(1000, 3)
    # Add outliers
    outliers = np.array([[100, 100, 100], [200, 200, 200]])
    points = np.vstack([points, outliers])
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    cleaner = PointCloudCleaner()
    pcd_clean = cleaner.clean(pcd)
    
    # Should remove outliers
    assert len(pcd_clean.points) < len(points)
    assert len(pcd_clean.points) >= 800  # Most inliers preserved
```

### Integration Tests (iOS)
```swift
// FashionTechScanTests/ARKitDepthCaptureTests.swift
import XCTest
@testable import FashionTechScan

class ARKitDepthCaptureTests: XCTestCase {
    func testCaptureInitializes() {
        let capture = ARKitDepthCapture()
        XCTAssertFalse(capture.isCapturing)
    }
    
    func testCaptureStartsSuccessfully() {
        let capture = ARKitDepthCapture()
        let started = capture.startCapture()
        XCTAssertTrue(started)
        XCTAssertTrue(capture.isCapturing)
    }
}
```

---

## 13. Documentation Outputs (Week 1)

By EOW, these files should be committed:

1. ✅ This file: `WEEK1_IMPLEMENTATION.md`
2. ✅ iOS app skeleton + source code
3. ✅ Python pipeline skeleton + source code
4. ✅ Setup instructions (iOS + Python)
5. ✅ Architecture diagrams (updated)
6. ✅ Test data (synthetic point cloud)
7. ✅ Git repo with clean history

---

## 14. Sign-Off & Next Steps

### Week 1 Complete Checklist
- [ ] iOS project builds on Xcode 14+
- [ ] ARKit depth capture functional (simulator or device)
- [ ] Point cloud saves as .ply locally
- [ ] Python pipeline processes .ply → FBX/glB
- [ ] All code committed to git
- [ ] No critical bugs, crashes, or hangs
- [ ] Documentation complete

### Week 2 Preview (Next)
1. **Backend API Setup** — FastAPI skeleton, S3 integration
2. **Cloud Upload Flow** — iOS → S3 → Processing queue
3. **Body Segmentation** — Heuristic-based vertex labeling
4. **Pose Normalization** — T-pose alignment
5. **Full Integration Test** — End-to-end pipeline
6. **Blender Handoff** — FBX import verification

---

**Version:** 1.0  
**Date:** 2026-03-18  
**Status:** Ready for Week 1 implementation  
**Next Review:** 2026-03-25 (EOW Week 1)

---

## Appendix A: Quick Reference

**Important Files:**
- `/workspace/docs/3d-scanning-lead/IOS_APP_DESIGN.md` — Detailed UI/UX specs
- `/workspace/docs/3d-scanning-lead/POINT_CLOUD_PIPELINE.md` — Detailed processing specs
- `/workspace/docs/3d-scanning-lead/SCANNING_ARCHITECTURE.md` — System design

**Useful Commands:**
```bash
# iOS
xcode-build -scheme FashionTechScan -configuration Debug

# Python
python pipeline/pipeline.py input.ply scan_id ./output
python -m pytest tests/

# Git
git status
git add -A
git commit -m "feat: Week 1 iOS + pipeline skeleton"
```

**Slack Channel:** `#fashion-tech-scanning`

---

**End of Week 1 Implementation Roadmap**
