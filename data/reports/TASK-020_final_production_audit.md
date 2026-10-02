# TASK-020 — Final Production Audit Report

**Audit Verdict**: `ANOMALIES_FOUND`  
**Timestamp**: 2026-10-01T11:42:36.332127+00:00  
**Scope**: Full Corpus (5,796 Questions / 638 Exercises / 225 Lessons)

---

## 1. Final Counts

| Entity | Total | VALIDATED | REJECTED | PENDING | Anomalies |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Questions** | 5,796 | 5,796 (100%) | 0 (0%) | 0 (0%) | 52 |
| **Exercises** | 638 | 638 (100%) | 0 (0%) | 0 (0%) | 0 |
| **Lessons** | 225 | 225 (100%) | 0 (0%) | 0 (0%) | 0 |

- **Total Deterministic Machine Anomalies**: `52`
- **Teacher Review Queue Size**: `259` items
- **Identical Normalized Adaptations**: `0` (0 found)

---

## 2. Machine Audit Summary

- **Database Integrity & PRAGMAs**: Foreign Keys: 0 violations | SQLite integrity: `ok` (both DBs).
- **Staging DB Immutability**: SHA-256 `3fd7250ecbd3956f...` (Exact match).
- **Evaluator Logic Integrity**: Clean (0 uncommitted changes, 0 modified files).
- **Preview Gate Status**: `PASS` (225 / 225 lessons valid, 100% compliant).
- **Jest Test Suite**: `PASS` (24 / 24 tests passed).
- **Python Test Suite**: `PASS` (40 / 40 tests passed).
- **Git Status**: Clean.

---

## 3. Originality & Similarity Metrics (All 5,796 Questions)

| Metric | Min | Mean | Median | P90 | P95 | P99 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Jaccard Similarity** | 0.0 | 0.121 | 0.1 | 0.25 | 0.3 | 0.4545 | 1.0 |
| **Levenshtein Similarity** | 0.0 | 0.3128 | 0.3014 | 0.4375 | 0.4808 | 0.6 | 0.8462 |

- **Jaccard > 0.50**: 20 items | **Jaccard > 0.40**: 84 items
- **Forbidden Shingles Detected**: 256 items
- **Elevated Levenshtein (>= 0.45)**: 479 items

---

## 4. Anomaly Breakdown (52 Total)

1. **Unexpected `{gap_N}` in Choice Questions**: 41 items (Batch 1 / 4 choice items formatted with gap tags instead of blanks `_____`).
2. **Syntactic / Validator Flags**: 4 items (QIDs 6105, 3068, 3361, 3365).
3. **Cross-Adaptation Duplicate Collisions**: 7 items (7 pairs sharing carrier sentences).
4. **Coverage / ID / Mapping / Status / FK**: 0 anomalies.

---

## 5. Top 20 Most Important Anomalies

1. QID 3760: `unexpected_gap_placeholder_in_choice_question`
2. QID 3761: `unexpected_gap_placeholder_in_choice_question`
3. QID 3762: `unexpected_gap_placeholder_in_choice_question`
4. QID 3763: `unexpected_gap_placeholder_in_choice_question`
5. QID 3764: `unexpected_gap_placeholder_in_choice_question`
6. QID 3766: `unexpected_gap_placeholder_in_choice_question`
7. QID 3767: `unexpected_gap_placeholder_in_choice_question`
8. QID 3768: `unexpected_gap_placeholder_in_choice_question`
9. QID 3994: `unexpected_gap_placeholder_in_choice_question`
10. QID 3998: `unexpected_gap_placeholder_in_choice_question`
11. QID 3999: `unexpected_gap_placeholder_in_choice_question`
12. QID 4085: `unexpected_gap_placeholder_in_choice_question`
13. QID 4090: `unexpected_gap_placeholder_in_choice_question`
14. QID 4091: `unexpected_gap_placeholder_in_choice_question`
15. QID 4151: `unexpected_gap_placeholder_in_choice_question`
16. QID 4236: `unexpected_gap_placeholder_in_choice_question`
17. QID 2947: `unexpected_gap_placeholder_in_choice_question`
18. QID 2948: `unexpected_gap_placeholder_in_choice_question`
19. QID 2949: `unexpected_gap_placeholder_in_choice_question`
20. QID 2950: `unexpected_gap_placeholder_in_choice_question`

---

## 6. Teacher Review Queue Breakdown

Full evidence exported to `data/reports/TASK-020_teacher_review_queue.json` (259 items):
- **Section A (Deterministic Anomalies)**: 52 items
- **Section B (Identical Normalized Cases)**: 0 items
- **Section C (Top 100 Similarity Pairs)**: 100 items
- **Section D (Suspicious Cross-Duplicates)**: 7 items
- **Section E (Stratified Random Sample)**: 100 items across A1, A2, B1, B1-B2, B2, C1, Shorts

---

## 7. Audit Verdict

`ANOMALIES_FOUND` — Exported exact machine evidence. No database modifications performed.
