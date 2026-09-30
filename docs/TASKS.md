---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

None (TASK-004 completed; awaiting next task definition from backlog/roadmap).

Status: pending

## OBJECTIVE

N/A

---

## COMPLETED RECENT TASKS

### TASK-004 — Build CMS-to-JSON export bridge
Status: completed
- Created `pipeline/cms/excel_to_json.py`: converts answered/draft Excel CMS workbooks (`english_cms_answered.xlsx` / `english_cms.xlsx`) into canonical Universal Lesson JSON.
- Supported relational grouping across all 6 sheets (`Lessons`, `Exercises`, `Questions`, `Gaps`, `Options`, `Explanations`), preserving stable IDs and order.
- Mapped question types (`gap` + `select` ➔ `gap_select`, `gap` + `text` ➔ `gap_text`, choice types).
- Reconstructed `accepted_answers`: `[correct_answer] + extras` (preserving order and deduplicating).
- Mapped boolean `is_correct` (True/False/None) ➔ JSON `true`/`false`/`null` per ADR-002.
- Normalized placeholders `{{gap_1}}` ➔ `{{gap1}}` strictly at the export boundary.
- Added npm script `"cms:export": "python pipeline/cms/excel_to_json.py"` to `package.json`.
- Refined `src/validation/index.js` `validateGap()` to differentiate `GAP_SELECT` (mandatory options) and `GAP_TEXT` (optional options, text answer validation).
- Verified with unit tests: 24/24 JS Jest tests PASS, 4/4 Python unit tests PASS.
- Verified on real Excel workbook (`C:\Users\user\Desktop\english_cms.xlsx`): all 6 lessons exported and achieve 0 validation errors in draft mode (`allowUnresolved: true`).
- Verified Preview Gate: blocks un-answered draft files in strict mode, permits in draft mode, and supports `--force` for local dev bypass.

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
- Full automated test suite passes (24/24 green).

### TASK-003 — Cross-platform npm test runner configuration
Status: completed
- Updated `package.json` test script to `"test": "node --experimental-vm-modules node_modules/jest/bin/jest.js"`.
- Verified cross-platform execution under Windows PowerShell.

---

## BACKLOG

Tasks to be defined according to the project roadmap.

---

## COMPLETED MAJOR MILESTONES

- Initial project baseline and orchestration system setup (commit `3148159`).
- Python Pipeline implementation: collector, parser, Excel CMS generator, Gemini answer processor, CMS validator (commits `b051d78`, `c728a73`).
- Data contract stabilization, preview validation gate, and cross-platform test runner (`TASK-002` + `TASK-003`, commit `0667ada`).
- Operational multi-model workflow formalized (`TASK-001`, `docs/WORKFLOW.md`).