---
trigger: always_on
---

# ADAPTATION ARCHITECTURE & PILOT CHECKPOINT

**Date**: 2026-09-30  
**Phase**: Content Adaptation Infrastructure & Pilot Validation  
**Status**: Architecture Finalized, Pilot Validated, Queue Staged, Pipeline Halted for Future Orchestration  

---

## 1. EXECUTIVE SUMMARY & ACCEPTED BASELINE

Today marked the formal architecture, algorithmic design, database instantiation, pilot generation, quality calibration, AI semantic review, and answer-preservation hardening of the **Content Adaptation Pipeline**.

All content adaptation activities are now finalized for today and frozen in a verifiable, regression-tested state.

### 1.1 Verified Full Source Corpus (Immutable Source of Truth)
The enriched source corpus is completely immutable, verified, and sealed in `data/staging.db`, `data/cms/english_cms_final_enriched.xlsx`, and `data/cms/universal_lessons_final_enriched.json`:
- **Lessons / Topics**: 225
- **Exercises**: 638
- **Questions**: 5,796
  - `gap`: 3,522 questions (4,733 total gaps)
  - `single_choice`: 1,927 questions
  - `multiple_choice`: 165 questions
- **Options**: 13,052 options
- **Answer Enrichment**: 100% complete (0 unanswered items, 0 NULLs).
- **Validation**: 100% passing across all 12 CMS structural checks and Preview Gate (225/225).

---

## 2. ADAPTATION INFRASTRUCTURE & ARCHITECTURE

The adaptation subsystem operates on an isolated relational database (`data/adaptation.db`) and a suite of dedicated Python validation and evaluation engines.

### 2.1 Storage & Schema (`data/adaptation.db`)
- Initialized from [`schemas/adaptation_schema.sql`](file:///c:/projects/English%20Breakfast%20Grammar/schemas/adaptation_schema.sql).
- Tables: `adapted_lessons`, `adapted_exercises`, `adapted_questions`, `adapted_gaps`, `adapted_options`, `adaptation_runs`, `pilot_semantic_reviews`.
- Strict foreign key constraints (`PRAGMA foreign_keys = ON;`), zero orphan records.
- 100% foreign key traceability back to source staging IDs (`source_question_id`, `source_lesson_id`, etc.).
- Excluded from version control via `.gitignore` (`data/`).

### 2.2 Implemented Subsystems & Modules
1. **Queue & Database Manager**: [`pipeline/adaptation/adaptation_db.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/adaptation_db.py)
   - Handles schema initialization, idempotent queue loading from `data/staging.db`, status reporting, and foreign key integrity verification.
2. **Originality & Similarity Evaluator**: [`pipeline/adaptation/similarity_evaluator.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/similarity_evaluator.py)
   - Evaluates Jaccard token similarity (excluding target grammar tokens), 3+ word n-gram shingle overlap, and normalized Levenshtein edit distance.
   - Calibrated for dialogue scaffolding (`A: ... B: ...`) and short grammatical items ($< 40$ chars).
3. **Answer Integrity & Grammatical Dependency Validator**: [`pipeline/adaptation/answer_integrity_validator.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/answer_integrity_validator.py)
   - Validates that the adapted context makes the correct answer unambiguously valid.
   - Monitors 13 high-risk mutation factors (singular/plural, gender, person, countability, etc.).
   - Asserts `source_correct_answer == adapted_correct_answer`.
4. **Generation Rules & Prompt Guidelines**: [`pipeline/adaptation/generation_rules.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/generation_rules.py)
   - Encapsulates canonical generation instruction, 8-tier priority hierarchy, and structured prompt construction.
5. **AI Semantic Reviewer**: [`pipeline/adaptation/semantic_reviewer.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/semantic_reviewer.py)
   - Evaluates 4 dimensions: Grammar target, Answer integrity, Originality, and English quality.
   - Writes immutable records to `pilot_semantic_reviews` table and JSON reports.
6. **Review Workbook Builder**: [`pipeline/adaptation/review_report_builder.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/adaptation/review_report_builder.py)
   - Generates 3-sheet Excel review artifact (`Summary`, `Review_Required`, `All_Pilot_Questions_200`).

---

## 3. CHRONOLOGY OF COMPLETED ADAPTATION TASKS

| Task | Scope & Objective | Deliverables & Key Result |
| :--- | :--- | :--- |
| **TASK-010B** | Adaptation Architecture Specification | Authored `docs/TASK-010B_ADAPTATION_SPEC.md` and `schemas/adaptation_schema.sql`. Defined invariants, lifecycle states, and anti-plagiarism metrics. |
| **TASK-011A** | Originality / Similarity Evaluator | Built `similarity_evaluator.py`. Implemented Jaccard, shingle overlap ($\ge 3$ consecutive words), and Levenshtein metrics. 9 unit tests green. |
| **TASK-011B** | Database & Queue Manager | Built `adaptation_db.py`. Initialized `data/adaptation.db`. Populated initial queue of 5,796 questions from immutable staging in `PENDING` status. 0 FK errors. |
| **TASK-011C** | Pilot Generation (20 Exercises / 200 Qs) | Curated balanced pilot sample (A1+A2, 103 single_choice, 90 gap, 7 multiple_choice). Evaluator: 125 VALIDATED, 75 REVIEW_REQUIRED, 0 REJECTED. Preview Gate: 12/12 passed. |
| **TASK-011D** | Human Review Workbook | Built `review_report_builder.py`. Generated `data/adaptation/pilot_review_20260930.xlsx` (mirrored to Desktop) with Summary, Review_Required_75, and All_Pilot_Questions_200. |
| **TASK-011E** | Evaluator Calibration (Short Items) | Calibrated `similarity_evaluator.py` with dialogue normalization and short-text Levenshtein exemption. Re-evaluation: 186 VALIDATED (93%), 14 REVIEW_REQUIRED (7%), 0 REJECTED. 16 tests green. |
| **TASK-011G** | AI-Based Semantic Review | Built `semantic_reviewer.py`. Audited 34 questions (14 REVIEW_REQUIRED + 20 control VALIDATED): 32 APPROVE, 2 REVISE (QID 4203 & 4211), 0 REJECT. 0 false acceptances in control set. |
| **TASK-011H (Part 1)** | Pilot Question Revisions | Reworked QID 4203 (storm travel scenario) and QID 4211 (school cafeteria vs library testing canonical `-y -> -ier`). Both `VALIDATED`. AI Review: 34/34 APPROVE (100.0%). Gate passed. |
| **TASK-011H (Part 2)** | Strategy Update (Preserve Correct Answer) | Hardened architecture: prefer preserving correct answer (`source == adapted`). Implemented `generation_rules.py`, `answer_integrity_validator.py`, and 7 dedicated unit tests. |

---

## 4. PILOT RESULTS & AUDIT METRICS

### 4.1 Sample & Scope
- **Total Pilot Exercises**: 20 (across A1 Elementary and A2 Pre-intermediate)
- **Total Pilot Questions**: 200
  - `single_choice`: 103
  - `gap`: 90 (gap_text and gap_select)
  - `multiple_choice`: 7

### 4.2 Calibrated Evaluator Distribution
* **`VALIDATED`**: **186 / 200 (93.0%)**
* **`REVIEW_REQUIRED`**: **14 / 200 (7.0%)**
* **`REJECTED`**: **0 / 200 (0.0%)**
* **Forbidden Shingle Violations ($\ge 3$ consecutive content words)**: **0 / 200 (0.0000)**

### 4.3 AI Semantic & Quality Audit (34-Question Cohort)
Audited all 14 originally flagged items + 20 deterministic control items:
* **`APPROVE`**: **34 / 34 (100.0%)**
* **`REVISE`**: **0 / 34 (0.0%)**
* **`REJECT`**: **0 / 34 (0.0%)**
* **False Acceptances on Control Sample**: **0 / 20 (0.0%)**

### 4.4 Preview Gate & Structural Validation
* **Exported Universal JSON**: `data/pilot_adapted_lessons.json`
* **Preview Gate Pass Rate**: **12 / 12 lessons (100.0%)**
* **Schema Errors**: **0**

---

## 5. FINAL ADAPTATION PRINCIPLES & RULES

### 5.1 Core Principle: Preserve the Correct Answer
The primary objective of the adaptation engine is:
```
SOURCE ITEM
  ↓ keep grammatical target & correct-answer mechanism
  ↓ change context / vocabulary / names / situation
  ↓ preserve the exact same correct answer
  ↓ validate that the adapted sentence independently makes that answer correct
ADAPTED ITEM
```

### 5.2 Adaptation Priority Hierarchy
1. **Preserve the same correct answer** whenever reasonably possible.
2. **Change context, names, objects, places, situations**, and non-target vocabulary.
3. **Preserve the exact grammatical mechanism** being tested.
4. **Preserve response_model** (`single_choice`, `multiple_choice`, `gap`).
5. **Preserve option and gap cardinality**.
6. **Avoid unnecessary grammatical mutations**.
7. **Avoid one-to-one lexical substitution** that leaves the whole sentence structurally identical.
8. **Do not force an answer change** merely to make the text look different.

### 5.3 Answer Integrity Invariant
$$\text{source\_correct\_answer} == \text{adapted\_correct\_answer}$$
- If $\text{source\_correct\_answer} \ne \text{adapted\_correct\_answer} \implies \text{review\_required} = \text{true}$.
- No blind copying: $\text{adapted\_text} + \text{adapted\_options} + \text{target\_grammar} \implies \text{answer valid}$.
- If answer becomes invalid: mark `REVIEW_REQUIRED` (no random word swapping).

### 5.4 Grammatical Dependency Rule: 13 High-Risk Mutation Factors
Avoid the following mutations unless strictly required:
1. Gender
2. Singular / Plural (number)
3. Grammatical person (1st, 2nd, 3rd)
4. Subject entity
5. Pronoun reference
6. Possessive form
7. Determiner / Demonstrative (`this`/`these`)
8. Article (`a`/`an`/`the`/zero)
9. Countability (count vs non-count)
10. Tense / Aspect
11. Auxiliary verb
12. Verb agreement
13. Comparative / Superlative form

### 5.5 Canonical AI Model Generation Instruction
> *"Preserve the source correct answer whenever possible. Prefer changing the situation and vocabulary around the grammar target rather than changing the grammatical form that determines the answer."*

### 5.6 Quality Rule
The goal is **not maximum textual difference**. The goal is:
1. Independent wording and context (free of plagiarism);
2. Identical educational objective and CEFR difficulty;
3. Identical correct-answer logic;
4. Natural, idiomatic English.

---

## 6. CURRENT ADAPTATION QUEUE STATUS (`data/adaptation.db`)

| Status | Count | Description |
| :--- | :--- | :--- |
| **`PENDING`** | **5,571** | Remaining unadapted questions queued for future full-corpus production batches. |
| **`VALIDATED`** | **206** | 188 synchronized pilot questions + 18 dry-run questions. |
| **`REVIEW_REQUIRED`** | **19** | 12 synchronized pilot questions + 7 dry-run questions flagged for review (all approved in semantic review). |
| **`APPROVED`** | **0** | Reserved for final editorial sign-off prior to production publishing. |
| **`REJECTED`** | **0** | Zero unsalvageable transformations across pilot and dry-run items. |
| **TOTAL QUESTIONS** | **5,796** | Matches exactly the 5,796 source questions in `data/staging.db`. |

---

## 7. FULL-CORPUS ORCHESTRATOR & 25-QUESTION DRY RUN (TASK-012)

The production-grade batch orchestrator was implemented in `pipeline/adaptation/full_corpus_orchestrator.py` and verified via a 25-question dry-run across all 3 response models:

1. **Pilot Status Normalization**:
   - `pipeline/adaptation/pilot_sync.py` normalized the 200 pilot questions in `data/adaptation.db` to 188 VALIDATED, 12 REVIEW_REQUIRED, 0 REJECTED.
2. **Multi-Tier Validation Pipeline**:
   - Structural validation -> Answer integrity validation (`validate_answer_integrity`) -> Originality / Similarity evaluation (`evaluate_similarity`) -> Preview Gate validation.
3. **25-Question Dry Run Results**:
   - Run ID: `orch_task012_dryrun_25`
   - Generated questions: 25 / 25
     * 10 `single_choice` (quiz-13)
     * 10 `gap` (quiz-6)
     * 5 `multiple_choice` (quiz-92)
   - Status distribution: 18 VALIDATED, 7 REVIEW_REQUIRED, 0 REJECTED
   - Answer preservation: 100% (0 answer divergences)
   - High-risk mutations: 7 (all routed to `REVIEW_REQUIRED`)
   - Similarity metrics (mean): Jaccard=0.1070, Max Shingle=0.0000, Levenshtein=0.3108
   - AI Semantic Reviews: 8 reviews conducted (8 APPROVE, 0 REVISE, 0 REJECT)
   - Preview Gate result: PASSED (Node JS Preview Gate and strict JS validator pass)

---

## 8. AUTOMATED TEST SUITE STATUS

All automated regression and validation test suites pass with zero errors:
- **Python Unit Tests**: **97 / 97 passing (OK in 26.2s)**
  - `test_full_corpus_orchestrator.py` (8 tests)
  - `test_answer_integrity_validator.py` (7 tests)
  - `test_semantic_reviewer.py` (5 tests)
  - `test_review_report_builder.py` (5 tests)
  - `test_similarity_evaluator.py` (16 tests)
  - `test_adaptation_db.py` (7 tests)
  - Staging, CMS, and enrichment validation tests (49 tests)
- **JavaScript Jest Tests**: **24 / 24 passing (OK in 6.7s)**
  - `preview-gate.test.js` (12 tests)
  - `validation.test.js` (12 tests)
- **Total Green Tests**: **121 / 121 tests passing**.

---

## 9. EXACT NEXT TASK FOR FUTURE WORK

When work resumes, the exact next task is:

```text
TASK-013: FULL-CORPUS ADAPTATION BATCH GENERATION

Goal:
Run production batches for the remaining 5,571 PENDING questions in data/adaptation.db
using pipeline/adaptation/full_corpus_orchestrator.py.

Key Objectives:
1. Level-by-level roll-out (A1 -> A2 -> B1 -> B1+ -> B2 -> C1).
2. Rate-limited Gemini model calls with exponential backoff.
3. Multi-tier validation with answer preservation and selective AI review.
4. Export updated universal lessons and pass Preview Gate checkpoints.
```
