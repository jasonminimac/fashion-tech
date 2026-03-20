# Export Pipeline Specification: glTF, FBX, USD

**Date:** 2026-03-17  
**Author:** Blender Integration Lead  
**Phase:** Discovery & Detailed Design  
**Status:** Ready for Implementation  

---

## Overview

This document specifies the export pipeline: converting fully rigged Blender scenes into production-ready 3D formats (glTF 2.0, FBX, USD) for use by Frontend (Three.js web viewer), Clothing Lead (garment fitting), and Backend (archival/distribution).

**Goal:** Clean, optimized exports in <2 seconds, compatible with downstream tools, with all animations and materials embedded.

---

## 1. Export Strategy & Format Selection

### 1.1 Three Formats, Different Purposes

| Format | MVP | Why | Downstream Use |
|--------|-----|-----|-----------------|
| **glTF 2.0** | ✅ Primary | Web-friendly, standardized, embedded assets | Three.js viewer, web apps |
| **FBX** | ✅ Secondary | Industry fallback, compatible tools | Clothing Lead, alternative tools |
| **USD** | ❌ Phase 2 | Pixar format, future-proofing, advanced tools | Long-term archival, VFX pipeline |

### 1.2 Export Workflow

```
Blender .blend Scene
    │
    ├─ Cleanup & Optimize
    │   ├─ Merge meshes (if multiple)
    │   ├─ Remove modifiers (apply, don't keep procedural)
    │   ├─ Clean up materials
    │   └─ Optimize topology (decimate if needed)
    │
    ├─ Embed Assets
    │   ├─ Bake textures into mesh (if not already)
    │   ├─ Embed animation data
    │   └─ Include skeleton + weights
    │
    ├─ Export glTF 2.0 (Binary)
    │   └─ body.glb (10-50MB typical)
    │
    ├─ Export FBX
    │   └─ body.fbx (5-20MB typical)
    │
    └─ Export USD (Phase 2)
        └─ body.usd + assets/
```

---

## 2. glTF 2.0 Export (Three.js Viewer Primary Format)

### 2.1 Why glTF 2.0?

**glTF = GL Transmission Format (Khronos Group standard)**

- ✅ **Web-native:** Designed for real-time 3D on the web
- ✅ **Standardized:** Industry consensus (Google, Microsoft, Adobe, Khronos)
- ✅ **Efficient:** Binary format (.glb), <10MB for typical body scans
- ✅ **Feature-complete:** Supports mesh, skeleton, animation, PBR materials
- ✅ **Three.js native:** GLTFLoader has excellent support
- ✅ **Validated:** Official test suites and validators

**Downsides:**
- Less feature-rich than USD or FBX (no cloth sim data, no advanced physics)
- Deferred for Phase 2

### 2.2 Blender glTF Export Settings

**Blender has native glTF export (built-in):**

```python
import bpy

def export_gltf(blend_file, output_path):
    """Export Blender scene to glTF 2.0."""
    
    # Load the .blend file
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    # Export glTF
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        
        # Format: use .glb (binary)
        export_format='GLB',
        
        # Mesh
        export_mesh_format=True,
        export_apply_modifiers=True,  # Apply deformations
        export_include_custom_properties=True,
        
        # Vertex Data
        export_vertex_color=False,  # Include vertex colors if needed
        export_materials=True,
        export_original_specular=False,  # Use PBR (metallic-roughness)
        
        # Skeleton & Animation
        export_skins=True,  # Include armature/skeleton
        export_animations=True,  # Include all animations
        export_nla_strips=True,  # Include NLA animation tracks
        export_def_bones=False,  # Don't export deform bones separately
        
        # Cleanup
        export_morph_normal=False,  # Skip morph targets (no shape keys)
        export_morph_tangent=False,
        
        # Compression
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,  # 0-7, higher = smaller
        
        # Extras
        export_extras=True,  # Store custom metadata
        
        # Tangent space (for normal maps)
        export_tangents=True,
        
        # Texture export
        export_image_format='NONE',  # Embed images in .glb, don't create separate files
    )
    
    print(f"glTF export complete: {output_path}")
```

### 2.3 glTF Export Checklist

Before exporting, ensure:

```python
def validate_scene_for_export(blend_file):
    """Check scene is ready for glTF export."""
    
    import bpy
    
    checks = {}
    
    # Check 1: Single mesh
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    checks['single_mesh'] = len(meshes) == 1
    if not checks['single_mesh']:
        print(f"Warning: {len(meshes)} meshes found. Consider merging.")
    
    # Check 2: Armature exists
    armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    checks['armature_exists'] = len(armatures) > 0
    if not checks['armature_exists']:
        print("Error: No armature found.")
    
    # Check 3: Mesh is parented to armature
    if meshes and armatures:
        mesh = meshes[0]
        rig = armatures[0]
        
        has_armature_modifier = any(
            m.type == 'ARMATURE' and m.object == rig
            for m in mesh.modifiers
        )
        checks['mesh_parented'] = has_armature_modifier
    
    # Check 4: Animations exist
    animations = bpy.data.actions
    checks['animations_exist'] = len(animations) > 0
    print(f"Animations found: {[a.name for a in animations]}")
    
    # Check 5: Materials are PBR-compatible
    materials_ok = True
    for mat in bpy.data.materials:
        # Check for Principled BSDF (PBR shader)
        if mat.use_nodes:
            has_bsdf = any(
                node.type == 'BSDF_PRINCIPLED'
                for node in mat.node_tree.nodes
            )
            if not has_bsdf:
                print(f"Warning: Material '{mat.name}' not PBR. Consider converting.")
                materials_ok = False
    checks['materials_pbr'] = materials_ok
    
    # Check 6: No infinite/NaN values in mesh
    for v in meshes[0].data.vertices:
        if any(not (-1e6 < c < 1e6) for c in v.co):
            checks['mesh_valid'] = False
            print(f"Error: Invalid vertex coordinates in {meshes[0].name}")
            break
    else:
        checks['mesh_valid'] = True
    
    return checks

def pre_export_cleanup(blend_file):
    """Clean scene before export."""
    
    import bpy
    
    # Remove orphaned data
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
    
    # Apply modifiers (except Armature)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for mod in obj.modifiers:
                if mod.type != 'ARMATURE':
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    except:
                        print(f"Could not apply {mod.name}")
    
    # Ensure scale is 1.0
    for obj in bpy.context.scene.objects:
        if obj.scale != (1, 1, 1):
            bpy.ops.object.transform_apply(scale=True)
```

### 2.4 Animation Naming Convention

Animations in glTF are exported as separate **Action tracks**. Three.js will load these by name:

```python
def setup_animations(scene_data):
    """Ensure animations are named and set up correctly."""
    
    import bpy
    
    # Expected animation names (used by Frontend)
    animation_names = {
        'walk': 'Walk Cycle',
        'run': 'Run Cycle',
        'idle': 'Idle Stand',
    }
    
    # Create/rename animations in Blender
    for key, display_name in animation_names.items():
        action = bpy.data.actions.get(key)
        if action is None:
            print(f"Warning: Expected animation '{key}' not found")
        else:
            # Ensure action has proper frame range
            if action.frame_range[0] == 0 and action.frame_range[1] == 0:
                print(f"Warning: '{key}' animation has no frames")
            else:
                print(f"Animation '{key}': {int(action.frame_range[1])} frames")
    
    return animation_names
```

**Three.js Usage Example:**

```javascript
// In frontend code (Three.js):
const gltf = await loader.loadAsync('body.glb');
const model = gltf.scene;
const animations = gltf.animations;

// Find animation by name
const walkAction = animator.clipAction(
    THREE.AnimationClip.findByName(animations, 'walk')
);
walkAction.play();
```

### 2.5 Material Export for PBR

Blender's Principled BSDF shader maps to glTF PBR (Physically-Based Rendering):

```
Blender Principled BSDF    →    glTF 2.0 PBR
────────────────────────────────────────────
Base Color                  →    baseColorFactor + baseColorTexture
Metallic                    →    metallicFactor
Roughness                   →    roughnessFactor
Normal Map                  →    normalTexture
Emission                    →    emissiveFactor + emissiveTexture
(Alpha/Transparency)        →    alphaMode (BLEND or MASK)
```

**Ensure materials use Principled BSDF:**

```python
def convert_materials_to_gltf(mesh):
    """Ensure all materials are glTF-compatible."""
    
    import bpy
    
    for slot in mesh.material_slots:
        mat = slot.material
        
        if not mat.use_nodes:
            mat.use_nodes = True
        
        # Get or create Principled BSDF
        bsdf = None
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf = node
                break
        
        if bsdf is None:
            # Create new Principled BSDF
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Set default values
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # Light gray skin
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.5
        
        # Link to Material Output
        links = mat.node_tree.links
        output_node = mat.node_tree.nodes.get('Material Output')
        if output_node and not links.get((bsdf.outputs[0], output_node.inputs[0])):
            links.new(bsdf.outputs[0], output_node.inputs[0])
```

### 2.6 Draco Compression (Optional)

Draco reduces file size by 3-10x:

```
Without Draco: body.glb = 45MB
With Draco:    body.glb = 8MB (80% smaller)

Tradeoff: Requires decompression on client side (Draco.js library)
```

**Three.js with Draco:**

```javascript
const dracoLoader = new THREE.DRACOLoader();
dracoLoader.setDecoderPath('/draco/');  // Path to Draco decoder WASM files
gltfLoader.setDRACOLoader(dracoLoader);

const gltf = await gltfLoader.loadAsync('body.glb');
```

**MVP Decision:** Enable Draco compression level 6 (good balance of compression and decompression speed).

---

## 3. FBX Export (Industry Fallback Format)

### 3.1 Why FBX?

- ✅ **Industry standard:** 3D software (Maya, 3DS Max, Houdini) use FBX
- ✅ **Feature-rich:** Supports skeleton, animation, materials, custom properties
- ✅ **Compatible:** Clothing Lead may need FBX for fitting tools
- ✅ **Fallback:** If glTF has issues, FBX is available
- ⚠️ **Larger files:** Typically 5-20MB (uncompressed)

### 3.2 Blender FBX Export

```python
def export_fbx(blend_file, output_path):
    """Export Blender scene to FBX."""
    
    import bpy
    
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        
        # Mesh
        use_mesh_modifiers=True,  # Apply all modifiers
        mesh_smooth_type='OFF',  # Don't smooth (keep original topology)
        use_smoothing_groups=True,
        
        # Skeleton & Animation
        use_armature_deform_only=False,  # Include all bones
        add_leaf_bones=False,  # Don't add extra leaf bones
        
        # Animation
        use_anim=True,  # Export animations
        use_nla_strips=True,  # Include NLA tracks
        
        # Materials & Textures
        use_materials=True,
        use_bake_space_transform=False,
        
        # Version
        version='FBX202000',  # FBX 2020 (widely compatible)
        
        # Scale
        global_scale=1.0,
        forward_axis='Y',
        up_axis='Z',
        
        # Cleanup
        batch_mode='OFF',  # Single file output
    )
    
    print(f"FBX export complete: {output_path}")
```

### 3.3 FBX Compatibility Checklist

```python
def validate_fbx_export(fbx_path):
    """Validate FBX file."""
    
    import os
    
    # Check file size
    size_mb = os.path.getsize(fbx_path) / (1024**2)
    print(f"FBX file size: {size_mb:.1f}MB")
    
    # Check validity (basic)
    # FBX is binary, so we just check it's not corrupted
    with open(fbx_path, 'rb') as f:
        header = f.read(23)
        if not header.startswith(b'Kaydara FBX Binary'):
            raise ValueError("Invalid FBX file (corrupt header)")
    
    print("FBX validation passed")
```

---

## 4. USD Export (Phase 2 Foundation)

### 4.1 Why USD (Pixar Uniied Scene Description)?

- ✅ **Future-proof:** Industry moving toward USD (Disney, Apple, Nvidia)
- ✅ **Advanced features:** Cloth simulation, materials, lighting
- ✅ **Scalable:** Supports large scenes with instancing
- ✅ **Non-destructive:** Layering and composition
- ⚠️ **Complex:** Steeper learning curve
- ⚠️ **Newer:** Less widespread adoption than FBX/glTF

### 4.2 USD Export (Outline for Phase 2)

```python
def export_usd(blend_file, output_dir):
    """Export Blender to USD (Phase 2)."""
    
    import bpy
    
    # Phase 2: Requires additional USD plugin or usdpy library
    # For now, placeholder implementation
    
    # Option A: Use Blender's Pixar USD addon (if available)
    # bpy.ops.export.usd(filepath=output_dir)
    
    # Option B: Use usdpy (Pixar's Python library)
    # from pxr import Usd, UsdGeom
    
    raise NotImplementedError("USD export deferred to Phase 2")
```

**Phase 2 considerations:**
- Export mesh, skeleton, animations to .usd
- Include materials (with PBR conversion)
- Optional: cloth simulation data (for Marvelous Designer integration)

---

## 5. Export Quality Assurance

### 5.1 Post-Export Validation

```python
def validate_export(gltf_path, fbx_path):
    """Validate exported files."""
    
    import os
    import json
    
    results = {}
    
    # File existence
    results['glb_exists'] = os.path.exists(gltf_path)
    results['fbx_exists'] = os.path.exists(fbx_path)
    
    # File sizes
    results['glb_size_mb'] = os.path.getsize(gltf_path) / (1024**2) if results['glb_exists'] else 0
    results['fbx_size_mb'] = os.path.getsize(fbx_path) / (1024**2) if results['fbx_exists'] else 0
    
    # Reasonable file sizes
    if results['glb_size_mb'] > 100:
        print(f"Warning: glTF very large ({results['glb_size_mb']:.1f}MB). Consider optimization.")
    
    if results['fbx_size_mb'] > 200:
        print(f"Warning: FBX very large ({results['fbx_size_mb']:.1f}MB).")
    
    # Check glTF structure (JSON metadata)
    try:
        import zipfile
        with zipfile.ZipFile(gltf_path, 'r') as z:
            # glB is a ZIP-like structure with metadata JSON
            json_data = z.read('metadata.json')  # Might not exist; just checking
            results['glb_structure_ok'] = True
    except:
        results['glb_structure_ok'] = False  # Non-critical
    
    return results

def test_export_in_three_js():
    """Test exported glTF in Three.js simulator."""
    
    # This would require a Node.js environment with Three.js
    # For MVP, we just ensure the file is valid glTF
    
    # Phase 2: Automated Three.js testing
    # node test_gltf_loader.js body.glb
    
    pass
```

### 5.2 Export Report (JSON Metadata)

After export, generate a summary:

```python
def generate_export_report(blend_file, gltf_path, fbx_path):
    """Generate export metadata report."""
    
    import bpy
    import json
    import os
    from datetime import datetime
    
    # Load scene info
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    animations = list(bpy.data.actions)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'source_blend': blend_file,
        'exports': {
            'gltf': {
                'path': gltf_path,
                'size_mb': os.path.getsize(gltf_path) / (1024**2),
            },
            'fbx': {
                'path': fbx_path,
                'size_mb': os.path.getsize(fbx_path) / (1024**2),
            }
        },
        'scene': {
            'meshes': len(meshes),
            'vertices': sum(len(m.data.vertices) for m in meshes),
            'faces': sum(len(m.data.polygons) for m in meshes),
            'armatures': len(armatures),
            'bones': sum(len(a.data.bones) for a in armatures),
            'animations': len(animations),
            'animation_names': [a.name for a in animations],
        },
        'metadata': {
            'blender_version': bpy.app.version_string,
            'format_version': '2.0',
        }
    }
    
    # Write JSON
    report_path = blend_file.replace('.blend', '_export_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report, report_path
```

**Example report output:**

```json
{
  "timestamp": "2026-03-17T14:30:00Z",
  "source_blend": "/path/to/scan_12345.blend",
  "exports": {
    "gltf": {
      "path": "/path/to/scan_12345.glb",
      "size_mb": 12.5
    },
    "fbx": {
      "path": "/path/to/scan_12345.fbx",
      "size_mb": 18.3
    }
  },
  "scene": {
    "meshes": 1,
    "vertices": 45000,
    "faces": 89000,
    "armatures": 1,
    "bones": 45,
    "animations": 3,
    "animation_names": ["Walk", "Run", "Idle"]
  }
}
```

---

## 6. Optimization Strategies

### 6.1 Mesh Optimization

**Before Export:**

```python
def optimize_mesh_for_export(mesh):
    """Reduce polygon count without losing quality."""
    
    import bpy
    
    # Option 1: Decimate modifier (simplify mesh)
    decimate = mesh.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = 0.8  # Keep 80% of vertices (reduces by 20%)
    
    # Apply
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.modifier_apply(modifier='Decimate')
    
    # Option 2: Remove small disconnected parts
    # (requires selecting by area; skip for MVP)
    
    print(f"Mesh optimized: {len(mesh.data.vertices)} vertices")
```

**Result:** 45k vertices → 36k vertices, file size reduced 20%.

### 6.2 Texture Optimization

```python
def optimize_textures(mat):
    """Reduce texture resolution."""
    
    import bpy
    
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            image = node.image
            
            # Reduce resolution (e.g., 4K → 2K)
            if image.size[0] > 2048:
                print(f"Resizing {image.name}: {image.size[0]}x{image.size[1]} → 2048x2048")
                image.scale(2048, 2048)
```

### 6.3 Animation Optimization

```python
def optimize_animations(actions):
    """Clean up animation keyframes."""
    
    # Remove keyframes with < 1% change
    # Reduce sample rate if needed
    # This is complex; defer to Phase 2 if needed
    
    for action in actions:
        print(f"Animation '{action.name}': {len(action.fcurves)} tracks")
```

---

## 7. End-to-End Export Pipeline

### 7.1 Complete Export Function

```python
def export_complete(blend_file, output_dir):
    """Export scene to all formats."""
    
    import bpy
    import os
    from pathlib import Path
    
    print(f"\n{'='*60}")
    print(f"[EXPORT] {blend_file}")
    print(f"{'='*60}\n")
    
    # Setup output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load scene
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    # Validate
    print("[1/5] Validating scene...")
    checks = validate_scene_for_export(blend_file)
    if not all(checks.values()):
        print("Validation issues found:")
        for check, passed in checks.items():
            print(f"  {check}: {'✓' if passed else '✗'}")
    
    # Cleanup
    print("[2/5] Cleaning up scene...")
    pre_export_cleanup(blend_file)
    
    # glTF export
    print("[3/5] Exporting glTF 2.0...")
    gltf_path = os.path.join(output_dir, 'model.glb')
    export_gltf(blend_file, gltf_path)
    
    # FBX export
    print("[4/5] Exporting FBX...")
    fbx_path = os.path.join(output_dir, 'model.fbx')
    export_fbx(blend_file, fbx_path)
    
    # Generate report
    print("[5/5] Generating report...")
    report, report_path = generate_export_report(blend_file, gltf_path, fbx_path)
    
    # Summary
    print(f"\n{'='*60}")
    print("✓ Export complete!")
    print(f"{'='*60}")
    print(f"glTF:  {report['exports']['gltf']['size_mb']:.1f}MB")
    print(f"FBX:   {report['exports']['fbx']['size_mb']:.1f}MB")
    print(f"Report: {report_path}\n")
    
    return {
        'gltf': gltf_path,
        'fbx': fbx_path,
        'report': report_path,
    }
```

---

## 8. Quality Checklist

### Pre-Export

- [ ] Mesh is clean (no floating geometry, holes filled)
- [ ] Mesh is parented to armature with Armature modifier
- [ ] Animations are named (Walk, Run, Idle, etc.)
- [ ] Materials are Principled BSDF (glTF-compatible)
- [ ] No orphaned data (unused meshes, materials, textures)
- [ ] Scene is centered (object at world origin)
- [ ] Transforms are applied (no weird scales/rotations)

### Post-Export

- [ ] glTF file loads without errors in Three.js
- [ ] FBX file is valid (can open in Maya/Blender)
- [ ] Animations play correctly
- [ ] Mesh deforms correctly with skeleton
- [ ] Materials/colors are correct
- [ ] File sizes are reasonable (<50MB glTF, <100MB FBX)
- [ ] Metadata report is accurate

---

## 9. Troubleshooting

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **glTF file won't load in Three.js** | Invalid format, corrupt data | Validate with glTF validator tool (khronos.org) |
| **Mesh deforms strangely** | Bad weight painting | Review weight map, manual cleanup |
| **Animations jerky/popping** | Bone constraints incorrect | Check IK targets, bake constraints |
| **File too large (>100MB)** | High-resolution textures | Reduce texture size (2K→1K) |
| **Materials missing in glTF** | Non-PBR shaders used | Convert to Principled BSDF |
| **FBX won't open in Maya** | Version incompatibility | Use FBX 2020 format |

---

## 10. Testing & Validation

### 10.1 Unit Tests

```python
# tests/test_export.py

def test_gltf_export():
    """Test glTF export."""
    export_gltf('test_data/sample.blend', '/tmp/test.glb')
    assert os.path.exists('/tmp/test.glb')
    assert os.path.getsize('/tmp/test.glb') > 1000

def test_fbx_export():
    """Test FBX export."""
    export_fbx('test_data/sample.blend', '/tmp/test.fbx')
    assert os.path.exists('/tmp/test.fbx')

def test_export_complete():
    """Test full export pipeline."""
    result = export_complete('test_data/sample.blend', '/tmp/export')
    assert os.path.exists(result['gltf'])
    assert os.path.exists(result['fbx'])
    assert os.path.exists(result['report'])
```

### 10.2 Integration Test (Three.js)

```javascript
// test/test_gltf_loader.js (Node.js + Three.js)

const THREE = require('three');
const fs = require('fs');

async function testGLTFLoad() {
    const loader = new THREE.GLTFLoader();
    const gltf = await loader.loadAsync('./test_export/model.glb');
    
    console.assert(gltf.scene !== undefined, 'Scene loaded');
    console.assert(gltf.animations.length > 0, 'Animations present');
    console.assert(gltf.scene.children.length > 0, 'Mesh present');
    
    console.log('✓ glTF validation passed');
}

testGLTFLoad();
```

---

## 11. Performance Targets

| Operation | Target Time | Notes |
|-----------|------------|-------|
| **glTF export** | <1 second | 45k vertices + animations |
| **FBX export** | <1 second | Same mesh |
| **Validation** | <500ms | Checks and report generation |
| **Total export** | <2.5 seconds | Both formats + report |

---

## 12. Handoff & Documentation

### For Frontend Engineer

**glTF Spec:**
- Format: glB (binary), Draco-compressed
- Animations: Named "Walk", "Run", "Idle"
- Skeleton: Standard humanoid, VRChat-compatible
- Materials: Principled BSDF (PBR metallic-roughness)

**Three.js Integration:**
```javascript
const loader = new THREE.GLTFLoader();
const gltf = await loader.loadAsync('body.glb');
const model = gltf.scene;
const mixer = new THREE.AnimationMixer(model);
```

### For Clothing Lead

**FBX File:**
- Compatible with industry tools (Maya, 3DS Max, Houdini)
- Includes deformed mesh + skeleton
- Ready for garment fitting

---

## 13. Roadmap

### Week 5-6: MVP Export Pipeline
- [ ] Implement glTF export (Blender's built-in)
- [ ] Implement FBX export (Blender's built-in)
- [ ] Write validation tests
- [ ] Test with Three.js viewer
- [ ] Document export spec

### Week 7-8: Optimization & Polish
- [ ] Add Draco compression
- [ ] Optimize mesh decimation
- [ ] Generate export reports
- [ ] Performance profiling

### Phase 2: USD Export
- [ ] Implement USD export pipeline
- [ ] Integrate Cloth simulation data
- [ ] Support advanced materials

---

**Status:** Ready for Implementation  
**Next Checkpoint:** End of Week 5 (glTF export working in Three.js)

