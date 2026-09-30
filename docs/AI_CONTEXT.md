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
   - *Note*: Operates independently; hardcoded default file paths point to user desktop in current scripts.

2. **JavaScript Core (`src/`)**: Runtime, Models & Presentation
   - Canonical content domain models (`src/models/index.js`).
   - Structural JSON validation (`src/validation/index.js`).
   - Local preview server and renderer (`src/preview/server.js`, `src/preview/renderer.js`) consuming standalone lesson JSON files (e.g., `data/json/L001.json`).
   - Google Sheets synchronization module (`src/sheets/`).
   - Architectural scaffolding for Test Engine, UI, admin, and analytics.

*Important*: A continuous end-to-end bridge from the Python pipeline's answered Excel CMS back into canonical JSON for the JS Preview/runtime does NOT yet exist.

## CURRENT TASK

TASK-001 (Modified) — Project orchestration and memory synchronization.

## COMPLETED

- Project workspace configured.
- Core AI orchestration rules defined (`.agents/rules/01-core.md`, `.agents/rules/02-ai-consultation.md`).
- External AI consultation skill established (`.agents/skills/consult/SKILL.md`).
- Baseline documentation established in `/docs`.
- Python ETL pipeline scripts implemented (collector, parser, sheets generator, Gemini processor, validators).
- JavaScript baseline implemented (models, parser adapter, preview renderer, sheets sync, validator).
- ADR-001 accepted (Orchestration architecture and documentation-based memory).

## KNOWN ISSUES (OPEN)

- **OPEN ISSUE [SCHEMA-01]**: Data contract mismatch between `src/models/index.js` (`Option.is_correct: boolean|null`) and `src/validation/index.js` / `tests/validation.test.js` (`opt.correct: boolean`). Causes 2 Jest validation tests to fail. Code changes deferred pending task assignment.
- **OPEN ISSUE [INTEGRATION-01]**: Missing link between Python Pipeline output (`english_cms_answered.xlsx`) and JavaScript preview/runtime. There is currently no script to export answered Excel CMS back into Universal JSON.
- **OPEN ISSUE [TOOLING-01]**: `package.json` test script references POSIX binary path (`node --experimental-vm-modules node_modules/.bin/jest`), causing execution errors under Windows PowerShell.

## IMPORTANT DECISIONS

- **ADR-001**: Antigravity is primary engineering orchestrator; persistent documentation in `/docs` is source of truth; external AI used for decision review.
- **Rule 12A**: Parsers must never set correct answers (`correct_answer=null`, `is_correct=null`). Correct answers are resolved strictly by AI Answer Processing or editorial review.

## NEXT STEPS

1. Finalize TASK-001 (orchestration alignment and multi-model workflow guidelines).
2. Resolve OPEN ISSUE [SCHEMA-01] (`is_correct vs correct`) in JavaScript validation and test suite.
3. Fix test execution script in `package.json` for cross-platform compatibility.
4. Implement CMS-to-JSON export bridge to connect Python pipeline outputs with JS Preview / Test Engine.

## HANDOFF NOTES

Handoff between AI models operates as a documentation-based protocol (there is no automated `/handoff` tool):
1. Consult `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md` first.
2. Inspect `docs/DECISIONS.md` before proposing architectural changes.
3. Check actual files before assuming implementation details.
4. Remember that Python Pipeline and JS Core are currently separate toolchains requiring integration.
5. Do not modify unresolved open issues without an explicit task assignment.