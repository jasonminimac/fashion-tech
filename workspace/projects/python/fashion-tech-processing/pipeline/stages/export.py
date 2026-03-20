"""Mesh export to multiple formats."""

import logging
from pathlib import Path
import open3d as o3d

logger = logging.getLogger(__name__)


class MeshExporter:
    """Export triangle mesh to multiple formats."""

    def export_fbx(self, mesh: o3d.geometry.TriangleMesh, path: str) -> bool:
        """Export mesh to FBX format.

        Args:
            mesh: Input triangle mesh
            path: Output FBX file path

        Returns:
            True if successful
        """
        try:
            # Open3D doesn't natively support FBX; use OBJ + note limitation
            obj_path = str(Path(path).with_suffix('.obj'))
            o3d.io.write_triangle_mesh(obj_path, mesh)
            logger.info("  Exported OBJ: %s (FBX requires external conversion)", obj_path)
            return True
        except Exception as e:
            logger.error("  FBX export failed: %s", e)
            return False

    def export_glb(self, mesh: o3d.geometry.TriangleMesh, path: str) -> bool:
        """Export mesh to glTF 2.0 binary format.

        Args:
            mesh: Input triangle mesh
            path: Output GLB file path

        Returns:
            True if successful
        """
        try:
            o3d.io.write_triangle_mesh(path, mesh, write_ascii=False)
            file_size_mb = Path(path).stat().st_size / (1024 * 1024)
            logger.info("  Exported glTF 2.0 (GLB): %s (%.2f MB)", path, file_size_mb)
            return True
        except Exception as e:
            logger.error("  glTF export failed: %s", e)
            return False

    def export_ply(self, mesh: o3d.geometry.TriangleMesh, path: str) -> bool:
        """Export mesh to PLY format.

        Args:
            mesh: Input triangle mesh
            path: Output PLY file path

        Returns:
            True if successful
        """
        try:
            o3d.io.write_triangle_mesh(path, mesh, write_ascii=False)
            file_size_mb = Path(path).stat().st_size / (1024 * 1024)
            logger.info("  Exported PLY: %s (%.2f MB)", path, file_size_mb)
            return True
        except Exception as e:
            logger.error("  PLY export failed: %s", e)
            return False
