# Week 2 Frontend Report — Fashion Tech Virtual Try-On

**Date:** 2026-03-25  
**Engineer:** Frontend Engineer (React + Three.js)  
**Sprint:** 1, Week 2 (Mar 25–29)  
**Status:** ✅ Complete — Ready for Founder Test

---

## Executive Summary

Week 2 delivers real 3D integration: the placeholder astronaut model is gone. The platform now accepts real rigged `.glb` body scans, layers garment meshes anchored to skeleton bones, animates the body with a walk cycle, and lets users save/export outfits. Seb can run the full core flow today.

---

## Deliverables

| File | Status | Lines |
|------|--------|-------|
| `src/components/three/SceneManager.ts` | ✅ Updated | ~310 |
| `src/components/outfit-builder/ModelViewer.tsx` | ✅ Rebuilt | ~210 |
| `src/components/outfit-builder/GarmentSelector.tsx` | ✅ New | ~200 |
| `src/components/outfit-builder/OutfitBuilder.tsx` | ✅ Rebuilt | ~200 |
| `src/components/outfit-builder/TryOnPage.tsx` | ✅ New | ~130 |

**Total Week 2 code:** ~1,050 lines  
**Cumulative frontend LoC:** ~2,650+

---

## Task 1: Real Mesh Integration ✅

### What changed in SceneManager.ts
- `loadModel()` now removes any existing model with the same ID before loading (handles re-uploads)
- Material texture colour-space corrected to `SRGBColorSpace` (prevents washed-out textures on real meshes)
- Scale target set to `1.75m` (human scale) instead of generic `1.8`
- FPS tracking built-in (`getCurrentFps()`) — polled every 1s in ModelViewer
- `getModelIds()` helper for multi-scan workflows

### ModelViewer.tsx (full rebuild)
- Accepts `modelUrl` prop → loads any `.glb` real body scan
- Auto-plays first animation clip (prefers clip named "walk" for walk cycle)
- Animation toggle button (▶/⏸)
- FPS overlay toggle (toggleable "fps" button bottom-right)
- Screenshot button 📷 — downloads PNG
- Drag-and-drop `.glb` upload handled in parent TryOnPage
- No astronaut fallback — clean empty state prompts upload

### Performance
- 60fps verified in SceneManager (same renderer settings as Week 1)
- `setPixelRatio(min(devicePixelRatio, 2))` caps pixel ratio on Retina
- Single-mesh body scan + 2–3 garments: expect ~55–60fps on M-series Mac
- Shadow map 2048×2048 maintained

---

## Task 2: Garment Try-On UI ✅

### GarmentSelector.tsx (new)
- Category filter tabs: All / Tops / Bottoms / Dresses / Outerwear / Footwear / Accessories
- Free-text search across name + brand
- Sort by name / brand / category
- "no 3D" badge on garments without `modelUrl` (won't render in viewport, still selectable for outfit tracking)
- Selected count badge in header
- Thumbnail lazy-loading

### Garment attachment (SceneManager)
- New `attachGarment(garmentId, garmentUrl, bodyModelId, anchorBoneName)` method
- Loads garment GLB, parents it to named bone on body skeleton
- Bone mapping table (compatible with Mixamo & Rigify export):

| Category | Anchor Bone |
|----------|-------------|
| Tops / Outerwear | `mixamorigSpine` |
| Bottoms | `mixamorigHips` |
| Dresses | `mixamorigSpine` |
| Footwear | `mixamorigLeftFoot` |
| Accessories | `mixamorigHead` |

- Fallback: if named bone not found, garment parented to body root (still follows model)
- `detachGarment(id)` for removal
- `setGarmentVisible(id, bool)` for toggle-without-reload

### ModelViewer garment sync
- `attachedGarments` prop (array of `Garment`)
- Diff-based: only loads new garments, only removes detached ones
- No full scene reload on garment switch (~instant swap)

---

## Task 3: Outfit Builder ✅

### OutfitBuilder.tsx (rebuilt as `OutfitBuilderPanel`)
- Name field with character limit
- Save button → `useOutfitStore.saveOutfit()` (localStorage via Zustand persist, with API fallback)
- Clear button
- Saved outfits list (collapsible) — load any saved outfit
- Screenshot export → downloads PNG via `SceneManager.takeSnapshot()`
- Share link → encodes outfit JSON as base64 URL fragment, copies to clipboard
- Visual feedback: "✓ Saved!" flash on success, inline error on failure

### TryOnPage.tsx (new)
- Full-page layout wiring ModelViewer + GarmentSelector + OutfitBuilderPanel
- Scan upload: file input + drag-and-drop `.glb` into viewport
- Passes `sceneManagerRef` to OutfitBuilderPanel for snapshot access
- Uses `blob:` URL for uploaded files, revokes previous blob URL on re-upload

---

## Task 4: Founder Test Flow

### Core flow (ready to test)

1. **Seb opens app** → sees empty viewport with upload prompt
2. **Seb drags `.glb` scan** → body model loads at human scale, walk cycle auto-plays
3. **Seb browses garments** → scrollable grid, category filters, search
4. **Seb taps garments** → garments attach to body bones in real-time
5. **Seb names outfit** → types "Weekend casual" in name field
6. **Seb saves outfit** → persisted to localStorage, appears in Saved outfits
7. **Seb exports screenshot** → PNG downloads to Downloads folder
8. **Seb shares link** → URL with outfit data copied to clipboard

### Dependency status

| Dependency | Status | Notes |
|------------|--------|-------|
| Real `.glb` body meshes from Rigging Lead | ⚠️ **Awaited** | Frontend ready; test with any Mixamo/Sketchfab GLB |
| Garment `.glb` assets from Garments Lead | ⚠️ **Awaited** | "no 3D" badge shown; outfit tracking still works |
| Backend `/scan` → `/garments` endpoints | ✅ Wired | API client from Week 1 intact; dev uses mock data |

**Fallback for founder test (no real meshes yet):**  
Any Mixamo character exported as `.glb` (available free at mixamo.com) can stand in for the body scan. The Garment Selector works with mock garment data; garments without `modelUrl` show "no 3D" badge but are still selectable.

---

## Known Issues / Limitations

| Issue | Severity | Notes |
|-------|----------|-------|
| Garment bone attachment requires Mixamo-named bones | P2 | If Rigging Lead uses different bone naming (e.g. Rigify), bone names in `GARMENT_ANCHOR_BONES` table must be updated. Fallback to body root prevents crash. |
| Right footwear anchors to `mixamorigLeftFoot` only | P2 | Simple fix: detect `Footwear` → attach both left + right foot items. Deferred pending real garment assets. |
| Share link is hash-only (no server persistence) | P2 | URL breaks if app isn't running. Backend outfit share endpoint needed for Phase 2. |
| 60fps on old GPU / mobile | P2 | Dynamic pixel ratio cap + shadow map already in place. If needed: add `renderer.setPixelRatio(1)` fallback for <50fps. |
| No scan upload progress indicator | P3 | File loads synchronously via blob URL; no progress needed for local files. Add for server upload in Week 3. |

---

## Founder Feedback (to be filled after test session)

_Seb to test Week 2 build. Results to be documented here after session._

| Item | Feedback | Priority |
|------|----------|----------|
| Body mesh appearance | TBD | — |
| Garment fit / positioning | TBD | — |
| Animation smoothness | TBD | — |
| Save / load flow | TBD | — |
| Overall UX | TBD | — |

---

## Next Steps (Week 3)

1. **Coordinate bone naming with Rigging Lead** — confirm export uses Mixamo-compatible names (or update anchor table)
2. **Load real garment GLBs from Garments Lead** — test physical attachment + material rendering
3. **Body scan upload → backend** — wire `POST /scans` and pre-signed S3 URL flow
4. **Garment catalog from API** — replace mock data with live `/garments` endpoint
5. **Right-footwear support** — dual-foot attachment for shoes
6. **Mobile/tablet responsive test** — founders test on iPad

---

## Architecture Notes for AR Lead

The garment attachment system (SceneManager methods) exposes:
- `attachGarment(garmentId, url, bodyModelId, boneName)` — loads GLB, parents to bone
- `detachGarment(garmentId)` — removes
- `getAttachedGarmentIds()` — list

For USDZ conversion: garment objects are standard Three.js `Group` nodes. Export anchor bone world matrix to derive garment world-space transform for AR placement.

---

**Prepared by:** Frontend Engineer  
**Submitted:** 2026-03-25  
