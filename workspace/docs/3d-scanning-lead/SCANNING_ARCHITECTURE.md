# 3D Scanning Pipeline Architecture

**Document Owner:** 3D Scanning Lead  
**Date:** 2026-03-17  
**Phase:** MVP (Weeks 1-8)  
**Status:** Architecture & Design

---

## Executive Summary

The 3D Scanning pipeline is the user-facing entry point for Fashion Tech. It converts an iPhone LiDAR scan into a clean, rigged, and normalized 3D body model ready for Blender import and garment fitting.

**Core loop:** Capture (iOS) → Point Cloud Processing → Mesh Generation → Body Segmentation → Normalization → Export

**Success criteria:**
- Scan capture time: <30 seconds on iPhone 12 Pro+
- Reconstruction error: <5mm (validated against manual body measurements)
- Support diverse body types (ages 16–70, BMI 15–50)
- Output: FBX/glTF ready for Blender rigging pipeline

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER (iPhone)                              │
├─────────────────────────────────────────────────────────────────┤
│
│ [ARKit LiDAR Capture]
│  • Depth frames (320×256 depth buffer, 30fps)
│  • RGB video (1080p, 30fps)
│  • Camera intrinsics + IMU data
│  • ~10-30 seconds of recording
│
├─────────────────────────────────────────────────────────────────┤
│
│ [Local On-Device Alignment]
│  • Coarse ICP (Iterative Closest Point)
│  • Real-time preview in AR
│  • ~5MB point cloud data
│
├─────────────────────────────────────────────────────────────────┤
│
│ [Upload to Processing Server]
│  • Compressed point cloud (.xyz or .ply)
│  • Optional: RGB video for post-processing
│
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│            PROCESSING BACKEND (Python / Server)                 │
├─────────────────────────────────────────────────────────────────┤
│
│ [1] POINT CLOUD CLEANUP
│  • Remove noise (statistical outlier removal)
│  • Downsample to uniform density (~10mm voxel size)
│  • Fill small holes (isolated points)
│  • Output: Cleaned point cloud (~500k points)
│
│ [2] MESH GENERATION
│  • Poisson reconstruction or Ball Pivoting Algorithm
│  • Surface extraction from point cloud
│  • Output: Triangle mesh (~100k–200k faces)
│
│ [3] BODY SEGMENTATION
│  • Separate head, torso, left/right arms, left/right legs
│  • Heuristics: Z-axis clustering, body proportions, symmetry
│  • Label vertices by body part
│
│ [4] SYMMETRY ENFORCEMENT
│  • Detect and enforce bilateral symmetry
│  • Mirror asymmetric features (e.g., one arm captured poorly)
│  • Smooth artifacts from scanning noise
│
│ [5] POSE NORMALIZATION
│  • Align to T-pose (arms extended, neutral stance)
│  • Standardize orientation (Z-up, facing +Y)
│  • Scale to consistent height (or preserve original)
│
│ [6] EXPORT
│  • FBX (for Blender import)
│  • glTF (for web preview)
│  • Metadata JSON (body measurements, segmentation labels)
│
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│            DOWNSTREAM: Blender Integration Lead                 │
├─────────────────────────────────────────────────────────────────┤
│
│ [Blender Import & Rigging]
│  • Auto-rig using Rigify addon + pose detection
│  • Weight painting for deformation
│  • Shape keys for body type variation
│  • Export animation-ready .blend
│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Subsystems

### 2.1 iOS ARKit Capture (App Module)

**Goal:** Record a high-quality LiDAR scan in <30 seconds with minimal user friction.

**Requirements:**
- iPhone 12 Pro, 12 Pro Max, 13 Pro, 13 Pro Max, 14 Pro, 14 Pro Max (LiDAR capable)
- iOS 14.5+
- ARKit 5+
- Local on-device preview (AR overlay)

**Capture Strategy:**
1. **Depth Buffer Streaming:** ARKit provides 30fps depth frames (320×256)
   - Use `ARFrame.capturedDepthData` (LiDAR raw data)
   - Also capture RGB video frame for later reference
2. **Frame Accumulation:** Merge frames using IMU (accelerometer + gyro) for rough tracking
3. **User Guidance:** On-screen prompts (circle around body, keep still at end)
4. **Confidence Filtering:** Flag low-confidence depth values (occlusions, reflections)

**Technical Approach:**
- Use ARKit's `ARWorldTrackingConfiguration` with `frameSemantics = [.personSegmentationWithDepth]`
- Accumulate depth frames in a fixed-size circular buffer (~5 seconds, decimated to 5fps)
- Apply coarse ICP alignment to estimate camera pose between frames
- Merge aligned frames into a unified point cloud

**Output:**
- Raw point cloud: XYZ coordinates + confidence scores (~1–5M points)
- Camera trajectory: Poses for each captured frame
- RGB video (optional, for debugging/texture)

**Deliverables (Week 1–2):**
- iOS app skeleton (Xcode project, Swift + SwiftUI)
- ARKit integration (depth capture, IMU fusion)
- AR preview (render point cloud in real-time)
- File export (save point cloud to .ply format)

**Success Metrics:**
- <30 second total scan time (capture + preview)
- <200MB app size
- 60fps UI responsiveness

---

### 2.2 Point Cloud Processing Pipeline (Backend Module)

**Goal:** Convert noisy LiDAR point cloud → clean, segmented mesh in <2 minutes.

**Inputs:**
- Point cloud (.ply file, ~1–5M points)
- Camera intrinsics (optional, for refinement)
- Confidence scores per point (from ARKit)

**Processing Steps:**

#### Step 1: Noise Removal & Outlier Filtering
```python
# Pseudocode
import open3d as o3d

pcd = o3d.io.read_point_cloud("scan.ply")

# Statistical outlier removal
pcd_clean, _ = pcd.remove_statistical_outliers(
    nb_neighbors=20, 
    std_ratio=2.0
)

# Confidence-based filtering (remove low-confidence points)
pcd_clean = pcd_clean.select_by_index(confidence_mask)
```
- Remove isolated points (statistical outlier detection)
- Filter by confidence score (keep points with confidence >0.8)
- Output: ~500k–1M points

#### Step 2: Downsampling
```python
# Voxel grid downsampling (uniform density)
pcd_down = pcd_clean.voxel_down_sample(voxel_size=0.01)  # 10mm voxel size
```
- Reduces computation for downstream steps
- Creates uniform point density (easier for meshing)
- Output: ~100k–500k points

#### Step 3: Normal Estimation
```python
pcd_down.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(
        radius=0.1, max_nn=30
    )
)
```
- Estimate surface normals (required for Poisson reconstruction)
- Orient normals outward (consistent direction)

#### Step 4: Mesh Generation (Poisson Reconstruction)
```python
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd_down, 
    depth=9,  # octree depth (higher = more detail)
    width=0, linear_fit=False
)

# Trim low-density voxels
mesh = mesh.remove_degenerate_triangles()
mesh.remove_duplicate_vertices()
```
- Convert point cloud to triangle mesh
- Handles holes and smooths noise
- Typical output: 100k–200k vertices

**Alternative: Ball Pivoting Algorithm**
```python
# For denser point clouds with better boundary definition
radii = [0.01, 0.02, 0.05]
mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
    pcd_down, 
    o3d.utility.DoubleVector(radii)
)
```
- More detail-preserving, but requires denser point cloud
- Better for high-quality scans

**Decision:** Use **Poisson** for MVP (robust, handles holes). Switch to **Ball Pivoting** if LiDAR data is dense enough.

#### Step 5: Hole Filling & Smoothing
```python
# Fill small holes
mesh = mesh.remove_unreferenced_vertices()

# Laplacian smoothing (optional, only if noisy)
mesh = mesh.filter_smooth_laplacian(number_of_iterations=5)
```
- Fill gaps from occlusions (e.g., between legs)
- Smooth artifacts from sensor noise

**Output:**
- Cleaned mesh: ~100k–200k vertices, manifold topology

#### Step 6: Body Segmentation (Heuristic-Based)
```python
# Simple heuristic segmentation
vertices = np.asarray(mesh.vertices)

# Identify body parts based on spatial position
# Head: highest Z, smallest cross-section
# Torso: mid-height, largest cross-section
# Arms/Legs: defined by Z-ranges and distance from torso centerline

def segment_body(vertices):
    z_values = vertices[:, 2]
    
    # Define Z-ranges (relative to height)
    z_min, z_max = z_values.min(), z_values.max()
    height = z_max - z_min
    
    head_z_min = z_max - 0.15 * height
    torso_z_min = z_max - 0.65 * height
    leg_z_min = z_min
    
    # Segment
    segmentation = np.zeros(len(vertices), dtype=int)
    
    # Head (top 15% of height)
    segmentation[z_values > head_z_min] = 1  # Head
    
    # Torso (next 50%)
    torso_mask = (z_values > torso_z_min) & (z_values <= head_z_min)
    segmentation[torso_mask] = 2  # Torso
    
    # Arms/Legs (by distance from centerline)
    # ... (requires analyzing cross-sections)
    
    # Legs (bottom 35%)
    segmentation[z_values < leg_z_min + 0.35 * height] = 5  # Legs
    
    return segmentation

segmentation = segment_body(vertices)
```

**Labels:**
- 0: Unassigned
- 1: Head
- 2: Torso
- 3: Left Arm
- 4: Right Arm
- 5: Legs

**Approach:**
- **MVP (Week 3):** Simple heuristics (Z-axis ranges, cross-sectional analysis)
- **Phase 2:** ML-based segmentation (PointNet++, Semantic3D)

#### Step 7: Symmetry Enforcement
```python
# Detect bilateral symmetry plane (typically YZ plane at centerline)
def enforce_symmetry(mesh):
    vertices = np.asarray(mesh.vertices)
    
    # Find centerline (X = 0 plane)
    x_center = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
    
    # For each vertex, find mirror candidate on opposite side
    # Average symmetric pairs to enforce bilateral symmetry
    for i, v in enumerate(vertices):
        mirror_candidate = np.array([-v[0] + 2*x_center, v[1], v[2]])
        
        # Find closest vertex to mirror_candidate
        closest_j = np.argmin(np.linalg.norm(vertices - mirror_candidate, axis=1))
        
        # Average positions
        vertices[i] = (v + vertices[closest_j]) / 2
        vertices[closest_j] = (v + vertices[closest_j]) / 2
    
    return mesh
```

- Enforces left-right symmetry (typical for human body)
- Handles asymmetric scans (e.g., one arm captured worse)
- Output: Symmetric mesh

#### Step 8: Pose Normalization (T-Pose Alignment)
```python
def normalize_pose(mesh):
    vertices = np.asarray(mesh.vertices)
    
    # 1. Orient to canonical direction (Z-up, Y-forward)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(vertices)
    
    # Find principal axes (PCA)
    cov = np.cov(vertices.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov)
    
    # Align longest axis to Z (height)
    longest_idx = np.argmax(eigenvalues)
    z_axis = eigenvectors[:, longest_idx]
    
    # Ensure Z points up (positive)
    if z_axis[2] < 0:
        z_axis *= -1
    
    # 2. Center at origin (feet at Z=0 or mid-body at origin)
    z_min = vertices[:, 2].min()
    vertices[:, 2] -= z_min  # Move feet to Z=0
    
    # Center XY (face +Y)
    x_center = vertices[:, 0].mean()
    y_center = vertices[:, 1].mean()
    vertices[:, 0] -= x_center
    vertices[:, 1] -= y_center
    
    return mesh
```

- Align body to canonical orientation (Z-up, standing position)
- Center at origin
- Consistent coordinate frame for downstream rigging

**Output:**
- Normalized mesh (canonical pose, orientation, scale)
- Segmentation labels (JSON)

#### Step 9: Export (FBX + glTF)
```python
# Export mesh
o3d.io.write_triangle_mesh("body_scan.fbx", mesh)
o3d.io.write_triangle_mesh("body_scan.glb", mesh)

# Save segmentation & metadata
metadata = {
    "scan_id": "user_123_scan_001",
    "timestamp": "2026-03-17T10:30:00Z",
    "device": "iPhone 14 Pro",
    "point_cloud_size": 500000,
    "mesh_vertices": len(np.asarray(mesh.vertices)),
    "mesh_faces": len(np.asarray(mesh.triangles)),
    "estimated_height": 1.75,  # in meters
    "segmentation": {
        "head_vertices": [...],
        "torso_vertices": [...],
        # ... etc
    },
    "quality_score": 0.92  # 0-1 confidence
}

with open("scan_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

**Outputs:**
- `body_scan.fbx` (for Blender)
- `body_scan.glb` (for web viewer)
- `scan_metadata.json` (body measurements, segmentation, quality metrics)

---

### 2.3 Processing Pipeline Orchestration

**Goal:** Coordinate all steps into a single, robust pipeline.

**Technology Stack:**
- **Language:** Python 3.10+
- **Libraries:** Open3D, NumPy, SciPy, PyVista
- **Async Framework:** FastAPI (for REST API)
- **Job Queue:** Celery + Redis (for background processing)
- **Storage:** AWS S3 (scans, results)

**API Endpoint (FastAPI):**
```python
@app.post("/api/v1/scans/process")
async def process_scan(scan_id: str, file_path: str):
    """
    Trigger point cloud processing.
    
    Args:
        scan_id: User's scan ID
        file_path: S3 path to uploaded .ply file
    
    Returns:
        {
            "job_id": "celery_task_123",
            "status": "processing",
            "eta_seconds": 120
        }
    """
    task = process_scan_task.delay(scan_id, file_path)
    return {"job_id": task.id, "status": "processing"}

@celery_app.task
def process_scan_task(scan_id: str, file_path: str):
    # Download from S3
    pcd = download_point_cloud(file_path)
    
    # Step 1: Clean
    pcd_clean = clean_point_cloud(pcd)
    
    # Step 2: Mesh
    mesh = generate_mesh(pcd_clean)
    
    # Step 3: Segment
    segmentation = segment_body(mesh)
    
    # Step 4: Symmetry
    mesh = enforce_symmetry(mesh)
    
    # Step 5: Normalize
    mesh = normalize_pose(mesh)
    
    # Step 6: Export
    save_results(scan_id, mesh, segmentation)
    
    return {"scan_id": scan_id, "status": "completed"}
```

**Estimated Processing Time:** 60–120 seconds per scan (most time spent in Poisson reconstruction)

---

## 3. iOS App Architecture

**Goal:** Build a lightweight, user-friendly scanning app.

**Tech Stack:**
- **Language:** Swift 5.5+
- **UI:** SwiftUI (modern, declarative)
- **Framework:** ARKit 5, RealityKit
- **Storage:** FileManager, Core Data (for local scans)

**Core Components:**

### 3.1 ARKit Depth Capture Module
```swift
import ARKit

class ARKitDepthCapture: NSObject, ARSessionDelegate {
    var arSession: ARSession
    var depthFrames: [ARFrame] = []
    var rgbFrames: [CVPixelBuffer] = []
    var isRecording = false
    
    func startCapture() {
        isRecording = true
        depthFrames.removeAll()
        
        let config = ARWorldTrackingConfiguration()
        config.frameSemantics.insert(.personSegmentationWithDepth)
        config.planeDetection = []  // Not needed for body scanning
        
        arSession.run(config)
    }
    
    func stopCapture() -> (pointCloud: [SIMD3<Float>], confidence: [Float]) {
        isRecording = false
        arSession.pause()
        
        // Merge and return point cloud
        return mergeDepthFrames(depthFrames)
    }
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        if !isRecording { return }
        
        guard let depthData = frame.capturedDepthData else { return }
        
        depthFrames.append(frame)
        
        // Save RGB frame
        if let pixelBuffer = frame.capturedImage as? CVPixelBuffer {
            rgbFrames.append(pixelBuffer)
        }
    }
    
    private func mergeDepthFrames(_ frames: [ARFrame]) -> (pointCloud: [SIMD3<Float>], confidence: [Float]) {
        // Use coarse ICP to align frames
        // Merge into unified point cloud
        // Return XYZ + confidence scores
    }
}
```

### 3.2 AR Preview Module
```swift
class ARPreviewViewController: UIViewController, ARViewDelegate {
    @IBOutlet var arView: ARView!
    var pointCloud: PointCloudModel?
    
    func displayPointCloud(_ points: [SIMD3<Float>]) {
        // Render point cloud in AR using RealityKit
        pointCloud = PointCloudModel(points: points)
        arView.scene.addAnchor(pointCloud!)
    }
}
```

### 3.3 Scan Manager (Orchestration)
```swift
class ScanManager: NSObject {
    let capture = ARKitDepthCapture()
    let uploader = ScanUploader()
    
    func performScan(duration: TimeInterval = 20) async {
        // 1. Capture
        capture.startCapture()
        try? await Task.sleep(nanoseconds: UInt64(duration * 1e9))
        let (pointCloud, confidence) = capture.stopCapture()
        
        // 2. Local alignment (optional coarse ICP)
        let alignedCloud = alignPointCloud(pointCloud)
        
        // 3. Save locally
        let scanId = UUID().uuidString
        saveScanLocally(scanId, alignedCloud)
        
        // 4. Upload to backend
        await uploader.uploadScan(scanId, alignedCloud)
    }
}
```

**Deliverables (Week 1–2):**
- Xcode project + app skeleton
- ARKit capture + preview
- File export (.ply)
- Error handling (low light, motion blur, etc.)

---

## 4. Quality Assurance & Validation

### 4.1 Reconstruction Error Measurement

**Goal:** Validate <5mm error against ground truth.

**Approach:**
1. **Synthetic Test Scans:** Generate point clouds from 3D body models with known geometry
2. **Real Test Scans:** Use 3D body scans from commercial scanners (RealityCapture, Structure.io) as ground truth
3. **Error Metrics:**
   - **Hausdorff Distance:** Max distance between reconstructed and ground truth meshes
   - **Chamfer Distance:** Average bidirectional distance between point sets
   - **Volume Difference:** How well does the reconstructed mesh enclose the true body?

**Success Criteria:**
- Mean Chamfer Distance: <5mm
- Hausdorff Distance: <15mm
- 95% of surface points within 10mm

### 4.2 Diversity Testing

**Body Types to Test:**
- Age range: 16–70 years
- BMI range: 15–45
- Height: 150cm–200cm
- Ethnicities: Represent diverse skin tones (affects LiDAR reflectance)
- Clothing: Various fabrics (reflective, tight, loose, transparent)

**Test Protocol:**
1. Recruit 10 users across body type spectrum
2. Perform 2–3 scans per user (different clothing, lighting)
3. Measure reconstruction error + segmentation accuracy
4. Log failures / edge cases

**Acceptance Criteria:** 90% of scans produce <5mm error mesh

---

## 5. Dependencies & Integration Points

### 5.1 Upstream (iOS App)
- Depends on: ARKit, iOS 14.5+
- Deliverable: Point cloud files (.ply, ~5MB each)

### 5.2 Downstream (Blender Integration Lead)
- Receives: FBX + metadata JSON
- Uses: Mesh + segmentation labels for rigging
- Feedback loop: Report rigging failures, mesh quality issues

### 5.3 Backend (Backend Engineer)
- Handles: S3 storage, scan metadata DB
- Provides: Upload URLs, scan status API
- Receives: Processing results for web viewer

### 5.4 Frontend (Frontend Engineer)
- Receives: glTF + preview images
- Uses: Web 3D viewer (Three.js)
- Feedback: UX issues (slow uploads, confusing UI)

---

## 6. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **LiDAR accuracy insufficient** | High | Test on diverse body types early (Week 2). Fall back to photogrammetry if needed. |
| **Automated segmentation fails** | Medium | Start with heuristics. Add ML segmentation in Phase 2 if accuracy <90%. |
| **Processing time >2min** | Medium | Optimize Poisson depth parameter. Use Ball Pivoting if faster. Parallelize with Celery workers. |
| **Users wear reflective/shiny clothing** | Medium | Add guidance UI (wear matte clothing). Post-process to remove outliers. |
| **App crashes during capture** | High | Rigorous testing on target devices. Error handling for low memory. |

---

## 7. Development Roadmap

### Week 1–2: iOS Capture & ARKit Integration
- [ ] Xcode project setup
- [ ] ARKit depth capture
- [ ] AR preview rendering
- [ ] File export (.ply)
- [ ] User guidance UI

### Week 2–3: Point Cloud Processing
- [ ] Open3D pipeline setup
- [ ] Noise removal + downsampling
- [ ] Normal estimation
- [ ] Poisson mesh generation

### Week 3–4: Body Segmentation & Normalization
- [ ] Heuristic-based segmentation
- [ ] Symmetry enforcement
- [ ] Pose normalization (T-pose)
- [ ] Validation on test scans

### Week 4–5: Export & Integration
- [ ] FBX export
- [ ] glTF export
- [ ] Metadata JSON
- [ ] Integration with Blender Lead

### Week 5–8: Testing & Refinement
- [ ] Quality validation (reconstruction error)
- [ ] Diversity testing (body types)
- [ ] Performance optimization
- [ ] Bug fixes + UX polish

---

## 8. Success Metrics (MVP)

✅ **Capture:**
- <30 second total time
- Works on iPhone 12 Pro+
- Provides AR preview

✅ **Processing:**
- <2 minutes end-to-end
- <5mm reconstruction error (validated on 10+ users)
- Handles diverse body types (BMI 15–45)

✅ **Export:**
- Valid FBX for Blender import
- Clean glTF for web viewer
- Accurate segmentation labels

✅ **Team:**
- Unblocked Blender Lead (receives clean meshes)
- Unblocked Frontend Engineer (receives glTF)
- Clear integration points documented

---

## Next Steps

1. **Finalize iOS App Design:** Confirm app UI/UX with Product
2. **Set up Infrastructure:** S3 bucket, Celery workers, FastAPI server
3. **Prototype ARKit Capture:** Week 1 goal
4. **Prototype Point Cloud Pipeline:** Week 2 goal
5. **Weekly Check-in:** Sync with Blender Lead on mesh quality expectations

---

**Version:** 1.0  
**Last Updated:** 2026-03-17
