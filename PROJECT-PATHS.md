# Fashion Tech — Project Path Reference
**Version:** 1.0
**Date:** 2026-03-18
**Owner:** Fashion Tech CEO

All work for the Fashion Tech platform lives under:
```
/Users/Jason/.openclaw/workspace/projects/fashion-tech/
```

## Directory Structure

```
projects/fashion-tech/
├── pipeline/
│   ├── scanning/          ← Open3D, COLMAP, LiDAR processing scripts
│   ├── rigging/           ← Blender Rigify scripts, weight painting automation
│   ├── garments/          ← CLO3D simulation pipeline, garment QA scripts
│   └── ar/                ← ARKit/RealityKit integration, .usdz conversion
├── apps/
│   ├── ios-ar/            ← iOS app (Swift/Xcode) — scanner + AR try-on
│   ├── api/               ← FastAPI backend (Python)
│   └── web/               ← React frontend (model-viewer, Three.js)
├── assets/
│   ├── meshes/            ← Test body scan .ply / .obj files
│   ├── garments/          ← Baked garment .obj sequences, .usdz, .glb
│   ├── textures/          ← PBR texture maps (albedo, normal, roughness)
│   └── animations/        ← .bvh motion capture, walk cycle data
├── data/
│   ├── scans/             ← Body scan outputs (measurements.json, joints.json)
│   ├── test-subjects/     ← Test subject scan archives
│   └── benchmarks/        ← AR performance traces, accuracy reports
├── docs/
│   ├── sprints/           ← Sprint briefs, meeting notes, decisions, summaries
│   ├── decisions/         ← Architecture decision records (ADRs)
│   └── research/          ← Partner recon, market research docs
├── packages/
│   └── retailer-sdk/      ← JS retailer embed SDK (Phase 2)
└── infrastructure/
    ├── db/                ← schema.sql, migrations
    ├── s3/                ← S3 bucket configs, IAM policies
    └── cdn/               ← CloudFront configs

```

## Per-Role Output Locations

| Role | Primary Output Path | Key Deliverables |
|------|---------------------|-----------------|
| `fashion-scanning` | `pipeline/scanning/` | Open3D scripts, COLMAP pipeline, measurement extraction |
| `fashion-scanning` | `apps/ios-ar/scanner/` | Swift LiDAR capture app |
| `fashion-scanning` | `data/scans/` | Test scan outputs (.ply, .obj, measurements.json, joints.json) |
| `fashion-rigging` | `pipeline/rigging/` | Blender Rigify scripts, headless pipeline |
| `fashion-rigging` | `assets/meshes/` | Rigged .blend files, exported .glb, .usdz |
| `fashion-garments` | `pipeline/garments/` | CLO3D sim config, garment_metadata.json schema |
| `fashion-garments` | `assets/garments/` | Baked .obj sequences, .usdz garment assets |
| `fashion-ar` | `apps/ios-ar/` | Xcode project — ARKit body tracking, try-on renderer |
| `fashion-platform` | `apps/api/` | FastAPI app, schema.sql, OpenAPI spec |
| `fashion-platform` | `apps/web/` | React components, model-viewer, Three.js viewer |
| `fashion-platform` | `infrastructure/db/` | schema.sql, seed data |
| CEO | `docs/sprints/` | Sprint briefs, decisions, summaries |
| CEO | `docs/research/` | Partner recon reports, roadmap docs |

## Naming Conventions

- Sprint docs: `SPRINT-N-BRIEF.md`, `SPRINT-N-MEETING.md`, `SPRINT-N-DECISIONS.md`, `SPRINT-N-SUMMARY.md`
- Test scans: `scan-{subject-id}-{date}.ply` (e.g. `scan-001-2026-03-18.ply`)
- Garment assets: `{garment-id}-{size}-{frame:03d}.obj` (e.g. `tshirt-m-001.obj`)
- Schema versions: `schema-v{N}.sql`

## Important Notes

1. **No destructive operations** without CEO approval (no `rm -rf`, no `git reset --hard`)
2. **Write outputs to this tree**, not to the floor root (`/Users/Shared/...`)
3. **CEO floor root** (for sprint docs/meeting notes): `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`
4. **When in doubt**: put deliverables in your role's primary output path and document the location in your task output
