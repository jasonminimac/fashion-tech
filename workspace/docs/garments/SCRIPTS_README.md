# Garment Pipeline Scripts - Week 1 Deliverables

This folder contains production-ready Python scripts for Week 1 of the garment & cloth simulation pipeline.

## Scripts Included

### 1. `import_clo3d.py`
**Purpose:** Parse CLO3D `.zprj` files and extract geometry + textures  
**Status:** Ready to run  
**Dependencies:** zipfile (stdlib), xml.etree (stdlib)  

**Usage:**
```bash
python import_clo3d.py garment.zprj --output ./extracted/
```

**Output:**
```
./extracted/
├─ geometry.obj           (3D mesh)
├─ metadata.json          (garment metadata)
└─ textures/
   ├─ color.jpg
   ├─ normal.jpg
   └─ ...
```

---

### 2. `cleanup_mesh.py`
**Purpose:** Decimates meshes, validates topology, smooths normals  
**Status:** Ready with dependencies  
**Dependencies:** trimesh, numpy, pyvista  

**Installation:**
```bash
pip install trimesh numpy pyvista
```

**Usage:**
```bash
python cleanup_mesh.py geometry.obj --target-triangles 8000 --output cleaned.obj
```

**Features:**
- Decimates to target triangle count
- Validates manifold topology
- Removes duplicate vertices
- Smooths normals
- Performance: <60s for typical garments

---

### 3. `database_schema.sql`
**Purpose:** PostgreSQL schema for garment metadata  
**Status:** Production-ready  

**Installation:**
```bash
psql -U postgres -d fashion_tech < database_schema.sql
```

**Tables:**
- `garments` — Master garment records
- `garment_sizes` — Per-size scaling data
- `garment_partners` — Partner tracking
- `garment_validation_log` — QA history

---

### 4. `fabric_parameters.py`
**Purpose:** Fabric lookup table for Phase 2 cloth sim  
**Status:** Complete  

**Usage:**
```python
from fabric_parameters import FABRIC_PARAMETERS

cotton_props = FABRIC_PARAMETERS["cotton"]
# Access: mass_g_per_m2, damping, elasticity, etc.
```

**Supported Fabrics:**
- cotton, cotton_light
- silk
- denim
- spandex
- polyester
- blend_cotton_poly
- linen

---

## Week 1 Integration Workflow

### Day 1-2: Infrastructure Setup

```bash
# 1. Clone/init repo
mkdir -p ~/fashion-tech/garment-pipeline
cd ~/fashion-tech/garment-pipeline

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install trimesh numpy pyvista

# 3. Create directory structure
mkdir -p scripts/{import,fit,validate,export}
mkdir -p tests data/{sample_garments,fabric_params}

# 4. Copy scripts
cp import_clo3d.py scripts/import/
cp cleanup_mesh.py scripts/import/
cp fabric_parameters.py scripts/export/
```

### Day 3-4: Database Setup

```bash
# 1. Create PostgreSQL database
createdb fashion_tech

# 2. Load schema
psql -U postgres -d fashion_tech < database_schema.sql

# 3. Verify tables
psql -U postgres -d fashion_tech -c "\dt"
```

### Day 5: Test with Sample Garments

```bash
# 1. Download sample CLO3D file (from CLO3D demo library)
wget https://demo.clo3d.com/sample_garment.zprj

# 2. Import
python scripts/import/import_clo3d.py sample_garment.zprj --output ./extracted/

# 3. Cleanup
python scripts/import/cleanup_mesh.py extracted/geometry.obj \
  --target-triangles 8000 \
  --output extracted/geometry_cleaned.obj

# 4. Verify results
ls -lh extracted/
```

---

## Next Steps (Week 2)

1. **Fitting Algorithm** (`fit_garment_to_body.py`)
   - Shrinkwrap implementation
   - Collision detection
   - Size scaling

2. **Animation Integration** (`bind_garment_to_skeleton.py`)
   - Blender armature binding
   - Weight painting automation

3. **Web Export** (`export_to_glb.py`)
   - Mesh optimization for web
   - Texture compression
   - LOD variant generation

---

## Troubleshooting

### ImportError: No module named 'trimesh'
```bash
source venv/bin/activate
pip install trimesh
```

### CLO3D file can't be parsed
- Verify file is valid `.zprj` (it's a ZIP archive)
- Check for embedded `root.xml` and `geometry.obj`
- Extract manually: `unzip -l garment.zprj`

### PostgreSQL connection error
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT 1"

# If fails, start service:
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

---

## References

- **CLO3D Format:** https://www.clo3d.com/resources
- **Trimesh Docs:** https://trimesh.org/
- **Blender Python API:** https://docs.blender.org/api/current/

---

## Questions?

Slack: #garment-pipeline  
Email: [Fashion Tech Tech Lead]
