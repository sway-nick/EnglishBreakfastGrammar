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
2. **JavaScript Core (`src/`)**: Canonical domain models, structured JSON validation with strict and `allowUnresolved` modes (differentiating `GAP_SELECT` and `GAP_TEXT`), preview rendering with validation gate, Google Sheets sync, and automated test suite (24/24 JS Jest tests green, 32/32 Python unit tests green).

The end-to-end data bridge connecting answered/draft Excel CMS workbooks back into canonical JSON for the JavaScript preview/runtime was completed and verified under `TASK-004`. Real export of `english_cms.xlsx` achieves 0 structural validation errors in draft mode (`allowUnresolved: true`).
Source taxonomy discovery across all 7 levels and 225 topics was completed under `TASK-005`.
Full authorized content acquisition across all 225 topics and 7 levels (638 unique exercise HTML pages, 646 total files, ~206.9 MB cached in `data/cache/html` with 0 failures and 0 challenges) was completed under `TASK-006` / `ADR-003`. Checkpoint recorded in `docs/ACQUISITION_CHECKPOINT_2026-09-30.md`.
Full offline parsing across all 638 exercise pages into preliminary Universal JSON and Excel CMS workbooks was completed under `TASK-007`.
Full corpus staging import into relational SQLite database `data/staging.db` with strict foreign key integrity and zero duplicates was completed under `TASK-008` (225 topics, 638 exercises, 5,796 questions, 4,733 gaps, 13,052 options).
Full corpus answer enrichment and staging import for all remaining 5,614 questions from the evaluated Gemini workbook was completed under `TASK-009D`. All 5,796 questions, 4,733 gaps, and 13,052 options in `data/staging.db` are now 100% answered and verified with 0 unresolved questions remaining.

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

Full-corpus orchestrator (`pipeline/adaptation/full_corpus_orchestrator.py`) is implemented and verified. Pilot statuses normalized to 188 VALIDATED, 12 REVIEW_REQUIRED. 25-question dry run completed and verified (18 VALIDATED, 7 REVIEW_REQUIRED, 0 REJECTED, 100% answers preserved, Preview Gate PASSED). Ready for full-corpus production batches (TASK-013).

## CURRENT TASK

TASK-012 — Full-Corpus Adaptation Orchestrator & Dry Run.

Status: completed

## NEXT TASK

TASK-013 — Full-Corpus Adaptation Batch Generation (Production batches for remaining 5,571 PENDING questions).

## OPEN ISSUES

None. Staging corpus (5,796 questions) is 100% immutable and intact. Adaptation database holds 5,796 questions: 5,571 PENDING, 19 REVIEW_REQUIRED, 206 VALIDATED, 0 REJECTED. Multi-tier validation pipeline and Preview Gate verified. Full test suite (97 Python tests + 24 JS tests = 121 total) passing.

## RESOLVED ISSUES

- **[EXPORT-01]**: Resolved via TASK-010A. Full semantic and referential validation passed with 0 errors across 5,796 questions. Exported `english_cms_final_enriched.xlsx` and `universal_lessons_final_enriched.json` (local and Desktop). Passed `npm run cms:validate`, `npm run validate` (strict), Preview Gate (225/225 lessons), 43 Python tests, and 24 JS tests.
- **[ENRICHMENT-02]**: Resolved via TASK-009D. Imported all 5,614 Gemini enrichment results into `data/staging.db` (`pipeline/staging/import_enrichment_results.py`, `npm run staging:import-results`). 0 unanswered questions, 0 unanswered gaps, 0 unanswered options remain in staging. Existing 182 checkpoint questions verified untouched.
- **[ENRICHMENT-01]**: Resolved via TASK-009B. Prepared and validated `english_cms_gemini_remaining_5614.xlsx` containing all 5,614 unresolved questions with tailored prompt formulas (gap=3,522, single_choice=1,927, multiple_choice=165; 0 errors).
- **[CHECKPOINT-01]**: Resolved via TASK-009A. Merged 182 verified Gemini question answers into `data/staging.db` (224 gaps, 258 options answered; 0 errors, 0 scope violations).
- **[STAGING-01]**: Resolved via TASK-008. Staged all 225 topics, 638 exercises, 5,796 questions, 4,733 gaps, and 13,052 options in `data/staging.db` with strict foreign key constraints and zero orphaned records.
- **[PARSER-01]**: Resolved via TASK-007. Extended parser with full `multiple_choice` support; 0 unknown response models across entire corpus.
- **[ACQUISITION-01]**: Resolved via TASK-006 / ADR-003. Full browser-assisted acquisition completed via Remote CDP across all 7 levels (225/225 topics, 638 exercise pages, 646 total HTML files, 206.9 MB cache, 0 challenges, 0 failures).
- **[CATALOG-01]**: Resolved via TASK-005. Complete source taxonomy of 7 levels and 225 topics mapped into canonical `data/catalog/source_catalog.json` and human-readable summary report.
- **[INTEGRATION-01]**: Resolved via TASK-004. Implemented `pipeline/cms/excel_to_json.py` and `npm run cms:export` to convert Excel CMS workbooks back into canonical Universal Lesson JSON with relational grouping across all 6 sheets, placeholder normalization, and preview gate integration.
- **[SCHEMA-01]**: Resolved via ADR-002. Unified `.is_correct` across JS validation, models, preview renderer, sheets module, and tests. Implemented `validate(lesson, { allowUnresolved })`. Preview server enforces validation gate with dev-only guardrails for `--force`.
- **[TOOLING-01]**: Resolved. Updated `package.json` test runner to use cross-platform node executable path `node_modules/jest/bin/jest.js`.

## NEXT STEPS

1. Execute answer generation in Google Sheets or via batch processor for the 5,614 questions.
2. Merge results into `data/staging.db` using atomic transaction.
3. Validate enriched content through strict Universal JSON and Preview Gate.

## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Consult `docs/WORKFLOW.md` for task dispatch and return reporting conventions.
3. Inspect `docs/DECISIONS.md` for accepted ADRs (ADR-001, ADR-002, ADR-003).
4. Inspect relevant source files before proposing changes.
5. Run `npm test` (24/24 JS green) and `python -m unittest discover tests` (37/37 Python green) to verify regression baseline.
6. Follow the manual handoff checklist in `01-core.md`.