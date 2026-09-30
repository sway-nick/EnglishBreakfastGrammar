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
1. **Python Pipeline (`pipeline/`)**: Scraping/parsing source HTML, collecting lessons into structured JSON, creating Excel CMS sheets, calling Gemini API to fill answers (`english_cms_answered.xlsx`), performing CMS validation, exporting CMS workbooks back to canonical JSON via `pipeline/cms/excel_to_json.py` (`npm run cms:export`), and discovering source taxonomy and exercise pages via `pipeline/catalog/source_catalog_builder.py` (`npm run catalog:discover`).
2. **JavaScript Core (`src/`)**: Canonical domain models, structured JSON validation with strict and `allowUnresolved` modes (differentiating `GAP_SELECT` and `GAP_TEXT`), preview rendering with validation gate, Google Sheets sync, and automated test suite (24/24 JS Jest tests green, 21/21 Python unit tests green).

The end-to-end data bridge connecting answered/draft Excel CMS workbooks back into canonical JSON for the JavaScript preview/runtime was completed and verified under `TASK-004`. Real export of `english_cms.xlsx` achieves 0 structural validation errors in draft mode (`allowUnresolved: true`).
Source taxonomy discovery across all 7 levels and 225 topics was completed under `TASK-005`.
Full authorized content acquisition across all 225 topics and 7 levels (638 unique exercise HTML pages, 646 total files, ~206.9 MB cached in `data/cache/html` with 0 failures and 0 challenges) was completed under `TASK-006` / `ADR-003`. 0 partial topics remaining in web acquisition. Checkpoint recorded in `docs/ACQUISITION_CHECKPOINT_2026-09-30.md`.

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
- `docs/DECISIONS.md`: Architectural decision records (ADR-001 accepted, ADR-002 accepted, ADR-003 accepted).
- `docs/PROJECT.md`: Purpose, principles, and scope boundaries.
- `docs/ARCHITECTURE.md`: High-level system architecture, target flows, and subsystem boundaries.
- `docs/WORKFLOW.md`: Operational multi-model development workflow and packet templates.
- `docs/LEGACY_PRODUCT_CONTEXT.md`: Historical contracts and product context (reference only).
- `docs/ACQUISITION_CHECKPOINT_2026-09-30.md`: Complete audit and metrics for the 225-topic Test-English HTML acquisition.

## CURRENT OBJECTIVE

Web content acquisition is 100% complete (225/225 topics, 638 exercise pages). The next planned phase is fully offline: offline parsing of the complete cached HTML corpus, CMS generation, answer enrichment, adaptation/rewrite, and database import.

## CURRENT TASK

TASK-007 — Offline Parser Batch Execution & CMS Ingestion across Cached Corpus.

## OPEN ISSUES

None. Web acquisition is complete.

## RESOLVED ISSUES

- **[ACQUISITION-01]**: Resolved via TASK-006 / ADR-003. Full browser-assisted acquisition completed via Remote CDP across all 7 levels (225/225 topics, 638 exercise pages, 646 total HTML files, 206.9 MB cache, 0 challenges, 0 failures).
- **[CATALOG-01]**: Resolved via TASK-005. Complete source taxonomy of 7 levels and 225 topics mapped into canonical `data/catalog/source_catalog.json` and human-readable summary report.
- **[INTEGRATION-01]**: Resolved via TASK-004. Implemented `pipeline/cms/excel_to_json.py` and `npm run cms:export` to convert Excel CMS workbooks back into canonical Universal Lesson JSON with relational grouping across all 6 sheets, placeholder normalization, and preview gate integration.
- **[SCHEMA-01]**: Resolved via ADR-002. Unified `.is_correct` across JS validation, models, preview renderer, sheets module, and tests. Implemented `validate(lesson, { allowUnresolved })`. Preview server enforces validation gate with dev-only guardrails for `--force`.
- **[TOOLING-01]**: Resolved. Updated `package.json` test runner to use cross-platform node executable path `node_modules/jest/bin/jest.js`.

## NEXT STEPS

1. Run offline catalog discovery (`npm run catalog:discover -- --offline`) to sync `source_catalog.json` with the newly cached HTML pages.
2. Execute offline parser (`pipeline/parser/test_english_parser.py`) across all 638 cached exercise pages.
3. Ingest parsed lessons into Excel CMS workbook.


## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Consult `docs/WORKFLOW.md` for task dispatch and return reporting conventions.
3. Inspect `docs/DECISIONS.md` for accepted ADRs (ADR-001, ADR-002, ADR-003).
4. Inspect relevant source files before proposing changes.
5. Run `npm test` (24/24 JS green) and `python -m unittest discover tests` (21/21 Python green) to verify regression baseline.
6. Follow the manual handoff checklist in `01-core.md`.