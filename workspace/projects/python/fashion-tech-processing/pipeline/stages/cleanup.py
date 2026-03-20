"""Mesh cleanup and optimization."""

import logging
import open3d as o3d

logger = logging.getLogger(__name__)


class MeshCleaner:
    """Clean and optimize triangle mesh."""

    def __init__(self, remove_degenerate: bool = True, remove_unreferenced: bool = True):
        """Initialize mesh cleaner.

        Args:
            remove_degenerate: Remove degenerate triangles
            remove_unreferenced: Remove unreferenced vertices
        """
        self.remove_degenerate = remove_degenerate
        self.remove_unreferenced = remove_unreferenced

    def clean(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Clean and optimize mesh.

        Args:
            mesh: Input triangle mesh

        Returns:
            Cleaned mesh
        """
        initial_vertices = len(mesh.vertices)
        initial_triangles = len(mesh.triangles)

        # Remove degenerate triangles (zero area)
        if self.remove_degenerate:
            mesh.remove_degenerate_triangles()
            logger.debug("  Degenerate triangle removal: → %d triangles", len(mesh.triangles))

        # Remove unreferenced vertices
        if self.remove_unreferenced:
            mesh.remove_unreferenced_vertices()
            logger.debug("  Unreferenced vertex removal: → %d vertices", len(mesh.vertices))

        # Compute normals for shading
        mesh.compute_vertex_normals()

        logger.debug("  Mesh cleanup: %d → %d vertices, %d → %d triangles", 
                    initial_vertices, len(mesh.vertices),
                    initial_triangles, len(mesh.triangles))

        return mesh
