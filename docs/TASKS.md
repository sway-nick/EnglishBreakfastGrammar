---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

TASK-001 (Modified) — Project orchestration and memory synchronization

Status: in_progress

## OBJECTIVE

Establish consistent project context, define subsystem boundaries between the Python Pipeline and JavaScript Core, record known open issues without premature code modification, and prepare the project for reliable multi-model collaboration.

## SUBTASKS

### TASK-001.1 — Core orchestration rules
Status: completed
- Created `.agents/rules/01-core.md` (Always On).
- Defined source-of-truth hierarchy, context management, verification rules, and handoff checkpoints.

### TASK-001.2 — External AI consultation
Status: completed
- Created `.agents/rules/02-ai-consultation.md` (Model Decision).
- Created `.agents/skills/consult/SKILL.md`.
- Defined consultation thresholds, compact English consultation packages, and Russian user summaries.

### TASK-001.3 — Project memory documentation
Status: completed
- Updated `docs/AI_CONTEXT.md` (subsystem roles, open issues, removed placeholders).
- Updated `docs/CURRENT_STATE.md` (current status as of 2026-09-30).
- Updated `docs/DECISIONS.md` (ADR-001 accepted).
- Updated `docs/PROJECT.md` (boundaries and principles).
- Updated `docs/TASKS.md` (current active tasks and backlog).

### TASK-001.4 — Architecture review & dual-stack subsystem roles
Status: completed
- Inspected codebase structure: identified Python Pipeline (`pipeline/`) and JavaScript Core (`src/`).
- Documented role boundaries and target data flow in `docs/ARCHITECTURE.md`.
- Verified that subsystems are currently decoupled (missing CMS-to-JSON bridge).
- Identified and isolated OPEN ISSUE [SCHEMA-01] (`is_correct vs correct`).

### TASK-001.5 — Multi-model workflow definition
Status: in_progress
- Baseline principles agreed in ADR-001 (Antigravity as orchestrator, Claude/Gemini for implementation, ChatGPT Thinking for consultation).
- *Pending*: Formulate specific operational task handoff conventions and task prompt templates between models.

---

## BACKLOG

### TASK-002 — Fix `is_correct vs correct` schema mismatch in JS validation and tests
Status: pending
- Update `src/validation/index.js` to inspect `option.is_correct` in accordance with Rule 12A and `src/models/index.js`.
- Update `tests/validation.test.js` to pass `is_correct: true/false` instead of `correct`.
- Verify all Jest tests pass.

### TASK-003 — Cross-platform npm test runner configuration
Status: pending
- Update `package.json` test script to ensure compatibility with Windows PowerShell and POSIX shells without relying on raw bash wrapper paths.

### TASK-004 — Build CMS-to-JSON export bridge
Status: pending
- Implement an export script to convert answered Excel CMS files (`english_cms_answered.xlsx`) back into canonical Universal Lesson JSON.
- Verify end-to-end integration: Python pipeline output ➔ Universal JSON ➔ JS Preview server (`src/preview/server.js`).

---

## COMPLETED MAJOR MILESTONES

- Initial project baseline and orchestration system setup (commit `3148159`).
- Python Pipeline implementation: collector, parser, Excel CMS generator, Gemini answer processor, CMS validator (commits `b051d78`, `c728a73`).