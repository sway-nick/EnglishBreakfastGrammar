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

The repository contains two operational subsystems:
1. **Python Pipeline (`pipeline/`)**: Scraping/parsing source HTML, collecting lessons into structured JSON, creating Excel CMS sheets, calling Gemini API to fill answers (`english_cms_answered.xlsx`), and performing CMS validation.
2. **JavaScript Core (`src/`)**: Canonical domain models, structured JSON validation with strict and `allowUnresolved` modes, preview rendering with validation gate, Google Sheets sync, and passing automated test suite (20/20 tests green).

An end-to-end data bridge connecting the answered Excel output of the Python pipeline into canonical JSON for the JavaScript preview/runtime is planned under `TASK-004`.

## AI ORCHESTRATION

Configured and active:
- `.agents/rules/01-core.md` (Always On): Core orchestration, context boundaries, source-of-truth hierarchy, verification, and model handoff protocol.
- `.agents/rules/02-ai-consultation.md` (Model Decision): Protocol for external AI consultation on high-risk or uncertain architectural decisions.
- `.agents/skills/consult/SKILL.md`: Structured consultation workflow.
- `docs/WORKFLOW.md`: Operational multi-model task lifecycle, model selection defaults, and task dispatch / return templates.

## PROJECT MEMORY

Configured:
- `docs/AI_CONTEXT.md`: Short project context, subsystem roles, and open issues.
- `docs/CURRENT_STATE.md`: Detailed current snapshot and status.
- `docs/TASKS.md`: Task tracking, active tasks, subtasks, and backlog.
- `docs/DECISIONS.md`: Architectural decision records (ADR-001 accepted, ADR-002 accepted).
- `docs/PROJECT.md`: Purpose, principles, and scope boundaries.
- `docs/ARCHITECTURE.md`: High-level system architecture, target flows, and subsystem boundaries.
- `docs/WORKFLOW.md`: Operational multi-model development workflow and packet templates.
- `docs/LEGACY_PRODUCT_CONTEXT.md`: Historical contracts and product context (reference only).

## CURRENT OBJECTIVE

Implement `TASK-004` (CMS-to-JSON export bridge) to connect Python Pipeline outputs directly with the JavaScript preview and runtime engine.

## CURRENT TASK

TASK-004 — Build CMS-to-JSON export bridge (Pending start).

## OPEN ISSUES

1. **[INTEGRATION-01] Missing CMS-to-JSON export bridge**:
   - Python pipeline outputs `english_cms_answered.xlsx`.
   - JavaScript preview server requires individual lesson JSON (e.g. `data/json/L001.json`).
   - No converter exists to transform answered Excel CMS back into canonical JSON. Tracked under `TASK-004`.

## RESOLVED ISSUES

- **[SCHEMA-01]**: Resolved via ADR-002. Unified `.is_correct` across JS validation, models, preview renderer, sheets module, and tests. Implemented `validate(lesson, { allowUnresolved })`. Preview server enforces validation gate with dev-only guardrails for `--force`.
- **[TOOLING-01]**: Resolved. Updated `package.json` test runner to use cross-platform node executable path `node_modules/jest/bin/jest.js`.

## NEXT STEPS

1. Implement TASK-004: CMS-to-JSON export bridge to enable end-to-end previewing of pipeline data.

## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Consult `docs/WORKFLOW.md` for task dispatch and return reporting conventions.
3. Inspect `docs/DECISIONS.md` for accepted ADRs (ADR-001, ADR-002).
4. Inspect relevant source files before proposing changes.
5. Run `npm test` to verify that all 20 tests continue to pass.
6. Follow the manual handoff checklist in `01-core.md`.