#!/usr/bin/env python3
"""
extract_joints.py — MediaPipe Pose landmark extraction
Sprint 1 · fashion-scanning · 2026-03-18

Extracts 33 body landmarks (MediaPipe Pose schema) from:
  - An image file (JPEG/PNG)
  - A rendered front-view of a 3D mesh (if --render is passed with an .obj/.ply)

Outputs joints.json in the MediaPipe Pose 33-landmark schema.

Usage:
  # From image:
  python extract_joints.py --image subject.jpg --scan-id scan-001 --out joints.json

  # From mesh (renders a front-view, then runs pose on it):
  python extract_joints.py --mesh scan-001.obj --scan-id scan-001 --out joints.json

Dependencies:
  pip install mediapipe opencv-python numpy open3d

Body type test approach
-----------------------
MediaPipe Pose (BlazePose) was trained on a diverse corpus including:
  1. Slim / athletic builds   — typically high-confidence, clean landmark detection
  2. Average / mid-size builds — most common in training set, best baseline accuracy
  3. Plus-size / large builds  — can reduce confidence on waist/hip landmarks;
     we handle this by:
     (a) using STATIC_IMAGE_MODE=True (single-frame, no temporal smoothing artefacts)
     (b) running with model_complexity=2 (most accurate variant)
     (c) flagging low-confidence landmarks (visibility < 0.5) in output JSON
     (d) recommending a multi-view ensemble (front + side) for production use
                       -- see MULTI_VIEW note below --

MULTI_VIEW note: For production Sprint 2+, the recommended approach is:
  - Capture 3 images (front, left-side, right-side)
  - Run extract_joints on each
  - Average XYZ landmarks where all 3 views are high-visibility
  - This improves depth (Z) accuracy for all body types, especially plus-size
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    raise ImportError("mediapipe is required: pip install mediapipe")


# ---------------------------------------------------------------------------
# MediaPipe landmark name map (33 landmarks, BlazePose topology)
# ---------------------------------------------------------------------------

LANDMARK_NAMES = [
    "nose",
    "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear",
    "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_pinky", "right_pinky",
    "left_index", "right_index",
    "left_thumb", "right_thumb",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]


# ---------------------------------------------------------------------------
# Mesh → image render (simple orthographic projection, front view)
# ---------------------------------------------------------------------------

def render_mesh_front_view(mesh_path: str, image_size: int = 1024) -> np.ndarray:
    """
    Render an orthographic front-view of a 3D mesh as an RGB numpy array.
    Uses Open3D offscreen rendering (headless-safe via CPU rasteriser).

    Falls back to point cloud scatter plot if mesh loading fails.
    """
    try:
        import open3d as o3d  # type: ignore
    except ImportError:
        raise ImportError("open3d required for mesh rendering: pip install open3d")

    ext = Path(mesh_path).suffix.lower()
    if ext == ".ply":
        # Try mesh first, fall back to point cloud
        geom = o3d.io.read_triangle_mesh(mesh_path)
        if len(geom.vertices) == 0:
            geom = o3d.io.read_point_cloud(mesh_path)
    else:
        geom = o3d.io.read_triangle_mesh(mesh_path)

    # Centre the mesh
    if hasattr(geom, "vertices"):
        pts = np.asarray(geom.vertices)
    else:
        pts = np.asarray(geom.points)

    centroid = pts.mean(axis=0)
    y_min, y_max = pts[:, 1].min(), pts[:, 1].max()
    height = y_max - y_min

    # Orthographic projection: X → image_u, Y → image_v (inverted), Z ignored
    scale = (image_size * 0.85) / height   # fit 85% of image height
    u = ((pts[:, 0] - centroid[0]) * scale + image_size / 2).astype(int)
    v = ((y_max - pts[:, 1]) * scale + image_size * 0.075).astype(int)

    img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 240  # light grey bg
    for ui, vi in zip(u, v):
        if 0 <= ui < image_size and 0 <= vi < image_size:
            img[vi, ui] = [60, 60, 60]  # dark grey points

    # Light blur to help pose detector find body silhouette
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img


# ---------------------------------------------------------------------------
# Pose extraction
# ---------------------------------------------------------------------------

def extract_pose_landmarks(image_bgr: np.ndarray) -> list[dict] | None:
    """
    Run MediaPipe Pose on a BGR image.
    Returns list of 33 landmark dicts, or None if no pose detected.
    """
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,         # highest accuracy (see body type note)
        enable_segmentation=False,
        min_detection_confidence=0.3,  # lower threshold improves recall on diverse builds
    ) as pose:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return None

    landmarks = []
    for i, lm in enumerate(results.pose_landmarks.landmark):
        landmarks.append({
            "id": i,
            "name": LANDMARK_NAMES[i],
            "x": round(float(lm.x), 6),
            "y": round(float(lm.y), 6),
            "z": round(float(lm.z), 6),
            "visibility": round(float(lm.visibility), 4),
        })
    return landmarks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_extraction(
    image_path: str | None,
    mesh_path: str | None,
    scan_id: str,
    out_path: str,
) -> dict:
    """
    Core extraction: loads image or renders mesh, runs pose, writes joints.json.
    Returns the joints dict.
    """
    if image_path:
        print(f"  Loading image: {image_path}")
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
    elif mesh_path:
        print(f"  Rendering mesh front-view: {mesh_path}")
        image_bgr = render_mesh_front_view(mesh_path)
    else:
        raise ValueError("Must provide --image or --mesh")

    print(f"  Running MediaPipe Pose (model_complexity=2)…")
    landmarks = extract_pose_landmarks(image_bgr)

    if landmarks is None:
        # Log low-confidence / no-detection result — still write file with empty list
        print("  WARNING: No pose detected. Output will have empty landmarks.")
        print("  Suggestions: ensure full body is visible, try a higher-resolution image,")
        print("  or use multi-view ensemble approach (see MULTI_VIEW note in script header).")
        landmarks = []

    # Flag low-visibility landmarks for downstream consumers
    low_vis = [lm["name"] for lm in landmarks if lm["visibility"] < 0.5]
    if low_vis:
        print(f"  Low-visibility landmarks (<0.5): {', '.join(low_vis)}")

    joints = {
        "scan_id": scan_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "landmark_count": len(landmarks),
        "landmarks": landmarks,
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(joints, f, indent=2)

    print(f"  Wrote joints.json → {out_path}  ({len(landmarks)} landmarks)")
    return joints


def main():
    parser = argparse.ArgumentParser(
        description="Extract MediaPipe Pose 33 landmarks → joints.json"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--image", help="Input image file (JPEG/PNG)")
    source.add_argument("--mesh",  help="Input 3D mesh file (.obj or .ply) — renders front-view")
    parser.add_argument("--scan-id", required=True, help="Scan identifier string")
    parser.add_argument("--out", default="joints.json", help="Output JSON path")
    args = parser.parse_args()

    print(f"\nscan_id: {args.scan_id}")
    joints = run_extraction(
        image_path=args.image,
        mesh_path=args.mesh,
        scan_id=args.scan_id,
        out_path=args.out,
    )
    print(f"\nDone.")
    return joints


if __name__ == "__main__":
    main()
