import SwiftUI

struct ARCaptureView: View {
    @StateObject private var depthCapture = ARKitDepthCapture()
    @State private var isCapturing = false
    @State private var elapsedTime = 0
    @State private var captureTimer: Timer?
    @State private var lastMessage = ""
    @State private var showError = false
    
    let targetDuration = 25
    
    var body: some View {
        ZStack {
            // Placeholder for ARView (actual ARView requires UIViewControllerRepresentable)
            Color.black.ignoresSafeArea()
            
            VStack {
                // Title
                Text("Body Scan")
                    .font(.title)
                    .foregroundColor(.white)
                    .padding()
                
                Spacer()
                
                // Status
                VStack(spacing: 16) {
                    Text("\(elapsedTime) / \(targetDuration) seconds")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    ProgressView(value: Double(elapsedTime), total: Double(targetDuration))
                        .tint(.green)
                        .frame(height: 6)
                    
                    Text(getGuidanceText())
                        .font(.body)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                }
                .padding()
                .background(Color.black.opacity(0.6))
                .cornerRadius(12)
                .padding()
                
                Spacer()
                
                // Point cloud stats
                if depthCapture.depthFrameCount > 0 {
                    Text("Frames: \(depthCapture.depthFrameCount) | Points: \(depthCapture.pointCloudPoints.count)")
                        .font(.caption)
                        .foregroundColor(.gray)
                        .padding()
                }
                
                // Buttons
                HStack(spacing: 16) {
                    Button(action: startCapture) {
                        Text("Start Scan")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .disabled(isCapturing)
                    
                    Button(action: finishCapture) {
                        Text("Finish")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .disabled(!isCapturing)
                }
                .padding()
            }
            
            if showError {
                Text(lastMessage)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.red.opacity(0.8))
                    .cornerRadius(8)
                    .padding()
            }
        }
    }
    
    private func startCapture() {
        if depthCapture.startCapture() {
            isCapturing = true
            elapsedTime = 0
            lastMessage = "Capture started"
            
            captureTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
                elapsedTime += 1
                
                if elapsedTime >= targetDuration {
                    finishCapture()
                }
            }
        } else {
            lastMessage = "Failed to start capture"
            showError = true
        }
    }
    
    private func finishCapture() {
        captureTimer?.invalidate()
        isCapturing = false
        
        let (points, confidences) = depthCapture.stopCapture()
        
        guard !points.isEmpty else {
            lastMessage = "No point cloud captured"
            showError = true
            return
        }
        
        let scanId = UUID().uuidString
        let plyURL = PointCloudWriter.savePLY(
            points: points,
            confidences: confidences,
            scanId: scanId
        )
        let metadataURL = PointCloudWriter.saveMetadata(
            scanId: scanId,
            pointCount: points.count,
            duration: TimeInterval(elapsedTime)
        )
        
        if plyURL != nil && metadataURL != nil {
            lastMessage = "✅ Scan saved: \(points.count) points"
        } else {
            lastMessage = "❌ Failed to save scan"
            showError = true
        }
    }
    
    private func getGuidanceText() -> String {
        let guidance = [
            "Circle to your left...",
            "Capture from the side...",
            "Circle to your right...",
            "Move to capture from above..."
        ]
        return guidance[elapsedTime % 4]
    }
}

#Preview {
    ARCaptureView()
}
