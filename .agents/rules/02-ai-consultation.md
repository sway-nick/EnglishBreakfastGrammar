---
trigger: model_decision
description: Use this rule when a significant technical, architectural, high-risk, or uncertain decision may benefit from external AI consultation.
---

# EXTERNAL AI CONSULTATION RULE

## PURPOSE

Use external AI as an architecture and decision-review mechanism.

External AI is not the default solution for every problem.

The primary agent remains responsible for understanding the project, forming an initial position, implementing the decision, and verifying the result.

---

## FIRST CHECK EXISTING DECISIONS

Before considering external consultation:

1. Check existing project documentation.
2. Check `DECISIONS.md` and existing ADRs when available.
3. Check the actual project implementation and configuration.
4. Check whether the same or a sufficiently similar decision has already been made.

If an existing accepted decision applies, follow it unless there is concrete evidence that it should be reconsidered.

Do not create a new decision for something already covered by an accepted decision.

---

## DECISION THRESHOLD

First form your own recommendation.

Estimate your confidence.

### Proceed without external AI when:

- confidence is approximately 70% or higher;
- the change is low or moderate risk;
- the decision is reversible;
- the implementation cost of being wrong is limited.

### Consult external AI when:

- confidence is below approximately 70%;
- there are several materially different approaches;
- important trade-offs are unclear;
- the decision has significant long-term consequences;
- another technical perspective could materially reduce risk.

### Mandatory consultation for high-risk decisions

Consult external AI regardless of confidence for decisions involving:

- database architecture;
- destructive or difficult-to-reverse migrations;
- authentication or authorization;
- security architecture;
- payments or financial integrity;
- public API contracts;
- infrastructure architecture;
- major vendor or platform lock-in;
- major architectural changes;
- large or expensive refactors;
- changes that would be costly to undo.

---

## USER APPROVAL

If a decision is expensive, difficult to reverse, externally visible, or has major business consequences:

1. analyze it;
2. consult external AI when required;
3. present the relevant trade-offs;
4. obtain user approval before implementation.

For low-risk and easily reversible decisions, the agent may proceed without explicit approval.

Significant provisional decisions should still be recorded.

---

## FORM YOUR OWN POSITION FIRST

Never ask external AI an unstructured question such as:

"How should we solve this?"

Before consultation, determine:

- your preferred option;
- your confidence;
- why you currently prefer it;
- the main uncertainty;
- the important constraints.

External AI should review our reasoning rather than restart the analysis from zero.

---

## CONSULTATION PACKAGE

Prepare a compact consultation package in English.

Do not send the entire project unless absolutely necessary.

Include only information relevant to the decision.

Use this structure:

# EXTERNAL AI CONSULTATION

## PROJECT

Brief description of the project and the relevant component.

## STACK

Relevant technologies, frameworks, database, infrastructure, and versions when important.

## CURRENT STATE

Short factual description of the current implementation.

## PROBLEM

Exact problem or decision that must be resolved.

## OPTIONS

### OPTION A

Description, advantages, disadvantages.

### OPTION B

Description, advantages, disadvantages.

### OPTION C

Description, advantages, disadvantages.

Include only meaningful alternatives.

## CONSTRAINTS

Important technical, business, performance, security, compatibility, time, and maintenance constraints.

## OUR CURRENT LEANING

Preferred option:

Confidence:

Reason:

Main uncertainty:

## WHAT WE NEED

Please evaluate our current leaning rather than starting from zero.

Return the answer in this format:

1. VERDICT - Agree / Disagree / Conditional
2. BEST OPTION
3. TOP 3 RISKS
4. WHEN OUR CHOICE WOULD BE WRONG
5. FIRST THING TO VERIFY
6. IMPORTANT TRADE-OFF
7. ALTERNATIVE
8. CONFIDENCE

---

## PRIVACY

Do not send:

- passwords;
- API keys;
- access tokens;
- personal data;
- confidential customer data;
- unnecessary commercial information;
- secrets from configuration files.

Anonymize sensitive values whenever possible.

Send only the minimum project context required for the decision.

---

## EVALUATING EXTERNAL ADVICE

Do not automatically accept external AI advice.

Evaluate it against:

- actual project architecture;
- existing decisions;
- project constraints;
- evidence;
- implementation complexity;
- maintenance cost;
- security;
- scalability;
- migration difficulty;
- reversibility;
- consistency with existing project patterns.

The final decision belongs to the project agent and user, not to external AI.

---

## AFTER CONSULTATION

Classify the result as one of:

- ACCEPT
- REJECT
- MODIFY
- DEFER

If modifying the recommendation, record what changed and why.

If rejecting it, record the concrete reason when the decision is significant.

---

## DECISION RECORD

For significant decisions, record an ADR in `DECISIONS.md` or the project's established ADR location.

Use this structure:

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

Reason rejected.

### Option B

Reason rejected.

## Consequences

### Positive

Expected benefits.

### Negative

Expected costs, risks, or limitations.

## Evidence

Relevant tests, documentation, experiments, or external consultation.

## Supersedes

Reference to the previous ADR when applicable.

Never rewrite historical ADRs.

If a decision changes, create a new ADR and mark the previous one as `superseded`.

---

## PROVISIONAL DECISIONS

For low-risk reversible decisions, a provisional decision may be made without user approval.

Use `provisional` when the decision is intentionally temporary and may be reconsidered after implementation or testing.

---

## TOKEN EFFICIENCY

External consultation must remain compact.

Do not send:

- the entire conversation;
- the entire repository;
- unchanged files;
- unrelated logs;
- duplicate documentation.

Prefer:

- exact problem;
- relevant files;
- concise current state;
- relevant constraints;
- meaningful alternatives;
- focused question.

---

## USER-FACING COMMUNICATION

The external consultation package must be written in English.

Explain the result to the user in Russian.

Use this structure when reporting a significant consultation:

РЕШЕНИЕ:
[ACCEPT / REJECT / MODIFY / DEFER]

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