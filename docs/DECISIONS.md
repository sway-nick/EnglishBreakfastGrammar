# ARCHITECTURAL DECISIONS

---

# ADR-001

## Status

accepted

## Date

2026-09-29

## Context

The project is developed with multiple AI models and conversations.

Different models may work on the same project, so project continuity cannot depend on conversation history.

We need a stable mechanism for project memory, AI handoff, architectural decisions, and efficient use of AI context.

## Decision

Use the following project workflow:

- Antigravity acts as the primary engineering orchestrator.
- Claude and Gemini may act as implementation-focused AI models.
- External ChatGPT Thinking may be used as an architecture and decision reviewer for significant or uncertain decisions.
- Project files and documentation are the source of persistent project context.
- `.agents/rules/01-core.md` contains the permanent orchestration rules.
- `.agents/rules/02-ai-consultation.md` contains the rules for external AI consultation.
- `docs/AI_CONTEXT.md` contains the short current project context.
- `docs/DECISIONS.md` stores important architectural decisions as ADRs.
- Git stores the history of project changes.

## Reason

This reduces dependence on long conversations, makes model switching safer, and minimizes unnecessary AI context.

## Alternatives Rejected

### Conversation-only memory

Rejected because another AI model cannot reliably reconstruct the full project state from previous conversation history.

### Sending the entire project to external AI

Rejected because it creates unnecessary context, increases cost, and exposes information that may not be relevant to the decision.

## Consequences

### Positive

- Better continuity between AI models.
- Smaller AI context.
- Explicit architectural history.
- Easier handoff between agents.
-状态- More controlled use of external AI.

### Negative

- Important project state must be kept updated.
- Significant decisions require documentation.
- Incorrect documentation can become a source of confusion.

## Evidence

Initial project orchestration design agreed during project setup.

## Supersedes

None.

---

# ADR-002

## Status

accepted

## Date

2026-09-30

## Context

The project had a data contract discrepancy:
- `src/models/index.js` defines `Option.is_correct: boolean|null` under Rule 12A (raw imported content legitimately has `null` pending AI answer processing).
- `src/validation/index.js`, `src/preview/renderer.js`, `src/sheets/index.js`, and `tests/validation.test.js` checked `opt.correct` as boolean.
- Automated tests failed because passing canonical `Option` models resulted in undefined correctness flags.
- An architectural check of the project revealed that `ContentStatus` is currently a passive metadata property without enforcement logic or lifecycle state machines, and cannot serve as an authoritative validation gate.

## Decision

1. Standardize property naming on `is_correct` across the entire JavaScript codebase (`models`, `validation`, `preview`, `sheets`, `tests`).
2. Implement explicit validation options: `validate(lesson, { allowUnresolved = false } = {})`.
3. Strict mode (`allowUnresolved: false`, default): `is_correct` must be boolean, and every gap / choice question must have at least one correct answer.
4. Import mode (`allowUnresolved: true`): `is_correct: null` is permitted without emitting fatal errors (emits `INFO` issue `GAP_UNRESOLVED_ANSWERS` / `QUESTION_UNRESOLVED_ANSWERS`), accommodating Rule 12A raw imports awaiting AI answer processing.
5. In `src/preview/server.js`, implement an explicit validation gate (`checkPreviewGate()`).
6. Enforce strict semantic boundaries between `allowUnresolved` and `--force`:
   - `allowUnresolved`: authorized domain validation mode for drafts/Rule 12A; structural errors (missing IDs, duplicate options, placeholder mismatches) remain fatal.
   - `--force`: strictly a local developer/debugging escape hatch; outputs a loud security/integrity warning; prohibited in publish or automated runtime delivery workflows.

## Reason

Decouples validation rigor from passive metadata fields, avoids silent validation bypasses, adheres to Rule 12A, and provides a deterministic contract for runtime and preview engines while isolating developer escape hatches.

## Alternatives Rejected

### Option A (Unconditional null allowance)

Rejected because it permanently relaxes correctness checks, allowing content without correct answers to pass validation into preview and runtime.

### Option B (Implicit reliance on ContentStatus)

Rejected because `ContentStatus` is not an authoritative lifecycle boundary in the current code; default status `'draft'` would quietly disable correctness validation.

## Consequences

### Positive

- Unified data model across Python ETL, JS domain models, and JS validation.
- All unit and integration tests pass deterministically (20/20 passing).
- Explicit caller control over validation strictness.
- Preview server gains an explicit, automated validation gate.
- Clean separation between valid draft states and debug-only bypasses.

### Negative

- Callers working with raw/unresolved imports must explicitly pass `{ allowUnresolved: true }`.

## Evidence

- Code inspection of `src/preview/renderer.js`, `src/sheets/index.js`, and `src/validation/index.js`.
- External AI architectural consultation and review on 2026-09-30.
- Automated regression suite: `tests/validation.test.js` and `tests/preview-gate.test.js` (20/20 passing).

## Supersedes

None.