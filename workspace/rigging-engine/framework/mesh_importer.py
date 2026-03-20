"""Blender mesh import and preparation pipeline."""

import pathlib
from typing import Dict, Optional, Tuple, Any

from framework.config import (
    APPLY_TRANSFORMS,
    MESH_MIN_VERTICES,
    MESH_MAX_VERTICES,
    BODY_HEIGHT_MIN,
    BODY_HEIGHT_MAX,
    BodyType,
    PoseType,
)
from framework.logger import get_logger

logger = get_logger(__name__)

# Optional Blender import (for testing without Blender installed)
try:
    import bpy
    from mathutils import Vector

    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False
    logger.warning("Blender (bpy) not available - running in test mode")


class MeshImporter:
    """Import and prepare 3D body meshes from FBX/OBJ formats."""

    def __init__(self):
        """Initialize the mesh importer."""
        self.logger = logger
        self.last_imported_mesh = None

    def import_fbx(self, fbx_path: str) -> Optional[Any]:
        """
        Import FBX file into Blender scene.

        Args:
            fbx_path: Path to FBX file

        Returns:
            Mesh object (bpy.types.Object) or None if Blender unavailable

        Raises:
            FileNotFoundError: If file doesn't exist
            ImportError: If import fails
        """
        if not HAS_BLENDER:
            self.logger.warning("Blender not available - simulating import")
            return self._mock_import_fbx(fbx_path)

        fbx_path = pathlib.Path(fbx_path)

        if not fbx_path.exists():
            raise FileNotFoundError(f"FBX file not found: {fbx_path}")

        self.logger.info(f"Importing FBX: {fbx_path}")

        # Clear scene to avoid conflicts
        try:
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False)
        except RuntimeError:
            self.logger.debug("Scene already empty")

        # Import FBX
        try:
            bpy.ops.import_scene.fbx(
                filepath=str(fbx_path),
                use_image_search=False,
                ignore_leaf_bones=False,
                force_connect_children=False,
                automatic_bone_orientation=False,
                use_anim=False,
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
        mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

        if not mesh_objects:
            raise ImportError("No mesh found in FBX file")

        if len(mesh_objects) > 1:
            self.logger.warning(
                f"Found {len(mesh_objects)} meshes. Using first; consider merging."
            )

        mesh = mesh_objects[0]
        self.last_imported_mesh = mesh

        # Apply transforms if requested
        if APPLY_TRANSFORMS:
            self._apply_transforms(mesh)

        return mesh

    def _mock_import_fbx(self, fbx_path: str) -> Dict[str, Any]:
        """
        Mock FBX import for testing without Blender.

        Args:
            fbx_path: Path to FBX file

        Returns:
            Mock mesh object dictionary
        """
        fbx_path = pathlib.Path(fbx_path)

        if not fbx_path.exists():
            raise FileNotFoundError(f"FBX file not found: {fbx_path}")

        # Return mock object for testing
        return {
            "name": fbx_path.stem,
            "type": "MESH",
            "vertices": 1000,
            "faces": 500,
            "path": str(fbx_path),
        }

    def _apply_transforms(self, obj: Any) -> None:
        """
        Apply all transforms to object (location, rotation, scale).

        Args:
            obj: Blender mesh object
        """
        if not HAS_BLENDER:
            self.logger.debug("Skipping transform application (no Blender)")
            return

        try:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            self.logger.info("✓ Transforms applied")
        except RuntimeError as e:
            self.logger.warning(f"Could not apply transforms: {e}")

    def validate_mesh(self, mesh: Any) -> Dict[str, bool]:
        """
        Validate mesh integrity with multiple checks.

        Args:
            mesh: Blender mesh object (or mock dict for testing)

        Returns:
            Dictionary of validation results (keys: check names, values: pass/fail)
        """
        checks = {}

        # Handle mock objects for testing
        if isinstance(mesh, dict):
            return self._validate_mock_mesh(mesh)

        if not HAS_BLENDER:
            return {"mock": True}

        # Check 1: Vertex count
        n_verts = len(mesh.data.vertices)
        checks["vertex_count"] = MESH_MIN_VERTICES <= n_verts <= MESH_MAX_VERTICES
        if not checks["vertex_count"]:
            self.logger.warning(
                f"Vertex count {n_verts} outside acceptable range "
                f"[{MESH_MIN_VERTICES}, {MESH_MAX_VERTICES}]"
            )
        else:
            self.logger.info(f"✓ Vertex count: {n_verts}")

        # Check 2: Face count
        n_faces = len(mesh.data.polygons)
        checks["face_count"] = n_faces > 10
        if not checks["face_count"]:
            self.logger.warning(f"Face count very low: {n_faces}")
        else:
            self.logger.info(f"✓ Face count: {n_faces}")

        # Check 3: Valid vertex coordinates
        checks["coordinates_valid"] = True
        for v in mesh.data.vertices:
            if any(not (-1e6 < c < 1e6) for c in v.co):
                checks["coordinates_valid"] = False
                self.logger.error(f"Invalid vertex coordinates: {v.co}")
                break
        if checks["coordinates_valid"]:
            self.logger.info("✓ Vertex coordinates valid")

        # Check 4: Non-manifold geometry
        non_manifold_count = len([v for v in mesh.data.vertices if len(v.link_edges) < 2])
        checks["manifold"] = non_manifold_count == 0
        if non_manifold_count > 0:
            self.logger.warning(
                f"Non-manifold vertices: {non_manifold_count} "
                "(may cause issues)"
            )
        else:
            self.logger.info("✓ Mesh is manifold")

        return checks

    def _validate_mock_mesh(self, mesh: Dict[str, Any]) -> Dict[str, bool]:
        """Validate mock mesh object."""
        return {
            "vertex_count": mesh.get("vertices", 0) >= MESH_MIN_VERTICES,
            "face_count": mesh.get("faces", 0) > 10,
            "coordinates_valid": True,
            "manifold": True,
        }

    def analyze_proportions(self, mesh: Any) -> Dict[str, Any]:
        """
        Analyze body proportions from mesh bounding box.

        Args:
            mesh: Blender mesh object (or mock dict for testing)

        Returns:
            Dictionary with height, width, aspect_ratio, body_type, pose
        """
        if isinstance(mesh, dict):
            return self._analyze_mock_proportions(mesh)

        if not HAS_BLENDER:
            return {
                "height": 1.75,
                "width": 0.4,
                "depth": 0.3,
                "aspect_ratio": 0.23,
                "body_type": BodyType.AVERAGE,
                "pose": PoseType.T_POSE,
            }

        # Get bounding box
        bbox_coords = [Vector(co) for co in mesh.bound_box]
        bbox_min = bbox_coords[0]
        bbox_max = bbox_coords[7]

        dimensions = bbox_max - bbox_min

        height = dimensions.y  # Assuming Y-up
        width = dimensions.x  # Shoulders
        depth = dimensions.z  # Front-back

        # Classify body type
        aspect_ratio = width / height if height > 0 else 0

        if height < BODY_HEIGHT_MIN * 0.9:
            body_type = BodyType.SMALL
        elif height > BODY_HEIGHT_MAX * 1.1:
            body_type = BodyType.TALL
        elif aspect_ratio > 0.35:
            body_type = BodyType.BROAD
        elif aspect_ratio < 0.25:
            body_type = BodyType.TALL
        else:
            body_type = BodyType.AVERAGE

        self.logger.info(
            f"Body proportions: Height={height:.2f}m, "
            f"Width={width:.2f}m, Aspect={aspect_ratio:.2f}, "
            f"Type={body_type.value}"
        )

        return {
            "height": height,
            "width": width,
            "depth": depth,
            "aspect_ratio": aspect_ratio,
            "body_type": body_type,
            "pose": PoseType.T_POSE,
        }

    def _analyze_mock_proportions(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mock mesh proportions."""
        height = 1.75
        width = 0.4
        aspect_ratio = width / height

        if height < BODY_HEIGHT_MIN:
            body_type = BodyType.SMALL
        elif height > BODY_HEIGHT_MAX:
            body_type = BodyType.TALL
        elif aspect_ratio > 0.35:
            body_type = BodyType.BROAD
        else:
            body_type = BodyType.AVERAGE

        return {
            "height": height,
            "width": width,
            "depth": 0.3,
            "aspect_ratio": aspect_ratio,
            "body_type": body_type,
            "pose": PoseType.T_POSE,
        }


def import_and_validate_fbx(fbx_path: str, verbose: bool = True) -> Tuple[Any, Dict[str, Any]]:
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
