#!/usr/bin/env python3
"""
process_scan.py — Open3D body scan cleanup pipeline
Sprint 1 · fashion-scanning · 2026-03-18

Inputs:  <scan_file>.ply
Outputs: <output_dir>/<scan_id>.obj
         <output_dir>/measurements.json

Pipeline:
  1. Load .ply point cloud
  2. Remove statistical outliers (noise removal)
  3. Voxel downsample
  4. Estimate normals
  5. Poisson surface reconstruction → triangle mesh
  6. Crop mesh to body bounding box, remove non-manifold artefacts
  7. Export .obj
  8. Extract body measurements (chest, waist, hip, inseam, height) via AABB slices
  9. Write measurements.json

Usage:
  python process_scan.py input.ply [--out-dir ./output] [--scan-id auto]

Dependencies:
  pip install open3d numpy
"""

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    import open3d as o3d
except ImportError:
    raise ImportError("open3d is required: pip install open3d")


# ---------------------------------------------------------------------------
# Constants / tunables
# ---------------------------------------------------------------------------

VOXEL_SIZE = 0.005          # 5 mm — good balance for body scans
OUTLIER_NB_NEIGHBORS = 30   # statistical outlier removal neighbours
OUTLIER_STD_RATIO = 2.0     # std-dev multiplier for outlier removal
POISSON_DEPTH = 9           # Poisson reconstruction octree depth (8-10 for bodies)
POISSON_DENSITY_QUANTILE = 0.02  # remove lowest-density vertices after reconstruction

# Anatomical landmark height fractions (relative to total height, feet=0, head=1)
# These are approximate mid-body averages; per-subject calibration improves accuracy.
CHEST_HEIGHT_FRAC   = 0.78
WAIST_HEIGHT_FRAC   = 0.62
HIP_HEIGHT_FRAC     = 0.52
INSEAM_HEIGHT_FRAC  = 0.47   # crotch-to-floor fraction for inseam estimate

# Slice half-thickness in metres (used when sampling circumference at a height)
SLICE_HALF_HEIGHT = 0.025   # ±2.5 cm band around each landmark height


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pointcloud(path: str) -> "o3d.geometry.PointCloud":
    pcd = o3d.io.read_point_cloud(path)
    if len(pcd.points) == 0:
        raise ValueError(f"No points loaded from {path}")
    print(f"  Loaded {len(pcd.points):,} points from {path}")
    return pcd


def denoise(pcd: "o3d.geometry.PointCloud") -> "o3d.geometry.PointCloud":
    """Remove statistical outliers."""
    cl, ind = pcd.remove_statistical_outlier(
        nb_neighbors=OUTLIER_NB_NEIGHBORS,
        std_ratio=OUTLIER_STD_RATIO
    )
    print(f"  Denoised: {len(pcd.points):,} → {len(cl.points):,} points")
    return cl


def downsample(pcd: "o3d.geometry.PointCloud") -> "o3d.geometry.PointCloud":
    """Voxel downsample to uniform density."""
    ds = pcd.voxel_down_sample(voxel_size=VOXEL_SIZE)
    print(f"  Downsampled: → {len(ds.points):,} points  (voxel={VOXEL_SIZE} m)")
    return ds


def estimate_normals(pcd: "o3d.geometry.PointCloud") -> "o3d.geometry.PointCloud":
    """Estimate surface normals, orient toward camera origin."""
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.02, max_nn=30)
    )
    pcd.orient_normals_consistent_tangent_plane(k=20)
    return pcd


def reconstruct_mesh(pcd: "o3d.geometry.PointCloud") -> "o3d.geometry.TriangleMesh":
    """Poisson surface reconstruction with density-based trimming."""
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=POISSON_DEPTH, n_threads=-1
    )
    # Remove low-density artefacts (flying triangles at scan boundaries)
    densities_np = np.asarray(densities)
    threshold = np.quantile(densities_np, POISSON_DENSITY_QUANTILE)
    keep = densities_np > threshold
    mesh.remove_vertices_by_mask(~keep)
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()
    mesh.compute_vertex_normals()
    print(f"  Mesh: {len(mesh.vertices):,} vertices, {len(mesh.triangles):,} triangles")
    return mesh


def export_obj(mesh: "o3d.geometry.TriangleMesh", out_path: str) -> None:
    """Write triangle mesh to .obj."""
    success = o3d.io.write_triangle_mesh(out_path, mesh, write_ascii=False)
    if not success:
        raise IOError(f"Failed to write mesh to {out_path}")
    print(f"  Wrote .obj → {out_path}")


# ---------------------------------------------------------------------------
# Measurement extraction
# ---------------------------------------------------------------------------

def _slice_points_at_height(pts: np.ndarray, y_centre: float, half_h: float) -> np.ndarray:
    """
    Return XZ coordinates of all points within ±half_h of y_centre.
    Assumes Y is the up-axis (ARKit world coordinate convention).
    """
    mask = np.abs(pts[:, 1] - y_centre) <= half_h
    return pts[mask][:, [0, 2]]   # XZ slice


def _circumference_from_slice(xz: np.ndarray) -> float:
    """
    Approximate circumference (metres) of a horizontal cross-section.
    Strategy: convex hull perimeter of the XZ point slice.
    Returns 0.0 if the slice has fewer than 3 points.
    """
    if len(xz) < 3:
        return 0.0
    from scipy.spatial import ConvexHull  # type: ignore
    try:
        hull = ConvexHull(xz)
        # Compute perimeter of hull
        pts_hull = xz[hull.vertices]
        closed = np.vstack([pts_hull, pts_hull[0]])
        perimeter = float(np.sum(np.linalg.norm(np.diff(closed, axis=0), axis=1)))
        return perimeter
    except Exception:
        # Degenerate hull — return bounding box perimeter as fallback
        span = xz.max(axis=0) - xz.min(axis=0)
        return float(2 * (span[0] + span[1]))


def extract_measurements(mesh: "o3d.geometry.TriangleMesh", scan_id: str) -> dict:
    """
    Extract body measurements from the mesh using horizontal slice circumferences.

    Coordinate system: ARKit world — Y is up.

    The body bounding box defines total height; anatomical height fractions (constants
    at top of file) locate each circumference measurement.

    Returns a dict matching the measurements.json schema.
    """
    pts = np.asarray(mesh.vertices)

    y_min = float(pts[:, 1].min())
    y_max = float(pts[:, 1].max())
    height_m = y_max - y_min

    def y_at_frac(frac: float) -> float:
        return y_min + frac * height_m

    chest_circ_m  = _circumference_from_slice(pts, y_at_frac(CHEST_HEIGHT_FRAC),  SLICE_HALF_HEIGHT)
    waist_circ_m  = _circumference_from_slice(pts, y_at_frac(WAIST_HEIGHT_FRAC),  SLICE_HALF_HEIGHT)
    hip_circ_m    = _circumference_from_slice(pts, y_at_frac(HIP_HEIGHT_FRAC),    SLICE_HALF_HEIGHT)

    # Inseam: floor to crotch height (INSEAM_HEIGHT_FRAC of total height)
    inseam_m = height_m * INSEAM_HEIGHT_FRAC

    def m_to_cm(v: float) -> float:
        return round(v * 100, 1)

    measurements = {
        "chest_cm":   m_to_cm(chest_circ_m),
        "waist_cm":   m_to_cm(waist_circ_m),
        "hip_cm":     m_to_cm(hip_circ_m),
        "inseam_cm":  m_to_cm(inseam_m),
        "height_cm":  m_to_cm(height_m),
        "scan_id":    scan_id,
        "timestamp":  datetime.now(timezone.utc).isoformat()
    }

    print(f"  Measurements: height={measurements['height_cm']} cm, "
          f"chest={measurements['chest_cm']} cm, "
          f"waist={measurements['waist_cm']} cm, "
          f"hip={measurements['hip_cm']} cm, "
          f"inseam={measurements['inseam_cm']} cm")

    return measurements


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def process_scan(ply_path: str, out_dir: str, scan_id: str) -> dict:
    """
    Full pipeline: .ply → .obj + measurements.json
    Returns the measurements dict.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n[1/6] Loading point cloud…")
    pcd = load_pointcloud(ply_path)

    print(f"[2/6] Denoising…")
    pcd = denoise(pcd)

    print(f"[3/6] Downsampling…")
    pcd = downsample(pcd)

    print(f"[4/6] Estimating normals…")
    pcd = estimate_normals(pcd)

    print(f"[5/6] Poisson reconstruction…")
    mesh = reconstruct_mesh(pcd)

    obj_path = str(Path(out_dir) / f"{scan_id}.obj")
    print(f"[6a/6] Exporting .obj…")
    export_obj(mesh, obj_path)

    print(f"[6b/6] Extracting measurements…")
    measurements = extract_measurements(mesh, scan_id)

    json_path = str(Path(out_dir) / "measurements.json")
    with open(json_path, "w") as f:
        json.dump(measurements, f, indent=2)
    print(f"  Wrote measurements.json → {json_path}")

    return measurements


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Process a LiDAR body scan .ply → .obj + measurements.json"
    )
    parser.add_argument("ply_path", help="Input .ply point cloud file")
    parser.add_argument("--out-dir", default="./output",
                        help="Output directory (default: ./output)")
    parser.add_argument("--scan-id", default=None,
                        help="Scan identifier (default: auto UUID)")
    args = parser.parse_args()

    if not os.path.isfile(args.ply_path):
        raise FileNotFoundError(f"Input file not found: {args.ply_path}")

    scan_id = args.scan_id or str(uuid.uuid4())
    print(f"scan_id: {scan_id}")

    measurements = process_scan(args.ply_path, args.out_dir, scan_id)
    print(f"\nDone. Outputs in {args.out_dir}/")
    return measurements


if __name__ == "__main__":
    main()
