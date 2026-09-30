---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

TASK-001.5 — Multi-model workflow definition & task dispatching

Status: in_progress

## OBJECTIVE

Formulate operational task delegation and handoff conventions between Antigravity (primary orchestrator), Claude/Gemini (implementation), and external AI (architectural review), ensuring minimal token overhead and predictable verification.

## COMPLETED RECENT TASKS

### TASK-002 — Fix `is_correct vs correct` schema mismatch in JS validation and tests
Status: completed
- Added ADR-002 (provisional) to `docs/DECISIONS.md`.
- Unified `.is_correct` in `src/validation/index.js`, `src/preview/renderer.js`, `src/sheets/index.js`, and `tests/validation.test.js`.
- Implemented `validate(lesson, { allowUnresolved = false } = {})`:
  - Strict mode (default): enforces boolean `is_correct` and at least one correct answer per gap/choice.
  - `allowUnresolved: true`: accommodates Rule 12A raw imports awaiting AI answer processing (`is_correct: null`), emitting non-blocking `INFO` diagnostics.
- Added explicit validation gate to `src/preview/server.js`.
- Added test coverage for both strict and `allowUnresolved` modes (10/10 tests pass).

### TASK-003 — Cross-platform npm test runner configuration
Status: completed
- Updated `package.json` test script to `"test": "node --experimental-vm-modules node_modules/jest/bin/jest.js"`.
- Verified execution works cleanly under Windows PowerShell and cross-platform environments.

---

## SUBTASKS OF TASK-001 (Setup & Orchestration)

### TASK-001.1 — Core orchestration rules (completed)
### TASK-001.2 — External AI consultation (completed)
### TASK-001.3 — Project memory documentation (completed)
### TASK-001.4 — Architecture review & dual-stack subsystem roles (completed)
### TASK-001.5 — Multi-model workflow definition (in_progress)

---

## BACKLOG

### TASK-004 — Build CMS-to-JSON export bridge
Status: pending
- Implement an export script to convert answered Excel CMS files (`english_cms_answered.xlsx`) back into canonical Universal Lesson JSON.
- Verify end-to-end integration: Python pipeline output ➔ Universal JSON ➔ JS Preview server (`src/preview/server.js`).

---

## COMPLETED MAJOR MILESTONES

- Initial project baseline and orchestration system setup (commit `3148159`).
- Python Pipeline implementation: collector, parser, Excel CMS generator, Gemini answer processor, CMS validator (commits `b051d78`, `c728a73`).
- Data contract stabilization and cross-platform test runner (`TASK-002` + `TASK-003`).