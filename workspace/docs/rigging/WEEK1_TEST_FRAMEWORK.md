# Week 1 Test Framework & Validation Spec

**Date:** 2026-03-18  
**Phase:** Week 1 Foundation Testing  
**Owner:** Blender Rigging & Animation Engineer  

---

## Overview

This document provides the **complete test framework specification** for Week 1 deliverables, including:
- Unit test cases with expected outputs
- Integration test scenarios
- Test data fixtures (synthetic + reference)
- Quality gates and validation criteria
- Performance benchmarks

**Target:** 80%+ code coverage, all tests passing before Week 2 kickoff.

---

## 1. Unit Test Specifications

### 1.1 Test: Mesh Import (`test_mesh_importer.py`)

#### Test Case 1.1.1: Import Valid FBX

```python
def test_import_valid_fbx():
    """Import FBX with valid body mesh."""
    importer = MeshImporter()
    
    # Use synthetic test mesh (cube for MVP)
    # TODO: Replace with actual body scan after Week 1
    
    # Create simple cube in Blender
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    
    cube = bpy.context.active_object
    cube.name = "test_body"
    
    # Save as FBX
    fbx_path = "/tmp/test_cube.fbx"
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Now test import
    mesh = importer.import_fbx(fbx_path)
    
    # Assertions
    assert mesh is not None
    assert mesh.type == 'MESH'
    assert len(mesh.data.vertices) > 0
    assert len(mesh.data.polygons) > 0
    
    print("✓ Test passed: Import valid FBX")
```

**Expected Output:**
```
✓ Test passed: Import valid FBX
  - Mesh object created
  - Vertex count: 8 (cube)
  - Face count: 6 (cube)
```

#### Test Case 1.1.2: Import Non-Existent File

```python
def test_import_missing_file():
    """Attempt to import non-existent file."""
    importer = MeshImporter()
    
    with pytest.raises(FileNotFoundError):
        mesh = importer.import_fbx("/path/to/nonexistent.fbx")
    
    print("✓ Test passed: Correctly raises FileNotFoundError")
```

#### Test Case 1.1.3: Import Corrupted FBX

```python
def test_import_corrupted_fbx():
    """Attempt to import corrupted FBX file."""
    importer = MeshImporter()
    
    # Create dummy corrupted file
    with open("/tmp/corrupted.fbx", "w") as f:
        f.write("Not a valid FBX file")
    
    with pytest.raises(ImportError):
        mesh = importer.import_fbx("/tmp/corrupted.fbx")
    
    print("✓ Test passed: Correctly raises ImportError for corrupted file")
```

#### Test Case 1.1.4: Apply Transforms

```python
def test_apply_transforms():
    """Test transform application."""
    importer = MeshImporter()
    
    # Create cube with non-identity transform
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add()
    
    cube = bpy.context.active_object
    cube.location = (5, 3, 2)  # Offset
    cube.scale = (2, 1.5, 0.5)  # Non-uniform scale
    
    # Before
    assert cube.location != (0, 0, 0)
    assert cube.scale != (1, 1, 1)
    
    # Apply transforms
    importer._apply_transforms(cube)
    
    # After (transforms baked into geometry)
    assert cube.location == (0, 0, 0)
    assert cube.scale == (1, 1, 1)
    
    print("✓ Test passed: Transforms applied correctly")
```

### 1.2 Test: Mesh Validation (`test_mesh_validator.py`)

#### Test Case 1.2.1: Validate Valid Mesh

```python
def test_validate_valid_mesh():
    """Validate a valid mesh."""
    importer = MeshImporter()
    
    # Create cube
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add()
    mesh = bpy.context.active_object
    
    # Run validation
    checks = importer.validate_mesh(mesh)
    
    # Assertions
    assert checks['vertex_count'] == True
    assert checks['face_count'] == True
    assert checks['coordinates_valid'] == True
    assert checks['manifold'] == True
    
    print("✓ Test passed: Valid mesh passes all checks")
```

**Expected Output:**
```
✓ Vertex count: 8
✓ Face count: 6
✓ Vertex coordinates valid
✓ Mesh is manifold
```

#### Test Case 1.2.2: Validate Sparse Mesh

```python
def test_validate_sparse_mesh():
    """Validate mesh with too few vertices."""
    importer = MeshImporter()
    
    # Create minimal mesh (triangle)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    mesh_data = bpy.data.meshes.new("sparse")
    mesh_data.from_pydata(
        [(0,0,0), (1,0,0), (0,1,0)],  # 3 verts
        [],
        [(0,1,2)]  # 1 face
    )
    
    mesh_obj = bpy.data.objects.new("sparse", mesh_data)
    bpy.context.collection.objects.link(mesh_obj)
    
    # Run validation
    checks = importer.validate_mesh(mesh_obj)
    
    # Should fail vertex count check
    assert checks['vertex_count'] == False
    assert checks['face_count'] == True
    
    print("✓ Test passed: Sparse mesh correctly fails validation")
```

#### Test Case 1.2.3: Validate Invalid Coordinates

```python
def test_validate_invalid_coordinates():
    """Validate mesh with NaN/Inf coordinates."""
    importer = MeshImporter()
    
    # Create mesh with invalid coord
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add()
    mesh = bpy.context.active_object
    
    # Manually set invalid coordinate
    mesh.data.vertices[0].co = (float('inf'), 0, 0)
    
    # Run validation
    checks = importer.validate_mesh(mesh)
    
    assert checks['coordinates_valid'] == False
    
    print("✓ Test passed: Invalid coordinates detected")
```

### 1.3 Test: Body Proportion Analysis

#### Test Case 1.3.1: Analyze Standard Body

```python
def test_analyze_standard_body():
    """Analyze proportions of standard-sized mesh."""
    importer = MeshImporter()
    
    # Create scaled cube (simulate 1.7m tall body)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add(size=1)
    mesh = bpy.context.active_object
    mesh.scale = (0.4, 1.7, 0.3)  # Height=1.7, Width=0.4
    
    # Analyze
    analysis = importer.analyze_proportions(mesh)
    
    # Assertions
    assert abs(analysis['height'] - 1.7) < 0.1
    assert abs(analysis['width'] - 0.4) < 0.1
    assert analysis['body_type'] == BodyType.AVERAGE
    
    print("✓ Test passed: Standard body classified correctly")
```

#### Test Case 1.3.2: Analyze Tall Body

```python
def test_analyze_tall_body():
    """Analyze proportions of tall person."""
    importer = MeshImporter()
    
    # Create tall, narrow mesh
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add(size=1)
    mesh = bpy.context.active_object
    mesh.scale = (0.3, 2.0, 0.25)  # Height=2.0, Width=0.3
    
    analysis = importer.analyze_proportions(mesh)
    
    assert analysis['height'] > 1.95
    assert analysis['body_type'] == BodyType.TALL
    
    print("✓ Test passed: Tall body detected")
```

#### Test Case 1.3.3: Analyze Broad Body

```python
def test_analyze_broad_body():
    """Analyze proportions of broad/muscular person."""
    importer = MeshImporter()
    
    # Create broad mesh
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add(size=1)
    mesh = bpy.context.active_object
    mesh.scale = (0.55, 1.7, 0.3)  # Height=1.7, Width=0.55 (broad)
    
    analysis = importer.analyze_proportions(mesh)
    
    assert analysis['aspect_ratio'] > 0.3
    assert analysis['body_type'] == BodyType.BROAD
    
    print("✓ Test passed: Broad body detected")
```

---

## 2. Integration Tests

### 2.1 End-to-End: Import + Validate

```python
def test_import_and_validate_workflow():
    """Complete import + validation workflow."""
    importer = MeshImporter()
    
    # Create test FBX
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 1.7, 0))
    cube = bpy.context.active_object
    bpy.ops.export_scene.fbx(filepath="/tmp/test_workflow.fbx", use_selection=True)
    
    # Clear
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Full workflow: Import → Validate → Analyze
    mesh = importer.import_fbx("/tmp/test_workflow.fbx")
    validation = importer.validate_mesh(mesh)
    analysis = importer.analyze_proportions(mesh)
    
    # Check all pass
    assert all(validation.values())
    assert analysis['height'] > 0
    assert analysis['body_type'] != BodyType.UNKNOWN
    
    print("✓ Integration test passed: Import → Validate → Analyze")
```

### 2.2 Performance Test: Import Speed

```python
def test_import_performance():
    """Measure import performance."""
    import time
    
    importer = MeshImporter()
    
    # Create test FBX (1000 vertices)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Use Blender's subdivided cube for more vertices
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 1.7, 0))
    sphere = bpy.context.active_object
    
    # Subdivide for more vertices (~10k)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.export_scene.fbx(filepath="/tmp/test_perf.fbx", use_selection=True)
    
    # Clear
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Measure import time
    start = time.time()
    mesh = importer.import_fbx("/tmp/test_perf.fbx")
    elapsed = time.time() - start
    
    # Performance target: <500ms
    assert elapsed < 0.5, f"Import took {elapsed:.3f}s (target <0.5s)"
    
    print(f"✓ Performance test passed: Import in {elapsed*1000:.1f}ms")
```

---

## 3. Test Data Fixtures

### 3.1 Synthetic Test Data (For Week 1)

Until 3D Scanning Lead provides real meshes, use synthetic fixtures:

```python
# test_data/create_synthetic_fixtures.py

import bpy
import pathlib

def create_cube_fixture(name: str, scale_xyz: tuple, output_dir: str):
    """Create synthetic test fixture."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1)
    mesh = bpy.context.active_object
    mesh.scale = scale_xyz
    
    # Export as FBX
    output_path = pathlib.Path(output_dir) / f"{name}.fbx"
    bpy.ops.export_scene.fbx(filepath=str(output_path), use_selection=True)
    
    print(f"✓ Created: {output_path}")
    return output_path

# Create fixtures
fixtures_dir = pathlib.Path("test_data/fixtures")
fixtures_dir.mkdir(exist_ok=True)

# Scale: (width, height, depth)
create_cube_fixture("average_male", (0.40, 1.75, 0.30), fixtures_dir)
create_cube_fixture("tall_female", (0.38, 1.95, 0.28), fixtures_dir)
create_cube_fixture("broad_male", (0.50, 1.75, 0.35), fixtures_dir)
create_cube_fixture("small_child", (0.25, 1.30, 0.22), fixtures_dir)
create_cube_fixture("large_build", (0.55, 1.70, 0.38), fixtures_dir)

print("\n✓ All synthetic fixtures created")
```

### 3.2 Reference Test Data (For Week 2+)

After 3D Scanning Lead provides real meshes:

```
test_data/fixtures/
├── average_male.fbx          (Real scan from Week 2)
├── tall_female.fbx           (Real scan)
├── broad_male.fbx            (Real scan)
├── small_child.fbx           (Real scan)
├── large_build.fbx           (Real scan)
└── metadata.json             (Scan metadata)
```

**metadata.json Format:**
```json
{
  "average_male": {
    "height_cm": 175,
    "width_cm": 40,
    "body_type": "average",
    "pose": "T-pose",
    "confidence": 0.95
  },
  "tall_female": {
    "height_cm": 195,
    "width_cm": 38,
    "body_type": "tall",
    "pose": "T-pose",
    "confidence": 0.94
  }
}
```

---

## 4. Quality Gates & Success Criteria

### 4.1 Code Coverage Target

**Target:** 80%+ coverage for implemented modules

```bash
# Run coverage analysis
pytest tests/ --cov=framework --cov-report=html

# Expected output:
# framework/mesh_importer.py .... 92%
# framework/mesh_validator.py ... 85%
# framework/config.py ........... 100%
# framework/logger.py ........... 95%
# ==================
# TOTAL ...................... 93%
```

### 4.2 Performance Benchmarks

| Operation | Target | MVP Acceptable |
|-----------|--------|-----------------|
| **Import FBX** | <500ms | <1000ms |
| **Validate Mesh** | <100ms | <200ms |
| **Analyze Proportions** | <50ms | <100ms |
| **Full Pipeline** | <1500ms | <2000ms |

### 4.3 Test Execution Checklist

```bash
# Before Week 1 completion, run:

# 1. Unit tests
pytest tests/ -v
# Expected: All tests pass, 80%+ coverage

# 2. Code formatting
black framework tests scripts
# Expected: No changes needed

# 3. Lint
flake8 framework tests scripts
# Expected: 0 errors

# 4. Type checking
mypy framework tests --ignore-missing-imports
# Expected: 0 errors (or minor warnings)

# 5. Documentation
# Expected: README, API ref, dev guide complete

# 6. CI/CD
# Expected: GitHub Actions passing on push

# Success Criteria Met If:
# ✓ All tests pass
# ✓ Coverage 80%+
# ✓ No lint errors
# ✓ Documentation complete
# ✓ CI/CD green
```

---

## 5. Test Execution Commands

### 5.1 Run All Tests

```bash
# Full test suite with coverage
pytest tests/ -v --cov=framework --cov-report=html

# Output directory: htmlcov/index.html
# Open in browser to view coverage
```

### 5.2 Run Specific Test

```bash
# Single test case
pytest tests/test_mesh_importer.py::TestMeshImporter::test_import_valid_fbx -v

# Specific module
pytest tests/test_mesh_importer.py -v

# With detailed output
pytest tests/ -vv --tb=long
```

### 5.3 Run with Blender Headless

```bash
# Run tests using Blender's Python directly
blender -b -P << 'EOF'
import sys
import subprocess

# Run pytest with Blender's Python
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v"],
    cwd="/path/to/rigging-engine"
)
sys.exit(result.returncode)
EOF
```

---

## 6. Continuous Integration (GitHub Actions)

### 6.1 Test Run in CI/CD

**Expected CI/CD Output:**

```
name: Unit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
    - Install Blender 3.6 LTS
    - Install Python 3.10
    - Install dependencies
    - Run tests
    - Check coverage
    
Result: ✓ PASSED
Coverage: 93%
Tests: 18 passed in 3.42s
```

### 6.2 CI/CD Failure Scenarios

| Scenario | Action |
|----------|--------|
| Test fails | Fix code, re-push |
| Coverage <80% | Add tests, increase coverage |
| Lint errors | Run `black` and `flake8` |
| Type errors | Run `mypy`, add type hints |
| Blender version mismatch | Update CI config to use 3.6 LTS |

---

## 7. Troubleshooting & Common Issues

### 7.1 Test Issue: "bpy module not found"

**Symptom:**
```
ModuleNotFoundError: No module named 'bpy'
```

**Solution:**
```bash
# Run tests with Blender's Python
BLENDER_PYTHON=$(blender -b -P - <<'EOF'
import sys
print(sys.executable)
EOF
)

$BLENDER_PYTHON -m pytest tests/
```

### 7.2 Test Issue: "Scene already contains objects"

**Symptom:**
```
RuntimeError: No context for operator "object.delete"
```

**Solution:** Ensure conftest.py fixture runs:
```python
@pytest.fixture
def clean_scene():
    """Clean Blender scene before each test."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    yield
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Use in tests:
def test_something(clean_scene):
    # Scene is now clean
    pass
```

### 7.3 Performance Issue: Tests running slow

**Symptom:**
```
18 tests completed in 45.2s
```

**Solution:** Use headless Blender (faster than GUI):
```bash
# Ensure -b flag in execution
blender -b -P -c /dev/null -P scripts/main.py
```

---

## 8. Week 1 Test Report Template

**Save as:** `test_reports/week1_report.md`

```markdown
# Week 1 Test Report

**Date:** 2026-03-22  
**Tester:** Blender Rigging Lead  
**Build:** v0.1-week1  

## Summary

- **Tests Run:** 18
- **Tests Passed:** 18 ✓
- **Tests Failed:** 0
- **Coverage:** 93%
- **Duration:** 3.42s

## Test Results

### Unit Tests
- ✓ test_import_valid_fbx
- ✓ test_import_missing_file
- ✓ test_import_corrupted_fbx
- ✓ test_apply_transforms
- ✓ test_validate_valid_mesh
- ✓ test_validate_sparse_mesh
- ✓ test_validate_invalid_coordinates
- ✓ test_analyze_standard_body
- ✓ test_analyze_tall_body
- ✓ test_analyze_broad_body

### Integration Tests
- ✓ test_import_and_validate_workflow
- ✓ test_import_performance

### Performance
- Import FBX: 245ms (target <500ms) ✓
- Validate Mesh: 78ms (target <100ms) ✓
- Analyze Proportions: 42ms (target <50ms) ✓

## Code Quality

- **Coverage:** 93% (target 80%) ✓
- **Lint:** 0 errors ✓
- **Type Check:** 0 errors ✓
- **Format:** Black compliant ✓

## Issues & Blockers

None. Week 1 complete and ready for Week 2.

## Recommendations

1. ✓ Proceed with Week 2 (rigging implementation)
2. ✓ Schedule 3D Scanning Lead sync for test data validation
3. ✓ Prepare MediaPipe setup for Week 3

---

**Approved for Production:** CEO sign-off required
```

---

## 9. Automated Test Report Generation

**Script:** `scripts/generate_test_report.sh`

```bash
#!/bin/bash

# Run tests and generate report

echo "Running Week 1 Tests..."
pytest tests/ \
    -v \
    --cov=framework \
    --cov-report=html \
    --cov-report=term \
    --tb=short \
    > test_reports/week1_raw.txt 2>&1

RESULT=$?

echo "Generating HTML report..."
# Report already in htmlcov/index.html

if [ $RESULT -eq 0 ]; then
    echo "✓ All tests passed!"
    echo "Coverage report: htmlcov/index.html"
else
    echo "✗ Tests failed. Review test_reports/week1_raw.txt"
fi

exit $RESULT
```

---

## 10. Sign-Off Checklist

**Before Week 2 kickoff, confirm:**

- [ ] All 18 unit tests passing
- [ ] Coverage 80%+ (target 93%)
- [ ] Performance benchmarks met
- [ ] No lint errors
- [ ] Documentation complete
- [ ] CI/CD green on GitHub
- [ ] Synthetic test fixtures working
- [ ] Test data expected from 3D Scanning Lead
- [ ] Developer environment reproducible
- [ ] Blocker escalation process understood

**Signed by:** CEO (approval for Week 2)  
**Date:** 2026-03-22

---

**Week 1 Test Framework Complete**  
**Ready for Implementation**
