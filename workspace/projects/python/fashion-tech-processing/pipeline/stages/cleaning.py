"""Point cloud cleaning and outlier removal."""

import logging
import numpy as np
import open3d as o3d

logger = logging.getLogger(__name__)


class PointCloudCleaner:
    """Statistical outlier removal and noise filtering."""

    def __init__(self, config: dict = None):
        """Initialize cleaner with configuration."""
        self.config = config or {
            "outlier_nb_neighbors": 20,
            "outlier_std_ratio": 2.0,
            "confidence_threshold": 0.5,
        }

    def clean(self, pcd: o3d.geometry.PointCloud, confidences: np.ndarray = None) -> o3d.geometry.PointCloud:
        """Remove noise and outliers from point cloud.

        Args:
            pcd: Input point cloud
            confidences: Optional confidence scores per point (0-1)

        Returns:
            Cleaned point cloud
        """
        initial_count = len(pcd.points)

        # Step 1: Statistical outlier removal
        pcd_clean, inlier_mask = pcd.remove_statistical_outliers(
            nb_neighbors=self.config["outlier_nb_neighbors"],
            std_ratio=self.config["outlier_std_ratio"],
        )
        logger.debug("  Outlier removal: %d → %d points", initial_count, len(pcd_clean.points))

        # Step 2: Confidence-based filtering
        if confidences is not None and len(confidences) > 0:
            # Map to inlier indices
            inlier_confidences = confidences[inlier_mask]
            mask = inlier_confidences >= self.config["confidence_threshold"]
            pcd_clean = pcd_clean.select_by_index(np.where(mask)[0])
            logger.debug("  Confidence filtering (threshold=%.2f): → %d points", 
                        self.config["confidence_threshold"], len(pcd_clean.points))

        # Step 3: Remove isolated points
        if len(pcd_clean.points) > 0:
            pcd_clean, _ = pcd_clean.remove_statistical_outliers(nb_neighbors=10, std_ratio=1.5)

        return pcd_clean
