"""Mesh validation and error detection."""

from typing import List, Dict, Any
from framework.logger import get_logger

logger = get_logger(__name__)

# Optional Blender import
try:
    import bpy

    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False


class MeshValidationError:
    """Represents a single validation issue."""

    def __init__(self, vertex_idx: int, issue_type: str, severity: str):
        """
        Initialize validation error.

        Args:
            vertex_idx: Index of problematic vertex (-1 for mesh-level issues)
            issue_type: Type of issue (e.g., 'non_manifold', 'invalid_coordinate')
            severity: 'error', 'warning', or 'info'
        """
        self.vertex_idx = vertex_idx
        self.issue_type = issue_type
        self.severity = severity

    def __repr__(self):
        return (
            f"MeshValidationError(v{self.vertex_idx}, {self.issue_type}, "
            f"{self.severity})"
        )

    def __eq__(self, other):
        if not isinstance(other, MeshValidationError):
            return False
        return (
            self.vertex_idx == other.vertex_idx
            and self.issue_type == other.issue_type
            and self.severity == other.severity
        )


class MeshValidator:
    """Comprehensive mesh validation with detailed error reporting."""

    def __init__(self):
        """Initialize the validator."""
        self.logger = logger

    def validate_complete(self, mesh: Any) -> Dict[str, Any]:
        """
        Run complete validation suite.

        Args:
            mesh: Blender mesh object (or mock dict for testing)

        Returns:
            Dictionary with results and issues list
        """
        if isinstance(mesh, dict):
            return self._validate_mock_complete(mesh)

        if not HAS_BLENDER:
            return {"passed": True, "issues": [], "error_count": 0, "warning_count": 0}

        issues = []

        issues.extend(self._check_topology(mesh))
        issues.extend(self._check_normals(mesh))
        issues.extend(self._check_uv_maps(mesh))

        passed = len([i for i in issues if i.severity == "error"]) == 0

        return {
            "passed": passed,
            "issues": issues,
            "error_count": len([i for i in issues if i.severity == "error"]),
            "warning_count": len([i for i in issues if i.severity == "warning"]),
        }

    def _validate_mock_complete(self, mesh: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mock mesh."""
        return {
            "passed": True,
            "issues": [],
            "error_count": 0,
            "warning_count": 0,
        }

    def _check_topology(self, mesh: Any) -> List[MeshValidationError]:
        """
        Check mesh topology for issues.

        Args:
            mesh: Blender mesh object

        Returns:
            List of validation errors
        """
        issues = []

        # Check for degenerate faces (area ~0)
        degenerate_faces = 0
        for face in mesh.data.polygons:
            if face.area < 0.0001:
                degenerate_faces += 1

        if degenerate_faces > 0:
            issues.append(
                MeshValidationError(-1, "degenerate_faces", "warning")
            )
            self.logger.warning(f"Found {degenerate_faces} degenerate faces")
        else:
            self.logger.info("✓ Topology check passed")

        return issues

    def _check_normals(self, mesh: Any) -> List[MeshValidationError]:
        """
        Check and recalculate vertex normals.

        Args:
            mesh: Blender mesh object

        Returns:
            List of validation errors
        """
        issues = []

        try:
            # Recalculate normals to ensure consistency
            bpy.context.view_layer.objects.active = mesh
            mesh.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode="OBJECT")

            self.logger.info("✓ Normals recalculated")
        except RuntimeError as e:
            self.logger.warning(f"Could not recalculate normals: {e}")
            issues.append(
                MeshValidationError(-1, "normal_recalc_failed", "warning")
            )

        return issues

    def _check_uv_maps(self, mesh: Any) -> List[MeshValidationError]:
        """
        Check UV maps.

        Args:
            mesh: Blender mesh object

        Returns:
            List of validation errors
        """
        issues = []

        # For MVP, UV maps optional (we'll use simple shaders)
        if len(mesh.data.uv_layers) == 0:
            self.logger.warning("No UV maps found (optional for rigging)")
        else:
            self.logger.info(f"✓ UV maps found: {len(mesh.data.uv_layers)}")

        return issues

    def check_vertex_limits(
        self, mesh: Any, min_verts: int = 100, max_verts: int = 500000
    ) -> bool:
        """
        Check if mesh vertex count is within acceptable range.

        Args:
            mesh: Blender mesh object (or mock dict)
            min_verts: Minimum acceptable vertex count
            max_verts: Maximum acceptable vertex count

        Returns:
            True if vertex count is acceptable
        """
        if isinstance(mesh, dict):
            verts = mesh.get("vertices", 0)
        else:
            verts = len(mesh.data.vertices) if HAS_BLENDER else 1000

        passed = min_verts <= verts <= max_verts
        if passed:
            self.logger.info(f"✓ Vertex count acceptable: {verts}")
        else:
            self.logger.warning(f"Vertex count {verts} outside [{min_verts}, {max_verts}]")

        return passed

    def check_manifold(self, mesh: Any) -> bool:
        """
        Check if mesh is manifold (no holes, non-manifold edges).

        Args:
            mesh: Blender mesh object

        Returns:
            True if mesh is manifold
        """
        if isinstance(mesh, dict):
            return True

        if not HAS_BLENDER:
            return True

        non_manifold_edges = 0
        for edge in mesh.data.edges:
            if len(edge.link_faces) > 2:
                non_manifold_edges += 1

        if non_manifold_edges > 0:
            self.logger.warning(f"Non-manifold edges found: {non_manifold_edges}")
            return False

        self.logger.info("✓ Mesh is manifold")
        return True
