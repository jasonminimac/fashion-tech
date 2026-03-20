# FOUNDER DECISION MEMO — Fashion Tech

**Date:** 2026-03-17  
**From:** Seb (Founder)  
**To:** Fashion Tech CEO  
**Re:** Answers to Open Questions — Greenlight to Proceed

---

## Decisions

**1. Revenue model:** Both B2C and B2B.

**2. Market:** Global, starting with US and UK first.

**3. Brand partnerships:** Target Zara, H&M and major consumer retail chains as first partners for the garment catalogue.

**4. Timeline & budget:** 6-month target. No budget — building solo. Lean approach.

**5. Scanning approach:** Support both LiDAR and photogrammetry for now. At MVP we choose whichever produces the most realistic output. Realism is the priority — use Blender, Unreal Engine, AI enhancement, whatever it takes to make the result look real. Don't constrain to one tool.

**6. Target user:** Fashion-forward early adopters first, to generate buzz. Then broader market.

**7. Garment variety:** Mixed categories from the start.

**8. Blender requirement:** NOT a hard requirement. Use the best tools for the job. Blender is well-known but if Unreal Engine, CLO3D, or another solution produces better output, use that. Goal is realism and quality.

**9. Real-time AR try-on:** In MVP scope.

**10. Data ownership:** Platform owns body scan data. Retailers connect via API — users can access their data from any retailer touchpoint through the platform.

---

## What This Means for Your Roadmap

- **Realism over tooling** — don't get anchored to Blender. Evaluate Unreal Engine's MetaHuman framework and CLO3D alongside Blender. Pick what produces the most convincing output.
- **AR in MVP** — this significantly increases MVP complexity. Prioritise it but be ready to descope to "realistic 3D viewer" if AR proves too unstable for MVP quality bar. Propose a clear go/no-go milestone for AR.
- **Platform-owned data + retailer API** — design the data architecture for this from day one. The body scan is platform property; retailers get a read-only API window into relevant user measurements/fit preferences. This is a competitive moat.
- **Mixed categories** means garment fitting logic must handle diverse garment types (structured vs. draped, rigid vs. stretch). Scope the physics model accordingly.
- **Zara/H&M partnerships** — these are large retailers. Start conversations early to understand their 3D asset capabilities (do they have CLO3D files? Or will we need to scan everything ourselves?).

---

## Action Required

Please update your DISCOVERY.md with these decisions, reassess your tooling recommendations (especially Blender vs Unreal Engine vs CLO3D), and begin recruiting your agent team. Propose the full team structure (roles, session labels) and first sprint plan back to Seb when ready.
