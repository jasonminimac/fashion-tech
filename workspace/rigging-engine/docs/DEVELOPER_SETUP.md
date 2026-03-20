# Developer Setup Guide

## Prerequisites

- macOS 11.0+ (or Linux/Windows)
- Blender 3.6 LTS
- Python 3.10+
- Git

## Installation

### 1. Clone Repository

```bash
git clone <repo-url>
cd blender-rigging
```

### 2. Install Blender

```bash
# macOS with Homebrew
brew install blender@3.6

# Or download from blender.org
# https://www.blender.org/download/

# Verify
blender --version
# Expected: Blender 3.6.x
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3.10 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Test Installation

```bash
# Run unit tests
pytest tests/ -v

# Expected output:
# tests/test_import_validate.py::TestMeshImporter::test_validate_valid_mesh PASSED
# ...
# 18 passed in 3.42s
```

## Project Structure

```
blender-rigging/
├── framework/              # Core Blender automation
│   ├── __init__.py
│   ├── config.py           # Configuration & enums
│   ├── logger.py           # Logging utilities
│   ├── mesh_importer.py    # FBX import (~400 LOC)
│   └── mesh_validator.py   # Validation (~200 LOC)
├── rigging/                # Skeleton generation (Week 3+)
│   └── __init__.py
├── export/                 # Export pipelines (Week 5+)
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   └── test_import_validate.py  # 18 test cases
├── test_data/
│   ├── fixtures/           # FBX test files
│   └── expected_output/    # Reference outputs
├── docs/
│   ├── API_REFERENCE.md
│   └── DEVELOPER_SETUP.md (← this file)
├── scripts/
│   └── main.py             # CLI entry point
├── .github/
│   └── workflows/
│       └── test.yml        # CI/CD pipeline
├── .gitignore
├── requirements.txt
└── README.md
```

## Common Tasks

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_import_validate.py::TestMeshImporter::test_validate_valid_mesh -v

# With coverage
pytest tests/ --cov=framework --cov-report=html
open htmlcov/index.html
```

### Format Code

```bash
# Auto-format with Black
black framework rigging export tests scripts

# Check with Flake8
flake8 framework rigging export tests scripts
```

### Type Check

```bash
mypy framework tests --ignore-missing-imports
```

### Run CLI Pipeline

```bash
# Validate FBX
python scripts/main.py test_data/fixtures/average_male.fbx --validate --verbose

# (Full rigging coming Week 3)
```

## Troubleshooting

### Issue: "blender: command not found"

**Solution:** Ensure Blender is in PATH

```bash
# Verify installation
which blender

# If not found, install via Homebrew
brew install blender@3.6

# Or add to PATH manually
export PATH="/Applications/Blender.app/Contents/MacOS:$PATH"
```

### Issue: ModuleNotFoundError: No module named 'bpy'

**Solution:** Use Blender's Python directly

```bash
# Find Blender's Python path
BLENDER_PYTHON=$(blender -b -P - <<'EOF'
import sys
print(sys.executable)
EOF
)

# Run tests with Blender's Python
$BLENDER_PYTHON -m pytest tests/
```

### Issue: Tests fail with "No context for operator"

**Solution:** Blender needs a scene context. Tests use mocks, so this is usually temporary.

```bash
# Ensure pytest fixtures run
pytest tests/ -v

# If still failing, check conftest.py
cat tests/conftest.py
```

### Issue: Import errors

**Solution:** Ensure project root is in Python path

```bash
# Verify from project root
cd /path/to/rigging-engine
python -c "from framework import MeshImporter; print('OK')"

# Should print: OK
```

## Git Workflow

### Create a Feature Branch

```bash
git checkout -b feature/mesh-import
```

### Make Changes

```bash
# Edit files
vim framework/mesh_importer.py

# Format code
black framework/

# Run tests
pytest tests/ -v

# Check linting
flake8 framework/
```

### Commit Changes

```bash
# Stage files
git add framework/

# Commit with descriptive message
git commit -m "Add: mesh validation checks for non-manifold geometry"

# Push to remote
git push origin feature/mesh-import
```

### Create Pull Request

On GitHub:
1. Create PR from feature branch → main
2. Ensure CI/CD passes
3. Request review
4. Merge when approved

## Performance Profiling

### Profile Import Time

```python
import time
from framework.mesh_importer import MeshImporter

importer = MeshImporter()

start = time.time()
mesh = importer.import_fbx("large_mesh.fbx")
elapsed = time.time() - start

print(f"Import took {elapsed*1000:.1f}ms")
```

### Profile Full Pipeline

```bash
python -m cProfile -s cumtime scripts/main.py test_data/fixtures/average_male.fbx
```

## Environment Variables

**Optional configuration:**

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Blender settings
export BLENDER_VERSION="3.6.0"
```

## Next Steps

After setup:

1. ✓ Run tests to verify installation
2. ✓ Read `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine/docs/API_REFERENCE.md`
3. ✓ Explore framework modules
4. ✓ Check out Week 1 tasks in SPRINT-1.md
5. ✓ Create your first feature branch

## Getting Help

- **Blender API:** https://docs.blender.org/api/current/
- **Python pytest:** https://docs.pytest.org/
- **GitHub Issues:** Create issue for bugs/blockers

---

**Updated:** 2026-03-18  
**Status:** Ready for Week 1 Development
