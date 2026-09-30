---
trigger: always_on
---

# CURRENT PROJECT STATE

## DATE

2026-09-30

## PROJECT

Universal English Test Platform

## WORKSPACE

English Breakfast Grammar

## DEVELOPMENT STATUS

Active development.

The repository contains two operational subsystems that are currently **decoupled**:
1. **Python Pipeline (`pipeline/`)**: Handles scraping/parsing source HTML, collecting lessons into structured JSON, creating Excel CMS sheets, calling Gemini API to fill answers (`english_cms_answered.xlsx`), and performing validation. Scripts currently rely on default file paths.
2. **JavaScript Core (`src/`)**: Provides canonical data models, JSON schema validation, interactive HTML preview rendering for static lesson JSON, and future test engine runtime components.

*Reality check*: An automated end-to-end data bridge connecting the answered Excel output of the Python pipeline into the JavaScript preview/runtime has not yet been built.

## AI ORCHESTRATION

Configured and active:
- `.agents/rules/01-core.md` (Always On): Core orchestration, context boundaries, source-of-truth hierarchy, verification, and model handoff protocol.
- `.agents/rules/02-ai-consultation.md` (Model Decision): Protocol for external AI consultation on high-risk or uncertain architectural decisions.
- `.agents/skills/consult/SKILL.md`: Structured consultation workflow.
- *Handoff Mechanism*: Documented protocol/checklist in rules and `/docs`. No automated command or `/handoff` skill exists.

## PROJECT MEMORY

Configured:
- `docs/AI_CONTEXT.md`: Short project context, subsystem roles, and open issues.
- `docs/CURRENT_STATE.md`: Detailed current snapshot and status.
- `docs/TASKS.md`: Task tracking, active tasks, subtasks, and backlog.
- `docs/DECISIONS.md`: Architectural decision records (ADRs).
- `docs/PROJECT.md`: Purpose, principles, and scope boundaries.
- `docs/ARCHITECTURE.md`: High-level system architecture, target flows, and subsystem boundaries.
- `docs/LEGACY_PRODUCT_CONTEXT.md`: Historical contracts and product context (reference only).

## CURRENT OBJECTIVE

Stabilize project memory documentation, complete multi-model workflow guidelines, and address known schema discrepancies in the JavaScript validation layer.

## CURRENT TASK

TASK-001 (Modified) — Project memory initialization, subsystem role fixation, and documentation synchronization.

## OPEN ISSUES

1. **[SCHEMA-01] Mismatch `is_correct` vs `correct` in JS validation/tests**:
   - `src/models/index.js` defines Option with `is_correct: boolean|null` (per Rule 12A).
   - `src/validation/index.js` and `tests/validation.test.js` check `opt.correct`.
   - Result: 2 Jest tests fail. Code remains untouched per instruction pending next task.

2. **[INTEGRATION-01] Missing CMS-to-JSON export bridge**:
   - Python pipeline outputs `english_cms_answered.xlsx`.
   - JavaScript preview server requires individual lesson JSON (e.g. `data/json/L001.json`).
   - No converter exists to transform answered Excel CMS back into canonical JSON.

3. **[TOOLING-01] npm test on Windows**:
   - `package.json` contains a POSIX-style path for Jest (`node --experimental-vm-modules node_modules/.bin/jest`), causing issues when run on Windows without `.cmd` or explicit node runner.

## NEXT STEPS

1. Complete TASK-001 documentation alignment and multi-model workflow notes.
2. Implement TASK-002: Align JS validation and unit tests with `is_correct` contract.
3. Implement TASK-003: Cross-platform npm test runner configuration.
4. Implement TASK-004: CMS-to-JSON export bridge to enable end-to-end previewing of pipeline data.

## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Inspect `docs/DECISIONS.md` for accepted ADRs.
3. Inspect relevant source files before proposing changes.
4. Distinguish Python Pipeline (ETL/AI batching) from JavaScript Core (models/runtime/preview).
5. Follow the manual handoff checklist in `01-core.md` (no automated tool exists).
6. Do not modify open issues until authorized by a specific task.