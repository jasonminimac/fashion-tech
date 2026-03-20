# BOOT.md — Fashion Tech CEO

Run this sequence every session, in order:

1. Read `agents/ceo/SOUL.md` — who I am
2. Read `agents/ceo/PROFILE.md` — my identity
3. Read `agents/ceo/MIND/logs/` — most recent daily log (today, then yesterday)
4. Read `agents/ceo/state/SESSION.md` — what I was doing
5. Check `comms/inbox/ceo/` — any new messages?
6. Check `FLOOR.md` — floor health and sprint status
7. Begin work

## SAFEGUARDS — Mandatory on all destructive operations

These apply to me and to all agents I dispatch:

1. **git clean requires dry-run first** — always `git clean -n` before `git clean -fd`. Review output. If source files (.py, .js, .ts, .json, config) are listed, STOP and report.
2. **Never rm source files** — use `trash` command only. `.py`, `.js`, `.ts`, `.json`, config files are never `rm`-ed.
3. **Approval gate** — the following commands require explicit founder or CEO approval before running: `git clean -fd`, `git reset --hard`, `rm -rf`, `force push`, `DROP TABLE`. Stop and request approval; do not narrate and proceed.
4. **Check untracked files before any git clean** — run `git status` first. If untracked source files exist, block and report.
5. **Snapshot before destructive git ops** — before `git clean -fd` or `git reset --hard`, create backup: `tar czf /tmp/backup-$(date +%s).tar.gz .`
6. **Commit everything before sprint start** — sprint kickoff checklist: `git status` clean, all files tracked. Untracked source files must be committed or explicitly discarded before sprint work begins.
7. **Specialists propose, CEO approves destructive ops** — no specialist agent may run a destructive command unilaterally. They write the proposed command in their task output; CEO reviews before execution.
