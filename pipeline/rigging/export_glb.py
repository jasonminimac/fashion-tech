"""
export_glb.py — Walk Cycle Bake + .glb Export
Fashion Tech Pipeline — Sprint 1

Takes a rigged .blend file (produced by auto_rig.py), applies a walk cycle
animation (keyframed procedural walk or BVH retarget), and exports a .glb
file suitable for playback in Google's <model-viewer> web component.

USAGE:
    blender --background --python export_glb.py -- input_rigged.blend output.glb [walk.bvh]

EXAMPLES:
    # Procedural keyframed walk cycle (no BVH needed):
    blender --background --python export_glb.py -- rigged.blend output/avatar.glb

    # BVH retarget walk cycle:
    blender --background --python export_glb.py -- rigged.blend output/avatar.glb walk.bvh

NOTES:
    - Output .glb is Y-up (GLTF convention) — correct for <model-viewer>
    - Animation name in .glb: "Walk"
    - Walk cycle: 30-frame loop at 30 fps = 1 second cycle
    - The .glb includes the mesh, rig (as skin), and Walk animation track
    - Tested compatible with Google model-viewer >= 3.x

<model-viewer> test snippet:
    <model-viewer
        src="avatar.glb"
        autoplay
        animation-name="Walk"
        camera-controls
        style="width:400px;height:600px">
    </model-viewer>
"""

import sys
import os
import math

try:
    import bpy
    import mathutils
except ImportError:
    print("ERROR: Must be run inside Blender.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    """Parse CLI args after '--'."""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    if len(argv) < 2:
        print("USAGE: blender --background --python export_glb.py -- input.blend output.glb [walk.bvh]")
        sys.exit(1)

    blend_path = argv[0]
    glb_path   = argv[1]
    bvh_path   = argv[2] if len(argv) >= 3 else None
    return blend_path, glb_path, bvh_path


# ---------------------------------------------------------------------------
# BVH retarget helpers
# ---------------------------------------------------------------------------

def import_bvh_and_retarget(bvh_path: str, target_rig):
    """
    Import a BVH animation file and retarget it onto target_rig using
    Blender's built-in BVH importer + NLA/Action retargeting.

    The BVH is expected to be Mixamo-compatible (Y-up, standard bone names).
    Retargeting strategy: copy-transforms approach via pose library or manual
    constraint-based retarget.

    Args:
        bvh_path: Path to the .bvh file (Mixamo walk cycle recommended)
        target_rig: The Armature object to receive the animation

    Returns:
        The baked Action on target_rig, or None on failure.
    """
    print(f"  Importing BVH: {bvh_path}")

    # Import BVH as a new armature
    bpy.ops.import_anim.bvh(
        filepath=bvh_path,
        axis_forward='-Z',
        axis_up='Y',
        use_fps=30,
    )
    bvh_rig = bpy.context.active_object
    if not bvh_rig or bvh_rig.type != 'ARMATURE':
        print("  ERROR: BVH import did not produce an armature.")
        return None

    bvh_rig.name = "BVH_Source"
    print(f"  BVH source rig: {bvh_rig.name}")

    # --- Constraint-based retarget ---
    # For each bone in target_rig that has a matching name in bvh_rig,
    # add a COPY_ROTATION + COPY_LOCATION constraint pointing at bvh_rig.
    # Then bake to a new action.

    bpy.ops.object.select_all(action='DESELECT')
    target_rig.select_set(True)
    bpy.context.view_layer.objects.active = target_rig
    bpy.ops.object.mode_set(mode='POSE')

    retarget_map = _build_bone_retarget_map(target_rig, bvh_rig)
    _apply_retarget_constraints(target_rig, bvh_rig, retarget_map)

    # Determine frame range from BVH action
    bvh_action = bvh_rig.animation_data.action if bvh_rig.animation_data else None
    frame_start = int(bvh_action.frame_range[0]) if bvh_action else 1
    frame_end   = int(bvh_action.frame_range[1]) if bvh_action else 30

    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end   = frame_end

    # Bake constraints to keyframes
    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        use_current_action=False,
        bake_types={'POSE'},
    )

    action = target_rig.animation_data.action
    if action:
        action.name = "Walk"
        # Mark as cyclic
        for fc in action.fcurves:
            fc.modifiers.new(type='CYCLES')

    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove BVH source rig
    bpy.ops.object.select_all(action='DESELECT')
    bvh_rig.select_set(True)
    bpy.ops.object.delete()

    print("  BVH retarget complete.")
    return action


def _build_bone_retarget_map(target_rig, bvh_rig) -> dict:
    """
    Build a mapping from target bone names → BVH bone names.

    Tries exact match first, then a normalized (lowercase, strip prefix)
    fuzzy match. Extend this map for your specific BVH bone naming convention.

    Returns:
        { "upper_arm.L": "LeftArm", ... }
    """
    # Rigify → Mixamo BVH bone name mapping
    RIGIFY_TO_MIXAMO = {
        "spine":         "Hips",
        "spine.001":     "Spine",
        "spine.002":     "Spine1",
        "spine.003":     "Spine2",
        "neck":          "Neck",
        "head":          "Head",
        "shoulder.L":    "LeftShoulder",
        "upper_arm.L":   "LeftArm",
        "forearm.L":     "LeftForeArm",
        "hand.L":        "LeftHand",
        "shoulder.R":    "RightShoulder",
        "upper_arm.R":   "RightArm",
        "forearm.R":     "RightForeArm",
        "hand.R":        "RightHand",
        "thigh.L":       "LeftUpLeg",
        "shin.L":        "LeftLeg",
        "foot.L":        "LeftFoot",
        "toe.L":         "LeftToeBase",
        "thigh.R":       "RightUpLeg",
        "shin.R":        "RightLeg",
        "foot.R":        "RightFoot",
        "toe.R":         "RightToeBase",
    }

    bvh_bone_names = {b.name for b in bvh_rig.pose.bones}
    retarget_map = {}

    for rigify_name, mixamo_name in RIGIFY_TO_MIXAMO.items():
        if rigify_name in {b.name for b in target_rig.pose.bones}:
            if mixamo_name in bvh_bone_names:
                retarget_map[rigify_name] = mixamo_name
            else:
                print(f"    SKIP retarget: BVH bone '{mixamo_name}' not found.")

    print(f"    Retarget map: {len(retarget_map)} bones matched.")
    return retarget_map


def _apply_retarget_constraints(target_rig, bvh_rig, retarget_map: dict):
    """Add COPY_ROTATION + COPY_LOCATION constraints to pose bones."""
    for rigify_name, bvh_name in retarget_map.items():
        pbone = target_rig.pose.bones.get(rigify_name)
        if not pbone:
            continue

        # Copy location only for root/hips
        if rigify_name == "spine":
            loc_c = pbone.constraints.new(type='COPY_LOCATION')
            loc_c.target  = bvh_rig
            loc_c.subtarget = bvh_name

        rot_c = pbone.constraints.new(type='COPY_ROTATION')
        rot_c.target    = bvh_rig
        rot_c.subtarget = bvh_name
        rot_c.mix_mode  = 'REPLACE'


# ---------------------------------------------------------------------------
# Procedural keyframed walk cycle
# ---------------------------------------------------------------------------

def create_procedural_walk_cycle(rig, frame_start: int = 1, frame_end: int = 30):
    """
    Insert a simple, procedural keyframed walk cycle onto the rig.

    This is a fallback when no BVH file is provided. It produces a
    convincing looping walk cycle using sinusoidal bone rotations.

    Walk cycle design (30 frames = 1 full stride at 30 fps):
        - Hips: gentle side-to-side sway + slight vertical bob
        - Legs: alternating swing (thigh + shin) — forward/back pendulum
        - Arms: opposite swing to legs (cross-body)
        - Spine: slight forward lean + counter-rotation

    All rotations are in degrees and applied as pose bone rotations.

    Args:
        rig: The Armature object (Rigify rig or plain armature)
        frame_start: First frame of the cycle
        frame_end:   Last frame (exclusive — frame_end keyframe == frame_start)

    Returns:
        The created Action.
    """
    print("  Creating procedural walk cycle...")

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    scene = bpy.context.scene
    scene.frame_start = frame_start
    scene.frame_end   = frame_end - 1  # last keyframe is frame_end-1; frame_end == frame_start

    # Create a fresh action
    action = bpy.data.actions.new(name="Walk")
    if not rig.animation_data:
        rig.animation_data_create()
    rig.animation_data.action = action

    N      = frame_end - frame_start  # number of frames in one cycle (30)
    frames = list(range(frame_start, frame_end + 1))  # inclusive end for loop closure

    def deg2rad(d):
        return d * math.pi / 180.0

    def set_rotation(bone_name, axis_index, angle_deg, frame):
        """
        Set a single Euler rotation channel for a pose bone at a frame.
        axis_index: 0=X, 1=Y, 2=Z
        """
        pbone = rig.pose.bones.get(bone_name)
        if not pbone:
            return
        pbone.rotation_mode = 'XYZ'
        rot = list(pbone.rotation_euler)
        rot[axis_index] = deg2rad(angle_deg)
        pbone.rotation_euler = rot
        pbone.keyframe_insert(data_path="rotation_euler", index=axis_index, frame=frame)

    def set_location(bone_name, axis_index, value, frame):
        """Set a single location channel for a pose bone at a frame."""
        pbone = rig.pose.bones.get(bone_name)
        if not pbone:
            return
        loc = list(pbone.location)
        loc[axis_index] = value
        pbone.location = loc
        pbone.keyframe_insert(data_path="location", index=axis_index, frame=frame)

    # Reset all pose bones to rest pose first
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()

    # Walk cycle bone parameters
    # Each entry: (bone_name, axis, amplitude_deg, phase_offset_frames, dc_offset_deg)
    # Phase: leg swing is 180° out of phase L vs R
    leg_swing_params = [
        # thigh swing: primary propulsion — 30° amplitude, X axis (forward/back)
        ("thigh.L",     0,  30.0,  0,   5.0),   # left thigh leads
        ("thigh.R",     0,  30.0,  N/2, 5.0),   # right thigh 180° behind
        # knee bend: trails thigh by 90° — shin bends back as leg swings back
        ("shin.L",      0, -20.0, N/4,  -10.0),
        ("shin.R",      0, -20.0, N*3//4, -10.0),
        # foot pitch: toe-off and heel-strike
        ("foot.L",      0,  15.0,  N/4,  5.0),
        ("foot.R",      0,  15.0,  N*3//4, 5.0),
        # arm swing: cross-body (opposite to legs)
        ("upper_arm.L", 0, -25.0, N/2, 0.0),   # left arm swings opposite right leg
        ("upper_arm.R", 0, -25.0,  0,   0.0),
        # slight elbow bend during swing
        ("forearm.L",   0,  10.0,  0,   -5.0),
        ("forearm.R",   0,  10.0,  N/2, -5.0),
    ]

    hip_params = [
        # hips: side-to-side sway (Y axis) at 2x stride frequency
        ("spine",       1,  3.0,   0,   0.0),
        # hips: vertical bob (Z location) at 2x stride frequency
        # slight forward lean
        ("spine",       0,  5.0,   0,   8.0),   # constant forward lean
    ]

    spine_twist = [
        # spine counter-rotation to arms
        ("spine.003",   2,  5.0,   N/4, 0.0),
    ]

    all_params = leg_swing_params + hip_params + spine_twist

    for frame in frames:
        t = (frame - frame_start) / N  # normalised [0, 1)
        angle_rad = 2 * math.pi * t

        for bone_name, axis, amplitude, phase_frames, dc in all_params:
            phase_rad = 2 * math.pi * (phase_frames / N)
            angle = amplitude * math.sin(angle_rad + phase_rad) + dc
            set_rotation(bone_name, axis, angle, frame)

        # Vertical hip bob (Z location) — 2x per stride
        hip_bob = 0.02 * math.sin(2 * angle_rad)
        set_location("spine", 2, hip_bob, frame)

    # Make all fcurves interpolate with BEZIER for smooth motion
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
        # Add CYCLES modifier so it loops in model-viewer
        mod = fc.modifiers.new(type='CYCLES')
        mod.mode_before = 'REPEAT'
        mod.mode_after  = 'REPEAT'

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"  Walk cycle created: {len(action.fcurves)} fcurves, frames {frame_start}–{frame_end}.")
    return action


# ---------------------------------------------------------------------------
# .glb export
# ---------------------------------------------------------------------------

def export_glb(output_path: str, frame_start: int = 1, frame_end: int = 30):
    """
    Export the current scene to a binary glTF 2.0 (.glb) file.

    Export settings for <model-viewer> compatibility:
        - Y-up axis (GLTF standard)
        - Apply modifiers (clean geometry)
        - Include all animations
        - Embed textures
        - Use armature bones as skin
        - No extras / custom properties

    Args:
        output_path: Destination .glb file path
        frame_start: Animation start frame (for export range)
        frame_end:   Animation end frame
    """
    print(f"  Exporting .glb → {output_path}")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(output_path),
        export_format='GLB',
        export_apply=True,               # apply modifiers
        export_animations=True,          # include animations
        export_frame_range=True,
        export_frame_step=1,
        export_anim_single_armature=True,
        export_skins=True,
        export_morph=True,
        export_morph_normal=True,
        export_texcoords=True,
        export_normals=True,
        export_colors=True,
        export_materials='EXPORT',
        export_yup=True,                 # Y-up for web / model-viewer
        export_cameras=False,
        export_lights=False,
        export_extras=False,
        use_selection=False,             # export whole scene
    )
    print(f"  ✓ .glb exported: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    blend_path, glb_path, bvh_path = parse_args()

    print("=" * 60)
    print("Fashion Tech — Walk Cycle Bake + .glb Export")
    print(f"  Blend:  {blend_path}")
    print(f"  Output: {glb_path}")
    if bvh_path:
        print(f"  BVH:    {bvh_path}")
    else:
        print("  Mode:   Procedural keyframed walk cycle")
    print("=" * 60)

    if not os.path.isfile(blend_path):
        print(f"ERROR: .blend file not found: {blend_path}")
        sys.exit(1)

    # Load the rigged .blend
    print(f"  Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend_path))

    # Find the rig armature
    rig = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            rig = obj
            break

    if rig is None:
        print("ERROR: No armature found in .blend file. Was auto_rig.py run first?")
        sys.exit(1)

    print(f"  Found rig: {rig.name}")

    # Apply animation
    frame_start, frame_end = 1, 30

    if bvh_path:
        if not os.path.isfile(bvh_path):
            print(f"  WARNING: BVH file not found ({bvh_path}), falling back to procedural walk.")
            bvh_path = None

    if bvh_path:
        action = import_bvh_and_retarget(bvh_path, rig)
        if action:
            frame_start = int(bpy.context.scene.frame_start)
            frame_end   = int(bpy.context.scene.frame_end)
        else:
            print("  BVH retarget failed — falling back to procedural walk cycle.")
            action = create_procedural_walk_cycle(rig, frame_start, frame_end)
    else:
        action = create_procedural_walk_cycle(rig, frame_start, frame_end)

    # Export
    export_glb(glb_path, frame_start, frame_end)

    print(f"\n✓ Done. Walk cycle .glb ready: {glb_path}")
    print("=" * 60)
    print("To test in model-viewer:")
    print(f"""
  <model-viewer
      src="{os.path.basename(glb_path)}"
      autoplay
      animation-name="Walk"
      camera-controls
      style="width:400px;height:700px">
  </model-viewer>
    """)


if __name__ == "__main__":
    main()
