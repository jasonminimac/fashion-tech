# Clothing & Physics Technical Architecture
## Garment Scanning, Fitting & Simulation System

**Document Owner:** Clothing & Physics Lead  
**Date:** 2026-03-17  
**Status:** Phase 1 Design (Pre-Build)  
**Phase 1 Duration:** 6-8 weeks  

---

## Table of Contents

1. [Overview](#overview)
2. [Garment Data Model](#garment-data-model)
3. [Garment Import Pipeline](#garment-import-pipeline)
4. [Fitting Algorithm Strategy](#fitting-algorithm-strategy)
5. [Cloth Simulation Architecture](#cloth-simulation-architecture)
6. [B2B Onboarding Workflow](#b2b-onboarding-workflow)
7. [Phase 1 Deliverables](#phase-1-deliverables)
8. [Technical Risks & Mitigation](#technical-risks--mitigation)
9. [Success Metrics](#success-metrics)

---

## Overview

The Clothing & Physics subsystem is responsible for:

1. **Garment Acquisition:** Import 3D garment models from manufacturers (CLO3D, Marvelous Designer, scans, CAD)
2. **Garment Fitting:** Deform garments to fit user bodies at different sizes and poses
3. **Cloth Simulation:** Add realistic drape, wrinkles, and fabric behavior via Blender cloth physics
4. **Database & Metadata:** Store garment geometry, textures, sizing parameters, and fit rules
5. **B2B Integration:** Onboard manufacturers, validate garments, manage catalogue updates

### Key Constraints

- **Blender is our primary 3D engine** (integration lead provides rigged bodies, physics simulation)
- **Garments must fit bodies across S/M/L/XL** and multiple body types (proportions vary)
- **Cloth sim must be real-time or near-real-time** for web viewer (60fps goal)
- **50+ garments in MVP** to demonstrate catalogue diversity
- **Accuracy within 1 size category** (e.g., if user wears M, garment should look like M, not S)

---

## Garment Data Model

### Database Schema

Each garment in the Fashion Tech catalogue is represented as:

```python
{
  "id": "garment_uuid",
  "metadata": {
    "name": "Classic White Shirt",
    "brand": "Brand Name",
    "category": "shirt",  # shirt, dress, pants, jacket, etc.
    "sku": "BRAND-SKU-123",
    "description": "100% cotton button-up shirt",
    "color": "white",
    "material": "cotton",
    "price_usd": 79.99,
    "retail_url": "https://brand.com/products/...",
    "created_at": "2026-03-17",
    "updated_at": "2026-03-17"
  },
  
  "geometry": {
    "base_model_url": "s3://garments/shirt_uuid/base_model.glb",  # in T-pose, neutral size
    "base_scale": {
      "height_cm": 170,  # reference body height (for scaling)
      "chest_cm": 100,
      "waist_cm": 80,
      "hips_cm": 95
    },
    "texture_url": "s3://garments/shirt_uuid/texture.jpg",
    "normal_map_url": "s3://garments/shirt_uuid/normal.jpg",
    "roughness_map_url": "s3://garments/shirt_uuid/roughness.jpg",
    "vertex_count": 4500,
    "triangles": 9000
  },
  
  "sizing": {
    "size_chart": {
      "XS": {"scale_factor": 0.85, "length_adjust_cm": -5},
      "S":  {"scale_factor": 0.92, "length_adjust_cm": -2},
      "M":  {"scale_factor": 1.0,  "length_adjust_cm": 0},   # reference size
      "L":  {"scale_factor": 1.08, "length_adjust_cm": 2},
      "XL": {"scale_factor": 1.16, "length_adjust_cm": 5}
    },
    "fit_type": "regular",  # regular, slim, relaxed, oversized
    "stretch_factor": 1.15,  # fabric elasticity (1.0 = no stretch, 1.2 = 20% elastic)
    "recommended_body_types": ["slim", "athletic", "average"],  # hint for recommendations
    "size_notes": "Runs true to size. Suggest one size up for relaxed fit."
  },
  
  "cloth_physics": {
    "fabric_type": "cotton",  # cotton, silk, denim, lycra, blend, etc.
    "weight_g_per_m2": 150,  # fabric weight (affects drape)
    "thickness_mm": 0.5,
    "elasticity": 0.1,  # 0-1 stretch resistance
    "damping": 0.05,  # 0-1 motion damping (higher = stiffer)
    "collision_margin_cm": 0.5,
    "wind_force": 0.2,  # 0-1 how much wind affects fabric
    "wrinkle_intensity": 0.7  # 0-1 how pronounced wrinkles are
  },
  
  "fitting_parameters": {
    "fit_offset_chest": 5,  # cm clearance from chest
    "fit_offset_waist": 3,
    "fit_offset_hip": 4,
    "sleeve_length_ratio": 0.45,  # arm length / body height
    "torso_length_ratio": 0.35,  # shirt length / body height
    "collar_fit": 0.95,  # 0-1, how tight collar should be
    "shoulder_width_ratio": 0.35,  # shoulder width / body width
    "armhole_depth_cm": 20  # depth of arm opening
  },
  
  "blend_file": {
    "url": "s3://garments/shirt_uuid/garment.blend",  # Blender source file (optional, for advanced editing)
    "rigged": false,  # whether garment has bones/armature
    "material_nodes": true  # if using Blender shader nodes (for better rendering)
  },
  
  "quality_metrics": {
    "scan_accuracy_mm": 2.5,  # if scanned from photogrammetry
    "cloth_sim_tested": true,
    "animation_tested_poses": ["walk", "idle"],
    "notes": "Validated with 5 test body scans, cloth drape looks natural"
  }
}
```

### Size Scaling Strategy

**Problem:** Garments designed for size M don't simply scale to size L. Different body proportions and fabric behavior complicate scaling.

**Our Approach:**

1. **Base Model:** Store garment in size M (reference)
2. **Scale Factor:** For XS/S/L/XL, apply a uniform scale (e.g., 1.0 for M, 1.08 for L)
3. **Non-Uniform Adjustments:** Adjust specific dimensions:
   - Length (sleeves, shirt tail) adjusts per size
   - Chest/waist clearance stays consistent
   - Armhole depth scales proportionally
4. **Brand-Specific Tweaks:** Allow partners to define custom scale factors (e.g., some brands run large)
5. **Test Across Body Types:** Validate fit on multiple body shapes (slim, average, athletic)

**Implementation:**
- Store per-size adjustments in the `sizing.size_chart` field
- Blender script applies scale + per-dimension offsets when fitting to user body
- Fail-safe: if fit quality <80%, flag for manual review (B2B QA)

---

## Garment Import Pipeline

### Input Sources

| Source | Format | Effort | Quality |
|--------|--------|--------|---------|
| **CLO3D Files** | `.zprj` | Medium | High (parametric, design-validated) |
| **Marvelous Designer** | `.md`, `.ztn` | Medium | High (industry standard) |
| **Photogrammetry Scans** | Point cloud → mesh | Medium | Medium-High |
| **3D CAD Models** | `.obj`, `.fbx`, `.glb` | Low | Medium (depends on source) |
| **2D Sewing Patterns** | `.pdf` or CAD → 3D | High | Variable |

### Import Workflow

```
[Manufacturer Submission]
  ↓
[Format Detection & Validation]
  ├─ CLO3D (.zprj) → Export to OBJ/FBX
  ├─ Marvelous Designer (.md) → Export to OBJ/FBX
  ├─ Photogrammetry → Mesh cleanup & decimation
  └─ 3D CAD → Validation checks
  ↓
[Geometry Cleanup]
  ├─ Remove internal faces
  ├─ Decimate mesh (target ~5k-10k triangles for real-time)
  ├─ Smooth artifacts
  ├─ Ensure manifold topology
  └─ Validate watertight (no holes)
  ↓
[Reference Body Binding]
  ├─ Load reference T-pose body (from Blender Lead)
  ├─ Fit garment to reference body
  ├─ Extract fitting parameters
  └─ Store fit offset values
  ↓
[Texture & Material Assignment]
  ├─ Extract textures from source file
  ├─ Bake normal/roughness maps if needed
  ├─ Create simplified PBR (roughness, metallic)
  └─ Test rendering in viewer
  ↓
[Cloth Physics Calibration]
  ├─ Run test simulation on reference body (static pose)
  ├─ Adjust fabric parameters (weight, damping, elasticity)
  ├─ Validate drape matches reference (if available)
  └─ Store final physics config
  ↓
[Quality Assurance]
  ├─ Visual inspection (UV seams, texture quality)
  ├─ Cloth sim validation (no unrealistic bunching, tears)
  ├─ Fit test on 3+ body types
  ├─ Animation test (walk cycle, weight shifts)
  └─ Partner sign-off
  ↓
[Database Storage]
  ├─ Store GLB (optimized mesh) in S3
  ├─ Store .blend source file for future edits
  ├─ Index metadata in PostgreSQL
  └─ Mark as "catalogue_ready"
```

### Technical Implementation

**Tools & Scripts (Python-based):**

1. **`import_clo3d.py`** — Parse CLO3D `.zprj` (XML + embedded OBJ)
   - Extract garment OBJ, textures, basic fabric parameters
   - Output: cleaned OBJ + texture map

2. **`import_marvelous_designer.py`** — Parse MD `.md` file
   - Extract 3D mesh and material info
   - Handle parametric sizing (if available)
   - Output: OBJ + fabric config

3. **`cleanup_mesh.py`** — Geometry cleanup utility
   - Remove duplicates, non-manifold faces
   - Decimate to target triangle count
   - Smooth surface while preserving important edges
   - Libraries: PyVista, trimesh

4. **`fit_to_reference_body.py`** — Auto-binding script
   - Load reference body (from Blender Lead)
   - Use shrinkwrap modifier in Blender to fit garment
   - Extract and measure clearances (chest, waist, hip)
   - Store fit parameters

5. **`test_cloth_sim.py`** — Blender-based simulation validator
   - Run cloth sim on reference body (5-10 second sim)
   - Check for unrealistic artifacts (excessive bunching, tears)
   - Extract and log physics parameters for fine-tuning
   - Automatically adjust damping/weight if needed

6. **`generate_web_assets.py`** — Optimize for viewer
   - Export to compressed GLB format
   - Generate LOD (level of detail) variants
   - Compress textures
   - Create web-ready material definitions

**Blender Integration:**
- Use Blender Python API (`bpy`) to:
  - Import/export OBJ, FBX, GLB formats
  - Set up cloth simulation physics
  - Run batch simulations (headless mode)
  - Extract shrinkwrap fitting data
  - Validate geometry (watertight, manifold)

**Database:**
- PostgreSQL stores metadata (schema shown above)
- S3 stores 3D models (GLB), textures, source .blend files
- Indexed search by category, brand, size, color

---

## Fitting Algorithm Strategy

### Overview

Garment fitting is the process of deforming a garment 3D model to conform to a user's scanned body at a specific size and pose.

**Key Challenge:** Garments must look realistic (no clipping, proper drape) across:
- Multiple body sizes (XS → XL)
- Different poses (T-pose → walking → sitting)
- Diverse body proportions (slim, athletic, curvy)

### Approach: Two-Phase Fitting

#### Phase 1: Static Fitting (MVP)

**Goal:** Quick, deterministic garment fit for T-pose or neutral stance.

**Algorithm:**

1. **Size Scaling**
   - Load garment in base size (M)
   - Apply scale factor from `sizing.size_chart` (e.g., 1.08 for L)
   - Apply per-dimension adjustments (length, sleeve length)
   
2. **Shrinkwrap Approximation**
   - Use Blender's shrinkwrap modifier on garment mesh
   - Project vertices onto reference body surface
   - Preserve garment interior structure (seams, darts)
   - Target offset: from `fitting_parameters` (e.g., 5cm chest clearance)
   
3. **Lattice Refinement (Optional)**
   - Apply lattice deformer over garment
   - Adjust lattice nodes to match body contours (chest, waist, hips)
   - Smooth results to avoid harsh deformations
   
4. **Collision Avoidance**
   - Check for mesh-to-mesh collisions (garment vs. body)
   - If detected, expand garment outward in problem areas
   - Validate fit: no clipping, reasonable clearance

5. **Output**
   - Store fitted garment as new mesh variant
   - Cache in S3 (per-user, per-size)
   - Use for web viewer display

**Implementation (Blender Python):**
```python
def fit_garment_to_body(garment_obj, body_obj, size_code, fitting_params):
    """
    Fit a garment to a user body at a specific size.
    
    Args:
        garment_obj: Blender mesh object (garment)
        body_obj: Blender mesh object (user scanned body)
        size_code: "XS", "S", "M", "L", "XL"
        fitting_params: dict with scale factors, offsets, clearances
    
    Returns:
        fitted_garment_mesh: Positioned and deformed garment
    """
    
    # Step 1: Scale garment based on size
    scale_factor = fitting_params["size_chart"][size_code]["scale_factor"]
    garment_obj.scale = (scale_factor, scale_factor, scale_factor)
    
    # Step 2: Apply shrinkwrap modifier
    shrinkwrap = garment_obj.modifiers.new("Shrinkwrap", "SHRINKWRAP")
    shrinkwrap.target = body_obj
    shrinkwrap.offset = fitting_params["fit_offset_chest"] / 100  # cm → m
    shrinkwrap.use_positive_direction = True
    
    # Step 3: Apply and evaluate
    fitted_mesh = garment_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    
    # Step 4: Collision check
    collision_margin = fitting_params["cloth_physics"]["collision_margin_cm"]
    check_collisions(fitted_mesh, body_obj, margin=collision_margin)
    
    return fitted_mesh
```

**Expected Results:**
- Basic garment fit in <1 second (Blender headless)
- Fit quality: ~80-90% (good enough for MVP)
- Limitations: No dynamic drape, rigid deformation

#### Phase 2: Dynamic Cloth Simulation (Phase 2+)

**Goal:** Realistic drape, wrinkles, and weight distribution.

**Algorithm:**

1. **Pose-Space Deformation**
   - Store pre-deformed garment poses (T-pose, walk frame 1, 2, ...)
   - Blend poses based on current animation frame
   - Much faster than full simulation

2. **Cloth Simulation (Full Blender)**
   - Use Blender's cloth sim as fallback for higher accuracy
   - Runs offline, caches results
   - Trade-off: slower but more realistic
   
3. **Learning-Based Prediction (Future)**
   - Train neural net on cloth sim data
   - Predicts garment deformation from body pose + physics params
   - Real-time inference (on GPU or CPU)

**Timing:**
- Phase 1 (MVP): Static fitting only
- Phase 2 (Weeks 5-6+): Add pose-space deformation
- Phase 3: Full cloth sim or learning-based model

---

## Cloth Simulation Architecture

### Blender Cloth Sim Setup

**Why Blender?**
- Free, built-in cloth simulation engine
- Decent quality for real-time applications
- Scriptable via Python API
- Integrates with our pipeline (Blender Lead already using it)

**Physics Parameters** (from garment metadata):

| Parameter | Range | Impact | Example (Cotton) |
|-----------|-------|--------|------------------|
| **Mass** | 0.5-10 g/m² | Weight & drape | 5.0 |
| **Damping** | 0.0-1.0 | Stiffness | 0.1 |
| **Elasticity** | 0.0-1.0 | Stretch resistance | 0.2 |
| **Bending Stiffness** | 0.0-1.0 | Fold resistance | 0.5 |
| **Air Damping** | 0.0-1.0 | Air resistance | 0.02 |
| **Friction** | 0.0-1.0 | Body/fabric friction | 0.3 |
| **Collision Margin** | 0.1-1.0 cm | Buffer distance | 0.3 |

### Simulation Workflow

**Pre-Sim Calibration** (per garment):

```
1. Import garment geometry (from import pipeline)
2. Create reference body (T-pose)
3. Set cloth sim parameters (from fabric_type lookup table)
4. Run 100-frame sim on static body
5. Compare result to reference (if available)
6. Adjust parameters (mass, damping, bending) iteratively
7. Store final config in database
```

**Runtime Simulation** (user try-on):

```
1. Load fitted garment (from static fitting, sized for user)
2. Load user body + current animation frame (from Blender Lead)
3. Apply cloth sim with pre-calibrated parameters
4. Simulate 10-30 frames (lightweight cache or real-time)
5. Render result in viewer
6. Cache result if used frequently
```

**Performance Optimization:**

| Approach | Speed | Quality | Implementation |
|----------|-------|---------|-----------------|
| **Static mesh** | ⚡ Fast | ⚠️ Low | MVP: just load pre-fitted garment |
| **Pre-baked sim** | ⚡ Fast | ✅ Good | Cache sim results for common animations |
| **Pose-space blend** | ⚡ Fast | ✅ Good | Linear blend between pre-simmed poses |
| **Real-time cloth sim** | 🐢 Slow | ✅✅ Best | Phase 2: for high-end viewers |
| **ML prediction** | ⚡ Fast | ✅✅ Best | Phase 3: trained neural network |

### Implementation Plan

**Week 1-2 (Phase 1):**
- Set up Blender cloth sim for one test garment
- Manual parameter tuning
- Store reference results

**Week 3-4:**
- Automate parameter extraction (fabric → physics)
- Run batch calibrations for 10+ garments
- Validate quality metrics

**Week 5-6:**
- Integrate pre-baked sim results into web viewer
- Add pose-space blending for animations
- Performance profiling

---

## B2B Onboarding Workflow

### Partner Submission Process

**Goal:** Make it easy for manufacturers to submit garments with minimal friction.

**Workflow:**

```
[Manufacturer Portal]
  ↓
[Login / API Key Auth]
  ↓
[Submit Garment]
  ├─ Upload CLO3D / MD file OR 3D scan
  ├─ Provide metadata (brand, category, color, price)
  ├─ Define size chart (XS-XL scaling)
  └─ Fabric properties (material, weight, notes)
  ↓
[Automated Validation]
  ├─ Parse file format (success/failure)
  ├─ Geometry checks (watertight, reasonable size)
  ├─ Metadata completeness
  └─ Return validation report
  ↓
[Auto-Import Process] (Backend + Clothing Lead)
  ├─ Cleanup mesh, extract textures
  ├─ Fit to reference body
  ├─ Run cloth sim calibration
  └─ Generate web assets
  ↓
[QA Review] (Clothing Lead + Partner)
  ├─ Visual inspection
  ├─ Fit validation on 3 body types
  ├─ Cloth sim quality check
  └─ Partner feedback loop
  ↓
[Catalogue Deployment]
  ├─ Store in PostgreSQL + S3
  ├─ Add search tags
  ├─ Link to retail product URL
  └─ Live in user-facing app
```

### Partner Portal Features

**API Endpoint (Backend):**

```
POST /api/v1/partners/{partner_id}/garments
{
  "name": "Classic White Shirt",
  "category": "shirt",
  "brand": "Brand Name",
  "sku": "BRAND-123",
  "color": "white",
  "material": "cotton",
  "price_usd": 79.99,
  "retail_url": "https://...",
  "garment_file": <file upload>,
  "size_chart": {
    "XS": {"scale_factor": 0.85},
    "S": {"scale_factor": 0.92},
    "M": {"scale_factor": 1.0},
    "L": {"scale_factor": 1.08},
    "XL": {"scale_factor": 1.16}
  },
  "fabric_properties": {
    "fabric_type": "cotton",
    "weight_g_per_m2": 150,
    "stretch_factor": 1.0
  }
}

Response:
{
  "garment_id": "garment_uuid",
  "status": "submitted",
  "validation_report": {
    "errors": [],
    "warnings": [
      "Mesh has 50k triangles; will be decimated to 8k for web"
    ]
  },
  "next_step": "Await QA review (typically 24-48 hours)"
}
```

**Status Dashboard:**
- View submitted garments
- Track import status (validation → import → QA → live)
- Download validation reports
- Communicate with Fashion Tech team via dashboard

---

## Phase 1 Deliverables

### Week 1-2: Garment Data Model & Import Pipeline Setup

**Deliverables:**
- ✅ Garment database schema (PostgreSQL)
- ✅ Garment metadata structure (JSON schema)
- ✅ S3 bucket setup and access patterns
- ✅ `import_*.py` scripts (CLO3D, Marvelous Designer, generic 3D)
- ✅ `cleanup_mesh.py` utility

**Acceptance Criteria:**
- Can successfully import and clean 5 sample garments
- Metadata schema validated against 3 different garment types
- S3 storage organized and accessible

### Week 3-4: Fitting Algorithm Implementation

**Deliverables:**
- ✅ `fit_garment_to_body.py` (static fitting)
- ✅ Shrinkwrap + lattice deformation logic
- ✅ Collision detection and resolution
- ✅ Size scaling per garment type
- ✅ Unit tests and sample fits (T-pose, multiple sizes)

**Acceptance Criteria:**
- Fit garment to reference body (static pose) in <1 second
- Fit quality validated visually on 5+ body types
- No mesh clipping or penetration
- All sizes (XS-XL) fit consistently

### Week 4-5: Cloth Simulation Calibration

**Deliverables:**
- ✅ Blender cloth sim setup (headless)
- ✅ Fabric parameter lookup table (fabric_type → physics params)
- ✅ `test_cloth_sim.py` validation script
- ✅ Calibration data for 10+ garments
- ✅ Documentation on tuning parameters

**Acceptance Criteria:**
- Run cloth sim on 10 garments without crashes
- Fabric params correctly tuned (no excessive stretching/bunching)
- Sim results reproducible
- Performance: single garment sim <30 seconds

### Week 5-6: B2B Onboarding & Integration

**Deliverables:**
- ✅ Partner portal API (submit garment endpoint)
- ✅ Validation logic (file parsing, geometry checks)
- ✅ Automated import pipeline (end-to-end)
- ✅ QA review checklist + documentation
- ✅ Sample partner submission + full import test

**Acceptance Criteria:**
- Submit garment via API → auto-validated and imported
- 10+ sample garments ready in catalogue
- No manual intervention needed (except QA approval)
- Partner can track submission status

### Week 6-8: Refinement & Testing

**Deliverables:**
- ✅ Unit tests (fitting, simulation, import)
- ✅ Integration tests (end-to-end pipeline)
- ✅ Documentation (API, schema, tuning guide)
- ✅ Performance benchmarks
- ✅ Known issues & workarounds log

**Acceptance Criteria:**
- 50+ garments in catalogue (test dataset)
- All systems tested with Frontend Engineer (viewer integration)
- No critical bugs blocking user try-on flow
- Ready for Phase 2 cloth sim enhancements

---

## Technical Risks & Mitigation

### Risk 1: Shrinkwrap Fitting Produces Poor Results

**Problem:** Shrinkwrap modifier may over-compress or fail on complex geometries.

**Severity:** High (blocks MVP)

**Mitigation:**
1. Test extensively with diverse body shapes (10+ test bodies)
2. Have fallback: manual lattice adjustment if shrinkwrap fails
3. Consider hybrid: shrinkwrap + manual layer (partner can tweak)
4. Implement feedback loop: partner provides "golden reference" fits, we improve algorithm

### Risk 2: Blender Cloth Sim Produces Unrealistic Results

**Problem:** Blender's cloth sim is physics-based but can look cartoonish or unstable.

**Severity:** Medium (Phase 1 uses static fitting, Phase 2 problem)

**Mitigation:**
1. Experiment with Blender version (3.6 vs. 4.0) for best quality
2. Pre-bake simulation for key poses, blend between them (no real-time sim)
3. Keep option to integrate Marvelous Designer later (paid, better quality)
4. Consider ML-based alternative (learning-based prediction)

### Risk 3: Garment Import Formats Too Varied

**Problem:** Different manufacturers use different tools; file formats differ, parameters are non-standard.

**Severity:** Medium (slows onboarding)

**Mitigation:**
1. Start with CLO3D + Marvelous Designer (80% of professional garment design)
2. Provide detailed submission guidelines (template sizes, formats)
3. Require partners to export to standard format (OBJ/FBX)
4. Manual intervention for edge cases (2D pattern → 3D)

### Risk 4: Cloth Sim Parameters Unique Per Garment

**Problem:** Each garment may need different physics tuning; no one-size-fits-all.

**Severity:** Medium (labor-intensive)

**Mitigation:**
1. Build fabric lookup table (fabric_type → approximate parameters)
2. Auto-tune via iterative simulation (tweak params until results match reference)
3. Partner provides feedback → we adjust parameters
4. Batch processing: calibrate 5-10 garments at once

### Risk 5: Performance: Cloth Sim Too Slow for Real-Time

**Problem:** Full Blender cloth sim may take 10+ seconds per garment.

**Severity:** High (blocks Phase 2)

**Mitigation:**
1. Phase 1: No real-time cloth sim, use static fitting only
2. Phase 2: Pre-bake sim results for 5-10 key animation frames, blend between them
3. Profiling: measure overhead, optimize mesh decimation, reduce collision complexity
4. GPU acceleration: explore NVIDIA GARNet or similar learning-based model

---

## Success Metrics

### Phase 1 Completion (Week 8)

| Metric | Target | Success Criteria |
|--------|--------|------------------|
| **Garment Catalogue Size** | 50+ garments | Mix of shirts, dresses, pants |
| **Import Success Rate** | >95% | Auto-import works for 95%+ of submissions |
| **Fitting Quality** | <10% clipping | No visual penetration in web viewer |
| **Fit Accuracy** | ±1 size category | User wears M, garment looks M (not S/L) |
| **Processing Speed** | <5 min per garment | End-to-end: import → fit → export |
| **Cloth Sim Stability** | 0 crashes | Simulations complete without errors |
| **Partner Onboarding** | <30 min per brand | Simple submission process |
| **Documentation** | >90% coverage | API, schema, tuning guide complete |

### Example: Submit Garment, See It In Viewer

**End-to-end test (Week 8):**

```
1. Partner uploads CLO3D file via API
2. System auto-validates, imports, fits to reference body
3. Clothing Lead reviews QA checklist
4. Garment deployed to catalogue
5. Frontend Engineer adds to viewer
6. User scans body, tries on garment
   → See it fitted to their size
   → See it animated (walk cycle)
   → Download/compare with other garments
```

**Success:** Full loop works, no manual rework needed.

---

## Summary & Next Steps

### What This Document Defines

- **Garment data model:** Complete schema for storing garments + metadata
- **Import pipeline:** How garments flow from partners → our system
- **Fitting algorithm:** Deterministic, size-aware deformation
- **Cloth simulation:** Blender-based physics calibration
- **B2B onboarding:** Partner submission & validation flow

### What Depends on Other Leads

- **Blender Lead:** Provides rigged reference body, animation pipeline
- **Backend Engineer:** Stores metadata, manages API, handles user scans
- **Frontend Engineer:** Displays garments in viewer, handles outfit building
- **3D Scanning Lead:** Provides normalized body scans for fitting validation

### Critical Path (Weeks 1-4)

1. **Collab with Blender Lead:** Get reference body + rigging setup (Week 1)
2. **Build fitting algorithm:** Shrinkwrap + lattice (Week 2-3)
3. **Test with 10 sample garments:** Iterate fitting quality (Week 3-4)
4. **Partner with Backend Lead:** API for garment submission (Week 3)
5. **Hand off to Frontend:** Ready for viewer integration (Week 5)

### Open Questions

1. **CLO3D/Marvelous Designer License:** Do we have access to their tools? (affects import automation)
2. **Reference Body Data:** What rigging level from Blender Lead? (T-pose only, or full skeleton?)
3. **Fabric Database:** Are there public fabric property tables, or do we build our own?
4. **Approval Threshold:** Who signs off on QA (Clothing Lead solo, or Partner + CEO)?
5. **Garment Sourcing:** Who recruits the 50 manufacturers? (Backend Lead, CEO, or Clothing Lead?)

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Milestone:** Week 1 kickoff, dependency check with Blender Lead
