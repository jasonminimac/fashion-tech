"""
generate_synthetic_scans.py
Week 2 — Generate synthetic body scan .ply files for testing.
Simulates realistic body proportions for 3 body types.
Used when real iPhone scans are not yet available from Scanning Lead.
"""

import numpy as np
import struct
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "test_data", "real_scans")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_body_point_cloud(
    height_m: float = 1.75,
    shoulder_width_m: float = 0.42,
    hip_width_m: float = 0.38,
    n_points: int = 50000,
    noise_mm: float = 3.0,
    body_type: str = "average",
) -> np.ndarray:
    """
    Generate a synthetic human body point cloud in T-pose.

    Returns: (N, 6) array of [x, y, z, r, g, b]
    Coordinate system: Y-up, meters
    """
    rng = np.random.default_rng(42)
    points = []

    def noisy(arr):
        return arr + rng.normal(0, noise_mm / 1000.0, arr.shape)

    # Head (sphere at top)
    head_r = 0.12
    head_center = np.array([0, height_m - head_r * 0.8, 0])
    n_head = int(n_points * 0.08)
    theta = rng.uniform(0, np.pi, n_head)
    phi = rng.uniform(0, 2 * np.pi, n_head)
    head_pts = head_center + head_r * np.column_stack([
        np.sin(theta) * np.cos(phi),
        np.cos(theta),
        np.sin(theta) * np.sin(phi),
    ])
    points.append(noisy(head_pts))

    # Torso (ellipsoid-ish)
    torso_top = height_m - head_r * 2
    torso_bot = height_m * 0.52
    n_torso = int(n_points * 0.30)
    t = rng.uniform(0, 1, n_torso)
    torso_y = torso_bot + t * (torso_top - torso_bot)
    ratio = (torso_y - torso_bot) / (torso_top - torso_bot)
    width = (shoulder_width_m * ratio + hip_width_m * (1 - ratio)) / 2
    depth = width * 0.6
    angle = rng.uniform(0, 2 * np.pi, n_torso)
    torso_pts = np.column_stack([
        width * np.cos(angle),
        torso_y,
        depth * np.sin(angle),
    ])
    points.append(noisy(torso_pts))

    # Left arm
    n_arm = int(n_points * 0.12)
    arm_t = rng.uniform(0, 1, n_arm)
    arm_y = (torso_top - 0.05) - arm_t * 0.55
    arm_x = -(shoulder_width_m / 2 + arm_t * 0.15)
    arm_r = 0.04 - arm_t * 0.01
    arm_angle = rng.uniform(0, 2 * np.pi, n_arm)
    left_arm = np.column_stack([
        arm_x + arm_r * np.cos(arm_angle),
        arm_y,
        arm_r * np.sin(arm_angle),
    ])
    points.append(noisy(left_arm))

    # Right arm (mirror)
    right_arm = left_arm.copy()
    right_arm[:, 0] = -left_arm[:, 0]
    points.append(noisy(right_arm))

    # Left leg
    n_leg = int(n_points * 0.15)
    leg_t = rng.uniform(0, 1, n_leg)
    leg_y = torso_bot - leg_t * torso_bot
    leg_x = -(hip_width_m / 4 + leg_t * 0.02)
    leg_r = 0.07 - leg_t * 0.02
    leg_angle = rng.uniform(0, 2 * np.pi, n_leg)
    left_leg = np.column_stack([
        leg_x + leg_r * np.cos(leg_angle),
        leg_y,
        leg_r * np.sin(leg_angle),
    ])
    points.append(noisy(left_leg))

    # Right leg
    right_leg = left_leg.copy()
    right_leg[:, 0] = -left_leg[:, 0]
    points.append(noisy(right_leg))

    all_pts = np.vstack(points)

    # RGB: skin-tone approximation
    r = np.full(len(all_pts), 220, dtype=np.uint8)
    g = np.full(len(all_pts), 180, dtype=np.uint8)
    b = np.full(len(all_pts), 150, dtype=np.uint8)
    color_noise = rng.integers(-15, 15, (len(all_pts), 3), dtype=np.int16)
    rgb = np.clip(
        np.column_stack([r, g, b]).astype(np.int16) + color_noise,
        0, 255
    ).astype(np.uint8)

    return np.column_stack([all_pts, rgb])


def write_ply(filepath: str, points: np.ndarray):
    """Write points (N, 6) as ASCII PLY."""
    n = len(points)
    with open(filepath, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {n}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for pt in points:
            f.write(f"{pt[0]:.6f} {pt[1]:.6f} {pt[2]:.6f} "
                    f"{int(pt[3])} {int(pt[4])} {int(pt[5])}\n")


BODY_TYPES = [
    {
        "scan_id": "scan_001_average",
        "body_type": "average",
        "height_m": 1.75,
        "shoulder_width_m": 0.42,
        "hip_width_m": 0.38,
        "n_points": 55000,
    },
    {
        "scan_id": "scan_002_tall",
        "body_type": "tall",
        "height_m": 1.92,
        "shoulder_width_m": 0.46,
        "hip_width_m": 0.40,
        "n_points": 55000,
    },
    {
        "scan_id": "scan_003_broad",
        "body_type": "broad",
        "height_m": 1.70,
        "shoulder_width_m": 0.52,
        "hip_width_m": 0.46,
        "n_points": 55000,
    },
]


def main():
    print("Generating synthetic body scan .ply files...")
    for spec in BODY_TYPES:
        t0 = time.time()
        pts = generate_body_point_cloud(
            height_m=spec["height_m"],
            shoulder_width_m=spec["shoulder_width_m"],
            hip_width_m=spec["hip_width_m"],
            n_points=spec["n_points"],
            body_type=spec["body_type"],
        )
        outpath = os.path.join(OUTPUT_DIR, f"{spec['scan_id']}.ply")
        write_ply(outpath, pts)
        elapsed = (time.time() - t0) * 1000
        size_kb = os.path.getsize(outpath) / 1024
        print(f"  ✅ {spec['scan_id']}: {len(pts)} pts, "
              f"{size_kb:.0f} KB, {elapsed:.0f}ms")
    print(f"\nSaved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
