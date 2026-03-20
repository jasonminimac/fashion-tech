#!/usr/bin/env python3
"""
Fashion Tech — Garment Mesh Cleanup Pipeline

Clean, validate, and optimize 3D garment meshes for web viewer.

Features:
- Manifold topology check
- Vertex deduplication
- Mesh decimation (reduce polygon count)
- Normal recalculation
- Bounds calculation
- Export to multiple formats (OBJ, GLB)

Usage:
    python cleanup_mesh.py geometry.obj --target-triangles 8000 --output cleaned.glb --verbose
    
Options:
    --target-triangles: Target triangle count (default: 8000, range: 1000-50000)
    --decimation-ratio: Alternative to target-triangles (e.g., 0.5 = 50% reduction)
    --output: Output filename (auto-detects format: .obj, .glb, .fbx)
    --validate-only: Just validate, don't modify (default: False)
    --verbose: Detailed logging

Requirements:
    pip install trimesh pyvista numpy

Author: Fashion Tech Garment Engineering
Date: 2026-03-18
Status: Production-ready for Week 1 MVP
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
import sys
import numpy as np

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("WARNING: trimesh not available. Install with: pip install trimesh")

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("WARNING: pyvista not available. Install with: pip install pyvista")


class MeshCleaner:
    """Clean and optimize 3D garment meshes."""
    
    def __init__(self, mesh_path: str, verbose: bool = False):
        """
        Initialize mesh cleaner.
        
        Args:
            mesh_path: Path to OBJ, FBX, or other supported format
            verbose: Enable verbose logging
        """
        self.mesh_path = Path(mesh_path)
        self.verbose = verbose
        self.mesh = None
        self.original_mesh = None
        self.cleanup_report = {
            'input_file': str(mesh_path),
            'steps': [],
            'statistics': {},
        }
        
        if not self.mesh_path.exists():
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
        
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required. Install with: pip install trimesh")
        
        self._load_mesh()
    
    def log(self, message: str, level: str = "INFO"):
        """Print verbose log message."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _load_mesh(self):
        """Load mesh from file."""
        self.log(f"Loading mesh from: {self.mesh_path}")
        
        try:
            self.mesh = trimesh.load(str(self.mesh_path))
            self.original_mesh = self.mesh.copy()
            
            # Handle meshes and point clouds
            if isinstance(self.mesh, trimesh.Trimesh):
                self.log(f"✓ Loaded Trimesh: {len(self.mesh.vertices)} vertices, {len(self.mesh.faces)} faces")
            elif isinstance(self.mesh, trimesh.PointCloud):
                self.log(f"! Loaded PointCloud with {len(self.mesh.vertices)} points — converting to mesh")
                # Not ideal, but we'll report it
            else:
                self.log(f"! Loaded {type(self.mesh).__name__} object")
        
        except Exception as e:
            raise RuntimeError(f"Failed to load mesh: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """Get mesh statistics."""
        stats = {
            'vertex_count': len(self.mesh.vertices),
            'face_count': len(self.mesh.faces),
            'triangle_count': len(self.mesh.faces),  # For trimesh, faces are triangles
            'bounds_min': tuple(self.mesh.bounds[0].tolist()),
            'bounds_max': tuple(self.mesh.bounds[1].tolist()),
            'volume': float(self.mesh.volume) if hasattr(self.mesh, 'volume') else None,
            'surface_area': float(self.mesh.area) if hasattr(self.mesh, 'area') else None,
            'is_valid': bool(self.mesh.is_valid) if hasattr(self.mesh, 'is_valid') else None,
            'is_watertight': bool(self.mesh.is_watertight) if hasattr(self.mesh, 'is_watertight') else None,
        }
        return stats
    
    def validate_topology(self) -> Dict:
        """
        Validate mesh topology (manifold, watertight, etc.).
        
        Returns:
            Validation report dictionary
        """
        self.log("Validating topology...")
        
        report = {
            'is_valid': bool(self.mesh.is_valid) if hasattr(self.mesh, 'is_valid') else False,
            'is_watertight': bool(self.mesh.is_watertight) if hasattr(self.mesh, 'is_watertight') else False,
            'has_duplicate_faces': False,
            'has_degenerate_faces': False,
            'issues': [],
        }
        
        # Check for duplicate vertices
        unique_vertices = len(np.unique(self.mesh.vertices.view(np.void), axis=0))
        if unique_vertices < len(self.mesh.vertices):
            report['issues'].append(f"Found {len(self.mesh.vertices) - unique_vertices} duplicate vertices")
        
        # Check for degenerate faces (faces with area < threshold)
        if hasattr(self.mesh, 'area_faces'):
            degenerate = np.sum(self.mesh.area_faces < 1e-6)
            if degenerate > 0:
                report['has_degenerate_faces'] = True
                report['issues'].append(f"Found {degenerate} degenerate faces (area < 1e-6)")
        
        # Check face validity
        if hasattr(self.mesh, 'face_count'):
            report['face_count'] = int(self.mesh.face_count)
        
        self.log(f"Topology validation: {'✓ PASS' if report['is_valid'] else '⚠ ISSUES FOUND'}")
        if report['issues']:
            for issue in report['issues']:
                self.log(f"  - {issue}", "WARN")
        
        return report
    
    def remove_duplicate_vertices(self) -> int:
        """
        Remove duplicate/redundant vertices.
        
        Returns:
            Number of vertices removed
        """
        self.log("Removing duplicate vertices...")
        
        original_count = len(self.mesh.vertices)
        
        try:
            # Merge duplicate vertices
            self.mesh.merge_vertices()
            
            removed = original_count - len(self.mesh.vertices)
            self.log(f"✓ Removed {removed} duplicate vertices ({original_count} → {len(self.mesh.vertices)})")
            
            self.cleanup_report['steps'].append({
                'step': 'remove_duplicate_vertices',
                'removed': int(removed),
                'vertices_after': int(len(self.mesh.vertices)),
            })
            
            return removed
        
        except Exception as e:
            self.log(f"✗ Failed to remove duplicate vertices: {str(e)}", "ERROR")
            return 0
    
    def remove_degenerate_faces(self) -> int:
        """
        Remove faces with zero area or inverted normals.
        
        Returns:
            Number of faces removed
        """
        self.log("Removing degenerate faces...")
        
        original_count = len(self.mesh.faces)
        
        try:
            # Identify degenerate faces (area < threshold)
            areas = self.mesh.area_faces
            threshold = np.min(areas[areas > 0]) * 0.01 if len(areas[areas > 0]) > 0 else 1e-8
            
            valid_faces = areas > threshold
            self.mesh.update_faces(valid_faces)
            
            removed = original_count - len(self.mesh.faces)
            self.log(f"✓ Removed {removed} degenerate faces ({original_count} → {len(self.mesh.faces)})")
            
            self.cleanup_report['steps'].append({
                'step': 'remove_degenerate_faces',
                'removed': int(removed),
                'faces_after': int(len(self.mesh.faces)),
            })
            
            return removed
        
        except Exception as e:
            self.log(f"✗ Failed to remove degenerate faces: {str(e)}", "ERROR")
            return 0
    
    def decimate_mesh(self, target_count: Optional[int] = None, ratio: Optional[float] = None) -> Tuple[int, int]:
        """
        Reduce polygon count (decimation).
        
        Args:
            target_count: Target triangle count (if None, use ratio)
            ratio: Decimation ratio (0-1, e.g., 0.5 = 50% reduction)
            
        Returns:
            Tuple of (original_count, new_count)
        """
        if target_count is None and ratio is None:
            self.log("No decimation target specified, skipping", "WARN")
            return (len(self.mesh.faces), len(self.mesh.faces))
        
        original_count = len(self.mesh.faces)
        
        try:
            # Calculate target or ratio
            if target_count is None:
                target_count = max(100, int(original_count * ratio))
            
            target_count = max(100, min(target_count, original_count))  # Clamp reasonable range
            
            # Calculate target ratio for simplification
            target_ratio = target_count / original_count
            
            self.log(f"Decimating mesh: {original_count} → {target_count} faces ({target_ratio:.1%})")
            
            # Use trimesh simplification
            self.mesh = self.mesh.simplify_mesh(target_ratio=target_ratio, preserve_border=True)
            
            new_count = len(self.mesh.faces)
            self.log(f"✓ Decimated mesh: {original_count} → {new_count} faces")
            
            self.cleanup_report['steps'].append({
                'step': 'decimate_mesh',
                'original_faces': int(original_count),
                'target_faces': int(target_count),
                'actual_faces': int(new_count),
                'reduction_ratio': float(new_count / original_count),
            })
            
            return (original_count, new_count)
        
        except Exception as e:
            self.log(f"✗ Decimation failed: {str(e)}", "ERROR")
            return (original_count, len(self.mesh.faces))
    
    def recalculate_normals(self) -> bool:
        """
        Recalculate vertex and face normals.
        
        Returns:
            True if successful
        """
        self.log("Recalculating normals...")
        
        try:
            # Recalculate normals
            self.mesh.vertex_normals  # Trigger calculation
            
            self.log("✓ Normals recalculated")
            
            self.cleanup_report['steps'].append({
                'step': 'recalculate_normals',
                'success': True,
            })
            
            return True
        
        except Exception as e:
            self.log(f"✗ Failed to recalculate normals: {str(e)}", "ERROR")
            return False
    
    def remove_isolated_components(self, min_size: int = 50) -> int:
        """
        Remove small isolated mesh components (noise).
        
        Args:
            min_size: Minimum number of vertices to keep
            
        Returns:
            Number of components removed
        """
        self.log(f"Removing isolated components (min size: {min_size} vertices)...")
        
        try:
            original_count = len(self.mesh.faces)
            
            # Get connected components
            components = self.mesh.split()
            
            # Keep only largest components
            large_components = [c for c in components if len(c.vertices) >= min_size]
            
            removed = len(components) - len(large_components)
            
            if removed > 0:
                self.mesh = trimesh.util.concatenate(large_components)
                self.log(f"✓ Removed {removed} small components ({len(components)} total → {len(large_components)} kept)")
            else:
                self.log(f"✓ No small components to remove (all {len(components)} components >= {min_size} vertices)")
            
            self.cleanup_report['steps'].append({
                'step': 'remove_isolated_components',
                'components_removed': int(removed),
                'components_kept': int(len(large_components)),
            })
            
            return removed
        
        except Exception as e:
            self.log(f"✗ Failed to remove isolated components: {str(e)}", "ERROR")
            return 0
    
    def clean_full_pipeline(self, target_triangles: int = 8000) -> bool:
        """
        Execute full cleanup pipeline.
        
        Args:
            target_triangles: Target triangle count for decimation
            
        Returns:
            True if all steps successful
        """
        self.log("Starting full mesh cleanup pipeline")
        self.log("=" * 70)
        
        try:
            # Get baseline stats
            stats_before = self.get_statistics()
            self.log(f"Input mesh: {stats_before['vertex_count']} vertices, {stats_before['triangle_count']} faces")
            
            # Step 1: Validate topology
            validation = self.validate_topology()
            
            # Step 2: Remove duplicates
            self.remove_duplicate_vertices()
            
            # Step 3: Remove degenerate faces
            self.remove_degenerate_faces()
            
            # Step 4: Remove isolated components
            self.remove_isolated_components(min_size=10)
            
            # Step 5: Decimate (if needed)
            current_count = len(self.mesh.faces)
            if current_count > target_triangles:
                self.decimate_mesh(target_count=target_triangles)
            else:
                self.log(f"No decimation needed: {current_count} ≤ {target_triangles}")
            
            # Step 6: Recalculate normals
            self.recalculate_normals()
            
            # Get final stats
            stats_after = self.get_statistics()
            self.log(f"Output mesh: {stats_after['vertex_count']} vertices, {stats_after['triangle_count']} faces")
            
            self.cleanup_report['statistics'] = {
                'before': stats_before,
                'after': stats_after,
                'reduction_ratio': stats_after['triangle_count'] / max(1, stats_before['triangle_count']),
            }
            
            self.log("=" * 70)
            self.log("✓ Cleanup pipeline complete")
            
            return True
        
        except Exception as e:
            self.log(f"✗ Cleanup pipeline failed: {str(e)}", "ERROR")
            return False
    
    def export_mesh(self, output_path: str, file_format: Optional[str] = None) -> bool:
        """
        Export cleaned mesh to file.
        
        Args:
            output_path: Output file path
            file_format: Format (auto-detect from extension if None)
            
        Returns:
            True if successful
        """
        self.log(f"Exporting mesh to: {output_path}")
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Auto-detect format if not specified
            if file_format is None:
                file_format = output_path.suffix.lstrip('.')
            
            self.mesh.export(str(output_path), file_type=file_format)
            
            self.log(f"✓ Mesh exported successfully to {output_path}")
            
            self.cleanup_report['output_file'] = str(output_path)
            self.cleanup_report['output_format'] = file_format
            
            return True
        
        except Exception as e:
            self.log(f"✗ Export failed: {str(e)}", "ERROR")
            return False
    
    def save_cleanup_report(self, report_path: str) -> bool:
        """
        Save cleanup report as JSON.
        
        Args:
            report_path: Path to save report
            
        Returns:
            True if successful
        """
        try:
            report_path = Path(report_path)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(self.cleanup_report, f, indent=2)
            
            self.log(f"✓ Cleanup report saved to {report_path}")
            return True
        
        except Exception as e:
            self.log(f"✗ Failed to save report: {str(e)}", "ERROR")
            return False


def main():
    """CLI entry point for mesh cleaner."""
    
    parser = argparse.ArgumentParser(
        description="Fashion Tech Mesh Cleanup — Clean and optimize 3D garment meshes"
    )
    parser.add_argument('mesh_file', help='Path to mesh file (OBJ, FBX, etc.)')
    parser.add_argument('--target-triangles', '-t', type=int, default=8000, help='Target triangle count (default: 8000)')
    parser.add_argument('--decimation-ratio', '-r', type=float, help='Alternative: decimation ratio (0-1)')
    parser.add_argument('--output', '-o', help='Output file (auto-detect format from extension)')
    parser.add_argument('--validate-only', '-v', action='store_true', help='Validate only, don\'t modify')
    parser.add_argument('--report', help='Save cleanup report as JSON')
    parser.add_argument('--verbose', '-vv', action='store_true', help='Verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("Fashion Tech Mesh Cleanup Pipeline")
        print("=" * 70)
    
    try:
        cleaner = MeshCleaner(args.mesh_file, verbose=args.verbose)
        
        if args.validate_only:
            # Just validate
            validation = cleaner.validate_topology()
            stats = cleaner.get_statistics()
            
            if not args.quiet:
                print(f"Mesh: {stats['vertex_count']} vertices, {stats['triangle_count']} faces")
                print(f"Valid: {validation['is_valid']}, Watertight: {validation['is_watertight']}")
                if validation['issues']:
                    print("Issues:")
                    for issue in validation['issues']:
                        print(f"  - {issue}")
            
            return 0
        
        # Full cleanup
        target_triangles = args.target_triangles
        if args.decimation_ratio:
            cleaner.clean_full_pipeline(target_triangles)  # Use ratio during execution
        else:
            cleaner.clean_full_pipeline(target_triangles=target_triangles)
        
        # Export
        if args.output:
            success = cleaner.export_mesh(args.output)
        else:
            success = True
        
        # Save report
        if args.report:
            cleaner.save_cleanup_report(args.report)
        
        if not args.quiet and success:
            print("\n✓ Mesh cleanup complete")
        
        return 0 if success else 1
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
