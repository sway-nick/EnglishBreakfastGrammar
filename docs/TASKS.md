---
trigger: always_on
---

# PROJECT TASKS

## CURRENT TASK

TASK-001 — Complete AI orchestration and project context setup

Status: in_progress

## OBJECTIVE

Create a reliable project workflow that allows different AI models to continue development using project files and documentation instead of relying on conversation history.

## SUBTASKS

### TASK-001.1 — Core orchestration rules

Status: completed

- Create `.agents/rules/01-core.md`
- Configure activation as `Always On`
- Define source-of-truth hierarchy
- Define context management
- Define model handoff rules
- Define verification and documentation checkpoints

### TASK-001.2 — External AI consultation

Status: completed

- Create `.agents/rules/02-ai-consultation.md`
- Configure activation as `Model Decision`
- Define consultation threshold
- Define consultation package
- Define privacy requirements
- Define ADR requirements

### TASK-001.3 — Project memory

Status: in_progress

- Create `docs/AI_CONTEXT.md` — completed
- Create `docs/CURRENT_STATE.md` — completed
- Create `docs/DECISIONS.md` — completed
- Create `docs/TASKS.md` — current
- Create remaining project documentation files

### TASK-001.4 — Project architecture review

Status: pending

- Inspect the actual project structure
- Identify major components
- Identify database and external services
- Identify important existing architectural decisions
- Record significant decisions as ADRs

### TASK-001.5 — Multi-model workflow

Status: pending

- Define how Claude and Gemini receive tasks
- Define handoff procedure
- Define when external AI consultation is triggered
- Define how implementation results are verified
- Minimize repeated context

## BACKLOG

Add future development tasks here.

## COMPLETED TASKS

Move completed major tasks here only when they are no longer relevant to the active workflow.