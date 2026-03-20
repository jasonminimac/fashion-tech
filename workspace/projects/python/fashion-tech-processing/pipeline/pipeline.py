"""Main pipeline orchestration for body scan processing."""

import logging
import time
from pathlib import Path
from typing import Dict, Tuple, Optional

import open3d as o3d
import numpy as np

from .stages.cleaning import PointCloudCleaner
from .stages.downsampling import PointCloudDownsampler
from .stages.normals import NormalEstimator
from .stages.meshing import MeshGenerator
from .stages.cleanup import MeshCleaner
from .stages.export import MeshExporter

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ScanProcessingPipeline:
    """End-to-end point cloud → mesh processing pipeline."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize pipeline with configuration."""
        self.config = config or self._default_config()

        self.cleaner = PointCloudCleaner(self.config["cleaning"])
        self.downsampler = PointCloudDownsampler(self.config["voxel_size"])
        self.estimator = NormalEstimator()
        self.generator = MeshGenerator(self.config["mesh_depth"])
        self.mesh_cleaner = MeshCleaner()
        self.exporter = MeshExporter()

        logger.info("✅ Pipeline initialized with config: %s", self.config)

    @staticmethod
    def _default_config() -> Dict:
        """Default pipeline configuration."""
        return {
            "cleaning": {
                "outlier_nb_neighbors": 20,
                "outlier_std_ratio": 2.0,
                "confidence_threshold": 0.5,
            },
            "voxel_size": 0.01,  # 10mm downsampling
            "mesh_depth": 9,  # Poisson reconstruction depth
        }

    def process(
        self,
        input_ply: str,
        scan_id: str,
        output_dir: str = ".",
        verbose: bool = True,
    ) -> Dict[str, str]:
        """
        Process raw point cloud through full pipeline.

        Args:
            input_ply: Path to input .ply file
            scan_id: Unique scan identifier
            output_dir: Output directory for results
            verbose: Enable verbose logging

        Returns:
            Dictionary with output file paths (fbx, glb, debug_ply)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        logger.info("[%s] ========== PIPELINE START ==========", scan_id)

        try:
            # ===== LOAD =====
            logger.info("[%s] Stage 0: Loading point cloud...", scan_id)
            pcd = o3d.io.read_point_cloud(str(input_ply))
            logger.info("[%s]   Input: %d points", scan_id, len(pcd.points))

            # Extract confidence from RGB if available
            confidences = None
            if pcd.has_colors():
                colors = np.asarray(pcd.colors)
                # Red channel as confidence metric (0-1)
                confidences = colors[:, 0]

            # ===== STAGE 1: CLEANING =====
            logger.info("[%s] Stage 1: Noise removal & outlier filtering...", scan_id)
            pcd = self.cleaner.clean(pcd, confidences)
            logger.info("[%s]   After cleaning: %d points", scan_id, len(pcd.points))

            # ===== STAGE 2: DOWNSAMPLING =====
            logger.info("[%s] Stage 2: Voxel downsampling (%.3f m)...", scan_id, self.config["voxel_size"])
            pcd = self.downsampler.downsample(pcd)
            logger.info("[%s]   After downsampling: %d points", scan_id, len(pcd.points))

            # ===== STAGE 3: NORMALS =====
            logger.info("[%s] Stage 3: Normal estimation...", scan_id)
            pcd = self.estimator.estimate(pcd)
            logger.info("[%s]   Normals estimated", scan_id)

            # ===== STAGE 4: MESHING =====
            logger.info("[%s] Stage 4: Poisson surface reconstruction...", scan_id)
            mesh = self.generator.generate_poisson(pcd)
            logger.info(
                "[%s]   Mesh: %d vertices, %d triangles",
                scan_id,
                len(mesh.vertices),
                len(mesh.triangles),
            )

            # Save intermediate mesh for debugging
            debug_ply = output_dir / f"{scan_id}_mesh_raw.ply"
            o3d.io.write_triangle_mesh(str(debug_ply), mesh)

            # ===== STAGE 5: MESH CLEANUP =====
            logger.info("[%s] Stage 5: Mesh cleanup & optimization...", scan_id)
            mesh = self.mesh_cleaner.clean(mesh)
            logger.info(
                "[%s]   After cleanup: %d vertices, %d triangles",
                scan_id,
                len(mesh.vertices),
                len(mesh.triangles),
            )

            # ===== STAGE 6: EXPORT =====
            logger.info("[%s] Stage 6: Exporting to FBX & glTF...", scan_id)
            fbx_path = output_dir / f"{scan_id}.fbx"
            glb_path = output_dir / f"{scan_id}.glb"
            ply_path = output_dir / f"{scan_id}.ply"

            self.exporter.export_fbx(mesh, str(fbx_path))
            self.exporter.export_glb(mesh, str(glb_path))
            self.exporter.export_ply(mesh, str(ply_path))

            elapsed = time.time() - start_time
            logger.info("[%s] ✅ Pipeline complete! (%.2f sec)", scan_id, elapsed)

            return {
                "fbx_path": str(fbx_path),
                "glb_path": str(glb_path),
                "ply_path": str(ply_path),
                "debug_ply": str(debug_ply),
                "elapsed_sec": elapsed,
            }

        except Exception as e:
            logger.error("[%s] ❌ Pipeline failed: %s", scan_id, str(e), exc_info=True)
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.pipeline <input.ply> [scan_id] [output_dir]")
        sys.exit(1)

    input_ply = sys.argv[1]
    scan_id = sys.argv[2] if len(sys.argv) > 2 else Path(input_ply).stem
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    pipeline = ScanProcessingPipeline()
    result = pipeline.process(input_ply, scan_id, output_dir)

    print("\n📊 Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
