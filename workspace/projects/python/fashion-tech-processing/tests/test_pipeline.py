"""Test suite for fashion-tech-processing."""

import pytest
import numpy as np
import open3d as o3d
from pathlib import Path
import tempfile

from pipeline.pipeline import ScanProcessingPipeline
from pipeline.stages.cleaning import PointCloudCleaner
from pipeline.stages.downsampling import PointCloudDownsampler
from pipeline.stages.meshing import MeshGenerator


@pytest.fixture
def sample_point_cloud():
    """Create a sample point cloud for testing."""
    # Generate sphere point cloud
    pcd = o3d.geometry.PointCloud()
    points = np.random.randn(1000, 3) * 0.1
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Add colors (confidence in R channel)
    colors = np.random.rand(1000, 3)
    colors[:, 0] = np.random.rand(1000)  # Confidence
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    return pcd


@pytest.fixture
def sample_ply_file(sample_point_cloud):
    """Create a temporary PLY file."""
    with tempfile.NamedTemporaryFile(suffix=".ply", delete=False) as f:
        o3d.io.write_point_cloud(f.name, sample_point_cloud)
        yield f.name
    # Cleanup
    Path(f.name).unlink()


class TestPointCloudCleaner:
    """Test point cloud cleaning."""

    def test_clean_removes_outliers(self, sample_point_cloud):
        """Test that outlier removal reduces point count."""
        cleaner = PointCloudCleaner()
        initial_count = len(sample_point_cloud.points)
        
        cleaned = cleaner.clean(sample_point_cloud)
        final_count = len(cleaned.points)
        
        # Should remove some points
        assert final_count < initial_count

    def test_clean_preserves_structure(self, sample_point_cloud):
        """Test that cleaning doesn't remove all points."""
        cleaner = PointCloudCleaner()
        cleaned = cleaner.clean(sample_point_cloud)
        
        assert len(cleaned.points) > 100  # Still has significant data


class TestPointCloudDownsampler:
    """Test point cloud downsampling."""

    def test_downsample_reduces_points(self, sample_point_cloud):
        """Test that downsampling reduces point count."""
        downsampler = PointCloudDownsampler(voxel_size=0.1)
        initial_count = len(sample_point_cloud.points)
        
        downsampled = downsampler.downsample(sample_point_cloud)
        final_count = len(downsampled.points)
        
        # Should significantly reduce points
        assert final_count < initial_count / 2


class TestPipeline:
    """Test full pipeline."""

    def test_pipeline_initialization(self):
        """Test pipeline initializes with default config."""
        pipeline = ScanProcessingPipeline()
        assert pipeline.config is not None
        assert "voxel_size" in pipeline.config

    def test_pipeline_process(self, sample_ply_file):
        """Test full pipeline processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = ScanProcessingPipeline()
            result = pipeline.process(sample_ply_file, "test_scan", tmpdir)
            
            assert "fbx_path" in result or "glb_path" in result
            assert result.get("elapsed_sec", 0) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
