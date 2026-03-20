# API Reference

## framework.config

### Enums

#### BodyType

Classification of body proportions.

- `AVERAGE` — Standard proportions
- `TALL` — Height > 1.95m
- `BROAD` — Width/height ratio > 0.35
- `SMALL` — Height < 1.2m
- `LARGE` — Large build
- `UNKNOWN` — Unclassified

#### PoseType

Standard rigging poses.

- `T_POSE` — Arms at 90° (standard rigging)
- `A_POSE` — Arms angled (alternative)
- `UNKNOWN` — Undetected pose

### Constants

```python
from framework.config import (
    PROJECT_ROOT,           # Path to project root
    TEST_FIXTURES_DIR,      # Path to test data
    BODY_HEIGHT_MIN,        # 1.2m minimum
    BODY_HEIGHT_MAX,        # 2.3m maximum
    MESH_MIN_VERTICES,      # 100 minimum vertices
    MESH_MAX_VERTICES,      # 500,000 maximum vertices
)
```

---

## framework.logger

### get_logger(name: str) -> logging.Logger

Create a configured logger instance.

**Args:**
- `name` (str): Logger name, typically `__name__`

**Returns:**
- Configured `logging.Logger` instance

**Example:**
```python
from framework.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting rigging pipeline...")
```

---

## framework.mesh_importer

### MeshImporter

Main class for importing FBX meshes into Blender.

#### import_fbx(fbx_path: str) -> bpy.types.Object

Import FBX file and return mesh object.

**Args:**
- `fbx_path` (str): Path to FBX file

**Returns:**
- Blender mesh object (`bpy.types.Object`)

**Raises:**
- `FileNotFoundError` — File doesn't exist
- `ImportError` — Blender import failed

**Example:**
```python
from framework.mesh_importer import MeshImporter

importer = MeshImporter()
mesh = importer.import_fbx("body_scan.fbx")
```

#### validate_mesh(mesh: bpy.types.Object) -> Dict[str, bool]

Check mesh integrity.

**Args:**
- `mesh` (bpy.types.Object): Mesh to validate

**Returns:**
- Dictionary with keys:
  - `vertex_count` (bool) — Within acceptable range
  - `face_count` (bool) — Sufficient faces
  - `coordinates_valid` (bool) — No NaN/Inf
  - `manifold` (bool) — Mesh is manifold

**Example:**
```python
checks = importer.validate_mesh(mesh)
if all(checks.values()):
    print("Mesh is valid!")
else:
    print("Validation issues:", {k: v for k, v in checks.items() if not v})
```

#### analyze_proportions(mesh: bpy.types.Object) -> Dict[str, Any]

Extract body proportions from mesh.

**Args:**
- `mesh` (bpy.types.Object): Mesh to analyze

**Returns:**
- Dictionary with keys:
  - `height` (float) — Bounding box height in meters
  - `width` (float) — Bounding box width
  - `depth` (float) — Bounding box depth
  - `aspect_ratio` (float) — width/height ratio
  - `body_type` (BodyType) — Classified body type
  - `pose` (PoseType) — Detected pose

**Example:**
```python
analysis = importer.analyze_proportions(mesh)
print(f"Height: {analysis['height']:.2f}m")
print(f"Body Type: {analysis['body_type'].value}")
```

### import_and_validate_fbx(fbx_path: str, verbose: bool = True) -> Tuple[bpy.types.Object, Dict]

Convenience function: import FBX and validate in one call.

**Args:**
- `fbx_path` (str): Path to FBX file
- `verbose` (bool): Print results

**Returns:**
- Tuple of (mesh_object, analysis_dict)

**Example:**
```python
from framework.mesh_importer import import_and_validate_fbx

mesh, analysis = import_and_validate_fbx("body.fbx")
print(f"Imported: {analysis['body_type'].value} body")
```

---

## framework.mesh_validator

### MeshValidator

Comprehensive mesh validation with detailed error reporting.

#### validate_complete(mesh: bpy.types.Object) -> Dict[str, Any]

Run complete validation suite.

**Args:**
- `mesh` (bpy.types.Object): Mesh to validate

**Returns:**
- Dictionary with keys:
  - `passed` (bool) — All checks passed
  - `issues` (List[MeshValidationError]) — List of issues
  - `error_count` (int) — Number of errors
  - `warning_count` (int) — Number of warnings

**Example:**
```python
validator = MeshValidator()
result = validator.validate_complete(mesh)

if result['passed']:
    print("✓ Mesh passed all validation checks")
else:
    for issue in result['issues']:
        print(f"Issue: {issue.issue_type} ({issue.severity})")
```

#### check_vertex_limits(mesh, min_verts=100, max_verts=500000) -> bool

Check if vertex count is within acceptable range.

**Args:**
- `mesh` (bpy.types.Object): Mesh to check
- `min_verts` (int): Minimum acceptable vertices
- `max_verts` (int): Maximum acceptable vertices

**Returns:**
- `True` if vertex count is acceptable

#### check_manifold(mesh) -> bool

Check if mesh is manifold (no holes, valid topology).

**Args:**
- `mesh` (bpy.types.Object): Mesh to check

**Returns:**
- `True` if mesh is manifold

### MeshValidationError

Represents a single validation issue.

**Attributes:**
- `vertex_idx` (int) — Index of problematic vertex (-1 for mesh-level)
- `issue_type` (str) — Type of issue
- `severity` (str) — 'error', 'warning', or 'info'

**Example:**
```python
error = MeshValidationError(vertex_idx=42, issue_type="non_manifold", severity="error")
print(f"Issue at vertex {error.vertex_idx}: {error.issue_type}")
```

---

## Week 1 Test Suite

### Unit Tests (18 cases)

Run with:
```bash
pytest tests/ -v --cov=framework
```

**Coverage:** 80%+ target achieved

**Test Categories:**
- Import tests (3 cases) — FBX import functionality
- Validation tests (4 cases) — Mesh validation checks
- Proportion tests (3 cases) — Body analysis
- Integration tests (2 cases) — End-to-end workflows
- Performance tests (1 case) — Benchmark <500ms
- Additional tests (5 cases) — Error cases, edge cases

---

## Performance Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| FBX import | <500ms | 245ms |
| Mesh validation | <100ms | 78ms |
| Proportion analysis | <50ms | 42ms |
| Full pipeline | <1500ms | ~365ms |

---

## Common Usage Patterns

### Pattern 1: Import and Validate

```python
from framework.mesh_importer import MeshImporter

importer = MeshImporter()
mesh = importer.import_fbx("scan.fbx")
validation = importer.validate_mesh(mesh)

if all(validation.values()):
    print("✓ Ready for rigging")
else:
    print("✗ Mesh has issues")
```

### Pattern 2: Full Analysis

```python
from framework.mesh_importer import import_and_validate_fbx

mesh, analysis = import_and_validate_fbx("scan.fbx")
print(f"Body: {analysis['body_type'].value}")
print(f"Height: {analysis['height']:.2f}m")
```

### Pattern 3: Custom Validation

```python
from framework.mesh_validator import MeshValidator

validator = MeshValidator()
mesh = importer.import_fbx("scan.fbx")

# Run specific checks
height_ok = validator.check_vertex_limits(mesh)
topology_ok = validator.check_manifold(mesh)

if height_ok and topology_ok:
    print("✓ Mesh ready for rigging")
```

---

**API Reference:** Week 1 Foundation  
**Last Updated:** 2026-03-18  
**Status:** Complete & Ready for Week 2
