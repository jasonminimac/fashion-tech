# AGENTS.md

## This Is Your Workspace

Root: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/`

## Session Startup

Read in order:
1. `SOUL.md` — who you are
2. `FLOOR.md` — the mission and team structure
3. `agents/[your-role]/MIND/logs/[CURRENT-MONTH]/YYYY-MM-DD.md` (today + yesterday) if they exist

## Memory

- Daily notes: `agents/[your-role]/MIND/logs/[CURRENT-MONTH]/YYYY-MM-DD.md`
- Long-term: `MEMORY.md` (main sessions only)

Write things down. Mental notes don't survive restarts.

## Red Lines

- Don't send emails, post publicly, or take external actions without asking
- Don't run destructive commands without confirming
- 3D pipeline work: be precise about what tools/libraries are in scope

## Communication

- CEO inbox: `comms/inbox/ceo/`
- Write decisions to `decisions/`
- Use `workspace/docs/` for research and planning docs

## Agent Spawn Protocol (mandatory)

When spawning any agent on this floor, the task briefing MUST end with:

```
## Your Protocol (mandatory — read this)

Read this file before starting work:
/Users/Shared/.openclaw-shared/company/AGENT-PROTOCOL.md

Key rules:
- When your task is complete, do NOT report to the CEO.
- Write all output to workspace/docs/[your-role]/
- Create workspace/docs/reviewer/INBOX-[task-id].md with: task ID, agent role, files produced, summary, uncertainties
- IMMEDIATELY spawn the Reviewer yourself (runtime=subagent, mode=run, model=claude-haiku-4.5) — do not wait for the CEO
- Your task is not done until the Reviewer issues a PASS
- If Reviewer returns REWORK: fix issues, resubmit as INBOX-[task-id]-v2.md, spawn Reviewer again
- Phase 1 only — no Phase 2 work without explicit founder approval
```

Omitting this breaks the quality gate. Every agent, every spawn, every time.


## Reviewer Lock & Sweep Protocol

**Problem this solves:** Multiple agents finishing in parallel would each try to spawn a Reviewer, causing race conditions and lost review history.

**How it works:**
1. Agent finishes work → writes `workspace/docs/reviewer/INBOX-[task-id].md`
2. Agent checks for `workspace/docs/reviewer/REVIEWER-ACTIVE.lock`
   - **Lock exists:** Another Reviewer is running. Do NOT spawn. Exit. The active Reviewer will sweep your INBOX before it finishes.
   - **No lock:** Spawn the Reviewer. It will create the lock immediately on start.
3. Reviewer always sweeps ALL pending INBOX files (not just the one that triggered it) before exiting.
4. Reviewer deletes the lock file when all INBOXes are processed.

**Result:** One Reviewer at a time, zero missed submissions.

