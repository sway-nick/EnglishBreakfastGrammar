# TASK-021 — Complete Anomaly Evidence Package

**Generated**: 2026-10-01T11:51:06.309215+00:00  
**Source of Truth**: [`TASK-021_anomaly_evidence.json`](file:///c:/projects/English%20Breakfast%20Grammar/data/reports/TASK-021_anomaly_evidence.json) (59 records)  
**Zero Modification Rule**: 100% strictly enforced. Databases, statuses, and evaluator logic unchanged.

---

## 1. Classification & Summary Overview

| Category | Records | Primary Classification | Teacher Action Required |
| :--- | :---: | :--- | :--- |
| **Category A** (`{{gap_N}}` in Choice) | 41 | `41` Format Errors (Raw placeholder syntax in choice prompt) | Review format decision (normalize to `_____` vs keep) |
| **Category B** (Syntactic Edge Cases) | 4 | `3` False Positives / `1` Uncertain (QID 3068) | Review copular agreement for QID 3068 ('Was/Were acoustics') |
| **Category C** (Cross Collisions) | 7 pairs | `1` Shared Frame / `2` Formulaic / `2` Suspicious / `2` Duplicates | Review whether duplicate carriers in same exercise need re-prompting |
| **Total Anomaly Records** | **59** | Complete machine evidence documented | External Teacher Review outside Antigravity |

---

## 2. Category A — 41 Choice Questions Containing `{{gap_N}}`

### Mechanical Verification:
1. **Stored in Content?** YES. String literals `{{gap_1}}` (or `{{gap_2}}`) are present in `adapted_questions.adapted_text`.
2. **Schema & Model Rule:** In Universal Content Model, `single_choice` questions do NOT possess `gaps` arrays. The placeholder references a non-existent entity.
3. **Source Representation:** All 41 source questions in `staging.db` use underscore blanks (`_____`), never curly tags.
4. **Renderer Behavior:** `renderChoiceQuestion()` in `src/preview/renderer.js` outputs `esc(q.text)` directly without tag replacement. Learners see raw code syntax `{{gap_1}}` instead of visual blanks.
5. **Mechanical Classification:** **`A. REAL PRODUCTION FORMAT ERROR`** (Unrendered code artifact in choice prompt).

### Sample of Affected QIDs:
- **QIDs 3760–3768** (Level A1, `quiz-443`, Questions 2–6, 8–10): Carrier `B: {{gap_1}}?` instead of `B: _____?`
- **QIDs 3994, 3998, 3999** (Level A1, `quiz-464`, Questions 5, 9, 10): Prompts contain `{{gap_1}}` instead of `_____`.
- **QIDs 4085, 4090, 4091** (Level A2, `quiz-477`, Questions 2, 7, 8): Prompts contain `{{gap_1}}` instead of `_____`.
- **QIDs 2947–2956** (Level A2, `quiz-344`, Questions 1–10): Single choice tense options with `{{gap_1}}` / `{{gap_2}}`.
- **QIDs 2880, 2882, 2888, 2962, 2963, 3076, 3077, 3082, 6180–6189**: Remaining 19 choice items.

---

## 3. Category B — 4 Syntactic / Agreement Edge Cases

### 1. QID 6105 (`quiz-710`, Level B1, Response Model: `gap`)
- **Source**: `7 play / football / after school / in the park / We ⇒ We {{gap_1}}.` (Answer: `play football in the park after school`)
- **Adapted**: `7 practice / basketball / after classes / in the gym / They ⇒ They {{gap_1}}.` (Answer: `practice basketball in the gym after classes`)
- **Validator Rule Triggered**: `Plural/compound subject conflicts with singular verb form 'practice basketball in the gym after classes'.`
- **Technical Root Cause**: Validator heuristic saw plural subject `They` and flagged the answer solely because the ending token `classes` ends with the character `s` (heuristically misclassified as a 3rd person singular verb).
- **Grammatical Reality**: 100% grammatically correct English. Approved previously by AI Semantic Review.
- **Classification**: **`B. VALID ADAPTATION / FALSE POSITIVE`**

### 2. QID 3068 (`quiz-358`, Level A2, Response Model: `gap`)
- **Source Prompt (Gap 4)**: `4 {{gap_4}} (be) it a good concert?` (Answer: `Was`)
- **Adapted Prompt (Gap 4)**: `4 {{gap_4}} (be) the auditorium acoustics satisfactory?` (Answer: `Was`)
- **Validator Rule Triggered**: `Plural/compound subject conflicts with singular verb form 'Was'.`
- **Technical Root Cause & Grammatical Analysis**: In standard English, *acoustics* (the acoustic properties of a venue) is treated as a plural noun taking a plural verb (*"Were the auditorium acoustics satisfactory?"*). Because the target answer is `Was`, there is a legitimate grammatical agreement tension.
- **Classification**: **`C. UNCERTAIN`** (Requires teacher pedagogical review on whether to accept singular usage or rephrase the carrier subject).

### 3. QID 3361 (`quiz-392`, Level A2, Response Model: `single_choice`)
- **Source**: `7 "Whose medicines are these?" "They are not _____. Ask Sally, maybe they are _____"` (Answer: `mine/hers`)
- **Adapted**: `7 "We found expensive wireless headphones in the lecture hall; whose property are they?" "They are certainly not _____. Speak with Clara after class; perhaps they are _____."` (Answer: `mine/hers`)
- **Validator Rule Triggered**: `Plural/compound subject conflicts with singular verb form 'mine/hers'.`
- **Technical Root Cause**: Validator assumed answer ending in `s` is a singular verb; it is actually the possessive pronoun `hers`.
- **Grammatical Reality**: Textbook flawless English.
- **Classification**: **`B. VALID ADAPTATION / FALSE POSITIVE`**

### 4. QID 3365 (`quiz-393`, Level A2, Response Model: `gap`)
- **Source (Gap 3, 4, 7)**: Letter about getting married to Maria and pet tortoise (`her`, `she`, `Its`).
- **Adapted (Gap 3, 4, 7)**: Letter about Dr. Angela's fellowship appointment and solar observatory dome (`her`, `she`, `Its`).
- **Validator Rule Triggered**: `Masculine subject antecedent conflicts with feminine pronoun answer 'her'` & `Plural/compound subject conflicts with singular verb form 'Its'.`
- **Technical Root Cause**: Validator saw `Robert` in the salutation and assumed Robert was the antecedent (ignoring `Dr. Angela`), and flagged `Its` because it ends in `s`.
- **Grammatical Reality**: 100% grammatically correct and referentially coherent.
- **Classification**: **`B. VALID ADAPTATION / FALSE POSITIVE`**

---

## 4. Category C — 7 Cross-Adaptation Duplicate Collisions

| ID | Collided QIDs | Shared Adapted Text | Scope | Phrase Type | Classification |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | 53, 56, 1301 | `Could you tell me {{gap_1}}?` | Cross-exercise | Formulaic English | **`B. ACCEPTABLE FORMULAIC PHRASE`** |
| **2** | 5038, 5054 | `The cat is hiding {{gap_1}} the sofa.` | Cross-exercise (A1) | Repeated content | **`C. SUSPICIOUS DUPLICATE`** |
| **3** | 5044, 5047 | `The car is _____ the house.` | Same exercise (`quiz-590`) | Grammar scaffold | **`A. ACCEPTABLE SHARED FRAME`** (Source identical) |
| **4** | 5160, 5165 | `They _____ listening to music in the evening.` | Same exercise (`quiz-602`) | Repeated content | **`D. GENUINE DUPLICATE`** |
| **5** | 7493, 7513 | `We arrived at the station {{gap_1}} to catch the last train.` | Cross-exercise (A2) | Repeated content | **`C. SUSPICIOUS DUPLICATE`** |
| **6** | 2356, 2344 | `Could you tell me _____?` | Cross-exercise | Formulaic English | **`B. ACCEPTABLE FORMULAIC PHRASE`** |
| **7** | 6739, 6742 | `They completed a _____ hike through the national park.` | Same exercise (`quiz-782`) | Repeated content | **`D. GENUINE DUPLICATE`** |

---

## 5. Summary & Next Steps

- Complete machine evidence is packaged in [`TASK-021_anomaly_evidence.json`](file:///c:/projects/English%20Breakfast%20Grammar/data/reports/TASK-021_anomaly_evidence.json).
- No modifications were made to `adaptation.db`, `staging.db`, or any production logic.
- Ready for supervisor / English teacher pedagogical determination.
