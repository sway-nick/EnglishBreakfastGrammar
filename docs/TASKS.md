---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

TASK-004 — Build CMS-to-JSON export bridge (Pending start)

Status: pending

## OBJECTIVE

Implement a reliable data bridge to convert answered Excel CMS workbooks (`english_cms_answered.xlsx`) back into validated canonical Universal Lesson JSON files, establishing the missing link between the Python ETL pipeline and the JavaScript Test Engine / Preview server.

---

## COMPLETED RECENT TASKS

### TASK-001 — Complete AI orchestration and multi-model workflow setup
Status: completed
- **TASK-001.1**: Core orchestration rules (`.agents/rules/01-core.md`) — completed.
- **TASK-001.2**: External AI consultation rules & skill (`02-ai-consultation.md`, `skills/consult/SKILL.md`) — completed.
- **TASK-001.3**: Persistent project memory docs (`docs/AI_CONTEXT.md`, `CURRENT_STATE.md`, `PROJECT.md`, `DECISIONS.md`, `TASKS.md`) — completed.
- **TASK-001.4**: Architecture review & subsystem boundaries (`docs/ARCHITECTURE.md`) — completed.
- **TASK-001.5**: Operational multi-model workflow definition (`docs/WORKFLOW.md`), model selection matrix, and dispatch/report templates — completed.

### TASK-002 — Fix `is_correct vs correct` schema mismatch in JS validation and tests
Status: completed
- Added ADR-002 (accepted) to `docs/DECISIONS.md`.
- Unified `.is_correct` across `src/validation/index.js`, `src/preview/renderer.js`, `src/sheets/index.js`, and test suite.
- Implemented `validate(lesson, { allowUnresolved = false } = {})` with strict default and Rule 12A draft mode.
- Implemented preview server validation gate and dev-only guardrails for `--force`.
- Full automated test suite passes (20/20 green).

### TASK-003 — Cross-platform npm test runner configuration
Status: completed
- Updated `package.json` test script to `"test": "node --experimental-vm-modules node_modules/jest/bin/jest.js"`.
- Verified cross-platform execution under Windows PowerShell.

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
- Data contract stabilization, preview validation gate, and cross-platform test runner (`TASK-002` + `TASK-003`, commit `0667ada`).
- Operational multi-model workflow formalized (`TASK-001`, `docs/WORKFLOW.md`).