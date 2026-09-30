---
trigger: always_on
---

# AI PROJECT CONTEXT

## PROJECT

Name: Universal English Test Platform

Workspace: English Breakfast Grammar

## PURPOSE

A platform for creating, processing, storing, and delivering English grammar tests and exercises.

The project supports structured lesson content, questions, options, explanations, automated answer processing with AI, validation, and export/import workflows.

## CURRENT ARCHITECTURE & ROLES

The codebase currently contains two largely independent subsystems:

1. **Python Pipeline (`pipeline/`)**: ETL & Data Processing (Offline Toolchain)
   - Parses source HTML pages (Test-English / WatuPRO).
   - Collects parsed pages into `universal_lessons.json`.
   - Generates Excel CMS workbooks (`google_sheets_generator.py`).
   - Fills question answers using Gemini API (`gemini_answer_processor.py`) into `english_cms_answered.xlsx`.
   - Validates JSON and CMS Excel workbooks.
   - *Note*: Operates independently; default file paths point to user desktop in current scripts.

2. **JavaScript Core (`src/`)**: Runtime, Models & Presentation
   - Canonical content domain models (`src/models/index.js`).
   - Structural JSON validation (`src/validation/index.js`) supporting strict validation and `allowUnresolved` mode (Rule 12A).
   - Local preview server and renderer (`src/preview/server.js`, `src/preview/renderer.js`) with an explicit validation gate before server startup.
   - Google Sheets synchronization module (`src/sheets/`).
   - Architectural scaffolding for Test Engine, UI, admin, and analytics.

*Data Bridge*: The end-to-end bridge from Excel CMS workbooks back into canonical JSON for the JS Preview/runtime is implemented in `pipeline/cms/excel_to_json.py` (`npm run cms:export`) under `TASK-004`.

## CURRENT TASK

None (TASK-004 completed).

## COMPLETED

- Project workspace configured.
- Core AI orchestration rules defined (`.agents/rules/01-core.md`, `.agents/rules/02-ai-consultation.md`).
- External AI consultation skill established (`.agents/skills/consult/SKILL.md`).
- Baseline documentation established in `/docs`.
- Python ETL pipeline scripts implemented (collector, parser, sheets generator, Gemini processor, validators).
- JavaScript baseline implemented (models, parser adapter, preview renderer, sheets sync, validator).
- ADR-001 accepted (Orchestration architecture and documentation-based memory).
- ADR-002 accepted (Explicit validation modes & `is_correct` contract unification across JS core).
- TASK-002 completed: Unified `.is_correct` across JS validation, preview, sheets, and tests; implemented `allowUnresolved` mode.
- TASK-003 completed: Cross-platform npm test runner configured in `package.json` (20/20 tests passing).
- TASK-001 completed: Multi-model operational workflow, model selection matrix, and dispatch/return templates defined in `docs/WORKFLOW.md`.
- TASK-004 completed: CMS-to-JSON export bridge (`pipeline/cms/excel_to_json.py`, `npm run cms:export`), 24/24 JS and 4/4 Python tests passing.

## KNOWN ISSUES (OPEN)

- None currently blocking. [INTEGRATION-01] resolved via `TASK-004`.

## IMPORTANT DECISIONS

- **ADR-001**: Antigravity is primary engineering orchestrator; persistent documentation in `/docs` is source of truth; external AI used for decision review.
- **ADR-002**: Standardize on `is_correct` across JS; `validate(lesson, { allowUnresolved })` provides strict mode (default) and draft import mode; preview server enforces an explicit validation gate.
- **Rule 12A**: Parsers must never set correct answers (`correct_answer=null`, `is_correct=null`). Correct answers are resolved strictly by AI Answer Processing or editorial review.

## NEXT STEPS

1. Define next task from project roadmap.

## HANDOFF NOTES

Handoff between AI models operates as a documentation-based protocol:
1. Consult `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md` first.
2. Read `docs/WORKFLOW.md` for task dispatch and return reporting conventions.
3. Inspect `docs/DECISIONS.md` before proposing architectural changes.
4. Check actual files before assuming implementation details.
5. All 20 tests in JS test suite (`npm test`) are green and must remain green after changes.