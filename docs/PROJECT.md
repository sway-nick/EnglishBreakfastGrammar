---
trigger: always_on
---

# PROJECT

## PROJECT NAME

Universal English Test Platform

## WORKSPACE

English Breakfast Grammar

## PURPOSE

The project is an English learning and testing platform focused on structured grammar lessons, exercises, questions, answer options, explanations, and related learning content.

The platform is designed to support creation, validation, processing, storage, and delivery of English learning and testing content.

## CORE AREAS

The project may include:

- grammar lessons;
- exercises;
- questions;
- answer options;
- explanations;
- lesson and test structure;
- content validation;
- data processing and transformation;
- import/export workflows;
- analytics and supporting data structures.

The exact implementation must always be determined from the current project files.

## ARCHITECTURE PRINCIPLE

The project should prefer:

- clear separation of responsibilities;
- reusable components;
- explicit data structures;
- validation of important data;
- maintainable and testable code;
- minimal unnecessary complexity.

## AI DEVELOPMENT MODEL

Multiple AI models may participate in development.

Antigravity is the primary engineering orchestrator.

Other AI models may perform implementation, analysis, review, or specialized tasks.

External AI may be used as a decision reviewer for significant or uncertain technical decisions.

Project files and documentation are the persistent source of project context.

Conversation history is not considered a reliable long-term source of truth.

## DOCUMENTATION

Project documentation is maintained in:

`/docs`

Important files include:

- `AI_CONTEXT.md` — short current context;
- `CURRENT_STATE.md` — current project state;
- `TASKS.md` — active tasks and backlog;
- `DECISIONS.md` — architectural decisions and ADRs;
- `PROJECT.md` — project purpose and boundaries.

## SOURCE OF TRUTH

For implementation decisions, use this priority:

1. Actual project files and configuration
2. Actual database and external system state
3. Git history
4. Project documentation
5. Current conversation
6. Previous conversations

## SCOPE CONTROL

Do not introduce unrelated features or architectural changes.

Before changing a major component, identify:

- why the change is required;
- which existing components are affected;
- whether an existing pattern can be reused;
- how the change will be verified.

## UPDATE POLICY

Keep this document focused on the project's purpose, boundaries, and development principles.

Do not use it as a detailed task log or technical changelog.

Detailed current state belongs in `CURRENT_STATE.md`.

Tasks belong in `TASKS.md`.

Architectural decisions belong in `DECISIONS.md`.