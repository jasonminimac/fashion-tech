# WEEK 1 IMPLEMENTATION SPEC
## Garment & Cloth Simulation - Fashion Tech MVP

**Document Owner:** Garment & Cloth Simulation Engineer  
**Date:** 2026-03-18  
**Phase:** Phase 1 (MVP)  
**Duration:** Week 1 Kickoff (March 18-22, 2026)  
**Status:** Ready for Execution  

---

## Executive Summary

This document defines Week 1 deliverables for the Garment & Cloth Simulation subsystem, with partnership-focused outreach specs and technical integration architecture. **Goal:** Establish infrastructure, confirm B2B onboarding workflow, and prepare Zara/H&M outreach with clear asset requirements.

### Week 1 Core Tasks

1. ✅ **Infrastructure Setup** — Database schema, S3 structure, git repo
2. ✅ **Partner Outreach Spec** — What to ask Zara/H&M, asset requirements, CLO3D maturity assessment
3. ✅ **Garment Intake Checklist** — Format requirements, validation criteria, SLA
4. ✅ **CLO3D Integration Architecture** — How to parse `.zprj` files, extract assets
5. ✅ **Blender Cloth Sim Fallback** — MVP web viewer path (static fitting + skeleton binding)
6. ✅ **Garment Database Schema** — Complete metadata model for MVP
7. ✅ **Fabric Physics Parameters** — Lookup table for cotton, silk, denim, etc.
8. ✅ **MVP Garment Category Spec** — 3-5 sample garments with metadata requirements
9. ✅ **Fitting Pipeline Workflow** — Shrinkwrap algorithm, size scaling, collision detection

---

## PART 1: PARTNER OUTREACH SPEC

### 1.1 Target Partners: Zara & H&M

**Why Zara & H&M?**
- **Scale:** 2,500+ stores each, massive retail inventory
- **Tech maturity:** Both have invested in 3D design tools (CLO3D, Marvelous Designer)
- **Speed:** Fast fashion model means 3D prototyping is already critical
- **Leverage:** Partnership de-risks other manufacturers

### 1.2 What to Ask Zara/H&M in Initial Outreach

#### Email/Call 1: Discovery & Capability Assessment

**Subject:** Fashion Tech — Virtual Try-On Partnership (CLO3D Asset Integration)

**Key Questions:**

1. **Current 3D Workflow**
   - "Do your design teams use CLO3D or Marvelous Designer?"
   - "What's your current 3D-to-production pipeline?"
   - "How mature are your 3D garment assets?" (Are they design-validated?)

2. **Asset Availability**
   - "Can you share sample `.zprj` files (CLO3D) or `.md` (Marvelous Designer)?"
   - "Do you maintain a library of garment blocks/bases?"
   - "What's your typical garment complexity?" (polygon count, materials)

3. **Size & Scaling**
   - "How do you currently scale garments across sizes (XS-XL)?"
   - "Do you use parametric sizing or manual per-size adjustments?"
   - "What are your tolerance requirements?" (fit accuracy ±1cm, ±2cm?)

4. **Physical Validation**
   - "Do you do fit validation on dress forms/mannequins?"
   - "Can you provide reference fit photos for 5-10 sample garments?"
   - "What fabric types do you prioritize?" (% cotton, % synthetic, blends?)

5. **Timelines & Resources**
   - "Who is the key contact for technical integration?"
   - "Can we schedule 2-3 hour technical deep-dive in Week 2?"
   - "What's your bandwidth for pilot program?" (dedicated person, timeline)

#### Email/Call 2: Technical Specification (Post-Discovery)

**Subject:** Fashion Tech Integration — Technical Requirements & Timeline

**Deliverables to Share:**
1. Garment Intake Checklist (see Section 1.3)
2. CLO3D Asset Compatibility Matrix (see Section 1.4)
3. SLA & Timeline (see Section 1.5)
4. Revenue Split / Partnership Terms (from CEO)

**Technical Discussion Topics:**
- File format handoff (CLO3D → OBJ/FBX export standards)
- Metadata requirements (brand, size chart, fabric type)
- QA process (how we validate fits)
- Go-live timeline (5 pilot garments in 4 weeks)

---

### 1.3 Garment Intake Checklist

**This checklist is shared with partners. Use it to evaluate incoming garments.**

```markdown
# Fashion Tech — Garment Submission Checklist

## Mandatory Requirements ✓

### 1. File Format
- [ ] CLO3D file (`.zprj`) OR
- [ ] Marvelous Designer file (`.md`) OR
- [ ] 3D scan (OBJ/FBX with textures)

### 2. Garment Metadata
- [ ] Garment name (e.g., "Classic White Button-Up Shirt")
- [ ] Brand name
- [ ] Category (shirt, dress, pants, jacket, etc.)
- [ ] SKU / Internal reference
- [ ] Color (primary + secondary)
- [ ] Material / Fabric type (cotton, silk, denim, blend, etc.)
- [ ] Retail price (USD)
- [ ] Retail product URL (link to e-commerce)

### 3. Sizing Information
- [ ] Base size for design file (typically "M" or "Medium")
- [ ] Size chart: XS, S, M, L, XL
  - Scale factors per size (uniform, e.g., M=1.0, L=1.08)
  - OR per-size adjustments (length, width per size)
- [ ] Fit type (regular, slim, relaxed, oversized)
- [ ] Any special notes (runs large, runs small, tight in chest, etc.)

### 4. 3D Geometry
- [ ] Mesh is manifold (no holes, closed topology)
- [ ] Texture mapped (UV unwrapping complete)
- [ ] Polygon count reasonable for web (target: 5k-10k triangles)
  - If >20k: we'll decimate during import
- [ ] All seams and construction details preserved
- [ ] No internal mesh artifacts (double faces, debris)

### 5. Materials & Textures
- [ ] Diffuse / Base Color texture (2K or lower)
- [ ] Normal map (optional but preferred)
- [ ] Roughness/specularity map (optional)
- [ ] All textures in standard format (PNG, JPG)
- [ ] Texture file paths relative (not absolute)

### 6. Fabric Properties (Designer Input)
- [ ] Material weight (g/m²) if known
  - Example: 150 g/m² = medium cotton
- [ ] Fabric type (cotton, silk, denim, spandex, blend)
- [ ] Stretch / elasticity (if applicable)
  - 0-10%: no stretch (woven cotton)
  - 15-20%: mild stretch (most blends)
  - 50%+: elastic (spandex, lycra)
- [ ] Design notes on fabric behavior (how it drapes, folds, etc.)

### 7. Quality Standards
- [ ] Garment tested in CLO3D/MD for fit on dress form
- [ ] No clipping or intersection errors in design file
- [ ] Colors match brand reference (visual QA)
- [ ] Design intent documented (specific pose, wear style, etc.)

### 8. Submission Format

**Folder structure (ZIP):**
```
Brand_Garment_SK U_v1.zip
├─ garment.zprj          (or .md, .obj)
├─ textures/
│  ├─ color.jpg
│  ├─ normal.jpg
│  └─ roughness.jpg
├─ metadata.json          (see template below)
└─ README.txt            (notes from designer)
```

**metadata.json template:**
```json
{
  "garment_name": "Classic White Button-Up Shirt",
  "brand": "Zara",
  "sku": "ZARA-SHIRT-12345",
  "category": "shirt",
  "color": "white",
  "material": "100% cotton",
  "price_usd": 79.99,
  "retail_url": "https://www.zara.com/products/...",
  "base_size": "M",
  "size_chart": {
    "XS": { "scale_factor": 0.85, "notes": "" },
    "S":  { "scale_factor": 0.92, "notes": "" },
    "M":  { "scale_factor": 1.0,  "notes": "reference size" },
    "L":  { "scale_factor": 1.08, "notes": "" },
    "XL": { "scale_factor": 1.16, "notes": "runs large" }
  },
  "fit_type": "regular",
  "fabric_properties": {
    "type": "cotton",
    "weight_g_per_m2": 150,
    "stretch_percent": 0,
    "notes": "Lightweight, minimal stretch, settles quickly"
  }
}
```

## Optional Enhancements ⭐

- [ ] Design approval photo from brand (fit on dress form)
- [ ] Marvelous Designer parametric data (if available)
- [ ] Animation-tested pose (walk cycle, arm movement)
- [ ] Competitor garment comparisons (fit, drape quality)

## Validation Timeline

- **Submission:** Partner uploads file + metadata
- **Auto-validation:** 24 hours (parsing, geometry checks)
- **Fashion Tech QA:** 24-48 hours (fit validation, visual QA)
- **Revision Loop:** Up to 2 rounds of feedback (if needed)
- **Go-Live:** Approved garments live in catalogue within 5 business days

---

## Questions?

Contact: [Fashion Tech Technical Team]
Email: partnerships@fashion-tech.com
Timeline: Week 2 onboarding call scheduled
```

---

### 1.4 Asset Compatibility Matrix

**This matrix helps us assess partner maturity and predict integration effort.**

| Capability | Zara Target | H&M Target | Why It Matters |
|------------|------------|------------|----------------|
| **CLO3D Usage** | ✅ Daily | ✅ Daily | Native `.zprj` import (easiest path) |
| **3D File Export** | ✅ OBJ + FBX | ✅ OBJ + FBX | Web-compatible formats |
| **Texture Maps** | ✅ Diffuse + Normal | ✅ Diffuse + Normal | Material quality in viewer |
| **Parametric Sizing** | ⚠️ Partial | ⚠️ Partial | Saves scaling work (manual tweaks OK) |
| **Fit Validation Data** | ⚠️ Dress form only | ⚠️ Dress form only | We add human body validation |
| **Fabric Properties DB** | ✅ Known types | ✅ Known types | Helps cloth sim tuning (Phase 2) |
| **Animation Testing** | ❌ Not typical | ❌ Not typical | We handle post-submission |
| **Multi-Body Fit** | ❌ Not tested | ❌ Not tested | Our fitting algorithm validates |

**Legend:**
- ✅ Ready (partner has this, direct integration)
- ⚠️ Partial (partner has data, we need to normalize/convert)
- ❌ Not available (we build from scratch or workaround)

**Integration Effort Estimate:**
- CLO3D file + OBJ export + basic metadata = **2-3 hours** per garment
- With parametric sizing data = **1-2 hours**
- No CLO3D (manual 3D scan) = **4-6 hours** (full mesh cleanup needed)

---

### 1.5 SLA & Partnership Timeline

**What we promise partners:**

| Milestone | Timeline | Commitment |
|-----------|----------|-----------|
| **Initial Outreach Response** | Same day | Confirm interest, schedule call |
| **Technical Deep-Dive** | Week 2 | Define integration path, answer Q&A |
| **Intake Checklist Approved** | Week 2 end | Partner signs off on submission format |
| **First 5 Garments Submitted** | Week 3-4 | Partner uploads pilot garments |
| **Auto-Validation Report** | 24h after submit | We provide feedback (pass/fail/fixes) |
| **Fashion Tech QA Review** | 24-48h after submit | Fit validation, visual sign-off |
| **Live in Catalogue** | 5 business days | Garments go live in viewer |
| **Feedback Loop** | Ongoing | Weekly sync, quarterly reviews |

**Partner Success Metrics (Month 1):**
- ✅ 5-10 garments live in catalogue
- ✅ <15 min average integration time per garment (target)
- ✅ Zero critical fit issues
- ✅ Partner can submit independently (no hand-holding)

---

## PART 2: TECHNICAL ARCHITECTURE

### 2.1 CLO3D Integration Architecture

**Goal:** Parse CLO3D `.zprj` files, extract garment geometry + textures, convert to web-ready format.

#### CLO3D File Structure

```
garment.zprj (XML + embedded 3D data)
├─ [Root XML]
│  ├─ version info
│  ├─ garment_name, brand, etc.
│  └─ references to embedded files
├─ [Embedded OBJ]
│  └─ 3D mesh (vertices, faces, normals)
├─ [Embedded MTL]
│  └─ Material definitions
├─ [Embedded Textures]
│  ├─ color.jpg
│  ├─ normal.jpg
│  └─ other maps
└─ [Metadata]
   ├─ Design parameters (if parametric)
   ├─ Size scaling rules (if available)
   └─ Fabric properties (if stored)
```

#### Import Pipeline (CLO3D Specific)

```
[Partner Submission: garment.zprj]
  ↓
[Step 1: Unzip & Parse]
  Extract XML root
  List embedded assets
  Validate structure
  ↓
[Step 2: Extract Geometry]
  Read embedded OBJ
  Parse vertices, faces, normals
  Validate manifold topology
  ↓
[Step 3: Extract Textures]
  Export embedded images
  Validate format (JPG, PNG)
  Check dimensions (max 2K)
  ↓
[Step 4: Parse Metadata]
  Extract garment name, brand, SKU
  Read design parameters (if parametric)
  Extract fabric type (if stored)
  ↓
[Step 5: Geometry Cleanup]
  Decimate if >20k triangles (target 5k-10k)
  Check for manifold violations
  Remove duplicate vertices
  Smooth normals
  ↓
[Step 6: Validate Against Checklist]
  ✓ Geometry watertight?
  ✓ Textures present?
  ✓ Metadata complete?
  If fails: Generate error report → Partner revises
  ↓
[Step 7: Store in S3]
  s3://garments/{garment_id}/
    ├─ garment_base.glb     (cleaned mesh)
    ├─ textures/
    │  ├─ color_2k.jpg
    │  └─ normal_2k.jpg
    └─ metadata.json
  ↓
[Step 8: Register in PostgreSQL]
  Insert garment record
  Mark status: "imported_pending_fit"
  ↓
[Step 9: Hand Off to Fitting Pipeline]
  Ready for shrinkwrap + sizing
```

#### Python Implementation: `import_clo3d.py`

```python
#!/usr/bin/env python3
"""
Parse CLO3D .zprj files and extract garment assets.

Usage:
    python import_clo3d.py garment.zprj --output ./extracted/
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path

class CLO3DImporter:
    def __init__(self, zprj_path):
        self.zprj_path = zprj_path
        self.archive = zipfile.ZipFile(zprj_path, 'r')
        self.metadata = {}
        self.textures = []
        self.geometry = None
    
    def extract_metadata(self):
        """Parse XML root to get garment metadata."""
        try:
            root_xml = self.archive.read('root.xml')  # CLO3D root
            tree = ET.fromstring(root_xml)
            
            # Extract common metadata
            self.metadata = {
                'garment_name': tree.find('.//garmentName').text,
                'brand': tree.find('.//brand').text or 'Unknown',
                'sku': tree.find('.//sku').text or '',
                'fabric_type': tree.find('.//fabricType').text or 'cotton',
                'color': tree.find('.//color').text or 'mixed',
                'scale_factor_m': 1.0,  # Default to M
            }
            print(f"✓ Extracted metadata: {self.metadata['garment_name']}")
            return self.metadata
        except Exception as e:
            print(f"✗ Failed to extract metadata: {e}")
            return None
    
    def extract_geometry(self):
        """Extract embedded OBJ mesh."""
        try:
            # CLO3D typically embeds geometry.obj
            obj_data = self.archive.read('geometry.obj').decode('utf-8')
            self.geometry = obj_data
            print(f"✓ Extracted geometry ({len(obj_data)} bytes)")
            return self.geometry
        except Exception as e:
            print(f"✗ Failed to extract geometry: {e}")
            return None
    
    def extract_textures(self):
        """Extract all embedded texture files."""
        texture_extensions = ('.jpg', '.png', '.jpeg')
        textures = []
        
        for name in self.archive.namelist():
            if any(name.lower().endswith(ext) for ext in texture_extensions):
                texture_data = self.archive.read(name)
                textures.append({
                    'name': name,
                    'data': texture_data,
                    'size_mb': len(texture_data) / (1024 * 1024)
                })
        
        self.textures = textures
        print(f"✓ Extracted {len(textures)} textures")
        return textures
    
    def validate(self):
        """Validate extracted assets against checklist."""
        errors = []
        warnings = []
        
        # Check metadata completeness
        required_fields = ['garment_name', 'brand', 'fabric_type']
        for field in required_fields:
            if field not in self.metadata or not self.metadata[field]:
                errors.append(f"Missing metadata: {field}")
        
        # Check geometry
        if not self.geometry or len(self.geometry) < 100:
            errors.append("Geometry is missing or too small")
        
        # Check textures
        if len(self.textures) == 0:
            warnings.append("No textures found (will use placeholder)")
        
        # Check texture sizes
        for tex in self.textures:
            if tex['size_mb'] > 5:
                warnings.append(f"Texture {tex['name']} is large ({tex['size_mb']:.1f}MB); will be compressed")
        
        return {'errors': errors, 'warnings': warnings, 'valid': len(errors) == 0}
    
    def export_to_folder(self, output_dir):
        """Export extracted assets to folder."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export geometry
        if self.geometry:
            with open(output_path / 'geometry.obj', 'w') as f:
                f.write(self.geometry)
            print(f"✓ Exported geometry to {output_path / 'geometry.obj'}")
        
        # Export textures
        textures_dir = output_path / 'textures'
        textures_dir.mkdir(exist_ok=True)
        for tex in self.textures:
            tex_path = textures_dir / tex['name']
            with open(tex_path, 'wb') as f:
                f.write(tex['data'])
            print(f"✓ Exported texture to {tex_path}")
        
        # Export metadata
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"✓ Exported metadata to {output_path / 'metadata.json'}")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python import_clo3d.py <garment.zprj>")
        sys.exit(1)
    
    zprj_file = sys.argv[1]
    output = sys.argv[3] if len(sys.argv) > 3 else './extracted'
    
    importer = CLO3DImporter(zprj_file)
    importer.extract_metadata()
    importer.extract_geometry()
    importer.extract_textures()
    
    validation = importer.validate()
    print(f"\nValidation Result: {'PASS' if validation['valid'] else 'FAIL'}")
    if validation['errors']:
        print("Errors:")
        for err in validation['errors']:
            print(f"  ✗ {err}")
    if validation['warnings']:
        print("Warnings:")
        for warn in validation['warnings']:
            print(f"  ⚠ {warn}")
    
    if validation['valid']:
        importer.export_to_folder(output)
        print(f"\n✓ Import complete. Assets exported to {output}")
    else:
        print("\n✗ Import failed. Please fix errors above.")

if __name__ == '__main__':
    main()
```

---

### 2.2 Blender Cloth Sim Fallback (MVP Web Viewer Path)

**Phase 1 MVP Strategy:** No real-time cloth simulation. Instead:

1. **Static Fitting:** Shrinkwrap garment to body (deterministic, <1s)
2. **Skeleton Binding:** Garment follows animation skeleton (lightweight)
3. **Optional Lattice Deformer:** Light secondary motion (procedural wrinkles)

**Why This Path?**
- Fast MVP delivery (no cloth sim tuning needed)
- Deterministic results (reproducible, debuggable)
- Works on all devices (no GPU required)
- Phase 2 can add full cloth sim without disrupting MVP

#### Static Fitting Algorithm

```python
def fit_garment_to_body(garment_mesh, body_mesh, size_code, fitting_params):
    """
    Static fit a garment to a body at a specific size.
    
    Args:
        garment_mesh: Blender mesh object (garment in T-pose, size M)
        body_mesh: Blender mesh object (rigged, animated-ready)
        size_code: "XS", "S", "M", "L", "XL"
        fitting_params: dict with scale factors, offsets, clearances
    
    Returns:
        fitted_mesh: Positioned garment ready for animation
    """
    
    # Step 1: Scale based on size
    scale = fitting_params['size_chart'][size_code]['scale_factor']
    garment_mesh.scale = (scale, scale, scale)
    
    # Step 2: Apply shrinkwrap modifier
    #   - Projects vertices onto body surface
    #   - Maintains garment interior structure
    #   - Offset = clearance (e.g., 0.05m = 5cm from chest)
    shrinkwrap = garment_mesh.modifiers.new('Shrinkwrap', 'SHRINKWRAP')
    shrinkwrap.target = body_mesh
    shrinkwrap.offset = fitting_params['fit_offset_chest'] / 100
    shrinkwrap.use_positive_direction = True
    shrinkwrap.show_render = True
    shrinkwrap.show_viewport = True
    
    # Step 3: Apply shrinkwrap to geometry
    fitted_geom = garment_mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    
    # Step 4: Collision check
    collision_margin = fitting_params['cloth_physics']['collision_margin_cm']
    collisions = check_mesh_collisions(fitted_geom, body_mesh, margin=collision_margin)
    if collisions:
        print(f"⚠ Warning: {len(collisions)} collision points detected")
        # Expand garment outward in problem areas
        fitted_geom = resolve_collisions(fitted_geom, collisions)
    
    return fitted_geom
```

#### Skeleton Binding (Animation)

```python
def bind_garment_to_skeleton(garment_mesh, body_mesh, body_armature):
    """
    Bind garment to body skeleton for animation.
    
    Garment vertices follow same bone transformations as nearby body vertices.
    Result: Garment animates naturally without separate cloth sim.
    """
    
    # Step 1: Add Armature modifier to garment
    armature_mod = garment_mesh.modifiers.new('Armature', 'ARMATURE')
    armature_mod.object = body_armature
    
    # Step 2: Auto-weight (Blender's algorithm)
    #   - Analyzes proximity of garment vertices to bones
    #   - Assigns weights automatically
    #   - Result: nearby garment verts follow nearby body bones
    with bpy.context.temp_override(object=garment_mesh, pose_object=body_mesh):
        bpy.ops.object.mod_armature_auto_weight()
    
    # Step 3: (Optional) Manual weight painting for fine-tuning
    #   - If some vertices move wrong, painter can adjust weights
    #   - Weights range 0-1 per vertex per bone
    
    # Step 4: Test animation
    #   - Play walk cycle
    #   - Verify garment follows smoothly
    #   - Check for unrealistic deformation
    
    return True
```

#### Optional: Lattice Deformer (Secondary Motion)

```python
def add_lattice_deformer(garment_mesh, intensity=0.3):
    """
    Add procedural secondary motion to garment.
    
    Light lattice deformation on top of skeleton binding.
    Creates visual interest (wrinkles, settling) without full cloth sim.
    """
    
    # Create lattice (grid of control points)
    # Typically 5×5×5 lattice points around garment
    lattice = bpy.data.lattices.new('GarmentLattice')
    lattice.points_u = 5
    lattice.points_v = 5
    lattice.points_w = 5
    
    # Add lattice modifier to garment
    lattice_mod = garment_mesh.modifiers.new('Lattice', 'LATTICE')
    lattice_mod.object = lattice
    lattice_mod.strength = intensity  # 0-1, how much effect
    
    # (Optional) Animate lattice for procedural wrinkles
    # This is a keyframe-based animation that repeats subtly
    # Creates settling effect as garment comes to rest after movement
    
    return lattice_mod
```

---

### 2.3 Garment Database Schema (PostgreSQL)

```sql
-- GARMENTS TABLE (Master garment records)
CREATE TABLE garments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Metadata
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- shirt, dress, pants, jacket, etc.
    sku VARCHAR(100) UNIQUE,
    description TEXT,
    color VARCHAR(100),
    material VARCHAR(255),
    price_usd DECIMAL(10, 2),
    retail_url TEXT,
    
    -- Geometry & Storage
    base_model_url TEXT,  -- s3://garments/{id}/garment.glb
    texture_url TEXT,
    normal_map_url TEXT,
    roughness_map_url TEXT,
    vertex_count INT,
    triangle_count INT,
    
    -- Sizing
    base_scale_height_cm INT DEFAULT 170,
    base_scale_chest_cm INT DEFAULT 100,
    base_scale_waist_cm INT DEFAULT 80,
    base_scale_hips_cm INT DEFAULT 95,
    
    -- Fabric Properties (for Phase 2 cloth sim)
    fabric_type VARCHAR(50),  -- cotton, silk, denim, spandex, etc.
    fabric_weight_g_per_m2 INT,
    fabric_thickness_mm DECIMAL(3,1),
    fabric_elasticity DECIMAL(3,2),  -- 0-1
    fabric_damping DECIMAL(3,2),     -- 0-1
    
    -- Fitting Parameters
    fit_offset_chest_cm INT DEFAULT 5,
    fit_offset_waist_cm INT DEFAULT 3,
    fit_offset_hip_cm INT DEFAULT 4,
    sleeve_length_ratio DECIMAL(3,2),
    torso_length_ratio DECIMAL(3,2),
    
    -- Status & Tracking
    status VARCHAR(50) DEFAULT 'draft',  -- draft, imported, fitted, validated, live
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    -- QA
    quality_notes TEXT,
    validation_passed BOOLEAN DEFAULT FALSE,
    validation_date TIMESTAMP,
    validated_by VARCHAR(255)
);

-- GARMENT_SIZES TABLE (Per-size scaling)
CREATE TABLE garment_sizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    garment_id UUID NOT NULL REFERENCES garments(id),
    
    size_code VARCHAR(3),  -- XS, S, M, L, XL
    scale_factor DECIMAL(3,2),  -- 0.85, 0.92, 1.0, 1.08, 1.16
    length_adjust_cm INT,
    width_adjust_cm INT,
    
    -- Per-size model URLs (cached fitted variants)
    fitted_model_url TEXT,  -- s3://garments/{id}/fitted_{size}.glb
    
    UNIQUE(garment_id, size_code)
);

-- GARMENT_PARTNERS TABLE (Which partner provides which garment)
CREATE TABLE garment_partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    garment_id UUID NOT NULL REFERENCES garments(id),
    partner_id UUID NOT NULL,
    partner_name VARCHAR(255),
    
    submitted_date TIMESTAMP,
    submission_format VARCHAR(50),  -- zprj, md, obj, fbx, etc.
    submission_notes TEXT,
    
    revision_count INT DEFAULT 0,
    last_revision_date TIMESTAMP,
    
    UNIQUE(garment_id, partner_id)
);

-- GARMENT_VALIDATION_LOG TABLE (QA history)
CREATE TABLE garment_validation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    garment_id UUID NOT NULL REFERENCES garments(id),
    
    validation_type VARCHAR(50),  -- geometry, fit, animation, visual, etc.
    result VARCHAR(50),  -- pass, fail, warning
    notes TEXT,
    
    validated_by VARCHAR(255),
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    collision_count INT,
    fit_quality_score DECIMAL(3,2),  -- 0-1
    visual_notes TEXT
);

-- Indexes for fast queries
CREATE INDEX idx_garments_status ON garments(status);
CREATE INDEX idx_garments_category ON garments(category);
CREATE INDEX idx_garments_brand ON garments(brand);
CREATE INDEX idx_garment_sizes_garment ON garment_sizes(garment_id);
CREATE INDEX idx_partners_partner ON garment_partners(partner_id);
```

---

### 2.4 Fabric Physics Parameters Lookup Table

**Used by Blender cloth sim in Phase 2. Provides starting point for tuning.**

```python
FABRIC_PARAMETERS = {
    "cotton": {
        "mass_g_per_m2": 150,
        "damping": 0.08,
        "elasticity": 0.15,
        "bending_stiffness": 0.5,
        "air_damping": 0.02,
        "friction_coefficient": 0.3,
        "wrinkle_intensity": 0.8,
        "settling_speed": 0.5,
        "color": "#E8D7C3",
        "description": "Heavy, natural settles with distinct wrinkles",
    },
    "cotton_light": {
        "mass_g_per_m2": 100,
        "damping": 0.05,
        "elasticity": 0.1,
        "bending_stiffness": 0.3,
        "air_damping": 0.01,
        "friction_coefficient": 0.2,
        "wrinkle_intensity": 0.5,
        "settling_speed": 0.3,
        "description": "Lightweight cotton, minimal wrinkles"
    },
    "silk": {
        "mass_g_per_m2": 80,
        "damping": 0.02,
        "elasticity": 0.05,
        "bending_stiffness": 0.1,
        "air_damping": 0.01,
        "friction_coefficient": 0.15,
        "wrinkle_intensity": 0.2,
        "settling_speed": 0.2,
        "color": "#F5E6D3",
        "description": "Light, flows smoothly, minimal permanent wrinkles"
    },
    "denim": {
        "mass_g_per_m2": 600,
        "damping": 0.12,
        "elasticity": 0.08,
        "bending_stiffness": 0.8,
        "air_damping": 0.03,
        "friction_coefficient": 0.4,
        "wrinkle_intensity": 0.6,
        "settling_speed": 0.7,
        "color": "#3B4D5C",
        "description": "Heavy, stiff, defined creases, resists stretching"
    },
    "spandex": {
        "mass_g_per_m2": 200,
        "damping": 0.25,
        "elasticity": 0.85,
        "bending_stiffness": 0.2,
        "air_damping": 0.02,
        "friction_coefficient": 0.5,
        "wrinkle_intensity": 0.1,
        "settling_speed": 0.9,  # Snappy, recovers fast
        "color": "#1C1C1C",
        "description": "Stretchy, hugs body, snaps back quickly"
    },
    "polyester": {
        "mass_g_per_m2": 120,
        "damping": 0.06,
        "elasticity": 0.1,
        "bending_stiffness": 0.4,
        "air_damping": 0.015,
        "friction_coefficient": 0.25,
        "wrinkle_intensity": 0.4,
        "settling_speed": 0.4,
        "description": "Synthetic, moderate drape, wrinkle-resistant"
    },
    "blend_cotton_poly": {
        "mass_g_per_m2": 140,
        "damping": 0.07,
        "elasticity": 0.12,
        "bending_stiffness": 0.45,
        "air_damping": 0.015,
        "friction_coefficient": 0.3,
        "wrinkle_intensity": 0.5,
        "settling_speed": 0.45,
        "description": "Cotton-poly blend, balanced drape & durability"
    },
    "linen": {
        "mass_g_per_m2": 160,
        "damping": 0.09,
        "elasticity": 0.08,
        "bending_stiffness": 0.6,
        "air_damping": 0.02,
        "friction_coefficient": 0.35,
        "wrinkle_intensity": 1.0,  # Linens wrinkle a lot
        "settling_speed": 0.5,
        "description": "Natural, heavy, pronounced creasing, rustic look"
    },
}
```

---

## PART 3: MVP GARMENT CATEGORY SPEC

### 3.1 Sample Garments (3-5 Pilot Garments)

**These 3-5 garments represent the diversity needed for MVP validation. Use them as reference for partner outreach.**

#### Garment 1: Classic Button-Up Shirt (Structured)

**Category:** Shirt / Top  
**Fabric:** 100% cotton  
**Fit:** Regular (not slim, not relaxed)  

**Why This Garment?**
- Most common garment type
- Tests fitting on upper body
- Defined seams and structure (easier to preserve through import)
- High volume in retail

**Technical Specs:**
```json
{
  "name": "Classic White Button-Up Shirt",
  "brand": "[Sample]",
  "category": "shirt",
  "sku": "SHIRT-BU-001",
  "color": "white",
  "material": "100% cotton",
  "price_usd": 79.99,
  "base_size": "M",
  "size_chart": {
    "XS": { "scale_factor": 0.85, "notes": "" },
    "S":  { "scale_factor": 0.92, "notes": "" },
    "M":  { "scale_factor": 1.0,  "notes": "reference size" },
    "L":  { "scale_factor": 1.08, "notes": "" },
    "XL": { "scale_factor": 1.16, "notes": "" }
  },
  "fit_type": "regular",
  "fabric_properties": {
    "type": "cotton",
    "weight_g_per_m2": 150,
    "stretch_percent": 0,
    "notes": "Lightweight, settles naturally"
  },
  "fitting_parameters": {
    "fit_offset_chest": 5,
    "fit_offset_waist": 3,
    "fit_offset_hip": 4,
    "sleeve_length_ratio": 0.45,
    "torso_length_ratio": 0.35,
    "collar_fit": 0.95,
    "shoulder_width_ratio": 0.35,
    "armhole_depth_cm": 20
  },
  "quality_requirements": {
    "target_triangles": 6000,
    "polygon_limit": 12000,
    "texture_resolution": "2K",
    "normal_map_required": true
  }
}
```

**Fitting Validation Checklist:**
- [ ] Collar fits neck without clipping
- [ ] Sleeves extend to wrist (proportionally)
- [ ] Chest clearance ~5cm from body
- [ ] Waist follows body curves naturally
- [ ] No shoulder seam clipping
- [ ] Button placement aligned with center line

---

#### Garment 2: Fitted Wrap Dress (Draped)

**Category:** Dress / Outerwear  
**Fabric:** Viscose blend (draped fabric)  
**Fit:** Regular (curves-following)  

**Why This Garment?**
- Tests fitting on full body (torso + legs)
- Fluid fabric (less structured than button-up)
- High-value for retail (dresses = significant revenue)
- Validates size scaling across larger range

**Technical Specs:**
```json
{
  "name": "Wrap Dress with Waist Tie",
  "brand": "[Sample]",
  "category": "dress",
  "color": "navy",
  "material": "65% viscose, 35% polyester",
  "price_usd": 129.99,
  "base_size": "M",
  "fit_type": "regular",
  "fabric_properties": {
    "type": "blend_viscose_poly",
    "weight_g_per_m2": 180,
    "stretch_percent": 5,
    "notes": "Draped, follows body curves"
  },
  "fitting_parameters": {
    "fit_offset_chest": 4,
    "fit_offset_waist": 2,
    "fit_offset_hip": 5,
    "sleeve_length_ratio": 0.40,
    "torso_length_ratio": 0.80,  // Full dress length
    "waist_definition": true,
    "hem_length_ratio": 0.45  // Knee-length
  }
}
```

**Fitting Validation:**
- [ ] Wrap overlaps correctly at chest
- [ ] Waist tie sits at natural waist
- [ ] Drapes from chest to hip without pulling
- [ ] Hem length proportional to body (knee-length look)
- [ ] No leg clipping or penetration
- [ ] Fabric folds naturally (test with lattice deformer)

---

#### Garment 3: Fitted Stretch Jeans (Elastic)

**Category:** Pants / Bottoms  
**Fabric:** 98% cotton + 2% spandex (slight stretch)  
**Fit:** Slim  

**Why This Garment?**
- Elastic fabric (different physics than structured)
- Tests lower-body fitting
- Highest volume category in retail
- Validates size scaling precision (waist/inseam critical)

**Technical Specs:**
```json
{
  "name": "Skinny Stretch Jeans - Blue",
  "brand": "[Sample]",
  "category": "pants",
  "color": "indigo",
  "material": "98% cotton, 2% spandex",
  "price_usd": 99.99,
  "base_size": "M",
  "size_chart": {
    "XS": { "scale_factor": 0.90, "length_adjust_cm": -3 },
    "S":  { "scale_factor": 0.95, "length_adjust_cm": -1 },
    "M":  { "scale_factor": 1.0,  "length_adjust_cm": 0 },
    "L":  { "scale_factor": 1.05, "length_adjust_cm": 2 },
    "XL": { "scale_factor": 1.12, "length_adjust_cm": 4 }
  },
  "fit_type": "slim",
  "fabric_properties": {
    "type": "spandex_blend",
    "weight_g_per_m2": 560,
    "stretch_percent": 2,
    "notes": "Slight stretch for comfort, hugs body"
  },
  "fitting_parameters": {
    "fit_offset_waist": 1,
    "fit_offset_hip": 1,
    "fit_offset_thigh": 2,
    "inseam_length_ratio": 0.50,
    "waist_fit_snug": true,
    "ankle_openness": 0.2
  }
}
```

**Fitting Validation:**
- [ ] Waist sits at natural hip
- [ ] Thigh fit snug but not penetrating
- [ ] Inseam length reaches ankle (proportional)
- [ ] Crotch doesn't clip into body geometry
- [ ] Ankle opening reasonable (not too wide, not too tight)
- [ ] Stretch fabric smooths out wrinkles in static fit

---

#### Garment 4: Oversized T-Shirt (Relaxed)

**Category:** Shirt / Casual  
**Fabric:** 100% cotton jersey  
**Fit:** Oversized  

**Why This Garment?**
- Common baseline for casual wear
- Tests loose/relaxed fitting (opposite of slim)
- Jersey fabric (knit, different properties than woven cotton)
- High volume, low price point

**Technical Specs:**
```json
{
  "name": "Oversized Cotton T-Shirt",
  "brand": "[Sample]",
  "category": "shirt",
  "color": "heather gray",
  "material": "100% cotton jersey",
  "price_usd": 39.99,
  "base_size": "M",
  "fit_type": "oversized",
  "fabric_properties": {
    "type": "cotton_knit",
    "weight_g_per_m2": 160,
    "stretch_percent": 8,
    "notes": "Soft knit, stretches and recovers"
  },
  "fitting_parameters": {
    "fit_offset_chest": 15,
    "fit_offset_waist": 12,
    "fit_offset_hip": 10,
    "sleeve_length_ratio": 0.50,
    "torso_length_ratio": 0.50,
    "oversized_intent": true
  }
}
```

**Fitting Validation:**
- [ ] Large chest clearance (loose, not tight)
- [ ] Sleeves reach mid-bicep (oversized length)
- [ ] Torso length extends to mid-hip
- [ ] Fabric drapes softly without clinging
- [ ] Neckline sits at base of neck (not choking)

---

#### Garment 5: Tailored Blazer (Structured + Details)

**Category:** Outerwear / Jacket  
**Fabric:** Wool blend  
**Fit:** Regular (structured, defined)  

**Why This Garment?**
- Complex geometry (collar, lapels, pockets, linings)
- Tests fitting on wider shoulders
- Premium/formal category (high value)
- Challenging for cloth sim (stiff fabric, detailed structure)

**Technical Specs:**
```json
{
  "name": "Tailored Wool Blazer",
  "brand": "[Sample]",
  "category": "jacket",
  "color": "charcoal",
  "material": "68% wool, 32% polyester",
  "price_usd": 299.99,
  "base_size": "M",
  "fit_type": "regular",
  "fabric_properties": {
    "type": "wool_blend",
    "weight_g_per_m2": 400,
    "stretch_percent": 0,
    "notes": "Stiff, structured, minimal drape"
  },
  "fitting_parameters": {
    "fit_offset_chest": 8,
    "fit_offset_waist": 6,
    "shoulder_width_ratio": 0.36,
    "jacket_length_ratio": 0.55,
    "lapel_width": 8,
    "collar_fit": 0.98,
    "armhole_depth_cm": 22,
    "pocket_placement": "standard"
  }
}
```

**Fitting Validation:**
- [ ] Shoulders align (seams at shoulder point, not drooping)
- [ ] Chest room for layering (~8cm clearance)
- [ ] Lapels lay flat against chest
- [ ] Jacket length reaches hip (professional look)
- [ ] Collar sits snug without choking
- [ ] Armhole depth accommodates arm movement
- [ ] Pockets don't penetrate body

---

### 3.2 Fitting Pipeline Workflow

**High-level flow from submission to live catalogue:**

```
[Partner Submission]
    ↓ (Garment file + metadata)
    ├─→ Auto-Validation (24 hours)
    │   ├─ Format check (zprj/md/obj valid?)
    │   ├─ Geometry check (manifold, reasonable size?)
    │   ├─ Metadata check (required fields present?)
    │   └─ Texture check (images present, not too large?)
    │   
    │   Result: PASS → proceed | FAIL → feedback to partner
    │
    ├─→ Fashion Tech QA (24-48 hours)
    │   ├─ Visual inspection (colors match, seams present?)
    │   ├─ Mesh cleanup (decimate if needed)
    │   ├─ Extract textures (normalize formats)
    │   └─ Register in database
    │
    ├─→ Fitting Algorithm Execution
    │   ├─ Shrinkwrap to reference body
    │   ├─ Validate sizing (XS-XL scale factors)
    │   ├─ Collision detection (check for clipping)
    │   └─ Generate fitted variants (per size)
    │
    ├─→ Animation Testing
    │   ├─ Bind to skeleton
    │   ├─ Play walk cycle
    │   ├─ Check for unrealistic deformation
    │   └─ Validate frame rate (target: 60fps)
    │
    ├─→ Web Viewer Export
    │   ├─ Generate optimized GLB files
    │   ├─ Create LOD variants (low-poly fallback)
    │   ├─ Compress textures
    │   └─ Test loading in viewer
    │
    ├─→ Final QA & Partner Sign-Off
    │   ├─ Visual review (looks good?)
    │   ├─ Fit validation (on 3+ diverse bodies)
    │   ├─ Partner approval (brand confirms appearance)
    │   └─ Generate final report
    │
    └─→ Live Deployment
        ├─ Copy to production S3
        ├─ Add to PostgreSQL catalogue
        ├─ Mark status "live"
        └─ Available in user-facing app ✓

Timeline: Submission → Live = 5-7 business days
```

---

## PART 4: WEEK 1 EXECUTION CHECKLIST

### Monday, March 18

- [ ] **Morning:** Read all docs (this file + TECHNICAL_ARCHITECTURE + CLOTH_SIMULATION_STRATEGY)
- [ ] **10 AM:** Weekly team standup (confirm dependencies with Blender Lead, Backend Lead, Frontend Lead)
- [ ] **Afternoon:** Set up Git repo for garment pipeline scripts
  ```bash
  mkdir -p ~/fashion-tech/garment-pipeline
  cd ~/fashion-tech/garment-pipeline
  git init
  mkdir -p scripts/{import,fit,validate,export}
  mkdir -p tests data/{sample_garments,fabric_params}
  ```
- [ ] Create Python virtual environment
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install trimesh pyvista numpy pillow
  ```

### Tuesday, March 19

- [ ] **Database Schema:**
  - [ ] Finalize PostgreSQL schema (garments, garment_sizes, garment_partners, validation_log tables)
  - [ ] Create schema SQL file: `schema.sql`
  - [ ] Test schema locally (create tables, insert sample record)
  - [ ] Get Backend Lead approval on schema design

- [ ] **S3 Structure:**
  - [ ] Define S3 bucket structure:
    ```
    s3://fashion-tech-garments/
      ├─ garments/
      │  ├─ {garment_uuid}/
      │  │  ├─ garment_base.glb          (cleaned mesh)
      │  │  ├─ textures/
      │  │  │  ├─ color_2k.jpg
      │  │  │  └─ normal_2k.jpg
      │  │  ├─ fitted_variants/
      │  │  │  ├─ fitted_XS.glb
      │  │  │  ├─ fitted_S.glb
      │  │  │  ├─ fitted_M.glb
      │  │  │  ├─ fitted_L.glb
      │  │  │  └─ fitted_XL.glb
      │  │  └─ metadata.json
      │  └─ ...
      ├─ partners/
      │  └─ submissions/       (partner uploads)
      └─ quality_reports/      (QA logs)
    ```
  - [ ] Request S3 bucket setup from Backend Lead
  - [ ] Document access policies (who can read/write)

### Wednesday, March 20

- [ ] **Import Pipeline (CLO3D):**
  - [ ] Write `import_clo3d.py` (parse .zprj, extract geometry + textures)
  - [ ] Test on 1 sample CLO3D file (from CLO3D demo library)
  - [ ] Document extraction process (what works, what fails)

- [ ] **Mesh Cleanup:**
  - [ ] Write `cleanup_mesh.py` (decimate, manifold check, smoothing)
  - [ ] Test on sample meshes (target: 5k-10k triangles)
  - [ ] Measure performance (time per mesh)

### Thursday, March 21

- [ ] **Fabric Parameters:**
  - [ ] Finalize fabric lookup table (cotton, silk, denim, spandex, blends)
  - [ ] Store as Python dict + JSON file
  - [ ] Document parameters (why these values?)
  - [ ] Create reference for Phase 2 cloth sim tuning

- [ ] **Garment Intake Checklist:**
  - [ ] Polish checklist (grammar, clarity)
  - [ ] Create metadata.json template
  - [ ] Generate sample submission ZIP (for partner reference)
  - [ ] Get CEO/Product approval on checklist format

### Friday, March 22

- [ ] **Status Report to CEO:**
  - [ ] Write summary (what's done, blockers, next week plan)
  - [ ] Include:
    - ✓ Database schema finalized
    - ✓ S3 structure designed (awaiting setup)
    - ✓ Import pipeline skeleton written
    - ✓ Fabric parameters table complete
    - ✓ Garment intake checklist ready for partners
    - Blockers: Reference body from Blender Lead (confirm status)
    - Next week: Begin fitting algorithm, test with sample garments

  - [ ] **Deliverables to Archive:**
    - [ ] `schema.sql` (database schema)
    - [ ] `fabric_parameters.py` + `fabric_parameters.json`
    - [ ] `import_clo3d.py` (working script)
    - [ ] `cleanup_mesh.py` (working script)
    - [ ] `Garment_Intake_Checklist.md` (final version)
    - [ ] `WEEK1_IMPLEMENTATION.md` (this document)

  - [ ] **Commit to Git:**
    ```bash
    git add -A
    git commit -m "Week 1: Infrastructure setup, import pipeline, garment intake checklist"
    git push origin main
    ```

---

## PART 5: PARTNER OUTREACH MATERIALS

### Email Template: Initial Outreach (Week 1, Friday)

**Subject:** Fashion Tech Virtual Try-On Partnership Opportunity

---

Dear [Partner Name],

We're excited to introduce **Fashion Tech**, a new virtual try-on platform for online retail. We're partnering with leading fashion brands to bring realistic 3D garment visualization directly to e-commerce.

**What We Do:**
- Convert your 3D garment assets (CLO3D, Marvelous Designer) into web-ready models
- Integrate with your product catalog
- Enable customers to see how garments fit *before* they buy
- Reduce returns, increase customer confidence

**Why This Matters for [Partner Name]:**
- Return rates drop ~15-20% with accurate virtual try-on (industry data)
- Your existing 3D design assets → immediate value (no new files needed)
- Simple integration (we handle the heavy lifting)
- Exclusive early-access in [Region]

**Next Steps:**

We'd love to explore a partnership. Can we schedule a 30-minute technical discovery call for **Week 2**?

**In that call, we'll discuss:**
1. Your current 3D workflow (CLO3D, Marvelous Designer, or other tools)
2. Sample garments for a pilot program (5-10 pieces)
3. Technical requirements and timeline (4-week integration for MVP)
4. Partnership terms and revenue share

**What You Need to Prepare:**
- Sample CLO3D (`.zprj`) or Marvelous Designer (`.md`) files (3-5 garments)
- Basic size charts (XS-XL with scale factors)
- Primary contact for technical coordination

**Attached:**
- `Garment_Intake_Checklist.md` (what we need from you)
- `Asset_Compatibility_Matrix.md` (what file formats we support)
- `Partnership_Timeline.md` (4-week pilot roadmap)

**Our Commitment:**
- Dedicated technical support throughout integration
- <24h response time to questions
- Quality guarantee: we validate every garment before launch
- Revenue split: [Details from CEO]

Looking forward to building this together!

Best regards,  
[Fashion Tech Partnerships Team]

---

### Zara/H&M-Specific Angles

**For Zara:**
- Fast fashion speed advantage: "Your 3D assets are already validated. We just need to convert to web format."
- Scale: "If the pilot works, we can onboard thousands of garments in 2-3 months."
- Retail edge: "Be first in your market with virtual try-on."

**For H&M:**
- Sustainability: "Better fit = fewer returns = less waste."
- Inclusivity: "Show garments on diverse body types, not just standard mannequins."
- Global reach: "Translate easily to all H&M markets."

---

## PART 6: RISK MITIGATION & ESCALATION

### Known Blockers (>2h escalation to CEO)

**Blocker 1: Reference Body Not Available**
- **Status:** TBD (confirm with Blender Lead, Week 1 kickoff)
- **Impact:** High (blocks fitting algorithm development)
- **Mitigation:** Start with synthetic placeholder body, iterate when real body available
- **Escalation Trigger:** If Blender Lead can't provide by end of Week 1 → alert CEO

**Blocker 2: S3 Setup Delayed**
- **Status:** Awaiting Backend Lead confirmation
- **Impact:** Medium (can use local disk temporarily)
- **Mitigation:** Develop with local file structure, migrate to S3 later
- **Timeline:** If not ready by Wed → switch to local dev, plan migration for Week 2

**Blocker 3: CLO3D Files Unavailable**
- **Status:** Planning to use CLO3D demo library
- **Impact:** Low (open-source garment samples available)
- **Mitigation:** Use sample files from CLO3D public library, test import pipeline
- **Escalation Trigger:** If no samples work → request from Zara/H&M in outreach

---

## Appendices

### A: File Formats Quick Reference

| Format | Extension | Pros | Cons | Use Case |
|--------|-----------|------|------|----------|
| CLO3D | `.zprj` | Industry standard, parametric sizing | Proprietary, requires CLO3D to view | Primary target for Zara/H&M |
| Marvelous Designer | `.md` | Professional quality | Proprietary, expensive tool | Secondary target |
| OBJ | `.obj` | Universal, simple | No animation, no materials | Intermediate format (we convert here) |
| FBX | `.fbx` | Animation support, Blender-friendly | Larger file size | Blender editing, animation |
| GLB | `.glb` | Web-optimized, compressed | Limited material support | Final web viewer format |

---

### B: Performance Baselines (Target)

| Metric | Target | Notes |
|--------|--------|-------|
| Import (CLO3D → OBJ) | <30 sec | Per garment |
| Mesh cleanup (decimation) | <60 sec | From 20k to 10k triangles |
| Shrinkwrap fitting | <1 sec | Per garment, per body |
| Collision detection | <2 sec | Per fitted garment |
| Web export (GLB generation) | <5 sec | Per garment, per size |
| **Total: Import → Live** | <5 min | End-to-end per garment |

---

### C: Success Metrics (Week 8)

**By end of Phase 1, we measure success by:**

1. ✅ **50+ garments in catalogue**
   - Mix of categories (shirts, dresses, pants, jackets)
   - Diverse brands (5+ partners)
   - All sizes (XS-XL)

2. ✅ **Import success rate >95%**
   - Auto-validated, minimal manual rework
   - CLO3D files parse cleanly
   - Textures extract correctly

3. ✅ **Fitting quality: <10% clipping**
   - Visual inspection on web viewer
   - No mesh penetration
   - All sizes look proportional

4. ✅ **<5 min per garment (end-to-end)**
   - From submission → live
   - Including QA review time

5. ✅ **5+ partners recruited & onboarded**
   - Zara/H&M confirmed
   - Others in pipeline
   - Pilot garments submitted

6. ✅ **Web viewer integration complete**
   - Garments load smoothly
   - Animation at 60fps
   - User try-on flow works end-to-end

---

### D: Contact Matrix

| Role | Name | Email | Phone | Availability |
|------|------|-------|-------|--------------|
| Blender Lead | [TBD] | [TBD] | [TBD] | Mon/Wed standup + ad-hoc |
| Backend Lead | [TBD] | [TBD] | [TBD] | Mon/Wed standup + ad-hoc |
| Frontend Lead | [TBD] | [TBD] | [TBD] | Mon/Wed standup, Week 5+ |
| 3D Scanning Lead | [TBD] | [TBD] | [TBD] | Ad-hoc, Week 4+ |
| CEO | [TBD] | [TBD] | [TBD] | Friday 4 PM status, blockers anytime |

---

## Summary

**Week 1 Outcome:**

By Friday, March 22, we will have:

1. ✅ **Infrastructure ready:**
   - PostgreSQL schema designed
   - S3 structure planned
   - Git repo initialized

2. ✅ **Partner outreach materials:**
   - Garment Intake Checklist (final)
   - Asset Compatibility Matrix
   - SLA & Timeline (Week 4 pilot)

3. ✅ **Technical foundation:**
   - CLO3D import script (working)
   - Mesh cleanup script (working)
   - Fabric parameters table (complete)

4. ✅ **MVP garment specs:**
   - 5 sample garments defined (shirt, dress, pants, t-shirt, blazer)
   - Metadata templates ready
   - Validation criteria documented

5. ✅ **Zara/H&M outreach:**
   - Email templates prepared
   - Discovery call scheduled (Week 2)
   - Assets & expectations documented

**What Happens Next (Week 2-3):**
- Week 2: Begin fitting algorithm development + first Zara/H&M technical call
- Week 3: Import first 5 sample garments, validate fitting quality
- Week 4: Diverse body type validation, begin B2B partner recruitment

**Escalation Triggers:**
- Reference body from Blender Lead > 2h delay → CEO alert
- S3 setup > 2h delay → CEO alert
- CLO3D parsing fails on multiple test files → Technical review with CEO

---

**Document Version:** 1.0  
**Created:** 2026-03-18  
**Status:** READY FOR EXECUTION  
**Next Review:** End of Week 1 (March 22, 2026)

---

## Contact & Questions

**Questions about this spec?**
- Slack: #garment-pipeline
- Email: [Fashion Tech Tech Lead]
- Schedule: 1:1 available Mon-Fri 9 AM - 5 PM

**For partners:**
- Website: [fashion-tech.com/partners](http://fashion-tech.com/partners)
- Email: partnerships@fashion-tech.com
- Phone: [TBD]

---

*This document is the foundation for Week 1 execution. All tasks are sized for completion by EOD Friday, March 22, 2026.*
