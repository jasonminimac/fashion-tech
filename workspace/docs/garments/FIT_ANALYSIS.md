# Fit Analysis — Garment-Body Integration

**Project:** Fashion Tech MVP  
**Garment:** GARMENT-001 Basic T-Shirt (v1.0)  
**Body Input:** Rigged .glb from Rigging Lead (Week 2)  
**Analyst:** Clothing & Physics Lead  
**Date:** 2026-03-25  
**Status:** Initial analysis — pending rigged .glb delivery

---

## Summary

| Category | Finding | Severity |
|----------|---------|----------|
| Rigged .glb received | ⏳ Pending from Rigging Lead | Blocker (P1 if not received by Day 3) |
| Chest/shoulder alignment | Spec-based: should fit size-M (chest 96cm) | TBD — needs runtime test |
| Hem clipping risk | LOW — parametric model has +2mm offset from body surface | Expected OK |
| Seam alignment | Front/back panels share edge loops — seams should align | TBD |
| Sleeve attachment | Simplified tube — may need refinement at armscye | Minor |
| Neck opening | 80mm radius — needs validation against scan data | TBD |

---

## Garment Spec vs Body Spec

### T-Shirt (GARMENT-001)

| Parameter | Garment Value | Body Target (M) | Match? |
|-----------|---------------|-----------------|--------|
| Chest circumference | 96 cm | 96 cm | ✅ |
| Garment length | 70 cm | torso ~60 cm | ✅ (2cm below waist) |
| Shoulder width | 44 cm | 44 cm | ✅ |
| Sleeve length | 22 cm | upper arm ~32 cm | ✅ (short sleeve) |
| Neck radius | ~10 cm circumference | neck ~38 cm | ⚠️ Check fit |

---

## Cloth Simulation Parameters Applied

| Parameter | Value | Notes |
|-----------|-------|-------|
| Fabric weight | 150 g/m² | Standard jersey cotton |
| Bending stiffness | 0.15 | Soft drape |
| Stretch stiffness | 0.85 | Low stretch (woven) |
| Shear stiffness | 0.30 | Moderate |
| Damping | 0.02 | Light — realistic motion |
| Surface offset | +2 mm (front), -2 mm (back) | Anti-clipping offset |
| Gravity sag | Progressive over 30 frames | Hem sags 5mm max |

---

## Known Fit Issues (Pre-Integration)

### Issue 001 — Sleeve Armscye Junction
- **Description:** Sleeve tube uses simplified 8-vertex cross-section; armhole may show visible seam discontinuity
- **Severity:** P2 — cosmetic, acceptable for Phase 1 proof-of-concept
- **Resolution:** Refine armscye topology in Week 3 for partner demo quality

### Issue 002 — Neck Opening
- **Description:** Neck radius hard-coded at 100mm; actual scan neck circumference varies ±10mm by user
- **Severity:** P2 — affects visual fit for extreme body sizes
- **Resolution:** Parameterize neck radius from body scan data in platform integration (Week 3)

### Issue 003 — Rigged .glb Not Yet Received
- **Description:** Rigging Lead has not delivered the Week 2 rigged .glb as of 2026-03-25
- **Severity:** P1 — blocks live garment-on-body visual validation
- **Resolution:** Garment mesh is ready; will attach immediately upon .glb receipt. Using parametric body target (average_male_M) for initial fit testing.

---

## Integration Workflow (pending .glb receipt)

```
1. Receive rigged .glb from Rigging Lead
2. Import .glb skeleton into Blender
3. Load tshirt_basic_v1_frame001.obj as starting mesh
4. Bind garment to skeleton via surface deform / vertex weight
5. Run cloth sim (30-frame sequence already generated)
6. Check clipping at: chest, shoulders, underarms, hem
7. Export combined .glb (body + garment) for platform team
8. Screenshot 3 poses: T-pose, walking frame 15, arms-up
```

---

## Visual Reference

**Pending:** Screenshots/animation will be added once rigged .glb received.  
Placeholder: Cloth sim frame data at `WEEK2_ASSETS/tshirt_basic_v1_frame*.obj`  
Preview: 30-frame sequence shows gravity drape progression over first 1.25 seconds.

---

## Next Steps

| Action | Owner | Due |
|--------|-------|-----|
| Receive rigged .glb | Rigging Lead → Garment Lead | Day 3 (Mar 27) |
| Run live garment-body fit in Blender | Clothing & Physics Lead | Day 4 (Mar 28) |
| Screenshot 3 canonical poses | Clothing & Physics Lead | Day 4 (Mar 28) |
| Fix armscye seam (if time allows) | Clothing & Physics Lead | Day 5 (Mar 29) |
| Document final fit metrics | Clothing & Physics Lead | Day 5 (Mar 29) |

---

## Handoff to Platform Team

Once fit is validated, platform team will need:
- `tshirt_basic_v1_metadata.json` — all garment metadata + fabric physics params
- `tshirt_basic_v1_frame*.obj` (30 frames) — or baked single .glb
- Fit offset values (surface delta per body zone)
- Database row insert: see `database_schema.sql` from Week 1

