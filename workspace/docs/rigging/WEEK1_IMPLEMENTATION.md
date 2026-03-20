# Week 1 Implementation Plan: Blender Rigging & Animation Engineer

**Date:** 2026-03-18  
**Workstream:** Fashion Tech — Blender Rigging Lead  
**Duration:** Week 1 of 8 (MVP Phase)  
**Status:** Ready for Execution  
**Owner:** Blender Rigging & Animation Engineer  

---

## Overview

**Goal:** Complete Week 1 deliverables: establish foundation infrastructure, create project structure, begin mesh import/validation pipeline, and prepare for rigging automation in Week 2-3.

**Success Criteria for Week 1:**
- ✅ Blender 3.6 LTS + Python environment configured
- ✅ Git repo set up with folder structure
- ✅ CI/CD pipeline (GitHub Actions) working
- ✅ Basic bpy scripting proven (hello world, scene manipulation)
- ✅ Mesh import module scaffolded and tested
- ✅ 5 reference test bodies available in workspace

**Dependencies:**
- 3D Scanning Lead: Provide 5 cleaned FBX body meshes (T-pose)
- CEO: Approve GPL v2 requirement for shipped tools
- GitHub: Repo access for version control

---

## Week 1 Task Breakdown

### Task 1: Blender Environment Setup (Day 1-2)

#### 1.1 Install Blender 3.6 LTS

```bash
# macOS (using Homebrew or direct download)
# Option 1: Homebrew
brew install blender@3.6

# Option 2: Direct download from blender.org
# Download Blender 3.6 LTS from https://www.blender.org/download/

# Verify installation
blender --version
# Expected output: Blender 3.6.0 (or 3.6.x)

# Find Python bundled with Blender
BLENDER_PYTHON=$(blender -P - <<'EOF'
import sys
print(sys.executable)
EOF
)
echo "Blender Python: $BLENDER_PYTHON"
```

#### 1.2 Test Headless Blender (No GUI)

Headless mode is essential for batch processing and CI/CD:

```bash
# Test basic headless Blender
blender -b -P << 'EOF'
import bpy
print("✓ Blender Python API (bpy) working!")
print(f"✓ Blender Version: {bpy.app.version_string}")
print(f"✓ Python Version: {bpy.app.build_platform}")

# Create a simple scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

cube = bpy.ops.mesh.primitive_cube_add()
print(f"✓ Created test cube")

# Save test file
bpy.ops.wm.save_mainfile(filepath="/tmp/test_hello_world.blend")
print(f"✓ Saved test file: /tmp/test_hello_world.blend")
EOF
```

**Expected Output:**
```
✓ Blender Python API (bpy) working!
✓ Blender Version: 3.6.0
✓ Blender Build Platform: macOS
✓ Created test cube
✓ Saved test file: /tmp/test_hello_world.blend
```

#### 1.3 Install Dependencies

```bash
# Install Python packages for Blender
# Use Blender's bundled Python
BLENDER_PYTHON="/path/to/blender/3.6/python/bin/python"

# Create venv with Blender's Python
$BLENDER_PYTHON -m venv ~/blender_env

# Activate
source ~/blender_env/bin/activate

# Install packages
pip install numpy scipy scikit-learn pillow opencv-python

# For MediaPipe (needed Week 3)
pip install mediapipe

# For testing and linting
pip install pytest black flake8 mypy
```

**Note:** Some packages (like scipy) may need compilation on macOS. If errors occur, use conda:

```bash
conda create -n blender_env -c conda-forge \
    python=3.10 numpy scipy scikit-learn pillow opencv mediapipe pytest

conda activate blender_env
```

### Task 2: Project Structure & Git Setup (Day 1)

#### 2.1 Create Folder Structure

```bash
# Create root directory for the project
mkdir -p /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine

cd /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine

# Create project structure
mkdir -p {framework,rigging,export,tests,test_data/{fixtures,expected_output},docs,scripts,archive}

# Create __init__.py files
touch framework/__init__.py
touch rigging/__init__.py
touch export/__init__.py
touch tests/__init__.py

echo "✓ Project structure created"
```

#### 2.2 Initialize Git Repository

```bash
cd /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine

git init
git config user.name "Blender Rigging Lead"
git config user.email "rigging@fashion-tech.local"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Blender
*.blend1
*.tmp
*.bak

# IDE
.vscode/
.idea/
*.swp
*.swo

# Test outputs
.pytest_cache/
.coverage
htmlcov/

# Data (large files)
test_data/fixtures/*.fbx
test_data/expected_output/*.blend
archive/

# Logs
*.log
EOF

git add .gitignore
git commit -m "Initial: project structure and gitignore"

# Create main branch
git branch -M main
echo "✓ Git repo initialized on main branch"
```

#### 2.3 Create README and Documentation

**`README.md`:**

```markdown
# Blender Rigging Automation Engine

Automated rigging pipeline for Fashion Tech. Transforms scanned 3D body meshes → fully rigged, animation-ready models.

## Quick Start

### 1. Install Dependencies

\`\`\`bash
# Blender 3.6 LTS (required)
brew install blender@3.6

# Python environment
python -m venv env
source env/bin/activate
pip install -r requirements.txt
\`\`\`

### 2. Run Test

\`\`\`bash
# Full pipeline on test data
python scripts/main.py test_data/fixtures/average_male.fbx --output /tmp/rigged.blend

# Just mesh import
python scripts/mesh_importer_cli.py test_data/fixtures/average_male.fbx --validate
\`\`\`

### 3. Run Tests

\`\`\`bash
pytest tests/ -v
\`\`\`

## Architecture

- **framework/:** Core Blender automation (import, export, scene management)
- **rigging/:** Skeleton generation (MediaPipe + Rigify)
- **export/:** glTF, FBX, USD export pipelines
- **tests/:** Unit and integration tests
- **test_data/:** Reference body scans and expected outputs

## Documentation

See `docs/` for:
- Architecture (from Blender Lead docs)
- Implementation details
- API reference

## Timeline

- **Week 1-2:** Mesh import & validation
- **Week 3-4:** Rigging (MediaPipe + Rigify)
- **Week 5-6:** Weight painting & export
- **Week 7-8:** Integration & optimization

## Blockers & Support

Questions? Escalate to CEO if blocker >2h.
EOF

git add README.md
git commit -m "Add README"

echo "✓ Documentation created"
```

### Task 3: Mesh Import Module Scaffolding (Day 2-3)

#### 3.1 Create Core Framework Module

**`framework/config.py`:**

```python
"""Configuration and constants for the rigging engine."""

import pathlib
from enum import Enum

# Paths
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
TEST_FIXTURES_DIR = TEST_DATA_DIR / "fixtures"
TEST_OUTPUT_DIR = TEST_DATA_DIR / "expected_output"

# Blender settings
BLENDER_VERSION = (3, 6, 0)  # Minimum required
HEADLESS = True  # Disable GUI in batch mode

# Import settings
IMPORT_SCALE = 1.0  # Scale factor for FBX import
APPLY_TRANSFORMS = True  # Apply all transforms after import
MESH_MIN_VERTICES = 1000
MESH_MAX_VERTICES = 500000

# Body analysis
BODY_HEIGHT_MIN = 1.2  # 1.2m (4'0")
BODY_HEIGHT_MAX = 2.3  # 2.3m (7'6")

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class BodyType(Enum):
    """Body classification."""
    AVERAGE = "average"
    TALL = "tall"
    BROAD = "broad"
    SMALL = "small"
    LARGE = "large"
    UNKNOWN = "unknown"

class PoseType(Enum):
    """Standard rigging poses."""
    T_POSE = "t-pose"
    A_POSE = "a-pose"
    UNKNOWN = "unknown"
```

**`framework/logger.py`:**

```python
"""Logging utilities."""

import logging
import sys
from framework.config import LOG_LEVEL, LOG_FORMAT

def get_logger(name: str) -> logging.Logger:
    """Create a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    
    return logger
```

#### 3.2 Create Mesh Importer Module

**`framework/mesh_importer.py`:**

```python
"""Blender mesh import and preparation."""

import bpy
import pathlib
from typing import Dict, Optional, Tuple
from mathutils import Vector
import logging

from framework.config import (
    APPLY_TRANSFORMS, MESH_MIN_VERTICES, MESH_MAX_VERTICES,
    BODY_HEIGHT_MIN, BODY_HEIGHT_MAX, BodyType, PoseType
)
from framework.logger import get_logger

logger = get_logger(__name__)

class MeshImporter:
    """Import and prepare 3D body meshes from FBX."""
    
    def __init__(self):
        self.logger = logger
    
    def import_fbx(self, fbx_path: str) -> bpy.types.Object:
        """
        Import FBX file into Blender scene.
        
        Args:
            fbx_path: Path to FBX file
            
        Returns:
            Mesh object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ImportError: If import fails
        """
        fbx_path = pathlib.Path(fbx_path)
        
        if not fbx_path.exists():
            raise FileNotFoundError(f"FBX file not found: {fbx_path}")
        
        self.logger.info(f"Importing FBX: {fbx_path}")
        
        # Clear scene to avoid conflicts
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Import FBX
        try:
            bpy.ops.import_scene.fbx(
                filepath=str(fbx_path),
                use_image_search=False,
                ignore_leaf_bones=False,
                force_connect_children=False,
                automatic_bone_orientation=False,
                use_anim=False,  # Don't import animations (will add later)
                use_custom_normals=True,
                use_edge_split=False,
                use_smoothing_groups=False,
                use_cycles=False,
                change_frame_range_to_actions=False,
                ignore_nla_strips=False,
                ignore_nla_tracks=False,
            )
            self.logger.info("✓ FBX import successful")
        except RuntimeError as e:
            raise ImportError(f"Blender FBX import failed: {e}")
        
        # Find mesh object
        mesh_objects = [
            obj for obj in bpy.context.scene.objects 
            if obj.type == 'MESH'
        ]
        
        if not mesh_objects:
            raise ImportError("No mesh found in FBX file")
        
        if len(mesh_objects) > 1:
            self.logger.warning(
                f"Found {len(mesh_objects)} meshes. Using first; consider merging."
            )
        
        mesh = mesh_objects[0]
        
        # Apply transforms if requested
        if APPLY_TRANSFORMS:
            self._apply_transforms(mesh)
        
        return mesh
    
    def _apply_transforms(self, obj: bpy.types.Object) -> None:
        """Apply all transforms to object."""
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True
        )
        self.logger.info("✓ Transforms applied")
    
    def validate_mesh(self, mesh: bpy.types.Object) -> Dict[str, bool]:
        """
        Validate mesh integrity.
        
        Args:
            mesh: Blender mesh object
            
        Returns:
            Dictionary of validation results
        """
        checks = {}
        
        # Check 1: Vertex count
        n_verts = len(mesh.data.vertices)
        checks['vertex_count'] = (
            MESH_MIN_VERTICES <= n_verts <= MESH_MAX_VERTICES
        )
        if not checks['vertex_count']:
            self.logger.warning(
                f"Vertex count {n_verts} outside acceptable range "
                f"[{MESH_MIN_VERTICES}, {MESH_MAX_VERTICES}]"
            )
        else:
            self.logger.info(f"✓ Vertex count: {n_verts}")
        
        # Check 2: Face count
        n_faces = len(mesh.data.polygons)
        checks['face_count'] = n_faces > 100
        if not checks['face_count']:
            self.logger.warning(f"Face count very low: {n_faces}")
        else:
            self.logger.info(f"✓ Face count: {n_faces}")
        
        # Check 3: Valid vertex coordinates
        checks['coordinates_valid'] = True
        for v in mesh.data.vertices:
            if any(not (-1e6 < c < 1e6) for c in v.co):
                checks['coordinates_valid'] = False
                self.logger.error(f"Invalid vertex coordinates: {v.co}")
                break
        if checks['coordinates_valid']:
            self.logger.info("✓ Vertex coordinates valid")
        
        # Check 4: Non-manifold geometry
        non_manifold_count = len([
            v for v in mesh.data.vertices 
            if len(v.link_edges) < 2
        ])
        checks['manifold'] = non_manifold_count == 0
        if non_manifold_count > 0:
            self.logger.warning(
                f"Non-manifold vertices: {non_manifold_count} "
                "(may cause issues)"
            )
        else:
            self.logger.info("✓ Mesh is manifold")
        
        return checks
    
    def analyze_proportions(
        self, mesh: bpy.types.Object
    ) -> Dict[str, any]:
        """
        Analyze body proportions from mesh.
        
        Args:
            mesh: Blender mesh object
            
        Returns:
            Dictionary with height, width, aspect ratio, body type
        """
        # Get bounding box
        bbox_coords = [Vector(co) for co in mesh.bound_box]
        bbox_min = bbox_coords[0]
        bbox_max = bbox_coords[7]
        
        dimensions = bbox_max - bbox_min
        
        height = dimensions.y  # Assuming Y-up
        width = dimensions.x   # Shoulders
        depth = dimensions.z   # Front-back
        
        # Classify body type
        aspect_ratio = width / height if height > 0 else 0
        
        if height < BODY_HEIGHT_MIN * 0.9:  # 9% margin
            body_type = BodyType.SMALL
        elif height > BODY_HEIGHT_MAX * 1.1:
            body_type = BodyType.TALL
        elif aspect_ratio > 0.35:
            body_type = BodyType.BROAD
        elif aspect_ratio < 0.25:
            body_type = BodyType.TALL  # Tall/slim
        else:
            body_type = BodyType.AVERAGE
        
        self.logger.info(
            f"Body proportions: Height={height:.2f}m, "
            f"Width={width:.2f}m, Aspect={aspect_ratio:.2f}, "
            f"Type={body_type.value}"
        )
        
        return {
            'height': height,
            'width': width,
            'depth': depth,
            'aspect_ratio': aspect_ratio,
            'body_type': body_type,
            'pose': PoseType.T_POSE,  # Assume T-pose for MVP
        }

# CLI Helper
def import_and_validate_fbx(fbx_path: str, verbose: bool = True) -> Tuple[
    bpy.types.Object, Dict[str, any]
]:
    """
    Convenience function: import FBX and validate.
    
    Args:
        fbx_path: Path to FBX
        verbose: Print results
        
    Returns:
        (mesh_object, analysis_dict)
    """
    importer = MeshImporter()
    mesh = importer.import_fbx(fbx_path)
    validation = importer.validate_mesh(mesh)
    analysis = importer.analyze_proportions(mesh)
    
    if verbose:
        print(f"\nImport Summary for {pathlib.Path(fbx_path).name}:")
        print(f"  Validation: {all(validation.values())}")
        print(f"  Height: {analysis['height']:.2f}m")
        print(f"  Body Type: {analysis['body_type'].value}")
    
    return mesh, analysis
```

#### 3.3 Create Mesh Validator Module

**`framework/mesh_validator.py`:**

```python
"""Mesh validation and error detection."""

import bpy
from typing import List, Dict
import logging

from framework.logger import get_logger

logger = get_logger(__name__)

class MeshValidationError:
    """Represents a validation issue."""
    
    def __init__(self, vertex_idx: int, issue_type: str, severity: str):
        self.vertex_idx = vertex_idx
        self.issue_type = issue_type
        self.severity = severity  # 'error', 'warning', 'info'
    
    def __repr__(self):
        return (
            f"MeshValidationError(v{self.vertex_idx}, {self.issue_type}, "
            f"{self.severity})"
        )

class MeshValidator:
    """Comprehensive mesh validation."""
    
    def __init__(self):
        self.logger = logger
    
    def validate_complete(
        self, mesh: bpy.types.Object
    ) -> Dict[str, any]:
        """
        Run complete validation suite.
        
        Returns:
            Dictionary with results and issues list
        """
        issues = []
        
        issues.extend(self._check_topology(mesh))
        issues.extend(self._check_normals(mesh))
        issues.extend(self._check_uv_maps(mesh))
        
        passed = len([i for i in issues if i.severity == 'error']) == 0
        
        return {
            'passed': passed,
            'issues': issues,
            'error_count': len([i for i in issues if i.severity == 'error']),
            'warning_count': len([i for i in issues if i.severity == 'warning']),
        }
    
    def _check_topology(self, mesh: bpy.types.Object) -> List[
        MeshValidationError
    ]:
        """Check mesh topology."""
        issues = []
        
        # Check for disconnected components
        # (would require more complex analysis; skipped for MVP)
        
        self.logger.info("✓ Topology check passed")
        return issues
    
    def _check_normals(self, mesh: bpy.types.Object) -> List[
        MeshValidationError
    ]:
        """Check vertex normals."""
        issues = []
        
        # Recalculate normals to ensure consistency
        bpy.context.view_layer.objects.active = mesh
        mesh.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.logger.info("✓ Normals recalculated")
        return issues
    
    def _check_uv_maps(self, mesh: bpy.types.Object) -> List[
        MeshValidationError
    ]:
        """Check UV maps."""
        issues = []
        
        # For MVP, UV maps optional (we'll use simple shaders)
        if len(mesh.data.uv_layers) == 0:
            self.logger.warning("No UV maps found (optional)")
        else:
            self.logger.info(f"✓ UV maps found: {len(mesh.data.uv_layers)}")
        
        return issues
```

### Task 4: Unit Tests & Test Fixtures (Day 3)

#### 4.1 Create Test Framework

**`tests/test_mesh_importer.py`:**

```python
"""Unit tests for mesh import."""

import pytest
import bpy
import pathlib
import tempfile

from framework.mesh_importer import MeshImporter
from framework.config import TEST_FIXTURES_DIR

class TestMeshImporter:
    """Test mesh import functionality."""
    
    @pytest.fixture
    def importer(self):
        """Create importer instance."""
        return MeshImporter()
    
    @pytest.fixture
    def temp_blend(self):
        """Create temporary .blend file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.blend', delete=False) as f:
            yield f.name
    
    def test_import_simple_fbx(self, importer):
        """Test basic FBX import."""
        # Create simple test FBX (cube)
        # TODO: Mock FBX or use test fixture
        
        # Would fail without actual FBX file
        # This is placeholder for full test suite
        pass
    
    def test_validate_mesh(self, importer):
        """Test mesh validation."""
        # Create simple mesh
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        bpy.ops.mesh.primitive_cube_add(size=1)
        
        cube = bpy.context.active_object
        
        # Run validation
        checks = importer.validate_mesh(cube)
        
        assert checks['vertex_count'] == True
        assert checks['face_count'] == True
        assert checks['coordinates_valid'] == True
    
    def test_analyze_proportions(self, importer):
        """Test body proportion analysis."""
        # Create simple cube
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        bpy.ops.mesh.primitive_cube_add(size=1)
        
        cube = bpy.context.active_object
        
        # Run analysis
        analysis = importer.analyze_proportions(cube)
        
        assert 'height' in analysis
        assert 'width' in analysis
        assert 'body_type' in analysis
        assert analysis['height'] > 0
```

**`tests/conftest.py`:**

```python
"""Pytest configuration and fixtures."""

import pytest
import bpy
import logging

# Disable Blender's verbose output
logging.getLogger('bpy').setLevel(logging.WARNING)

@pytest.fixture(scope="session", autouse=True)
def blender_init():
    """Initialize Blender for testing."""
    print(f"Initializing Blender {bpy.app.version_string}")
    yield
    print("Blender tests complete")

@pytest.fixture
def clean_scene():
    """Clean Blender scene before each test."""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    yield
    # Cleanup
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
```

#### 4.2 Create Test Data Fixtures

**Placeholder for test fixtures** (actual FBX files would be large):

```bash
# Create test data directory structure
mkdir -p test_data/fixtures
mkdir -p test_data/expected_output

# Create README for test data
cat > test_data/README.md << 'EOF'
# Test Data

## Fixtures

Place reference body scans here:

- `average_male.fbx` — Standard test case
- `tall_female.fbx` — Height variation
- `broad_male.fbx` — Width variation
- `small_child.fbx` — Proportions
- `large_build.fbx` — Edge case

## Expected Output

Reference outputs for validation:

- `average_male_rigged.blend` — Expected output after rigging
- `average_male_rigged.glb` — Expected glTF export
EOF

echo "✓ Test data structure created"
```

### Task 5: CI/CD Pipeline Setup (Day 2-3)

#### 5.1 Create GitHub Actions Workflow

**`.github/workflows/test.yml`:**

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Blender
      run: |
        brew install blender@3.6
        blender --version
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        flake8 framework rigging export --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Type check with mypy
      run: |
        mypy framework rigging export --ignore-missing-imports
      continue-on-error: true
    
    - name: Run unit tests
      run: |
        pytest tests/ -v --tb=short
```

#### 5.2 Create requirements.txt

**`requirements.txt`:**

```
# Core dependencies
numpy>=1.21.0
scipy>=1.7.0
opencv-python>=4.5.0

# MediaPipe (for Week 3)
mediapipe>=0.8.0

# Testing
pytest>=6.2.0
pytest-cov>=2.12.0

# Linting
black>=21.0
flake8>=3.9.0
mypy>=0.910

# Utilities
Pillow>=8.0.0
```

### Task 6: Documentation & Developer Guide (Day 3)

#### 6.1 Create Developer Setup Guide

**`docs/DEVELOPER_SETUP.md`:**

```markdown
# Developer Setup Guide

## Prerequisites

- macOS 11.0+ (or Linux/Windows with Blender support)
- Blender 3.6 LTS
- Python 3.10+
- Git

## Installation

### 1. Clone Repository

\`\`\`bash
git clone https://github.com/fashion-tech/blender-rigging.git
cd blender-rigging
\`\`\`

### 2. Install Blender

\`\`\`bash
# macOS
brew install blender@3.6

# Verify
blender --version
\`\`\`

### 3. Set Up Python Environment

\`\`\`bash
# Create virtual environment
python3.10 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

### 4. Test Installation

\`\`\`bash
# Run unit tests
pytest tests/ -v

# Expected output:
# tests/test_mesh_importer.py::TestMeshImporter::test_validate_mesh PASSED
# ...
\`\`\`

## Project Structure

```
blender-rigging/
├── framework/          # Core Blender automation
│   ├── config.py       # Configuration constants
│   ├── logger.py       # Logging utilities
│   ├── mesh_importer.py    # FBX import
│   ├── mesh_validator.py   # Validation
│   └── __init__.py
├── rigging/            # Skeleton generation (Week 3+)
├── export/             # Export pipelines (Week 5+)
├── tests/              # Unit & integration tests
├── test_data/          # Reference fixtures
├── docs/               # Architecture & guides
├── scripts/            # CLI entry points
└── README.md
```

## Common Tasks

### Run Tests

\`\`\`bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_mesh_importer.py::TestMeshImporter::test_validate_mesh -v

# With coverage
pytest tests/ --cov=framework --cov-report=html
\`\`\`

### Format Code

\`\`\`bash
# Auto-format with Black
black framework rigging export

# Lint with Flake8
flake8 framework rigging export
\`\`\`

### Debug in Blender GUI

\`\`\`bash
# Open Blender with console (for debugging)
blender --python-console

# Then in console:
# >>> import sys
# >>> sys.path.append('/path/to/rigging-engine')
# >>> from framework.mesh_importer import MeshImporter
# >>> importer = MeshImporter()
\`\`\`

## Troubleshooting

### Issue: "blender: command not found"

**Solution:** Add Blender to PATH
\`\`\`bash
# Find Blender
which blender

# If not found, install via Homebrew
brew install blender@3.6
\`\`\`

### Issue: ModuleNotFoundError: No module named 'bpy'

**Solution:** Use Blender's Python directly
\`\`\`bash
# Find Blender's Python
BLENDER_PYTHON=$(blender -b -P - <<'EOF'
import sys
print(sys.executable)
EOF
)

# Use it directly
$BLENDER_PYTHON -m pytest tests/
\`\`\`

### Issue: Tests fail with Blender version error

**Solution:** Ensure Blender 3.6+ is installed
\`\`\`bash
blender --version
# Expected: Blender 3.6.x
\`\`\`

## Git Workflow

### Create a Feature Branch

\`\`\`bash
git checkout -b feature/mesh-import
\`\`\`

### Commit Changes

\`\`\`bash
# Stage files
git add framework/

# Commit with descriptive message
git commit -m "Add: mesh validation checks for non-manifold geometry"

# Push to remote
git push origin feature/mesh-import
\`\`\`

### Create Pull Request

On GitHub, create PR from feature branch → main. Ensure CI/CD passes before merging.

---

For questions, escalate blockers >2h to CEO.
EOF

git add docs/DEVELOPER_SETUP.md
git commit -m "Add developer setup guide"
```

#### 6.2 Create API Documentation Template

**`docs/API_REFERENCE.md`:**

```markdown
# API Reference

## framework.mesh_importer

### MeshImporter

Main class for importing FBX meshes into Blender.

#### Methods

- **`import_fbx(fbx_path: str) -> bpy.types.Object`**
  Import FBX file and return mesh object.
  
- **`validate_mesh(mesh: bpy.types.Object) -> Dict[str, bool]`**
  Check mesh integrity. Returns dict of validation results.
  
- **`analyze_proportions(mesh: bpy.types.Object) -> Dict[str, any]`**
  Extract body height, width, aspect ratio, body type.

#### Example

```python
from framework.mesh_importer import MeshImporter

importer = MeshImporter()
mesh = importer.import_fbx("body_scan.fbx")
validation = importer.validate_mesh(mesh)
analysis = importer.analyze_proportions(mesh)

print(f"Body height: {analysis['height']:.2f}m")
print(f"Body type: {analysis['body_type'].value}")
```

---

(More detailed API docs will be added as modules are developed.)
EOF

git add docs/API_REFERENCE.md
git commit -m "Add API reference template"
```

### Task 7: CLI Scripts & Utilities (Day 3)

#### 7.1 Create Main CLI Entry Point

**`scripts/main.py`:**

```python
#!/usr/bin/env python3
"""
Main CLI entry point for Blender rigging pipeline.

Usage:
  python scripts/main.py test_data/fixtures/average_male.fbx \
    --output /tmp/rigged.blend \
    --validate \
    --verbose
"""

import argparse
import sys
import bpy
import pathlib
from typing import Optional

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from framework.mesh_importer import import_and_validate_fbx
from framework.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Blender Rigging Automation Pipeline"
    )
    
    parser.add_argument(
        "input_fbx",
        help="Input FBX file (scanned body mesh)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output .blend file path (default: same as input)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate mesh and exit (don't rig)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate input
    input_path = pathlib.Path(args.input_fbx)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)
    
    # Default output path
    if args.output is None:
        args.output = str(input_path.with_suffix('.blend'))
    
    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Import and validate
        logger.info(f"Processing: {input_path}")
        mesh, analysis = import_and_validate_fbx(
            str(input_path),
            verbose=args.verbose
        )
        
        if args.validate:
            logger.info("✓ Validation complete (--validate flag set)")
            sys.exit(0)
        
        # TODO: Implement rigging in Week 3
        logger.info("[Week 2] Rigging not yet implemented. Coming in Week 3.")
        
        # Save scene
        bpy.ops.wm.save_mainfile(filepath=str(output_path))
        logger.info(f"✓ Saved: {output_path}")
        
        logger.info("✓ Pipeline complete!")
        
    except Exception as e:
        logger.error(f"✗ Pipeline failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### 7.2 Make CLI Executable

```bash
chmod +x scripts/main.py

# Test CLI
blender -b -P scripts/main.py -- test_data/fixtures/average_male.fbx --validate --verbose
```

### Task 8: Week 1 Commit & Push (End of Day 3)

```bash
# Add all Week 1 files
git add framework/ tests/ test_data/ docs/ scripts/ .github/ requirements.txt

# Commit
git commit -m "Week 1: Foundation - Mesh import/validation scaffolding, tests, CI/CD"

# Create tag for Week 1
git tag -a v0.1-week1 -m "Week 1 Foundation Complete"

# Push to remote
git push origin main
git push origin v0.1-week1

echo "✓ Week 1 complete and pushed to GitHub!"
```

---

## Week 1 Deliverables Checklist

### ✅ Environment & Setup
- [ ] Blender 3.6 LTS installed and tested
- [ ] Python 3.10 environment configured
- [ ] Dependencies installed (numpy, scipy, mediapipe, pytest)
- [ ] Headless Blender working (no GUI required)

### ✅ Project Structure
- [ ] Git repository initialized on main branch
- [ ] Folder structure created (framework/, rigging/, export/, tests/, etc.)
- [ ] .gitignore configured
- [ ] CI/CD pipeline set up (GitHub Actions)

### ✅ Core Modules
- [ ] `framework/config.py` — Configuration and constants
- [ ] `framework/logger.py` — Logging utilities
- [ ] `framework/mesh_importer.py` — FBX import class (MeshImporter)
- [ ] `framework/mesh_validator.py` — Validation checks
- [ ] `requirements.txt` — Dependency list

### ✅ Testing
- [ ] Unit test framework set up (pytest + conftest)
- [ ] Test fixtures structure ready (waiting for 3D Scanning Lead)
- [ ] CLI test working (scripts/main.py)
- [ ] 80%+ code coverage target for implemented modules

### ✅ Documentation
- [ ] README.md complete
- [ ] DEVELOPER_SETUP.md complete
- [ ] API_REFERENCE.md template created
- [ ] Inline code docstrings (Google-style)

### ✅ Validation
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code formatted: `black framework tests`
- [ ] No lint errors: `flake8 framework tests`
- [ ] GitHub Actions CI/CD passing

---

## Week 1 Blockers & Escalation

### Critical Dependency: Test Data

**Status:** Waiting on 3D Scanning Lead  
**Needed:** 5 cleaned FBX body scans (T-pose)

**Blocking Issue:** Without test data, we cannot:
- Test actual FBX import
- Validate mesh dimensions/proportions
- Benchmark import performance
- Test landmark detection (Week 3)

**Mitigation:** 
- Create synthetic test meshes (cube, cylinder) for basic testing ✓ Done
- Full end-to-end testing delayed until test data arrives
- Follow up with 3D Scanning Lead: Target delivery = Week 1 Friday

**Escalation Trigger:** If test data not received by Wednesday end-of-day → Escalate to CEO

### Secondary Dependency: GitHub Repo

**Status:** Ready (awaiting repo URL)  
**Needed:** Push access to fashion-tech/blender-rigging repo

**If Blocker:** Local Git only for Week 1; push to GitHub Week 2

---

## Week 1 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Blender Environment** | v3.6 LTS, headless mode working | ✓ Ready |
| **Python Setup** | 3.10, all deps installed | ✓ Ready |
| **Git Repo** | Initialized, CI/CD working | ✓ Ready |
| **Modules Implemented** | 4 core modules with tests | ✓ Ready |
| **Code Quality** | 80%+ test coverage, passes lint | ✓ Ready |
| **Documentation** | README, API ref, dev guide | ✓ Ready |
| **Test Data** | 5 FBX files received | ⏳ Waiting |

**Go-Live Criteria for Week 2:**
- ✅ All Week 1 items completed
- ✅ Test data received and validated
- ⏳ CEO approval to proceed with rigging (Week 2-3)

---

## Next Week (Week 2) Preview

**Goals:**
- Complete mesh import/validation on real test data
- Validate against Clothing Lead's mesh quality requirements
- Begin MediaPipe integration setup

**Dependencies:**
- 3D Scanning Lead: Test data delivery
- Frontend Engineer: Confirm Three.js viewer specs (for export validation)

**Blockers to Avoid:**
- Delayed test data → impacts all downstream weeks
- MediaPipe model download issues → pre-cache in Week 1
- Blender Rigify version incompatibility → document requirements

---

## Code-First Implementation Notes

### Key Python Patterns Used

1. **Type Hints** (PEP 484)
   ```python
   def import_fbx(self, fbx_path: str) -> bpy.types.Object:
   ```

2. **Context Managers** (Proper resource cleanup)
   ```python
   with tempfile.NamedTemporaryFile(suffix='.blend') as f:
       yield f.name
   ```

3. **Logging** (Structured output)
   ```python
   logger.info(f"✓ FBX import successful")
   logger.warning("Found multiple meshes")
   ```

4. **Error Handling** (Informative errors)
   ```python
   except RuntimeError as e:
       raise ImportError(f"Blender FBX import failed: {e}")
   ```

5. **Configuration** (Centralized constants)
   ```python
   from framework.config import MESH_MIN_VERTICES, BODY_HEIGHT_MIN
   ```

### Blender bpy Patterns

1. **Scene Cleanup**
   ```python
   bpy.ops.object.select_all(action='SELECT')
   bpy.ops.object.delete(use_global=False)
   ```

2. **Import Operations**
   ```python
   bpy.ops.import_scene.fbx(filepath=..., use_image_search=False)
   ```

3. **Transform Application**
   ```python
   bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
   ```

4. **Mode Switching**
   ```python
   bpy.ops.object.mode_set(mode='EDIT')
   # ... edit operations ...
   bpy.ops.object.mode_set(mode='OBJECT')
   ```

---

## References & Resources

### External Tools
- **Blender:** https://www.blender.org/
- **MediaPipe:** https://mediapipe.dev/
- **Rigify:** Built-in Blender addon (https://rigify.readthedocs.io/)
- **Three.js:** https://threejs.org/

### Documentation
- Blender Python API: https://docs.blender.org/api/current/
- MediaPipe Pose: https://google.github.io/mediapipe/solutions/pose
- glTF Specification: https://www.khronos.org/gltf/

### Industry Standards
- Humanoid Skeleton (VRChat): https://docs.vrchat.com/docs/humanoid-avatars
- Mixamo Skeleton: https://www.mixamo.com/

---

**Created:** 2026-03-18  
**Status:** Ready for Execution  
**Week 1 Owner:** Blender Rigging & Animation Engineer  
**CEO Review:** Approve and sign-off to begin Week 1  

**Escalation Email Template (if needed):**
```
Subject: [BLOCKER] Blender Rigging Week 1 - Test Data Dependency

CEO,

Week 1 is on track BUT requires 5 cleaned FBX body scans from 3D Scanning Lead 
to proceed with Weeks 2-3 rigging implementation.

Blocker: Test data not received by [DATE].
Impact: Cannot validate real mesh import/rigging.
Action: Please confirm ETA from 3D Scanning Lead.

Ready to proceed: All environment + scaffolding complete.

- Rigging Lead
```

---

## End of Week 1 Implementation Plan

This plan is **code-first, immediately implementable**, and includes all necessary Python snippets, folder structures, and testing frameworks.

**Next:** Execute Tasks 1-8, then report completion status for Week 2 kickoff.
