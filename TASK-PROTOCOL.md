# TASK-PROTOCOL.md — Fashion Tech

## Overview

All task assignments and completions follow this protocol. Every task has an ID linking brief to report.

## Task ID Format

`[ROLE-INITIAL][DATE]-[N]`

| Role | Initial |
|------|---------|
| Scanning Engineer | S |
| Rigging Engineer | R |
| Garments Engineer | G |
| AR Engineer | A |
| Platform Engineer | P |

Examples: `S20260318-1` (Scanning, March 18, task 1), `A20260318-2` (AR, same day)

---

## Task Brief (CEO → Specialist)

File: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/inbox/[role]/[TIMESTAMP]-from-ceo.md`

```markdown
# Task Brief — [TASK-ID]

**Assigned to:** [Name] ([Role])
**Assigned by:** [CEO Name]
**Date:** YYYY-MM-DD HH:MM
**Priority:** low | normal | high | urgent

## Goal
[One sentence: what needs to be achieved]

## Context
[What the specialist needs to know. Link to relevant files by absolute path.]

## Deliverables
- [ ] `path/to/output-file.md` — [what it contains]

## Success Criteria
[How we know this task is done and done well]

## Urgency / Deadline
[When needed, or "no deadline — work to quality"]

## If Blocked
[What to try first, then report to CEO via inbox]
```

---

## Task Report (Specialist → CEO)

File: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/inbox/ceo/[TIMESTAMP]-from-[name].md`

```markdown
# Task Report — [TASK-ID]

**From:** [Name] ([Role])
**To:** [CEO Name]
**Date:** YYYY-MM-DD HH:MM
**Status:** complete | blocked | partial

## Summary
[One sentence: what was done / what happened]

## Outputs Produced
- `path/to/file` — [description]

## Blockers
[If blocked or partial: what is blocking, what was tried, what CEO needs to resolve]

## Recommendations
[Optional: suggested next task, concerns, observations]
```

---

## CEO Workflow per Task

1. Write task brief → `comms/inbox/[role]/[TIMESTAMP]-from-ceo.md`
2. `sessions_send(label="fashion-[role]", message="New task in your inbox: [TASK-ID]")`
3. Update specialist's `state/SESSION.md` — set active task
4. Wait for report in `comms/inbox/ceo/`
5. On receipt: read report, update state, log outcome, assign next task

## Specialist Workflow per Task

1. Receive `sessions_send` notification OR find brief in inbox at boot
2. Read brief fully before starting
3. Execute — log progress to own memory
4. Write task report → `comms/inbox/ceo/[TIMESTAMP]-from-[name].md`
5. Update own `state/SESSION.md`
6. If inbox empty → enter Idle Protocol (see BOOT.md)
