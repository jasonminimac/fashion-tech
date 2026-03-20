# Agent Profile — Blender Integration Lead
**Floor:** Fashion Tech | **Created:** 2026-03-18 | **Updated:** 2026-03-19

## Mandate
Automated rigging pipeline: MediaPipe pose detection → Rigify armature → glTF/FBX export. Best tool wins — not Blender-only.

## Expected Outputs
Python rigging scripts, MediaPipe integration, Rigify setup, glTF export pipeline, test suite.

## Known Constraints
- Receives FBX/PLY from 3D Scanning Lead (Week 4 handoff; Week 3 will have real scans)
- Outputs glTF to Frontend Lead
- Target: <1.5s end-to-end rigging, 90% auto weight coverage
- Best tool wins — can use MetaHuman or CLO3D if better

## Review History

### Week 2 — ✅ PASS WITH NOTES
**File:** REVIEW-WEEK2_RIGGING-2026-03-25.md  
**Date:** 2026-03-19  
**Verdict:** PASS WITH NOTES

**Summary:**
- Full pipeline operational: .ply → joint detection → armature → walk cycle → .glb export
- 3 GLBs produced (scan_001_average, scan_002_tall, scan_003_broad), all within SLA (<160ms, <82KB)
- Two blockers handled professionally: MediaPipe API removed (heuristic fallback), no real iPhone scans (synthetic substitute)
- Blender 5.0 API changes fixed

**Issues raised:**
- P1: Bone naming convention (custom: root/spine/chest/neck/head/upper_arm_L etc.) NOT communicated to Frontend Lead — must resolve before Week 3
- P2: `sla_pass` threshold bug in auto_rig.py (500,000ms instead of 500ms)
- P2: Cyclic animation block has confused variable naming (NLA strip vs FCurve)
- P2: Uniform heuristic confidence scores (0.30 for all joints) — expected; real variance in Week 3
- P2: Walk cycle rotation axis needs visual verification on production mesh
- P3: Blender startup not measured separately from rig time
- P3: Test coverage dropped to zero this week — restore in Week 3

---

*(Week 1 work predates Reviewer initialization)*

## Patterns Noticed
- Handles external blockers cleanly: documents fallback, delivers substitute, leaves clean swap-in path
- Transparent documentation — flags limitations proactively without being asked
- Strong code architecture: clean module separation, graceful degradation
- Needs nudging on cross-agent coordination (bone naming → Frontend)
- Test coverage can slip under pressure — watch for this in Week 3

## Trust Calibration
🟢 High — transparent, technically sound, realistic scope management, honest about limitations
