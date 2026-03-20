# COMMS Protocol — Fashion Tech

## Agent → CEO Communication

Specialist agents communicate upward to the CEO via inbox:

```
comms/inbox/ceo/[TIMESTAMP]-from-[sender].md
```

Use this for:
- Task completion reports
- Blockers you cannot resolve yourself
- Questions requiring CEO direction
- Findings that affect the sprint

CEO checks inbox at start of every session and after every task.

## Sending a Message

1. Write message file to recipient's inbox:
   `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/inbox/[recipient]/[TIMESTAMP]-from-[sender].md`
   Format: `2026-03-15T18:30-from-ceo.md`

2. Log to comms audit trail:
   `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/log/YYYY-MM-DD.md`

3. Notify recipient via `sessions_send` if they have an active session.

## Checking Your Inbox

At the START of every session and END of every task:
```bash
ls /Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/inbox/[your-role]/
```
Read all unread messages, process them, then move to processed/.

## Message Format

```markdown
# Message — [DATE] [TIME]
**From:** [sender role]
**To:** [recipient role]
**Priority:** normal | urgent | escalation
**Subject:** [one line]

[body]

**Action required:** [what the recipient needs to do, if anything]
```

## Session Labels

| Agent | Session Label |
|-------|--------------|
| CEO | `fashion-tech-ceo` |
| Scanning Engineer | `fashion-scanning` |
| Rigging Engineer | `fashion-rigging` |
| Garments Engineer | `fashion-garments` |
| AR Engineer | `fashion-ar` |
| Platform Engineer | `fashion-platform` |

## Escalations to Main Agent

CEO only. Send via `sessions_send` targeting the main session:
```
ESCALATION — Fashion Tech
Type: [decision-needed | blocker | milestone | hr-change]
Summary: [one sentence]
Detail: [context]
Action needed: [what you need from Main Agent / Seb]
Urgency: [low | medium | high | immediate]
```

## Direct Specialist-to-Specialist Communication

Specialists may `sessions_send` each other directly at any time when:
- A question requires the other specialist's domain expertise
- A finding has direct implications for another specialist's current work
- Unblocking yourself requires a quick answer

**Rule:** Copy CEO on anything that changes scope, creates a new dependency, or contradicts a prior decision. Routine queries do not need to route through the CEO.

## Audit Trail

Every message sent is also logged to: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/comms/log/YYYY-MM-DD.md`
