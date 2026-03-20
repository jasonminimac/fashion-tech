# SPRINT-PROTOCOL.md — Fashion Tech Sprint & Collaboration Protocol

**Version:** 1.0
**Owner:** TBD (CEO, Fashion Tech)
**Applies to:** All Fashion Tech agents

---

## What Is a Sprint?

A sprint is a **structured collaborative session** — not just task dispatch. Sprints are used for:

- **Team updates** — each specialist reports current state, findings, and blockers
- **Collaborative work** — specialists respond to each other's findings and work together in real time
- **Reviews** — review of Seb's feedback AND peer review of work conducted by a specialist
- **Retrospectives** — what went wrong last sprint, what process to fix
- **Next steps** — jointly agreeing what the next sprint tackles; CEO synthesises and confirms

The CEO is the **chair** — opens the floor, manages turns, synthesises disagreements, and does **not** close the sprint until every specialist has had their say and there is genuine alignment. CEO does not dominate; CEO facilitates.

---

## Sprint File Naming

All sprint files are date-prefixed with the sprint open date.

```
workspace/sprints/
├── YYYY-MM-DD-SPRINT-N-BRIEF.md       ← goals, constraints, assignments
├── YYYY-MM-DD-SPRINT-N-MEETING.md     ← live meeting thread (append-only during sprint)
├── YYYY-MM-DD-SPRINT-N-DECISIONS.md   ← decisions made, rationale, owners
└── YYYY-MM-DD-SPRINT-N-SUMMARY.md     ← final summary for Seb/Main Agent
```

Absolute path: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/sprints/`

---

## Sprint Lifecycle

### Phase 1: Open (CEO)

1. Write `YYYY-MM-DD-SPRINT-N-BRIEF.md` covering:
   - Sprint goal (one sentence)
   - Context from previous sprint
   - Seb's feedback (if any)
   - Per-specialist assignments with clear deliverables
   - Open questions to resolve during sprint

2. Create `YYYY-MM-DD-SPRINT-N-MEETING.md` with agenda, attendees, opening questions per specialist.

3. `sessions_send` all specialists: "Sprint N open. Read brief. Add your opening position to MEETING.md under your section."

### Phase 2: Opening Positions (All Specialists)

Each specialist:
1. Reads the brief + referenced docs
2. Reviews what others have already written
3. Appends opening position to MEETING.md: current state, key findings, blockers, questions for the group
4. `sessions_send` CEO: "Position added"
5. May `sessions_send` another specialist directly for clarification

### Phase 3: Discussion Rounds (CEO chairs)

CEO reads all positions and runs rounds until convergence:
1. Identifies conflicts, gaps, cross-dependencies
2. Writes synthesis section to MEETING.md
3. Sends targeted follow-ups to relevant specialists
4. Specialists respond by appending to MEETING.md
5. Repeat until all cross-dependencies resolved and all specialists aligned

**Peer review:** If a specialist's work is significant or uncertain, other specialists may request peer review in MEETING.md.

### Phase 4: Work Phase

1. CEO writes `YYYY-MM-DD-SPRINT-N-DECISIONS.md`
2. Specialists execute assigned work
3. Specialists append progress updates to MEETING.md
4. Direct specialist-to-specialist comms continue as needed

### Phase 5: Close (CEO)

1. Each specialist writes deliverables to their docs subfolder (`workspace/docs/[role]/`)
2. CEO reads all deliverables and verifies coherence
3. CEO writes `YYYY-MM-DD-SPRINT-N-SUMMARY.md`
4. CEO `sessions_send` Main Agent with summary report

---

## Workspace Docs Structure

```
workspace/docs/
├── seb-reviews/     ← Seb's review files and post-review response docs
├── ceo/             ← CEO's sprint summaries and floor-wide docs
├── scanning/        ← Scanning Engineer's deliverables
├── rigging/         ← Rigging Engineer's deliverables
├── garments/        ← Garments Engineer's deliverables
├── ar/              ← AR Engineer's deliverables
├── platform/        ← Platform Engineer's deliverables
└── shared/          ← cross-agent docs, floor-wide references
```

Absolute root: `/Users/Shared/.openclaw-shared/company/floors/fashion-tech/workspace/docs/`

---

## Memory & Compaction

Each agent logs continuously to: `agents/[role]/memory/logs/[MON-YYYY]/YYYY-MM-DD.md`

**Manual log entries:**
```
[HH:MM] Topic: [what we're working on]
- Decision: ...
- Action taken: ...
- Open loops: ...
```

**Compaction checkpoint** (when context nears limit):
```
## Compaction Checkpoint [HH:MM]
[Summary of context not yet manually logged — gap-fill only]
```
