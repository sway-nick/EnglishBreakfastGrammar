# ARCHITECTURE

## OVERVIEW

The platform architecture is designed around two cooperating subsystems:

1. **Python Pipeline (`pipeline/`)**: Handles content acquisition, transformation, AI-assisted answer resolution, and dataset validation (offline ETL toolchain).
2. **JavaScript Core (`src/`)**: Provides canonical domain models, runtime validation, preview visualization, and the foundation for the interactive Test Engine.

Supporting directories include:
- `schemas/`: Shared data structure and validation schema definitions.
- `data/`: Inputs (`data/imports/`, `data/input/`), intermediate JSON (`data/json/`), processing logs (`data/logs/`), and generated outputs (`data/output/`).
- `tests/`: Automated unit and integration test suites.
- `docs/`: Persistent project documentation and memory.
- `.agents/rules/`: Agent orchestration rules.

---

## SUBSYSTEM ROLES & BOUNDARIES

### 1. Python Pipeline (`pipeline/`) — ETL & Data Processing

Responsible for offline batch processing and content preparation:

- **`pipeline/parser/` (`test_english_parser.py`)**:
  - Parses raw source HTML/text (e.g. WatuPRO/Test-English pages).
  - Extracts lesson metadata, exercise instructions, questions, gaps, and options.
  - Enforces **Rule 12A**: never marks correct answers during initial parsing (`correct_answer=null`, `is_correct=null`).

- **`pipeline/collector/` (`universal_collector.py`)**:
  - Aggregates multiple parsed pages into coherent lesson units.
  - Outputs `universal_lessons.json`.
  - *Current state note*: Uses default desktop path for outputs in current version.

- **`pipeline/cms/` (`google_sheets_generator.py`)**:
  - Converts raw JSON datasets into structured Excel/Sheets CMS files (`english_cms.xlsx`) for review and editing.

- **`pipeline/gemini/` (`gemini_answer_processor.py`, `prompt_builder.py`, `response_validator.py`, `excel_writer.py`)**:
  - Orchestrates automated batch processing of exercise questions via the Google Gemini API.
  - Uses structured JSON outputs (`response_json_schema`).
  - Isolates errors per question, verifies answers against option constraints, and writes answered exercises into output workbooks (`english_cms_answered.xlsx`).

- **`pipeline/validators/` (`universal_validator.py`, `cms_validator.py`)**:
  - Validates `universal_lessons.json` and CMS Excel files after generation and AI processing.

---

### 2. JavaScript Core (`src/`) — Models, Engine & Runtime

Responsible for application logic, runtime data integrity, and user-facing presentation:

- **`src/models/` (`index.js`)**:
  - Defines canonical JavaScript domain models: `Lesson`, `Exercise`, `Question`, `Gap`, `Option`.
  - Implements factory functions (`createLesson`, `createOption`, etc.) and ID generators (`IdCounter`).
  - Adheres to Rule 12A (`Option.is_correct`, `Gap.correct_answer`).

- **`src/validation/` (`index.js`)**:
  - Structured validation for universal lesson objects.
  - Performs bottom-up validation (Option -> Gap -> Question -> Exercise -> Lesson).
  - Emits non-destructive structured diagnostics (`ERROR`, `WARNING`, `INFO`).

- **`src/parser/` (`adapters/`, `BaseSourceAdapter.js`, `cli.js`)**:
  - Extensible JS adapter framework for alternative or direct source formats (e.g. `TestEnglishAdapter.js`).

- **`src/preview/` (`renderer.js`, `server.js`)**:
  - Renders lesson JSON into interactive HTML components for visual verification.
  - Runs a local lightweight preview HTTP server consuming individual JSON files (e.g. `data/json/L001.json`).

- **`src/sheets/` (`index.js`, `push.js`)**:
  - Handles synchronization and export directly to Google Sheets via Google APIs.

- **`src/test-engine/`, `src/ui/`, `src/admin/`, `src/analytics/`, `src/content/`, `src/firebase/`, `src/publish/`**:
  - Modular scaffolding for upcoming runtime test delivery, user session tracking, and publishing workflows.

---

## TARGET VS IMPLEMENTED DATA FLOW

The systems are currently **decoupled**: Python Pipeline and JS Core run independently, and an automated bridge converting the answered Excel CMS back into canonical JSON has not yet been built.

### Target End-to-End Flow:

```text
[Raw HTML / Source Files]
           │ (Implemented)
           ▼
[pipeline/parser (test_english_parser.py)]
           │ (Implemented)
           ▼
[pipeline/collector (universal_collector.py)] ──▶ [universal_lessons.json]
           │ (Implemented)                                  │
           ▼                                                ▼
[pipeline/cms (google_sheets_generator.py)]       [pipeline/validators (universal_validator.py)]
           │ (Implemented)
           ▼
[Excel CMS: english_cms.xlsx]
           │ (Implemented)
           ▼
[pipeline/gemini (gemini_answer_processor.py)] ──▶ [english_cms_answered.xlsx]
                                                               │ (Implemented)
                                                               ▼
                                                      [pipeline/validators (cms_validator.py)]
                                                               │
                                                               ░░ [MISSING BRIDGE: TASK-004] ░░
                                                               │
                                                               ▼
                                                  [Universal Final Lessons JSON]
                                                               │ (Partially implemented)
                                                               ▼
                                                      [src/validation]
                                                               │
                                                               ▼
                                                  [src/preview / Test Engine]
```

---

## ARCHITECTURAL CONSTRAINTS & OPEN ISSUES

### Rule 12A (Separation of Parsing and Answer Resolution)
Parsers must never establish correct answers. Raw content imports contain `correct_answer: null` and `is_correct: null`. The answer resolution is strictly the responsibility of AI Answer Processing or manual editorial CMS review.

### OPEN ISSUE [SCHEMA-01]: Data Contract Inconsistency
- In `src/models/index.js`, `Option` uses `is_correct: boolean|null`.
- In `src/validation/index.js` and `tests/validation.test.js`, validation checks `opt.correct`.
- This causes validation failures in Jest tests. Resolution is tracked under `TASK-002`.

### OPEN ISSUE [INTEGRATION-01]: Missing CMS-to-JSON Bridge
- Python Pipeline produces answered Excel workbooks (`english_cms_answered.xlsx`).
- JS Preview requires structured lesson JSON files.
- An automated exporter converting answered Excel CMS sheets back into validated canonical JSON is needed (tracked under `TASK-004`).