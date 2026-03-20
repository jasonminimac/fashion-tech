"""Normal estimation for point clouds."""

import logging
import open3d as o3d

logger = logging.getLogger(__name__)


class NormalEstimator:
    """Estimate vertex normals for point clouds."""

    def __init__(self, radius: float = 0.1, max_nn: int = 30):
        """Initialize normal estimator.

        Args:
            radius: Search radius in meters
            max_nn: Maximum number of neighbors
        """
        self.radius = radius
        self.max_nn = max_nn

    def estimate(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Estimate normals using hybrid search.

        Args:
            pcd: Input point cloud

        Returns:
            Point cloud with estimated normals
        """
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=self.radius,
                max_nn=self.max_nn,
            )
        )

        logger.debug("  Normal estimation: radius=%.3f m, max_nn=%d", self.radius, self.max_nn)

        return pcd
