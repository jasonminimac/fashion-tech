#!/usr/bin/env python3
"""
Fashion Tech — Fabric Physics Parameters Lookup Table

Pre-configured physics parameters for common fabric types.
Used by cloth simulation engine in Phase 2.
Can be tuned per garment.

Date: 2026-03-18
Version: 1.0
Author: Fashion Tech Garment Engineering
"""

import json
from typing import Dict, Optional
from pathlib import Path


# ============================================================================
# FABRIC PHYSICS PARAMETERS
# ============================================================================
# Each fabric has 9 parameters for cloth simulation
# Values range 0-1 unless otherwise noted

FABRIC_PARAMETERS = {
    "cotton": {
        "display_name": "Cotton (Medium Weight)",
        "category": "woven",
        "mass_density_g_per_m2": 150,
        "bending_stiffness": 0.5,      # How easily it creases
        "damping": 0.08,               # Energy loss (wrinkles fade)
        "elasticity": 0.15,            # Stretch capability (15%)
        "air_damping": 0.02,           # Air resistance
        "friction_coefficient": 0.3,   # Slipperiness
        "wrinkle_intensity": 0.8,      # How pronounced wrinkles appear
        "settling_speed": 0.5,         # How fast fabric settles
        "shine_level": 0.1,            # Specularity (0=matte, 1=glossy)
        "typical_color": "E8D7C3",     # Hex color reference
        "description": "Heavy, natural fiber. Settles with distinct wrinkles. Common in casual wear.",
        "design_notes": "Natural, comfortable. Wrinkles easily. Good for structured garments.",
        "suitable_for": ["shirts", "dresses", "casual wear", "structured pieces"],
    },
    
    "cotton_light": {
        "display_name": "Cotton (Lightweight)",
        "category": "woven",
        "mass_density_g_per_m2": 100,
        "bending_stiffness": 0.3,
        "damping": 0.05,
        "elasticity": 0.1,
        "air_damping": 0.01,
        "friction_coefficient": 0.2,
        "wrinkle_intensity": 0.5,
        "settling_speed": 0.3,
        "shine_level": 0.05,
        "typical_color": "F5F5DC",
        "description": "Lightweight cotton. Minimal wrinkles. Breathable and delicate.",
        "design_notes": "Breathable. Less wrinkly than medium. Good for summer garments.",
        "suitable_for": ["t-shirts", "light dresses", "summer tops", "casual wear"],
    },
    
    "silk": {
        "display_name": "Silk",
        "category": "natural_smooth",
        "mass_density_g_per_m2": 80,
        "bending_stiffness": 0.1,      # Very soft, flows easily
        "damping": 0.02,               # Wrinkles fade quickly
        "elasticity": 0.05,            # Minimal stretch
        "air_damping": 0.01,           # Low air resistance
        "friction_coefficient": 0.15,  # Very slippery
        "wrinkle_intensity": 0.2,      # Very few wrinkles
        "settling_speed": 0.2,         # Settles quickly, smoothly
        "shine_level": 0.5,            # Glossy/lustrous appearance
        "typical_color": "F5E6D3",
        "description": "Luxurious natural fiber. Flows smoothly. Minimal permanent wrinkles.",
        "design_notes": "Slippery, forms soft folds. Premium feel. Good for draped garments.",
        "suitable_for": ["formal wear", "dresses", "blouses", "draped pieces", "luxury items"],
    },
    
    "denim": {
        "display_name": "Denim",
        "category": "woven_heavy",
        "mass_density_g_per_m2": 600,
        "bending_stiffness": 0.8,      # Very stiff, holds creases
        "damping": 0.12,               # Wrinkles persist
        "elasticity": 0.08,            # Resists stretching
        "air_damping": 0.03,           # High air resistance
        "friction_coefficient": 0.4,   # Medium grip
        "wrinkle_intensity": 0.6,      # Defined creases
        "settling_speed": 0.7,         # Slow settling, structured look
        "shine_level": 0.2,            # Matte with slight texture
        "typical_color": "3B4D5C",
        "description": "Heavy woven fabric. Stiff, structured. Defined creases and visible seams.",
        "design_notes": "Durable, visible construction. Holds shape. Icon of jeans/workwear.",
        "suitable_for": ["jeans", "jackets", "workwear", "structured pieces"],
    },
    
    "spandex": {
        "display_name": "Spandex / Lycra",
        "category": "synthetic_elastic",
        "mass_density_g_per_m2": 200,
        "bending_stiffness": 0.2,      # Flexible
        "damping": 0.25,               # High internal friction (stretchy)
        "elasticity": 0.85,            # Highly stretchable (85%+)
        "air_damping": 0.02,           # Low air resistance
        "friction_coefficient": 0.5,   # Grippy, hugs body
        "wrinkle_intensity": 0.1,      # Few wrinkles (fabric hugs body)
        "settling_speed": 0.9,         # Snaps back instantly
        "shine_level": 0.3,            # Slight sheen
        "typical_color": "1C1C1C",
        "description": "Synthetic elastic fiber. Stretches and recovers instantly. Form-fitting.",
        "design_notes": "High tension. Snappy recovery. Perfect for active/fitted wear.",
        "suitable_for": ["leggings", "athletic wear", "fitted tops", "swimwear", "dance wear"],
    },
    
    "polyester": {
        "display_name": "Polyester",
        "category": "synthetic",
        "mass_density_g_per_m2": 120,
        "bending_stiffness": 0.4,
        "damping": 0.06,
        "elasticity": 0.1,
        "air_damping": 0.015,
        "friction_coefficient": 0.25,
        "wrinkle_intensity": 0.4,
        "settling_speed": 0.4,
        "shine_level": 0.15,
        "typical_color": "D3D3D3",
        "description": "Synthetic fiber. Moderate drape. Wrinkle-resistant, durable.",
        "design_notes": "Practical. Washable. Less natural appearance. Good for performance wear.",
        "suitable_for": ["casual wear", "performance wear", "durable pieces", "blends"],
    },
    
    "blend_cotton_poly": {
        "display_name": "Cotton-Polyester Blend",
        "category": "blend",
        "mass_density_g_per_m2": 140,
        "bending_stiffness": 0.45,     # Between cotton and polyester
        "damping": 0.07,
        "elasticity": 0.12,
        "air_damping": 0.015,
        "friction_coefficient": 0.3,
        "wrinkle_intensity": 0.5,
        "settling_speed": 0.45,
        "shine_level": 0.12,
        "typical_color": "E0D5C7",
        "description": "Balanced blend. Combines best of cotton and polyester. Durable and comfortable.",
        "design_notes": "Practical blend. Good for everyday wear. Balances comfort and durability.",
        "suitable_for": ["everyday wear", "work clothes", "casual shirts", "versatile pieces"],
    },
    
    "linen": {
        "display_name": "Linen",
        "category": "natural_structured",
        "mass_density_g_per_m2": 160,
        "bending_stiffness": 0.6,
        "damping": 0.09,
        "elasticity": 0.08,
        "air_damping": 0.02,
        "friction_coefficient": 0.35,
        "wrinkle_intensity": 1.0,      # VERY wrinkly (by design)
        "settling_speed": 0.5,
        "shine_level": 0.08,
        "typical_color": "E8D7C3",
        "description": "Natural fiber. Heavy, structured. Pronounced creasing (intentional aesthetic).",
        "design_notes": "Rustic, textured look. Wrinkles are part of charm. Good for summer.",
        "suitable_for": ["summer wear", "casual dresses", "rustic aesthetic", "relaxed pieces"],
    },
    
    "wool": {
        "display_name": "Wool",
        "category": "natural_insulating",
        "mass_density_g_per_m2": 350,
        "bending_stiffness": 0.7,      # Holds structure
        "damping": 0.11,
        "elasticity": 0.06,
        "air_damping": 0.025,
        "friction_coefficient": 0.38,
        "wrinkle_intensity": 0.55,
        "settling_speed": 0.6,
        "shine_level": 0.25,
        "typical_color": "4A4A4A",
        "description": "Natural insulating fiber. Structured, holds form. Warm and formal.",
        "design_notes": "Formal, tailored look. Holds shape. Premium feel. Good for structured garments.",
        "suitable_for": ["blazers", "suits", "winter wear", "formal pieces", "tailored items"],
    },
    
    "jersey": {
        "display_name": "Jersey (Knit)",
        "category": "knit",
        "mass_density_g_per_m2": 160,
        "bending_stiffness": 0.2,      # Soft, flexible
        "damping": 0.05,
        "elasticity": 0.3,             # Moderate stretch (knit fabric)
        "air_damping": 0.01,
        "friction_coefficient": 0.22,
        "wrinkle_intensity": 0.3,
        "settling_speed": 0.35,
        "shine_level": 0.05,
        "typical_color": "C0C0C0",
        "description": "Soft knit fabric. Comfortable, stretchy, relaxed drape.",
        "design_notes": "Comfortable. Stretches and recovers. Good for casual wear and t-shirts.",
        "suitable_for": ["t-shirts", "casual wear", "comfortable pieces", "everyday shirts"],
    },
}

# ============================================================================
# FABRIC CATEGORIES
# ============================================================================
# Logical groupings for fabric selection and recommendations

FABRIC_CATEGORIES = {
    "woven": {
        "description": "Traditional woven fabrics (crisp, structured)",
        "fabrics": ["cotton", "cotton_light", "denim", "polyester", "linen"],
    },
    "natural": {
        "description": "Natural fibers (silk, cotton, linen, wool)",
        "fabrics": ["cotton", "cotton_light", "silk", "linen", "wool"],
    },
    "synthetic": {
        "description": "Synthetic fibers (polyester, spandex)",
        "fabrics": ["polyester", "spandex"],
    },
    "elastic": {
        "description": "Stretchy fabrics (spandex blends, jersey)",
        "fabrics": ["spandex", "jersey", "blend_cotton_poly"],
    },
    "formal": {
        "description": "Formal wear fabrics (silk, wool, linen)",
        "fabrics": ["silk", "wool", "blend_cotton_poly"],
    },
    "casual": {
        "description": "Casual wear fabrics (cotton, jersey)",
        "fabrics": ["cotton", "cotton_light", "jersey", "polyester"],
    },
    "structured": {
        "description": "Structured fabrics (denim, wool, linen)",
        "fabrics": ["denim", "wool", "linen"],
    },
    "draped": {
        "description": "Draping fabrics (silk, jersey)",
        "fabrics": ["silk", "jersey", "cotton_light"],
    },
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_fabric_params(fabric_type: str) -> Optional[Dict]:
    """Get parameters for a specific fabric type."""
    return FABRIC_PARAMETERS.get(fabric_type)

def get_fabrics_by_category(category: str) -> Optional[list]:
    """Get list of fabric types in a category."""
    cat = FABRIC_CATEGORIES.get(category)
    return cat['fabrics'] if cat else None

def get_fabric_categories() -> Dict:
    """Get all fabric categories."""
    return FABRIC_CATEGORIES

def export_to_json(output_path: str) -> bool:
    """Export fabric parameters to JSON file."""
    try:
        data = {
            'fabrics': FABRIC_PARAMETERS,
            'categories': FABRIC_CATEGORIES,
            'metadata': {
                'version': '1.0',
                'date': '2026-03-18',
                'total_fabrics': len(FABRIC_PARAMETERS),
                'total_categories': len(FABRIC_CATEGORIES),
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {str(e)}")
        return False

def import_from_json(input_path: str) -> Optional[Dict]:
    """Import fabric parameters from JSON file."""
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error importing from JSON: {str(e)}")
        return None

def print_fabric_report():
    """Print a summary report of all fabrics."""
    print("=" * 80)
    print("FASHION TECH — FABRIC PHYSICS PARAMETERS REPORT")
    print("=" * 80)
    print()
    
    for fabric_type, params in FABRIC_PARAMETERS.items():
        print(f"{params['display_name']} ({fabric_type})")
        print(f"  Category: {params['category']}")
        print(f"  Mass: {params['mass_density_g_per_m2']} g/m²")
        print(f"  Stiffness: {params['bending_stiffness']:.2f} | Elasticity: {params['elasticity']:.2f}")
        print(f"  Suitable for: {', '.join(params['suitable_for'][:3])}")
        print(f"  Notes: {params['design_notes']}")
        print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--export':
        output = sys.argv[2] if len(sys.argv) > 2 else 'fabric_parameters.json'
        if export_to_json(output):
            print(f"✓ Exported to {output}")
        else:
            print(f"✗ Export failed")
    elif len(sys.argv) > 1 and sys.argv[1] == '--report':
        print_fabric_report()
    else:
        print("Fashion Tech Fabric Parameters")
        print(f"Available fabrics: {', '.join(FABRIC_PARAMETERS.keys())}")
        print()
        print("Usage:")
        print("  python fabric_parameters.py --report          # Print summary report")
        print("  python fabric_parameters.py --export <path>   # Export to JSON")
