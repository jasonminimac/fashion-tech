"""Configuration and fixtures for pytest."""

import pytest
import logging

# Silence Blender logging if available
try:
    logging.getLogger("bpy").setLevel(logging.WARNING)
except Exception:
    pass


@pytest.fixture(scope="session", autouse=True)
def blender_init():
    """Initialize Blender for testing if available."""
    try:
        import bpy

        print(f"Initializing Blender {bpy.app.version_string}")
    except ImportError:
        print("Blender not available - running in mock mode")

    yield
    print("Tests complete")


@pytest.fixture
def clean_scene():
    """Clean Blender scene before each test."""
    try:
        import bpy

        # Clear scene
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
    except (ImportError, RuntimeError):
        pass

    yield

    # Cleanup
    try:
        import bpy

        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
    except (ImportError, RuntimeError):
        pass
