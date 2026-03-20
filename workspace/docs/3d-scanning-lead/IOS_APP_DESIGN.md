# iOS App Design & Implementation Plan

**Document Owner:** 3D Scanning Lead  
**Date:** 2026-03-17  
**Phase:** MVP (Weeks 1–2)  
**Status:** Design & Specification

---

## 1. Overview

The iOS app is the primary capture interface for end users. It must be **fast, intuitive, and reliable** — users should be able to scan their body in under 2 minutes with minimal guidance.

**Key Constraints:**
- Target: iPhone 12 Pro, 13 Pro, 14 Pro (LiDAR equipped)
- OS: iOS 14.5+
- UX: New users should scan without training
- Performance: Real-time AR preview, <200MB app size

---

## 2. User Flow

```
┌─────────────────┐
│   App Launch    │
└────────┬────────┘
         ↓
┌──────────────────────────────────────┐
│ 1. Permission Check                  │
│  • Camera access                      │
│  • Motion data                        │
│  • Storage                            │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 2. Onboarding Screen                 │
│  • "How to Scan" video (15 sec)      │
│  • Tips (wear tight clothes, etc.)   │
│  • [Start Scan] button               │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 3. Camera Preview + AR Guides        │
│  • Live AR preview (point cloud)     │
│  • Progress circle (0–100%)          │
│  • Instructions: "Circle around..."  │
│  • [Cancel] [Finish Scan] buttons    │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 4. Scan Complete Screen              │
│  • "Processing..."                   │
│  • Estimated time: 2–3 minutes       │
│  • [Upload to Cloud] button          │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 5. Upload Status                     │
│  • Progress bar (upload speed)       │
│  • [View in Blender] or [Retry]      │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 6. Scan History Screen               │
│  • List of past scans                │
│  • Thumbnails (preview images)       │
│  • [View] / [Delete] / [Share]       │
└──────────────────────────────────────┘
```

---

## 3. Core UI Screens

### 3.1 Onboarding Screen

**Purpose:** Educate user on scanning technique before capturing.

**Layout:**
```
┌─────────────────────────────┐
│  Fashion Tech 3D Scan       │
├─────────────────────────────┤
│                             │
│  [Instructional Video]      │  ← 15–20 sec demo
│   "How to scan in 20s"      │
│                             │
├─────────────────────────────┤
│ Tips:                       │
│ • Wear fitted clothes       │
│ • Clean background (wall)   │
│ • Good lighting             │
│ • Circle around your body   │
│                             │
│  [Start Scan]  [Learn More] │
└─────────────────────────────┘
```

**Components:**
- AVPlayer video (bundled with app)
- Bullet-point list of tips
- Large CTA button ([Start Scan])

**Implementation:**
```swift
struct OnboardingView: View {
    @State var showVideo = false
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack {
            Text("Fashion Tech 3D Body Scan")
                .font(.title2)
                .bold()
            
            if showVideo {
                VideoPlayer(player: AVPlayer(url: Bundle.main.url(forResource: "how-to-scan", withExtension: "mp4")!))
                    .frame(height: 300)
            } else {
                Image("scan-placeholder")
                    .resizable()
                    .scaledToFill()
                    .frame(height: 300)
                    .onTapGesture {
                        showVideo = true
                    }
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Tips for Best Results:").bold()
                ForEach(["Wear fitted clothes", "Clean background", "Good lighting", "Circle around your body"], id: \.self) { tip in
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text(tip)
                    }
                }
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(8)
            
            Spacer()
            
            Button(action: startScan) {
                Text("Start Scan")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(8)
            }
        }
        .padding()
    }
    
    func startScan() {
        // Navigate to AR capture screen
    }
}
```

---

### 3.2 AR Capture Screen

**Purpose:** Real-time depth capture with visual feedback.

**Layout:**
```
┌──────────────────────────────────────┐
│                                      │
│  [AR Preview (Point Cloud)]          │
│   • Live depth visualization         │
│   • Point density indicator          │
│   • Crosshair (center target)        │
│                                      │
├──────────────────────────────────────┤
│                                      │
│  Progress: ████████░░░░ 65%          │
│  Time: 12 / 30 seconds               │
│                                      │
│  Guidance: "Move to the right..."    │
│                                      │
├──────────────────────────────────────┤
│  [X Cancel]        [✓ Finish]        │
└──────────────────────────────────────┘
```

**Components:**
- ARView (RealityKit) — live point cloud render
- Progress bar (% completion)
- Timer + guidance text
- Cancel / Finish buttons

**Implementation:**
```swift
import ARKit
import RealityKit

struct ARCaptureView: UIViewControllerRepresentable {
    class Coordinator: NSObject, ARSessionDelegate {
        var depthCapture: ARKitDepthCapture
        
        func session(_ session: ARSession, didUpdate frame: ARFrame) {
            depthCapture.processFrame(frame)
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    func makeUIViewController(context: Context) -> ARCaptureViewController {
        let vc = ARCaptureViewController()
        vc.delegate = context.coordinator
        return vc
    }
    
    func updateUIViewController(_ uiViewController: ARCaptureViewController, context: Context) {}
}

class ARCaptureViewController: UIViewController, ARViewDelegate {
    @IBOutlet var arView: ARView!
    
    var depthCapture: ARKitDepthCapture!
    var pointCloudAnchor: ModelEntity?
    var captureTimer: Timer?
    var elapsedTime: Int = 0
    let targetDuration: Int = 20  // seconds
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        depthCapture = ARKitDepthCapture()
        depthCapture.delegate = self
        
        // Start AR session
        let config = ARWorldTrackingConfiguration()
        config.frameSemantics.insert(.personSegmentationWithDepth)
        arView.session.run(config)
        
        // Start capture timer
        startCaptureTimer()
    }
    
    func startCaptureTimer() {
        depthCapture.startCapture()
        captureTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.elapsedTime += 1
            self?.updateProgressUI()
            
            if self?.elapsedTime ?? 0 >= self?.targetDuration ?? 20 {
                self?.finishCapture()
            }
        }
    }
    
    func updateProgressUI() {
        let progress = Float(elapsedTime) / Float(targetDuration)
        // Update progress bar, timer label, guidance text
    }
    
    func updatePointCloudPreview(frame: ARFrame) {
        // Extract depth data from frame
        guard let depthData = frame.capturedDepthData else { return }
        
        // Convert to point cloud vertices
        let vertices = extractPointCloud(depthData)
        
        // Update AR view (point cloud mesh)
        if pointCloudAnchor != nil {
            arView.scene.removeAnchor(pointCloudAnchor!)
        }
        
        pointCloudAnchor = createPointCloudMesh(vertices)
        arView.scene.addAnchor(pointCloudAnchor!)
    }
    
    @IBAction func finishCapture() {
        captureTimer?.invalidate()
        let (pointCloud, confidence) = depthCapture.stopCapture()
        
        // Save locally
        saveScanToDocuments(pointCloud, confidence)
        
        // Navigate to processing screen
        showProcessingScreen()
    }
}
```

**User Guidance & Feedback:**
- **Progress bar:** Visual indicator of capture progress (0–100%)
- **Time counter:** "12 / 30 seconds"
- **Guidance text:** Rotate through messages:
  - "Circle to the left..."
  - "Move to the right..."
  - "Capture from above..."
  - "Capture from below..."
- **Audio feedback:** Optional beeps when high-quality frames captured

---

### 3.3 Processing Screen

**Purpose:** Show progress as point cloud is uploaded and processed on backend.

**Layout:**
```
┌──────────────────────────────────────┐
│  Processing Your Scan                │
├──────────────────────────────────────┤
│                                      │
│  [Animated spinner]                  │
│                                      │
│  Step 1: Uploading...    [✓]         │
│  Step 2: Cleaning...     [⏳]        │
│  Step 3: Meshing...      [ ]         │
│  Step 4: Segmenting...   [ ]         │
│                                      │
│  Estimated time: 2–3 minutes         │
│                                      │
│  [Cancel]  [View Details]            │
└──────────────────────────────────────┘
```

**Components:**
- Animated spinner or progress indicator
- Step-by-step status (Upload → Clean → Mesh → Segment)
- ETA countdown
- Cancel button (deletes scan if in progress)

**Implementation:**
```swift
struct ProcessingView: View {
    @StateObject var processor = ScanProcessor()
    @State var currentStep: ProcessingStep = .uploading
    @State var progress: Double = 0
    @State var eta: Int = 180  // seconds
    
    var body: some View {
        VStack {
            Text("Processing Your Scan")
                .font(.title2)
                .bold()
            
            Spacer()
            
            // Spinner
            ProgressView()
                .scaleEffect(2)
            
            Spacer()
            
            // Step status
            VStack(alignment: .leading, spacing: 12) {
                ForEach(ProcessingStep.allCases, id: \.self) { step in
                    HStack {
                        Image(systemName: step.icon(processor.currentStep))
                            .foregroundColor(step.color(processor.currentStep))
                        Text(step.description)
                        Spacer()
                    }
                    .padding(8)
                }
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(8)
            
            Spacer()
            
            Text("Estimated time: \(eta) seconds")
                .font(.caption)
            
            Button(action: { processor.cancel() }) {
                Text("Cancel")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red.opacity(0.2))
                    .cornerRadius(8)
            }
        }
        .padding()
        .onAppear {
            processor.startProcessing()
        }
        .onReceive(processor.$currentStep) { step in
            currentStep = step
        }
        .onReceive(processor.$progress) { p in
            progress = p
        }
    }
}

enum ProcessingStep: CaseIterable {
    case uploading, cleaning, meshing, segmenting
    
    var description: String {
        switch self {
        case .uploading: return "Uploading..."
        case .cleaning: return "Cleaning point cloud..."
        case .meshing: return "Generating mesh..."
        case .segmenting: return "Segmenting body..."
        }
    }
    
    func icon(_ currentStep: ProcessingStep) -> String {
        if self.rawValue < currentStep.rawValue {
            return "checkmark.circle.fill"
        } else if self == currentStep {
            return "hourglass"
        } else {
            return "circle"
        }
    }
    
    func color(_ currentStep: ProcessingStep) -> Color {
        if self.rawValue < currentStep.rawValue {
            return .green
        } else if self == currentStep {
            return .blue
        } else {
            return .gray
        }
    }
}
```

**Backend Integration:**
```swift
class ScanProcessor: ObservableObject {
    @Published var currentStep: ProcessingStep = .uploading
    @Published var progress: Double = 0
    
    let apiClient = APIClient(baseURL: URL(string: "https://api.fashiontech.com")!)
    
    func startProcessing() {
        Task {
            do {
                // 1. Upload
                currentStep = .uploading
                let scanId = try await uploadScan()
                
                // 2. Poll for processing status
                var isComplete = false
                while !isComplete {
                    let status = try await checkProcessingStatus(scanId)
                    
                    currentStep = status.currentStep
                    progress = status.progress
                    
                    if status.isComplete {
                        isComplete = true
                    } else {
                        try await Task.sleep(nanoseconds: 1_000_000_000)  // Poll every 1 sec
                    }
                }
            } catch {
                print("Processing error: \(error)")
            }
        }
    }
    
    private func uploadScan() async throws -> String {
        // Upload point cloud file to S3
        // Return scan ID
    }
    
    private func checkProcessingStatus(_ scanId: String) async throws -> ProcessingStatus {
        let response = try await apiClient.get(
            "/scans/\(scanId)/status",
            responseType: ProcessingStatus.self
        )
        return response
    }
    
    func cancel() {
        // TODO: Cancel processing on backend
    }
}

struct ProcessingStatus: Codable {
    let scanId: String
    let currentStep: ProcessingStep
    let progress: Double  // 0.0 to 1.0
    let isComplete: Bool
    let eta: TimeInterval
}
```

---

### 3.4 Scan History Screen

**Purpose:** View past scans, manage local storage.

**Layout:**
```
┌──────────────────────────────────────┐
│  My Scans                            │
├──────────────────────────────────────┤
│                                      │
│  [+] New Scan                        │
│                                      │
│  ┌──────────────────────────────────┐
│  │ [Thumbnail]  Scan #1             │
│  │ Mar 17, 10:30  2.4 MB            │
│  │ [View] [Delete] [Share]          │
│  └──────────────────────────────────┘
│                                      │
│  ┌──────────────────────────────────┐
│  │ [Thumbnail]  Scan #2             │
│  │ Mar 16, 14:15  1.8 MB            │
│  │ [View] [Delete] [Share]          │
│  └──────────────────────────────────┘
│                                      │
└──────────────────────────────────────┘
```

**Components:**
- List of scans (newest first)
- Thumbnail preview image
- File size + timestamp
- Action buttons: View, Delete, Share

**Implementation:**
```swift
struct ScanHistoryView: View {
    @StateObject var scanManager = ScanManager()
    @State var scans: [LocalScan] = []
    
    var body: some View {
        NavigationView {
            VStack {
                Button(action: { /* Start new scan */ }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("New Scan")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .padding()
                
                List {
                    ForEach(scans, id: \.id) { scan in
                        NavigationLink(destination: ScanDetailView(scan: scan)) {
                            HStack {
                                Image(uiImage: scan.thumbnail ?? UIImage())
                                    .resizable()
                                    .scaledToFill()
                                    .frame(width: 60, height: 60)
                                    .cornerRadius(8)
                                
                                VStack(alignment: .leading) {
                                    Text("Scan #\(scan.id)")
                                        .font(.headline)
                                    Text(scan.timestamp.formatted())
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                    Text("\(scan.fileSize) MB")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                
                                Spacer()
                                
                                Menu {
                                    Button("View Details") { }
                                    Button("Share", action: { scanManager.share(scan) })
                                    Button("Delete", role: .destructive) { scanManager.delete(scan) }
                                } label: {
                                    Image(systemName: "ellipsis.circle")
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("My Scans")
            .onAppear {
                scans = scanManager.loadLocalScans()
            }
        }
    }
}

struct ScanDetailView: View {
    let scan: LocalScan
    
    var body: some View {
        VStack {
            // Show 3D preview (if glTF was downloaded)
            // Or show thumbnail + metadata
            Text("Scan Details")
        }
    }
}
```

---

## 4. Technical Architecture

### 4.1 Project Structure

```
FashionTechScan.xcodeproj/
├── FashionTechScan/
│   ├── App/
│   │   ├── FashionTechScanApp.swift       (Entry point)
│   │   └── AppDelegate.swift
│   ├── Models/
│   │   ├── LocalScan.swift                (Local storage model)
│   │   ├── ProcessingStatus.swift         (API response)
│   │   └── ARKitModels.swift              (Depth capture models)
│   ├── Views/
│   │   ├── OnboardingView.swift
│   │   ├── ARCaptureView.swift
│   │   ├── ProcessingView.swift
│   │   └── ScanHistoryView.swift
│   ├── ViewModels/
│   │   ├── ScanManager.swift              (Orchestration)
│   │   ├── ARKitDepthCapture.swift        (Depth capture)
│   │   └── ScanProcessor.swift            (Upload + polling)
│   ├── Services/
│   │   ├── APIClient.swift                (HTTP client)
│   │   ├── S3Uploader.swift               (S3 upload)
│   │   └── FileManager+Extensions.swift
│   ├── Resources/
│   │   ├── Localizable.strings            (i18n)
│   │   └── how-to-scan.mp4                (Onboarding video)
│   └── Info.plist
└── Tests/
    ├── ARKitDepthCaptureTests.swift
    ├── ScanProcessorTests.swift
    └── APIClientTests.swift
```

### 4.2 Key Dependencies

**Package Dependencies:**
- SwiftUI (built-in)
- ARKit (built-in)
- RealityKit (built-in)
- Combine (built-in)
- AVFoundation (built-in)
- AWSS3 (for S3 upload) — `pod 'AWSS3'`

**CocoaPods:**
```ruby
# Podfile
platform :ios, '14.5'

target 'FashionTechScan' do
    pod 'AWSS3', '~> 2.30'
end
```

### 4.3 Permissions & Entitlements

**Required Permissions (Info.plist):**
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to scan your body for 3D modeling.</string>

<key>NSMotionUsageDescription</key>
<string>We use motion data to improve scan accuracy.</string>

<key>NSLocalNetworkUsageDescription</key>
<string>We may use local network discovery for processing servers.</string>
```

**Capabilities (Xcode):**
- Camera
- Motion sensors
- ARKit

---

## 5. Data Flow & Storage

### 5.1 Local Storage

**Documents Directory Structure:**
```
~/Documents/FashionTechScans/
├── scan_<uuid>/
│   ├── scan.ply                    (Raw point cloud, ~5MB)
│   ├── metadata.json               (Capture params, timestamp)
│   ├── thumbnail.jpg               (Preview image)
│   └── status.json                 (Processing status)
├── scan_<uuid>/
│   └── ...
└── config.json                     (App settings, auth token)
```

**Core Data (Optional):**
Used for quick querying of scans by timestamp, status, size.

```swift
import CoreData

@Entity
final class LocalScanEntity {
    @Attribute(.unique) var id: UUID
    var timestamp: Date
    var fileSize: Double
    var processingStatus: String
    var thumbnailData: Data?
    var plyFilePath: String
    var metadataJSON: String
}
```

### 5.2 Upload & Processing Flow

```
┌─────────────────────────────────┐
│ 1. User finishes capture        │
│    Point cloud saved locally    │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ 2. Request upload credentials   │
│    GET /api/v1/scans/upload-url │
│    Response: {                  │
│      "scan_id": "uuid",         │
│      "s3_url": "presigned URL"  │
│    }                            │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ 3. Upload to S3 (multipart)     │
│    PUT <s3_url> + point cloud   │
│    Track progress (Combine)     │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ 4. Notify backend (processing)  │
│    POST /api/v1/scans/process   │
│    {"scan_id": "uuid"}          │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ 5. Poll for status              │
│    GET /api/v1/scans/{id}/status│
│    Every 1 second               │
│    Response includes:           │
│    • current_step               │
│    • progress (0–1)             │
│    • result_s3_paths (if done)  │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ 6. Download results (optional)  │
│    GET /s3/{fbx_url}            │
│    GET /s3/{glb_url}            │
│    Cache locally                │
└─────────────────────────────────┘
```

**API Client Implementation:**
```swift
class APIClient {
    let baseURL: URL
    let session: URLSession
    
    func requestUploadCredentials() async throws -> UploadCredentials {
        let url = baseURL.appendingPathComponent("/api/v1/scans/upload-url")
        let (data, response) = try await session.data(from: url)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw APIError.badResponse
        }
        
        return try JSONDecoder().decode(UploadCredentials.self, from: data)
    }
    
    func uploadToS3(url: URL, fileURL: URL, progress: @escaping (Double) -> Void) async throws {
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        
        let fileData = try Data(contentsOf: fileURL)
        
        let (_, response) = try await session.upload(for: request, from: fileData)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw APIError.uploadFailed
        }
    }
    
    func startProcessing(scanId: String) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/api/v1/scans/process"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["scan_id": scanId]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (_, response) = try await session.data(for: request)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw APIError.badResponse
        }
    }
    
    func checkProcessingStatus(scanId: String) async throws -> ProcessingStatus {
        let url = baseURL.appendingPathComponent("/api/v1/scans/\(scanId)/status")
        let (data, _) = try await session.data(from: url)
        
        return try JSONDecoder().decode(ProcessingStatus.self, from: data)
    }
}
```

---

## 6. Error Handling & Recovery

### 6.1 Common Failures

| Scenario | Root Cause | Recovery |
|----------|-----------|----------|
| **ARKit capture fails** | No LiDAR hardware, camera permission denied | Show error, request permissions, suggest alternative devices |
| **Upload stalls** | Poor network, S3 timeout | Retry with exponential backoff (3x max) |
| **Processing timeout** | Backend overloaded, crash | Notify user, allow retry later |
| **Low-quality scan** | Poor lighting, motion blur | Suggest retake, show confidence score |

### 6.2 Network Retry Logic

```swift
func uploadWithRetry(fileURL: URL, maxRetries: Int = 3) async throws {
    var lastError: Error?
    
    for attempt in 1...maxRetries {
        do {
            try await uploadToS3(fileURL: fileURL)
            return
        } catch {
            lastError = error
            
            // Exponential backoff: 1s, 2s, 4s
            let delay = UInt64(pow(2, Double(attempt - 1)) * 1_000_000_000)
            try await Task.sleep(nanoseconds: delay)
        }
    }
    
    throw lastError ?? APIError.maxRetriesExceeded
}
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```swift
import XCTest
@testable import FashionTechScan

class ARKitDepthCaptureTests: XCTestCase {
    var capture: ARKitDepthCapture!
    
    override func setUp() {
        super.setUp()
        capture = ARKitDepthCapture()
    }
    
    func testCaptureStartsSuccessfully() {
        capture.startCapture()
        XCTAssertTrue(capture.isRecording)
    }
    
    func testDepthFrameAccumulation() {
        // Mock ARFrame with depth data
        let mockFrame = createMockARFrame()
        capture.processFrame(mockFrame)
        
        XCTAssertGreaterThan(capture.depthFrames.count, 0)
    }
    
    func testMergePointClouds() {
        let cloud1 = createMockPointCloud()
        let cloud2 = createMockPointCloud()
        
        let merged = capture.mergePointClouds([cloud1, cloud2])
        
        // Merged should have more points than individual clouds
        XCTAssertGreaterThan(merged.count, cloud1.count)
    }
}

class ScanProcessorTests: XCTestCase {
    var processor: ScanProcessor!
    
    override func setUp() {
        super.setUp()
        processor = ScanProcessor()
    }
    
    func testUploadSuccess() async throws {
        let mockData = Data(repeating: 0, count: 1024)
        let url = try processor.uploadToS3(data: mockData)
        
        XCTAssertNotNil(url)
    }
}
```

### 7.2 Integration Tests

```swift
class EndToEndScanTests: XCTestCase {
    func testFullScanPipeline() async throws {
        // 1. Simulate user scanning
        let capture = ARKitDepthCapture()
        capture.startCapture()
        
        // Wait for ~20 seconds of mock depth frames
        try await Task.sleep(nanoseconds: 20_000_000_000)
        
        let (cloud, confidence) = capture.stopCapture()
        
        // 2. Upload
        let processor = ScanProcessor()
        let scanId = try await processor.uploadAndProcess(
            pointCloud: cloud,
            confidence: confidence
        )
        
        // 3. Verify processing completes
        var status = try await processor.checkStatus(scanId)
        while !status.isComplete {
            try await Task.sleep(nanoseconds: 1_000_000_000)
            status = try await processor.checkStatus(scanId)
        }
        
        XCTAssertTrue(status.isComplete)
        XCTAssertNotNil(status.fbxUrl)
        XCTAssertNotNil(status.glbUrl)
    }
}
```

### 7.3 Device Testing

**Test Devices:**
- iPhone 14 Pro Max (primary)
- iPhone 12 Pro
- iPad Pro 12.9" (M2) — if LiDAR equipped

**Test Scenarios:**
- ✅ Normal lighting
- ✅ Low light (< 50 lux)
- ✅ Reflective clothing (shiny, metallic)
- ✅ Loose clothing (baggy shirts, dresses)
- ✅ Movement during scan (user motion)
- ✅ Diverse body types (different BMI ranges)

---

## 8. Performance Optimization

### 8.1 Memory Management

**Depth Frame Buffer:**
- Keep only last 5–10 frames in memory (not all 30fps)
- Decimate depth data (320×256 → 160×128) if needed
- Release intermediate point clouds after merging

**App Size:**
- Compress video assets (target <20MB)
- Use App Thinning (bitcode, assets by device)
- Target app size: <150MB

### 8.2 Battery Optimization

- Use `.economyQoS` for background processing
- Minimize screen brightness during capture (or let user control)
- Disable screen timeout during capture
- Stop ARKit session when not in use

---

## 9. Roadmap

### Week 1: Skeleton & ARKit Integration
- [ ] Xcode project setup
- [ ] SwiftUI view structure
- [ ] ARKit depth capture (mock or real)
- [ ] Local point cloud storage

### Week 2: UI Polish & Backend Integration
- [ ] Onboarding video & animations
- [ ] Upload flow (S3 presigned URLs)
- [ ] Status polling + UI updates
- [ ] Error handling + retries
- [ ] Local scan history

---

## 10. Success Metrics

✅ App launches < 2 seconds  
✅ ARKit preview renders at 30fps  
✅ Capture takes 20–30 seconds  
✅ Upload + processing completes within 3 minutes (90th percentile)  
✅ <5% retry rate on uploads  
✅ App size <150MB  
✅ New users scan successfully without help  

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Review:** After Week 1 prototype
