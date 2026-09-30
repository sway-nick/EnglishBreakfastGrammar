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

The repository contains two operational subsystems that are currently **decoupled**:
1. **Python Pipeline (`pipeline/`)**: Handles scraping/parsing source HTML, collecting lessons into structured JSON, creating Excel CMS sheets, calling Gemini API to fill answers (`english_cms_answered.xlsx`), and performing validation.
2. **JavaScript Core (`src/`)**: Canonical domain models, structured JSON validation with strict and `allowUnresolved` modes, preview rendering with validation gate, Google Sheets sync, and passing automated test suite (10/10 tests green).

## AI ORCHESTRATION

Configured and active:
- `.agents/rules/01-core.md` (Always On): Core orchestration, context boundaries, source-of-truth hierarchy, verification, and model handoff protocol.
- `.agents/rules/02-ai-consultation.md` (Model Decision): Protocol for external AI consultation on high-risk or uncertain architectural decisions.
- `.agents/skills/consult/SKILL.md`: Structured consultation workflow.
- *Handoff Mechanism*: Documented protocol/checklist in rules and `/docs`. No automated command or `/handoff` skill exists.

## PROJECT MEMORY

Configured:
- `docs/AI_CONTEXT.md`: Short project context, subsystem roles, and open issues.
- `docs/CURRENT_STATE.md`: Detailed current snapshot and status.
- `docs/TASKS.md`: Task tracking, active tasks, subtasks, and backlog.
- `docs/DECISIONS.md`: Architectural decision records (ADR-001 accepted, ADR-002 accepted).
- `docs/PROJECT.md`: Purpose, principles, and scope boundaries.
- `docs/ARCHITECTURE.md`: High-level system architecture, target flows, and subsystem boundaries.
- `docs/LEGACY_PRODUCT_CONTEXT.md`: Historical contracts and product context (reference only).

## CURRENT OBJECTIVE

Complete multi-model workflow guidelines (TASK-001.5), then build the bridge connecting Python Pipeline output data into the JavaScript Test Engine and Preview (TASK-004).

## CURRENT TASK

TASK-001.5 — Multi-model workflow definition.

## OPEN ISSUES

1. **[INTEGRATION-01] Missing CMS-to-JSON export bridge**:
   - Python pipeline outputs `english_cms_answered.xlsx`.
   - JavaScript preview server requires individual lesson JSON (e.g. `data/json/L001.json`).
   - No converter exists to transform answered Excel CMS back into canonical JSON. Tracked under `TASK-004`.

## RESOLVED ISSUES

- **[SCHEMA-01]**: Resolved via ADR-002. Unified `.is_correct` across JS validation, models, preview renderer, sheets module, and tests. Implemented `validate(lesson, { allowUnresolved })`.
- **[TOOLING-01]**: Resolved. Updated `package.json` test runner to use cross-platform node executable path `node_modules/jest/bin/jest.js`.

## NEXT STEPS

1. Complete TASK-001.5 (multi-model task handoff conventions).
2. Implement TASK-004: CMS-to-JSON export bridge to enable end-to-end previewing of pipeline data.

## HANDOFF

Any AI model continuing work must:
1. Read `docs/AI_CONTEXT.md` and `docs/CURRENT_STATE.md`.
2. Inspect `docs/DECISIONS.md` for accepted/provisional ADRs.
3. Inspect relevant source files before proposing changes.
4. Run `npm test` to verify that all 10 tests continue to pass.
5. Follow the manual handoff checklist in `01-core.md`.