---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK
 
TASK-007 — Offline Parser Batch Execution & CMS Ingestion across Cached Corpus
 
Status: in_progress
 
## OBJECTIVE
 
Execute offline parsing on all 638 cached Test-English exercise HTML pages without any external network calls.
Extract lesson content, grammar rules, exercises, questions, gaps, and options into structured lesson JSON and ingest into the Excel CMS workbook.
 
---
 
## COMPLETED RECENT TASKS
 
### TASK-006 — Full Test-English Content Acquisition via Remote CDP
Status: completed
- Acquired all 225 topics across all 7 levels (`a1`, `a2`, `b1`, `b1-b2`, `b2`, `c1`, `shorts`) using `pipeline/acquisition/browser_collector.py` via Remote CDP (`http://127.0.0.1:9222`).
- Saved 638 unique exercise HTML pages and 8 category/index pages (646 total HTML files, ~206.9 MB) in local cache `data/cache/html`.
- Generated audit manifest `data/cache/acquisition_manifest.json` with 646/646 `success` entries (SHA-256 integrity, valid content checks).
- 0 failures, 0 partial topics remaining, 0 Cloudflare challenges detected.
- Hardened `browser_collector.py`: fixed Chromium 115+ `/json/new` target creation (`PUT` method) and implemented CDP message ID event filtering.
- Preserved existing 182-question Gemini checkpoint workbook and `english_cms.xlsx` untouched.
- Checkpoint documented in `docs/ACQUISITION_CHECKPOINT_2026-09-30.md`.
- Automated test regression: 21/21 Python tests PASS, 24/24 JS Jest tests PASS.
 
### TASK-005 — Source Catalog Discovery
Status: completed
- Created `pipeline/catalog/source_catalog_builder.py` and unit tests in `tests/test_source_catalog.py`.
- Added npm script `"catalog:discover": "python pipeline/catalog/source_catalog_builder.py"` to `package.json`.
- Discovered complete taxonomy across all 7 levels (`a1`, `a2`, `b1`, `b1-b2`, `b2`, `c1`, `shorts`) yielding 225 total topics.
- Discovered exercise pagination via `.page-links` container; 6 cached topics in A1 confirmed with multi-page exercises (20 exercises total).
- Gracefully handled Cloudflare HTTP 403 on uncached URLs via fallback: marked topics with explicit `discovery_status: "partial"`, preserving topic seed URLs for downstream resolution.
- Dynamically calculated all catalog statistics: `total_levels: 7`, `total_topics: 225`, `total_exercises: 239`, `topics_complete: 6`, `topics_partial: 219`, `network_errors: 219`.
- Exported canonical JSON catalog `data/catalog/source_catalog.json` and human-readable `data/catalog/source_catalog_summary.md`.
- Formalized ADR-003 (Acquisition boundary + persisted local HTML cache + offline parsing; core platform remains browser/session free).
- Verified with automated tests: 10/10 Python unit tests PASS, 24/24 JS Jest tests PASS.

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