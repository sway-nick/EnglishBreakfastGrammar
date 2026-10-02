# TASK-018A: Consistency Check & Candidate Validation Report

**Generated**: 2026-10-01T08:31:00.335747+00:00  
**Source of Truth Priority**:
1. `data/reports/TASK-017_rejected_evidence.json` (Machine-grounded SQLite evidence)
2. `data/reports/TASK-018_teacher_correction_worksheet.json` (Teacher audit worksheet)

---

## 1. Executive Summary

- **Total Records Inspected**: 28
- **Total PASS (Consistency & Structural Rules)**: **28**
- **Total FAIL**: **0**
- **Candidate Corrections Safe to Proceed**: **17**
- **Candidate Corrections Requiring Regeneration**: **11**

---

## 2. Per-QID Verification Matrix

| QID | Batch | Type | Audit Category | Consistency | Candidate Rules | Evaluator Status | Readiness | Overall Verdict |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **2823** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **2847** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **2894** | Batch 4 | single_choice | B. GENUINE ANSWER-PR... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **2952** | Batch 4 | single_choice | B. GENUINE ANSWER-PR... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **2964** | Batch 4 | single_choice | B. GENUINE ANSWER-PR... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **3067** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **3068** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **3361** | Batch 4 | single_choice | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **3365** | Batch 4 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **3382** | Batch 4 | single_choice | B. GENUINE ANSWER-PR... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **3579** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **3694** | Historical Batch 1 | gap | A. GENUINE GRAMMAR /... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **3917** | Historical Batch 1 | gap | A. GENUINE GRAMMAR /... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **4045** | Historical Batch 1 | gap | A. GENUINE GRAMMAR /... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **4054** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **4188** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **4214** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **4254** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **4501** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **4852** | Batch 4 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **5069** | Historical Batch 1 | single_choice | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **5085** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **5088** | Historical Batch 1 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **5134** | Historical Batch 1 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REJECTED` | REQUIRES_REGENERATION | **PASS** |
| **5142** | Historical Batch 1 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **5144** | Historical Batch 1 | gap | C. GENUINE SHALLOW C... | 0 mismatches | 0 violations | `REVIEW_REQUIRED` | SAFE_PENDING_AI_REVIEW | **PASS** |
| **5736** | Historical Batch 1 | single_choice | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |
| **7139** | Batch 4 | gap | D. LIKELY FALSE POSI... | 0 mismatches | 0 violations | `VALIDATED` | SAFE_TO_PROCEED | **PASS** |

---

## 3. Analysis: Safe to Proceed vs. Requiring Regeneration

### A. Candidate Corrections Safe to Proceed (17 QIDs)

These candidates satisfy all consistency checks, perfectly preserve answer keys and gap structures, and either pass the calibrated similarity evaluator immediately (`VALIDATED`) or trigger minor benign markers (`REVIEW_REQUIRED`) that are pedagogically justified:

| QID | Evaluator Simulated Status | Jaccard | Levenshtein | Matched Shingles | Rationale & Readiness |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **2894** | `VALIDATED` | 0.3182 | 0.3627 | None | SAFE_TO_PROCEED |
| **2964** | `REVIEW_REQUIRED` | 0.2727 | 0.4227 | `don't worry i` | SAFE_PENDING_AI_REVIEW |
| **3361** | `VALIDATED` | 0.1538 | 0.3113 | None | SAFE_TO_PROCEED |
| **3382** | `VALIDATED` | 0.2941 | 0.3684 | None | SAFE_TO_PROCEED |
| **3694** | `VALIDATED` | 0.1667 | 0.2424 | None | SAFE_TO_PROCEED |
| **4045** | `VALIDATED` | 0.0476 | 0.2778 | None | SAFE_TO_PROCEED |
| **4054** | `REVIEW_REQUIRED` | 0.2308 | 0.5323 | None | SAFE_PENDING_AI_REVIEW |
| **4188** | `REVIEW_REQUIRED` | 0.1481 | 0.3434 | `two or three` | SAFE_PENDING_AI_REVIEW |
| **4214** | `VALIDATED` | 0.1667 | 0.3636 | None | SAFE_TO_PROCEED |
| **4501** | `VALIDATED` | 0.1296 | 0.3067 | None | SAFE_TO_PROCEED |
| **5069** | `VALIDATED` | 0.1053 | 0.2571 | None | SAFE_TO_PROCEED |
| **5085** | `REVIEW_REQUIRED` | 0.1739 | 0.3300 | `i will open` | SAFE_PENDING_AI_REVIEW |
| **5088** | `VALIDATED` | 0.1364 | 0.2626 | None | SAFE_TO_PROCEED |
| **5142** | `REVIEW_REQUIRED` | 0.2500 | 0.2571 | `hasn't got a` | SAFE_PENDING_AI_REVIEW |
| **5144** | `REVIEW_REQUIRED` | 0.2500 | 0.1982 | `has she got` | SAFE_PENDING_AI_REVIEW |
| **5736** | `VALIDATED` | 0.1429 | 0.3385 | None | SAFE_TO_PROCEED |
| **7139** | `VALIDATED` | 0.0000 | 0.2029 | None | SAFE_TO_PROCEED |

### B. Candidate Corrections Requiring Regeneration (11 QIDs)

These candidates **PASS** all strict structural and consistency rules, but when evaluated against the automated production similarity engine, they still trigger `REJECTED` (High-confidence shallow copy) due to shared pedagogical sentence scaffolds, prompt quotations, or conversational filler phrases. If submitted as-is to the production pipeline, they would be rejected by the automated gate and require regeneration or deeper structural paraphrasing:

| QID | Evaluator Simulated Status | Jaccard | Levenshtein | Matched Shingles | Rejection Reason / Scaffold Root Cause |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **2823** | `REJECTED` | 0.3497 | 0.4863 | `and we 10`, `and we 4`, `day we 19`, `first night in`, `not be any`, `spend the first`, `stay there for`, `the day we`, `the first night`, `the week we`, `there for the`, `week we 11` | High-confidence shallow copy: verbatim shingle(s) ['and we 10', 'and we 4'] with elevated similarity (Jaccard=0.3497, Lev=0.4863). |
| **2847** | `REJECTED` | 0.3373 | 0.3585 | `and he 4`, `arrive at the`, `get off the`, `jacket and 10`, `take off his` | High-confidence shallow copy: verbatim shingle(s) ['and he 4', 'arrive at the'] with elevated similarity (Jaccard=0.3373, Lev=0.3585). |
| **2952** | `REJECTED` | 0.4615 | 0.4536 | `asked his boss`, `boss for a`, `his boss for`, `lewis asked his` | High-confidence shallow copy: verbatim shingle(s) ['asked his boss', 'boss for a'] with elevated similarity (Jaccard=0.4615, Lev=0.4536). |
| **3067** | `REJECTED` | 0.2959 | 0.4585 | `ever be to`, `never be to`, `you be to`, `you ever be`, `you ever travel`, `you go there` | High-confidence shallow copy: verbatim shingle(s) ['ever be to', 'never be to'] with elevated similarity (Jaccard=0.2959, Lev=0.4585). |
| **3068** | `REJECTED` | 0.3371 | 0.4370 | `ever hear the`, `ever lose your`, `no i 2`, `yes i 7`, `you ever hear`, `you ever lose` | High-confidence shallow copy: verbatim shingle(s) ['ever hear the', 'ever lose your'] with elevated similarity (Jaccard=0.3371, Lev=0.4370). |
| **3365** | `REJECTED` | 0.2585 | 0.3607 | `hear that you`, `news from 2`, `react when you`, `thanks for 1`, `to hear that` | High-confidence shallow copy: verbatim shingle(s) ['hear that you', 'news from 2'] with elevated similarity (Jaccard=0.2585, Lev=0.3607). |
| **3579** | `REJECTED` | 0.4375 | 0.3947 | `me your passport`, `must show me`, `show me your`, `you must show` | High-confidence shallow copy: verbatim shingle(s) ['me your passport', 'must show me'] with elevated similarity (Jaccard=0.4375, Lev=0.3947). |
| **3917** | `REJECTED` | 0.5000 | 0.5000 | `make mistakes often`, `mistakes often you`, `you make mistakes` | High-confidence shallow copy: verbatim shingle(s) ['make mistakes often', 'mistakes often you'] with elevated similarity (Jaccard=0.5000, Lev=0.5000). |
| **4254** | `REJECTED` | 0.2430 | 0.4057 | `come back until`, `not come back` | High-confidence shallow copy: verbatim shingle(s) ['come back until', 'not come back'] with elevated similarity (Jaccard=0.2430, Lev=0.4057). |
| **4852** | `REJECTED` | 0.3300 | 0.4133 | `by the way`, `definitely by the`, `do you know`, `know what 2`, `patrick do you`, `the way what`, `way what 15`, `yes i 1`, `you know what`, `you up in` | High-confidence shallow copy: verbatim shingle(s) ['by the way', 'definitely by the'] with elevated similarity (Jaccard=0.3300, Lev=0.4133). |
| **5134** | `REJECTED` | 0.5000 | 0.5165 | `do you have`, `have you got`, `yes i do` | High-confidence shallow copy: verbatim shingle(s) ['do you have', 'have you got'] with elevated similarity (Jaccard=0.5000, Lev=0.5165). |

---

## 4. Detailed Audit of Any Inconsistencies / Failures

No inconsistencies or critical rule failures were found across all 28 QIDs.
All fields in `data/reports/TASK-018_teacher_correction_worksheet.json` match `data/reports/TASK-017_rejected_evidence.json` exactly.
All candidates preserve the exact source answers, option sets, gap cardinalities, and pedagogical targets.

---

## 5. Strict Governance Confirmations

- **Database Integrity**: `data/adaptation.db` was untouched and remained in read-only state.
- **Production Status**: `VALIDATED = 2,242`, `REJECTED = 28`, `PENDING = 3,526` (Total: 5,796).
- **Evaluator Logic**: Calibrated similarity thresholds, formulas, and weights were completely untouched.
- **Untouched PENDING items**: QIDs 5013–5017 remain untouched in PENDING status.
- **Next Steps**: Awaiting teacher instructions before applying fixes or regenerating the 11 scaffold-bound candidates.
