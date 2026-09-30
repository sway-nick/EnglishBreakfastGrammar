---
trigger: always_on
---

# TASK-010B: CONTENT ADAPTATION PIPELINE SPECIFICATION

## 1. EXECUTIVE SUMMARY & CORE PRINCIPLE

The purpose of the Content Adaptation Pipeline is to transform the acquired, parsed, and answered source corpus into **our own original, legally compliant, pedagogically equivalent English learning content**.

### 1.1 Core Principle

```
SOURCE CORPUS (Immutable)
    ↓
ADAPTATION LAYER (Relational Traceability)
    ↓
OUR ORIGINAL CONTENT (Substantive Rewrite)
    ↓
FINAL APP CONTENT (Preview Gate / Production)
```

The adaptation pipeline ensures that **every adapted question preserves 100% of the educational and grammatical value** of the original question while utilizing **independently created situations, characters, context, syntax, and distractor sets**.

### 1.2 Immutability Contract

The source corpus files and database tables are strictly read-only and immutable:
- `data/staging.db` (staging tables)
- `data/cms/english_cms_final_enriched.xlsx`
- `data/cms/universal_lessons_final_enriched.json`
- `data/cache/html/*.html`

The adaptation pipeline writes strictly to a dedicated adaptation layer (`adapted_*` tables or `data/adaptation.db`). Source records are never overwritten or deleted.

---

## 2. INVARIANTS VS. VARIABLES (WHAT IS PRESERVED VS. WHAT MAY CHANGE)

To maintain pedagogical validity while ensuring original authorship, the pipeline defines clear boundaries between invariant pedagogical attributes and adaptable surface narrative.

| Dimension | Classification | Detailed Rule |
| :--- | :--- | :--- |
| **Lesson / Topic Taxonomy** | **INVARIANT** | Must map to the exact same grammatical category (e.g. `past_simple_vs_past_continuous`). |
| **CEFR Level** | **INVARIANT** | Target CEFR level (`A1` through `C1`) must remain identical. |
| **Grammatical Target** | **INVARIANT** | The grammatical structure being tested (e.g. third-person `-s`, irregular past form, inversion after negative adverbials) must remain identical. |
| **Correct Answer** | **PRIMARY INVARIANT** | Prefer preserving the identical correct answer (`source_correct_answer == adapted_correct_answer`). Do not recalculate or alter the answer unnecessarily when varying context. |
| **Response Model** | **INVARIANT** | `gap` (select/text), `single_choice`, and `multiple_choice` must NOT be changed. |
| **Gap Cardinality** | **INVARIANT** | If the source question has 1 gap, the adapted question must have exactly 1 gap. Multi-gap questions must preserve the exact gap count. |
| **Option Cardinality** | **INVARIANT** | If source choice has 3 options, adapted must have 3 options. Number of correct options must remain identical (e.g. exactly 1 for `single_choice`, exactly 2 for `multiple_choice`). |
| **Truth Semantics** | **INVARIANT** | The logic making an option correct or incorrect must be preserved. |
| **Characters & Names** | **VARIABLE** | Names of people, pets, or personas must be completely replaced. |
| **Locations & Settings** | **VARIABLE** | Cities, countries, domestic/workplace/academic environments should be varied. |
| **Narrative Situation** | **VARIABLE** | The surface topic (e.g. talking about cinema vs. talking about gardening) should be reimagined. |
| **Non-Target Vocabulary** | **VARIABLE** | Nouns, adjectives, and incidental verbs not tied to the target grammar must be varied. |
| **Distractor Narratives** | **VARIABLE** | Distractors must be rewritten to match the new sentence context while maintaining the same grammatical error patterns. |

---

## 3. DATA MODEL & STORAGE ARCHITECTURE

The adaptation data model is maintained in [`schemas/adaptation_schema.sql`](file:///c:/projects/English%20Breakfast%20Grammar/schemas/adaptation_schema.sql) and is separated into dedicated relational entities.

### 3.1 Entity Relationship Diagram

```mermaid
erDiagram
    ADAPTATION_RUNS ||--o{ ADAPTED_LESSONS : tracks
    ADAPTED_LESSONS ||--|{ ADAPTED_EXERCISES : contains
    ADAPTED_EXERCISES ||--|{ ADAPTED_QUESTIONS : contains
    ADAPTED_QUESTIONS ||--o{ ADAPTED_GAPS : contains
    ADAPTED_QUESTIONS ||--o{ ADAPTED_OPTIONS : contains
    ADAPTED_GAPS ||--o{ ADAPTED_OPTIONS : references
```

### 3.2 Schema Definition

```sql
-- Core adapted question schema
CREATE TABLE adapted_questions (
    adapted_question_id TEXT PRIMARY KEY,
    source_question_id TEXT NOT NULL,
    adapted_exercise_id TEXT NOT NULL REFERENCES adapted_exercises(adapted_exercise_id) ON DELETE CASCADE,
    adapted_lesson_id TEXT NOT NULL REFERENCES adapted_lessons(adapted_lesson_id) ON DELETE CASCADE,
    question_order INTEGER NOT NULL,
    response_model TEXT NOT NULL,                      -- 'gap', 'single_choice', 'multiple_choice'
    source_text TEXT NOT NULL,
    adapted_text TEXT,
    explanation TEXT,
    difficulty TEXT,
    similarity_score REAL,                             -- Jaccard/Levenshtein similarity to detect shallow rewrites
    adaptation_status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, GENERATED, VALIDATED, REVIEW_REQUIRED, APPROVED, REJECTED
    review_required INTEGER NOT NULL DEFAULT 0,        -- 0 = False, 1 = True
    adaptation_notes TEXT,
    adapted_by TEXT,
    adapted_at TEXT
);
```

### 3.3 Lifecycle Status Flow (TASK-012A Finalized)

> [!IMPORTANT]
> **Production Decision**: Human review will **NOT** be used for routine adaptation. Independent AI semantic review is the primary review mechanism. `APPROVED` status is not required for the automated production pipeline and remains purely an optional future editorial state.

```mermaid
stateDiagram-v2
    [*] --> PENDING: Initial Staging Extract
    PENDING --> DeterministicCheck: Batch Generator & Evaluators
    
    DeterministicCheck --> VALIDATED: Deterministic Checks PASS
    DeterministicCheck --> REJECTED: Structural Clash / Forbidden Shingle / Ungrammatical
    DeterministicCheck --> AISemanticReview: Deterministic Flag (REVIEW_REQUIRED / High-Risk Mutation)
    
    AISemanticReview --> VALIDATED: AI Decision APPROVE (review_required = 0)
    AISemanticReview --> REVIEW_REQUIRED: AI Decision REVISE (review_required = 1)
    AISemanticReview --> REJECTED: AI Decision REJECT (review_required = 0)
    
    VALIDATED --> [*]: Ready for Universal JSON Export & Preview Gate
```

#### Status Flow Rules:
1. **Deterministic Validation PASS** $\longrightarrow$ **`VALIDATED`** (`review_required = 0`)
   - Passes structural cardinality, answer integrity (unambiguously valid, no high-risk mutations), and originality thresholds (calibrated Levenshtein, Jaccard $\le 0.40$, 0 forbidden 3+ word shingles).
2. **Deterministic `REVIEW_REQUIRED`** $\longrightarrow$ **Trigger AI Semantic Review**
   - Automatically invoked for high-risk mutations (gender, singular/plural, countability shifts), borderline Jaccard similarity ($0.40 < J \le 0.50$), or calibrated Levenshtein triggers.
3. **AI Decision `APPROVE`** $\longrightarrow$ **`VALIDATED`** (`review_required = 0`)
   - The AI reviewer confirms educational validity, answer correctness, and genuine originality. The item transitions cleanly to `VALIDATED`.
4. **AI Decision `REVISE`** $\longrightarrow$ **`REVIEW_REQUIRED`** (`review_required = 1`)
   - The AI reviewer identified specific pedagogical or stylistic issues (e.g. shallow rewrite or rule mismatch). The item remains in `REVIEW_REQUIRED` for targeted regeneration.
5. **AI Decision `REJECT`** $\longrightarrow$ **`REJECTED`** (`review_required = 0`)
   - The adaptation fundamentally distorts the rule or is irrecoverable.
6. **Optional Editorial State**:
   - **`APPROVED`**: Reserved exclusively for optional human/editorial sign-off prior to publishing. It is **never** required for items to reach `VALIDATED` or export to production Universal JSON.

---

## 4. RULES BY RESPONSE MODEL

### 4.1 Gap Questions (`gap`)

1. **Placeholder Consistency**:
   - In database and CMS: `{{gap_1}}`, `{{gap_2}}`, etc.
   - On export boundary to Universal JSON: normalized to `{{gap1}}`, `{{gap2}}`.
   - Text must have an exact 1:1 match between placeholder tokens in `adapted_text` and child `adapted_gaps`.
2. **`input_control = 'select'` (Dropdowns)**:
   - Must have child options in `adapted_options`.
   - Exactly **1 option** must have `adapted_is_correct = 1`.
   - `adapted_correct_answer` must equal the `text` or `value` of the single correct option.
   - Distractors in the select dropdown must represent plausible grammatical mistakes relevant to the rule (e.g. wrong tense, wrong preposition, wrong inflection).
3. **`input_control = 'text'` (Fill-in Text)**:
   - Must NOT have child options.
   - `adapted_correct_answer` must be non-empty and natural for the gap.
   - `adapted_accepted_answers` must be a valid JSON array containing the canonical answer plus valid contracted or alternative spelling forms (e.g. `["do not", "don't"]`).

### 4.2 Single Choice Questions (`single_choice`)

1. **Option Cardinality**:
   - Exactly the same number of options as the source question (typically 3 or 4).
   - Zero gaps allowed (`gap_id` must be empty).
2. **Correctness Cardinality**:
   - Exactly **one option** must have `adapted_is_correct = 1`.
   - All other options must have `adapted_is_correct = 0`.
3. **Distractor Quality**:
   - Distractors must isolate the same grammatical distractor patterns as the original (e.g. if the original contrasts `Present Simple` vs `Present Continuous`, the adapted question must contrast the same two tenses, not introduce unrelated lexical traps).

### 4.3 Multiple Choice Questions (`multiple_choice`)

1. **Option Cardinality**:
   - Exactly the same number of total options as source (typically 3 or 4).
2. **Correctness Cardinality**:
   - Exactly the same number of correct choices as the source (in the Test-English corpus, all 165 multiple choice questions have **exactly 2 correct options**).
   - All correct options must be grammatically sound completions or answers in the new context.
   - Distractors must be indisputably incorrect under standard English grammar.

---

## 5. CORE ADAPTATION STRATEGY: PRESERVE CORRECT ANSWER & ANSWER INTEGRITY

### 5.1 Core Principle

**Prefer adaptations that preserve the original correct answer.**

We do NOT want to recalculate or mutate the correct answer unnecessarily when changing context.

```
SOURCE
  ↓ keep the grammatical target and correct-answer mechanism
  ↓ change context / vocabulary / names / situation
  ↓ preserve the same correct answer
  ↓ validate that the adapted sentence still makes that answer correct
ADAPTATION
```

#### Illustrative Examples:

- **Example 1 (Comparative Adjective Rule)**:
  * *Source*: `Kate is _____ than her sister.` (Options: `friendly | friendlier | more friendlier`; Correct: `friendlier`)
  * *Preferred Adaptation*: `Julia is _____ than her classmate.` (Options: `friendly | friendlier | more friendlier`; Correct: `friendlier`)
  * *Do NOT Prefer*: `Kate is _____ than her sister.` $\to$ `Tom and Jack are _____ than their sister.` because introducing a plural compound subject triggers unwanted grammatical mutations across the sentence.
- **Example 2 (Preposition of Place)**:
  * *Source*: `Where is the milk? It's _____ the fridge.` (Options: `at | in | on`; Correct: `in`)
  * *Preferred Adaptation*: `Where is the juice? It's _____ the cupboard.` (Options: `at | in | on`; Correct: `in`)

#### Unnecessary Mutations to Avoid:
Do NOT unnecessarily change:
- singular $\leftrightarrow$ plural
- `he` $\leftrightarrow$ `they`
- `this` $\leftrightarrow$ `these`
- `is` $\leftrightarrow$ `are`
- `has` $\leftrightarrow$ `have`
- `a/an` $\leftrightarrow$ `some`
- `his` / `her` / `their`
- tense / aspect
- grammatical person
- grammatical number
- countability

when such changes can affect or destabilize the correct answer.

---

### 5.2 Adaptation Priority Hierarchy

1. **Preserve the same correct answer** whenever reasonably possible.
2. **Change context, names, objects, places, situations**, and non-target vocabulary.
3. **Preserve the exact grammatical mechanism** being tested.
4. **Preserve response_model** (`single_choice`, `multiple_choice`, `gap`).
5. **Preserve option and gap cardinality**.
6. **Avoid unnecessary grammatical mutations**.
7. **Avoid one-to-one lexical substitution** that leaves the whole sentence structurally identical.
8. **Do not force an answer change** merely to make the text look different.

---

### 5.3 Answer Integrity Rule

The desired default invariant across the pipeline is:

$$\text{source\_correct\_answer} == \text{adapted\_correct\_answer}$$

- **`single_choice`**: Identical correct option text preferred.
- **`multiple_choice`**: Identical correct option set preferred.
- **`gap_select`**: Identical correct option text preferred.
- **`gap_text`**: Identical canonical answer string preferred where grammatically possible.

#### Automated Check:
$$\text{If } \text{source\_correct\_answer} \ne \text{adapted\_correct\_answer} \implies \text{review\_required} = \text{true}$$

Unless there is an explicit, validated pedagogical justification that changing the answer was strictly necessary, an answer divergence automatically routes the item to human editorial review.

#### Blind Copying Prohibited:
Do NOT simply copy the source answer blindly. The adapted sentence must independently and unequivocally make that answer correct. The engine validates:

$$\text{adapted\_text} + \text{adapted\_options} + \text{target\_grammar} \implies \text{source\_correct\_answer remains valid}$$

If the answer becomes invalid after adaptation:
- Do NOT try to repair automatically by changing random words.
- Automatically flag as **`REVIEW_REQUIRED`**.

---

### 5.4 Grammatical Dependency Rule: High-Risk Mutations

Treat the following 13 grammatical dimensions as **high-risk mutations**:
1. Gender
2. Singular / Plural (number)
3. Grammatical person (1st, 2nd, 3rd)
4. Subject entity
5. Pronoun reference
6. Possessive form
7. Determiner / Demonstrative (`this`/`these`, `that`/`those`)
8. Article (`a`/`an`/`the`/zero)
9. Countability (count vs. non-count nouns)
10. Tense / Aspect
11. Auxiliary verb (`do`, `be`, `have`, modals)
12. Verb agreement (singular subject with singular verb, etc.)
13. Comparative / Superlative morphological form

**Rule**: Avoid them unless strictly necessary. If any such mutation is detected, the entire item must undergo enhanced answer-integrity and validity validation.

---

### 5.5 Generation Instruction for AI Models

The prompt template for adaptation generation must explicitly instruct the model:

> *"Preserve the source correct answer whenever possible. Prefer changing the situation and vocabulary around the grammar target rather than changing the grammatical form that determines the answer."*

---

### 5.6 Quality Rule

The goal of adaptation is **NOT maximum textual difference**.

The goal is:
1. **Independent wording and context** (free of plagiarism and distinct in narrative);
2. **Identical educational objective** and CEFR difficulty;
3. **Identical correct-answer logic** and unambiguous distractor keys;
4. **Natural, idiomatic English**.

---

## 6. RULES & HEURISTICS FOR DETECTING INSUFFICIENT TRANSFORMATION

To guarantee genuine originality and eliminate plagiarism or surface-only paraphrasing, every generated adaptation is subjected to an automated **Transformation Quality & Anti-Plagiarism Engine**.

### 6.1 Similarity Thresholds

For each pair of `(source_text, adapted_text)`:

1. **Jaccard Token Similarity (excluding grammar target tokens)**:
   $$\text{Jaccard}(S_{\text{non-target}}, A_{\text{non-target}}) = \frac{|S \cap A|}{|S \cup A|} \le 0.40$$
   - If $\text{Jaccard} > 0.50$: **AUTOMATIC REJECTION** (Too close to original).
   - If $0.40 < \text{Jaccard} \le 0.50$: Flagged as **`REVIEW_REQUIRED`**.
2. **N-gram Shingle Overlap**:
   - No verbatim sequence of **3 or more consecutive non-target content words** (nouns, adjectives, lexical verbs) from the source may appear in the adapted sentence.
3. **Levenshtein Distance Ratio**:
   - Normalized Levenshtein similarity between non-target content must be $< 0.45$.

### 6.2 Disallowed Transformation Patterns

The engine rejects adaptations that exhibit:
- **Trivial Synonym Replacement**: Merely swapping `car` for `automobile` or `John` for `Peter` while preserving identical syntactic clauses.
- **Trivial Reordering**: Merely moving a time adverbial from the end of the sentence to the beginning without rewriting the clause.
- **Accidental Clue Giving**: Including the target answer word elsewhere in the instruction or sentence.
- **Unnatural Register**: Fabricating awkward or archaic sentences simply to achieve low similarity metrics.

---

## 7. WORKFLOW: SOURCE → GENERATE → VALIDATE → REVIEW → APPROVE

```mermaid
flowchart TD
    A["1. Source Extraction (data/staging.db)"] --> B["2. Prompt Construction (Task Context & Invariants)"]
    B --> C["3. Generation Engine (Batch LLM Execution)"]
    C --> D["4. Automated Structural Validation (Schemas & Cardinality)"]
    D -- "Fails Structural Checks" --> R1["Auto-Reject & Re-queue"]
    D -- "Passes Structure" --> E["5. Similarity & Quality Gate (Anti-Plagiarism)"]
    E -- "Similarity > 0.50" --> R2["Reject (Shallow Rewrite)"]
    E -- "0.40 < Similarity <= 0.50" --> F["6. Editorial Review Queue (REVIEW_REQUIRED)"]
    E -- "Similarity <= 0.40" --> G["7. Pedagogical Consistency Check"]
    G --> H["8. Approved for Production (APPROVED)"]
    F --> H
    F -- "Rejected by Editor" --> R3["Reject & Regenerate"]
```

1. **Source Extraction**: Reads immutable question, gaps, and options from `data/staging.db`.
2. **Prompt Construction**: Injects:
   - Lesson topic and CEFR level;
   - Target grammar point;
   - Source sentence and options (as reference only);
   - Invariant constraints (gap count, option count, correct answer semantics);
   - Explicit instructions on required narrative transformation.
3. **Generation Engine**: Generates adapted item with clean JSON output.
4. **Automated Structural Validation**: Asserts:
   - Valid JSON;
   - Exact gap count match;
   - Exact option count match;
   - Single choice has exactly 1 correct; multiple choice has matching correct count.
5. **Similarity Gate**: Computes Jaccard/Levenshtein scores and assigns status (`VALIDATED` vs `REVIEW_REQUIRED`).
6. **Editorial Review**: Human-in-the-loop review interface for flagged items.
7. **Approval & Production Staging**: Marked `APPROVED` and ready for compilation into production SQLite and Universal JSON.

---

## 8. ROLLBACK STRATEGY & SOURCE TRACEABILITY

1. **Foreign Key Mapping**:
   Every adapted question preserves `source_question_id`. At any moment, any adapted question can be compared against its exact source in `data/staging.db` or `universal_lessons_final_enriched.json`.
2. **Selective Rollback**:
   An individual exercise, topic, or question can be reverted to `PENDING` without affecting any other part of the corpus.
3. **Full System Fallback**:
   Because `data/staging.db` and `data/cms/english_cms_final_enriched.xlsx` are completely independent and immutable, the system can instantly revert to the source checkpoint if needed.

---

## 9. TEST & VERIFICATION STRATEGY

1. **Schema & Model Tests**:
   - Verify table creation, foreign keys (`PRAGMA foreign_keys = ON;`), and constraints in SQLite.
2. **Invariance Tests**:
   - Assert that for every record in `adapted_questions`, its `response_model`, gap count, and option count match its `source_question_id`.
3. **Similarity Evaluator Unit Tests**:
   - Unit tests covering identical text, shallow synonym substitution, and properly transformed sentences to confirm accurate flagging.
4. **Preview Gate Integration**:
   - Convert adapted records into Universal Lesson JSON format and feed directly through `checkPreviewGate` from `src/preview/server.js` with `allowUnresolved: false`.

---

## 10. REUSE OF EXISTING PROJECT COMPONENTS

The adaptation pipeline maximizes reuse of already implemented and tested modules in this repository:

| Existing Component | Location | Role in Adaptation Pipeline |
| :--- | :--- | :--- |
| **Universal Content Models** | [`src/models/index.js`](file:///c:/projects/English%20Breakfast%20Grammar/src/models/index.js) | Instantiates canonical `Lesson`, `Exercise`, `Question`, `Gap`, and `Option` objects. |
| **Universal Validator** | [`src/validation/index.js`](file:///c:/projects/English%20Breakfast%20Grammar/src/validation/index.js) | Enforces strict validation (`allowUnresolved = false`) on adapted lessons before approval. |
| **Preview Server & Gate** | [`src/preview/server.js`](file:///c:/projects/English%20Breakfast%20Grammar/src/preview/server.js) | Verifies that adapted lessons render cleanly in the interactive student test engine. |
| **CMS-to-JSON Bridge** | [`pipeline/cms/excel_to_json.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/cms/excel_to_json.py) | Reconstructs accepted answers, normalizes `{{gap_1}}` $\to$ `{{gap1}}`, and maps types. |
| **CMS Validator** | [`pipeline/validators/cms_validator.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/validators/cms_validator.py) | Validates exported adapted Excel workbooks across all 12 structural checks. |
| **Staging Importer & DB** | [`pipeline/staging/staging_importer.py`](file:///c:/projects/English%20Breakfast%20Grammar/pipeline/staging/staging_importer.py) | Provides the proven relational database architecture and transaction handling patterns. |

---

## 11. NEXT IMPLEMENTATION STEPS (FOR FUTURE EXECUTION)

When authorized to begin implementation, the execution steps will be:

1. **TASK-011A**: Implement `pipeline/adaptation/similarity_evaluator.py` and unit tests for transformation metrics.
2. **TASK-011B**: Implement `pipeline/adaptation/adaptation_db.py` to initialize `data/adaptation.db` and populate initial `PENDING` records mapped from `data/staging.db`.
3. **TASK-011C**: Implement batch adaptation generator / workbook builder for controlled pilot execution (e.g. 20 exercises in level A1).
4. **TASK-011D**: Review pilot results, verify anti-plagiarism metrics, and finalize production adaptation prompt templates.
