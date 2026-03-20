# Garment Data Model & API Reference

**Document Owner:** Clothing & Physics Lead  
**Date:** 2026-03-17  
**Audience:** Backend Engineers, Frontend Engineers, B2B Partners  

---

## Quick Reference: Garment Data Structure

### Core Garment Record (PostgreSQL)

```sql
CREATE TABLE garments (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  brand VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,  -- shirt, dress, pants, jacket, etc.
  sku VARCHAR(100),
  description TEXT,
  color VARCHAR(50),
  material VARCHAR(100),
  price_usd DECIMAL(10, 2),
  retail_url TEXT,
  
  -- Geometry References
  base_model_url TEXT,  -- S3 path to GLB file
  texture_url TEXT,
  normal_map_url TEXT,
  roughness_map_url TEXT,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(50) DEFAULT 'draft',  -- draft, submitted, qa_review, live, archived
  
  -- JSON columns for complex structures
  sizing JSONB,  -- size_chart, fit_type, stretch_factor, etc.
  cloth_physics JSONB,  -- fabric params
  fitting_parameters JSONB,  -- fit offsets, clearances
  quality_metrics JSONB,  -- validation results
  metadata JSONB  -- custom partner data
);

CREATE INDEX garments_brand_category ON garments(brand, category);
CREATE INDEX garments_status ON garments(status);
```

### Sizing Schema (JSONB)

```json
{
  "size_chart": {
    "XS": {
      "scale_factor": 0.85,
      "length_adjust_cm": -5,
      "notes": "Very small, may run large"
    },
    "S": {
      "scale_factor": 0.92,
      "length_adjust_cm": -2,
      "notes": ""
    },
    "M": {
      "scale_factor": 1.0,
      "length_adjust_cm": 0,
      "notes": "Reference size"
    },
    "L": {
      "scale_factor": 1.08,
      "length_adjust_cm": 2,
      "notes": ""
    },
    "XL": {
      "scale_factor": 1.16,
      "length_adjust_cm": 5,
      "notes": "May run small"
    }
  },
  "fit_type": "regular",  -- regular, slim, relaxed, oversized, athletic
  "stretch_factor": 1.15,  -- 1.0 = no stretch, 1.2 = 20% elastic
  "recommended_body_types": ["slim", "athletic", "average"],
  "size_notes": "Runs true to size. Suggest one size up for relaxed fit."
}
```

### Cloth Physics Schema (JSONB)

```json
{
  "fabric_type": "cotton",
  "weight_g_per_m2": 150,
  "thickness_mm": 0.5,
  "elasticity": 0.1,
  "damping": 0.05,
  "collision_margin_cm": 0.5,
  "wind_force": 0.2,
  "wrinkle_intensity": 0.7,
  "notes": "Heavy cotton, settles quickly in sim"
}
```

### Fitting Parameters Schema (JSONB)

```json
{
  "fit_offset_chest": 5,
  "fit_offset_waist": 3,
  "fit_offset_hip": 4,
  "sleeve_length_ratio": 0.45,
  "torso_length_ratio": 0.35,
  "collar_fit": 0.95,
  "shoulder_width_ratio": 0.35,
  "armhole_depth_cm": 20
}
```

---

## REST API Reference

### Partner Submission Endpoint

**POST** `/api/v1/partners/{partner_id}/garments`

**Request:**

```json
{
  "name": "Classic White Shirt",
  "brand": "Brand Name",
  "category": "shirt",
  "sku": "BRAND-SKU-123",
  "color": "white",
  "material": "cotton",
  "price_usd": 79.99,
  "retail_url": "https://brand.com/products/...",
  "garment_file": "<binary file data>",
  "garment_file_format": "clo3d",  -- clo3d, marvelous_designer, obj, fbx, glb
  "size_chart": {
    "XS": {"scale_factor": 0.85, "length_adjust_cm": -5},
    "S": {"scale_factor": 0.92, "length_adjust_cm": -2},
    "M": {"scale_factor": 1.0, "length_adjust_cm": 0},
    "L": {"scale_factor": 1.08, "length_adjust_cm": 2},
    "XL": {"scale_factor": 1.16, "length_adjust_cm": 5}
  },
  "fit_type": "regular",
  "stretch_factor": 1.15,
  "fabric_type": "cotton",
  "weight_g_per_m2": 150,
  "recommended_body_types": ["slim", "athletic", "average"],
  "notes": "Premium cotton shirt, runs true to size"
}
```

**Response (200 OK):**

```json
{
  "garment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "submitted",
  "validation": {
    "passed": true,
    "warnings": [
      "Mesh has 45k triangles; will be decimated to 8k for web viewer"
    ],
    "errors": []
  },
  "next_steps": [
    "System will auto-import and validate geometry",
    "Clothing Lead will perform QA review (24-48 hours)",
    "You'll receive email when garment is live"
  ]
}
```

**Response (400 Bad Request):**

```json
{
  "status": "submission_failed",
  "validation": {
    "errors": [
      "File format not recognized",
      "Category must be one of: shirt, dress, pants, jacket, ...",
      "Retail URL is invalid"
    ],
    "warnings": []
  }
}
```

### Get Garment Metadata

**GET** `/api/v1/garments/{garment_id}`

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Classic White Shirt",
  "brand": "Brand Name",
  "category": "shirt",
  "color": "white",
  "price_usd": 79.99,
  "sizing": { ... },
  "cloth_physics": { ... },
  "fitting_parameters": { ... },
  "status": "live",
  "created_at": "2026-03-17T10:30:00Z"
}
```

### Search Garments

**GET** `/api/v1/garments?category=shirt&brand=Nike&color=white&limit=20`

**Response:**

```json
{
  "results": [
    { "id": "...", "name": "...", "brand": "...", ... },
    { ... }
  ],
  "total": 156,
  "limit": 20,
  "offset": 0
}
```

### Get Garment 3D Model (for Web Viewer)

**GET** `/api/v1/garments/{garment_id}/model?size=M`

**Response:** Binary GLB file (Content-Type: model/gltf-binary)

---

## Internal APIs (Clothing Lead to Backend Lead)

### Database Insert (Garment Record)

```python
# Backend Engineer implements this
def create_garment(
    name: str,
    brand: str,
    category: str,
    sku: str,
    color: str,
    material: str,
    price_usd: float,
    retail_url: str,
    base_model_url: str,  # S3 path
    texture_url: str,
    sizing: dict,
    cloth_physics: dict,
    fitting_parameters: dict,
) -> uuid.UUID:
    """
    Create new garment record in database.
    
    Returns:
        garment_id: UUID for the newly created garment
    """
    pass
```

### S3 Upload Helper

```python
# Backend Engineer implements this
def upload_garment_assets(
    garment_id: uuid.UUID,
    model_glb: bytes,
    texture_jpg: bytes,
    normal_map: bytes,
    roughness_map: bytes,
) -> dict:
    """
    Upload garment assets to S3.
    
    Returns:
        {
          "model_url": "s3://garments/...",
          "texture_url": "s3://garments/...",
          ...
        }
    """
    pass
```

### Update Garment Status

```python
# Backend Engineer implements this
def update_garment_status(
    garment_id: uuid.UUID,
    new_status: str,  # draft, submitted, qa_review, live, archived
) -> None:
    """Update garment status in database."""
    pass
```

---

## File Format Specifications

### GLB (Web Model Format)

**What:** Binary glTF format with embedded textures and meshes.

**Constraints:**
- Max file size: 50 MB (for web loading)
- Target triangle count: 5,000-10,000 (balance quality vs. performance)
- LOD variants: Create 3 variants (high, medium, low poly)
  - High: 10k triangles (desktop)
  - Medium: 5k triangles (tablet)
  - Low: 2k triangles (mobile)

**Tools to generate:**
- Blender: File → Export → glTF Binary (.glb)
- Python: `pygltflib`, `trimesh`, `pyvista`

### Texture Specifications

**Format:** PNG or JPG

**Maps:**
- **Color/Diffuse:** RGB, 2048×2048 recommended
- **Normal:** RGB, derived from color or scan
- **Roughness:** Grayscale, 1024×1024
- **Metallic:** Grayscale (rarely used for fashion)

**Compression:**
- Use tools: `imagemagick`, `tinypng`, or similar
- Target: <500KB per texture for fast web loading

---

## Partner Submission Checklist

**Manufacturers, use this checklist when submitting garments:**

- [ ] Garment is designed in CLO3D, Marvelous Designer, or has 3D model
- [ ] File format is one of: .zprj, .md, .obj, .fbx, .glb
- [ ] All required metadata provided: name, brand, category, size chart, fabric type
- [ ] Size chart defined for XS-XL (scale factors or custom dimensions)
- [ ] Retail product URL is correct and live
- [ ] Price is accurate in USD
- [ ] Textures are included (or garment uses simple color)
- [ ] Notes on fit (runs large, small, true to size, etc.)

**Submit via:** `POST /api/v1/partners/{partner_id}/garments`

---

## QA Validation Checklist

**Clothing Lead, review each garment before marking live:**

### Geometry
- [ ] No non-manifold topology (holes, bad normals)
- [ ] No duplicate vertices or faces
- [ ] Mesh is manifold (watertight)
- [ ] Triangle count reasonable (<15k for desktop)

### Fitting
- [ ] Garment fitted to reference body (T-pose) looks good
- [ ] No visible clipping or penetration with body
- [ ] Fit validated on 3+ diverse body types
- [ ] Size scaling (XS-XL) looks proportional

### Visuals
- [ ] Textures load correctly, no seams
- [ ] Colors accurate to partner's specification
- [ ] Normal maps provide good shading (not flat-looking)
- [ ] Lighting looks natural in web viewer

### Animation
- [ ] Garment animates smoothly with body (walk cycle)
- [ ] No stretching or weird deformations
- [ ] Sleeves, hems move naturally

### Metadata
- [ ] All fields filled (name, brand, category, price, etc.)
- [ ] Size chart is accurate (matches partner's specs)
- [ ] Fabric properties sensible (not 0 weight, etc.)
- [ ] Fit notes helpful (runs large, true to size, etc.)

### Partner Communication
- [ ] Partner has approved final appearance
- [ ] Any issues documented in notes field
- [ ] QA feedback provided to partner (if revision needed)

---

## Common Issues & Resolutions

### Issue: Garment Clipping with Body

**Cause:** Shrinkwrap fit offset too small, or garment not sized correctly.

**Fix:**
- Increase `fit_offset_chest/waist/hip` values
- Check size scaling (scale_factor in size_chart)
- Try different offset values: 3, 5, 7 cm
- If still issues, may need manual lattice deformation

### Issue: Garment Looks Distorted After Import

**Cause:** Mesh has non-manifold topology or bad normals.

**Fix:**
- Run mesh cleanup: `cleanup_mesh.py`
- Check for duplicate vertices, bad normals
- Reimport from source file (CLO3D/MD)
- If all else fails, may need manual rework by 3D artist

### Issue: Texture Not Showing

**Cause:** Texture path incorrect in import, or file missing.

**Fix:**
- Verify texture URL in garment metadata
- Check S3 bucket (texture file uploaded?)
- Re-upload texture to S3
- Update garment record with correct texture_url

### Issue: Garment Too High Poly (slow to load)

**Cause:** Original mesh has 50k+ triangles.

**Fix:**
- Run mesh decimation: `cleanup_mesh.py --target_triangles 8000`
- Generate LOD variants (high, medium, low poly)
- Test load time in web viewer
- Aim for <2 second load time

---

## Example: End-to-End Garment Submission

**Partner: Nike**

1. **Nike designs shirt in CLO3D**, exports to OBJ + textures
2. **Nike calls:** `POST /api/v1/partners/nike/garments`
   - Attach .obj file
   - Attach textures (color.jpg, normal.jpg)
   - Metadata: name="Classic Nike T", category="shirt", etc.
3. **Backend validates:** File format OK, metadata complete
4. **Clothing Lead auto-imports:**
   - Parse OBJ, cleanup mesh
   - Fit to reference body (T-pose)
   - Extract fitting parameters
5. **Clothing Lead QA reviews:**
   - Check visual quality
   - Test on 3 body types
   - Approve or request revision
6. **Garment goes live:**
   - Deployed to database + S3
   - Searchable in web viewer
   - Users can try-on
7. **User tries on:**
   - Scans their body
   - Selects Nike T shirt
   - System fits shirt to user's body + size
   - User sees animated preview

---

## Troubleshooting

### "Import failed: File not recognized"

**Check:**
- Is file extension correct? (.zprj for CLO3D, .md for MD, etc.)
- Is file actually in that format? (use file utility: `file garment.zprj`)
- File not corrupted? (try opening in original tool)

### "Validation error: Mesh is not manifold"

**Check:**
- Does mesh have holes or open edges?
- Use tool: `meshlab` or `meshmixer` to inspect
- Run cleanup: `cleanup_mesh.py --verbose`
- Contact partner to re-export from CLO3D

### "Garment looks wrong after fit"

**Check:**
- Is reference body correct? (right skeleton, rigging)
- Are fitting_parameters reasonable? (5-10 cm clearance typical)
- Try different shrinkwrap offset
- Manual visual inspection in Blender

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Contact:** Clothing Lead for questions on this API
