"""
joint_detector.py
Week 2 — MediaPipe-based joint detection from body scan .ply files.

Approach:
1. Project the 3D point cloud onto a 2D front-view image
2. Run MediaPipe Pose on the 2D projection
3. Back-project 2D landmarks to 3D using the point cloud depth
4. Output joints.json with 3D positions + confidence scores
"""

import json
import os
import sys
import time
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import cv2

# MediaPipe import with graceful fallback
MEDIAPIPE_AVAILABLE = False
mp = None
try:
    import mediapipe as mp
    # MediaPipe 0.10+ uses tasks API; check for legacy solutions.pose
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'pose'):
        MEDIAPIPE_AVAILABLE = True
        print("MediaPipe: legacy solutions.pose API available")
    else:
        # Try new tasks API
        try:
            from mediapipe.tasks import python as mp_tasks
            from mediapipe.tasks.python import vision as mp_vision
            MEDIAPIPE_AVAILABLE = False  # Tasks API needs model file download
            print("MediaPipe: tasks API available but needs model file — using heuristic")
        except Exception:
            pass
        print("WARNING: mediapipe solutions.pose not available — using heuristic joint placement")
except ImportError:
    print("WARNING: mediapipe not installed — using heuristic joint placement")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# Mediapipe pose landmark indices
MP_LANDMARKS = {
    "nose": 0,
    "left_eye": 1,
    "right_eye": 2,
    "left_ear": 3,
    "right_ear": 4,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}

# Joints we care about for rigging
RIG_JOINTS = [
    "head", "neck", "spine_mid", "hips",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
]


def load_ply(filepath: str) -> np.ndarray:
    """Load ASCII PLY, return (N, 6) array [x, y, z, r, g, b]."""
    points = []
    in_header = True
    expected_cols = None

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if in_header:
                if line.startswith("element vertex"):
                    n_verts = int(line.split()[-1])
                if line == "end_header":
                    in_header = False
            else:
                vals = line.split()
                if vals:
                    points.append([float(v) for v in vals[:6]])

    arr = np.array(points, dtype=np.float32)
    logger.info(f"Loaded {len(arr)} points from {os.path.basename(filepath)}")
    return arr


def project_to_image(
    points: np.ndarray,
    img_size: int = 512,
) -> Tuple[np.ndarray, Dict]:
    """
    Project 3D point cloud to 2D front-view (XY plane) image.
    Returns image (H, W, 3) + projection metadata for back-projection.
    """
    xyz = points[:, :3]
    rgb = points[:, 3:6].astype(np.uint8)

    # Front view: X → image_x, Y → image_y (flip Y for image coords)
    x = xyz[:, 0]
    y = xyz[:, 1]

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    margin = 0.05
    x_range = (x_max - x_min) * (1 + margin)
    y_range = (y_max - y_min) * (1 + margin)

    scale = img_size / max(x_range, y_range)
    x_off = (img_size - x_range * scale) / 2 - x_min * scale
    y_off = (img_size - y_range * scale) / 2 - y_min * scale

    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)

    px = (x * scale + x_off).astype(int)
    py = (img_size - 1 - (y * scale + y_off)).astype(int)

    mask = (px >= 0) & (px < img_size) & (py >= 0) & (py < img_size)
    img[py[mask], px[mask]] = rgb[mask]

    meta = {
        "scale": scale,
        "x_off": x_off,
        "y_off": y_off,
        "img_size": img_size,
        "y_min": float(y_min),
        "y_max": float(y_max),
        "x_min": float(x_min),
        "x_max": float(x_max),
    }
    return img, meta


def backproject_landmark(
    norm_x: float,
    norm_y: float,
    meta: Dict,
    points: np.ndarray,
    radius_m: float = 0.05,
) -> Tuple[Optional[np.ndarray], float]:
    """
    Back-project a 2D MediaPipe normalized landmark to 3D.
    Finds closest points in the point cloud to the projected location.
    Returns (xyz_3d, depth_confidence).
    """
    img_size = meta["img_size"]
    scale = meta["scale"]
    x_off = meta["x_off"]
    y_off = meta["y_off"]

    px = norm_x * img_size
    py = norm_y * img_size

    # Image coords → world
    world_x = (px - x_off) / scale
    world_y = ((img_size - 1 - py) - y_off) / scale

    xyz = points[:, :3]
    dx = xyz[:, 0] - world_x
    dy = xyz[:, 1] - world_y
    dist_2d = np.sqrt(dx**2 + dy**2)

    close_mask = dist_2d < radius_m
    if not close_mask.any():
        # Expand search
        close_mask = dist_2d < radius_m * 3
    if not close_mask.any():
        return None, 0.0

    nearby = xyz[close_mask]
    center = nearby.mean(axis=0)
    confidence = min(1.0, close_mask.sum() / 50.0)
    return center, confidence


def detect_joints_mediapipe(
    points: np.ndarray,
    scan_id: str,
) -> Dict:
    """
    Run MediaPipe Pose on projected image, back-project to 3D.
    Returns joints dict with 3D positions and confidence scores.
    """
    img, meta = project_to_image(points, img_size=512)

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.3,
    ) as pose:
        # MediaPipe expects BGR
        img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        results = pose.process(img_rgb)

    joints = {}
    mp_confidences = {}

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        # Map MediaPipe landmarks to 3D
        for name, idx in MP_LANDMARKS.items():
            lmk = lm[idx]
            xyz, conf = backproject_landmark(
                lmk.x, lmk.y, meta, points
            )
            vis = lmk.visibility
            if xyz is not None:
                joints[name] = {
                    "x": float(xyz[0]),
                    "y": float(xyz[1]),
                    "z": float(xyz[2]),
                }
                mp_confidences[name] = {
                    "visibility": float(vis),
                    "depth_confidence": float(conf),
                    "combined": float(vis * conf),
                }

        # Derive composite joints
        if "left_shoulder" in joints and "right_shoulder" in joints:
            ls = np.array([joints["left_shoulder"]["x"],
                           joints["left_shoulder"]["y"],
                           joints["left_shoulder"]["z"]])
            rs = np.array([joints["right_shoulder"]["x"],
                           joints["right_shoulder"]["y"],
                           joints["right_shoulder"]["z"]])
            neck = (ls + rs) / 2 + np.array([0, 0.05, 0])
            joints["neck"] = {"x": float(neck[0]), "y": float(neck[1]), "z": float(neck[2])}
            mp_confidences["neck"] = {"visibility": 0.9, "depth_confidence": 0.9, "combined": 0.81}

        if "left_hip" in joints and "right_hip" in joints:
            lh = np.array([joints["left_hip"]["x"],
                           joints["left_hip"]["y"],
                           joints["left_hip"]["z"]])
            rh = np.array([joints["right_hip"]["x"],
                           joints["right_hip"]["y"],
                           joints["right_hip"]["z"]])
            hips = (lh + rh) / 2
            spine_mid = hips + np.array([0, 0.25, 0])
            joints["hips"] = {"x": float(hips[0]), "y": float(hips[1]), "z": float(hips[2])}
            joints["spine_mid"] = {"x": float(spine_mid[0]), "y": float(spine_mid[1]), "z": float(spine_mid[2])}
            mp_confidences["hips"] = {"visibility": 0.9, "depth_confidence": 0.85, "combined": 0.765}
            mp_confidences["spine_mid"] = {"visibility": 0.85, "depth_confidence": 0.80, "combined": 0.68}

        # Head from nose
        if "nose" in joints:
            nose = joints["nose"]
            joints["head"] = {
                "x": nose["x"],
                "y": nose["y"] + 0.08,
                "z": nose["z"],
            }
            mp_confidences["head"] = {"visibility": 0.95, "depth_confidence": 0.80, "combined": 0.76}

        logger.info(f"  MediaPipe: {len(joints)} joints detected")
    else:
        logger.warning("  MediaPipe: no pose detected — falling back to heuristic")
        joints, mp_confidences = heuristic_joints(points)

    return {
        "scan_id": scan_id,
        "method": "mediapipe" if results.pose_landmarks else "heuristic",
        "joints": joints,
        "confidence": mp_confidences,
        "n_joints": len(joints),
    }


def heuristic_joints(points: np.ndarray) -> Tuple[Dict, Dict]:
    """
    Fallback: compute joints from point cloud statistics.
    Uses body proportion heuristics when MediaPipe fails.
    """
    xyz = points[:, :3]
    y_min, y_max = xyz[:, 1].min(), xyz[:, 1].max()
    height = y_max - y_min

    x_center = float(xyz[:, 0].mean())
    z_center = float(xyz[:, 2].mean())

    def pt(x_frac, y_frac, z_frac=0.0):
        return {
            "x": x_center + x_frac * 0.2,
            "y": float(y_min + y_frac * height),
            "z": z_center + z_frac * 0.05,
        }

    # Estimate shoulder width from top 15% of points
    top_mask = xyz[:, 1] > (y_min + 0.78 * height)
    shoulder_pts = xyz[top_mask]
    sw = float(shoulder_pts[:, 0].std()) * 2.5 if len(shoulder_pts) > 10 else 0.21

    joints = {
        "head":           {"x": x_center, "y": float(y_min + 0.95 * height), "z": z_center},
        "neck":           {"x": x_center, "y": float(y_min + 0.88 * height), "z": z_center},
        "left_shoulder":  {"x": x_center - sw, "y": float(y_min + 0.83 * height), "z": z_center},
        "right_shoulder": {"x": x_center + sw, "y": float(y_min + 0.83 * height), "z": z_center},
        "left_elbow":     {"x": x_center - sw * 1.4, "y": float(y_min + 0.65 * height), "z": z_center},
        "right_elbow":    {"x": x_center + sw * 1.4, "y": float(y_min + 0.65 * height), "z": z_center},
        "left_wrist":     {"x": x_center - sw * 1.55, "y": float(y_min + 0.46 * height), "z": z_center},
        "right_wrist":    {"x": x_center + sw * 1.55, "y": float(y_min + 0.46 * height), "z": z_center},
        "spine_mid":      {"x": x_center, "y": float(y_min + 0.68 * height), "z": z_center},
        "hips":           {"x": x_center, "y": float(y_min + 0.52 * height), "z": z_center},
        "left_hip":       {"x": x_center - sw * 0.7, "y": float(y_min + 0.52 * height), "z": z_center},
        "right_hip":      {"x": x_center + sw * 0.7, "y": float(y_min + 0.52 * height), "z": z_center},
        "left_knee":      {"x": x_center - sw * 0.7, "y": float(y_min + 0.26 * height), "z": z_center},
        "right_knee":     {"x": x_center + sw * 0.7, "y": float(y_min + 0.26 * height), "z": z_center},
        "left_ankle":     {"x": x_center - sw * 0.7, "y": float(y_min + 0.03 * height), "z": z_center},
        "right_ankle":    {"x": x_center + sw * 0.7, "y": float(y_min + 0.03 * height), "z": z_center},
    }
    confidences = {j: {"visibility": 0.5, "depth_confidence": 0.6, "combined": 0.30}
                   for j in joints}
    return joints, confidences


def process_scan(ply_path: str, output_dir: str) -> Dict:
    """Process a single .ply file: detect joints, write joints.json."""
    scan_id = os.path.splitext(os.path.basename(ply_path))[0]
    logger.info(f"\nProcessing: {scan_id}")

    t0 = time.time()
    points = load_ply(ply_path)

    if MEDIAPIPE_AVAILABLE:
        result = detect_joints_mediapipe(points, scan_id)
    else:
        joints, confidences = heuristic_joints(points)
        result = {
            "scan_id": scan_id,
            "method": "heuristic",
            "joints": joints,
            "confidence": confidences,
            "n_joints": len(joints),
        }

    elapsed_ms = (time.time() - t0) * 1000
    result["processing_ms"] = round(elapsed_ms, 1)
    result["n_points"] = len(points)

    out_path = os.path.join(output_dir, f"{scan_id}_joints.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(f"  → {result['n_joints']} joints in {elapsed_ms:.0f}ms → {out_path}")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Joint detector for body scans")
    parser.add_argument("--scan-dir", required=True, help="Directory with .ply files")
    parser.add_argument("--output-dir", required=True, help="Output directory for joints.json")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    ply_files = [f for f in os.listdir(args.scan_dir) if f.endswith(".ply")]

    if not ply_files:
        print(f"No .ply files found in {args.scan_dir}")
        sys.exit(1)

    for ply_file in sorted(ply_files):
        process_scan(os.path.join(args.scan_dir, ply_file), args.output_dir)

    print(f"\nDone. Joints written to {args.output_dir}")
