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

The repository contains two operational subsystems connected by an automated export bridge:
1. **Python Pipeline (`pipeline/`)**: Scraping/parsing source HTML, collecting lessons into structured JSON, creating Excel CMS sheets, calling Gemini API to fill answers (`english_cms_answered.xlsx`), performing CMS validation, and exporting CMS workbooks back to canonical JSON via `pipeline/cms/excel_to_json.py` (`npm run cms:export`).
2. **JavaScript Core (`src/`)**: Canonical domain models, structured JSON validation with strict and `allowUnresolved` modes (differentiating `GAP_SELECT` and `GAP_TEXT`), preview rendering with validation gate, Google Sheets sync, and automated test suite (24/24 JS Jest tests green, 4/4 Python unit tests green).

The end-to-end data bridge connecting answered/draft Excel CMS workbooks back into canonical JSON for the JavaScript preview/runtime was completed and verified under `TASK-004`. Real export of `english_cms.xlsx` achieves 0 structural validation errors in draft mode (`allowUnresolved: true`).

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

Baseline end-to-end data flow (ETL ➔ Excel CMS ➔ Canonical JSON ➔ Validation ➔ Preview) is established. Next objective to be defined by project backlog/roadmap.

## CURRENT TASK

None (TASK-004 completed).

## OPEN ISSUES

None currently blocking.

## RESOLVED ISSUES

- **[INTEGRATION-01]**: Resolved via TASK-004. Implemented `pipeline/cms/excel_to_json.py` and `npm run cms:export` to convert Excel CMS workbooks back into canonical Universal Lesson JSON with relational grouping across all 6 sheets, placeholder normalization, and preview gate integration.
- **[SCHEMA-01]**: Resolved via ADR-002. Unified `.is_correct` across JS validation, models, preview renderer, sheets module, and tests. Implemented `validate(lesson, { allowUnresolved })`. Preview server enforces validation gate with dev-only guardrails for `--force`.
- **[TOOLING-01]**: Resolved. Updated `package.json` test runner to use cross-platform node executable path `node_modules/jest/bin/jest.js`.

## NEXT STEPS

1. Define next task from project roadmap (e.g. Test Engine runtime, content publishing pipeline, or Gemini answer processing automation).

## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Consult `docs/WORKFLOW.md` for task dispatch and return reporting conventions.
3. Inspect `docs/DECISIONS.md` for accepted ADRs (ADR-001, ADR-002).
4. Inspect relevant source files before proposing changes.
5. Run `npm test` (24/24 JS green) and `python -m unittest tests/test_excel_to_json.py` (4/4 Python green) to verify regression baseline.
6. Follow the manual handoff checklist in `01-core.md`.