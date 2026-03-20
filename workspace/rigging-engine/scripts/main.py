#!/usr/bin/env python3
"""
Main CLI entry point for Blender rigging pipeline.

Usage:
  python scripts/main.py test_data/fixtures/average_male.fbx \\
    --output /tmp/rigged.blend \\
    --validate \\
    --verbose
"""

import argparse
import sys
import pathlib

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from framework.mesh_importer import import_and_validate_fbx
from framework.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Blender Rigging Automation Pipeline"
    )

    parser.add_argument(
        "input_fbx",
        help="Input FBX file (scanned body mesh)",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output .blend file path (default: same as input)",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate mesh and exit (don't rig)",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Validate input
    input_path = pathlib.Path(args.input_fbx)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # Default output path
    if args.output is None:
        args.output = str(input_path.with_suffix(".blend"))

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Import and validate
        logger.info(f"Processing: {input_path}")
        mesh, analysis = import_and_validate_fbx(
            str(input_path),
            verbose=args.verbose,
        )

        if args.validate:
            logger.info("✓ Validation complete (--validate flag set)")
            sys.exit(0)

        # TODO: Implement rigging in Week 3
        logger.info("[Week 2] Rigging not yet implemented. Coming in Week 3.")

        # For now, just report success on import
        logger.info(f"✓ Body analysis complete:")
        logger.info(f"  Height: {analysis['height']:.2f}m")
        logger.info(f"  Width: {analysis['width']:.2f}m")
        logger.info(f"  Type: {analysis['body_type'].value}")

        logger.info("✓ Pipeline stage 1 complete!")

    except Exception as e:
        logger.error(f"✗ Pipeline failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
