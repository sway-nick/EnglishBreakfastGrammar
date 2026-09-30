---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

TASK-011H — Apply AI-Review Revisions to Pilot

Status: completed

## OBJECTIVE

Awaiting human review / final approval on the pilot adaptation run (100% semantic approval across audited sample) before commencing full-corpus adaptation planning.

---

## COMPLETED RECENT TASKS

### TASK-011H — Apply AI-Review Revisions to Pilot
Status: completed
- Revised only the 2 pilot questions identified with issues in TASK-011G:
  - **QID 4203** (`quiz-481`, `single_choice`): Replaced shallow rewrite (`"1 My cousin is taller than _____."`) with a completely independent storm travel scenario and fronted prepositional adverbial structure (`"1 During the heavy storm, all the other passengers were far calmer than _____."`). Grammar target preserved (comparative adjective + object pronoun after 'than'). Correct answer preserved (`"me"`), distractors preserved (`"me", "mine", "my"`). Jaccard=0.0, Shingle=0.0, Levenshtein=0.2794. Evaluator: `VALIDATED`.
  - **QID 4211** (`quiz-481`, `single_choice`): Replaced pedagogical mismatch and shallow rewrite (`"9 Julia is _____ than her classmate."` with `polite -> politer`) with canonical consonant + `-y` -> `-ier` spelling rule (`"9 During the lunch break, the school cafeteria is always far _____ than the library."`). Options: `noisy | noisier [CORRECT] | more noisier`. Jaccard=0.0769, Shingle=0.0, Levenshtein=0.2297. Evaluator: `VALIDATED`.
- Staging corpus (`data/staging.db`) verified 100% immutable and unmodified.
- No other pilot questions modified.
- Database integrity: 0 foreign key violations, 0 orphans.
- Preview Gate passed: 12/12 lessons valid, 12/12 passed gate.
- Re-executed AI semantic review: 34/34 APPROVE (100.0%), 0 REVISE, 0 REJECT.
- Regression test suite: 82/82 Python unittests green, 24/24 Jest JS tests green (106 total).
- Implemented `pipeline/adaptation/semantic_reviewer.py` (`npm run adaptation:semantic-review`).
- Executed comprehensive semantic, pedagogical, and quality audit across 34 questions:
  - All 14 `REVIEW_REQUIRED` items from calibrated evaluator;
  - Deterministic control sample of 20 `VALIDATED` items (ordered by stable source_question_id).
- Evaluated 4 major dimensions per question: Grammar-target preservation, Answer integrity, Originality, Quality.
- Decisions:
  - `APPROVE`: 32 questions (94.1%)
  - `REVISE`: 2 questions (5.9%) — QID 4203 (shallow rewrite) and QID 4211 (pedagogical mismatch on canonical '-y -> -ier' rule and shallow rewrite)
  - `REJECT`: 0 questions (0.0%)
- Sub-group outcomes:
  - `REVIEW_REQUIRED` (14 Qs): 12 APPROVE, 2 REVISE, 0 REJECT.
  - `VALIDATED_CONTROL` (20 Qs): 20 APPROVE, 0 REVISE, 0 REJECT (0 false acceptances by calibrated deterministic evaluator).
- Persisted results into `data/adaptation/semantic_review_pilot_34.json` and isolated SQLite table `pilot_semantic_reviews` in `data/adaptation.db` (original adaptation tables remain unmodified).
- Added comprehensive unit tests in `tests/test_semantic_reviewer.py` (5 tests).
- Total tests: 82/82 Python tests green, 24/24 JS Jest tests green (106 total).

### TASK-011E — Calibrate Originality Evaluator for Short Grammar Items
Status: completed
- Calibrated `pipeline/adaptation/similarity_evaluator.py`:
  - Rule 1: For very short text (<40 chars after normalization), Levenshtein similarity alone MUST NOT cause `REVIEW_REQUIRED`.
  - Rule 2: Normalizes/removes non-semantic dialogue scaffolding (speaker labels `A:`, `B:`, quotes, formatting instructions `Choose TWO correct answers`, redundant punctuation `⇒`, `->`, `_____`) prior to Levenshtein distance calculation.
  - Rule 3 & 5: Preserved primary originality signals: forbidden 3+ word non-target shingle detector (unconditional `REJECTED`), Jaccard token similarity (> 0.50 `REJECTED`, 0.40–0.50 `REVIEW_REQUIRED`).
  - Rule 4: Levenshtein secondary diagnostic role: on standard text (len >= 40 chars), Levenshtein >= 0.45 triggers review; on short text (<40 chars), Levenshtein >= 0.45 triggers review only when combined with elevated token similarity (Jaccard >= 0.25).
- Expanded `tests/test_similarity_evaluator.py` with 7 dedicated test suites covering: short article exercises, short irregular plural exercises, short preposition exercises, short dialogue exercises, legitimate short rewrites, genuinely similar short texts, and existing strict rejection cases (16 tests total).
- Re-evaluated the SAME 200 pilot questions without regenerating content or modifying source:
  - Old: 125 VALIDATED, 75 REVIEW_REQUIRED, 0 REJECTED
  - New: 186 VALIDATED (93.0%), 14 REVIEW_REQUIRED (7.0%), 0 REJECTED (0.0%)
  - 61 items transitioned from `REVIEW_REQUIRED -> VALIDATED` (all verified genuine pedagogical rewrites).
  - 0 items incorrectly accepted.
  - 14 items legitimately remain in `REVIEW_REQUIRED` for human review (4 sentence scrambles, 3 comparative templates, 2 plural templates, 5 borderline short phrases).
- Total tests: 77/77 Python tests green, 24/24 JS Jest tests green (101 total).

### TASK-011D — Human Review Report for Pilot Adaptation
Status: completed
- Implemented `pipeline/adaptation/review_report_builder.py` (`npm run adaptation:review`).
- Built the human-review Excel workbook at `data/adaptation/pilot_review_20260930.xlsx` (mirrored to `C:\Users\user\Desktop\pilot_review_20260930.xlsx`).
- Structured 3 comprehensive sheets:
  1. `Summary`: Executive status overview (200 total, 125 VALIDATED [62.5%], 75 REVIEW_REQUIRED [37.5%], 0 REJECTED [0.0%]), grouped reasons for review, metric distribution quantiles (Jaccard, Shingles, Levenshtein), response model and CEFR level breakdowns, complete 20-exercise portfolio, and linguistic review guidance.
  2. `Review_Required_75`: Dedicated sheet containing exclusively the 75 flagged items.
  3. `All_Pilot_Questions_200`: All 200 questions sorted with `REVIEW_REQUIRED` first (rows 2-76), followed by `VALIDATED` (rows 77-201).
- Enforced all 17 required columns per row with full question, option, gap, answer, and evaluator reason traceability.
- Confirmed zero plagiarism / zero copy-pastes across all 200 questions (0.0000 shingle overlap).
- Root-cause analyzed the 75 flagged items: 100% triggered by Rule 3 (Normalized Levenshtein similarity >= 0.45) due to short sentence lengths, morphological conversion pairs, and dialogue scaffolds rather than unoriginal content.
- Added comprehensive unit tests in `tests/test_review_report_builder.py` (5 tests).
- Total tests: 70/70 Python tests green, 24/24 JS Jest tests green (94 total).

### TASK-011C — Pilot Content Adaptation Generation
Status: completed
- Curated and generated 20 pilot exercises (200 questions, 90 gaps, 493 options) across 11 distinct grammar topics (A1 + A2).
- Represented all three response models: `multiple_choice` (7 Qs, 2 correct options each), `single_choice` (103 Qs), `gap` (90 Qs: 50 select, 40 text).
- Executed strict anti-plagiarism and originality checks via `pipeline/adaptation/similarity_evaluator.py`:
  - `VALIDATED`: 125 questions (62.5%)
  - `REVIEW_REQUIRED`: 75 questions (37.5%, flagged due to normalized Levenshtein ratios on short phrases/grammatical formulas; Jaccard <= 0.40, 0 forbidden shingles)
  - `REJECTED`: 0 questions (0.0%)
- Preserved strict relational and structural invariants in `data/adaptation.db` (`run_id="pilot_run_20260930_20ex"`):
  - 0 foreign key violations, 0 orphans, 0 unmatched source IDs.
- Validated via JS Domain Validator and Preview Gate (`src/preview/server.js`):
  - 12/12 adapted lessons valid, 0 errors, 12/12 passed Preview Gate (0 blocked).
- Added comprehensive unit tests in `tests/test_pilot_generator.py` (5 tests).
- Total tests: 65/65 Python tests green, 24/24 JS Jest tests green (89 total).

### TASK-011B — Implement Adaptation Database & Queue Manager
Status: completed
- Implemented `pipeline/adaptation/adaptation_db.py` (`npm run adaptation:db`) and DDL runner for `schemas/adaptation_schema.sql`.
- Initialized `data/adaptation.db` with strict `PRAGMA foreign_keys = ON;`.
- Populated queue from immutable `data/staging.db` with 100% idempotency (re-running skips existing rows with 0 duplicates):
  - 225 lessons (all PENDING)
  - 638 exercises (all PENDING)
  - 5,796 questions (all PENDING)
  - 4,733 gaps (all PENDING)
  - 13,052 options (all PENDING)
- Validated referential integrity: 0 foreign key violations, 0 orphan records, 0 unmatched source IDs, 0 duplicate question mappings.
- Added comprehensive unit test suite in `tests/test_adaptation_db.py` (7 tests).
- Total tests: 60/60 Python tests green, 24/24 JS Jest tests green (84 total).

### TASK-011A — Implement Originality / Similarity Evaluator
Status: completed
- Implemented `pipeline/adaptation/similarity_evaluator.py`:
  - Jaccard token similarity with grammar target token exclusions;
  - N-gram shingle overlap detector for verbatim sequences >= 3 significant consecutive words;
  - Levenshtein distance ratio;
  - Deterministic status assignment (`VALIDATED`, `REVIEW_REQUIRED`, `REJECTED`).
- Added unit tests in `tests/test_similarity_evaluator.py` (9 tests).

### TASK-010B — Adaptation Specification & Relational Schema Design
Status: completed
- Formulated comprehensive architectural specification in `docs/TASK-010B_ADAPTATION_SPEC.md`.
- Authored production-ready DDL schema in `schemas/adaptation_schema.sql` (6 tables, 11 indexes).
- Added schema tests in `tests/test_adaptation_schema.py` (4 tests).

### TASK-010A — Final Answer Validation & CMS Export
Status: completed
- Executed full semantic, relational, and checkpoint validation of `data/staging.db` via `pipeline/staging/validate_staging_corpus.py` (`npm run corpus:validate`):
  - 5,796 questions (100% answered, 0 unanswered)
  - 4,733 gaps (100% answered, 0 unanswered)
  - 13,052 options (100% resolved, 0 unanswered)
  - 1,927 `single_choice` (0 violations; exactly 1 correct option each)
  - 165 `multiple_choice` (0 violations; >= 1 correct options each, specifically 2)
  - 3,522 `gap` questions (0 violations; 100% canonical answers present in accepted_answers, select options matched)
  - 0 orphan questions, gaps, or options
  - 0 suspicious answers
  - 0 checkpoint discrepancies against original 182-question verified baseline
  - 0 validation errors
- Exported production-ready CMS workbooks via `pipeline/export/export_enriched_corpus.py` (`npm run corpus:export`):
  - `data/cms/english_cms_final_enriched.xlsx` (1,139,315 bytes)
  - `C:\Users\user\Desktop\english_cms_final_enriched.xlsx` (1,139,378 bytes)
- Exported canonical Universal Lesson JSON:
  - `data/cms/universal_lessons_final_enriched.json` (7,487,752 bytes)
  - `C:\Users\user\Desktop\universal_lessons_final_enriched.json` (7,487,752 bytes)
- Executed full validation and verification suite:
  - `npm run cms:validate`: 0 errors across all 12 checks (225 lessons, 638 exercises, 5,796 questions, 4,733 gaps, 13,052 options)
  - Strict JS validation (`npm run validate` / `src/validation/cli.js`): 225/225 lessons valid, 0 errors
  - Preview Gate (`src/preview/server.js`): 225/225 lessons evaluated, 0 blocked
  - Test suites: 43/43 Python tests PASS, 24/24 JS Jest tests PASS (67 tests total)

### TASK-009D — Import Full Gemini Enrichment Results
Status: completed
- Created `pipeline/staging/import_enrichment_results.py` (`npm run staging:import-results`) to import evaluated answers from `C:\Users\user\Desktop\english_cms_gemini_remaining_5614 (3).xlsx`.
- Preserved desktop file untouched and archived project copy at `data/gemini/english_cms_gemini_remaining_5614_evaluated.xlsx`.
- Merged answers into `data/staging.db` inside an atomic SQLite transaction with full rollback on error and strict validation.
- Preserved existing 182-question checkpoint answers completely untouched (0 changes, verified by byte and content assertions).
- Successfully imported and mapped all 5,614 remaining questions:
  - `single_choice`: 1,927 questions (100% matched to exactly 1 correct option)
  - `multiple_choice`: 165 questions (100% matched to at least 1 correct option, specifically 2 correct options)
  - `gap`: 3,522 questions (4,509 gaps populated with `correct_answer` and `accepted_answers`, select options marked)
- Database metrics after commit:
  - Total questions in staging: 5,796
  - Total answered questions: 5,796 (100%)
  - Remaining unanswered questions: 0
  - Total gaps in staging: 4,733 (100% answered, 0 remaining)
  - Total options in staging: 13,052 (100% resolved, 0 remaining)
  - Single choice violations (!= 1 correct): 0
  - Multiple choice violations (< 1 correct): 0
  - Validation errors: 0
- Added automated test suite `tests/test_import_enrichment_results.py` (40/40 Python tests PASS, 24/24 JS Jest tests PASS).

### TASK-009B — Prepare Full Gemini Enrichment Workbook
Status: completed
- Created `pipeline/gemini/enrichment_workbook_builder.py` (`npm run gemini:workbook`) to query all 5,614 currently unresolved questions from `data/staging.db`.
- Strictly excluded all 182 already-answered checkpoint questions (224 gaps, 258 options).
- Populated full context: `question_id`, `exercise_id`, `lesson_id`, `order`, `response_model`, `instruction`, `sentence`, `options_context`, `gemini_formula`, and `gemini_raw_values`.
- Tailored strict JSON output prompts for all 3 models:
  - `gap`: 3,522 rows (mapping gap IDs to exact option strings)
  - `single_choice`: 1,927 rows (`{"answer":"..."}`)
  - `multiple_choice`: 165 rows (`{"answers":["...", "..."]}`)
- Added `README` guide sheet with upload, formula evaluation, value freeze, and download steps.
- Generated output workbooks:
  - Desktop: `C:\Users\user\Desktop\english_cms_gemini_remaining_5614.xlsx` (591,101 bytes)
  - Project: `data/gemini/english_cms_gemini_remaining_5614.xlsx` (591,101 bytes)
- Enforced strict pre- and post-write assertions:
  - Exactly 5,614 rows (0 duplicate QIDs, 0 already-answered questions, 0 empty sentences)
  - 0 validation errors
- Added automated test suite `tests/test_enrichment_workbook.py` (37/37 Python tests PASS, 24/24 JS Jest tests PASS).

### TASK-009A — Merge Existing Gemini Checkpoint into Staging
Status: completed
- Merged the verified 182-question Gemini answers from `english_cms_gemini_all_182.xlsx` into `data/staging.db` using `pipeline/staging/merge_checkpoint.py` (`npm run staging:merge`).
- Executed inside an atomic SQLite transaction with full rollback on error and strict validation.
- Preserved 100% of stable IDs without altering question text, options, gaps, or explanations.
- Verified 0 changes outside the 182-question scope:
  - Checkpoint questions: 182 / 182 matched (0 unmatched)
  - Answered gaps: 224 (populated `correct_answer` and `accepted_answers`)
  - Answered options: 258 (set `is_correct` 1/0)
  - Remaining unanswered questions: 5,614
  - Remaining unanswered gaps: 4,509
  - Remaining unanswered options: 12,794
  - Validation errors: 0
- Added automated test suite `tests/test_merge_checkpoint.py` (35/35 Python tests PASS, 24/24 JS Jest tests PASS).

### TASK-008 — Full Corpus Staging Import
Status: completed
- Created minimal relational staging schema `schemas/staging_schema.sql` with strict foreign key constraints (`PRAGMA foreign_keys = ON;`), primary keys, and explicit status isolation (`status = 'staging'`).
- Implemented `pipeline/staging/staging_importer.py` (`npm run staging:import`) with automated transaction management and post-import verification assertions.
- Successfully imported the entire preliminary dataset from `data/cms/universal_lessons_preliminary.json` into SQLite staging database `data/staging.db`.
- Preserved all stable IDs, response models, and counts:
  - 225 / 225 topics represented (100%)
  - 638 / 638 exercises represented (100%)
  - 5,796 / 5,796 questions represented (100%)
  - 4,733 / 4,733 gaps represented (100%)
  - 13,052 / 13,052 options represented (100%)
  - response_models: gap=3,674, single_choice=1,957, multiple_choice=165
  - zero duplicate IDs (0)
  - zero orphaned references across all relational tables (0)
  - unresolved answers preserved per Rule 12A (17,785 NULL answers)
- Added automated test suite `tests/test_staging_import.py` (32/32 Python tests PASS, 24/24 JS Jest tests PASS).

### TASK-007 — Full Offline Parser Batch Execution & Preliminary CMS Generation
Status: completed
- Executed offline parsing on all 638 cached Test-English exercise HTML pages without any external network calls.
- Extended `pipeline/parser/test_english_parser.py` with full `multiple_choice` (checkbox) support, eliminating all unknown response models.
- Implemented `pipeline/collector/batch_corpus_processor.py` generating canonical preliminary dataset:
  - `data/cms/universal_lessons_preliminary.json` (and Desktop copy)
  - `data/cms/english_cms_preliminary.xlsx` (and Desktop copy)
- Preserved existing `english_cms.xlsx` and `english_cms_gemini_all_182.xlsx` untouched.
- Added parser unit tests in `tests/test_parser.py`.

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