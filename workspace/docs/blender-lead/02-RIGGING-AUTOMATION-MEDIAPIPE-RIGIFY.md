# Rigging Automation: MediaPipe + Rigify Integration

**Date:** 2026-03-17  
**Author:** Blender Integration Lead  
**Phase:** Discovery & Detailed Design  
**Status:** Ready for Implementation  

---

## Overview

This document details the automated rigging workflow: from scanned body mesh to fully rigged, animation-ready humanoid skeleton. We use MediaPipe Pose for landmark detection + Blender's Rigify addon for automated skeleton generation.

**Goal:** Turn raw mesh (10k-100k vertices) into a rigged armature in <1 second, with 90%+ automatic weight coverage.

---

## 1. Rigging Pipeline Overview

### 1.1 The Three-Stage Process

```
Stage 1: Input Mesh Analysis
├─ Import FBX (scanned body)
├─ Validate topology (check for holes, manifold)
├─ Analyze proportions (height, width ratios)
└─ Compute mesh center of mass and dimensions
        │
        ▼
Stage 2: Skeleton Generation
├─ Detect landmarks (MediaPipe: 33 body keypoints)
├─ Map landmarks to mesh surface (ray-casting)
├─ Refine positions (smoothing, constraint enforcement)
├─ Generate Rigify armature (automated)
└─ Create bone constraints (limits, locks)
        │
        ▼
Stage 3: Weight Painting
├─ Automatic proximity-based weights
├─ Validation (check weight distribution)
├─ Identify problem areas (high-error zones)
├─ Apply fixes (per-bone weight smoothing)
└─ Export clean weights
        │
        ▼
Output: Rigged .blend with animation-ready armature
```

### 1.2 Key Assumptions

- **Input:** T-pose or A-pose mesh (not random pose)
- **Mesh quality:** Relatively clean, watertight preferred (not critical)
- **Topology:** Body is roughly symmetric (left/right sides similar)
- **Body type:** Reasonable variation (adults, diverse builds; not extreme outliers in Week 1)

---

## 2. Stage 1: Mesh Analysis & Preparation

### 2.1 Import & Validation

```python
# Pseudocode: bpy-based mesh import
import bpy

def import_body_mesh(fbx_path):
    """Import scanned FBX, validate, return mesh object."""
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    # Find mesh object
    mesh_obj = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not mesh_obj:
        raise ValueError("No mesh found in FBX")
    
    mesh = mesh_obj[0]
    
    # Validation checks
    validate_mesh(mesh)
    
    # Apply transforms
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    return mesh

def validate_mesh(mesh):
    """Check mesh integrity."""
    assert len(mesh.data.vertices) > 1000, "Mesh too sparse (<1k vertices)"
    assert len(mesh.data.faces) > 100, "Mesh has no faces"
    
    # Check for non-manifold geometry (optional warning)
    non_manifold = [v for v in mesh.data.vertices if len(v.link_edges) < 2]
    if non_manifold:
        print(f"Warning: {len(non_manifold)} non-manifold vertices (may cause issues)")
```

**Key Steps:**
1. Clear scene (avoid conflicts)
2. Import FBX with proper scaling
3. Validate vertex/face count
4. Apply all transforms (critical for accurate landmark detection)
5. Ensure single mesh object (merge if needed)

### 2.2 Compute Body Dimensions & Pose Detection

```python
def analyze_body_proportions(mesh):
    """Extract height, width, and pose from mesh."""
    
    # Get bounding box
    bbox_min = Vector(mesh.bound_box[0])
    bbox_max = Vector(mesh.bound_box[7])
    dimensions = bbox_max - bbox_min
    
    # Height is Y axis (assuming +Y is up)
    height = dimensions.y
    
    # Width (shoulders) is X axis
    width = dimensions.x
    
    # Depth is Z axis
    depth = dimensions.z
    
    # Detect pose (T-pose vs A-pose)
    # T-pose: arms at 90°, legs straight
    # A-pose: arms at ~45°, legs slightly apart
    
    pose = detect_pose(mesh, height, width)
    
    print(f"Body Height: {height:.2f}m, Width: {width:.2f}m, Pose: {pose}")
    
    return {
        'height': height,
        'width': width,
        'depth': depth,
        'pose': pose,
        'aspect_ratio': width / height
    }

def detect_pose(mesh, height, width):
    """Infer pose from silhouette."""
    # Simple heuristic: measure hand positions relative to body center
    # T-pose: hands are roughly at shoulder height, wide apart
    # A-pose: hands are lower, narrower apart
    
    # For MVP, assume T-pose (most common input)
    return "T-pose"
```

**Why This Matters:**
- Height scaling: determines bone lengths
- Aspect ratio: informs if body is "normal", "broad", or "narrow"
- Pose detection: alerts us to non-standard input (future: add pose-correction preprocessing)

---

## 3. Stage 2: Skeleton Generation (MediaPipe + Rigify)

### 3.1 MediaPipe Pose Detection

MediaPipe detects 33 keypoints on the human body:

```
Keypoint Map (MediaPipe Pose 33):
 0: nose           17: left_ear          32: right_foot_index
 1: left_eye       18: right_ear
 2: right_eye      19: mouth_left        [Upper Body]
 3: left_ear       20: mouth_right        8: left_wrist       12: right_wrist
 4: right_ear      21: left_shoulder     11: left_elbow       15: right_elbow
 5: left_shoulder  22: right_shoulder    10: left_elbow       14: right_elbow
 6: right_shoulder 23: left_hip          9: left_wrist        13: right_wrist
 7: left_hip       24: right_hip
 8: right_hip      25: left_knee         [Lower Body]
 9: left_knee      26: right_knee        26: right_knee       28: right_ankle
10: right_knee     27: left_ankle        27: left_ankle       29: left_foot_index
11: left_ankle     28: right_ankle       ...
12: right_ankle    29: left_foot_index
13: left_foot_idx  30: right_foot_index
14: right_foot_idx 31: left_foot_index
                   32: right_foot_index
```

**Implementation Approach:**

```python
import mediapipe as mp
import cv2
import numpy as np

def detect_landmarks_from_mesh(mesh, render_to_image=False):
    """Use MediaPipe to detect body landmarks."""
    
    # Step 1: Render mesh from canonical view (front)
    # We need a 2D image to feed to MediaPipe
    
    image = render_mesh_to_image(mesh, width=512, height=512)
    # This uses Blender's Cycles/Eevee to render a silhouette
    
    # Step 2: Run MediaPipe Pose
    mp_pose = mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=2,  # High accuracy
        min_detection_confidence=0.7
    )
    
    results = mp_pose.process(image)
    
    if not results.pose_landmarks:
        raise ValueError("No pose detected (check image quality)")
    
    # Step 3: Extract 3D landmarks (MediaPipe outputs 3D in normalized space)
    landmarks_3d = []
    for landmark in results.pose_landmarks:
        # MediaPipe gives normalized [0,1] coordinates; scale to mesh space
        x = landmark.x * mesh.dimensions.x + mesh.location.x
        y = landmark.y * mesh.dimensions.y + mesh.location.y
        z = landmark.z * mesh.dimensions.z + mesh.location.z
        
        confidence = landmark.visibility
        landmarks_3d.append({
            'pos': Vector((x, y, z)),
            'confidence': confidence
        })
    
    return landmarks_3d

def render_mesh_to_image(mesh, width=512, height=512):
    """Render mesh silhouette for MediaPipe."""
    
    # Switch to camera view, render to image
    import bpy
    
    # Create render scene (simple silhouette)
    mat = bpy.data.materials.new(name="Silhouette")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (1, 1, 1, 1)  # White
    
    mesh.data.materials.append(mat)
    
    # Render
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    bpy.context.scene.render.filepath = "/tmp/silhouette.png"
    bpy.ops.render.render(write_still=True)
    
    # Load and return image
    import cv2
    image = cv2.imread(bpy.context.scene.render.filepath)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) / 255.0
```

**Why MediaPipe?**
- ✅ Fast (real-time on CPU)
- ✅ Accurate (trained on 400k images, diverse poses/body types)
- ✅ Free and open-source
- ✅ 33 keypoints cover full body
- ⚠️ Requires 2D image input (we render from 3D mesh)

### 3.2 Landmark-to-Surface Mapping

MediaPipe gives us 33 keypoints in 3D space, but they may float in space above the mesh. We need to **snap them to the nearest mesh surface** via ray-casting:

```python
def snap_landmarks_to_mesh(mesh, landmarks_3d):
    """Project landmarks onto mesh surface via raycasting."""
    
    from mathutils import Vector, Matrix
    import bmesh
    
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.normal_update()
    
    # Create BVH tree for fast ray-casting
    from mathutils.bvhtree import BVHTree
    bvh = BVHTree.FromBMesh(bm)
    
    snapped_landmarks = []
    
    for lm in landmarks_3d:
        pos = lm['pos']
        
        # Cast ray downward (along local Y, which is height)
        direction = Vector((0, -1, 0))
        
        # Find closest intersection
        location, normal, face_idx, distance = bvh.ray_cast(pos, direction)
        
        if location is not None:
            # Snap to surface
            snapped_pos = location
            confidence = lm['confidence']
        else:
            # Fallback: use original position (might be above surface)
            snapped_pos = pos
            confidence = lm['confidence'] * 0.7  # Lower confidence
        
        snapped_landmarks.append({
            'pos': snapped_pos,
            'confidence': confidence,
            'on_mesh': location is not None
        })
    
    bm.free()
    return snapped_landmarks
```

**Key Point:** This ensures skeleton bones are anchored to the actual mesh surface, not floating in space.

### 3.3 Bone Position Refinement

MediaPipe landmarks are sampled; we refine them to improve skeleton accuracy:

```python
def refine_bone_positions(snapped_landmarks, constraints):
    """Smooth and constrain landmark positions."""
    
    refined = snapped_landmarks.copy()
    
    # Constraint 1: Enforce bilateral symmetry
    # Left and right sides should mirror across X=0
    for i, lm in enumerate(refined):
        if 'left' in str(i):
            mirror_idx = str(i).replace('left', 'right')
            if mirror_idx in landmarks:
                # Average left and mirrored right
                left_pos = refined[i]['pos']
                right_pos = refined[mirror_idx]['pos']
                
                # Mirror right to match left (X coordinate negated)
                mirrored_right = Vector((
                    -right_pos.x,
                    right_pos.y,
                    right_pos.z
                ))
                
                # Blend (slightly bias toward left to preserve asymmetries)
                refined[i]['pos'] = left_pos.lerp(mirrored_right, 0.1)
    
    # Constraint 2: Enforce limb lengths (bones shouldn't stretch/compress too much)
    # E.g., upper arm + lower arm length should be consistent
    
    # Constraint 3: Smooth high-frequency noise (Gaussian blur in 3D)
    refined = smooth_landmarks_3d(refined, kernel_size=3)
    
    return refined

def smooth_landmarks_3d(landmarks, kernel_size=3):
    """Gaussian smoothing in 3D."""
    from scipy.ndimage import gaussian_filter1d
    
    positions = np.array([lm['pos'] for lm in landmarks])
    smoothed = gaussian_filter1d(positions, sigma=1.0, axis=0)
    
    for i, lm in enumerate(landmarks):
        lm['pos'] = Vector(smoothed[i])
    
    return landmarks
```

### 3.4 Rigify Armature Generation

Rigify is a Blender add-on that generates humanoid rigs from bone positions:

```python
def generate_rigify_armature(mesh, refined_landmarks):
    """Use Rigify to generate rig from landmark positions."""
    
    import bpy
    
    # Step 1: Create base armature with bones at landmark positions
    
    arm_data = bpy.data.armatures.new("Armature")
    arm_obj = bpy.data.objects.new("Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    
    # Enter edit mode to add bones
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create bones from landmarks (simplified bone hierarchy)
    bones = create_bone_hierarchy(arm_data, refined_landmarks)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Step 2: Apply Rigify to generate control rig
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Enable Rigify metarig: set bone layers and properties
    for bone in arm_obj.pose.bones:
        bone_name = bone.name
        
        # Rigify uses "Bone Type" property to identify bone roles
        if 'hips' in bone_name.lower():
            bone.rigify_type = 'hips'
        elif 'spine' in bone_name.lower():
            bone.rigify_type = 'spine'
        elif 'shoulder' in bone_name.lower():
            bone.rigify_type = 'shoulder'
        # ... etc for all bone types
    
    # Generate the rig (Rigify creates control bones and constraints)
    bpy.ops.pose.rigify_generate()
    
    # This creates a new armature called "Armature.rig" with FK/IK controls
    
    # Step 3: Parent mesh to new armature with Armature modifier
    
    mesh = bpy.context.scene.objects['body_mesh']
    rig = bpy.context.scene.objects['Armature.rig']  # Generated by Rigify
    
    modifier = mesh.modifiers.new(name="Armature", type='ARMATURE')
    modifier.object = rig
    
    # Parent mesh to bones
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.parent_set(type='ARMATURE')
    
    return rig
```

**Rigify Key Features:**
- Auto-generates FK (Forward Kinematics) controls for fine animation
- Auto-generates IK (Inverse Kinematics) for limbs (easier animation)
- Handles bone constraints and limits
- Production-quality rigs ready for animation

**Why Not Just Manual Bones?**
- Manual rigs lack IK controls (hard to animate)
- Rigify saves time and ensures consistency
- Industry-standard (used in animation studios)

---

## 4. Stage 3: Weight Painting (Automatic + Optional ML)

### 4.1 Automatic Proximity-Based Weights

For each vertex in the mesh, compute weights to all bones based on distance:

```python
def compute_automatic_weights(mesh, armature):
    """Generate vertex weights based on proximity to bones."""
    
    import bpy
    import numpy as np
    from mathutils import Vector
    
    # Get mesh vertices
    vertices = np.array([v.co for v in mesh.data.vertices])
    
    # Get bone positions (head and tail of each bone)
    bones = {}
    for bone in armature.data.bones:
        # Bone head and tail in world space
        head = armature.matrix_world @ bone.head_local
        tail = armature.matrix_world @ bone.tail_local
        bones[bone.name] = {'head': head, 'tail': tail}
    
    # Initialize weights (one weight per vertex per bone)
    num_verts = len(vertices)
    num_bones = len(bones)
    weights = np.zeros((num_verts, num_bones))
    
    # Compute distances and weights
    for v_idx, vertex in enumerate(vertices):
        distances = {}
        
        for b_idx, (bone_name, bone_data) in enumerate(bones.items()):
            # Distance from vertex to bone (line segment)
            head = bone_data['head']
            tail = bone_data['tail']
            
            dist = distance_point_to_line_segment(vertex, head, tail)
            distances[bone_name] = dist
        
        # Convert distances to weights (inverse distance weighting)
        # Closer bones get higher weights
        
        min_dist = min(distances.values())
        max_dist = max(distances.values())
        
        for b_idx, (bone_name, dist) in enumerate(distances.items()):
            # Normalize distance [0, 1]
            norm_dist = (dist - min_dist) / (max_dist - min_dist + 1e-6)
            
            # Inverse distance: closer = higher weight
            # Use Gaussian falloff: exp(-dist^2)
            weight = np.exp(-norm_dist**2 * 2.0)  # Sigma=0.7
            
            weights[v_idx, b_idx] = weight
        
        # Normalize weights to sum to 1 (soft-body deformation requirement)
        weight_sum = weights[v_idx].sum()
        if weight_sum > 0:
            weights[v_idx] /= weight_sum
    
    # Apply weights to vertex groups
    for bone_idx, (bone_name, _) in enumerate(bones.items()):
        # Create vertex group for this bone
        vgroup = mesh.vertex_groups.new(name=bone_name)
        
        # Assign weights
        for v_idx in range(num_verts):
            weight = weights[v_idx, bone_idx]
            if weight > 0.001:  # Only add if non-negligible
                vgroup.add([v_idx], weight, 'REPLACE')
    
    return weights

def distance_point_to_line_segment(point, line_start, line_end):
    """Compute distance from point to line segment."""
    from mathutils import Vector
    
    p = Vector(point)
    a = Vector(line_start)
    b = Vector(line_end)
    
    ab = b - a
    ap = p - a
    
    t = max(0, min(1, ap.dot(ab) / ab.dot(ab)))
    closest = a + t * ab
    
    return (p - closest).length
```

**Result:** Every vertex is assigned weights to multiple bones, with strength based on proximity. This is deterministic and fast.

### 4.2 Weight Quality Metrics & Problem Detection

```python
def validate_weights(mesh, armature):
    """Check weight distribution for issues."""
    
    issues = []
    
    for vertex in mesh.data.vertices:
        # Get all groups (bones) this vertex belongs to
        groups = vertex.groups
        
        # Calculate weight sum (should be ~1.0)
        weight_sum = sum(g.weight for g in groups)
        
        if abs(weight_sum - 1.0) > 0.01:
            issues.append({
                'vertex_idx': vertex.index,
                'issue': 'Weight sum != 1.0',
                'weight_sum': weight_sum
            })
        
        # Check for "bad" deformation (single dominant weight + outliers)
        if len(groups) > 0:
            weights = [g.weight for g in groups]
            max_weight = max(weights)
            
            if max_weight > 0.95:
                # Single bone controls this vertex (may cause hard edges)
                issues.append({
                    'vertex_idx': vertex.index,
                    'issue': 'Too dominant single bone',
                    'dominant_weight': max_weight
                })
        
        # Check for problematic areas (shoulders, hips, elbows)
        # These often have weight painting issues
        
        if groups:
            group_names = [armature.data.bones[g.group].name for g in groups]
            
            if any('shoulder' in name.lower() for name in group_names):
                # Shoulder area: check for smooth weight transitions
                pass  # Flag for manual review
    
    # Summarize
    print(f"Weight validation: {len(issues)} issues found")
    return issues

def identify_problem_areas(mesh, armature, issues):
    """Identify regions requiring manual cleanup."""
    
    problem_zones = {
        'shoulders': [],
        'elbows': [],
        'hips': [],
        'knees': [],
        'hands': []
    }
    
    for issue in issues:
        v_idx = issue['vertex_idx']
        v_pos = mesh.data.vertices[v_idx].co
        
        # Classify by position
        if v_pos.z > 0.15:  # High (shoulders/head)
            problem_zones['shoulders'].append(v_idx)
        elif abs(v_pos.x) > 0.08 and v_pos.z > 0.05:  # Arms/elbows
            problem_zones['elbows'].append(v_idx)
        elif v_pos.z < -0.15:  # Low (knees/ankles)
            problem_zones['knees'].append(v_idx)
        # ... etc
    
    return problem_zones
```

**Output:** List of vertices needing manual cleanup (shoulders, elbows, hips).  
**User Interaction:** Clothing Lead (or QA person) can manually paint these zones in Blender if needed.

### 4.3 ML-Guided Weight Priors (Optional, Phase 2)

For future iterations, we can train a neural network to predict weights:

```python
# Pseudocode for Phase 2
def predict_weights_ml(mesh, armature, reference_model):
    """Use trained ML model to predict weights."""
    
    # Encode mesh (point cloud or voxel grid)
    mesh_encoding = encode_mesh_to_voxel_grid(mesh, resolution=32)
    
    # Encode skeleton (bone positions and structure)
    skeleton_encoding = encode_skeleton(armature)
    
    # Predict weights (neural network)
    weights = reference_model.predict(mesh_encoding, skeleton_encoding)
    
    # Apply to vertex groups
    apply_weights_to_mesh(mesh, weights)
    
    return weights
```

**Training Data Needed:**
- ~20 reference scans with manually-curated high-quality weights
- Used to fine-tune a pre-trained model (transfer learning)
- Only worth it if automation quality (Stage 1) is insufficient

**MVP Decision:** Skip this for now. Proximity-based weights + manual cleanup are good enough.

---

## 5. Integration: Putting It Together

### 5.1 End-to-End Rigging Pipeline (Pseudocode)

```python
def automate_rigging_complete(fbx_path, output_blend_path):
    """Full pipeline: FBX → rigged .blend in one call."""
    
    import bpy
    
    # Stage 1: Import & Analyze
    print("[Stage 1] Importing and analyzing mesh...")
    mesh = import_body_mesh(fbx_path)
    proportions = analyze_body_proportions(mesh)
    print(f"  Height: {proportions['height']:.2f}m, Aspect: {proportions['aspect_ratio']:.2f}")
    
    # Stage 2a: Detect Landmarks
    print("[Stage 2a] Detecting landmarks with MediaPipe...")
    landmarks_raw = detect_landmarks_from_mesh(mesh)
    print(f"  Found {len(landmarks_raw)} landmarks")
    
    # Stage 2b: Snap to Mesh
    print("[Stage 2b] Snapping landmarks to mesh surface...")
    landmarks_snapped = snap_landmarks_to_mesh(mesh, landmarks_raw)
    on_mesh = sum(1 for lm in landmarks_snapped if lm['on_mesh'])
    print(f"  {on_mesh}/{len(landmarks_snapped)} landmarks on mesh")
    
    # Stage 2c: Refine & Rigify
    print("[Stage 2c] Refining positions and generating rig...")
    landmarks_refined = refine_bone_positions(landmarks_snapped, constraints={})
    armature = generate_rigify_armature(mesh, landmarks_refined)
    print(f"  Rig generated with {len(armature.bones)} bones")
    
    # Stage 3: Weight Painting
    print("[Stage 3] Computing automatic weights...")
    weights = compute_automatic_weights(mesh, armature)
    print(f"  Weights computed for {mesh.data.vertices.__len__()} vertices")
    
    # Validate
    print("[Validation] Checking weight quality...")
    issues = validate_weights(mesh, armature)
    problem_areas = identify_problem_areas(mesh, armature, issues)
    print(f"  {len(issues)} vertices flagged for manual review")
    
    # Save
    print("[Output] Saving to", output_blend_path)
    bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)
    
    print("[Done] Rigging complete!")
    return {
        'blend_path': output_blend_path,
        'bone_count': len(armature.bones),
        'issues': len(issues),
        'problem_areas': problem_areas
    }
```

### 5.2 Error Handling & Robustness

```python
def rigging_with_fallback(fbx_path, output_blend_path):
    """Rigging with error recovery."""
    
    try:
        result = automate_rigging_complete(fbx_path, output_blend_path)
        return result
    
    except MediaPipeDetectionError as e:
        print(f"MediaPipe detection failed: {e}")
        print("Falling back to manual landmark input")
        # TODO: User provides 3D positions manually (UI)
    
    except RigifyError as e:
        print(f"Rigify generation failed: {e}")
        print("Creating basic FK skeleton instead")
        # TODO: Simple forward-kinematics rig without IK controls
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

---

## 6. Testing & Validation

### 6.1 Unit Tests

```python
# tests/test_rigging.py

def test_mesh_import():
    """Test FBX import."""
    mesh = import_body_mesh("test_data/body_sample.fbx")
    assert mesh is not None
    assert len(mesh.data.vertices) > 1000

def test_landmark_detection():
    """Test MediaPipe landmark detection."""
    mesh = import_body_mesh("test_data/body_sample.fbx")
    landmarks = detect_landmarks_from_mesh(mesh)
    assert len(landmarks) == 33
    assert all(lm['confidence'] > 0 for lm in landmarks)

def test_rigify_generation():
    """Test Rigify armature creation."""
    mesh = import_body_mesh("test_data/body_sample.fbx")
    landmarks = detect_landmarks_from_mesh(mesh)
    armature = generate_rigify_armature(mesh, landmarks)
    assert len(armature.bones) > 20
    assert any('hip' in b.name.lower() for b in armature.bones)

def test_weight_painting():
    """Test automatic weight generation."""
    mesh = import_body_mesh("test_data/body_sample.fbx")
    armature = generate_rigify_armature(mesh, landmarks)
    weights = compute_automatic_weights(mesh, armature)
    assert weights.shape == (len(mesh.data.vertices), len(armature.bones))
    assert all(weights[i].sum() > 0.99 for i in range(len(weights)))

def test_end_to_end():
    """Test full pipeline."""
    result = automate_rigging_complete("test_data/body_sample.fbx", "/tmp/output.blend")
    assert result['bone_count'] > 20
    assert result['issues'] < 100  # Allow some issues for manual cleanup
```

### 6.2 Reference Test Cases

We'll use a set of reference body scans:

| Name | Type | Notes | Expected Issues |
|------|------|-------|-----------------|
| `average_male.fbx` | Average build | Standard test case | <50 |
| `tall_female.fbx` | Tall, slim | Tests height handling | <60 |
| `broad_male.fbx` | Broad shoulders | Tests width handling | <70 |
| `small_child.fbx` | Small proportions | Tests scaling | <80 |
| `large_build.fbx` | Large, round | Tests extreme proportions | <100 |

---

## 7. Known Limitations & Edge Cases

### 7.1 What Works Well

- ✅ Average adult bodies (most common)
- ✅ T-pose and A-pose inputs
- ✅ Diverse ethnicities and builds (MediaPipe is diverse)
- ✅ Semi-automated pipeline (handles most cases with <5min cleanup)

### 7.2 Edge Cases (Week 1 Limitations)

| Case | Issue | Workaround |
|------|-------|-----------|
| **Extreme heights** (very tall/short) | Bone lengths may be slightly off | Manual scaling in Rigify |
| **Extreme builds** (very round, muscular) | Weight painting may miss some areas | Manual touch-up (5-10 min) |
| **Non-standard pose** (sitting, lying down) | MediaPipe expects standing pose | Preprocess to standard pose first |
| **Clothing (jacket, long sleeves)** | Mesh silhouette obscured | Remove before scanning (user guidance) |
| **Very sparse mesh** (<5k verts) | Poor landmark accuracy | Require minimum mesh density |
| **Multiple bodies in scene** | MediaPipe detects only one | Pre-process to single mesh |

### 7.3 Phase 2 Improvements

- Advanced pose-space deformation for weight painting
- ML-guided weight priors (trained on reference scans)
- Support for non-standard poses (with pose-correction preprocessing)
- Facial rigging and expressions

---

## 8. Performance Targets & Benchmarks

| Stage | Operation | Target Time | Notes |
|-------|-----------|------------|-------|
| **1** | Mesh import | 100ms | FBX parsing |
| **2a** | MediaPipe detection | 200-500ms | Depends on mesh resolution |
| **2b** | Snap landmarks | 100ms | Ray-casting on BVH tree |
| **2c** | Rigify generation | 200-300ms | Blender armature creation |
| **3** | Weight painting | 100-200ms | Proximity-based computation |
| **Validation** | Checking weights | 50ms | Fast validation loop |
| **Output** | Save .blend | 500ms-2s | Depends on file size |
| **TOTAL** | Full pipeline | **<1.5 seconds** | MVP target |

**Optimization Notes:**
- MediaPipe is the slowest step; we render a 512x512 silhouette
- Can optimize by using lower resolution or simplified mesh for landmark detection
- Rigify + weight painting are fast in bpy

---

## 9. Documentation & Handoff

### 9.1 For Developers (Internal)

Each component will have:
- Docstrings (Google-style)
- Type hints (Python 3.10+)
- Unit tests
- Error handling
- Example usage

### 9.2 For Users (Clothing Lead, Frontend)

- **How to use the rigging tool:** Commands and file format
- **Output specification:** What the .blend file contains
- **Weight painting UI:** Manual cleanup instructions (if needed)
- **Common issues & fixes:** Troubleshooting guide

### 9.3 For Integration (Backend)

- **Metadata export:** Store mesh stats, rigging quality score in JSON
- **Versioning:** Track which Blender version, Rigify version used
- **Reproducibility:** Same input → same output (deterministic)

---

## 10. Next Steps

### Week 1-2: Setup & Foundation
- [ ] Set up Blender Python environment
- [ ] Create test mesh fixtures (5 reference bodies)
- [ ] Implement mesh import/validation
- [ ] Write unit tests for Stage 1

### Week 2-3: Landmark Detection & Rigify
- [ ] Integrate MediaPipe Pose
- [ ] Build landmark-to-surface snapping
- [ ] Integrate Rigify armature generation
- [ ] Test on 5 reference bodies

### Week 3-4: Weight Painting
- [ ] Implement proximity-based weight algorithm
- [ ] Build validation metrics
- [ ] Identify problem areas
- [ ] Write tests and documentation

### Week 4-5: Integration & Testing
- [ ] Combine all stages into one pipeline
- [ ] End-to-end testing
- [ ] Performance profiling
- [ ] Optimize for <1.5 second runtime

---

**Status:** Ready for Implementation  
**Next Checkpoint:** End of Week 2 (landmark detection + Rigify working)

