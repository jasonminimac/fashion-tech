"""Blender Rigging Automation Framework.

Core infrastructure for mesh import, validation, and rigging automation.
"""

from .config import BodyType, PoseType, PROJECT_ROOT, TEST_FIXTURES_DIR
from .logger import get_logger
from .mesh_importer import MeshImporter
from .mesh_validator import MeshValidator, MeshValidationError

__version__ = "0.1.0"
__all__ = [
    "BodyType",
    "PoseType",
    "PROJECT_ROOT",
    "TEST_FIXTURES_DIR",
    "get_logger",
    "MeshImporter",
    "MeshValidator",
    "MeshValidationError",
]
