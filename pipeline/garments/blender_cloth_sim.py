"""
blender_cloth_sim.py — Fashion Tech Sprint 1
Garment Systems Engineer: fashion-garments

PURPOSE:
    CLO3D LICENCE BLOCKER FALLBACK
    Generates a 30-frame baked .obj sequence of a t-shirt cloth simulation
    using Blender's built-in cloth physics. This is a pipeline stand-in
    until the CLO3D licence is confirmed.

    The output is structurally valid for pipeline testing (AR engineer,
    platform engineer) but is NOT production quality. Re-run in CLO3D
    once licence is acquired — see CLO3D-SETUP.md.

USAGE:
    blender --background --python pipeline/garments/blender_cloth_sim.py

    Or from the Blender scripting tab (no arguments needed).

OUTPUT:
    assets/garments/tshirt-sprint1/tshirt_frame_001.obj
    assets/garments/tshirt-sprint1/tshirt_frame_002.obj
    ...
    assets/garments/tshirt-sprint1/tshirt_frame_030.obj

REQUIREMENTS:
    - Blender 4.x (tested on 4.1+)
    - Run from the project root:
        /Users/Jason/.openclaw/workspace/projects/fashion-tech/

FABRIC PARAMETERS (matched to CLO3D-SETUP.md spec):
    - Fabric weight: 150 g/m² cotton jersey
    - Quality: 10 steps/frame (balanced speed vs accuracy)
    - Stiffness tuned for soft cotton drape
"""

import bpy
import os
import sys
import math

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = "/Users/Jason/.openclaw/workspace/projects/fashion-tech"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "garments", "tshirt-sprint1")
FRAME_START = 1
FRAME_END = 30
FRAME_RATE = 24

# Cloth physics parameters — tuned for 150 g/m² cotton jersey
CLOTH_PARAMS = {
    "quality": 10,          # solver quality steps per frame
    "mass": 0.15,           # kg/m² — 150 g/m² → 0.15 kg/m²
    "tension_stiffness": 15.0,   # weft stretch resistance
    "compression_stiffness": 15.0,
    "shear_stiffness": 5.0,
    "bending_stiffness": 0.5,    # soft cotton bends easily
    "tension_damping": 25.0,
    "compression_damping": 25.0,
    "shear_damping": 25.0,
    "bending_damping": 0.5,
    "use_self_collision": True,
    "self_distance_min": 0.003,  # 3mm self-collision distance
    "collision_distance": 0.005, # 5mm avatar collision margin
}

# Walk cycle: simple hip sway + arm swing approximation
# Frame 1 = A-pose (static drape), Frames 2-30 = walk cycle
WALK_CYCLE_FRAMES = 29  # frames 2–30


# ---------------------------------------------------------------------------
# Scene Setup
# ---------------------------------------------------------------------------

def clear_scene():
    """Remove all default objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def set_frame_rate(fps: int):
    bpy.context.scene.render.fps = fps
    bpy.context.scene.frame_start = FRAME_START
    bpy.context.scene.frame_end = FRAME_END


# ---------------------------------------------------------------------------
# Avatar (Collision Object)
# ---------------------------------------------------------------------------

def create_avatar() -> bpy.types.Object:
    """
    Create a simplified humanoid torso as a collision object.
    In production, import the actual body scan mesh here.
    For Sprint 1: two cylinders (torso + neck) welded together.
    """
    # Torso
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.24,    # ~48cm chest circumference / 2π ≈ 0.24m
        depth=0.60,     # 60cm torso height
        location=(0, 0, 1.0),
        vertices=32,
    )
    torso = bpy.context.active_object
    torso.name = "Avatar_Torso"

    # Neck stub
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08,
        depth=0.12,
        location=(0, 0, 1.36),
        vertices=16,
    )
    neck = bpy.context.active_object
    neck.name = "Avatar_Neck"

    # Join torso + neck
    bpy.ops.object.select_all(action='DESELECT')
    torso.select_set(True)
    neck.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    avatar = bpy.context.active_object
    avatar.name = "Avatar"

    # Add collision modifier
    bpy.ops.object.modifier_add(type='COLLISION')
    avatar.collision.thickness_outer = CLOTH_PARAMS["collision_distance"]
    avatar.collision.thickness_inner = CLOTH_PARAMS["collision_distance"]
    avatar.collision.damping = 0.5
    avatar.collision.friction = 0.35  # cotton-on-skin friction

    return avatar


# ---------------------------------------------------------------------------
# T-Shirt Mesh
# ---------------------------------------------------------------------------

def create_tshirt_mesh() -> bpy.types.Object:
    """
    Build a t-shirt mesh from primitives:
      - Tube body (front + back panels joined)
      - Two sleeve tubes
    This is a low-fidelity placeholder. In production, import the
    pattern-constructed mesh from CLO3D or a proper 3D garment tool.
    """
    # Body tube
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.26,    # slightly larger than avatar — will drape inward
        depth=0.72,     # ~72cm length (size M)
        location=(0, 0, 1.0),
        vertices=32,
    )
    body = bpy.context.active_object
    body.name = "TShirt_Body"

    # Subdivide for better cloth simulation
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=4)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Left sleeve
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.09,
        depth=0.22,
        location=(-0.35, 0, 1.25),
        vertices=16,
    )
    bpy.context.active_object.rotation_euler = (0, math.radians(75), 0)
    sleeve_l = bpy.context.active_object
    sleeve_l.name = "TShirt_Sleeve_L"

    # Right sleeve
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.09,
        depth=0.22,
        location=(0.35, 0, 1.25),
        vertices=16,
    )
    bpy.context.active_object.rotation_euler = (0, math.radians(-75), 0)
    sleeve_r = bpy.context.active_object
    sleeve_r.name = "TShirt_Sleeve_R"

    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    sleeve_l.select_set(True)
    sleeve_r.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    tshirt = bpy.context.active_object
    tshirt.name = "TShirt"

    return tshirt


# ---------------------------------------------------------------------------
# Cloth Physics
# ---------------------------------------------------------------------------

def add_cloth_modifier(obj: bpy.types.Object):
    """Apply cloth physics modifier with cotton jersey parameters."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.modifier_add(type='CLOTH')
    cloth = obj.modifiers["Cloth"]
    cs = cloth.settings

    cs.quality = CLOTH_PARAMS["quality"]
    cs.mass = CLOTH_PARAMS["mass"]
    cs.tension_stiffness = CLOTH_PARAMS["tension_stiffness"]
    cs.compression_stiffness = CLOTH_PARAMS["compression_stiffness"]
    cs.shear_stiffness = CLOTH_PARAMS["shear_stiffness"]
    cs.bending_stiffness = CLOTH_PARAMS["bending_stiffness"]
    cs.tension_damping = CLOTH_PARAMS["tension_damping"]
    cs.compression_damping = CLOTH_PARAMS["compression_damping"]
    cs.shear_damping = CLOTH_PARAMS["shear_damping"]
    cs.bending_damping = CLOTH_PARAMS["bending_damping"]

    # Self-collision
    cs.use_self_collision = CLOTH_PARAMS["use_self_collision"]
    cs.self_distance_min = CLOTH_PARAMS["self_distance_min"]

    # Collision with avatar
    cs.collision_settings.use_collision = True
    cs.collision_settings.distance_min = CLOTH_PARAMS["collision_distance"]


# ---------------------------------------------------------------------------
# Walk Cycle (Simple)
# ---------------------------------------------------------------------------

def animate_avatar_walk(avatar: bpy.types.Object):
    """
    Add a simple walk cycle approximation to the avatar:
    - Light side-to-side hip sway
    - Slight forward lean oscillation
    Frame 1: A-pose (static), Frames 2-30: walk cycle
    """
    scene = bpy.context.scene

    # Frame 1: A-pose, no movement
    scene.frame_set(1)
    avatar.location = (0, 0, 0)
    avatar.keyframe_insert(data_path="location", frame=1)
    avatar.rotation_euler = (0, 0, 0)
    avatar.keyframe_insert(data_path="rotation_euler", frame=1)

    # Walk cycle: hip sway over 28 frames (frames 2–30, ~1 full cycle at 24fps)
    sway_amplitude = 0.025   # metres — subtle hip sway
    bob_amplitude = 0.015    # metres — vertical bounce
    lean_amplitude = 0.015   # radians — forward lean oscillation

    for frame in range(2, 31):
        scene.frame_set(frame)
        t = (frame - 2) / WALK_CYCLE_FRAMES  # 0.0 → 1.0
        angle = t * 2 * math.pi              # full cycle

        x_sway = sway_amplitude * math.sin(angle)
        z_bob = bob_amplitude * abs(math.sin(angle))
        y_lean = lean_amplitude * math.sin(angle * 0.5)

        avatar.location = (x_sway, 0, z_bob)
        avatar.keyframe_insert(data_path="location", frame=frame)
        avatar.rotation_euler = (y_lean, 0, 0)
        avatar.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Set interpolation to BEZIER for smooth motion
    if avatar.animation_data and avatar.animation_data.action:
        for fcurve in avatar.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'


# ---------------------------------------------------------------------------
# Bake Cloth Simulation
# ---------------------------------------------------------------------------

def bake_cloth_simulation(tshirt: bpy.types.Object):
    """Bake the cloth simulation for all frames."""
    bpy.ops.object.select_all(action='DESELECT')
    tshirt.select_set(True)
    bpy.context.view_layer.objects.active = tshirt

    # Set frame range
    bpy.context.scene.frame_start = FRAME_START
    bpy.context.scene.frame_end = FRAME_END

    # Free any existing bake
    bpy.ops.ptcache.free_bake_all()

    # Bake
    print("[blender_cloth_sim] Baking cloth simulation...")
    bpy.ops.ptcache.bake_all(bake=True)
    print("[blender_cloth_sim] Bake complete.")


# ---------------------------------------------------------------------------
# Export .obj Sequence
# ---------------------------------------------------------------------------

def export_obj_sequence(tshirt: bpy.types.Object, output_dir: str):
    """Export one .obj file per frame."""
    os.makedirs(output_dir, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    tshirt.select_set(True)
    bpy.context.view_layer.objects.active = tshirt

    scene = bpy.context.scene

    for frame in range(FRAME_START, FRAME_END + 1):
        scene.frame_set(frame)

        # Ensure modifiers are applied to get current deformed mesh
        bpy.ops.object.duplicate()
        dupe = bpy.context.active_object
        bpy.ops.object.convert(target='MESH')

        filename = f"tshirt_frame_{frame:03d}.obj"
        filepath = os.path.join(output_dir, filename)

        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            export_uv=True,
            export_normals=True,
            export_materials=False,
            forward_axis='NEGATIVE_Z',
            up_axis='Y',
            global_scale=1.0,
        )

        # Remove the duplicate
        bpy.ops.object.delete()

        # Re-select original
        tshirt.select_set(True)
        bpy.context.view_layer.objects.active = tshirt

        print(f"[blender_cloth_sim] Exported frame {frame:03d}/{FRAME_END}: {filename}")

    print(f"\n[blender_cloth_sim] ✓ {FRAME_END} frames exported to: {output_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Fashion Tech — Blender Cloth Sim (CLO3D Fallback)")
    print("Garment: Classic White T-Shirt, 150 g/m² cotton jersey")
    print(f"Output:  {OUTPUT_DIR}")
    print("=" * 60)

    clear_scene()
    set_frame_rate(FRAME_RATE)

    avatar = create_avatar()
    tshirt = create_tshirt_mesh()
    add_cloth_modifier(tshirt)
    animate_avatar_walk(avatar)
    bake_cloth_simulation(tshirt)
    export_obj_sequence(tshirt, OUTPUT_DIR)

    print("\n[blender_cloth_sim] Done.")
    print("⚠️  REMINDER: This is a CLO3D BLOCKER FALLBACK.")
    print("   Re-run simulation in CLO3D once licence is confirmed.")
    print("   See pipeline/garments/CLO3D-SETUP.md for exact settings.")


if __name__ == "__main__":
    main()
else:
    # When run from Blender's scripting tab or --python flag
    main()
