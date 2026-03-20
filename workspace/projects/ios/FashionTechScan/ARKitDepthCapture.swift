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
        config.planeDetection = []
        config.environmentTexturing = .automatic
        
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
        
        let (cloud, confidences) = mergeDepthFrames()
        
        return (cloud, confidences)
    }
    
    // MARK: - ARSessionDelegate
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        guard isCapturing else { return }
        
        guard let depthData = frame.capturedDepthData else {
            print("⚠️ No depth data in frame")
            return
        }
        
        depthFrameCount += 1
        depthFrames.append((frame: frame, timestamp: frame.timestamp))
        
        if let pixelBuffer = frame.capturedImage as? CVPixelBuffer {
            rgbFrames.append(pixelBuffer)
        }
        
        if depthFrameCount % 3 == 0 {
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
        
        let points = extractPointCloud(depthData, intrinsics: frame.camera.intrinsics)
        
        DispatchQueue.main.async {
            self.pointCloudPoints = points
            self.confidence = 0.85
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
        
        let fx = intrinsics[0, 0]
        let fy = intrinsics[1, 1]
        let cx = intrinsics[2, 0]
        let cy = intrinsics[2, 1]
        
        for y in 0..<height {
            for x in 0..<width {
                let depth = floatBuffer[y * width + x]
                
                guard depth > 0 && depth < 5.0 else { continue }
                
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
    
    // MARK: - Frame Merging
    
    private func mergeDepthFrames() -> (pointCloud: [SIMD3<Float>], confidence: [Float]) {
        var mergedCloud: [SIMD3<Float>] = []
        var confidences: [Float] = []
        
        for (frame, _) in depthFrames {
            guard let depthData = frame.capturedDepthData else { continue }
            
            let points = extractPointCloud(depthData, intrinsics: frame.camera.intrinsics)
            mergedCloud.append(contentsOf: points)
            
            confidences.append(contentsOf: Array(repeating: Float(0.9), count: points.count))
        }
        
        print("✅ Merged \(mergedCloud.count) points from \(depthFrames.count) frames")
        
        return (mergedCloud, confidences)
    }
}
