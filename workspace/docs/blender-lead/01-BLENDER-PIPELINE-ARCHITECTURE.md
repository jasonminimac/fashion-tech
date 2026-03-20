# Blender Integration Pipeline Architecture

**Date:** 2026-03-17  
**Author:** Blender Integration Lead  
**Phase:** Discovery & Architecture  
**Status:** Ready for Implementation  

---

## Overview

The Blender Integration Pipeline automates the complete rigging and export workflow for scanned 3D body models. This document defines the architecture, data flow, component responsibilities, and technical decisions for Phase 1 MVP.

**Goal:** Transform raw scanned body meshes → fully rigged, animation-ready 3D models in Blender → clean glTF/FBX/USD exports.

---

## 1. System Architecture

### 1.1 High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fashion Tech Pipeline                         │
└─────────────────────────────────────────────────────────────────┘

[3D Scanning Lead]              [Blender Integration Lead]
       │                               │
       ├─ Raw LiDAR/Point Cloud       │
       ├─ Mesh Processing             │
       └─ Normalized FBX              │
                                      │
                    ┌─────────────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Blender Automation         │
        │  Framework (Python/bpy)     │
        └─────────────────────────────┘
                    │
        ┌───────────┬───────────┬───────────┐
        │           │           │           │
        ▼           ▼           ▼           ▼
    ┌──────┐  ┌──────────┐  ┌────────┐  ┌────────┐
    │Import│  │Rigging   │  │Weight  │  │Export  │
    │Mesh  │→ │Skeleton  │→ │Paint   │→ │glTF/   │
    │      │  │(MediaPipe│  │(Semi-  │  │FBX/USD │
    │      │  │+Rigify)  │  │Auto)   │  │        │
    └──────┘  └──────────┘  └────────┘  └────────┘
        │           │           │           │
        └───────────┴───────────┴───────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │ Output: Rigged .blend File  │
        │ + Exported Assets (glTF)    │
        └─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    [Animation]           [Clothing Lead]
    (Mixamo Retarget)     (Garment Fitting)
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Frontend (Three.js)        │
        │  Web Viewer & Outfit Builder│
        └─────────────────────────────┘
```

### 1.2 Component Architecture

```
Blender Integration Framework
├── Core Engine (bpy automation)
│   ├── Scene initialization
│   ├── Import/export management
│   ├── Batch processing orchestration
│   └── Error handling & logging
│
├── Rigging Pipeline
│   ├── Mesh import & validation
│   ├── Skeleton generation (MediaPipe + Rigify)
│   ├── Joint position detection & refinement
│   └── Armature creation & parenting
│
├── Weight Painting
│   ├── Automatic weight calculation (proximity-based)
│   ├── ML-based priors (optional enhancement)
│   ├── Manual correction interface
│   └── Validation & quality checks
│
├── Animation System
│   ├── Animation import (FBX/BVH)
│   ├── Retargeting (skeleton mapping)
│   ├── Bone constraint setup
│   └── NLA (Non-Linear Animation) management
│
├── Export Pipeline
│   ├── glTF 2.0 export (Three.js compatible)
│   ├── FBX export (industry standard)
│   ├── USD export (Pixar format, future)
│   ├── Material/texture handling
│   └── Animation embedding
│
└── Scene Templates
    ├── Lighting setup
    ├── Camera positioning
    ├── Default animation stack
    └── Material library
```

---

## 2. Phase 1 MVP Scope

### 2.1 In Scope (Week 1-8)

1. **Blender Automation Framework**
   - Python/bpy scripting engine
   - Batch processing for multiple scans
   - Clear error handling and logging
   - Integrated unit testing

2. **Rigging Pipeline (MediaPipe + Rigify)**
   - Detect 33 body landmarks from mesh topology
   - Generate humanoid skeleton using Rigify
   - Handle diverse body types (height, build variations)
   - Confidence scoring for rigging quality

3. **Weight Painting (Semi-Automated)**
   - Automatic weight calculation based on proximity to bones
   - ML-guided priors (optional: pre-trained weights from reference bodies)
   - Manual refinement UI for problem areas (shoulders, hips, hands)
   - Quality metrics (weight distribution validation)

4. **Animation Integration**
   - Import Mixamo animations (FBX format)
   - Skeleton mapping (Mixamo → custom skeleton)
   - Retargeting via bone constraints and baking
   - Basic NLA setup (default walk + idle loops)

5. **Export Pipeline**
   - glTF 2.0 export (target: Three.js web viewer)
   - FBX export (fallback for industry tools)
   - Clean geometry (merged shapes, optimized topology)
   - Embedded animations in glTF

6. **Scene Template**
   - Standard lighting (3-point setup)
   - Camera position (T-pose, front view)
   - Material setup (basic skin shader)
   - Default animation stack (walk cycle loop)

7. **Success Criteria**
   - ✅ End-to-end automation: scan → rigged model in <1 second
   - ✅ glTF exports playable in Three.js viewer without modification
   - ✅ Works with body scans from 3D Scanning Lead (diverse body types)
   - ✅ Weight painting quality acceptable for garment fitting (manual cleanup <5 min per scan)

### 2.2 Out of Scope (Phase 2+)

- Advanced cloth simulation integration (use Blender's built-in; Marvelous Designer integration deferred)
- Complex facial rigging or expressions
- Muscle/bulge shape key generation
- Advanced morphs (extreme sizes, custom proportions)
- Real-time preview server (Blender as a service)
- Mobile integration

---

## 3. Technical Decisions & Rationale

### 3.1 Why Blender + Python/bpy?

| Decision | Rationale | Trade-offs |
|----------|-----------|-----------|
| **Blender 3.6+ (LTS)** | Stable, free, fully scriptable, industry standard | GPL v2 (open-source requirement if we ship tools) |
| **Python API (bpy)** | Full control over Blender internals, automation-friendly | Requires headless/scripting knowledge, slower than C plugins |
| **Rigify addon** | Industry-standard armature generation, works with diverse meshes | Requires parameter tuning per body type, not AI-based |
| **MediaPipe Pose** | 33 body landmarks, real-time CPU inference, free | Requires mesh topology analysis for bone placement |

**Alternative Considered:** Adobe Mixamo's auto-rigging (cloud-based, paid per-rig) vs. our DIY approach.  
**Decision Rationale:** Mixamo is fast but expensive at scale. Our ML-guided approach with Rigify gives us control and lower cost.

### 3.2 Skeleton Structure (Human IK Compliant)

We'll use a standard humanoid skeleton that aligns with **VRChat's humanoid spec** (industry-standard):

```
Armature
├── Hips (root bone)
├── Spine
│   ├── Chest
│   │   ├── Neck
│   │   │   └── Head
│   │   └── Shoulders (L/R)
│   │       └── Upper Arm (L/R)
│   │           └── Lower Arm (L/R)
│   │               └── Hand (L/R)
│   └── Hip (L/R)
│       └── Upper Leg (L/R)
│           └── Lower Leg (L/R)
│               └── Foot (L/R)
└── [IK chains for arms/legs if needed]
```

**Rationale:**
- Compatible with Mixamo animations (standard humanoid spec)
- Supports inverse kinematics (IK) for future animation blending
- Works with garment-fitting algorithms (clothing expects this bone structure)

### 3.3 Weight Painting Strategy

**Tier 1 (Automatic):** Proximity-based soft weights
- For each vertex, distribute weights to nearest bones (weighted by distance)
- Fast, deterministic, works for most of mesh

**Tier 2 (ML-Guided, Optional):** Pre-trained weight priors
- Train on reference scans with high-quality manual weights
- Use neural network to predict weights for new scans
- Requires ~20 reference bodies to train (future iteration)

**Tier 3 (Manual):** Interactive refinement
- User identifies problem areas (shoulders, hips, fingers)
- Paint fine adjustments directly in Blender
- Estimate: <5 min per scan for acceptable quality

**Why This Approach:**
- Fully automatic rigging rarely produces perfect weights
- Manual-only is too slow at scale
- ML approach requires training data we don't have yet (Phase 2)
- Hybrid keeps MVP timeline realistic

### 3.4 Animation Retargeting Approach

**Goal:** Map Mixamo animations (standard humanoid) → custom skeleton

**Method 1: Bone Mapping + Baking**
```
Mixamo Skeleton          Custom Skeleton
    │                          │
    ├─ Armature              ├─ Armature
    │  ├─ Hip                │  ├─ Hips
    │  ├─ Spine              │  ├─ Spine
    │  └─ LeftArm      →      │  ├─ LeftUpperArm
    │                         │  └─ LeftLowerArm
    │
Step 1: Create bone name mapping dictionary
Step 2: Copy animation from Mixamo to custom bones
Step 3: Apply constraints (IK if needed) and bake
Step 4: Cleanup (remove Mixamo armature)
```

**Method 2: IK Constraint Transfer (Future)**
- More robust to skeleton differences
- Handles arm/leg proportions automatically
- Requires IK setup (chains, pole targets)

**MVP Decision:** Method 1 (simpler, sufficient for walk/run cycles with consistent proportions)

---

## 4. Data Structures & Specifications

### 4.1 Input: Scanned Body Mesh

**Source:** 3D Scanning Lead  
**Format:** FBX (Autodesk FBX 2020 or newer)  
**Geometry Specs:**
- Mesh: T-pose or A-pose, cleaned, single mesh or simple hierarchy
- Vertex count: 10k-100k triangles (typical for body scans)
- Topology: Watertight preferred (no holes), symmetric preferred
- Materials: Basic (single skin material OK; full PBR optional)
- Armature: None (we generate it)

**Metadata (JSON alongside FBX):**
```json
{
  "scan_id": "scan_12345",
  "user_height_cm": 175,
  "body_type": "average",
  "pose": "T-pose",
  "processing_status": "cleaned",
  "confidence_score": 0.92,
  "timestamp": "2026-03-17T10:30:00Z"
}
```

### 4.2 Output: Rigged Blender Scene

**Primary Output:** `.blend` file (Blender native)

```
scene
├── Mesh
│   ├── body_mesh (vertices, faces, materials)
│   └── modifiers
│       ├── Armature (deform)
│       └── [optional: Mirror, Subdivision, etc.]
│
├── Armature
│   ├── Root: Hips
│   ├── Bone structure (33+ bones)
│   ├── IK targets (if used)
│   └── Constraints (limit rotation, pole targets)
│
├── Animation
│   ├── Walk cycle (60 frames @ 30fps)
│   ├── Run cycle (60 frames @ 30fps)
│   └── Idle (looping stand, weight shifts)
│
├── Materials
│   ├── Skin (Principled BSDF shader)
│   └── [optional: eyes, nails, etc.]
│
├── Lighting
│   ├── Key light (main)
│   ├── Fill light (shadow reduction)
│   └── Back light (rim lighting)
│
└── Camera
    └── Front view (T-pose framing)
```

**Secondary Outputs (Exported):**
- `body.glb` (glTF 2.0 binary, includes mesh + skeleton + animations)
- `body.fbx` (FBX 2020, compatibility format)
- `body.usd` (USD, future; Pixar format for advanced tools)

### 4.3 Export Specification: glTF 2.0

**Three.js Compatibility Checklist:**

| Feature | Required | Notes |
|---------|----------|-------|
| **Format** | glB (binary) | Smaller, faster loading |
| **Mesh Geometry** | ✅ Yes | Vertices, faces, normals, UVs |
| **Skeleton** | ✅ Yes | Bones, hierarchy, inverse bind matrices |
| **Animations** | ✅ Yes | Walk, run, idle (separate tracks) |
| **Materials** | ✅ Yes | Principled BSDF → glTF PBR metallic-roughness |
| **Textures** | ✅ Yes | Embedded or referenced (color, normal, roughness) |
| **Morphs/Shape Keys** | ❌ No | Out of scope (Phase 2) |
| **Vertex Colors** | ✅ Optional | For quick shading if no textures |
| **Custom Metadata** | ✅ Optional | Store scan_id, user_height in glTF extras |

---

## 5. Implementation Roadmap

### Week 1-2: Foundation
- [ ] Set up Blender Python environment and bpy API
- [ ] Create base framework (scene init, import/export, logging)
- [ ] Write unit tests (test fixtures with sample meshes)
- [ ] Set up CI/CD pipeline for batch processing

### Week 2-3: Rigging (MediaPipe + Rigify)
- [ ] Integrate MediaPipe Pose for landmark detection
- [ ] Build skeleton generation (Rigify automation)
- [ ] Handle diverse body types (scale, proportion adjustments)
- [ ] Test with 5+ reference scans

### Week 3-4: Weight Painting
- [ ] Implement proximity-based automatic weights
- [ ] Build validation metrics (weight distribution checks)
- [ ] Create test suite with manual reference weights
- [ ] Assess need for ML priors (feedback loop)

### Week 4-5: Animation Retargeting
- [ ] Download/license Mixamo animations (walk, run, idle)
- [ ] Build bone mapping system
- [ ] Implement animation retargeting (baking)
- [ ] Test with retargeted animations

### Week 5-6: Export Pipeline
- [ ] Build glTF 2.0 exporter (leverage Blender's built-in)
- [ ] Build FBX exporter with cleanup
- [ ] Validate with Three.js web viewer
- [ ] Add material/texture export

### Week 6-7: Scene Templates & Integration
- [ ] Build default scene template (lighting, camera, materials)
- [ ] Integrate with 3D Scanning Lead's pipeline
- [ ] End-to-end testing (scan → rigged → exported)
- [ ] Performance profiling and optimization

### Week 7-8: Refinement & Documentation
- [ ] Bug fixes and edge case handling
- [ ] Performance tuning (target: <1 sec rigging time)
- [ ] Write comprehensive documentation
- [ ] Hand off to Clothing Lead and Frontend Engineer

---

## 6. Success Metrics

### Quantitative

| Metric | MVP Target | Notes |
|--------|-----------|-------|
| **Rigging Time** | <1 second | End-to-end automation (import → skeleton → weights) |
| **Export Time** | <2 seconds | glTF export of 50k-vertex mesh + animation |
| **Accuracy (IK Chain)** | ±5cm wrist position | After animation retargeting |
| **Weight Quality** | 90% acceptable | With <5 min manual cleanup per scan |
| **Mesh Coverage** | 95%+ vertices painted | Automatic weights should cover most mesh |

### Qualitative

- ✅ Outputs usable by Clothing Lead (no pre-processing needed)
- ✅ Exports load in Three.js without errors
- ✅ Animations play smoothly (no pops, blending)
- ✅ Code well-documented for future handoff

---

## 7. Dependencies & Blockers

### Internal Dependencies

| Team | Dependency | When Needed |
|------|-----------|------------|
| **3D Scanning Lead** | Cleaned FBX meshes | Week 1 (for testing) |
| **Frontend Engineer** | Three.js viewer setup | Week 5 (for export validation) |
| **Clothing Lead** | Feedback on weight quality | Week 6 (integration testing) |
| **Backend Engineer** | Storage schema for .blend files | Week 7 (for archival) |

### External Dependencies

- **Blender:** Downloadable, no blockers
- **Rigify:** Comes with Blender, no blockers
- **MediaPipe:** Free, open-source, no blockers
- **Mixamo:** Adobe account, need licensing clarity (3D Scanning Lead to confirm)

### Known Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Rigify not suitable for very diverse body types** | Medium | Test early with edge cases (very tall, very short, large build); may need fallback method |
| **Weight painting produces artifacts at joints** | Medium | Plan for manual cleanup; validate with Clothing Lead early |
| **Animation retargeting jerky for extreme proportions** | Low | Test with reference scans; document edge cases |
| **glTF export performance degrades with complex textures** | Low | Optimize texture resolution; use embedded binary format |

---

## 8. Handoff Plan

**End of Phase 1:** Blender Lead delivers:
1. Fully automated Python framework (documented, tested)
2. Reference .blend template with all components
3. Export pipeline validated with Three.js
4. Documentation for downstream teams
5. Known limitations and edge cases documented

**To Clothing Lead:** 
- How to use/modify weights for garment fitting
- Expected mesh quality (vertex normals, UV maps)
- Constraints and limitations (no facial rigging yet, etc.)

**To Frontend Engineer:**
- glTF export specification
- Animation naming conventions (walk, run, idle)
- Material/texture expectations
- Mesh optimization recommendations

**To Backend Engineer:**
- .blend file structure and metadata
- Export size/performance characteristics
- Storage and versioning recommendations

---

## 9. Appendix: Tools & Versions

### Required Software
- **Blender:** 3.6 LTS or later (free, GPL v2)
- **Python:** 3.10+ (comes with Blender)
- **MediaPipe:** Latest (free, Apache 2.0)
- **Rigify:** Built-in addon (free)

### Optional Libraries
- **Open3D:** For point cloud processing (if needed; free)
- **NumPy/SciPy:** Math utilities (free)
- **Pytest:** Unit testing (free)
- **Marvelous Designer/CLO3D:** For garment integration (Phase 2+; paid)

### Version Control & Infrastructure
- **Git:** For code (Blender scripts, Python modules)
- **GitHub/GitLab:** For repository hosting
- **CI/CD:** GitHub Actions or similar for batch testing

---

**Status:** Ready for Development  
**Next Review:** End of Week 2 (checkpoint: MediaPipe integration working)

