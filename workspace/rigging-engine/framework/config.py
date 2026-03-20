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
MESH_MIN_VERTICES = 100  # Lowered for synthetic test meshes
MESH_MAX_VERTICES = 500000

# Body analysis
BODY_HEIGHT_MIN = 1.2  # 1.2m (4'0")
BODY_HEIGHT_MAX = 2.3  # 2.3m (7'6")

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class BodyType(Enum):
    """Body classification based on proportions."""

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
