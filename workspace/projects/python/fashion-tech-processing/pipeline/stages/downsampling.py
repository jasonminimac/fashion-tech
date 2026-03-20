"""Point cloud downsampling via voxel grid."""

import logging
import open3d as o3d

logger = logging.getLogger(__name__)


class PointCloudDownsampler:
    """Voxel-based point cloud downsampling."""

    def __init__(self, voxel_size: float = 0.01):
        """Initialize downsampler.

        Args:
            voxel_size: Voxel size in meters (default 10mm)
        """
        self.voxel_size = voxel_size

    def downsample(self, pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Downsample point cloud using voxel grid.

        Args:
            pcd: Input point cloud

        Returns:
            Downsampled point cloud
        """
        initial_count = len(pcd.points)

        pcd_down = pcd.voxel_down_sample(self.voxel_size)

        logger.debug("  Voxel downsampling (%.4f m): %d → %d points", 
                    self.voxel_size, initial_count, len(pcd_down.points))

        return pcd_down
