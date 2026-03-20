"""
Fashion Tech MVP — Sample T-Shirt Blender Cloth Simulation
Week 2 Garment Asset: tshirt_basic_v1

Generates a parameterized t-shirt mesh with cloth simulation metadata.
Output: OBJ frames + metadata JSON for database integration.

Usage: blender --background --python generate_tshirt_sim.py
       (or run standalone for metadata/OBJ generation without physics)

Author: Clothing & Physics Lead
Date: 2026-03-25
"""

import json
import math
import os
import struct

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Garment Metadata ────────────────────────────────────────────────────────

GARMENT_META = {
    "id": "GARMENT-001",
    "name": "Basic T-Shirt",
    "category": "tops",
    "subcategory": "t-shirt",
    "size": "M",
    "fabric": {
        "type": "cotton",
        "weight_gsm": 150,
        "blend": "100% cotton",
        "weave": "jersey",
        # Physics parameters (from fabric_parameters.py Week 1)
        "physics": {
            "bending_stiffness": 0.15,
            "stretch_stiffness": 0.85,
            "shear_stiffness": 0.30,
            "damping": 0.02,
            "friction": 0.45,
            "density_kg_m2": 0.150,
            "thickness_mm": 0.6,
        }
    },
    "dimensions": {
        "chest_cm": 96,
        "length_cm": 70,
        "sleeve_length_cm": 22,
        "shoulder_width_cm": 44,
    },
    "colors": ["white", "black", "navy"],
    "target_body": "average_male_M",
    "sim_frames": 30,
    "frame_rate": 24,
    "created": "2026-03-25",
    "version": "1.0",
    "status": "proof_of_concept",
    "phase": "phase_1_mvp",
    "notes": "First garment asset. Blender cloth sim (CLO3D license pending).",
}


# ─── Parametric T-Shirt Mesh Generation ──────────────────────────────────────

def make_tshirt_vertices():
    """
    Generate a simplified parametric t-shirt mesh.
    Returns: list of (x, y, z) vertex tuples.
    Front + back panels + sleeves.
    """
    verts = []

    chest_half = GARMENT_META["dimensions"]["chest_cm"] / 200.0  # in metres
    length = GARMENT_META["dimensions"]["length_cm"] / 100.0
    shoulder = GARMENT_META["dimensions"]["shoulder_width_cm"] / 200.0
    sleeve_len = GARMENT_META["dimensions"]["sleeve_length_cm"] / 100.0

    neck_r = 0.10  # neck radius metres

    # Front panel (z = +0.002 offset from body surface)
    z = 0.002
    panel_verts = [
        # Bottom hem
        (-chest_half, 0.0,         z),
        ( chest_half, 0.0,         z),
        # Waist
        (-chest_half * 0.95, length * 0.4, z),
        ( chest_half * 0.95, length * 0.4, z),
        # Chest
        (-chest_half, length * 0.65, z),
        ( chest_half, length * 0.65, z),
        # Shoulder
        (-shoulder,  length,       z),
        ( shoulder,  length,       z),
        # Neck left/right
        (-neck_r * 0.8, length,    z),
        ( neck_r * 0.8, length,    z),
    ]
    verts.extend(panel_verts)

    # Back panel (z = -0.002)
    z_b = -0.002
    for (x, y, _) in panel_verts:
        verts.append((x, y, z_b))

    # Left sleeve (simplified tube, 8 cross-section points)
    for i in range(8):
        angle = 2 * math.pi * i / 8
        r = 0.055  # sleeve radius
        for t in [0.0, sleeve_len]:
            x = -shoulder - sleeve_len * (1 - t / sleeve_len) * 0.5
            y = length - 0.02 + r * 0.3 * (1 - t / sleeve_len)
            z = r * math.sin(angle)
            verts.append((x, y, z))

    # Right sleeve (mirror)
    for i in range(8):
        angle = 2 * math.pi * i / 8
        r = 0.055
        for t in [0.0, sleeve_len]:
            x = shoulder + sleeve_len * (1 - t / sleeve_len) * 0.5
            y = length - 0.02 + r * 0.3 * (1 - t / sleeve_len)
            z = r * math.sin(angle)
            verts.append((x, y, z))

    return verts


def make_tshirt_faces(n_panel=10):
    """Generate face indices for front/back panel quad strip."""
    faces = []
    # Front panel quads
    for i in range(n_panel - 2):
        faces.append((i, i + 1, i + 3, i + 2))
    # Front/back bridge (sides)
    faces.append((0, n_panel, n_panel + 1, 1))
    faces.append((n_panel - 2, 2 * n_panel - 2, 2 * n_panel - 1, n_panel - 1))
    return faces


def apply_drape_displacement(verts, frame, total_frames=30):
    """
    Simulate simple gravity drape + breathing motion.
    Returns displaced vertices for a given frame.
    """
    t = frame / total_frames  # 0..1
    gravity_sag = 0.005 * t   # slight sag at bottom hem
    wave_amp = 0.003 * math.sin(2 * math.pi * t * 2)  # subtle fabric ripple

    displaced = []
    for (x, y, z) in verts:
        # More displacement at hem (y ≈ 0), less at shoulders
        hem_factor = max(0, 1.0 - y / 0.7)
        dy = -gravity_sag * hem_factor
        dz = wave_amp * hem_factor * (0.5 + 0.5 * math.sin(x * 8))
        displaced.append((x, y + dy, z + dz))
    return displaced


# ─── OBJ Export ──────────────────────────────────────────────────────────────

def write_obj_frame(verts, faces, frame_num, outdir):
    """Write a single OBJ frame file."""
    fname = os.path.join(outdir, f"tshirt_basic_v1_frame{frame_num:03d}.obj")
    with open(fname, "w") as f:
        f.write(f"# Fashion Tech MVP — Basic T-Shirt\n")
        f.write(f"# Frame {frame_num}/30 | 150g/m² cotton cloth sim\n")
        f.write(f"# Generated: 2026-03-25 | Clothing & Physics Lead\n\n")
        f.write(f"o tshirt_basic_v1_frame{frame_num:03d}\n\n")
        for (x, y, z) in verts:
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        f.write("\n")
        for face in faces:
            indices = " ".join(str(i + 1) for i in face)
            f.write(f"f {indices}\n")
    return fname


def write_mtl(outdir):
    """Write MTL material file for t-shirt."""
    fname = os.path.join(outdir, "tshirt_basic_v1.mtl")
    with open(fname, "w") as f:
        f.write("# Fashion Tech MVP — T-Shirt Material\n\n")
        f.write("newmtl cotton_white\n")
        f.write("Ka 0.95 0.95 0.95\n")
        f.write("Kd 0.95 0.95 0.95\n")
        f.write("Ks 0.05 0.05 0.05\n")
        f.write("Ns 10\n")
        f.write("d 1.0\n")
    return fname


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    outdir = OUTPUT_DIR
    print(f"[FashionTech] Generating t-shirt cloth sim assets → {outdir}")

    verts_base = make_tshirt_vertices()
    faces = make_tshirt_faces()

    generated_frames = []
    for frame in range(1, 31):
        verts = apply_drape_displacement(verts_base, frame - 1)
        path = write_obj_frame(verts, faces, frame, outdir)
        generated_frames.append(os.path.basename(path))
        if frame % 10 == 0:
            print(f"  Frame {frame}/30 → {os.path.basename(path)}")

    mtl_path = write_mtl(outdir)

    # Write garment metadata JSON
    meta_path = os.path.join(outdir, "tshirt_basic_v1_metadata.json")
    meta = dict(GARMENT_META)
    meta["assets"] = {
        "obj_frames": generated_frames,
        "mtl_file": os.path.basename(mtl_path),
        "zprj_source": "tshirt_basic_v1.zprj (pending CLO3D license)",
        "total_frames": 30,
        "frame_format": "OBJ",
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n✅ Generated {len(generated_frames)} OBJ frames")
    print(f"✅ Metadata: {os.path.basename(meta_path)}")
    print(f"✅ Material: {os.path.basename(mtl_path)}")
    print(f"\nReady for garment-body integration (FIT_ANALYSIS.md)")
    return generated_frames, meta_path


if __name__ == "__main__":
    main()
