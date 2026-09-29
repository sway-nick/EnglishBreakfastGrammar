---
trigger: always_on
---

# CURRENT PROJECT STATE

## DATE

2026-09-29

## PROJECT

Universal English Test Platform

## WORKSPACE

English Breakfast Grammar

## DEVELOPMENT STATUS

Active development.

The project contains code, data, schemas, tests, and processing/export components.

The actual project files are the primary source of truth.

## AI ORCHESTRATION

Configured:

- `.agents/rules/01-core.md`
  - Activation: Always On
  - Purpose: core project orchestration

- `.agents/rules/02-ai-consultation.md`
  - Activation: Model Decision
  - Purpose: external AI consultation for significant or uncertain decisions

## PROJECT MEMORY

Configured:

- `docs/AI_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/DECISIONS.md`

## CURRENT OBJECTIVE

Establish a reliable AI development workflow where multiple AI models can continue work using project files and documentation rather than conversation history.

## CURRENT TASK

Complete the project AI orchestration and documentation structure.

## KNOWN ISSUES

None recorded yet.

Update this section when a real project issue becomes relevant.

## NEXT STEPS

1. Complete the core project documentation structure.
2. Inspect the actual project architecture and current implementation.
3. Record important existing architectural decisions.
4. Define an efficient workflow for switching between AI models.
5. Begin normal feature development using the new orchestration workflow.

## HANDOFF

Any AI model continuing work should:

1. Read `docs/AI_CONTEXT.md`.
2. Read `docs/CURRENT_STATE.md`.
3. Check `docs/DECISIONS.md`.
4. Inspect the actual files relevant to the task.
5. Continue from the existing implementation.

## UPDATE POLICY

Update this file whenever:

- the project enters a materially different development stage;
- the current objective changes;
- major work is completed;
- important problems appear or are resolved;
- the handoff state changes significantly.