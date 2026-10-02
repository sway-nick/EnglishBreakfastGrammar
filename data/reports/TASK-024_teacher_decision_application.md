# TASK-024 — Teacher Decision Application Report

**Timestamp**: 2026-10-01T12:12:43.587200+00:00  
**Status**: `SUCCESS — COMMITTED ATOMICALLY`  
**Transaction Result**: `COMMITTED` (5 of 5 applied)  

---

## 1. Database State & Counts

- **Questions**: **5,796** `VALIDATED` (0 REJECTED, 0 PENDING)
- **Exercises**: **638** `VALIDATED` (0 REJECTED, 0 PENDING)
- **Lessons**: **225** `VALIDATED` (0 REJECTED, 0 PENDING)
- **Staging DB SHA-256**: `3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded` (100% UNCHANGED)
- **Adaptation DB SHA-256 Before**: `2756ad757b816cf53975d0357eaa3738fa2a0f8a812ae81674e52e394c79e4cd`
- **Adaptation DB SHA-256 After**: `5101bc4690e766ffb443d48dbd6348ea142cfe3720e1aab940e57b7cbf44f60b`
- **SQLite Checks**: `PRAGMA foreign_key_check` = 0 violations | `PRAGMA integrity_check` = `ok`

---

## 2. Affected Scopes

- **Affected Exercises (5)**: `quiz-362, quiz-591, quiz-602, quiz-782, quiz-882`
- **Affected Lessons (5)**: `a1_next_to_under_between_in_front_behind_etc, a1_would_like, a2_on_time_vs_in_time_at_the_end_vs_in_the_end, a2_present_perfect_or_past_simple, b1_compound_adjectives_with_numbers_a_two_day_trip`

---

## 3. The 5 Applied Records

| QID | Level | Response Model | Category | Target Answer(s) | Similarity (Jaccard) | Status |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **3068** | `A2` | `gap` | SEMANTIC_COPULAR_AGREEMENT | `Have you ever heard... (10 answers)` | 0.2342 | `VALIDATED` |
| **5054** | `A1` | `gap` | SUSPICIOUS_DUPLICATE_CROSS_EXERCISE | `behind` | 0.1818 | `VALIDATED` |
| **5165** | `A1` | `single_choice` | GENUINE_DUPLICATE_SAME_EXERCISE | `like` | 0.0769 | `VALIDATED` |
| **7513** | `A2` | `gap` | SUSPICIOUS_DUPLICATE_CROSS_EXERCISE | `in time` | 0.1429 | `VALIDATED` |
| **6742** | `B1` | `single_choice` | GENUINE_DUPLICATE_SAME_EXERCISE | `50-kilometre` | 0.2 | `VALIDATED` |

---

## 4. Exact Before / After Evidence

### QID 3068 — SEMANTIC_COPULAR_AGREEMENT (Worker A)
- **Exercise**: `quiz-362` | **Lesson**: `a2_present_perfect_or_past_simple`
- **Response Model**: `gap` | **Answer Preserved**: `YES` (`['Have you ever heard', "haven't", 'saw', 'Was', 'liked', 'Have you ever lost', 'have', 'did it happen', 'was', 'did you do']`)
- **Teacher Decision**: STATUS: NEEDS FIX -> Candidate sentence 4 replaced with teacher approved wording 'Was the sound quality in the auditorium satisfactory?'. Preserved grammar target, answer 'Was', all other 9 gaps, all answer keys, gap ordering, and response model.
- **Similarity**: Jaccard `0.2342`, Levenshtein `0.3365`, Forbidden Shingles: `0`
- **Old Adapted Text**:
```
Part 1
LEO: 1 {{gap_1}} (ever/you/hear) broadcasts by the Cambridge Baroque Quartet?
TARA: Truly, I 2 {{gap_2}}. Which musical repertoire do they perform?
LEO: Classical chamber works. In fact, my family 3 {{gap_3}} (see) their ensemble performing live last Friday.
TARA: 4 {{gap_4}} (be) the auditorium acoustics satisfactory?
LEO: Exceptionally; audiences 5 {{gap_5}} (like) each symphony.

Part 2
FELIX: At busy airport terminals, 6 {{gap_6}} (ever/you/lose) international travel documents?
NINA: Regrettably, I 7 {{gap_7}}.
FELIX: Along which flight corridor 8 {{gap_8}} (it/happen)?
NINA: In Zurich; an oversized boarding envelope 9 {{gap_9}} (be) misplaced during customs transfers.
FELIX: Afterward, what emergency procedures 10 {{gap_10}} (you/do)?
```
- **New Adapted Text**:
```
Part 1
LEO: 1 {{gap_1}} (ever/you/hear) broadcasts by the Cambridge Baroque Quartet?
TARA: Truly, I 2 {{gap_2}}. Which musical repertoire do they perform?
LEO: Classical chamber works. In fact, my family 3 {{gap_3}} (see) their ensemble performing live last Friday.
TARA: 4 {{gap_4}} (be) the sound quality in the auditorium satisfactory?
LEO: Exceptionally; audiences 5 {{gap_5}} (like) each symphony.

Part 2
FELIX: At busy airport terminals, 6 {{gap_6}} (ever/you/lose) international travel documents?
NINA: Regrettably, I 7 {{gap_7}}.
FELIX: Along which flight corridor 8 {{gap_8}} (it/happen)?
NINA: In Zurich; an oversized boarding envelope 9 {{gap_9}} (be) misplaced during customs transfers.
FELIX: Afterward, what emergency procedures 10 {{gap_10}} (you/do)?
```

---

### QID 5054 — SUSPICIOUS_DUPLICATE_CROSS_EXERCISE (Worker B)
- **Exercise**: `quiz-591` | **Lesson**: `a1_next_to_under_between_in_front_behind_etc`
- **Response Model**: `gap` | **Answer Preserved**: `YES` (`['behind']`)
- **Teacher Decision**: STATUS: APPROVED -> Applied approved candidate text 'Sophie is standing {{gap_1}} Liam in the ticket queue.' (Answer: 'behind'). Breaks carrier collision with QID 5038.
- **Similarity**: Jaccard `0.1818`, Levenshtein `0.3721`, Forbidden Shingles: `0`
- **Old Adapted Text**:
```
The cat is hiding {{gap_1}} the sofa.
```
- **New Adapted Text**:
```
Sophie is standing {{gap_1}} Liam in the ticket queue.
```

---

### QID 5165 — GENUINE_DUPLICATE_SAME_EXERCISE (Worker C)
- **Exercise**: `quiz-602` | **Lesson**: `a1_would_like`
- **Response Model**: `single_choice` | **Answer Preserved**: `YES` (`['like']`)
- **Teacher Decision**: STATUS: APPROVED -> Applied approved candidate text 'We _____ reading novels in the park on sunny afternoons.' (Answer: 'like'). Breaks duplicate carrier with QID 5160. Preserved original options exactly.
- **Similarity**: Jaccard `0.0769`, Levenshtein `0.2857`, Forbidden Shingles: `0`
- **Old Adapted Text**:
```
They _____ listening to music in the evening.
```
- **New Adapted Text**:
```
We _____ reading novels in the park on sunny afternoons.
```

---

### QID 7513 — SUSPICIOUS_DUPLICATE_CROSS_EXERCISE (Worker D)
- **Exercise**: `quiz-882` | **Lesson**: `a2_on_time_vs_in_time_at_the_end_vs_in_the_end`
- **Response Model**: `gap` | **Answer Preserved**: `YES` (`['in time']`)
- **Teacher Decision**: STATUS: APPROVED -> Applied approved candidate text 'The technician finished repairing the laptop {{gap_1}} for my online presentation.' (Answer: 'in time'). Breaks carrier collision with QID 7493.
- **Similarity**: Jaccard `0.1429`, Levenshtein `0.2958`, Forbidden Shingles: `0`
- **Old Adapted Text**:
```
We arrived at the station {{gap_1}} to catch the last train.
```
- **New Adapted Text**:
```
The technician finished repairing the laptop {{gap_1}} for my online presentation.
```

---

### QID 6742 — GENUINE_DUPLICATE_SAME_EXERCISE (Worker E)
- **Exercise**: `quiz-782` | **Lesson**: `b1_compound_adjectives_with_numbers_a_two_day_trip`
- **Response Model**: `single_choice` | **Answer Preserved**: `YES` (`['50-kilometre']`)
- **Teacher Decision**: STATUS: APPROVED -> Applied approved candidate text 'Engineers constructed a _____ tunnel beneath the Alpine ridge.' (Answer: '50-kilometre'). Breaks duplicate carrier with QID 6739. Preserved original options exactly.
- **Similarity**: Jaccard `0.2`, Levenshtein `0.3281`, Forbidden Shingles: `0`
- **Old Adapted Text**:
```
They completed a _____ hike through the national park.
```
- **New Adapted Text**:
```
Engineers constructed a _____ tunnel beneath the Alpine ridge.
```

---
