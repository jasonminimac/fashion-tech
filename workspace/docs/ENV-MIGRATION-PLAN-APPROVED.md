# Fashion Tech — Environment Migration Plan (APPROVED)

**Status:** APPROVED — Execute in Week 4 (after Sprint 3 wraps)  
**Approved by:** Founder (Seb)  
**Approval date:** 2026-03-19  
**Planned execution window:** Week 4 (approx 2026-04-01), 2-3 days notice to teams before execution

---

## Founder Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend source | Floor's implementation | Production-grade, tested; dev skeleton discarded |
| Rigging engine | Part of main pipeline (`pipeline/rigging/`) | Aligned with PROJECT-PATHS.md architecture |
| Timing | After Sprint 3 ends | Avoid mid-sprint merge conflicts and broken CI |
| Archive strategy | Move to `_archive/` folder, no deletes | Zero-risk, supports rollback |

---

## Environment Architecture (Post-Migration)

**Dev** (`/Users/Jason/.openclaw/workspace/projects/fashion-tech/`)  
→ All source code, git-tracked, CI/CD  
→ Permanent home for: apps, pipeline, infrastructure, tests

**Floor workspace** (`/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/`)  
→ Team coordination hub only, NOT git-tracked  
→ Home for: sprint docs, agent outputs, reviewer logs, decisions  
→ NO code lives here after migration

---

## Migration Steps (Execute in Week 4)

### Pre-migration (2-3 days before)
- [ ] Notify all agents: freeze commits to floor workspace code paths
- [ ] Confirm Sprint 3 is complete and all PRs merged
- [ ] Create full backup of both environments

### Phase 1 — Copy code from floor → dev
```bash
# Backend (adopt floor's full implementation)
cp -r /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/ \
      /Users/Jason/.openclaw/workspace/projects/fashion-tech/apps/api/

# Rigging engine (part of pipeline)
cp -r /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine/ \
      /Users/Jason/.openclaw/workspace/projects/fashion-tech/pipeline/rigging/
```

### Phase 2 — Archive originals on floor
```bash
mkdir -p /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/_archive
mv /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/backend/ \
   /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/_archive/backend-moved-2026-03-19/
mv /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/rigging-engine/ \
   /Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/_archive/rigging-engine-moved-2026-03-19/
```

### Phase 3 — Initial commit in dev
```bash
cd /Users/Jason/.openclaw/workspace/projects/fashion-tech/
git add apps/api/ pipeline/rigging/
git commit -m "feat: migrate backend + rigging from floor workspace to dev environment"
git push origin main
```

### Phase 4 — Validate
- [ ] Dev repo builds cleanly (`docker-compose up`)
- [ ] All tests pass
- [ ] Agent briefings updated to point to new paths
- [ ] FLOOR.md updated: dev paths documented

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Active commits during migration | Freeze window + team notice |
| Broken imports/paths | Run full test suite post-migration |
| Lost work | Archive folder + git history preserved |
| Agents writing to old paths | Update all agent briefings post-migration |

---

## Post-Migration: Agent Briefing Update

All agents must be briefed that:
- Code lives in `/Users/Jason/.openclaw/workspace/projects/fashion-tech/`
- Floor workspace is for docs/coordination only
- Submit PRs to GitHub repo, not files to floor workspace
