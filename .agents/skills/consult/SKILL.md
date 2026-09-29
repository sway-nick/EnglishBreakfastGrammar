---
name: consult
description: Prepares and reviews external AI consultations for significant, uncertain, architectural, or high-risk technical decisions. Use when a project decision requires an independent architecture or implementation review.
---

# CONSULT

## PURPOSE

Run a structured external AI consultation for a technical or architectural decision.

The skill does not replace project analysis or decision-making.

The primary agent must:

1. inspect the project;
2. form its own position;
3. determine whether consultation is justified;
4. prepare a compact consultation package;
5. evaluate the external response;
6. make or escalate the final decision;
7. record significant decisions.

---

# PHASE 1 — UNDERSTAND THE DECISION

Before preparing a consultation:

1. Identify the exact decision.
2. Inspect the relevant project files.
3. Read relevant project documentation.
4. Check `docs/DECISIONS.md`.
5. Check whether an existing accepted ADR already answers the question.
6. Identify constraints and affected components.
7. Identify whether the decision is reversible.

Do not consult external AI for a decision that is already clearly covered by an accepted ADR unless there is concrete evidence that the decision should be reconsidered.

---

# PHASE 2 — FORM OUR OWN POSITION

Before asking external AI, determine:

Preferred option:

Confidence:

Reason:

Main uncertainty:

Important constraints:

Do not ask an external AI to solve the problem from zero.

External AI should review our reasoning and alternatives.

---

# PHASE 3 — DECIDE WHETHER CONSULTATION IS NECESSARY

Use these rules:

### Proceed without consultation

When:

- confidence is approximately 70% or higher;
- the change is low or moderate risk;
- the decision is reversible;
- the cost of being wrong is limited.

### Consult external AI

When:

- confidence is below approximately 70%;
- several materially different approaches exist;
- important trade-offs are unclear;
- the decision has significant long-term consequences;
- an independent technical review can materially reduce risk.

### Mandatory consultation

Consult for decisions involving:

- database architecture;
- destructive or difficult-to-reverse migrations;
- authentication or authorization;
- security architecture;
- payments or financial integrity;
- public API contracts;
- infrastructure architecture;
- major vendor lock-in;
- major architectural changes;
- large or expensive refactors.

---

# PHASE 4 — PREPARE THE CONSULTATION PACKAGE

The consultation package must be concise.

Do not send the entire project.

Send only the context required to evaluate the decision.

Write the package in English.

Use exactly this structure:

# EXTERNAL AI CONSULTATION

## PROJECT

Brief project description.

## STACK

Relevant technologies and versions.

## CURRENT STATE

Only facts relevant to the decision.

## PROBLEM

The exact decision that must be made.

## OPTIONS

### OPTION A

Description.

Advantages.

Disadvantages.

### OPTION B

Description.

Advantages.

Disadvantages.

### OPTION C

Description.

Advantages.

Disadvantages.

Include only meaningful alternatives.

## CONSTRAINTS

Technical, business, security, performance, compatibility, cost, time, and maintenance constraints.

## OUR CURRENT LEANING

Preferred option:

Confidence:

Reason:

Main uncertainty:

## WHAT WE NEED

Please evaluate our current leaning rather than starting from zero.

Return:

1. VERDICT — Agree / Disagree / Conditional
2. BEST OPTION
3. TOP 3 RISKS
4. WHEN OUR CHOICE WOULD BE WRONG
5. FIRST THING TO VERIFY
6. IMPORTANT TRADE-OFF
7. ALTERNATIVE
8. CONFIDENCE

## SCOPE

Evaluate only the stated decision.

Do not redesign unrelated parts of the project.

---

# PHASE 5 — PRIVACY

Before producing the package, remove:

- passwords;
- API keys;
- access tokens;
- personal data;
- confidential customer information;
- unnecessary commercial information;
- secrets from configuration files.

Anonymize sensitive values.

Send the minimum context required.

---

# PHASE 6 — WAIT FOR EXTERNAL REVIEW

Unless an external AI integration tool is explicitly available, do not claim that external AI was contacted.

Instead:

1. produce the consultation package;
2. present it to the user;
3. wait for the external AI response to be supplied.

Do not fabricate external AI feedback.

---

# PHASE 7 — REVIEW THE EXTERNAL RESPONSE

When the user supplies an external AI response:

Evaluate it against:

- actual project files;
- current architecture;
- existing ADRs;
- project constraints;
- evidence;
- implementation complexity;
- maintenance cost;
- security;
- scalability;
- reversibility;
- migration risk;
- consistency with existing patterns.

Do not automatically accept the external recommendation.

Classify the result:

- ACCEPT
- REJECT
- MODIFY
- DEFER

---

# PHASE 8 — HIGH-COST OR IRREVERSIBLE DECISIONS

If the decision is expensive, difficult to reverse, externally visible, or has major business consequences:

1. summarize the options;
2. summarize the external review;
3. identify the principal risks;
4. ask the user for approval;
5. do not implement until approval is received.

For low-risk reversible decisions, the agent may decide without explicit approval.

---

# PHASE 9 — DECISION RECORD

For a significant decision, create or update an ADR in:

`docs/DECISIONS.md`

Use:

# ADR-XXX

## Status

provisional / accepted / superseded / rejected

## Date

YYYY-MM-DD

## Context

What problem required a decision.

## Decision

What was chosen.

## Reason

Why it was chosen.

## Alternatives Rejected

### Option A

Reason.

### Option B

Reason.

## Consequences

### Positive

Expected benefits.

### Negative

Expected costs and risks.

## Evidence

Tests, experiments, project inspection, documentation, and external consultation.

## Supersedes

Previous ADR if applicable.

Never rewrite historical ADRs.

When a decision changes, create a new ADR and mark the previous ADR as `superseded`.

---

# PHASE 10 — DOCUMENTATION UPDATE

After the decision:

Update only the documentation that actually changed.

Possible files:

- `docs/AI_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/TASKS.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/CHANGELOG.md`

Do not duplicate the same information across files unnecessarily.

---

# USER-FACING RESULT

Explain the result to the user in Russian.

For significant consultations use:

РЕШЕНИЕ:
ACCEPT / REJECT / MODIFY / DEFER

НАША ПОЗИЦИЯ:
...

ЧТО СКАЗАЛ ВНЕШНИЙ AI:
...

ГЛАВНЫЙ РИСК:
...

ЧТО ПРОВЕРИЛИ:
...

ЧТО ДЕЛАЕМ:
...

ТРЕБУЕТСЯ РЕШЕНИЕ ПОЛЬЗОВАТЕЛЯ:
ДА / НЕТ

---

# IMPORTANT RULES

Never:

- fabricate external AI feedback;
- hide uncertainty;
- ignore an existing accepted ADR;
- send unnecessary project context;
- expose secrets;
- implement irreversible changes without required approval;
- rewrite historical ADRs;
- consult external AI merely because another approach exists.

Always:

- inspect the real project first;
- form our own position first;
- keep consultation context compact;
- distinguish facts from recommendations;
- verify external advice against the actual project;
- document significant decisions.