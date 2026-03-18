"""
auto_rig.py — Rigify Auto-Rig Script
Fashion Tech Pipeline — Sprint 1

Takes a .obj mesh + joints.json (33 MediaPipe landmarks) and produces a
Rigify-rigged .blend file, headlessly via Blender.

USAGE:
    blender --background --python auto_rig.py -- input.obj joints.json output.blend

EXAMPLE:
    blender --background --python auto_rig.py -- assets/meshes/test_human.obj \
        assets/meshes/test_joints.json output/rigged.blend

joints.json schema:
    {
        "scan_id": "scan_001",
        "landmarks": [
            { "id": 0, "name": "nose", "x": 0.0, "y": 1.75, "z": 0.0 },
            ...
        ]
    }

MediaPipe 33 Pose landmark indices (world-space, metres assumed):
    0:  nose
    11: left_shoulder    12: right_shoulder
    13: left_elbow       14: right_elbow
    15: left_wrist       16: right_wrist
    23: left_hip         24: right_hip
    25: left_knee        26: right_knee
    27: left_ankle       28: right_ankle
    29: left_heel        30: right_heel
    31: left_foot_index  32: right_foot_index
"""

import sys
import json
import math
import os

# ---------------------------------------------------------------------------
# Blender import guard — this script must run inside Blender's Python
# ---------------------------------------------------------------------------
try:
    import bpy
    import mathutils
except ImportError:
    print("ERROR: This script must be run inside Blender (bpy not found).")
    print("Run with: blender --background --python auto_rig.py -- mesh.obj joints.json out.blend")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing (Blender passes args after '--')
# ---------------------------------------------------------------------------

def parse_args():
    """Parse CLI arguments passed after the '--' separator to Blender."""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    if len(argv) < 3:
        print("USAGE: blender --background --python auto_rig.py -- input.obj joints.json output.blend")
        sys.exit(1)

    return argv[0], argv[1], argv[2]


# ---------------------------------------------------------------------------
# Landmark helpers
# ---------------------------------------------------------------------------

# Map MediaPipe landmark names → indices we actually need
MP_INDICES = {
    "nose": 0,
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13,    "right_elbow": 14,
    "left_wrist": 15,    "right_wrist": 16,
    "left_hip": 23,      "right_hip": 24,
    "left_knee": 25,     "right_knee": 26,
    "left_ankle": 27,    "right_ankle": 28,
    "left_heel": 29,     "right_heel": 30,
    "left_foot_index": 31, "right_foot_index": 32,
}


def load_landmarks(joints_path: str) -> dict:
    """
    Load joints.json and return a dict keyed by landmark name.

    Returns:
        { "nose": (x, y, z), "left_shoulder": (x, y, z), ... }
    """
    with open(joints_path, "r") as f:
        data = json.load(f)

    lm_by_id = {lm["id"]: lm for lm in data["landmarks"]}
    lm_by_name = {lm["name"]: lm for lm in data["landmarks"]}

    positions = {}
    for name, idx in MP_INDICES.items():
        if name in lm_by_name:
            lm = lm_by_name[name]
        elif idx in lm_by_id:
            lm = lm_by_id[idx]
        else:
            print(f"  WARNING: landmark '{name}' (id={idx}) not found in joints.json — will estimate.")
            lm = None

        if lm:
            # MediaPipe world coords: x=right, y=up, z=forward (into screen)
            # Blender coords:         x=right, y=forward, z=up
            # Conversion: blender_x=mp_x, blender_y=-mp_z, blender_z=mp_y
            positions[name] = (lm["x"], -lm["z"], lm["y"])

    return positions


def midpoint(a, b):
    """Return the midpoint between two (x,y,z) tuples."""
    return ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2)


def vec_add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def vec_scale(a, s):
    return (a[0]*s, a[1]*s, a[2]*s)


def estimate_missing_landmarks(pos: dict) -> dict:
    """
    Fill in any landmarks that couldn't be loaded from file using
    anatomical estimates from the ones we do have.
    """
    p = dict(pos)

    # Neck: midpoint of shoulders, slightly up
    if "neck" not in p and "left_shoulder" in p and "right_shoulder" in p:
        mid = midpoint(p["left_shoulder"], p["right_shoulder"])
        p["neck"] = (mid[0], mid[1], mid[2] + 0.05)

    # Head: above nose slightly
    if "head" not in p and "nose" in p:
        n = p["nose"]
        p["head"] = (n[0], n[1], n[2] + 0.10)

    # Pelvis: midpoint of hips
    if "pelvis" not in p and "left_hip" in p and "right_hip" in p:
        p["pelvis"] = midpoint(p["left_hip"], p["right_hip"])

    # Spine mid: halfway between pelvis and neck (rough)
    if "spine" not in p and "pelvis" in p and "neck" in p:
        p["spine"] = midpoint(p["pelvis"], p["neck"])

    return p


# ---------------------------------------------------------------------------
# Mesh import
# ---------------------------------------------------------------------------

def import_obj(obj_path: str):
    """
    Import .obj file into current Blender scene.

    Returns:
        The imported mesh object.
    """
    print(f"  Importing mesh: {obj_path}")

    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()

    # Import OBJ (Blender 3.x API)
    try:
        bpy.ops.import_scene.obj(filepath=obj_path)
    except AttributeError:
        # Blender 4.x uses wm.obj_import
        bpy.ops.wm.obj_import(filepath=obj_path)

    imported = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if not imported:
        raise RuntimeError("No mesh objects imported from OBJ file.")

    # Join if multiple meshes came in
    if len(imported) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in imported:
            o.select_set(True)
        bpy.context.view_layer.objects.active = imported[0]
        bpy.ops.object.join()

    mesh_obj = bpy.context.active_object
    mesh_obj.name = "BodyMesh"
    print(f"  Mesh imported: {mesh_obj.name} ({len(mesh_obj.data.vertices)} verts)")
    return mesh_obj


# ---------------------------------------------------------------------------
# Rigify skeleton construction
# ---------------------------------------------------------------------------

def build_rigify_metarig(positions: dict):
    """
    Add a Rigify human metarig and reposition its bones to match
    the landmark positions derived from joints.json.

    The strategy:
      1. Add the built-in Rigify human metarig (bpy.ops.object.armature_human_metarig_add)
      2. Enter edit mode and move bone heads/tails to the landmark positions.

    Returns:
        The metarig armature object.
    """
    print("  Building Rigify metarig...")

    # Add Rigify human metarig
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = "MetaRig"

    # Enter edit mode to reposition bones
    bpy.ops.object.mode_set(mode='EDIT')
    bones = metarig.data.edit_bones

    p = estimate_missing_landmarks(positions)

    def set_bone(bone_name, head, tail=None):
        """Set a bone's head (and optionally tail) position."""
        if bone_name not in bones:
            print(f"    SKIP: bone '{bone_name}' not in metarig.")
            return
        b = bones[bone_name]
        if head:
            b.head = mathutils.Vector(head)
        if tail:
            b.tail = mathutils.Vector(tail)

    # ---- Spine chain ----
    if "pelvis" in p:
        set_bone("spine",
                 head=p["pelvis"],
                 tail=p.get("spine", vec_add(p["pelvis"], (0, 0, 0.2))))

    if "spine" in p and "neck" in p:
        set_bone("spine.001", head=p["spine"],
                 tail=midpoint(p["spine"], p["neck"]))
        set_bone("spine.002",
                 head=midpoint(p["spine"], p["neck"]),
                 tail=p["neck"])
        set_bone("spine.003", head=p["neck"],
                 tail=p.get("head", vec_add(p["neck"], (0, 0, 0.15))))

    if "neck" in p and "head" in p:
        set_bone("neck", head=p["neck"], tail=p["head"])
        set_bone("head", head=p["head"],
                 tail=vec_add(p["head"], (0, 0, 0.15)))

    # ---- Arms ----
    for side, prefix in [("left", "upper_arm.L"), ("right", "upper_arm.R")]:
        shoulder_key = f"{side}_shoulder"
        elbow_key = f"{side}_elbow"
        wrist_key = f"{side}_wrist"
        forearm = "forearm.L" if side == "left" else "forearm.R"
        hand = "hand.L" if side == "left" else "hand.R"

        if shoulder_key in p and elbow_key in p:
            set_bone(prefix, head=p[shoulder_key], tail=p[elbow_key])
        if elbow_key in p and wrist_key in p:
            set_bone(forearm, head=p[elbow_key], tail=p[wrist_key])
            set_bone(hand, head=p[wrist_key],
                     tail=vec_add(p[wrist_key], vec_scale(
                         (p[wrist_key][0]-p[elbow_key][0],
                          p[wrist_key][1]-p[elbow_key][1],
                          p[wrist_key][2]-p[elbow_key][2]), 0.3)))

    # ---- Legs ----
    for side, thigh_b, shin_b, foot_b, toe_b in [
        ("left",  "thigh.L", "shin.L", "foot.L", "toe.L"),
        ("right", "thigh.R", "shin.R", "foot.R", "toe.R"),
    ]:
        hip_key   = f"{side}_hip"
        knee_key  = f"{side}_knee"
        ankle_key = f"{side}_ankle"
        heel_key  = f"{side}_heel"
        toe_key   = f"{side}_foot_index"

        if hip_key in p and knee_key in p:
            set_bone(thigh_b, head=p[hip_key], tail=p[knee_key])
        if knee_key in p and ankle_key in p:
            set_bone(shin_b, head=p[knee_key], tail=p[ankle_key])
        if ankle_key in p:
            heel = p.get(heel_key, vec_add(p[ankle_key], (0, -0.05, -0.07)))
            toe  = p.get(toe_key, vec_add(p[ankle_key], (0, 0.15, -0.07)))
            set_bone(foot_b, head=p[ankle_key], tail=heel)
            set_bone(toe_b,  head=heel, tail=toe)

    # ---- Shoulders (clavicles) ----
    if "neck" in p:
        for side, bone_name in [("left", "shoulder.L"), ("right", "shoulder.R")]:
            sh_key = f"{side}_shoulder"
            if sh_key in p:
                set_bone(bone_name, head=p["neck"], tail=p[sh_key])

    bpy.ops.object.mode_set(mode='OBJECT')
    print("  Metarig bones repositioned.")
    return metarig


# ---------------------------------------------------------------------------
# Rigify rig generation
# ---------------------------------------------------------------------------

def generate_rig(metarig):
    """
    Run Rigify's generate_rig operator to produce the final control rig.

    Returns:
        The generated rig object.
    """
    print("  Generating Rigify control rig...")
    bpy.ops.object.select_all(action='DESELECT')
    metarig.select_set(True)
    bpy.context.view_layer.objects.active = metarig

    try:
        bpy.ops.pose.rigify_generate()
    except Exception as e:
        print(f"  WARNING: rigify_generate failed: {e}")
        print("  Falling back to plain armature (metarig only).")
        return metarig

    # The generated rig is the active object after generation
    rig = bpy.context.active_object
    rig.name = "Rig"
    print(f"  Rig generated: {rig.name}")
    return rig


# ---------------------------------------------------------------------------
# Mesh skinning (automatic weights)
# ---------------------------------------------------------------------------

def skin_mesh_to_rig(mesh_obj, rig):
    """
    Parent the mesh to the rig with automatic weights.

    Uses Blender's 'Armature Deform with Automatic Weights' — best
    available automatic skinning without manual weight painting.
    """
    print("  Skinning mesh to rig with automatic weights...")
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig

    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    print("  Skinning complete.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    obj_path, joints_path, output_path = parse_args()

    print("=" * 60)
    print("Fashion Tech — Rigify Auto-Rig Pipeline")
    print(f"  Mesh:   {obj_path}")
    print(f"  Joints: {joints_path}")
    print(f"  Output: {output_path}")
    print("=" * 60)

    # Validate inputs
    if not os.path.isfile(obj_path):
        print(f"ERROR: OBJ file not found: {obj_path}")
        sys.exit(1)
    if not os.path.isfile(joints_path):
        print(f"ERROR: joints.json not found: {joints_path}")
        sys.exit(1)

    # Ensure Rigify is enabled
    print("  Enabling Rigify addon...")
    bpy.ops.preferences.addon_enable(module="rigify")

    # 1. Load landmarks
    print("  Loading landmarks...")
    positions = load_landmarks(joints_path)
    print(f"  Loaded {len(positions)} landmark positions.")

    # 2. Import mesh
    mesh_obj = import_obj(obj_path)

    # 3. Build metarig from landmarks
    metarig = build_rigify_metarig(positions)

    # 4. Generate Rigify control rig
    rig = generate_rig(metarig)

    # 5. Skin mesh to rig
    skin_mesh_to_rig(mesh_obj, rig)

    # 6. Save .blend
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(output_path))
    print(f"\n✓ Saved rigged .blend → {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
