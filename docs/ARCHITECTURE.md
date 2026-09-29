# ARCHITECTURE

## OVERVIEW

The project is organized into several major areas:

- `src/` — application source code
- `pipeline/` — processing and data pipeline components
- `schemas/` — schema definitions
- `data/` — project data, imports, outputs, logs, and JSON files
- `tests/` — automated tests
- `docs/` — project documentation
- `.agents/rules/` — Antigravity agent rules

The exact runtime architecture and dependencies must be verified from the actual source files and configuration.

---

## SOURCE STRUCTURE

### `src/`

Current top-level modules:

- `admin/`
- `analytics/`
- `content/`
- `firebase/`
- `models/`
- `parser/`
- `preview/`
- `publish/`
- `sheets/`
- `test-engine/`
- `ui/`
- `validation/`

The names suggest separation by responsibility, but the exact responsibilities and dependencies must be confirmed by inspecting the source code.

### `pipeline/`

Current top-level modules:

- `cms/`
- `collector/`
- `gemini/`
- `parser/`
- `validators/`

These modules appear to represent data collection, AI-related processing, parsing, CMS processing, and validation stages.

Their exact data flow and dependencies require verification.

### `schemas/`

Contains project schema definitions.

The exact schemas, formats, and consumers must be documented after inspection.

### `data/`

Current areas include:

- `imports/`
- `input/`
- `json/`
- `logs/`
- `output/`

These directories represent project data inputs, intermediate/generated JSON data, logs, and outputs.

Exact ownership and lifecycle of each data type must be verified.

### `tests/`

Current test structure includes:

- `validation.test.js`

Additional tests may exist elsewhere.

---

## KNOWN DATA FLOW

A complete end-to-end data flow has not yet been verified.

Potential processing stages suggested by the current directory structure include:

```text
Input
  ↓
Collection / Import
  ↓
Parsing
  ↓
Validation
  ↓
Transformation / Processing
  ↓
Storage / Export / Publishing