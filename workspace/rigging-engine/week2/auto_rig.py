"""
auto_rig.py — Blender headless rigging script (Week 2)
Run with: blender --background --python auto_rig.py -- <joints_json> <ply_path> <output_glb>

Takes:
  - joints.json  : 3D joint positions from joint_detector.py
  - .ply mesh    : body scan point cloud (converted to mesh inline)
  - output.glb   : rigged + animated glTF output

Pipeline:
  1. Load/create mesh from point cloud (or create humanoid proxy)
  2. Create Rigify armature from joint positions
  3. Parent mesh to armature with automatic weights
  4. Add walk cycle animation via keyframes
  5. Export as .glb
"""

import bpy
import json
import sys
import os
import time
import math

# Parse args after "--"
argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

if len(argv) < 3:
    print("Usage: blender --background --python auto_rig.py -- <joints.json> <ply_or_none> <output.glb>")
    sys.exit(1)

JOINTS_JSON = argv[0]
PLY_PATH = argv[1]  # May be "none" if unavailable
OUTPUT_GLB = argv[2]

t_start = time.time()

print(f"[auto_rig] Joints: {JOINTS_JSON}")
print(f"[auto_rig] Mesh: {PLY_PATH}")
print(f"[auto_rig] Output: {OUTPUT_GLB}")


# ── Load Joints ────────────────────────────────────────────────────────────────

with open(JOINTS_JSON, "r") as f:
    joint_data = json.load(f)

joints = joint_data["joints"]
scan_id = joint_data.get("scan_id", "scan")
print(f"[auto_rig] Loaded {len(joints)} joints for {scan_id}")


# ── Scene Setup ────────────────────────────────────────────────────────────────

# Clear default scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30


# ── Create Humanoid Mesh ───────────────────────────────────────────────────────
# Since .ply point clouds can't be directly rigged, we create a capsule-based
# humanoid mesh that matches the joint proportions. In production this would be
# replaced by proper mesh reconstruction from the point cloud.

def get_joint(name):
    j = joints.get(name)
    if j:
        return (j["x"], j["z"], j["y"])  # Blender: Y-forward, Z-up
    return None


def joint_dist(a, b):
    ja, jb = get_joint(a), get_joint(b)
    if ja and jb:
        return math.sqrt(sum((ja[i] - jb[i])**2 for i in range(3)))
    return 0.3


# Detect body proportions from joints
head_pos = get_joint("head") or (0, 0, 1.65)
neck_pos = get_joint("neck") or (0, 0, 1.5)
lsho_pos = get_joint("left_shoulder") or (-0.2, 0, 1.4)
rsho_pos = get_joint("right_shoulder") or (0.2, 0, 1.4)
lhip_pos = get_joint("left_hip") or (-0.1, 0, 0.9)
rhip_pos = get_joint("right_hip") or (0.1, 0, 0.9)
lankle_pos = get_joint("left_ankle") or (-0.1, 0, 0.05)
rankle_pos = get_joint("right_ankle") or (0.1, 0, 0.05)

body_height = head_pos[2] - min(lankle_pos[2], rankle_pos[2])
shoulder_span = abs(lsho_pos[0] - rsho_pos[0]) if lsho_pos and rsho_pos else 0.4

print(f"[auto_rig] Body height: {body_height:.3f}m, shoulder span: {shoulder_span:.3f}m")


def add_capsule_limb(name, p1, p2, radius, collection):
    """Create a capsule between two points."""
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    cz = (p1[2] + p2[2]) / 2
    length = math.sqrt(sum((p1[i]-p2[i])**2 for i in range(3)))

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=(cx, cy, cz),
        vertices=8,
    )
    obj = bpy.context.active_object
    obj.name = name

    # Orient along segment
    dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    if length > 0.001:
        rot_x = math.atan2(math.sqrt(dx**2 + dy**2), dz)
        rot_z = math.atan2(dy, dx)
        obj.rotation_euler = (rot_x, 0, rot_z)

    collection.objects.link(obj)
    return obj


# Create body mesh collection
body_col = bpy.data.collections.new("BodyMesh")
bpy.context.scene.collection.children.link(body_col)

mesh_objects = []

# Torso
hips_mid = get_joint("hips") or (0, 0, 0.95)
neck_mid = neck_pos

bpy.ops.mesh.primitive_uv_sphere_add(
    radius=shoulder_span * 0.55,
    location=(
        (lsho_pos[0]+rsho_pos[0])/2,
        (lsho_pos[1]+rsho_pos[1])/2,
        (neck_mid[2]+hips_mid[2])/2,
    ),
    segments=12, ring_count=8
)
torso = bpy.context.active_object
torso.name = "Torso"
torso.scale[2] = (neck_mid[2]-hips_mid[2]) / (shoulder_span * 1.1)
body_col.objects.link(torso)
mesh_objects.append(torso)

# Head
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.11,
    location=head_pos,
    segments=12, ring_count=8
)
head_obj = bpy.context.active_object
head_obj.name = "Head"
body_col.objects.link(head_obj)
mesh_objects.append(head_obj)

# Arms
for side, sho, elb, wri in [
    ("L", get_joint("left_shoulder"), get_joint("left_elbow"), get_joint("left_wrist")),
    ("R", get_joint("right_shoulder"), get_joint("right_elbow"), get_joint("right_wrist")),
]:
    if sho and elb:
        mesh_objects.append(add_capsule_limb(f"UpperArm_{side}", sho, elb, 0.04, body_col))
    if elb and wri:
        mesh_objects.append(add_capsule_limb(f"LowerArm_{side}", elb, wri, 0.03, body_col))

# Legs
for side, hip, kne, ank in [
    ("L", get_joint("left_hip"), get_joint("left_knee"), get_joint("left_ankle")),
    ("R", get_joint("right_hip"), get_joint("right_knee"), get_joint("right_ankle")),
]:
    if hip and kne:
        mesh_objects.append(add_capsule_limb(f"UpperLeg_{side}", hip, kne, 0.07, body_col))
    if kne and ank:
        mesh_objects.append(add_capsule_limb(f"LowerLeg_{side}", kne, ank, 0.05, body_col))

# Join all mesh parts into one
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    if obj is not None:
        obj.select_set(True)
bpy.context.view_layer.objects.active = mesh_objects[0]
bpy.ops.object.join()
body_mesh = bpy.context.active_object
body_mesh.name = f"BodyMesh_{scan_id}"

t_mesh = time.time()
print(f"[auto_rig] Mesh built in {(t_mesh - t_start)*1000:.0f}ms, "
      f"verts={len(body_mesh.data.vertices)}")


# ── Create Armature ────────────────────────────────────────────────────────────

bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
armature = bpy.context.active_object
armature.name = f"Armature_{scan_id}"
arm_data = armature.data
arm_data.name = f"Skeleton_{scan_id}"

edit_bones = arm_data.edit_bones

# Delete default bone
for b in list(edit_bones):
    edit_bones.remove(b)


def add_bone(name, head_pt, tail_pt, parent_name=None):
    """Add a bone, optionally parented."""
    b = edit_bones.new(name)
    b.head = head_pt
    b.tail = tail_pt
    if parent_name and parent_name in edit_bones:
        b.parent = edit_bones[parent_name]
        b.use_connect = False
    return b


def j2b(joint_name, fallback=(0, 0, 0)):
    """Get joint position in Blender coordinates (swap Y/Z)."""
    j = joints.get(joint_name)
    if j:
        return (j["x"], j["z"], j["y"])
    return fallback


# Root / Hips
root_pos = j2b("hips", (0, 0, 0.95))
add_bone("root", (root_pos[0], root_pos[1], 0.0), root_pos)

# Spine
spine_mid = j2b("spine_mid", (0, 0, 1.2))
add_bone("spine", root_pos, spine_mid, "root")

neck = j2b("neck", (0, 0, 1.5))
add_bone("chest", spine_mid, neck, "spine")

head_j = j2b("head", (0, 0, 1.7))
add_bone("neck", neck, head_j, "chest")
add_bone("head", head_j, (head_j[0], head_j[1], head_j[2] + 0.15), "neck")

# Left arm
ls = j2b("left_shoulder", (-0.2, 0, 1.4))
le = j2b("left_elbow", (-0.4, 0, 1.15))
lw = j2b("left_wrist", (-0.55, 0, 0.9))
add_bone("upper_arm_L", ls, le, "chest")
add_bone("lower_arm_L", le, lw, "upper_arm_L")
add_bone("hand_L", lw, (lw[0]-0.08, lw[1], lw[2]-0.02), "lower_arm_L")

# Right arm
rs = j2b("right_shoulder", (0.2, 0, 1.4))
re = j2b("right_elbow", (0.4, 0, 1.15))
rw = j2b("right_wrist", (0.55, 0, 0.9))
add_bone("upper_arm_R", rs, re, "chest")
add_bone("lower_arm_R", re, rw, "upper_arm_R")
add_bone("hand_R", rw, (rw[0]+0.08, rw[1], rw[2]-0.02), "lower_arm_R")

# Left leg
lh = j2b("left_hip", (-0.1, 0, 0.9))
lk = j2b("left_knee", (-0.1, 0, 0.5))
la = j2b("left_ankle", (-0.1, 0, 0.05))
add_bone("thigh_L", lh, lk, "root")
add_bone("shin_L", lk, la, "thigh_L")
add_bone("foot_L", la, (la[0]-0.05, la[1]+0.15, la[2]), "shin_L")

# Right leg
rh = j2b("right_hip", (0.1, 0, 0.9))
rk = j2b("right_knee", (0.1, 0, 0.5))
ra = j2b("right_ankle", (0.1, 0, 0.05))
add_bone("thigh_R", rh, rk, "root")
add_bone("shin_R", rk, ra, "thigh_R")
add_bone("foot_R", ra, (ra[0]+0.05, ra[1]+0.15, ra[2]), "shin_R")

bpy.ops.object.mode_set(mode='OBJECT')
t_rig = time.time()
print(f"[auto_rig] Armature built in {(t_rig - t_mesh)*1000:.0f}ms, "
      f"bones={len(arm_data.bones)}")


# ── Parent Mesh to Armature (Automatic Weights) ────────────────────────────────

bpy.ops.object.select_all(action='DESELECT')
body_mesh.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

t_weight = time.time()
print(f"[auto_rig] Weight painting done in {(t_weight - t_rig)*1000:.0f}ms")


# ── Walk Cycle Animation ───────────────────────────────────────────────────────
# Simple procedural walk cycle: 30 frames @ 30fps = 1 second loop

bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

pose_bones = armature.pose.bones
scene.frame_start = 1
scene.frame_end = 60  # 2 second loop

def set_rot_y(bone_name, frame, angle_deg):
    if bone_name not in pose_bones:
        return
    pb = pose_bones[bone_name]
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler[1] = math.radians(angle_deg)
    pb.keyframe_insert("rotation_euler", frame=frame, index=1)

def set_rot_x(bone_name, frame, angle_deg):
    if bone_name not in pose_bones:
        return
    pb = pose_bones[bone_name]
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler[0] = math.radians(angle_deg)
    pb.keyframe_insert("rotation_euler", frame=frame, index=0)


# Walk cycle keyframes
# Pattern: leg forward/back swings alternating, arms counter-swing
WALK_FRAMES = [1, 15, 30, 45, 60]

# Thigh L: forward at 1, back at 15, neutral at 30, forward again 60
thigh_L_angles = [25, -20, 25, -20, 25]
thigh_R_angles = [-20, 25, -20, 25, -20]
shin_L_angles =  [0, -30, 0, -30, 0]
shin_R_angles =  [-30, 0, -30, 0, -30]
arm_L_angles  =  [-20, 15, -20, 15, -20]
arm_R_angles  =  [15, -20, 15, -20, 15]

for i, frame in enumerate(WALK_FRAMES):
    set_rot_x("thigh_L", frame, thigh_L_angles[i])
    set_rot_x("thigh_R", frame, thigh_R_angles[i])
    set_rot_x("shin_L", frame, shin_L_angles[i])
    set_rot_x("shin_R", frame, shin_R_angles[i])
    set_rot_x("upper_arm_L", frame, arm_L_angles[i])
    set_rot_x("upper_arm_R", frame, arm_R_angles[i])

# Make all curves cyclic (Blender 5 compatible)
for action in bpy.data.actions:
    if action.is_action_legacy:
        for strip in getattr(action, 'fcurves', []):
            mod = strip.modifiers.new(type='CYCLES')
    # For layered actions, use use_cyclic flag
    action.use_cyclic = True

bpy.ops.object.mode_set(mode='OBJECT')
t_anim = time.time()
print(f"[auto_rig] Walk cycle keyed in {(t_anim - t_weight)*1000:.0f}ms")


# ── Export GLB ────────────────────────────────────────────────────────────────

os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_GLB)), exist_ok=True)

bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    export_morph=False,
    export_lights=False,
    export_cameras=False,
    use_selection=False,
    export_yup=True,
    export_apply=True,
)

t_end = time.time()
total_ms = (t_end - t_start) * 1000

# Collect metrics
glb_size_kb = os.path.getsize(OUTPUT_GLB) / 1024
vert_count = len(body_mesh.data.vertices)
bone_count = len(arm_data.bones)

print(f"\n[auto_rig] ✅ COMPLETE")
print(f"  scan_id:      {scan_id}")
print(f"  output:       {OUTPUT_GLB}")
print(f"  total_ms:     {total_ms:.0f}")
print(f"  vert_count:   {vert_count}")
print(f"  bone_count:   {bone_count}")
print(f"  glb_size_kb:  {glb_size_kb:.1f}")
print(f"  animation_fps: 30")

# Write metrics JSON alongside output
metrics = {
    "scan_id": scan_id,
    "rig_time_ms": round(total_ms, 1),
    "vert_count": vert_count,
    "bone_count": bone_count,
    "file_size_kb": round(glb_size_kb, 1),
    "animation_fps": 30,
    "walk_cycle_frames": 60,
    "sla_pass": total_ms < 500000,  # <500s total (including mesh creation)
}

metrics_path = OUTPUT_GLB.replace(".glb", "_metrics.json")
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"  metrics:      {metrics_path}")
