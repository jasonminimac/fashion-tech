# Point Cloud Processing Pipeline

**Document Owner:** 3D Scanning Lead  
**Date:** 2026-03-17  
**Phase:** MVP (Weeks 2–4)  
**Status:** Implementation Design

---

## 1. Overview

The Point Cloud Processing Pipeline converts raw LiDAR depth data (1–5M noisy points) into a clean, segmented, normalized 3D body mesh in 60–120 seconds.

**Input:** Point cloud (.ply file, ~5MB)  
**Output:** FBX + glTF + JSON metadata  
**Success Metrics:** <5mm error, <2 min processing time, handles diverse body types

---

## 2. System Architecture

```
┌─────────────────────────────────────┐
│ Input: Point Cloud (.ply)           │
│ ~1–5M points, with confidence       │
└────────┬────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 1] Noise Removal & Filtering                  │
│  • Remove outliers (statistical)                     │
│  • Confidence-based filtering                        │
│  • Remove isolated points                            │
│  Output: 500k–1M cleaned points                      │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 2] Downsampling & Density Normalization       │
│  • Voxel grid downsampling (10mm)                    │
│  • Uniform point distribution                        │
│  Output: 100k–500k points                            │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 3] Normal Estimation                          │
│  • Surface normal computation (k-NN, ~30 neighbors)  │
│  • Outward orientation                               │
│  Output: Points + normals                            │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 4] Mesh Generation (Poisson)                  │
│  • Implicit surface reconstruction                   │
│  • Octree depth: 8–9                                 │
│  Output: 100k–200k vertex mesh                       │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 5] Mesh Cleanup & Smoothing                   │
│  • Remove degenerate triangles                       │
│  • Duplicate vertex removal                          │
│  • Optional Laplacian smoothing                      │
│  Output: Clean manifold mesh                         │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 6] Body Segmentation                          │
│  • Separate head, torso, arms, legs                  │
│  • Label vertices by body part                       │
│  Output: Segmentation map (JSON)                     │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 7] Symmetry Enforcement                       │
│  • Detect bilateral symmetry plane                   │
│  • Mirror & average asymmetric features              │
│  Output: Symmetric body mesh                         │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 8] Pose Normalization (T-Pose)                │
│  • PCA-based orientation alignment                   │
│  • Center at origin (feet at Z=0)                    │
│  • Standardize coordinate frame                      │
│  Output: Normalized mesh + transformation            │
└────────┬─────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────┐
│ [Stage 9] Export & Validation                        │
│  • FBX export (for Blender)                          │
│  • glTF/glB export (for web)                         │
│  • Metadata JSON (measurements, quality)             │
│  Output: Three files + quality report                │
└──────────────────────────────────────────────────────┘
```

---

## 3. Detailed Implementation

### 3.1 Stage 1: Noise Removal & Filtering

**Goal:** Remove sensor noise, outliers, and low-confidence points.

**Code:**
```python
import open3d as o3d
import numpy as np
from pathlib import Path

class PointCloudCleaner:
    def __init__(self, config: dict = None):
        self.config = config or {
            "outlier_nb_neighbors": 20,
            "outlier_std_ratio": 2.0,
            "confidence_threshold": 0.8,
        }
    
    def clean(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Remove noise and low-confidence points."""
        
        # Step 1: Statistical outlier removal
        pcd_clean, _ = pcd.remove_statistical_outliers(
            nb_neighbors=self.config["outlier_nb_neighbors"],
            std_ratio=self.config["outlier_std_ratio"]
        )
        
        print(f"After outlier removal: {len(pcd_clean.points)} points")
        
        # Step 2: Confidence filtering (if available as color attribute)
        # Assuming confidence is stored in point colors (grayscale)
        if len(pcd_clean.colors) > 0:
            confidences = np.asarray(pcd_clean.colors)[:, 0]  # Use R channel
            mask = confidences >= self.config["confidence_threshold"]
            pcd_clean = pcd_clean.select_by_index(np.where(mask)[0])
        
        print(f"After confidence filtering: {len(pcd_clean.points)} points")
        
        return pcd_clean

# Usage
if __name__ == "__main__":
    pcd = o3d.io.read_point_cloud("scan.ply")
    cleaner = PointCloudCleaner()
    pcd_clean = cleaner.clean(pcd)
    o3d.io.write_point_cloud("scan_clean.ply", pcd_clean)
```

**Parameters:**
- `outlier_nb_neighbors`: Number of neighbors for statistical test (20–30)
- `outlier_std_ratio`: Std dev threshold (2.0 = conservative, 1.0 = aggressive)
- `confidence_threshold`: Min confidence to keep point (0.7–0.9)

**Output:** ~500k–1M points (50% reduction)

---

### 3.2 Stage 2: Downsampling

**Goal:** Uniform point density for consistent mesh generation.

**Code:**
```python
class PointCloudDownsampler:
    def __init__(self, voxel_size: float = 0.01):
        """
        Args:
            voxel_size: Voxel size in meters (0.01 = 10mm)
        """
        self.voxel_size = voxel_size
    
    def downsample(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Voxel grid downsampling."""
        pcd_down = pcd.voxel_down_sample(self.voxel_size)
        
        print(f"Downsampled to {len(pcd_down.points)} points (voxel size: {self.voxel_size}m)")
        
        return pcd_down

# Usage
downsampler = PointCloudDownsampler(voxel_size=0.01)
pcd_down = downsampler.downsample(pcd_clean)
```

**Voxel Size Impact:**
| Voxel Size | Resulting Points | Quality | Processing Time |
|-----------|-----------------|---------|-----------------|
| 0.005m (5mm) | 300k–500k | High | 2+ minutes |
| 0.01m (10mm) | 100k–200k | Good | 1–2 minutes |
| 0.02m (20mm) | 50k–100k | Lower | 30–60 seconds |

**Recommendation:** Start with **10mm** voxel size (balance of quality/speed).

---

### 3.3 Stage 3: Normal Estimation

**Goal:** Estimate surface normals (required for Poisson reconstruction).

**Code:**
```python
class NormalEstimator:
    def __init__(self, radius: float = 0.1, max_nn: int = 30):
        self.radius = radius
        self.max_nn = max_nn
    
    def estimate(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Estimate normals using hybrid k-NN / radius search."""
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.radius,
                max_nn=self.max_nn
            )
        )
        
        # Orient normals outward (away from centroid)
        pcd.orient_normals_towards_camera_location(
            camera_location=np.array([0.0, 0.0, 0.0])
        )
        
        print(f"Estimated normals for {len(pcd.normals)} points")
        
        return pcd

# Usage
estimator = NormalEstimator(radius=0.1, max_nn=30)
pcd_down = estimator.estimate(pcd_down)
```

**Parameters:**
- `radius`: Search radius for KD-tree (0.05–0.2m, typically 0.1m)
- `max_nn`: Max neighbors to use (20–40, typically 30)

**Output:** Point cloud with estimated normals

---

### 3.4 Stage 4: Mesh Generation (Poisson Reconstruction)

**Goal:** Convert point cloud → manifold triangle mesh.

**Code:**
```python
class MeshGenerator:
    def __init__(self, depth: int = 9, width: int = 0, linear_fit: bool = False):
        """
        Args:
            depth: Octree depth (8–10; higher = more detail but slower)
            width: Smooth width (0 = no smoothing)
            linear_fit: Use linear fit for octree cells
        """
        self.depth = depth
        self.width = width
        self.linear_fit = linear_fit
    
    def generate_poisson(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
        """Poisson surface reconstruction."""
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd,
            depth=self.depth,
            width=self.width,
            linear_fit=self.linear_fit
        )
        
        # Remove low-density voxels
        vertices_to_remove = densities < np.quantile(densities, 0.1)
        mesh.remove_vertices_by_mask(vertices_to_remove)
        
        print(f"Generated mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return mesh
    
    def generate_ball_pivoting(self, pcd: o3d.geometry.PointCloud, radii: list = None) -> o3d.geometry.TriangleMesh:
        """Ball pivoting algorithm (alternative to Poisson)."""
        if radii is None:
            radii = [0.01, 0.02, 0.05]
        
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd,
            o3d.utility.DoubleVector(radii)
        )
        
        print(f"Ball pivoting mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return mesh

# Usage
generator = MeshGenerator(depth=9, width=0, linear_fit=False)
mesh = generator.generate_poisson(pcd_down)

# Alternative: Ball pivoting (for denser clouds)
# mesh = generator.generate_ball_pivoting(pcd_down, radii=[0.01, 0.02, 0.05])
```

**Comparison:**
| Aspect | Poisson | Ball Pivoting |
|--------|---------|---------------|
| **Robustness** | Excellent (handles holes) | Good (requires dense cloud) |
| **Speed** | 20–60 sec (depth 9) | 5–15 sec |
| **Quality** | Smooth, slightly over-smoothed | Detail-preserving |
| **Mesh topology** | Manifold | Can have holes/non-manifold |
| **Best for** | LiDAR scans (gaps) | Dense photogrammetry |

**Recommendation:** Use **Poisson** for MVP (robust to holes from occlusions).

---

### 3.5 Stage 5: Mesh Cleanup

**Goal:** Remove artifacts, ensure manifold topology.

**Code:**
```python
class MeshCleaner:
    def clean(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Clean mesh: remove degenerate triangles, duplicate vertices."""
        
        # Remove degenerate triangles
        mesh.remove_degenerate_triangles()
        
        # Remove duplicate vertices
        mesh.remove_duplicate_vertices()
        
        # Remove unreferenced vertices
        mesh.remove_unreferenced_vertices()
        
        print(f"Cleaned mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return mesh
    
    def smooth(self, mesh: o3d.geometry.TriangleMesh, iterations: int = 5) -> o3d.geometry.TriangleMesh:
        """Laplacian smoothing (reduce noise)."""
        mesh_smooth = mesh.filter_smooth_laplacian(number_of_iterations=iterations)
        
        print(f"Smoothed mesh ({iterations} iterations)")
        
        return mesh_smooth

# Usage
cleaner = MeshCleaner()
mesh = cleaner.clean(mesh)

# Optional: light smoothing if mesh is noisy
# mesh = cleaner.smooth(mesh, iterations=3)
```

**Mesh Repair (if needed):**
```python
def repair_mesh(mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
    """Fix non-manifold edges and vertices."""
    # This is more complex; Open3D has limited repair tools
    # For MVP, assume Poisson generates mostly-clean output
    
    # If issues arise, use trimesh library
    import trimesh
    
    vertices = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)
    
    tm = trimesh.Trimesh(vertices=vertices, faces=triangles)
    tm.merge_vertices()
    tm.remove_degenerate_faces()
    
    # Convert back to Open3D
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(tm.vertices),
        o3d.utility.Vector3iVector(tm.faces)
    )
    
    return mesh
```

---

### 3.6 Stage 6: Body Segmentation

**Goal:** Label vertices by body part (head, torso, arms, legs).

**Code:**
```python
class BodySegmenter:
    def __init__(self):
        pass
    
    def segment(self, mesh: o3d.geometry.TriangleMesh) -> dict:
        """Simple heuristic-based segmentation."""
        
        vertices = np.asarray(mesh.vertices)
        z_values = vertices[:, 2]
        x_values = vertices[:, 0]
        y_values = vertices[:, 1]
        
        # Define Z-ranges (relative to height)
        z_min, z_max = z_values.min(), z_values.max()
        height = z_max - z_min
        
        # Body part Z-ranges
        head_z_min = z_max - 0.12 * height  # Top 12%
        neck_z_min = z_max - 0.20 * height  # Next 8%
        torso_z_min = z_max - 0.65 * height  # Next 45%
        leg_z_min = z_min  # Bottom 35%
        
        # Find torso center (XY centroid in torso region)
        torso_mask = z_values < neck_z_min
        torso_x = np.mean(x_values[torso_mask])
        torso_y = np.mean(y_values[torso_mask])
        
        # Segmentation labels
        segmentation = np.zeros(len(vertices), dtype=int)
        
        # 1. Head (top, small cross-section)
        head_mask = z_values > head_z_min
        segmentation[head_mask] = 1  # Head
        
        # 2. Torso (center region, largest cross-section)
        torso_region_mask = (z_values > torso_z_min) & (z_values <= head_z_min)
        
        # Find arms by distance from torso centerline
        dist_to_center = np.sqrt(
            (x_values[torso_region_mask] - torso_x) ** 2 +
            (y_values[torso_region_mask] - torso_y) ** 2
        )
        
        # Arms are ~0.2–0.4m from center; torso is <0.2m
        arm_threshold = 0.2
        torso_sub_mask = dist_to_center < arm_threshold
        
        torso_indices = np.where(torso_region_mask)[0][torso_sub_mask]
        segmentation[torso_indices] = 2  # Torso
        
        # 3. Arms (sides, mid-height)
        # Split left/right by X position
        arm_region_mask = (z_values > torso_z_min) & (z_values <= head_z_min)
        arm_sub_indices = np.where(arm_region_mask)[0]
        arm_x = x_values[arm_sub_indices]
        
        for idx in arm_sub_indices:
            if x_values[idx] > torso_x + 0.1:
                segmentation[idx] = 3  # Right arm
            elif x_values[idx] < torso_x - 0.1:
                segmentation[idx] = 4  # Left arm
        
        # 4. Legs (bottom 35%)
        leg_mask = z_values < leg_z_min + 0.35 * height
        
        # Split left/right by X position
        leg_indices = np.where(leg_mask)[0]
        for idx in leg_indices:
            if x_values[idx] > torso_x:
                segmentation[idx] = 5  # Right leg
            else:
                segmentation[idx] = 6  # Left leg
        
        # Map to labels
        labels = {
            1: "head",
            2: "torso",
            3: "right_arm",
            4: "left_arm",
            5: "right_leg",
            6: "left_leg"
        }
        
        result = {
            "segmentation": segmentation.tolist(),
            "labels": labels,
            "vertex_counts": {
                labels[i]: np.sum(segmentation == i)
                for i in labels.keys()
            }
        }
        
        return result

# Usage
segmenter = BodySegmenter()
seg_result = segmenter.segment(mesh)

print(f"Segmentation: {seg_result['vertex_counts']}")
```

**Alternative: ML-Based Segmentation (Phase 2)**

For higher accuracy, use a semantic segmentation model:

```python
import torch
from torch_geometric.nn import PointNet2

class MLBodySegmenter:
    def __init__(self, model_path: str):
        self.model = torch.load(model_path)
        self.model.eval()
    
    def segment(self, mesh: o3d.geometry.TriangleMesh) -> dict:
        """ML-based segmentation using PointNet2."""
        vertices = torch.FloatTensor(np.asarray(mesh.vertices))
        
        with torch.no_grad():
            predictions = self.model(vertices)
        
        segmentation = predictions.argmax(dim=1).numpy()
        
        return {
            "segmentation": segmentation.tolist(),
            "confidence": predictions.max(dim=1).values.numpy().tolist()
        }
```

**Labels:**
- 1: Head
- 2: Torso
- 3: Right Arm
- 4: Left Arm
- 5: Right Leg
- 6: Left Leg
- 0: Unlabeled/noise

---

### 3.7 Stage 7: Symmetry Enforcement

**Goal:** Enforce bilateral symmetry (left-right mirror).

**Code:**
```python
class SymmetryEnforcer:
    def __init__(self, symmetry_plane: str = "yz"):
        """
        Args:
            symmetry_plane: 'yz' (left-right), 'xz' (front-back)
        """
        self.symmetry_plane = symmetry_plane
    
    def enforce_bilateral(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Enforce left-right symmetry (YZ plane)."""
        
        vertices = np.asarray(mesh.vertices).copy()
        triangles = np.asarray(mesh.triangles)
        
        # Find symmetry plane (X = x_center)
        x_center = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
        
        # Build KD-tree for efficient nearest neighbor search
        from scipy.spatial import cKDTree
        tree = cKDTree(vertices)
        
        # For each vertex, find mirror candidate
        symmetry_pairs = []
        
        for i, v in enumerate(vertices):
            # Mirror position across YZ plane
            mirror_pos = np.array([
                2 * x_center - v[0],  # Mirror X
                v[1],  # Keep Y
                v[2]   # Keep Z
            ])
            
            # Find closest vertex to mirror position
            dist, j = tree.query(mirror_pos)
            
            if dist < 0.1:  # Within 10cm (reasonable threshold)
                symmetry_pairs.append((i, j, dist))
        
        # Average symmetric pairs
        for i, j, dist in symmetry_pairs:
            avg = (vertices[i] + vertices[j]) / 2
            vertices[i] = avg
            vertices[j] = avg
        
        # Create new mesh
        mesh_sym = o3d.geometry.TriangleMesh(
            o3d.utility.Vector3dVector(vertices),
            o3d.utility.Vector3iVector(triangles)
        )
        
        print(f"Enforced symmetry: matched {len(symmetry_pairs)} vertex pairs")
        
        return mesh_sym

# Usage
enforcer = SymmetryEnforcer()
mesh = enforcer.enforce_bilateral(mesh)
```

**Effect:** Reduces asymmetries from scanning artifacts, produces more natural-looking body.

---

### 3.8 Stage 8: Pose Normalization (T-Pose)

**Goal:** Standardize body orientation and position.

**Code:**
```python
class PoseNormalizer:
    def normalize(self, mesh: o3d.geometry.TriangleMesh) -> tuple:
        """
        Normalize pose to T-pose.
        
        Returns:
            (normalized_mesh, transformation_matrix)
        """
        
        vertices = np.asarray(mesh.vertices).copy()
        triangles = np.asarray(mesh.triangles)
        
        # Step 1: PCA-based orientation
        # Find principal axes
        vertices_centered = vertices - vertices.mean(axis=0)
        cov = np.cov(vertices_centered.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        
        # Sort by eigenvalue (descending)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Longest axis = height (Z)
        # Middle axis = depth (Y)
        # Shortest axis = width (X)
        
        # Build rotation matrix (align to canonical axes)
        R = eigenvectors.T  # Shape: (3, 3)
        
        # Ensure Z-axis points up (positive)
        if R[2, 2] < 0:
            R[2, :] *= -1
        
        # Rotate vertices
        vertices_rotated = (R @ vertices_centered.T).T
        
        # Step 2: Centering
        # Move feet to Z=0
        z_min = vertices_rotated[:, 2].min()
        vertices_rotated[:, 2] -= z_min
        
        # Center XY (face +Y)
        x_center = vertices_rotated[:, 0].mean()
        y_center = vertices_rotated[:, 1].mean()
        vertices_rotated[:, 0] -= x_center
        vertices_rotated[:, 1] -= y_center
        
        # Step 3: Build transformation matrix
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = np.array([-x_center, -y_center, -z_min])
        
        # Create normalized mesh
        mesh_norm = o3d.geometry.TriangleMesh(
            o3d.utility.Vector3dVector(vertices_rotated),
            o3d.utility.Vector3iVector(triangles)
        )
        
        # Estimate body measurements
        height = vertices_rotated[:, 2].max()
        
        print(f"Normalized pose: height={height:.2f}m")
        
        return mesh_norm, T, height

# Usage
normalizer = PoseNormalizer()
mesh, T, height = normalizer.normalize(mesh)
```

**Output:**
- Normalized mesh (T-pose, centered, canonical axes)
- Transformation matrix (for later inverse transform if needed)
- Estimated height (in meters)

---

### 3.9 Stage 9: Export

**Goal:** Save mesh in multiple formats + metadata.

**Code:**
```python
class MeshExporter:
    def export_fbx(self, mesh: o3d.geometry.TriangleMesh, filepath: str):
        """Export to FBX (for Blender)."""
        o3d.io.write_triangle_mesh(filepath, mesh)
        print(f"Saved FBX: {filepath}")
    
    def export_glb(self, mesh: o3d.geometry.TriangleMesh, filepath: str):
        """Export to glTF/glB (for web viewer)."""
        o3d.io.write_triangle_mesh(filepath, mesh)
        print(f"Saved glB: {filepath}")
    
    def export_metadata(self, 
                        mesh: o3d.geometry.TriangleMesh,
                        scan_id: str,
                        height: float,
                        segmentation: dict,
                        filepath: str):
        """Export metadata JSON."""
        
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        
        # Compute bounding box
        bbox = mesh.get_axis_aligned_bounding_box()
        
        metadata = {
            "scan_id": scan_id,
            "timestamp": "2026-03-17T10:30:00Z",
            "device": "iPhone 14 Pro",
            "mesh": {
                "vertices": len(vertices),
                "triangles": len(triangles),
                "estimated_height": float(height),
                "bounding_box": {
                    "min": bbox.get_min_bound().tolist(),
                    "max": bbox.get_max_bound().tolist(),
                }
            },
            "segmentation": segmentation,
            "quality": {
                "reconstruction_error_mm": 4.5,  # Placeholder
                "point_cloud_size": 500000,
                "confidence_score": 0.92  # 0–1
            }
        }
        
        with open(filepath, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Saved metadata: {filepath}")

# Usage
exporter = MeshExporter()
exporter.export_fbx(mesh, "body_scan.fbx")
exporter.export_glb(mesh, "body_scan.glb")
exporter.export_metadata(mesh, "scan_123", height, seg_result, "scan_metadata.json")
```

---

## 4. Full Pipeline (End-to-End)

**Orchestration Code:**

```python
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScanProcessingPipeline:
    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        
        self.cleaner = PointCloudCleaner(self.config["cleaning"])
        self.downsampler = PointCloudDownsampler(self.config["voxel_size"])
        self.estimator = NormalEstimator()
        self.generator = MeshGenerator(self.config["mesh_generation"])
        self.mesh_cleaner = MeshCleaner()
        self.segmenter = BodySegmenter()
        self.enforcer = SymmetryEnforcer()
        self.normalizer = PoseNormalizer()
        self.exporter = MeshExporter()
    
    @staticmethod
    def _default_config():
        return {
            "cleaning": {"outlier_nb_neighbors": 20, "outlier_std_ratio": 2.0},
            "voxel_size": 0.01,
            "mesh_generation": {"depth": 9, "width": 0},
        }
    
    def process(self, 
                input_ply: str, 
                scan_id: str,
                output_dir: str = ".") -> dict:
        """
        Full point cloud → mesh pipeline.
        
        Args:
            input_ply: Path to input .ply file
            scan_id: Scan identifier
            output_dir: Output directory for results
        
        Returns:
            {
                "fbx_path": "...",
                "glb_path": "...",
                "metadata_path": "...",
                "height": 1.75,
                "quality_score": 0.92
            }
        """
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[{scan_id}] Starting pipeline...")
        
        # Load
        logger.info(f"[{scan_id}] Loading point cloud: {input_ply}")
        pcd = o3d.io.read_point_cloud(input_ply)
        logger.info(f"  Input: {len(pcd.points)} points")
        
        # Stage 1: Clean
        logger.info(f"[{scan_id}] Stage 1: Noise removal...")
        pcd = self.cleaner.clean(pcd)
        
        # Stage 2: Downsample
        logger.info(f"[{scan_id}] Stage 2: Downsampling...")
        pcd = self.downsampler.downsample(pcd)
        
        # Stage 3: Estimate normals
        logger.info(f"[{scan_id}] Stage 3: Normal estimation...")
        pcd = self.estimator.estimate(pcd)
        
        # Stage 4: Generate mesh
        logger.info(f"[{scan_id}] Stage 4: Mesh generation (Poisson)...")
        mesh = self.generator.generate_poisson(pcd)
        
        # Stage 5: Clean mesh
        logger.info(f"[{scan_id}] Stage 5: Mesh cleanup...")
        mesh = self.mesh_cleaner.clean(mesh)
        
        # Stage 6: Segment
        logger.info(f"[{scan_id}] Stage 6: Body segmentation...")
        seg_result = self.segmenter.segment(mesh)
        
        # Stage 7: Enforce symmetry
        logger.info(f"[{scan_id}] Stage 7: Symmetry enforcement...")
        mesh = self.enforcer.enforce_bilateral(mesh)
        
        # Stage 8: Normalize pose
        logger.info(f"[{scan_id}] Stage 8: Pose normalization...")
        mesh, transform, height = self.normalizer.normalize(mesh)
        
        # Stage 9: Export
        logger.info(f"[{scan_id}] Stage 9: Exporting...")
        fbx_path = output_dir / f"{scan_id}.fbx"
        glb_path = output_dir / f"{scan_id}.glb"
        metadata_path = output_dir / f"{scan_id}_metadata.json"
        
        self.exporter.export_fbx(mesh, str(fbx_path))
        self.exporter.export_glb(mesh, str(glb_path))
        self.exporter.export_metadata(mesh, scan_id, height, seg_result, str(metadata_path))
        
        logger.info(f"[{scan_id}] ✅ Pipeline complete!")
        
        return {
            "fbx_path": str(fbx_path),
            "glb_path": str(glb_path),
            "metadata_path": str(metadata_path),
            "height": float(height),
            "quality_score": 0.92,  # Placeholder
        }

# Usage
if __name__ == "__main__":
    pipeline = ScanProcessingPipeline()
    
    result = pipeline.process(
        input_ply="scan.ply",
        scan_id="user_123_scan_001",
        output_dir="./output"
    )
    
    print(f"Results:\n{result}")
```

---

## 5. Backend Integration (FastAPI)

**API Server:**

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio

app = FastAPI()

class ProcessRequest(BaseModel):
    scan_id: str
    s3_key: str  # S3 path to uploaded .ply

class ProcessingStatus(BaseModel):
    scan_id: str
    status: str  # "processing", "completed", "failed"
    current_step: str
    progress: float  # 0.0 to 1.0
    result_paths: dict = None

# In-memory job tracking (use Redis in production)
jobs = {}

@app.post("/api/v1/scans/process")
async def process_scan(req: ProcessRequest, bg_tasks: BackgroundTasks):
    """Start processing a scan."""
    
    scan_id = req.scan_id
    s3_key = req.s3_key
    
    # Mark as processing
    jobs[scan_id] = {
        "status": "processing",
        "current_step": "downloading",
        "progress": 0.0
    }
    
    # Queue background task
    bg_tasks.add_task(run_pipeline, scan_id, s3_key)
    
    return {"job_id": scan_id, "status": "processing"}

@app.get("/api/v1/scans/{scan_id}/status")
async def check_status(scan_id: str):
    """Check processing status."""
    
    job = jobs.get(scan_id)
    
    if not job:
        return {"error": "Scan not found"}
    
    return ProcessingStatus(**job)

async def run_pipeline(scan_id: str, s3_key: str):
    """Background task: run full pipeline."""
    
    try:
        # Download from S3
        jobs[scan_id]["current_step"] = "downloading"
        pcd_path = download_from_s3(s3_key)
        jobs[scan_id]["progress"] = 0.1
        
        # Process
        jobs[scan_id]["current_step"] = "processing"
        pipeline = ScanProcessingPipeline()
        result = pipeline.process(pcd_path, scan_id)
        jobs[scan_id]["progress"] = 0.9
        
        # Upload results to S3
        jobs[scan_id]["current_step"] = "uploading"
        fbx_url = upload_to_s3(result["fbx_path"])
        glb_url = upload_to_s3(result["glb_path"])
        jobs[scan_id]["progress"] = 1.0
        
        # Mark complete
        jobs[scan_id].update({
            "status": "completed",
            "current_step": "done",
            "progress": 1.0,
            "result_paths": {
                "fbx": fbx_url,
                "glb": glb_url,
                "height": result["height"]
            }
        })
        
    except Exception as e:
        jobs[scan_id].update({
            "status": "failed",
            "error": str(e)
        })
```

---

## 6. Testing & Validation

### 6.1 Unit Tests

```python
import pytest
import numpy as np

def test_point_cloud_cleaning():
    # Create synthetic noisy point cloud
    pcd = o3d.geometry.PointCloud()
    points = np.random.randn(10000, 3)
    pcd.points = o3d.utility.Vector3dVector(points)
    
    cleaner = PointCloudCleaner()
    pcd_clean = cleaner.clean(pcd)
    
    # Should have fewer points after cleaning
    assert len(pcd_clean.points) < len(pcd.points)
    assert len(pcd_clean.points) > 1000  # Should not remove everything

def test_mesh_generation():
    # Create synthetic point cloud from sphere
    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere()
    pcd = mesh_sphere.sample_points_poisson_disk(5000)
    pcd.estimate_normals()
    
    generator = MeshGenerator()
    mesh = generator.generate_poisson(pcd)
    
    # Check mesh is valid
    assert mesh.is_edge_manifold()
    assert len(mesh.vertices) > 1000

def test_segmentation():
    mesh = create_synthetic_body_mesh()
    segmenter = BodySegmenter()
    seg_result = segmenter.segment(mesh)
    
    # Check all body parts are represented
    labels = seg_result["labels"].values()
    assert "head" in labels
    assert "torso" in labels
    assert "left_leg" in labels
```

### 6.2 Integration Tests

```python
def test_full_pipeline():
    """End-to-end pipeline test."""
    
    # Create synthetic body point cloud
    pcd = create_synthetic_body_point_cloud()
    pcd.write_ply("test_input.ply")
    
    # Run pipeline
    pipeline = ScanProcessingPipeline()
    result = pipeline.process("test_input.ply", "test_scan", "./test_output")
    
    # Verify outputs exist
    assert Path(result["fbx_path"]).exists()
    assert Path(result["glb_path"]).exists()
    assert Path(result["metadata_path"]).exists()
    
    # Verify mesh quality
    mesh = o3d.io.read_triangle_mesh(result["fbx_path"])
    assert mesh.is_edge_manifold()
    assert len(mesh.vertices) > 1000
```

---

## 7. Performance Benchmarks (Target)

| Stage | Time | Input | Output |
|-------|------|-------|--------|
| Cleaning | 5–10s | 1–5M pts | 500k–1M pts |
| Downsampling | 2–5s | 500k pts | 100k–200k pts |
| Normal Estimation | 5–10s | 200k pts | 200k pts (with normals) |
| Mesh Generation | 20–40s | 200k pts | 100k–200k tri |
| Segmentation | 2–5s | mesh | labels |
| Symmetry | 5–10s | mesh | mesh |
| Normalization | 2–3s | mesh | mesh |
| Export | 3–5s | mesh | .fbx + .glb + .json |
| **Total** | **45–90s** | 1–5M pts | FBX + glTF + JSON |

---

## 8. Roadmap

### Week 2: Core Pipeline
- [ ] Implement Stages 1–4 (cleaning, downsampling, normals, mesh)
- [ ] Test on synthetic data
- [ ] Benchmark performance

### Week 3: Body Segmentation & Normalization
- [ ] Implement Stages 6–8 (segmentation, symmetry, normalization)
- [ ] Test on real LiDAR scans
- [ ] Validate reconstruction error (<5mm)

### Week 4: Export & Integration
- [ ] Implement Stage 9 (export FBX/glTF)
- [ ] API server (FastAPI)
- [ ] Integration with Blender Lead

---

**Version:** 1.0  
**Last Updated:** 2026-03-17
