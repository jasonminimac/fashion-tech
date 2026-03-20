# FashionTech 3D Processing Pipeline

**Version:** 0.1.0  
**Status:** Week 1 MVP Foundation  
**Last Updated:** 2026-03-18

## Overview

Python-based point cloud processing pipeline for converting raw iPhone LiDAR scans into optimized 3D meshes suitable for garment simulation and AR try-on.

## Quick Start

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Basic Usage

```bash
# Process a single scan
python -m pipeline.pipeline input_scan.ply scan_001 ./output

# With configuration
python -c "
from pipeline import ScanProcessingPipeline
pipeline = ScanProcessingPipeline({
    'voxel_size': 0.005,  # 5mm downsampling
    'mesh_depth': 10,      # Finer detail
})
result = pipeline.process('input.ply', 'scan_001', './output')
print(result)
"
```

## Pipeline Stages

1. **Cleaning** — Statistical outlier removal, confidence filtering
2. **Downsampling** — Voxel grid reduction
3. **Normal Estimation** — Vertex normals for reconstruction
4. **Meshing** — Poisson surface reconstruction
5. **Cleanup** — Degenerate triangle removal, optimization
6. **Export** — GLB, OBJ, PLY formats

## Configuration

Default configuration in `ScanProcessingPipeline._default_config()`:

```python
{
    "cleaning": {
        "outlier_nb_neighbors": 20,
        "outlier_std_ratio": 2.0,
        "confidence_threshold": 0.5,
    },
    "voxel_size": 0.01,      # 10mm
    "mesh_depth": 9,          # Poisson depth
}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=pipeline --cov-report=html
```

## Output Files

For each scan, the pipeline produces:
- `{scan_id}.glb` — glTF 2.0 binary mesh (web-compatible)
- `{scan_id}.obj` — Wavefront OBJ mesh (fallback)
- `{scan_id}.ply` — PLY point cloud mesh
- `{scan_id}_mesh_raw.ply` — Debug output (before cleanup)

## Performance Targets (Week 1)

- Point cloud → mesh: **< 3 minutes** (development)
- Mesh size: **< 5MB** (glTF compressed)
- Vertex count: **50k - 200k** (body scan typical)
- Processing error: **< 5mm** reconstruction accuracy

## Dependencies

- **open3d** — Point cloud processing
- **numpy** — Numerical computation
- **scipy** — Scientific computing
- **trimesh** — Mesh utilities
- **pytest** — Testing framework

## Known Limitations (Week 1)

- ❌ No real-time preview (added Week 2)
- ❌ No pose normalization (Week 3)
- ❌ No body segmentation (Week 3)
- ❌ No rigging integration (Week 4)
- ⚠️ FBX export via OBJ proxy (true FBX requires external lib)

## Roadmap

- **Week 2** — Integration with backend API, S3 upload
- **Week 3** — Body segmentation, pose normalization
- **Week 4** — Blender rigging automation, joint extraction
- **Phase 2** — NeRF-based reconstruction, real-time simulation

## References

- Architecture: `/workspace/docs/DISCOVERY.md`
- Implementation spec: `/workspace/docs/scanning/WEEK1_IMPLEMENTATION.md`
- Open3D docs: http://www.open3d.org/docs/

---

**Maintainer:** 3D Scanning Lead  
**Contact:** team@fashiontech.local
