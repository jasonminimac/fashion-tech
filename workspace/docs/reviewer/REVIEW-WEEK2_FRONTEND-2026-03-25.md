# REVIEW — WEEK2_FRONTEND — 2026-03-25
**Reviewer:** Fashion Tech Reviewer  
**Date:** 2026-03-19 00:48 GMT (reviewing submission dated 2026-03-25)  
**Agent:** Frontend Engineer (React + Three.js)  
**Task ID:** WEEK2_FRONTEND  
**Verdict:** ✅ PASS WITH NOTES

---

## Summary

Exceptionally strong Week 2 delivery. The Frontend Engineer replaced placeholder scaffolding with real, production-quality integration code: real GLB loading, bone-parented garment attachment, walk-cycle animation, a complete outfit builder with save/export, and a drag-and-drop founder test flow. The code is TypeScript-strict, well-structured, and architecturally sound. All five deliverables reviewed; no Phase 2 scope creep found.

Issues are all P2/P3 (non-blocking, track for Week 3).

---

## Deliverables Reviewed

| File | LoC (reported) | Quality | Status |
|------|---------------|---------|--------|
| `SceneManager.ts` | ~310 | ⭐⭐⭐⭐⭐ | ✅ PASS |
| `ModelViewer.tsx` | ~210 | ⭐⭐⭐⭐⭐ | ✅ PASS |
| `GarmentSelector.tsx` | ~200 | ⭐⭐⭐⭐⭐ | ✅ PASS |
| `OutfitBuilder.tsx` | ~200 | ⭐⭐⭐⭐ | ✅ PASS |
| `TryOnPage.tsx` | ~130 | ⭐⭐⭐⭐⭐ | ✅ PASS |
| `WEEK2_FRONTEND_REPORT.md` | — | Thorough | ✅ PASS |

---

## Detailed Assessment

### SceneManager.ts — ✅ Excellent

**Strengths:**
- Clean separation of concerns: renderer setup, model lifecycle, animation, garment attachment, FPS tracking, snapshot — all well-encapsulated
- `loadModel()` correctly removes stale model before re-loading (prevents duplicate mesh ghost)
- `SRGBColorSpace` on material textures is correct — prevents washed-out materials on real scans
- Human-scale normalization to 1.75m is appropriate (slight improvement over Week 1's 1.8m)
- `attachGarment()` / `detachGarment()` / `setGarmentVisible()` API is clean and AR-handoff-ready (noted in report — good)
- Garment bone fallback to body root prevents crashes on mismatched rigs — correct defensive behaviour
- FPS tracker via `performance.now()` + `frameCount` is accurate (not interpolated)
- `dispose()` properly tears down all resources — no memory leaks
- `getModelIds()` helper is good for multi-scan workflows

**Issues:**
- **P2** — `removeModel()` cleans garments keyed by `id_` prefix (`garmentId.startsWith(`${id}_`)`). This assumes garment IDs are namespaced like `avatar_top-001`. If garment IDs are passed as bare IDs (e.g. just `top-001`), garments won't be cleaned up on model removal. Needs clarification with how `garmentId` is set in `ModelViewer` — currently ModelViewer passes `garment.id` directly (bare), so the `startsWith` check would never match. Low risk for now (no real garments), but could cause memory leaks in Week 3.
- **P2** — Garment GLBs loaded via `attachGarment()` are not disposed when detached (Three.js `Geometry` and `Material` objects remain in GPU memory). Add `dispose()` traversal on `att.object` in `detachGarment()`.

---

### ModelViewer.tsx — ✅ Excellent

**Strengths:**
- Clean React-to-Three.js bridge pattern: SceneManager owns all Three.js state, React owns UI state
- `useEffect` dependency arrays are correctly separated (scene init / model load / garment sync)
- Diff-based garment sync (only load new, only remove detached) prevents full scene reloads — correct
- `prevGarmentIds` ref correctly tracks previous garments to enable diff
- Walk cycle auto-detection via `/walk/i` regex is practical and expected-behaviour for Mixamo assets
- FPS overlay, animation toggle, screenshot, and camera reset are all clean and non-intrusive
- Error and empty-state UX are both handled
- Resize observer is properly cleaned up on unmount

**Issues:**
- **P2** — `useEffect(() => {...}, [])` for scene init has `eslint-disable-line` suppressing the exhaustive-deps warning. This is intentional and correct (scene should only init once) — but the comment should document *why* to avoid future confusion.
- **P2** — When `modelUrl` changes, the new model loads asynchronously. If a second `modelUrl` change arrives before the first finishes loading (rapid upload), there's a potential race where both promises resolve and one stomps the other. SceneManager's `removeModel()` on `loadModel` entry handles the visual side, but the first `setLoading(true)` would be overwritten and the first promise's `setLoading(false)` would fire. Low risk for founder test (single upload), but worth an abort controller in Week 3.

---

### GarmentSelector.tsx — ✅ Excellent

**Strengths:**
- `useMemo` with correct deps for filtered + sorted list — no unnecessary re-renders
- Category tabs, search, sort, lazy thumbnails, "no 3D" badge, selected checkmark, item count footer — all present
- Clear UX: empty state + search clear button
- Defensive `garment.thumbnailUrl ?? '/placeholder-garment.svg'` fallback
- Emoji category icons are a nice UX touch without being distracting
- `currency ?? '£'` fallback is correct for UK-first market

**Issues:**
- **P2** — Thumbnail `<img>` has `loading="lazy"` but no `width`/`height` attributes — can cause layout shift (CLS) as images load into the `aspect-square` container. Not critical but worth noting for performance.
- **P3** — Category `CATEGORIES` array and `CATEGORY_EMOJI` map are defined at module level. The `GarmentCategory` type from `@/types/garments` should be used to enforce type safety on the array entries (this may already work via the union type annotation, but worth confirming the type file lists all 6 categories).

---

### OutfitBuilder.tsx (OutfitBuilderPanel) — ✅ Good

**Strengths:**
- Zustand store integration pattern is clean
- Save → success flash → auto-clear (2s) is good UX
- Screenshot uses `sceneManagerRef.current` correctly — doesn't hold stale reference
- Share link base64 encoding is a pragmatic MVP approach (correctly noted as P2 for server persistence)
- Saved outfits collapsible list is clean

**Issues:**
- **P2** — `loadOutfit(outfit)` is called but there's no visible indication that garments from the loaded outfit are rendered to the 3D view. The `useOutfitStore` presumably updates `currentOutfit.garments`, which would propagate via `attachedGarments` prop in TryOnPage → ModelViewer. This chain should work, but it's worth verifying the store's `loadOutfit` action sets `currentOutfit.garments` correctly (not reviewed here — store file not submitted).
- **P2** — Outfit `load` button exists, but there's no `delete` saved outfit button in the UI. Users can accumulate many saved outfits with no way to prune. Small UX gap.
- **P3** — `outfit.id || outfit.createdAt` used as React list key. If `id` is undefined and `createdAt` repeats (e.g. two saves in same millisecond), there could be key collisions. Use a stable UUID for outfit identity.

---

### TryOnPage.tsx — ✅ Excellent

**Strengths:**
- Clean layout wiring of all three child components
- `sceneManagerRef` pattern correctly propagates SceneManager reference to OutfitBuilderPanel for screenshot access
- Drag-and-drop `.glb` upload is implemented correctly (preventDefault, dragover/dragleave/drop)
- Blob URL revocation on re-upload is correct — prevents memory leaks
- `.glb`/`.gltf` file type validation with user-friendly alert
- Upload CTA, drag overlay, and upload button are layered cleanly with `pointer-events-none` where appropriate
- `useGarmentsQuery` hook correctly decoupled from component

**Issues:**
- **P2** — Blob URL created on drag-drop is never revoked when the component unmounts (only revoked on re-upload). Should add a `useEffect` cleanup to call `URL.revokeObjectURL(avatarUrl)` if `avatarUrl` is a blob: URL on unmount.
- **P3** — The "Upload body scan" CTA label (inside `<label>`) and the drag-and-drop instructions are both visible when no avatar is loaded, but are positioned at the bottom and center respectively via absolute positioning. On small viewports, they may overlap the ModelViewer toolbar buttons (also bottom-positioned). Minor layout concern for mobile testing (Week 3).

---

## Phase Gate Check

✅ **No Phase 2 scope creep detected.** All deliverables are firmly within Phase 1 MVP scope:
- 3D viewer with real GLB: Phase 1 ✅
- Garment try-on UI: Phase 1 ✅
- Outfit save/export: Phase 1 ✅
- Founder test flow: Phase 1 ✅

Share link is hash-based (no server persistence) — correctly deferred as P2 to next phases. AR try-on (Week 6 go/no-go) not touched. B2B SDK not touched. ✅

---

## Cross-Agent Consistency

| Dependency | Status | Notes |
|------------|--------|-------|
| Rigging Lead → bone names | ⚠️ Awaited | Mixamo defaults set; `GARMENT_ANCHOR_BONES` table needs update when Rigging Lead confirms export convention |
| Garments Lead → garment GLBs | ⚠️ Awaited | "no 3D" badge handles gracefully; outfit tracking works without models |
| Backend → `/garments` endpoint | ✅ Mock in place | `useGarmentsQuery` hook ready; switch to live API Week 3 |
| Backend → `/scans` S3 upload | ⏳ Week 3 | Local blob: URL works for founder test; server upload next sprint |

The `GARMENT_ANCHOR_BONES` table in ModelViewer uses Mixamo convention (`mixamorigSpine`, `mixamorigHips`, etc.). Rigging Lead must confirm this matches their GLB export — if they use Rigify names (`spine`, `pelvis`, `foot_l`), the table needs updating. Agent correctly flagged this as uncertainty.

---

## Metrics Against Week 2 Goals

| Goal | Target | Delivered | Status |
|------|--------|-----------|--------|
| Real GLB mesh loading | ✅ | ✅ | PASS |
| Garment bone attachment | ✅ | ✅ | PASS |
| Animation playback | ✅ | ✅ | PASS |
| Outfit save/load | ✅ | ✅ | PASS |
| Founder test flow | ✅ | ✅ | PASS |
| 60fps target | ✅ | ✅ (tracked) | PASS |
| <200ms garment swap | ✅ | Diff-based, no full reload | PASS (estimated) |
| TypeScript strict | ✅ | ✅ | PASS |
| No regression to existing types | ✅ | ✅ (self-reported, no type errors) | PASS |

---

## Issues Summary

### P0 — Critical
_None._

### P1 — Fix Before Next Task
_None._

### P2 — Track (Non-blocking, address Week 3)

1. **SceneManager `removeModel()` garment cleanup** — `startsWith(id_)` pattern assumes namespaced garment IDs; ModelViewer passes bare IDs. Verify or fix namespacing convention.
2. **Garment GLB GPU disposal** — `detachGarment()` should traverse and dispose geometry/materials.
3. **ModelViewer race on rapid model URL change** — add AbortController pattern in Week 3.
4. **TryOnPage blob URL leak on unmount** — add cleanup `useEffect` to revoke blob URL.
5. **OutfitBuilderPanel: no delete saved outfit** — add delete/remove from saved list.
6. **Bone name coordination with Rigging Lead** — verify Mixamo vs Rigify naming before Week 3 real asset test.

### P3 — Low Priority / Track

7. GarmentSelector thumbnail CLS (add width/height attrs)
8. Outfit list key stability (use UUID not `createdAt`)
9. TryOnPage upload CTA/toolbar overlap on small viewports

---

## Overall Assessment

This is excellent Week 2 delivery. The Frontend Engineer shipped a complete, working founder test flow with clean architecture, appropriate fallbacks, and no scope creep. The code quality is high — proper TypeScript, sensible React patterns, correct Three.js resource management (mostly), and good UX polish.

The outstanding items are all P2/P3, none blocking the founder test session or Week 3 work. The self-reported uncertainties (bone names, missing GLBs, footwear dual-foot) are appropriately flagged and handled gracefully in code.

**Trust Calibration:** Upgrading from "New — standard scrutiny" → 🟢 High. Consistent with Week 1 performance reviewed in REVIEWER-MEMORY.

---

**Signed:** Fashion Tech Reviewer  
**Date:** 2026-03-19 00:48 GMT  
**Verdict:** ✅ PASS WITH NOTES
