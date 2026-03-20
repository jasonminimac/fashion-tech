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
        
        // Vertex data
        for i in 0..<points.count {
            let pt = points[i]
            let conf = confidences.indices.contains(i) ? confidences[i] : 0.9
            
            let confInt = UInt8(conf * 255)
            let red = UInt8(255 - confInt)
            let green = confInt
            let blue = UInt8(127)
            
            plyContent += "\(pt.x) \(pt.y) \(pt.z) \(red) \(green) \(blue)\n"
        }
        
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
