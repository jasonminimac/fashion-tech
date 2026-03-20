#!/usr/bin/env python3
"""
Fashion Tech — CLO3D Garment Importer

Parse CLO3D .zprj files and extract garment assets for web import pipeline.

Usage:
    python import_clo3d.py garment.zprj --output ./extracted/ --validate --verbose
    
    Options:
    --output: Directory to extract files (default: ./extracted/)
    --validate: Run validation checks after extraction (default: True)
    --verbose: Print detailed progress (default: False)

Author: Fashion Tech Garment Engineering
Date: 2026-03-18
Status: Production-ready for Week 1 MVP
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys


class CLO3DImporter:
    """Parser and extractor for CLO3D .zprj files."""
    
    def __init__(self, zprj_path: str, verbose: bool = False):
        """
        Initialize CLO3D importer.
        
        Args:
            zprj_path: Path to .zprj file
            verbose: Enable verbose logging
        """
        self.zprj_path = Path(zprj_path)
        self.verbose = verbose
        
        if not self.zprj_path.exists():
            raise FileNotFoundError(f"CLO3D file not found: {zprj_path}")
        
        try:
            self.archive = zipfile.ZipFile(self.zprj_path, 'r')
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid ZIP file: {zprj_path}")
        
        self.metadata = {}
        self.textures = []
        self.geometry = None
        self.materials = None
        self.validation_errors = []
        self.validation_warnings = []
    
    def log(self, message: str, level: str = "INFO"):
        """Print verbose log message."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def extract_metadata(self) -> Optional[Dict]:
        """
        Parse CLO3D XML root to extract garment metadata.
        
        Returns:
            Dictionary with metadata or None if extraction fails
        """
        self.log("Extracting metadata from CLO3D XML...")
        
        try:
            # CLO3D root.xml structure varies, try common locations
            root_xml = None
            
            # Try standard CLO3D structure
            if 'root.xml' in self.archive.namelist():
                root_xml = self.archive.read('root.xml')
            elif 'clo_3d_root.xml' in self.archive.namelist():
                root_xml = self.archive.read('clo_3d_root.xml')
            else:
                # Fallback: scan for any XML file
                xml_files = [f for f in self.archive.namelist() if f.endswith('.xml')]
                if xml_files:
                    root_xml = self.archive.read(xml_files[0])
                    self.log(f"Found XML at: {xml_files[0]}", "WARN")
            
            if not root_xml:
                raise ValueError("No XML metadata found in .zprj")
            
            tree = ET.fromstring(root_xml)
            
            # Extract common metadata (with fallbacks)
            def get_text(path: str, default: str = "Unknown") -> str:
                elem = tree.find(f"./{path}")
                return elem.text if elem is not None and elem.text else default
            
            self.metadata = {
                'garment_name': get_text('garmentName', 'Untitled Garment'),
                'brand': get_text('brand', 'Unknown Brand'),
                'sku': get_text('sku', ''),
                'category': get_text('category', 'garment'),
                'fabric_type': get_text('fabricType', 'cotton'),
                'color': get_text('color', 'mixed'),
                'material': get_text('material', '100% unknown'),
                'description': get_text('description', ''),
                'scale_factor_m': 1.0,  # Default to M size
            }
            
            self.log(f"✓ Extracted metadata: {self.metadata['garment_name']}", "INFO")
            return self.metadata
            
        except Exception as e:
            msg = f"Failed to extract metadata: {str(e)}"
            self.log(msg, "ERROR")
            self.validation_errors.append(msg)
            return None
    
    def extract_geometry(self) -> Optional[str]:
        """
        Extract embedded OBJ mesh from .zprj.
        
        Returns:
            OBJ file content as string or None if extraction fails
        """
        self.log("Extracting geometry (OBJ mesh)...")
        
        try:
            # Look for OBJ files in archive
            obj_files = [f for f in self.archive.namelist() if f.endswith('.obj')]
            
            if not obj_files:
                msg = "No OBJ geometry file found in .zprj"
                self.validation_errors.append(msg)
                self.log(msg, "ERROR")
                return None
            
            # Use first OBJ found
            obj_file = obj_files[0]
            obj_data = self.archive.read(obj_file).decode('utf-8', errors='replace')
            
            # Count vertices and faces for validation
            vertex_count = len([l for l in obj_data.split('\n') if l.startswith('v ')])
            face_count = len([l for l in obj_data.split('\n') if l.startswith('f ')])
            
            self.geometry = obj_data
            self.metadata['vertex_count'] = vertex_count
            self.metadata['face_count'] = face_count
            
            self.log(f"✓ Extracted geometry: {vertex_count} vertices, {face_count} faces", "INFO")
            
            return self.geometry
            
        except Exception as e:
            msg = f"Failed to extract geometry: {str(e)}"
            self.log(msg, "ERROR")
            self.validation_errors.append(msg)
            return None
    
    def extract_textures(self) -> List[Dict]:
        """
        Extract all embedded texture files.
        
        Returns:
            List of texture dictionaries with name, data, size
        """
        self.log("Extracting textures...")
        
        texture_extensions = ('.jpg', '.jpeg', '.png', '.tga', '.bmp')
        textures = []
        
        try:
            for name in self.archive.namelist():
                if any(name.lower().endswith(ext) for ext in texture_extensions):
                    texture_data = self.archive.read(name)
                    
                    # Categorize texture by name
                    name_lower = name.lower()
                    if any(x in name_lower for x in ['color', 'diffuse', 'albedo']):
                        tex_type = 'color'
                    elif any(x in name_lower for x in ['normal', 'norm']):
                        tex_type = 'normal'
                    elif any(x in name_lower for x in ['rough', 'roughness']):
                        tex_type = 'roughness'
                    elif any(x in name_lower for x in ['spec', 'specular']):
                        tex_type = 'specular'
                    elif any(x in name_lower for x in ['ao', 'ambient']):
                        tex_type = 'ao'
                    else:
                        tex_type = 'unknown'
                    
                    textures.append({
                        'name': os.path.basename(name),
                        'type': tex_type,
                        'data': texture_data,
                        'size_mb': len(texture_data) / (1024 * 1024),
                        'original_path': name
                    })
            
            self.textures = textures
            self.log(f"✓ Extracted {len(textures)} textures", "INFO")
            for tex in textures:
                self.log(f"  - {tex['type']:10} {tex['name']:30} ({tex['size_mb']:.2f} MB)", "INFO")
            
            return textures
            
        except Exception as e:
            msg = f"Failed to extract textures: {str(e)}"
            self.log(msg, "ERROR")
            self.validation_errors.append(msg)
            return []
    
    def extract_materials(self) -> Optional[Dict]:
        """
        Extract material definitions (MTL files).
        
        Returns:
            Material data or None if not found
        """
        self.log("Extracting materials...")
        
        try:
            mtl_files = [f for f in self.archive.namelist() if f.endswith('.mtl')]
            
            if mtl_files:
                mtl_data = self.archive.read(mtl_files[0]).decode('utf-8', errors='replace')
                self.materials = mtl_data
                self.log(f"✓ Extracted materials from {mtl_files[0]}", "INFO")
                return self.materials
            else:
                self.log("No MTL file found (optional)", "WARN")
                return None
                
        except Exception as e:
            self.log(f"Warning: Failed to extract materials: {str(e)}", "WARN")
            return None
    
    def validate(self) -> Dict[str, any]:
        """
        Validate extracted assets against checklist.
        
        Returns:
            Validation result dict with errors, warnings, and overall status
        """
        self.log("Validating extracted assets...")
        
        # Reset validation lists
        self.validation_errors = []
        self.validation_warnings = []
        
        # Check metadata completeness
        required_metadata = ['garment_name', 'brand', 'fabric_type']
        for field in required_metadata:
            if field not in self.metadata or not self.metadata[field]:
                self.validation_errors.append(f"Missing metadata: {field}")
        
        # Check if garment name is placeholder
        if self.metadata.get('garment_name') == 'Untitled Garment':
            self.validation_warnings.append("Garment name is placeholder (Untitled Garment) — rename during import")
        
        # Check geometry
        if not self.geometry or len(self.geometry) < 100:
            self.validation_errors.append("Geometry is missing or too small")
        
        # Check vertex/face count (should be reasonable for garment)
        vertex_count = self.metadata.get('vertex_count', 0)
        if vertex_count == 0:
            self.validation_errors.append("No vertices detected in geometry")
        elif vertex_count > 100000:
            self.validation_warnings.append(f"Very high poly count ({vertex_count} vertices) — will need decimation")
        elif vertex_count < 500:
            self.validation_warnings.append(f"Very low poly count ({vertex_count} vertices) — may be too simple")
        
        # Check textures
        if len(self.textures) == 0:
            self.validation_warnings.append("No textures found — will use placeholder color")
        else:
            # Check for essential texture types
            tex_types = {t['type'] for t in self.textures}
            if 'color' not in tex_types:
                self.validation_warnings.append("No color/diffuse texture found — will use plain color")
        
        # Check texture sizes
        for tex in self.textures:
            if tex['size_mb'] > 10:
                self.validation_warnings.append(f"Texture {tex['name']} is large ({tex['size_mb']:.1f}MB) — will be compressed")
        
        # Build result
        result = {
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'valid': len(self.validation_errors) == 0,
            'error_count': len(self.validation_errors),
            'warning_count': len(self.validation_warnings),
        }
        
        self.log(f"Validation result: {'PASS' if result['valid'] else 'FAIL'} ({result['error_count']} errors, {result['warning_count']} warnings)", "INFO")
        
        return result
    
    def export_to_folder(self, output_dir: str) -> bool:
        """
        Export extracted assets to folder structure.
        
        Args:
            output_dir: Destination directory
            
        Returns:
            True if export successful, False otherwise
        """
        self.log(f"Exporting to folder: {output_dir}")
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Export geometry
            if self.geometry:
                geo_path = output_path / 'geometry.obj'
                with open(geo_path, 'w') as f:
                    f.write(self.geometry)
                self.log(f"✓ Exported geometry to {geo_path}", "INFO")
            
            # Export materials
            if self.materials:
                mtl_path = output_path / 'materials.mtl'
                with open(mtl_path, 'w') as f:
                    f.write(self.materials)
                self.log(f"✓ Exported materials to {mtl_path}", "INFO")
            
            # Export textures
            textures_dir = output_path / 'textures'
            textures_dir.mkdir(exist_ok=True)
            
            for tex in self.textures:
                tex_path = textures_dir / tex['name']
                with open(tex_path, 'wb') as f:
                    f.write(tex['data'])
                self.log(f"✓ Exported texture to {tex_path}", "INFO")
            
            # Export metadata
            metadata_path = output_path / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            self.log(f"✓ Exported metadata to {metadata_path}", "INFO")
            
            # Export validation log
            if self.validation_errors or self.validation_warnings:
                validation_path = output_path / 'validation_report.txt'
                with open(validation_path, 'w') as f:
                    if self.validation_errors:
                        f.write("ERRORS:\n")
                        for err in self.validation_errors:
                            f.write(f"  - {err}\n")
                    if self.validation_warnings:
                        f.write("WARNINGS:\n")
                        for warn in self.validation_warnings:
                            f.write(f"  - {warn}\n")
                self.log(f"✓ Exported validation report to {validation_path}", "INFO")
            
            self.log(f"✓ Export complete to {output_dir}", "INFO")
            return True
            
        except Exception as e:
            msg = f"Export failed: {str(e)}"
            self.log(msg, "ERROR")
            return False
    
    def run_full_import(self, output_dir: str) -> Dict:
        """
        Execute full import workflow: extract → validate → export.
        
        Args:
            output_dir: Output directory for extracted assets
            
        Returns:
            Result dictionary with status and details
        """
        self.log(f"Starting full CLO3D import workflow for: {self.zprj_path}")
        self.log("=" * 70)
        
        # Step 1: Extract metadata
        if not self.extract_metadata():
            return {'success': False, 'error': 'Metadata extraction failed'}
        
        # Step 2: Extract geometry
        if not self.extract_geometry():
            return {'success': False, 'error': 'Geometry extraction failed'}
        
        # Step 3: Extract textures
        self.extract_textures()  # Non-blocking (warnings only)
        
        # Step 4: Extract materials
        self.extract_materials()  # Non-blocking
        
        # Step 5: Validate
        validation = self.validate()
        
        # Step 6: Export
        if validation['valid'] or True:  # Export even with warnings
            export_success = self.export_to_folder(output_dir)
        else:
            export_success = False
        
        # Return summary
        result = {
            'success': export_success and validation['valid'],
            'validation': validation,
            'metadata': self.metadata,
            'export_path': output_dir if export_success else None,
        }
        
        self.log("=" * 70)
        self.log(f"Import {'COMPLETE' if result['success'] else 'COMPLETED WITH ISSUES'}", "INFO")
        
        return result


def main():
    """CLI entry point for CLO3D importer."""
    
    parser = argparse.ArgumentParser(
        description="Fashion Tech CLO3D Importer — Parse and extract CLO3D garment files"
    )
    parser.add_argument('zprj_file', help='Path to CLO3D .zprj file')
    parser.add_argument('--output', '-o', default='./extracted', help='Output directory (default: ./extracted)')
    parser.add_argument('--validate', '-v', action='store_true', default=True, help='Run validation checks')
    parser.add_argument('--verbose', '-vv', action='store_true', help='Verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("Fashion Tech CLO3D Importer")
        print("=" * 70)
    
    try:
        importer = CLO3DImporter(args.zprj_file, verbose=args.verbose)
        result = importer.run_full_import(args.output)
        
        # Print result summary
        if not args.quiet:
            print()
            if result['success']:
                print("✓ SUCCESS: CLO3D import completed successfully")
                print(f"  Garment: {result['metadata']['garment_name']}")
                print(f"  Assets exported to: {result['export_path']}")
            else:
                print("✗ FAILED: CLO3D import encountered errors")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                if 'validation' in result:
                    print(f"  Validation errors: {result['validation']['error_count']}")
            print()
        
        return 0 if result['success'] else 1
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
