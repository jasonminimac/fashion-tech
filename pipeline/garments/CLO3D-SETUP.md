# CLO3D Setup Guide — Sprint 1 T-Shirt Simulation
**Document:** CLO3D-SETUP.md
**Author:** fashion-garments (Garment Systems Engineer)
**Date:** 2026-03-18
**Status:** ⚠️ BLOCKER — CLO3D licence not confirmed. Blender fallback in use.

---

## ⚠️ Licence Blocker

CLO3D requires a paid licence (CLO Subscription or CLO for Enterprise).
**This simulation has NOT been run in CLO3D.** A Blender cloth simulation fallback (`blender_cloth_sim.py`) has been produced as a placeholder. Re-run in CLO3D once the licence is confirmed.

**Action required from CEO:** Confirm CLO3D licence acquisition and provide seat access to the garments agent before Sprint 2.

---

## Project Overview

| Field | Value |
|-------|-------|
| Garment type | T-shirt (crew neck, short sleeve) |
| Target fabric | 150 g/m² jersey cotton |
| Avatar | CLO3D default female/male A-pose avatar |
| Output format | Baked `.obj` sequence (30 frames, A-pose → walk cycle) |

---

## CLO3D Project Settings

### 1. New Project Setup

1. **File → New**
2. Load Avatar: `File → Load Avatar` → select standard A-pose avatar
   - Recommended: CLO3D default "Female_A-pose" or "Male_A-pose" (170cm)
3. Import T-shirt pattern: `File → Import → DXF/PDF pattern` or build directly in 2D Pattern view

### 2. T-Shirt Pattern Construction (if building from scratch)

In the 2D Pattern window:

- **Front panel:** width 52cm, length 68cm (size M)
- **Back panel:** same dimensions
- **Sleeve (×2):** width 22cm, length 22cm, tapered
- **Neckband:** width 4cm, circumference ~42cm

Arrange panels around the avatar in 3D view before simulating.

### 3. Fabric Properties — 150 g/m² Cotton Jersey

Navigate to: **Fabric Editor** (right panel)

| Property | Value | Notes |
|----------|-------|-------|
| Weight (g/m²) | 150 | Jersey cotton target |
| Thickness (mm) | 0.65 | Typical for 150gsm jersey |
| Stretch (Weft %) | 30 | Jersey horizontal stretch |
| Stretch (Warp %) | 20 | Slight vertical stretch |
| Shear | 45 | Mid-range shear stiffness |
| Bending (Weft) | 20 | Soft drape for cotton |
| Bending (Warp) | 20 | |
| Density (g/m²) | 150 | Match fabric weight |
| Friction | 0.35 | Cotton-on-skin typical |
| Collidable Thickness | 1.0mm | Prevent clipping |
| Self-Collision | Enabled | Critical for tuck/fold regions |

**Preset starting point:** CLO3D built-in `Cotton Jersey` preset → then dial in the values above.

### 4. Simulation Parameters

**Simulation Properties panel:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Simulation Quality | 5 | Medium-high quality |
| Particle Distance | 5mm | Fine enough for realistic drape |
| Gravity | -9.8 m/s² | Standard |
| Solver Frequency | 300 | Higher = more stable |
| Self-Collision | On | |
| Layer Order | T-shirt = Layer 1 (outermost) | |

**Running the initial drape (A-pose):**
1. Press **Simulate** (spacebar or toolbar)
2. Allow simulation to fully settle (~10–30 seconds)
3. Visually confirm: no clipping through avatar, even hem drape, collar sits naturally

### 5. Walk Cycle Animation Setup

1. Open **Animation** panel: `Window → Animation`
2. Import walk cycle BVH:
   - Use CLO3D built-in walk animation, or
   - `Import → Motion (BVH)` → use the walk cycle BVH from `assets/animations/`
3. Set timeline: 30 frames at 24fps (~1.25 seconds, half walk cycle loop)
4. Press **Record** and run simulation through animation frames

**Frame range:** 1–30
**FPS:** 24
**Total duration:** 1.25s (half walk cycle, sufficient for a loop)

### 6. Export Settings — Baked `.obj` Sequence

1. `File → Export → OBJ (Sequence)`
2. Settings:
   - **Export format:** OBJ
   - **Scale:** 1:1 (centimetres)
   - **Include:** Unified UV, texture coordinates
   - **Merge:** All fabrics into single mesh per frame (for simplicity in Sprint 1)
   - **Weld vertices:** On
   - **Frame range:** 1–30
3. Output directory: `assets/garments/tshirt-sprint1/`
4. Filename pattern: `tshirt_frame_%03d.obj`

### 7. Quality Checks Before Export

- [ ] No visible clipping through avatar at any frame
- [ ] Hem and collar maintain consistent position
- [ ] No exploding geometry (vertices shooting to infinity)
- [ ] Fabric folds look physically plausible (not too stiff, not too floppy)
- [ ] Frame 001 (A-pose) = clean resting drape
- [ ] Frame 030 = clean end frame (no simulation instability)

---

## Files to Hand Off to AR Engineer

Once CLO3D is run, the AR engineer needs:

| File | Location | Notes |
|------|----------|-------|
| `tshirt_frame_001.obj` → `tshirt_frame_030.obj` | `assets/garments/tshirt-sprint1/` | Full baked sequence |
| `garment_metadata_example.json` | `pipeline/garments/` | Schema + metadata record |
| Texture maps (if any) | `assets/textures/` | Albedo, normal (Phase 2) |

---

## Blender Fallback

Until the CLO3D licence is confirmed, use `blender_cloth_sim.py` (same directory) to generate a stand-in `.obj` sequence. The Blender simulation is lower fidelity but structurally correct for pipeline testing.

---

## Contacts

- **CLO3D licence enquiries:** https://www.clo3d.com/pricing
- **CLO3D docs:** https://support.clo3d.com/
