---
trigger: always_on
---

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
- More controlled use of external AI.

### Negative

- Important project state must be kept updated.
- Significant decisions require documentation.
- Incorrect documentation can become a source of confusion.

## Evidence

Initial project orchestration design agreed during project setup.

## Supersedes

None.