# TASK-017: Machine-Grounded Audit of All Remaining REJECTED Records

**Audit Generated**: `2026-10-01T08:10:27.660775+00:00`  
**Source Databases**: `data/adaptation.db`, `data/staging.db`  
**Corpus State**: VALIDATED=2242, REJECTED=28, PENDING=3526, TOTAL=5796  

---

## 1. Summary Verification Metrics

| Metric | Count | Note |
|:---|---:|:---|
| **Total Target QIDs** | `28` | Exactly 14 Historical Batch 1 + 14 Batch 4 |
| **QIDs Found in Database** | `28` | All 28 resolved directly from SQLite |
| **QIDs Missing** | `0` | Zero missing records |
| **Duplicate QIDs** | `0` | Zero duplicate records in `adapted_questions` |
| **Staging/Adaptation Mismatches** | `0` | 100% ID and Response Model parity |
| **Records with Answer Divergence** | `4` | 4 Batch 4 items diverged during Gemini generation |
| **Rejected by Similarity / Shingles** | `19` | 10 in Batch 1 (uncalibrated 3-word rule) + 9 in Batch 4 |
| **Rejected by Structural / Grammar Validity** | `9` | 4 in Batch 1 (article / agreement / gender) + 5 in Batch 4 (agreement / gender) |
| **Rejected by AI Review** | `4` | 4 Batch 4 items flagged for answer divergence |
| **Insufficient Evidence Records** | `0` | Zero records with missing fields |

---

## 2. Compact Tabular Overview

| QID | Batch | Level | Model | Preserved? | Jaccard | Levenshtein | Primary Rejection Mechanism |
|:---|:---|:---|:---|:---:|---:|---:|:---|
| **3694** | Historical Batch 1 | A1 | `gap` | YES | 0.0000 | 0.2105 | Grammar / Agreement |
| **3917** | Historical Batch 1 | A1 | `gap` | YES | 0.0000 | 0.3191 | Grammar / Agreement |
| **4254** | Historical Batch 1 | A1 | `gap` | YES | 0.1398 | 0.4558 | Similarity / Shingle |
| **4214** | Historical Batch 1 | A1 | `gap` | YES | 0.2000 | 0.4727 | Similarity / Shingle |
| **5736** | Historical Batch 1 | A1 | `single_choice` | YES | 0.1667 | 0.3061 | Similarity / Shingle |
| **5134** | Historical Batch 1 | A1 | `gap` | YES | 0.6667 | 0.7544 | Similarity / Shingle |
| **5142** | Historical Batch 1 | A1 | `gap` | YES | 0.4286 | 0.6000 | Similarity / Shingle |
| **5144** | Historical Batch 1 | A1 | `gap` | YES | 0.6000 | 0.6552 | Similarity / Shingle |
| **5069** | Historical Batch 1 | A1 | `single_choice` | YES | 0.3571 | 0.5000 | Similarity / Shingle |
| **5085** | Historical Batch 1 | A1 | `gap` | YES | 0.1579 | 0.3506 | Similarity / Shingle |
| **5088** | Historical Batch 1 | A1 | `gap` | YES | 0.1429 | 0.4375 | Similarity / Shingle |
| **4188** | Historical Batch 1 | A1 | `gap` | YES | 0.2381 | 0.3614 | Similarity / Shingle |
| **4045** | Historical Batch 1 | A1 | `gap` | YES | 0.0625 | 0.2766 | Grammar / Agreement |
| **4054** | Historical Batch 1 | A1 | `gap` | YES | 0.1429 | 0.3382 | Grammar / Agreement |
| **2847** | Batch 4 | A2 | `gap` | YES | 0.2037 | 0.3477 | Similarity / Shingle |
| **2823** | Batch 4 | A2 | `gap` | YES | 0.3712 | 0.5485 | Similarity / Shingle, Grammar / Agreement |
| **4501** | Batch 4 | A2 | `gap` | YES | 0.1860 | 0.3512 | Similarity / Shingle |
| **2964** | Batch 4 | A2 | `single_choice` | **NO** | 0.2000 | 0.3115 | AI Review (Answer Divergence) |
| **3067** | Batch 4 | A2 | `gap` | YES | 0.3077 | 0.5799 | Similarity / Shingle |
| **3068** | Batch 4 | A2 | `gap` | YES | 0.3784 | 0.5737 | Similarity / Shingle, Grammar / Agreement |
| **3579** | Batch 4 | A2 | `gap` | YES | 0.3846 | 0.5250 | Similarity / Shingle |
| **4852** | Batch 4 | A2 | `gap` | YES | 0.2062 | 0.3459 | Similarity / Shingle |
| **3382** | Batch 4 | A2 | `single_choice` | **NO** | 0.0526 | 0.3188 | AI Review (Answer Divergence) |
| **7139** | Batch 4 | A2 | `gap` | YES | 0.0769 | 0.2973 | Grammar / Agreement |
| **3361** | Batch 4 | A2 | `single_choice` | YES | 0.1579 | 0.4937 | Similarity / Shingle, Grammar / Agreement |
| **3365** | Batch 4 | A2 | `gap` | YES | 0.1241 | 0.3014 | Grammar / Agreement |
| **2952** | Batch 4 | A2 | `single_choice` | **NO** | 0.1250 | 0.4906 | Similarity / Shingle, AI Review (Answer Divergence) |
| **2894** | Batch 4 | A2 | `single_choice` | **NO** | 0.3750 | 0.5079 | AI Review (Answer Divergence) |

---

## 3. Detailed Machine Evidence per QID

### QID 3694 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-426` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `2 src / 2 adp` | Options: `0 src / 0 adp` | Answers: `2 src / 2 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.0`, Levenshtein: `0.2105`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Indefinite article 'an' is ungrammatical before plural noun 'enormous'.`

**Source Text**:
```text
9 {{gap_1}} elephant ⇒ {{gap_2}}
```

**Source Answers**: `["an", "elephants"]`

**Adapted Text**:
```text
9 {{gap_1}} enormous animal ⇒ two {{gap_2}}
```

**Adapted Answers**: `["an", "elephants"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "Indefinite article 'an' is ungrammatical before plural noun 'enormous'."]`

---

### QID 3917 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-449` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.0`, Levenshtein: `0.3191`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; singular_plural: Subject/demonstrative number shifted between singular and plural.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Plural/compound subject conflicts with singular verb form 'often make mistakes'.`

**Source Text**:
```text
9 You make mistakes. (often) ⇒ You {{gap_1}}.
```

**Source Answers**: `["often make mistakes"]`

**Adapted Text**:
```text
They create errors during practice. (often) ⇒ They {{gap_1}}.
```

**Adapted Answers**: `["often make mistakes"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "singular_plural: Subject/demonstrative number shifted between singular and plural.", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).", "Plural/compound subject conflicts with singular verb form 'often make mistakes'."]`

---

### QID 4254 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-488` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `10 src / 10 adp` | Options: `0 src / 0 adp` | Answers: `10 src / 10 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.1398`, Levenshtein: `0.4558`)
- **Matched Shingles**: `["and then they"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'and then they'; gender: Gender of primary person shifted.; countability: Countable vs uncountable noun environment shifted.`

**Source Text**:
```text
Hi Tim, How are you? 1 {{gap_1}} (you/visit) us this summer? In July we 2 {{gap_2}} (have) a big party. It 3 {{gap_3}} (be) really fun. I want to have some great music, so I 4 {{gap_4}} (find) a good DJ. My parents 5 {{gap_5}} (pay) for the food and drinks. My sister 6 {{gap_6}} (not be) there because she 7 {{gap_7}} (travel) to Canada with a friend. Sorry! They 8 {{gap_8}} (fly) to Montreal and then they 9 {{gap_9}} (go) to Vancouver by train. They 10 {{gap_10}} (not come) back until August. Hope you can come to the party! Ben
```

**Source Answers**: `["Are you going to visit", "are going to have", "is going to be", "am going to find", "are going to pay", "isn't going to be", "is going to travel", "are going to fly", "are going to go", "aren't going to come"]`

**Adapted Text**:
```text
Dear Sam, {{gap_1}} (you/visit) our new home next month? Soon we {{gap_2}} (have) a family dinner. It {{gap_3}} (be) an exciting day. I need a place to work, so I {{gap_4}} (find) a quiet desk. My cousins {{gap_5}} (pay) for all the groceries. My brother {{gap_6}} (not be) available because he {{gap_7}} (travel) across Spain soon. My friends said they {{gap_8}} (fly) to Madrid and then they {{gap_9}} (go) to Seville. They {{gap_10}} (not come) home soon. Best, Leo
```

**Adapted Answers**: `["Are you going to visit", "are going to have", "is going to be", "am going to find", "are going to pay", "isn't going to be", "is going to travel", "are going to fly", "are going to go", "aren't going to come"]`

**Validation Flags**: `["Verbatim shingle detected 'and then they' with moderate/low similarity (Jaccard=0.1398 <= 0.40, Lev=0.4558 < 0.55). Routed to AI review.", "gender: Gender of primary person shifted.", "countability: Countable vs uncountable noun environment shifted."]`

---

### QID 4214 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-482` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.2`, Levenshtein: `0.4727`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'is noisy the'`

**Source Text**:
```text
2 This bar is {{gap_1}} (noisy) the bars in my street.
```

**Source Answers**: `["noisier than"]`

**Adapted Text**:
```text
The central market is {{gap_1}} (noisy) the shops near our school.
```

**Adapted Answers**: `["noisier than"]`

**Validation Flags**: `["Normalized Levenshtein similarity (0.4727) exceeds threshold (< 0.45) on standard text (len=55)."]`

---

### QID 5736 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-670` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `4 src / 4 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.1667`, Levenshtein: `0.3061`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'p m then'; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`

**Source Text**:
```text
2 I get home at around 7 p.m., _____ then I make dinner.
```

**Source Answers**: `["and"]`
**Source Options**: 1. but ; 2. and [CORRECT]; 3. or ; 4. because 

**Adapted Text**:
```text
She finishes work at 5 p.m., _____ then she goes for a run.
```

**Adapted Answers**: `["and"]`
**Adapted Options**: 1. but ; 2. and [CORRECT]; 3. or ; 4. because 

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person)."]`

---

### QID 5134 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-599` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.6667`, Levenshtein: `0.7544`)
- **Matched Shingles**: `["yes i do", "you got a"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'a do you' (+6 more); Jaccard token similarity (0.7000) exceeds rejection threshold (> 0.50).`

**Source Text**:
```text
6 A: Do you have a laptop? B: Yes, I do. ⇒ A: Have you got a laptop? B: Yes, I {{gap_1}}.
```

**Source Answers**: `["have"]`

**Adapted Text**:
```text
A: Do you own a camera? B: Yes, I do. ⇒ A: Have you got a camera? B: Yes, I {{gap_1}}.
```

**Adapted Answers**: `["have"]`

**Validation Flags**: `["Jaccard token similarity (0.6667) exceeds rejection threshold (> 0.50).", "High-confidence shallow copy: verbatim shingle(s) ['yes i do', 'you got a'] with elevated similarity (Jaccard=0.6667, Lev=0.7544)."]`

---

### QID 5142 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-600` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.4286`, Levenshtein: `0.6`)
- **Matched Shingles**: `["hasn't got a"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'hasn't got a'; Jaccard token similarity (0.4286) is in review zone (0.40 < J <= 0.50).; gender: Gender of primary person shifted.`

**Source Text**:
```text
4 She hasn't got a sister. ⇒ She {{gap_1}} a sister.
```

**Source Answers**: `["didn't have"]`

**Adapted Text**:
```text
He hasn't got a bicycle. ⇒ He {{gap_1}} a bicycle.
```

**Adapted Answers**: `["didn't have"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) [\"hasn't got a\"] with elevated similarity (Jaccard=0.4286, Lev=0.6000).", "gender: Gender of primary person shifted."]`

---

### QID 5144 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-600` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.6`, Levenshtein: `0.6552`)
- **Matched Shingles**: `["has got a"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'has got a'; Jaccard token similarity (0.6000) exceeds rejection threshold (> 0.50).`

**Source Text**:
```text
6 Has she got a cold? ⇒ {{gap_1}} a cold?
```

**Source Answers**: `["Did she have"]`

**Adapted Text**:
```text
Has she got a ticket? ⇒ {{gap_1}} a ticket?
```

**Adapted Answers**: `["Did she have"]`

**Validation Flags**: `["Jaccard token similarity (0.6000) exceeds rejection threshold (> 0.50).", "High-confidence shallow copy: verbatim shingle(s) ['has got a'] with elevated similarity (Jaccard=0.6000, Lev=0.6552)."]`

---

### QID 5069 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-593` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.3571`, Levenshtein: `0.5`)
- **Matched Shingles**: `["there is a"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'there is a'`

**Source Text**:
```text
1 _____ to the cinema. There is a good film today.
```

**Source Answers**: `["Let's go"]`
**Source Options**: 1. You go ; 2. Don't go ; 3. Let's go [CORRECT]

**Adapted Text**:
```text
_____ to the museum. There is a new exhibit this week.
```

**Adapted Answers**: `["Let's go"]`
**Adapted Options**: 1. You go ; 2. Don't go ; 3. Let's go [CORRECT]

**Validation Flags**: `["Verbatim shingle detected 'there is a' with moderate/low similarity (Jaccard=0.3571 <= 0.40, Lev=0.5000 < 0.55). Routed to AI review."]`

---

### QID 5085 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-594` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.1579`, Levenshtein: `0.3506`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'a i will'`

**Source Text**:
```text
7 A: 'I will open a bottle of wine.' B: 'No, {{gap_1}} a bottle of wine, please. I prefer beer.
```

**Source Answers**: `["don't open"]`

**Adapted Text**:
```text
A: 'I will open the front door.' B: 'Please {{gap_1}} the door yet because it is freezing outside.'
```

**Adapted Answers**: `["don't open"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles)."]`

---

### QID 5088 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-594` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.1429`, Levenshtein: `0.4375`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'b no about'; singular_plural: Subject/demonstrative number shifted between singular and plural.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`

**Source Text**:
```text
10 A: 'Do you want to talk about work?' B: 'No, {{gap_1}} about work. Let's talk about something different.'
```

**Source Answers**: `["let's not talk"]`

**Adapted Text**:
```text
A: "Should we talk about politics?" B: "No, {{gap_1}} about politics during dinner."
```

**Adapted Answers**: `["let's not talk"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "singular_plural: Subject/demonstrative number shifted between singular and plural.", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person)."]`

---

### QID 4188 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-479` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.2381`, Levenshtein: `0.3614`)
- **Matched Shingles**: `["two or three"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Forbidden verbatim 3+ word shingle detected: 'two or three'; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`

**Source Text**:
```text
5 They only scored one goal. They didn't have {{gap_1}} opportunities to score; maybe two or three.
```

**Source Answers**: `["many"]`

**Adapted Text**:
```text
We didn't buy {{gap_1}} apples at the market today; only two or three.
```

**Adapted Answers**: `["many"]`

**Validation Flags**: `["Verbatim shingle detected 'two or three' with moderate/low similarity (Jaccard=0.2381 <= 0.40, Lev=0.3614 < 0.55). Routed to AI review.", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person)."]`

---

### QID 4045 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-462` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.0625`, Levenshtein: `0.2766`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; singular_plural: Subject/demonstrative number shifted between singular and plural.; gender: Gender of primary person shifted.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Feminine subject antecedent conflicts with masculine pronoun answer 'him'.`

**Source Text**:
```text
10 That man over there is David. I work with {{gap_1}}.
```

**Source Answers**: `["him"]`
**Source Options**: 1. he ; 2. him [CORRECT]; 3. her 

**Adapted Text**:
```text
The chef is in the kitchen and Sarah is helping {{gap_1}}.
```

**Adapted Answers**: `["him"]`
**Adapted Options**: 1. he ; 2. him [CORRECT]; 3. her 

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "singular_plural: Subject/demonstrative number shifted between singular and plural.", "gender: Gender of primary person shifted.", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).", "Feminine subject antecedent conflicts with masculine pronoun answer 'him'."]`

---

### QID 4054 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-463` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-09-30T20:34:16.820922+00:00` | **Last Updated**: `2026-09-30T20:34:16.820922+00:00`
- **Cardinality**: Gaps: `2 src / 2 adp` | Options: `0 src / 0 adp` | Answers: `2 src / 2 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.1429`, Levenshtein: `0.3382`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; gender: Gender of primary person shifted.; Masculine subject antecedent conflicts with feminine pronoun answer 'her'.`

**Source Text**:
```text
5 Suzan and Tom call their daughter every day. ⇒ {{gap_1}} call {{gap_2}} every day.
```

**Source Answers**: `["They", "her"]`

**Adapted Text**:
```text
Peter and Mark visit their grandmother on weekends. ⇒ {{gap_1}} visit {{gap_2}} on weekends.
```

**Adapted Answers**: `["They", "her"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "gender: Gender of primary person shifted.", "Masculine subject antecedent conflicts with feminine pronoun answer 'her'."]`

---

### QID 2847 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-331` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `20 src / 20 adp` | Options: `0 src / 0 adp` | Answers: `20 src / 20 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.2037`, Levenshtein: `0.3477`)
- **Matched Shingles**: `["arrive at the", "get of the"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['arrive at the', 'get of the'] with elevated similarity (Jaccard=0.2037, Lev=0.3477).`

**Source Text**:
```text
When I 1 {{gap_1}} (arrive) at the station, Raimond 2 {{gap_2}} (wait) for me. He 3 {{gap_3}} (wear) a nice black suit and he 4 {{gap_4}} (hold) a red rose in his right hand. When I 5 {{gap_5}} (get off) the train, he 6 {{gap_6}} (run) up to me and 7 {{gap_7}} (kiss) me passionately. It 8 {{gap_8}} (rain) heavily so he 9 {{gap_9}} (take off) his jacket and 10 {{gap_10}} (put) it over my head. I 11 {{gap_11}} (tell) Raimond to go to a café so that we could talk, but he 12 {{gap_12}} (insist) on going to another place. While he 13 {{gap_13}} (drive), I 14 {{gap_14}} (throw) a look at him. He 15 {{gap_15}} (smile) all the time, but he also 16 {{gap_16}} (look) nervous. He finally 17 {{gap_17}} (stop) his car on the top of a hill with fantastic views. It was so wonderful. We 18 {{gap_18}} (get out) of the car, and he 19 {{gap_19}} (kneel) in front of me and 20 {{gap_20}} (take) a ring out of his pocket. “Kathy, will you...” he said. “Listen, Raimond, I want to break up with you,” I interrupted.
```

**Source Answers**: `["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"]`

**Adapted Text**:
```text
When the guest {{gap_1}} (arrive) at the venue, the host {{gap_2}} (wait) near the entrance. She {{gap_3}} (wear) a bright blue dress, and she {{gap_4}} (hold) a clipboard in her left hand. As soon as I {{gap_5}} (get off) the bus, the organizer {{gap_6}} (run) towards the door and {{gap_7}} (kiss) her colleague on both cheeks. It {{gap_8}} (rain) outside, so the driver {{gap_9}} (take off) his wet coat and {{gap_10}} (put) it in the trunk. The manager {{gap_11}} (tell) the staff to start the meeting, but the director {{gap_12}} (insist) on waiting a bit longer. While the chauffeur {{gap_13}} (drive) through the city, the passenger {{gap_14}} (throw) a glance out the window. The tour guide {{gap_15}} (smile) warmly, though he {{gap_16}} (look) tired after the long journey. The bus driver {{gap_17}} (stop) near the park entrance. Everyone {{gap_18}} (get out) of the vehicle, and a young athlete {{gap_19}} (knelt) beside the track and {{gap_20}} (take) his running shoes out of a bag.
```

**Adapted Answers**: `["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['arrive at the', 'get of the'] with elevated similarity (Jaccard=0.2037, Lev=0.3477)."]`

---

### QID 2823 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-326` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `20 src / 20 adp` | Options: `0 src / 0 adp` | Answers: `20 src / 20 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.3712`, Levenshtein: `0.5485`)
- **Matched Shingles**: `["and it 16", "and we 4", "but it 18", "but we 15", "not be any", "stay there for", "when we 5"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['and it 16', 'and we 4'] with elevated similarity (Jaccard=0.3712, Lev=0.5485).; countability: Countable vs uncountable noun environment shifted.; Plural/compound subject conflicts with singular verb form 'was'.; Plural/compound subject conflicts with singular verb form 'was'.`

**Source Text**:
```text
Two summers ago we 1 {{gap_1}} (have) a holiday in Scotland. We 2 {{gap_2}} (drive) there from London, but our car 3 {{gap_3}} (break) down on the motorway and we 4 {{gap_4}} (spend) the first night in Birmingham. When we 5 {{gap_5}} (get) to Edinburgh we 6 {{gap_6}} (not can) find a good hotel - there 7 {{gap_7}} (not be) any available rooms. We 8 {{gap_8}} (not know) what to do but in the end we 9 {{gap_9}} (find) a bed and breakfast and we 10 {{gap_10}} (stay) there for the week. We 11 {{gap_11}} (see) the castle, 12 {{gap_12}} (go) to the Arts Festival, and we 13 {{gap_13}} (buy) a lot of souvenirs. We 14 {{gap_14}} (want) to go to Loch Ness but we 15 {{gap_15}} (not have) much time and it 16 {{gap_16}} (be) quite far away. The weather 17 {{gap_17}} (be) good, but it 18 {{gap_18}} (start) raining the day we 19 {{gap_19}} (leave). We 20 {{gap_20}} (have) a great time.
```

**Source Answers**: `["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"]`

**Adapted Text**:
```text
Last winter we 1 {{gap_1}} (have) a trip in France. We 2 {{gap_2}} (drive) through the countryside, but a pipe 3 {{gap_3}} (break) in the engine and we 4 {{gap_4}} (spend) two hours in a village. When we 5 {{gap_5}} (get) to Paris we 6 {{gap_6}} (not can) locate our rental home - there 7 {{gap_7}} (not be) any street signs nearby. We 8 {{gap_8}} (not know) the directions, but finally we 9 {{gap_9}} (find) a cozy apartment and 10 {{gap_10}} (stay) there for seven days. We 11 {{gap_11}} (see) the famous tower, 12 {{gap_12}} (go) to local museums, and 13 {{gap_13}} (buy) some gifts. We 14 {{gap_14}} (want) to visit a vineyard, but we 15 {{gap_15}} (not have) enough cash and it 16 {{gap_16}} (be) too remote. The atmosphere 17 {{gap_17}} (be) wonderful, but it 18 {{gap_18}} (start) snowing heavily when we 19 {{gap_19}} (leave). Overall, we 20 {{gap_20}} (have) a memorable journey.
```

**Adapted Answers**: `["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['and it 16', 'and we 4'] with elevated similarity (Jaccard=0.3712, Lev=0.5485).", "countability: Countable vs uncountable noun environment shifted.", "Plural/compound subject conflicts with singular verb form 'was'."]`

---

### QID 4501 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-345` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `3 src / 3 adp` | Options: `9 src / 9 adp` | Answers: `3 src / 3 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.186`, Levenshtein: `0.3512`)
- **Matched Shingles**: `["not yet because", "yet because i"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['not yet because', 'yet because i'] with elevated similarity (Jaccard=0.1860, Lev=0.3512).; singular_plural: Subject/demonstrative number shifted between singular and plural.`

**Source Text**:
```text
Dialogue 2 ROY: What time 5 {{gap_1}} tomorrow? VALERIA: Very early. I 6 {{gap_2}} the 6.50 train. ROY: Do you have the ticket? VALERIA: Not yet, because I 7 {{gap_3}} it online when I arrive home.
```

**Source Answers**: `["are you leaving", "'m taking", "'m going to buy"]`
**Source Options**: 1. are you going to leave ; 1. will take ; 1. 'm buying ; 2. will you leave ; 2. 'm going to take ; 2. 'm going to buy [CORRECT]; 3. are you leaving [CORRECT]; 3. 'm taking [CORRECT]; 3. 'll buy 

**Adapted Text**:
```text
LUCAS: When {{gap_1}} for the conference? SOPHIA: Early in the morning. I {{gap_2}} the morning flight. LUCAS: Have you reserved your seat? SOPHIA: Not yet, because I {{gap_3}} a pass on the mobile app later.
```

**Adapted Answers**: `["are you leaving", "'m taking", "'m going to buy"]`
**Adapted Options**: 1. are you going to leave ; 1. will take ; 1. 'm buying ; 2. will you leave ; 2. 'm going to take ; 2. 'm going to buy [CORRECT]; 3. are you leaving [CORRECT]; 3. 'm taking [CORRECT]; 3. 'll buy 

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['not yet because', 'yet because i'] with elevated similarity (Jaccard=0.1860, Lev=0.3512).", "singular_plural: Subject/demonstrative number shifted between singular and plural."]`

---

### QID 2964 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-346` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `False`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.2`, Levenshtein: `0.3115`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `REJECT` | **AI Reason**: `Answer divergence: target answer not preserved in adapted context.`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Correct answer diverged from source: source=["'ll read"], adapted=["'ll carry"]. Flagged for review.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`

**Source Text**:
```text
7 A: 'I can't see without my glasses.' B: 'Don't worry. I _____ the letter for you.'
```

**Source Answers**: `["'ll read"]`
**Source Options**: 1. 'll read [CORRECT]; 2. 'm reading ; 3. 'm going to read 

**Adapted Text**:
```text
A: "My heavy bag is difficult to carry." B: "Stay calm. I _____ it for you."
```

**Adapted Answers**: `["'ll carry"]`
**Adapted Options**: 1. 'll carry [CORRECT]; 2. 'm carrying ; 3. 'm going to carry 

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "Correct answer diverged from source: source=[\"'ll read\"], adapted=[\"'ll carry\"]. Flagged for review."]`

---

### QID 3067 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-361` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `10 src / 10 adp` | Options: `0 src / 0 adp` | Answers: `10 src / 10 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.3077`, Levenshtein: `0.5799`)
- **Matched Shingles**: `["yes i 4", "yes it 9"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['yes i 4', 'yes it 9'] with elevated similarity (Jaccard=0.3077, Lev=0.5799).; gender: Gender of primary person shifted.`

**Source Text**:
```text
PETER: 1 {{gap_1}} (you/ever/be) to England? LAURA: I 2 {{gap_2}} (never/be) to England, but I’d like to go someday. And you? 3 {{gap_3}} (you/ever/travel) to England? PETER: Yes. I 4 {{gap_4}} (be) there four times. In fact, I 5 {{gap_5}} (travel) to many English speaking countries. LAURA: 6 {{gap_6}} (you/be) to Australia, too? PETER: Yes, of course. LAURA: When 7 {{gap_7}} (you/go) there? PETER: Last year, during my Christmas holiday. LAURA: 8 {{gap_8}} (you/like) it? PETER: Yes, it 9 {{gap_9}} (be) fantastic! We 10 {{gap_10}} (spend) 12 incredible days there.
```

**Source Answers**: `["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"]`

**Adapted Text**:
```text
MARK: 1 {{gap_1}} (you/ever/be) to Japan? ANNA: I 2 {{gap_2}} (never/be) to Japan, but I hope to visit soon. What about you? 3 {{gap_3}} (you/ever/travel) to Asia? MARK: Yes. I 4 {{gap_4}} (be) there three times. Actually, I 5 {{gap_5}} (travel) to several foreign countries. ANNA: 6 {{gap_6}} (you/be) to South Korea as well? MARK: Yes, definitely. ANNA: When 7 {{gap_7}} (you/go) there? MARK: Two years ago, during summer break. ANNA: 8 {{gap_8}} (you/like) the trip? MARK: Yes, it 9 {{gap_9}} (be) amazing! We 10 {{gap_10}} (spend) two memorable weeks exploring.
```

**Adapted Answers**: `["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['yes i 4', 'yes it 9'] with elevated similarity (Jaccard=0.3077, Lev=0.5799).", "gender: Gender of primary person shifted."]`

---

### QID 3068 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-362` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `10 src / 10 adp` | Options: `0 src / 0 adp` | Answers: `10 src / 10 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.3784`, Levenshtein: `0.5737`)
- **Matched Shingles**: `["i really 5", "no i 2", "yes i 7", "yes i really"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['i really 5', 'no i 2'] with elevated similarity (Jaccard=0.3784, Lev=0.5737).; Plural/compound subject conflicts with singular verb form 'Was'.; Plural/compound subject conflicts with singular verb form 'was'.`

**Source Text**:
```text
Dialogue 1 MARK: 1 {{gap_1}} (you/ever/hear) the group The Darkness? BIANCA: No, I 2 {{gap_2}}. What kind of music do they play? MARK: Rock music. I 3 {{gap_3}} (see) them in concert last night. BIANCA: 4 {{gap_4}} (be) it a good concert? MARK: Yes, I really 5 {{gap_5}} (like) it. Dialogue 2 ANDY: 6 {{gap_6}} (you/ever/lose) your car keys? BART: Yes, I 7 {{gap_7}}. ANDY: Where 8 {{gap_8}} (it/happen)? BART: In Portugal. I 9 {{gap_9}} (be) there on holiday. ANDY: What 10 {{gap_10}} (you/do)?
```

**Source Answers**: `["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"]`

**Adapted Text**:
```text
Dialogue 1 SAM: 1 {{gap_1}} (you/ever/hear) about the podcast Audio World? CLARA: No, I 2 {{gap_2}}. What topic do they cover? SAM: Tech news. I 3 {{gap_3}} (see) a live recording last Friday. CLARA: 4 {{gap_4}} (be) it an exciting show? SAM: Yes, I really 5 {{gap_5}} (like) the hosts. Dialogue 2 LEO: 6 {{gap_6}} (you/ever/lose) your wallet outdoors? MIA: Yes, I 7 {{gap_7}}. LEO: Where 8 {{gap_8}} (it/happen)? MIA: In Spain. I 9 {{gap_9}} (be) at a beach resort. LEO: What 10 {{gap_10}} (you/do)?
```

**Adapted Answers**: `["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['i really 5', 'no i 2'] with elevated similarity (Jaccard=0.3784, Lev=0.5737).", "Plural/compound subject conflicts with singular verb form 'Was'.", "Plural/compound subject conflicts with singular verb form 'was'."]`

---

### QID 3579 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-416` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `0 src / 0 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.3846`, Levenshtein: `0.525`)
- **Matched Shingles**: `["must me your", "you must me"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['must me your', 'you must me'] with elevated similarity (Jaccard=0.3846, Lev=0.5250).`

**Source Text**:
```text
7 'You must show me your passport.' ⇒ She told me that {{gap_1}}.
```

**Source Answers**: `["I had to show her my passport"]`

**Adapted Text**:
```text
The customs officer said, 'You must show me your passport.' ⇒ The woman explained that {{gap_1}}.
```

**Adapted Answers**: `["I had to show her my passport"]`

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['must me your', 'you must me'] with elevated similarity (Jaccard=0.3846, Lev=0.5250)."]`

---

### QID 4852 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-568` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `20 src / 20 adp` | Options: `60 src / 60 adp` | Answers: `20 src / 20 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.2062`, Levenshtein: `0.3459`)
- **Matched Shingles**: `["in that case", "last time i", "the last time"]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `High-confidence shallow copy: verbatim shingle(s) ['in that case', 'last time i'] with elevated similarity (Jaccard=0.2062, Lev=0.3459).; gender: Gender of primary person shifted.`

**Source Text**:
```text
AUTUMN: Hello? SARAH: Hi, Autumn; it’s Sarah. AUTUMN: Hi, Sarah. Everything OK? SARAH: Yes, I 1 {{gap_1}} to tell you about Patrick. Do you know what 2 {{gap_2}} to him yesterday? AUTUMN: No, what? SARAH: Well, he 3 {{gap_3}} some money, so he 4 {{gap_4}} to a cash machine. And when he 5 {{gap_5}} the money out, he 6 {{gap_6}} that there was an envelope on the floor. He 7 {{gap_7}} it and there were 20,000 pounds! AUTUMN: Really? 8 {{gap_8}}? SARAH: No! It's true. AUTUMN: What 9 {{gap_9}} now with the envelope? SARAH: He 10 {{gap_10}}. But he thinks that the owner of the money 11 {{gap_11}} to the police soon. AUTUMN: And then? SARAH: He says then he 12 {{gap_12}} the money back. AUTUMN: Maybe it’s money from crime or drugs! SARAH: In that case I don't think anybody 13 {{gap_13}} it. AUTUMN: If nobody reclaims it, we 14 {{gap_14}} Patrick to pay for a nice and expensive dinner! SARAH: Yes, definitely! By the way, what 15 {{gap_15}} when I rang you. AUTUMN: I 16 {{gap_16}} the house. SARAH: 17 {{gap_17}} anything when you finish cleaning? AUTUMN: No. Why? Would you like to go for a beer? SARAH: Yes, please! I think the last time I 18 {{gap_18}} for a beer, I 19 {{gap_19}} with Jeremy. AUTUMN: OK then, I 20 {{gap_20}} you up in about twenty minutes then. SARAH: Excellent! See you later. AUTUMN: See you!
```

**Source Answers**: `["’m calling", "happened", "needed", "went", "was taking", "noticed", "opened", "Are you joking", "is he going to do", "doesn’t know", "will go", "is going to give", "will reclaim", "’ll tell", "were you doing", "was cleaning", "Are you doing", "went", "was still going out", "’ll pick"]`
**Source Options**: 1. call ; 1. was happening ; 1. needed [CORRECT]; 1. went [CORRECT]; 1. takes ; 1. noticed [CORRECT]; 1. has opened ; 1. Are you joking [CORRECT]; 1. is he going to do [CORRECT]; 1. isn't knowing ; 1. will go [CORRECT]; 1. is going to give [CORRECT]; 1. will reclaim [CORRECT]; 1. are telling ; 1. did you do ; 1. was cleaning [CORRECT]; 1. Are you doing [CORRECT]; 1. was going ; 1. did still go out ; 1. 'm going to pick ; 2. called ; 2. happened [CORRECT]; 2. was needing ; 2. has gone ; 2. was taking [CORRECT]; 2. was noticing ; 2. opens ; 2. Do you joke ; 2. will he do ; 2. doesn’t know [CORRECT]; 2. is going to go ; 2. is giving ; 2. reclaims ; 2. ’ll tell [CORRECT]; 2. have you done ; 2. cleaned ; 2. Do you do ; 2. have gone ; 2. have still gone out ; 2. 'm picking ; 3. ’m calling [CORRECT]; 3. has happened ; 3. has needed ; 3. was going ; 3. has taken ; 3. has noticed ; 3. opened [CORRECT]; 3. Did you joke ; 3. is he doing ; 3. not knows ; 3. is going ; 3. gives ; 3. is reclaiming ; 3. tell ; 3. were you doing [CORRECT]; 3. have cleaned ; 3. Will you do ; 3. went [CORRECT]; 3. was still going out [CORRECT]; 3. ’ll pick [CORRECT]

**Adapted Text**:
```text
LEO: Hey, Chloe! CHLOE: Hi Leo, I {{gap_1}} to discuss Lucas. Do you know what {{gap_2}} at the office on Friday? LEO: No, tell me! CHLOE: Well, he {{gap_3}} some advice, so he {{gap_4}} to the manager's desk. While he {{gap_5}} notes, he {{gap_6}} a document left on the table. He {{gap_7}} the folder and found confidential files! LEO: Wow, {{gap_8}}? CHLOE: Truly! LEO: What {{gap_9}} with the files? CHLOE: He {{gap_10}}. But he thinks the director {{gap_11}} to human resources soon. LEO: What happens after that? CHLOE: He mentioned he {{gap_12}} the document back immediately. LEO: Maybe it contains sensitive company secrets! CHLOE: In that case, nobody {{gap_13}} it publicly. LEO: If no one claims it, we {{gap_14}} Lucas to join us for dinner! CHLOE: Great idea! What {{gap_15}} earlier when I phoned? LEO: I {{gap_16}} my kitchen. CHLOE: {{gap_17}} anything later tonight? LEO: Not really. CHLOE: Awesome! The last time I {{gap_18}} out, I {{gap_19}} with David. LEO: Cool, I {{gap_20}} you up around seven!
```

**Adapted Answers**: `["’m calling", "happened", "needed", "went", "was taking", "noticed", "opened", "Are you joking", "is he going to do", "doesn’t know", "will go", "is going to give", "will reclaim", "’ll tell", "were you doing", "was cleaning", "Are you doing", "went", "was still going out", "’ll pick"]`
**Adapted Options**: 1. call ; 1. was happening ; 1. needed [CORRECT]; 1. went [CORRECT]; 1. takes ; 1. noticed [CORRECT]; 1. has opened ; 1. Are you joking [CORRECT]; 1. is he going to do [CORRECT]; 1. isn't knowing ; 1. will go [CORRECT]; 1. is going to give [CORRECT]; 1. will reclaim [CORRECT]; 1. are telling ; 1. did you do ; 1. was cleaning [CORRECT]; 1. Are you doing [CORRECT]; 1. was going ; 1. did still go out ; 1. 'm going to pick ; 2. called ; 2. happened [CORRECT]; 2. was needing ; 2. has gone ; 2. was taking [CORRECT]; 2. was noticing ; 2. opens ; 2. Do you joke ; 2. will he do ; 2. doesn’t know [CORRECT]; 2. is going to go ; 2. is giving ; 2. reclaims ; 2. ’ll tell [CORRECT]; 2. have you done ; 2. cleaned ; 2. Do you do ; 2. have gone ; 2. have still gone out ; 2. 'm picking ; 3. ’m calling [CORRECT]; 3. has happened ; 3. has needed ; 3. was going ; 3. has taken ; 3. has noticed ; 3. opened [CORRECT]; 3. Did you joke ; 3. is he doing ; 3. not knows ; 3. is going ; 3. gives ; 3. is reclaiming ; 3. tell ; 3. were you doing [CORRECT]; 3. have cleaned ; 3. Will you do ; 3. went [CORRECT]; 3. was still going out [CORRECT]; 3. ’ll pick [CORRECT]

**Validation Flags**: `["High-confidence shallow copy: verbatim shingle(s) ['in that case', 'last time i'] with elevated similarity (Jaccard=0.2062, Lev=0.3459).", "gender: Gender of primary person shifted."]`

---

### QID 3382 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-394` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `False`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.0526`, Levenshtein: `0.3188`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `REJECT` | **AI Reason**: `Answer divergence: target answer not preserved in adapted context.`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Correct answer diverged from source: source=["'d tell"], adapted=["'d drive"]. Flagged for review.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`

**Source Text**:
```text
7 I don't know the answer. If I knew the answer, I _____ you.
```

**Source Answers**: `["'d tell"]`
**Source Options**: 1. 'd tell [CORRECT]; 2. 'll tell ; 3. told 

**Adapted Text**:
```text
7 She doesn't own a car. If she owned a vehicle, she _____ to work every morning.
```

**Adapted Answers**: `["'d drive"]`
**Adapted Options**: 1. 'd drive [CORRECT]; 2. 'll drive ; 3. drove 

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "Correct answer diverged from source: source=[\"'d tell\"], adapted=[\"'d drive\"]. Flagged for review.", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person)."]`

---

### QID 7139 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-833` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `1 src / 1 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.0769`, Levenshtein: `0.2973`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Plural/compound subject conflicts with singular verb form 'has'.`

**Source Text**:
```text
10 Daniel {{gap_1}} brown hair and blue eyes.
```

**Source Answers**: `["has"]`
**Source Options**: 1. are having ; 2. is having ; 3. has [CORRECT]

**Adapted Text**:
```text
My sister {{gap_1}} a friendly dog and two cats.
```

**Adapted Answers**: `["has"]`
**Adapted Options**: 1. are having ; 2. is having ; 3. has [CORRECT]

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).", "Plural/compound subject conflicts with singular verb form 'has'."]`

---

### QID 3361 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-391` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.1579`, Levenshtein: `0.4937`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Normalized Levenshtein similarity (0.4937) exceeds threshold (< 0.45) on standard text (len=79).; Plural/compound subject conflicts with singular verb form 'mine/hers'.`

**Source Text**:
```text
7 "Whose medicines are these?" "They are not _____. Ask Sally, maybe they are _____"
```

**Source Answers**: `["mine/hers"]`
**Source Options**: 1. me/hers ; 2. mine/hers [CORRECT]; 3. my/hers 

**Adapted Text**:
```text
"Whose keys are on the kitchen table?" "They aren't _____. Check with Emma, perhaps they are _____."
```

**Adapted Answers**: `["mine/hers"]`
**Adapted Options**: 1. me/hers ; 2. mine/hers [CORRECT]; 3. my/hers 

**Validation Flags**: `["Normalized Levenshtein similarity (0.4937) exceeds threshold (< 0.45) on standard text (len=79).", "Plural/compound subject conflicts with singular verb form 'mine/hers'."]`

---

### QID 3365 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-392` | **Response Model**: `gap`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `10 src / 10 adp` | Options: `0 src / 0 adp` | Answers: `10 src / 10 adp`
- **Answer Preservation Passed**: `True`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.1241`, Levenshtein: `0.3014`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `NULL` | **AI Reason**: `NULL`
- **Stored Database Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; countability: Countable vs uncountable noun environment shifted.; Masculine subject antecedent conflicts with feminine pronoun answer 'her'.; Plural/compound subject conflicts with singular verb form 'Its'.`

**Source Text**:
```text
Dear James, Thanks for 1 {{gap_1}} email. It was very nice to have news from 2 {{gap_2}}. I was very happy to hear that you are finally getting married to Maria. It's perfect! I think you will make 3 {{gap_3}} very happy and 4 {{gap_4}} will make you very happy, too. How did your parents react when you gave 5 {{gap_5}} the news? Aren't 6 {{gap_6}} excited? I'm sure they are really happy. I'm really looking forward to seeing you all at the wedding. By the way, do you remember that I wanted a tortoise? I already have one. 7 {{gap_7}} name is Green. Sara and I saw 8 {{gap_8}} in a pet shop and 9 {{gap_9}} decided to buy the little thing right away. We are so happy with 10 {{gap_10}} new pet! Well, I hope to see you soon, James. Please call me if you need any help. Love, Samuel.
```

**Source Answers**: `["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"]`

**Adapted Text**:
```text
Hi David, Thank you for {{gap_1}} message. I was glad to hear from {{gap_2}}. I heard that you hired Clara for the project. I hope you support {{gap_3}} during training, as {{gap_4}} can assist you a lot. What did the directors say when you offered {{gap_5}} the proposal? Were {{gap_6}} satisfied with it? Also, we adopted a parrot recently. {{gap_7}} feathers are bright blue. My roommate and I found {{gap_8}} last month, so {{gap_9}} took it home. We adore {{gap_10}} new bird! Best regards, Alex.
```

**Adapted Answers**: `["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"]`

**Validation Flags**: `["Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).", "countability: Countable vs uncountable noun environment shifted.", "Masculine subject antecedent conflicts with feminine pronoun answer 'her'.", "Plural/compound subject conflicts with singular verb form 'Its'."]`

---

### QID 2952 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-343` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `False`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `True` (Jaccard: `0.125`, Levenshtein: `0.4906`)
- **Matched Shingles**: `[]`
- **AI Review Status**: `REJECT` | **AI Reason**: `Answer divergence: target answer not preserved in adapted context.`
- **Stored Database Reason**: `Normalized Levenshtein similarity (0.4906) exceeds threshold (< 0.45) on standard text (len=53).; Correct answer diverged from source: source=['Who asked his boss'], adapted=['Who asked his teacher']. Flagged for review.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`

**Source Text**:
```text
6 Lewis asked his boss for a promotion. ⇒ _____ for a promotion?
```

**Source Answers**: `["Who asked his boss"]`
**Source Options**: 1. Who asked his boss [CORRECT]; 2. Who did he ask his boss ; 3. Who did ask his boss 

**Adapted Text**:
```text
David asked his teacher for extra time. ⇒ _____ for extra time?
```

**Adapted Answers**: `["Who asked his teacher"]`
**Adapted Options**: 1. Who asked his teacher [CORRECT]; 2. Who did he ask his teacher ; 3. Who did ask his teacher 

**Validation Flags**: `["Normalized Levenshtein similarity (0.4906) exceeds threshold (< 0.45) on standard text (len=53).", "Correct answer diverged from source: source=['Who asked his boss'], adapted=['Who asked his teacher']. Flagged for review."]`

---

### QID 2894 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-336` | **Response Model**: `single_choice`
- **Status**: `REJECTED` | **Stage**: `original_batch_execution`
- **Generation Timestamp**: `2026-10-01T07:03:32.750815+00:00` | **Last Updated**: `2026-10-01T07:03:32.750815+00:00`
- **Cardinality**: Gaps: `0 src / 0 adp` | Options: `3 src / 3 adp` | Answers: `1 src / 1 adp`
- **Answer Preservation Passed**: `False`
- **Structural Validation Passed**: `True`
- **Rejected by Similarity**: `False` (Jaccard: `0.375`, Levenshtein: `0.5079`)
- **Matched Shingles**: `["yes but the"]`
- **AI Review Status**: `REJECT` | **AI Reason**: `Answer divergence: target answer not preserved in adapted context.`
- **Stored Database Reason**: `Verbatim shingle detected 'yes but the' with moderate/low similarity (Jaccard=0.3750 <= 0.40, Lev=0.5079 < 0.55). Routed to AI review.; Correct answer diverged from source: source=["Are you going to drive / 'm going to be"], adapted=["Are you going to fly / 'm going to be"]. Flagged for review.; countability: Countable vs uncountable noun environment shifted.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`

**Source Text**:
```text
6 A: ______ to work today? B: Yes, but the traffic is awful, so I _____ late.
```

**Source Answers**: `["Are you going to drive / 'm going to be"]`
**Source Options**: 1. Will you drive / will be ; 2. Will you drive / 'm going to be ; 3. Are you going to drive / 'm going to be [CORRECT]

**Adapted Text**:
```text
A: _____ to the airport tonight? B: Yes, but the storm is severe, so I _____ delayed.
```

**Adapted Answers**: `["Are you going to fly / 'm going to be"]`
**Adapted Options**: 1. Will you fly / will be ; 2. Will you fly / 'm going to be ; 3. Are you going to fly / 'm going to be [CORRECT]

**Validation Flags**: `["Verbatim shingle detected 'yes but the' with moderate/low similarity (Jaccard=0.3750 <= 0.40, Lev=0.5079 < 0.55). Routed to AI review.", "Correct answer diverged from source: source=[\"Are you going to drive / 'm going to be\"], adapted=[\"Are you going to fly / 'm going to be\"]. Flagged for review.", "countability: Countable vs uncountable noun environment shifted."]`

---
