# MULTI-MODEL DEVELOPMENT WORKFLOW

## PURPOSE

This document defines the operational protocol for multi-model development on the **Universal English Test Platform (`English Breakfast Grammar`)**.

It formalizes how tasks are planned, reviewed, dispatched to implementation models, verified, and documented across model switches, ensuring continuity without relying on conversation history.

---

## 1. ROLES & RECOMMENDED MODEL DEFAULTS

Model selection is guided by **recommended defaults**, not rigid restrictions.
**Antigravity** acts as the primary orchestrator and makes the final decision on model selection. Antigravity may assign any task to a different model if the specific context justifies it, noting a brief rationale.

### 1. Antigravity — Primary Engineering Orchestrator
- **Core Responsibilities**:
  - Project task planning and backlog management ([docs/TASKS.md](file:///c:/projects/English%20Breakfast%20Grammar/docs/TASKS.md)).
  - Source-of-truth governance and architectural boundary enforcement ([01-core.md](file:///c:/projects/English%20Breakfast%20Grammar/.agents/rules/01-core.md)).
  - Git repository operations (staging, commits, pushes, clean working tree).
  - Executing automated tests and verifying code integrity.
  - Maintaining persistent project documentation in `/docs`.
  - Initiating and evaluating external consultations (`/consult`).
  - Preparing and reviewing Task Dispatch Packets for implementation models.

### 2. Claude — Recommended Default: Complex JS/TS & Core Architecture
- **Best Suited For**:
  - Non-trivial JavaScript domain model refactoring (`src/models/`, `src/validation/`).
  - Interactive Test Engine logic and browser preview components (`src/preview/`).
  - Complex schema validation rules and edge-case test suites.
  - Algorithmic and structural tasks requiring deep reasoning.

### 3. Gemini — Recommended Default: Python, ETL & Large Text Data
- **Best Suited For**:
  - Python ETL pipelines (`pipeline/collector/`, `pipeline/parser/`, `pipeline/validators/`).
  - Google Cloud / Gemini API batch integrations (`pipeline/gemini/`).
  - Excel/Sheets CMS generation and processing of large volume text datasets.
  - Rapid scaffolding and large context data transformations.

### 4. External Architect (ChatGPT Thinking) — Independent Reviewer
- **Best Suited For**:
  - Independent review of significant, irreversible, or high-risk architectural decisions.
  - Review of data contracts, security boundaries, and major integrations via [.agents/rules/02-ai-consultation.md](file:///c:/projects/English%20Breakfast%20Grammar/.agents/rules/02-ai-consultation.md).

---

## 2. STANDARD TASK LIFECYCLE

Every non-trivial engineering task follows this standard 7-step lifecycle:

```text
[1. Planning & Task Intake] (docs/TASKS.md)
            │
            ▼
[2. Architectural Consultation Check] ──(If high-risk or uncertain)──▶ [/consult (External Review)]
            │                                                                     │
            ▼                                                                     ▼
[3. Task Dispatch Packet] ◀────────────────────────────────────────── [ACCEPT / MODIFY / DEFER]
            │
            ▼
[4. Implementation] (Claude / Gemini / Antigravity)
            │
            ▼
[5. Verification] (npm test / python validation / automated checks)
            │
            ▼
[6. Documentation Checkpoint] (AI_CONTEXT.md / CURRENT_STATE.md / DECISIONS.md)
            │
            ▼
[7. Review & Git Commit] (Clean working tree, commit & push)
```

---

## 3. TASK DISPATCH PACKET (ORCHESTRATOR ➔ IMPLEMENTER)

When a task is handed off to an implementation model (or when switching models), Antigravity produces a compact **Task Dispatch Packet**.

The implementer must rely only on the specified context files, avoiding full-codebase re-scans.

```markdown
### TASK DISPATCH PACKET

**TASK ID**: TASK-XXX — [Short title]
**ASSIGNED MODEL**: [Claude / Gemini / Antigravity] (Reason if departing from defaults)
**OBJECTIVE**: [1-2 sentences on what must be achieved]

**CONTEXT FILES TO READ**:
- `docs/AI_CONTEXT.md`
- [Target file 1]
- [Target file 2]

**FILES TO MODIFY**:
- [Target file to edit/create]

**CONSTRAINTS & POLICIES**:
- [e.g., Rule 12A: parsers never mark correct answers]
- [e.g., Do NOT modify untracked data/ directory]
- [e.g., Maintain 100% test passing rate]

**VERIFICATION COMMAND**:
- `npm test` / [Command]

**COMPLETION CRITERIA**:
- [Clear definition of done]
```

---

## 4. TASK RETURN REPORT (IMPLEMENTER ➔ ORCHESTRATOR)

Upon completing implementation, the model returns a standardized **Return Report**.

```markdown
### TASK RETURN REPORT

**TASK ID**: TASK-XXX
**STATUS**: [COMPLETED / BLOCKED / PARTIAL]

**MODIFIED FILES**:
1. `path/to/file.js` — [Brief description of change]
2. `tests/test.js` — [Tests added or updated]

**VERIFICATION RESULTS**:
- Command executed: `npm test`
- Outcome: [e.g., 20/20 passed, 0 failures]

**UNEXPECTED FINDINGS / OPEN QUESTIONS**:
- [None, or description of any discovered discrepancies]

**RECOMMENDED ORCHESTRATOR ACTION**:
- [Review and commit / verify specific edge-case]
```

---

## 5. TOKEN EFFICIENCY & CONTEXT MANAGEMENT

To prevent context dilution and excessive token usage:
1. **Never send entire directory trees or large data files** to conversational models.
2. **Use persistent documentation** (`docs/AI_CONTEXT.md`, `docs/CURRENT_STATE.md`) as the primary context anchor.
3. **Respect subsystem boundaries**: Python Pipeline (`pipeline/`) and JavaScript Core (`src/`) are largely decoupled tools; changes to one should not unnecessarily load the other.
4. **Clean handoffs**: Every model switch must begin from project files and docs, not from assumptions about prior conversation logs.
