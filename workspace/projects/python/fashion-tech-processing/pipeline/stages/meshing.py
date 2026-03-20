"""Poisson surface reconstruction."""

import logging
import numpy as np
import open3d as o3d

logger = logging.getLogger(__name__)


class MeshGenerator:
    """Generate mesh from point cloud using Poisson reconstruction."""

    def __init__(self, depth: int = 9, density_threshold: float = 0.1):
        """Initialize mesh generator.

        Args:
            depth: Poisson octree depth (8-10 typical, higher = finer detail)
            density_threshold: Remove low-density voxels (quantile threshold)
        """
        self.depth = depth
        self.density_threshold = density_threshold

    def generate_poisson(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
        """Generate mesh via Poisson surface reconstruction.

        Args:
            pcd: Input point cloud (must have normals)

        Returns:
            Triangle mesh
        """
        if not pcd.has_normals():
            raise ValueError("Point cloud must have normals estimated")

        # Poisson reconstruction
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd,
            depth=self.depth,
            width=0,
            linear_fit=False,
        )

        logger.debug("  Poisson reconstruction: depth=%d → %d vertices, %d triangles", 
                    self.depth, len(mesh.vertices), len(mesh.triangles))

        # Remove low-density voxels
        densities_array = np.asarray(densities)
        threshold = np.quantile(densities_array, self.density_threshold)
        vertices_to_remove = densities_array < threshold

        mesh.remove_vertices_by_mask(vertices_to_remove)

        logger.debug("  Density filtering (threshold=%.2f): → %d vertices", 
                    self.density_threshold, len(mesh.vertices))

        return mesh
