# REVIEW — WEEK2_RIGGING
**Reviewer:** Fashion Tech Reviewer  
**Submission:** INBOX-WEEK2_RIGGING.md  
**Agent:** Blender Integration Lead (Rigging Engineer)  
**Date:** 2026-03-19 (reviewing Week 2 work dated 2026-03-25)  
**Verdict:** ✅ PASS WITH NOTES

---

## Overall Assessment

Strong Week 2 delivery. The agent correctly handled two significant external blockers — the MediaPipe 0.10+ API breakage and the absence of real iPhone scans — without blocking or spinning. Three GLB files produced, walk cycle baked in, handoff documentation clear. The pipeline proves the concept end-to-end; real scans and ML joint detection slot in cleanly in Week 3. Transparency about limitations is excellent.

**Phase 1 scope:** Clean. No Phase 2 creep detected.

---

## Deliverable Checklist

| File | Expected | Present | Quality |
|------|----------|---------|---------|
| WEEK2_RIGGING_REPORT.md | ✅ | ✅ | High — thorough, honest |
| RIGGING_METRICS.json | ✅ | ✅ | Complete, machine-readable |
| JOINT_VALIDATION_LOG.md | ✅ | ✅ | Accurate (heuristic limitations noted) |
| scan_001_average.glb | ✅ | ✅ (81.9 KB) | Within SLA |
| scan_002_tall.glb | ✅ | ✅ (80.9 KB) | Within SLA |
| scan_003_broad.glb | ✅ | ✅ (81.3 KB) | Within SLA |
| joint_detector.py | ✅ | ✅ | Production-quality with clean fallback |
| auto_rig.py | ✅ | ✅ | Solid; two code bugs noted |
| run_week2_pipeline.py | ✅ | ✅ | Well-orchestrated |
| generate_synthetic_scans.py | ✅ | ✅ | — |

---

## Performance vs SLA

| Scan | Rig Time | SLA (500ms) | File Size | SLA (<30MB) |
|------|----------|-------------|-----------|-------------|
| scan_001_average | 158.7ms | ✅ | 81.9 KB | ✅ |
| scan_002_tall | 110.9ms | ✅ | 80.9 KB | ✅ |
| scan_003_broad | 110.0ms | ✅ | 81.3 KB | ✅ |

All well within SLA. Note: rig time excludes Blender startup (~2s); this is correctly documented and acceptable — startup time is infrastructure overhead, not pipeline overhead.

---

## Issues Found

### 🟡 P2 — Code Bug: SLA check uses wrong threshold in `auto_rig.py`

**Location:** `auto_rig.py`, line near metrics dict:
```python
"sla_pass": total_ms < 500000,  # <500s total (including mesh creation)
```

The SLA target is **500ms**, not 500,000ms (500 seconds). The comment even says `<500s` which is wrong. This bug doesn't affect the GLB output or the `rig_time_ms` metric (correct), but it means `sla_pass` will be `True` for any run under 8 minutes, hiding future regressions.

**Fix required (Week 3):** Change to `total_ms < 500` and update comment accordingly. Also consider separating Blender startup time from pipeline time — startup overhead should be measured separately.

---

### 🟡 P2 — Code Bug: Cyclic animation loop iterates FCurves as NLA strips

**Location:** `auto_rig.py`, walk cycle section:
```python
for action in bpy.data.actions:
    if action.is_action_legacy:
        for strip in getattr(action, 'fcurves', []):
            mod = strip.modifiers.new(type='CYCLES')  # strip is an FCurve, not a strip
    action.use_cyclic = True
```

`action.fcurves` returns `FCurve` objects, not NLA strips. The inner loop calls `.modifiers.new(type='CYCLES')` on an FCurve object, which is correct per-curve usage but the variable name `strip` is misleading and the logic is mixed up with the NLA strip API. In practice `action.use_cyclic = True` (Blender 5 path) handles the cyclic flag correctly, so the animation likely loops correctly. But the legacy code path may silently error.

**Fix required (Week 3):** Clean up the cyclic block:
```python
for action in bpy.data.actions:
    action.use_cyclic = True
    # For Blender <5 compatibility, also add CYCLES modifier per fcurve:
    for fcurve in action.fcurves:
        if not any(m.type == 'CYCLES' for m in fcurve.modifiers):
            fcurve.modifiers.new(type='CYCLES')
```

---

### 🟠 P1 — Cross-Agent: Bone naming convention unresolved with Frontend Lead

**Context:** The REVIEWER-MEMORY from the Week 2 Frontend review flagged "Bone name coordination with Rigging Lead (Mixamo vs Rigify)" as a P2 item. Now that real GLBs exist, this becomes **P1** — the Frontend Lead cannot implement garment bone-parenting without knowing the exact bone names in these files.

**Bone names in these GLBs:**
`root, spine, chest, neck, head, upper_arm_L, lower_arm_L, hand_L, upper_arm_R, lower_arm_R, hand_R, thigh_L, shin_L, foot_L, thigh_R, shin_R, foot_R`

These are **not Mixamo names** (Mixamo uses `mixamorig:Hips`, `mixamorig:LeftUpLeg`, etc.) and **not Rigify names** (`DEF-spine`, `DEF-upper_arm.L`, etc.). They're a custom naming convention.

**Action required before Week 3:** Rigging Lead must communicate bone name list to Frontend Lead. Frontend Lead needs to update garment attachment logic to use these names (or Rigging Lead should adopt a standard naming convention). Recommend Mixamo convention for maximum Three.js/ecosystem compatibility.

---

### 🟡 P2 — Heuristic confidence scores are uniform (all 0.30)

**Observation:** All 16 joints across all 3 scans report identical confidence (visibility=0.50, depth=0.60, combined=0.30). This is because the heuristic fallback assigns fixed constants to every joint. While correct, it makes the validation log useless for identifying *which* joints are less reliable (e.g., wrists/ankles are typically harder to place than hips/shoulders in heuristic mode).

**Not a blocker** — the heuristic is acknowledged as Week 2-only. But when MediaPipe Tasks API is integrated in Week 3, the confidence scores should show real per-joint variance. Track for Week 3 validation.

---

### 🟡 P2 — Walk cycle rotation axis may need per-bone review

**Observation:** All walk cycle rotations use `rotation_euler[0]` (X axis). This is correct for forward/backward leg swing in Blender's default bone orientation. However, for shoulder counter-swing, the upper arm bones in this rig may require Y-axis rotation depending on how they're oriented in edit mode. If the arms appear to swing forward/back (correct) vs. up/down (wrong), this is a bone orientation issue.

**Not blocking** — the 300-vert capsule proxy is explicitly temporary. Flagging for visual verification when higher-fidelity mesh arrives in Week 3.

---

### ℹ️ P3 — Blender startup time excluded from SLA but not measured

The report correctly notes that Blender startup (~2s) is excluded from the 158ms/110ms/110ms timings. For production viability, the *total wall time* matters. `run_week2_pipeline.py` does capture `wall_time_ms` but this includes process spawn overhead, not just startup.

**Recommendation:** Add a `blender_startup_ms` measurement to the pipeline output so the full picture is visible (rig: 158ms + startup: ~2000ms = ~2.2s total). Still well within any reasonable production SLA, but good to make explicit.

---

## Contextual Assessment of Blockers

Both major blockers were handled correctly:

**1. MediaPipe 0.10.33 — solutions.pose removed**  
The graceful fallback to heuristic joint placement is well-implemented. The fallback produces anatomically reasonable joint positions scaled to body proportions. The code structure cleanly separates the ML path from the heuristic path and will accept the Tasks API in Week 3 with minimal refactoring. ✅

**2. No real iPhone scans from Scanning Lead**  
Using synthetic scans at 50,600 pts with 3mm Gaussian noise (matching ARKit spec) is the right call. The pipeline is spec-to-spec identical for real scans — the swap is trivially a directory change. Correctly documented and flagged. ✅

---

## Code Quality

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Architecture | High | Clean module separation, clear data flow |
| Error handling | Good | Graceful fallback, subprocess error capture |
| Documentation | High | Inline comments, clear purpose per function |
| Naming | Good | Clear; bone names could follow standard convention (P1 above) |
| Test coverage | None | No unit tests this week — acceptable for integration week |
| SLA compliance | Pass | Two minor code bugs (P2) don't affect correctness |

**Missing:** No tests for `joint_detector.py` or `auto_rig.py`. Week 1 had 22 tests. For Week 3, restore test coverage — especially for the MediaPipe Tasks API integration and the coordinate transform `j2b()` function.

---

## Cross-Agent Consistency Check

| Dependency | Status |
|-----------|--------|
| GLB format matches Frontend expectations (GLTF 2.0, Y-up, meters) | ✅ |
| Animation clip accessible via Three.js AnimationMixer | ✅ (documented) |
| GLB file size suitable for web delivery (~82KB each) | ✅ |
| Bone names communicated to Frontend Lead | ❌ P1 unresolved |
| Poisson mesh from Scanning Lead for Week 3 | ⏳ Pending |
| USDZ export path for AR Lead | ⏳ Week 3 (noted) |

---

## Week 3 Readiness

The agent's Week 3 prep list is accurate and appropriately scoped:
1. MediaPipe Tasks API + `pose_landmarker_heavy.task` model — ✅ correctly identified
2. Real scan testing from Scanning Lead — ✅ pipeline is swap-ready
3. Higher-fidelity Poisson mesh (50k-200k verts) — ✅ noted; re-benchmark SLA required
4. USDZ export for AR Lead — ✅ noted

**Additional Week 3 requirement (from this review):** Fix SLA threshold bug and cyclic animation bug before production mesh testing.

---

## Summary of Issues

| ID | Level | Description | Action |
|----|-------|-------------|--------|
| R-01 | P1 | Bone naming convention not communicated to Frontend Lead | Rigging Lead → provide bone list to Frontend Lead before Week 3 garment attachment work |
| R-02 | P2 | `sla_pass` threshold is 500,000ms not 500ms | Fix in auto_rig.py Week 3 |
| R-03 | P2 | Cyclic animation loop variable naming confused NLA strip vs FCurve | Clean up in auto_rig.py Week 3 |
| R-04 | P2 | Heuristic confidence scores uniform — no per-joint variance | Accept for Week 2; real variance expected with MediaPipe in Week 3 |
| R-05 | P2 | Walk cycle rotation axis per-bone needs visual verification | Verify on higher-fidelity mesh Week 3 |
| R-06 | P3 | Blender startup time not measured separately | Add to pipeline metrics Week 3 |
| R-07 | P3 | Test coverage dropped to zero this week | Restore in Week 3 (especially j2b() and MediaPipe integration) |

**No P0 issues.** No Phase 2 scope creep. No founder constraint violations.

---

## Verdict

**✅ PASS WITH NOTES**

The Week 2 rigging pipeline is production-quality for its stated scope. All deliverables present, all SLAs met, blockers handled professionally. The two code bugs are minor and don't affect output correctness. The only P1 action item (bone naming) is a cross-agent coordination task, not a quality defect in the submission itself.

No resubmission required. Carry all P2 items into Week 3 sprint planning.

---

**Signed:** Fashion Tech Reviewer  
**Date:** 2026-03-19  
**Next review trigger:** Week 3 Rigging submission (real scans + MediaPipe Tasks API)
