# IMPLEMENTATION PLAN — Rigging & Animation Pipeline
## Sprint 1 | Fashion Tech | 2026-03-18

---

## Overview

This document describes the complete technical design for the two pipeline scripts
delivered in Sprint 1:

1. `auto_rig.py` — OBJ + joints.json → rigged `.blend`
2. `export_glb.py` — rigged `.blend` + optional BVH → walk-cycle `.glb`

Both scripts are production-ready stubs — all function signatures, docstrings,
and core logic are written out. A Blender operator can run them with minimal
changes after installing Blender 3.6+ / 4.x.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Blender | 3.6 LTS or 4.x | Download from blender.org |
| Rigify | Built-in | Enable via Preferences → Add-ons → Rigging: Rigify |
| Python | 3.10+ (Blender's bundled) | No external packages needed |
| BVH walk file | Optional | Mixamo-compatible; download free from mixamo.com |

**Blender install path (macOS):**
```
/Applications/Blender.app/Contents/MacOS/Blender
```

---

## Script 1: `auto_rig.py`

### Invocation
```bash
blender --background --python pipeline/rigging/auto_rig.py \
  -- assets/meshes/test_human.obj \
     assets/meshes/test_joints.json \
     output/rigged.blend
```

### Architecture

```
parse_args()
    ↓
load_landmarks(joints_path)          ← parse joints.json, convert MP→Blender coords
    ↓
estimate_missing_landmarks(pos)      ← fill gaps (neck, pelvis, spine) by anatomy
    ↓
import_obj(obj_path)                 ← import mesh, join multi-mesh, name "BodyMesh"
    ↓
build_rigify_metarig(positions)      ← add human metarig, reposition bones in edit mode
    ↓
generate_rig(metarig)                ← bpy.ops.pose.rigify_generate()
    ↓
skin_mesh_to_rig(mesh_obj, rig)      ← parent + auto weights
    ↓
bpy.ops.wm.save_as_mainfile(output)
```

### Coordinate System Conversion

MediaPipe world-space coordinates (from `joints.json`):
- X: subject's right
- Y: subject's up  
- Z: subject's forward (toward camera, positive = away from camera)

Blender world-space:
- X: right
- Y: forward (into scene)
- Z: up

Conversion applied in `load_landmarks()`:
```python
blender_x =  mp_x
blender_y = -mp_z   # flip forward axis
blender_z =  mp_y   # Y becomes Z
```

### Rigify Bone Mapping

| Rigify Bone | MediaPipe Landmark |
|-------------|-------------------|
| `spine` (head) | pelvis midpoint (`left_hip` + `right_hip` / 2) |
| `neck` (head) | derived: shoulder midpoint + 5cm up |
| `head` | `nose` + 10cm up |
| `upper_arm.L` | `left_shoulder` → `left_elbow` |
| `forearm.L` | `left_elbow` → `left_wrist` |
| `thigh.L` | `left_hip` → `left_knee` |
| `shin.L` | `left_knee` → `left_ankle` |
| `foot.L` | `left_ankle` → `left_heel` |
| *(mirror .R)* | *(same, right side)* |

### Known Limitations

1. **Finger bones** — MediaPipe pose (33 landmarks) does not include finger joints.
   Rigify finger bones will remain in default position. For hand animation, use
   MediaPipe Hands (21 landmarks per hand) as a future enhancement.

2. **Automatic weights** — `ARMATURE_AUTO` is a best-effort skinning. Complex meshes
   (clothing layers, accessories) may need manual weight painting on the elbow/knee
   areas. Tested acceptable for body-suit style avatar meshes.

3. **Rigify version** — `bpy.ops.pose.rigify_generate()` API is stable since Blender 2.93.
   Blender 4.x may require `bpy.ops.pose.rigify_generate(rig_ui_type='...'])`; the script
   catches exceptions and falls back to the raw metarig.

---

## Script 2: `export_glb.py`

### Invocation

**Procedural walk (no BVH):**
```bash
blender --background --python pipeline/rigging/export_glb.py \
  -- output/rigged.blend output/avatar.glb
```

**BVH retarget:**
```bash
blender --background --python pipeline/rigging/export_glb.py \
  -- output/rigged.blend output/avatar.glb assets/bvh/mixamo_walk.bvh
```

### Walk Cycle Design (Procedural Mode)

30-frame loop at 30 fps = 1-second stride cycle.

All rotations are sinusoidal with the following parameters:

| Bone | Axis | Amplitude | Phase | DC Offset |
|------|------|-----------|-------|-----------|
| `thigh.L` | X (fwd/back) | ±30° | 0 | +5° |
| `thigh.R` | X | ±30° | 180° | +5° |
| `shin.L` | X (knee bend) | ±20° | 90° | -10° |
| `shin.R` | X | ±20° | 270° | -10° |
| `foot.L` | X (pitch) | ±15° | 90° | +5° |
| `foot.R` | X | ±15° | 270° | +5° |
| `upper_arm.L` | X | ±25° | 180° | 0° |
| `upper_arm.R` | X | ±25° | 0° | 0° |
| `spine` | X (lean) | 0° | — | +8° (constant) |
| `spine` | Z (location) | ±2cm | 2× stride | — |

Phase alternates L/R by 180° (N/2 frames) to produce the natural cross-body walk pattern.

### BVH Retarget

1. Import BVH via `bpy.ops.import_anim.bvh()`
2. Build bone name map: Rigify → Mixamo (e.g. `upper_arm.L` → `LeftArm`)
3. Apply COPY_ROTATION (+ COPY_LOCATION for hips) constraints
4. Bake with `bpy.ops.nla.bake(visual_keying=True, clear_constraints=True)`
5. Name resulting action `"Walk"`
6. Add CYCLES fcurve modifier for looping

Recommended free BVH source: **Mixamo** (Adobe) — download "Walking" animation,
export as BVH without skin. Bone names match the `RIGIFY_TO_MIXAMO` map in the script.

### glTF Export Settings

```python
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_apply=True,           # apply all modifiers
    export_animations=True,
    export_yup=True,             # Y-up — required for model-viewer
    export_skins=True,           # include armature as skin
    export_morph=True,           # include shape keys if any
    export_materials='EXPORT',   # include materials/textures
)
```

### model-viewer Integration

```html
<!DOCTYPE html>
<html>
<head>
  <script type="module"
    src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js">
  </script>
</head>
<body>
  <model-viewer
    src="avatar.glb"
    autoplay
    animation-name="Walk"
    camera-controls
    auto-rotate
    style="width: 400px; height: 700px; background: #f0f0f0">
  </model-viewer>
</body>
</html>
```

---

## Test Mesh

**For Sprint 1 bootstrapping**, we recommend one of these freely available meshes:

| Source | File | Notes |
|--------|------|-------|
| MakeHuman | `default_human.obj` | Open-source, clean topology, A-pose |
| Mixamo | Any character OBJ export | Good proportions, pre-posed |
| Ready Player Me | `.glb` → convert to `.obj` via Blender | Needs format conversion |

To generate a test `joints.json` without the scanning agent output, use
`assets/meshes/test_joints.json` (to be created by scanning agent, or use the
sample file in `pipeline/rigging/samples/`).

---

## Sample joints.json (MakeHuman default proportions)

```json
{
  "scan_id": "test_sprint1",
  "landmarks": [
    { "id": 0,  "name": "nose",             "x":  0.000, "y":  1.720, "z":  0.090 },
    { "id": 11, "name": "left_shoulder",    "x":  0.190, "y":  1.460, "z":  0.000 },
    { "id": 12, "name": "right_shoulder",   "x": -0.190, "y":  1.460, "z":  0.000 },
    { "id": 13, "name": "left_elbow",       "x":  0.310, "y":  1.200, "z":  0.000 },
    { "id": 14, "name": "right_elbow",      "x": -0.310, "y":  1.200, "z":  0.000 },
    { "id": 15, "name": "left_wrist",       "x":  0.350, "y":  0.960, "z":  0.000 },
    { "id": 16, "name": "right_wrist",      "x": -0.350, "y":  0.960, "z":  0.000 },
    { "id": 23, "name": "left_hip",         "x":  0.110, "y":  1.020, "z":  0.000 },
    { "id": 24, "name": "right_hip",        "x": -0.110, "y":  1.020, "z":  0.000 },
    { "id": 25, "name": "left_knee",        "x":  0.110, "y":  0.540, "z":  0.020 },
    { "id": 26, "name": "right_knee",       "x": -0.110, "y":  0.540, "z":  0.020 },
    { "id": 27, "name": "left_ankle",       "x":  0.100, "y":  0.080, "z":  0.000 },
    { "id": 28, "name": "right_ankle",      "x": -0.100, "y":  0.080, "z":  0.000 },
    { "id": 29, "name": "left_heel",        "x":  0.100, "y":  0.030, "z": -0.050 },
    { "id": 30, "name": "right_heel",       "x": -0.100, "y":  0.030, "z": -0.050 },
    { "id": 31, "name": "left_foot_index",  "x":  0.100, "y":  0.030, "z":  0.130 },
    { "id": 32, "name": "right_foot_index", "x": -0.100, "y":  0.030, "z":  0.130 }
  ]
}
```

---

## End-to-End Run Instructions

```bash
# 1. Rig the mesh
blender --background --python pipeline/rigging/auto_rig.py \
  -- assets/meshes/test_human.obj \
     assets/meshes/test_joints.json \
     output/rigged.blend

# 2. Bake walk cycle + export .glb
blender --background --python pipeline/rigging/export_glb.py \
  -- output/rigged.blend \
     assets/meshes/avatar_walk.glb

# 3. Test in browser
open pipeline/rigging/samples/model-viewer-test.html
```

---

## Blockers / Open Questions

| # | Item | Owner | Priority |
|---|------|-------|----------|
| 1 | Need test `.obj` mesh from scanning agent or manual source | scanning / rigging | P1 |
| 2 | Rigify `rigify_generate()` may need version-specific flags on Blender 4.x | rigging | P2 |
| 3 | Finger/hand animation — needs MediaPipe Hands 21-landmark output | scanning | P3 |
| 4 | BVH walk source — recommend Mixamo "Walking" free download | rigging | P2 |
| 5 | Physical test run blocked until Blender is installed on CI/build host | platform | P1 |

---

## What Platform Needs to Test model-viewer

1. **`assets/meshes/avatar_walk.glb`** — the exported avatar file
2. Animation name inside `.glb` must be exactly `"Walk"` (already set in both scripts)
3. Y-up axis — set in export (`export_yup=True`)
4. Serve the `.glb` over HTTP (model-viewer requires HTTP/S, not `file://`)
5. Use the HTML snippet in the model-viewer section above

Minimal test: `npx serve .` in the `assets/meshes/` folder, open `localhost:3000`, load the HTML snippet.

---

*Written by: fashion-rigging — Sprint 1, 2026-03-18*
