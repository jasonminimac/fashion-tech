# FashionTech iOS Body Scan Capture

**Version:** 0.1.0  
**Status:** Week 1 MVP Foundation  
**Minimum iOS:** 14.5  
**Minimum Device:** iPhone 12 Pro+ (LiDAR required)

## Overview

Native iOS app for capturing 3D body scans using iPhone LiDAR depth sensing and ARKit. Point clouds are processed locally and exported as PLY files for pipeline processing.

## Features (Week 1)

- ✅ ARKit LiDAR depth capture at 30fps
- ✅ Real-time point cloud preview
- ✅ Local PLY file export
- ✅ Metadata JSON export
- ✅ Scan history management (skeleton)

## Setup

### Requirements

- Xcode 14+ (with iOS 14.5+ SDK)
- iPhone 12 Pro+, iPhone 13 Pro+, iPhone 14 Pro+, or iPhone 15 Pro+ (LiDAR required)
- Swift 5.5+

### Build & Run

```bash
# Open in Xcode
open FashionTechScan.xcodeproj

# Or from command line
xcodebuild -scheme FashionTechScan -configuration Debug

# Run on device
xcodebuild -scheme FashionTechScan -configuration Debug -destination 'platform=iOS,name=iPhone 12 Pro'
```

### Permissions (Info.plist)

The following permissions are required:

```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to capture your 3D body scan using LiDAR.</string>

<key>NSMotionUsageDescription</key>
<string>Motion data helps improve scan alignment and accuracy.</string>
```

## Architecture

### File Structure

```
FashionTechScan/
├── FashionTechScanApp.swift       ← Entry point
├── ARCaptureView.swift             ← Main UI (SwiftUI)
├── ARKitDepthCapture.swift         ← ARKit controller
└── PointCloudWriter.swift          ← File export
```

### Data Flow

```
iPhone LiDAR
    ↓
ARKit.capturedDepthData
    ↓
Extract point cloud (intrinsics + depth map)
    ↓
Merge frames (25 sec capture)
    ↓
Save as PLY + metadata.json
    ↓
Documents/Scans/{scan_id}/
```

## Usage

1. **Start App** — ARKit initialization + permission check
2. **Tap "Start Scan"** — Begin 25-second capture
3. **Follow Guidance** — Circle around body, change elevation
4. **Tap "Finish"** — Stop capture, save PLY locally
5. **Transfer** — Export PLY to computer for Python pipeline

## Output

Each scan produces:

```
Documents/Scans/{scan_id}/
├── scan.ply                 ← Point cloud (PLY format)
└── metadata.json            ← Scan metadata
```

**Example metadata.json:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-18T20:50:00Z",
  "device": "iPhone",
  "point_count": 2500000,
  "capture_duration_sec": 25,
  "status": "captured_locally"
}
```

## ARKit Configuration

### Depth Capture Parameters

- **Frame rate:** 30 fps (ARKit managed)
- **Depth format:** 32-bit floating point
- **Resolution:** 320×256 (standard ARKit depth map)
- **Range:** 0.2 - 5.0 meters
- **Semantics:** Person segmentation with depth

### Camera Intrinsics

Extracted from `ARFrame.camera.intrinsics`:
- Focal length (fx, fy)
- Principal point (cx, cy)
- Used for depth-to-3D projection

## Known Limitations (Week 1)

- ❌ No cloud upload (Week 2)
- ❌ No real-time mesh preview (Week 2)
- ❌ No pose normalization (Week 3)
- ❌ No body segmentation (Week 3)
- ⚠️ No occlusion handling in preview (Week 4)

## Testing

### On Simulator

```bash
# Simulator LiDAR is mocked; depth data will be generated randomly
# Useful for UI testing only; no real depth accuracy
```

### On Device

```bash
# Real LiDAR depth capture only works on physical device
# Requires iPhone 12 Pro+ or newer

# Test flow:
# 1. Run on device
# 2. Tap "Start Scan"
# 3. Circle around test object for 25 sec
# 4. Tap "Finish"
# 5. Check Files app → On My iPhone → FashionTechScan → Documents/Scans/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Person segmentation not supported" | Upgrade to iPhone 12 Pro+ or newer |
| "Tracking limited" | Better lighting, less motion blur |
| "No depth data" | Ensure scene has texture (not blank walls) |
| "File save failed" | Check app has Files permission |

## Performance Targets

- **Capture:** 30 fps sustained (p95 > 25 fps)
- **Frame latency:** < 50ms
- **Point cloud accuracy:** < 10mm per frame
- **Memory:** < 300MB during capture

## Integration with Pipeline

After exporting PLY from device:

```bash
# Transfer via iCloud, email, or USB
# Then process with Python pipeline
python -m pipeline.pipeline Documents/Scans/{scan_id}/scan.ply {scan_id} ./output
```

## Roadmap

- **Week 2** — Backend API integration, cloud upload
- **Week 3** — Body segmentation, pose normalization
- **Week 4** — Blender rigging preview (AR)
- **Phase 2** — NeRF-based super-resolution

## References

- ARKit docs: https://developer.apple.com/arkit/
- Depth capture: https://developer.apple.com/documentation/arkit/ardepthdata
- PLY format: http://paulbourke.net/dataformats/ply/

---

**Maintainer:** 3D Scanning Lead  
**Contact:** team@fashiontech.local
