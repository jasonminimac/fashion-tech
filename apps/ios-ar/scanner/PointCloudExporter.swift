import Foundation
import ARKit
import simd

/// Accumulates world-space 3D points from ARFrame depth maps.
/// Thread-safe for concurrent reads; append must be called from a single serial queue.
class PointCloudAccumulator {

    // MARK: - Storage

    private var points: [simd_float3] = []
    private let lock = NSLock()

    var pointCount: Int {
        lock.lock(); defer { lock.unlock() }
        return points.count
    }

    // MARK: - Public API

    func reset() {
        lock.lock(); defer { lock.unlock() }
        points.removeAll()
    }

    /// Extracts world-space points from the given ARFrame's scene depth map
    /// and appends them to the accumulator.
    ///
    /// - Parameter frame: The ARFrame containing sceneDepth and camera intrinsics.
    /// - Parameter stride: Pixel sampling stride (default 4 — every 4th pixel in each axis).
    func accumulate(frame: ARFrame, stride: Int = 4) {
        guard let depthMap = frame.sceneDepth?.depthMap else { return }

        let width  = CVPixelBufferGetWidth(depthMap)
        let height = CVPixelBufferGetHeight(depthMap)

        CVPixelBufferLockBaseAddress(depthMap, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(depthMap, .readOnly) }

        guard let base = CVPixelBufferGetBaseAddress(depthMap) else { return }
        let floatBuf = base.assumingMemoryBound(to: Float32.self)

        // Camera intrinsics: [fx, 0, cx / 0, fy, cy / 0, 0, 1] (column-major)
        let intrinsics = frame.camera.intrinsics
        let fx = intrinsics[0][0]
        let fy = intrinsics[1][1]
        let cx = intrinsics[2][0]
        let cy = intrinsics[2][1]

        let viewTransform = frame.camera.transform

        var newPoints: [simd_float3] = []
        newPoints.reserveCapacity((width / stride) * (height / stride))

        for row in Swift.stride(from: 0, to: height, by: stride) {
            for col in Swift.stride(from: 0, to: width, by: stride) {
                let depth = floatBuf[row * width + col]
                // Skip invalid / too-far depths (beyond 4 m for body scanning)
                guard depth > 0.1 && depth < 4.0 else { continue }
                // Back-project to camera-local 3D
                let localX = (Float(col) - cx) / fx * depth
                let localY = (Float(row) - cy) / fy * depth
                let localPoint = simd_float4(localX, localY, depth, 1.0)
                // Transform to world space
                let worldPoint = viewTransform * localPoint
                newPoints.append(simd_float3(worldPoint.x, worldPoint.y, worldPoint.z))
            }
        }

        lock.lock()
        points.append(contentsOf: newPoints)
        lock.unlock()
    }

    /// Returns a copy of all accumulated points.
    func snapshot() -> [simd_float3] {
        lock.lock(); defer { lock.unlock() }
        return points
    }
}

// MARK: -

/// Serialises an accumulated point cloud to a binary PLY file on disk.
class PointCloudExporter {

    let accumulator: PointCloudAccumulator
    let scanID: String

    init(accumulator: PointCloudAccumulator, scanID: String) {
        self.accumulator = accumulator
        self.scanID = scanID
    }

    /// Writes a binary little-endian PLY file to the app's Documents/Scans/ directory.
    /// - Returns: URL of the written file.
    func exportPLY() throws -> URL {
        let points = accumulator.snapshot()
        guard !points.isEmpty else {
            throw ExportError.noPoints
        }

        let scansDir = try Self.scansDirectory()
        let fileName = "scan-\(scanID).ply"
        let fileURL = scansDir.appendingPathComponent(fileName)

        var data = Data()

        // ASCII header
        let header = """
        ply\r\n\
        format binary_little_endian 1.0\r\n\
        element vertex \(points.count)\r\n\
        property float x\r\n\
        property float y\r\n\
        property float z\r\n\
        end_header\r\n
        """
        data.append(contentsOf: header.utf8)

        // Binary body — 3× Float32 per point, little-endian
        data.reserveCapacity(data.count + points.count * 12)
        for pt in points {
            var x = pt.x.littleEndian
            var y = pt.y.littleEndian
            var z = pt.z.littleEndian
            withUnsafeBytes(of: &x) { data.append(contentsOf: $0) }
            withUnsafeBytes(of: &y) { data.append(contentsOf: $0) }
            withUnsafeBytes(of: &z) { data.append(contentsOf: $0) }
        }

        try data.write(to: fileURL, options: .atomic)
        return fileURL
    }

    // MARK: - Helpers

    static func scansDirectory() throws -> URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let scans = docs.appendingPathComponent("Scans", isDirectory: true)
        try FileManager.default.createDirectory(at: scans, withIntermediateDirectories: true)
        return scans
    }

    enum ExportError: LocalizedError {
        case noPoints
        var errorDescription: String? {
            switch self {
            case .noPoints: return "No points were accumulated — scan duration may have been too short."
            }
        }
    }
}

// MARK: - ScanSessionManager

/// Manages scan session lifecycle: timing, frame throttle, metadata JSON.
class ScanSessionManager {

    private(set) var scanID: String = UUID().uuidString
    private var startDate: Date = Date()
    private var frameCounter = 0
    private let frameAccumulateInterval = 3   // accumulate every Nth frame

    func beginSession() {
        scanID = UUID().uuidString
        startDate = Date()
        frameCounter = 0
    }

    func endSession() {}

    /// Returns true when the current frame should be accumulated (throttle logic).
    func shouldAccumulateFrame() -> Bool {
        frameCounter += 1
        return frameCounter % frameAccumulateInterval == 0
    }

    /// Writes a metadata JSON file alongside the PLY.
    func writeMetadata(pointCount: Int, plyURL: URL) throws -> URL {
        let duration = Date().timeIntervalSince(startDate)
        let meta: [String: Any] = [
            "scan_id": scanID,
            "ios_version": UIDevice.current.systemVersion,
            "device_model": UIDevice.current.model,
            "capture_duration_s": round(duration * 10) / 10,
            "point_count": pointCount,
            "timestamp": ISO8601DateFormatter().string(from: startDate)
        ]
        let metaURL = plyURL.deletingLastPathComponent()
            .appendingPathComponent("scan-\(scanID)-meta.json")
        let jsonData = try JSONSerialization.data(withJSONObject: meta, options: .prettyPrinted)
        try jsonData.write(to: metaURL, options: .atomic)
        return metaURL
    }
}
