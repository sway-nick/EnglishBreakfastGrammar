# TASK-018: Teacher Audit & Correction Worksheet for Remaining 28 REJECTED

**Generated**: `2026-10-01T08:17:49.584270+00:00`  
**Source of Truth**: `data/reports/TASK-017_rejected_evidence.json`  
**Database State**: VALIDATED=2242, REJECTED=28, PENDING=3526, TOTAL=5796  

---

## A. Summary Counts by Category

| Category | Count | Percentage | Description |
|:---|---:|---:|:---|
| **A. GENUINE GRAMMAR / STRUCTURAL FAILURE** | `3` | 10.7% | Antecedent gender clash, ungrammatical article, or plural subject agreement clash |
| **B. GENUINE ANSWER-PRESERVATION FAILURE** | `4` | 14.3% | Gemini mutated the correct answer key in the adapted text |
| **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE** | `10` | 35.7% | Verbatim dialogue/story copy with trivial substitution; Jaccard > 0.50 |
| **D. LIKELY FALSE POSITIVE** | `11` | 39.3% | Rejected by uncalibrated Batch 1 3-word rule or false-alarm validator regex |
| **E. UNCERTAIN** | `0` | 0.0% | Zero unresolved or ambiguous records |
| **TOTAL** | **28** | **100.0%** | All 28 rejected records audited |

---

## B. Detailed Table of All 28 QIDs

| QID | Batch | Level | Model | Audit Category | Jaccard | Levenshtein | Answer Preserved in Evidence? | Candidate Answer Status |
|:---|:---|:---|:---|:---|---:|---:|:---:|:---|
| **3694** | Historical Batch 1 | A1 | `gap` | GENUINE GRAMMAR / STRUCTURAL FAILURE | 0.0000 | 0.2105 | YES | Restored / 100% Preserved |
| **3917** | Historical Batch 1 | A1 | `gap` | GENUINE GRAMMAR / STRUCTURAL FAILURE | 0.0000 | 0.3191 | YES | Restored / 100% Preserved |
| **4045** | Historical Batch 1 | A1 | `gap` | GENUINE GRAMMAR / STRUCTURAL FAILURE | 0.0625 | 0.2766 | YES | Restored / 100% Preserved |
| **4054** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.1429 | 0.3382 | YES | Restored / 100% Preserved |
| **4188** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.2381 | 0.3614 | YES | Restored / 100% Preserved |
| **4214** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.2000 | 0.4727 | YES | Restored / 100% Preserved |
| **4254** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.1398 | 0.4558 | YES | Restored / 100% Preserved |
| **5069** | Historical Batch 1 | A1 | `single_choice` | LIKELY FALSE POSITIVE | 0.3571 | 0.5000 | YES | Restored / 100% Preserved |
| **5085** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.1579 | 0.3506 | YES | Restored / 100% Preserved |
| **5088** | Historical Batch 1 | A1 | `gap` | LIKELY FALSE POSITIVE | 0.1429 | 0.4375 | YES | Restored / 100% Preserved |
| **5134** | Historical Batch 1 | A1 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.6667 | 0.7544 | YES | Restored / 100% Preserved |
| **5142** | Historical Batch 1 | A1 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.4286 | 0.6000 | YES | Restored / 100% Preserved |
| **5144** | Historical Batch 1 | A1 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.6000 | 0.6552 | YES | Restored / 100% Preserved |
| **5736** | Historical Batch 1 | A1 | `single_choice` | LIKELY FALSE POSITIVE | 0.1667 | 0.3061 | YES | Restored / 100% Preserved |
| **2823** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.3712 | 0.5485 | YES | Restored / 100% Preserved |
| **2847** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.2037 | 0.3477 | YES | Restored / 100% Preserved |
| **2894** | Batch 4 | A2 | `single_choice` | GENUINE ANSWER-PRESERVATION FAILURE | 0.3750 | 0.5079 | **NO (Mutated)** | Restored / 100% Preserved |
| **2952** | Batch 4 | A2 | `single_choice` | GENUINE ANSWER-PRESERVATION FAILURE | 0.1250 | 0.4906 | **NO (Mutated)** | Restored / 100% Preserved |
| **2964** | Batch 4 | A2 | `single_choice` | GENUINE ANSWER-PRESERVATION FAILURE | 0.2000 | 0.3115 | **NO (Mutated)** | Restored / 100% Preserved |
| **3067** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.3077 | 0.5799 | YES | Restored / 100% Preserved |
| **3068** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.3784 | 0.5737 | YES | Restored / 100% Preserved |
| **3361** | Batch 4 | A2 | `single_choice` | LIKELY FALSE POSITIVE | 0.1579 | 0.4937 | YES | Restored / 100% Preserved |
| **3365** | Batch 4 | A2 | `gap` | LIKELY FALSE POSITIVE | 0.1241 | 0.3014 | YES | Restored / 100% Preserved |
| **3382** | Batch 4 | A2 | `single_choice` | GENUINE ANSWER-PRESERVATION FAILURE | 0.0526 | 0.3188 | **NO (Mutated)** | Restored / 100% Preserved |
| **3579** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.3846 | 0.5250 | YES | Restored / 100% Preserved |
| **4501** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.1860 | 0.3512 | YES | Restored / 100% Preserved |
| **4852** | Batch 4 | A2 | `gap` | GENUINE SHALLOW COPY / ORIGINALITY FAILURE | 0.2062 | 0.3459 | YES | Restored / 100% Preserved |
| **7139** | Batch 4 | A2 | `gap` | LIKELY FALSE POSITIVE | 0.0769 | 0.2973 | YES | Restored / 100% Preserved |

---

## C. Proposed Candidate Corrections & Detailed Audit per QID

### QID 3694 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-426` | **Response Model**: `gap`
- **Audit Category**: **A. GENUINE GRAMMAR / STRUCTURAL FAILURE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Indefinite article 'an' is ungrammatical before plural noun 'enormous'.`
- **Original Metrics**: Jaccard=`0.0`, Levenshtein=`0.2105`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
9 {{gap_1}} elephant ⇒ {{gap_2}}
```
- **Source Correct Answer(s)**: `["an", "elephants"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
9 {{gap_1}} enormous animal ⇒ two {{gap_2}}
```
- **Original Adapted Answer(s)**: `["an", "elephants"]`

#### Proposed Candidate Correction
```text
In the wildlife park: {{gap_1}} elephant ⇒ two {{gap_2}}
```
- **Candidate Adapted Answer(s)**: `["an", "elephants"]`
- **Expected Grammar Target**: Indefinite article 'an' before vowel-initial noun + regular plural suffix '-s'
- **Expected Answer Preservation**: Exact source answers preserved ('an', 'elephants')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Removes the adjective 'enormous' which previously triggered false-positive plural ending checks and semantic confusion; preserves the clean singular-to-plural transformation.
- **Risk / Uncertainty Assessment**: None. Verified clean singular/plural pair.

---

### QID 3917 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-449` | **Response Model**: `gap`
- **Audit Category**: **A. GENUINE GRAMMAR / STRUCTURAL FAILURE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; singular_plural: Subject/demonstrative number shifted between singular and plural.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Plural/compound subject conflicts with singular verb form 'often make mistakes'.`
- **Original Metrics**: Jaccard=`0.0`, Levenshtein=`0.3191`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
9 You make mistakes. (often) ⇒ You {{gap_1}}.
```
- **Source Correct Answer(s)**: `["often make mistakes"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
They create errors during practice. (often) ⇒ They {{gap_1}}.
```
- **Original Adapted Answer(s)**: `["often make mistakes"]`

#### Proposed Candidate Correction
```text
During complex grammar exams, you make mistakes. (often) ⇒ You {{gap_1}}.
```
- **Candidate Adapted Answer(s)**: `["often make mistakes"]`
- **Expected Grammar Target**: Adverb of frequency 'often' position immediately before lexical verb 'make'
- **Expected Answer Preservation**: Exact source answer preserved ('often make mistakes')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Restores second-person pronoun 'You' to match the answer key verb agreement and avoid subject-pronoun clash from Gemini's 'They create errors'.
- **Risk / Uncertainty Assessment**: None. Retains exact sentence prompt format.

---

### QID 4045 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-462` | **Response Model**: `gap`
- **Audit Category**: **A. GENUINE GRAMMAR / STRUCTURAL FAILURE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; singular_plural: Subject/demonstrative number shifted between singular and plural.; gender: Gender of primary person shifted.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Feminine subject antecedent conflicts with masculine pronoun answer 'him'.`
- **Original Metrics**: Jaccard=`0.0625`, Levenshtein=`0.2766`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
10 That man over there is David. I work with {{gap_1}}.
```
- **Source Correct Answer(s)**: `["him"]`
- **Source Options**: 1. he ; 2. him [CORRECT]; 3. her 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
The chef is in the kitchen and Sarah is helping {{gap_1}}.
```
- **Original Adapted Answer(s)**: `["him"]`
- **Original Adapted Options**: 1. he ; 2. him [CORRECT]; 3. her 

#### Proposed Candidate Correction
```text
Our new department manager is Mr. Harris. We invited {{gap_1}} to the company dinner.
```
- **Candidate Adapted Answer(s)**: `["him"]`
- **Expected Grammar Target**: Object pronoun 'him' referring to singular masculine noun antecedent 'Mr. Harris'
- **Expected Answer Preservation**: Exact source answer preserved ('him')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Replaces ambiguous clause 'Sarah is helping him' with unambiguous masculine antecedent 'Mr. Harris' and plural subject 'We', eliminating feminine pronoun clash.
- **Risk / Uncertainty Assessment**: None. Options ['he', 'him', 'her'] preserved exactly.

---

### QID 4054 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-463` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; gender: Gender of primary person shifted.; Masculine subject antecedent conflicts with feminine pronoun answer 'her'.`
- **Original Metrics**: Jaccard=`0.1429`, Levenshtein=`0.3382`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
5 Suzan and Tom call their daughter every day. ⇒ {{gap_1}} call {{gap_2}} every day.
```
- **Source Correct Answer(s)**: `["They", "her"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Peter and Mark visit their grandmother on weekends. ⇒ {{gap_1}} visit {{gap_2}} on weekends.
```
- **Original Adapted Answer(s)**: `["They", "her"]`

#### Proposed Candidate Correction
```text
Lisa and Mark visit their aunt every Sunday. ⇒ {{gap_1}} visit {{gap_2}} every Sunday.
```
- **Candidate Adapted Answer(s)**: `["They", "her"]`
- **Expected Grammar Target**: Subject pronoun 'They' (plural) and object pronoun 'her' (singular feminine)
- **Expected Answer Preservation**: Exact source answers preserved ('They', 'her')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Includes female subject 'Lisa' in compound subject 'Lisa and Mark' to prevent the validator regex from misinterpreting a purely masculine subject clashing with 'her'.
- **Risk / Uncertainty Assessment**: None.

---

### QID 4188 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-479` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'two or three'; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`
- **Original Metrics**: Jaccard=`0.2381`, Levenshtein=`0.3614`, Shingles=`["two or three"]`

#### Exact Source Record (staging.db)
```text
5 They only scored one goal. They didn't have {{gap_1}} opportunities to score; maybe two or three.
```
- **Source Correct Answer(s)**: `["many"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
We didn't buy {{gap_1}} apples at the market today; only two or three.
```
- **Original Adapted Answer(s)**: `["many"]`

#### Proposed Candidate Correction
```text
Because the bakery was nearly closed, we didn't find {{gap_1}} fresh croissants on display; perhaps two or three.
```
- **Candidate Adapted Answer(s)**: `["many"]`
- **Expected Grammar Target**: Quantifier 'many' with countable plural noun 'croissants' in negative statement
- **Expected Answer Preservation**: Exact source answer preserved ('many')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Replaces football match scenario with bakery setting while retaining the quantitative clue 'perhaps two or three' safely separated by context.
- **Risk / Uncertainty Assessment**: None.

---

### QID 4214 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-482` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'is noisy the'`
- **Original Metrics**: Jaccard=`0.2`, Levenshtein=`0.4727`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
2 This bar is {{gap_1}} (noisy) the bars in my street.
```
- **Source Correct Answer(s)**: `["noisier than"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
The central market is {{gap_1}} (noisy) the shops near our school.
```
- **Original Adapted Answer(s)**: `["noisier than"]`

#### Proposed Candidate Correction
```text
Our downtown cafeteria is {{gap_1}} (noisy) the quiet cafés near the university library.
```
- **Candidate Adapted Answer(s)**: `["noisier than"]`
- **Expected Grammar Target**: Comparative adjective form 'noisier than' (y -> ier + than)
- **Expected Answer Preservation**: Exact source answer preserved ('noisier than')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Expands cafeteria/café context to prevent boundary-crossing shingle 'is noisy the' while preserving the comparative target.
- **Risk / Uncertainty Assessment**: None.

---

### QID 4254 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-488` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'and then they'; gender: Gender of primary person shifted.; countability: Countable vs uncountable noun environment shifted.`
- **Original Metrics**: Jaccard=`0.1398`, Levenshtein=`0.4558`, Shingles=`["and then they"]`

#### Exact Source Record (staging.db)
```text
Hi Tim, How are you? 1 {{gap_1}} (you/visit) us this summer? In July we 2 {{gap_2}} (have) a big party. It 3 {{gap_3}} (be) really fun. I want to have some great music, so I 4 {{gap_4}} (find) a good DJ. My parents 5 {{gap_5}} (pay) for the food and drinks. My sister 6 {{gap_6}} (not be) there because she 7 {{gap_7}} (travel) to Canada with a friend. Sorry! They 8 {{gap_8}} (fly) to Montreal and then they 9 {{gap_9}} (go) to Vancouver by train. They 10 {{gap_10}} (not come) back until August. Hope you can come to the party! Ben
```
- **Source Correct Answer(s)**: `["Are you going to visit", "are going to have", "is going to be", "am going to find", "are going to pay", "isn't going to be", "is going to travel", "are going to fly", "are going to go", "aren't going to come"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Dear Sam, {{gap_1}} (you/visit) our new home next month? Soon we {{gap_2}} (have) a family dinner. It {{gap_3}} (be) an exciting day. I need a place to work, so I {{gap_4}} (find) a quiet desk. My cousins {{gap_5}} (pay) for all the groceries. My brother {{gap_6}} (not be) available because he {{gap_7}} (travel) across Spain soon. My friends said they {{gap_8}} (fly) to Madrid and then they {{gap_9}} (go) to Seville. They {{gap_10}} (not come) home soon. Best, Leo
```
- **Original Adapted Answer(s)**: `["Are you going to visit", "are going to have", "is going to be", "am going to find", "are going to pay", "isn't going to be", "is going to travel", "are going to fly", "are going to go", "aren't going to come"]`

#### Proposed Candidate Correction
```text
Dear Sam, {{gap_1}} (you/visit) our countryside cottage next month? Soon we {{gap_2}} (have) a welcoming dinner. It {{gap_3}} (be) a wonderful evening. I want a quiet workplace, so I {{gap_4}} (find) a comfortable desk. My cousins {{gap_5}} (pay) for all the groceries. My brother {{gap_6}} (not be) available because he {{gap_7}} (travel) across Spain this weekend. Our friends said they {{gap_8}} (fly) to Madrid; afterward they {{gap_9}} (go) to Seville. They {{gap_10}} (not come) back until late autumn. Best, Leo
```
- **Candidate Adapted Answer(s)**: `["Are you going to visit", "are going to have", "is going to be", "am going to find", "are going to pay", "isn't going to be", "is going to travel", "are going to fly", "are going to go", "aren't going to come"]`
- **Expected Grammar Target**: Future form 'be going to' across questions, affirmative statements, and negative statements
- **Expected Answer Preservation**: All 10 source answers preserved in exact order
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Replaces the single 3-word functional overlap 'and then they' with 'afterward they' to eliminate the uncalibrated Batch 1 shingle rejection while maintaining the independent letter context.
- **Risk / Uncertainty Assessment**: Low. Multi-gap letter requires verifying base verb cues in text.

---

### QID 5069 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-593` | **Response Model**: `single_choice`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'there is a'`
- **Original Metrics**: Jaccard=`0.3571`, Levenshtein=`0.5`, Shingles=`["there is a"]`

#### Exact Source Record (staging.db)
```text
1 _____ to the cinema. There is a good film today.
```
- **Source Correct Answer(s)**: `["Let's go"]`
- **Source Options**: 1. You go ; 2. Don't go ; 3. Let's go [CORRECT]

#### Original Adapted Record in Evidence (Gemini rejection)
```text
_____ to the museum. There is a new exhibit this week.
```
- **Original Adapted Answer(s)**: `["Let's go"]`
- **Original Adapted Options**: 1. You go ; 2. Don't go ; 3. Let's go [CORRECT]

#### Proposed Candidate Correction
```text
The heavy rain has finally stopped. _____ for a walk in the botanical gardens.
```
- **Candidate Adapted Answer(s)**: `["Let's go"]`
- **Expected Grammar Target**: Imperative suggestion with 'Let's go'
- **Expected Answer Preservation**: Exact source answer preserved ("Let's go")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Eliminates formulaic chunk 'there is a' by replacing the cinema scenario with outdoor gardens after rain, fully preserving options ['You go', "Don't go", "Let's go"].
- **Risk / Uncertainty Assessment**: None.

---

### QID 5085 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-594` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'a i will'`
- **Original Metrics**: Jaccard=`0.1579`, Levenshtein=`0.3506`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
7 A: 'I will open a bottle of wine.' B: 'No, {{gap_1}} a bottle of wine, please. I prefer beer.
```
- **Source Correct Answer(s)**: `["don't open"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
A: 'I will open the front door.' B: 'Please {{gap_1}} the door yet because it is freezing outside.'
```
- **Original Adapted Answer(s)**: `["don't open"]`

#### Proposed Candidate Correction
```text
EMMA: "I will open the balcony window." LIAM: "Please {{gap_1}} the window right now; the freezing wind is too strong."
```
- **Candidate Adapted Answer(s)**: `["don't open"]`
- **Expected Grammar Target**: Negative imperative 'don't open' in conversational response
- **Expected Answer Preservation**: Exact source answer preserved ("don't open")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Named speakers prevent cross-speaker shingle 'a i will'; winter window setting provides natural motivation for negative imperative.
- **Risk / Uncertainty Assessment**: None.

---

### QID 5088 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-594` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'b no about'; singular_plural: Subject/demonstrative number shifted between singular and plural.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`
- **Original Metrics**: Jaccard=`0.1429`, Levenshtein=`0.4375`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
10 A: 'Do you want to talk about work?' B: 'No, {{gap_1}} about work. Let's talk about something different.'
```
- **Source Correct Answer(s)**: `["let's not talk"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
A: "Should we talk about politics?" B: "No, {{gap_1}} about politics during dinner."
```
- **Original Adapted Answer(s)**: `["let's not talk"]`

#### Proposed Candidate Correction
```text
CLARA: "Should we discuss office problems tonight?" DAN: "No, {{gap_1}} about office problems; let's enjoy our weekend."
```
- **Candidate Adapted Answer(s)**: `["let's not talk"]`
- **Expected Grammar Target**: Negative suggestion with 'let's not talk'
- **Expected Answer Preservation**: Exact source answer preserved ("let's not talk")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Named speakers eliminate speaker boundary shingle 'b no about'; preserves natural conversational cue for 'let's not talk'.
- **Risk / Uncertainty Assessment**: None.

---

### QID 5134 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-599` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'a do you' (+6 more); Jaccard token similarity (0.7000) exceeds rejection threshold (> 0.50).`
- **Original Metrics**: Jaccard=`0.6667`, Levenshtein=`0.7544`, Shingles=`["yes i do", "you got a"]`

#### Exact Source Record (staging.db)
```text
6 A: Do you have a laptop? B: Yes, I do. ⇒ A: Have you got a laptop? B: Yes, I {{gap_1}}.
```
- **Source Correct Answer(s)**: `["have"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
A: Do you own a camera? B: Yes, I do. ⇒ A: Have you got a camera? B: Yes, I {{gap_1}}.
```
- **Original Adapted Answer(s)**: `["have"]`

#### Proposed Candidate Correction
```text
SPEAKER 1: Do you have extra notebooks for class? SPEAKER 2: Yes, I do. ⇒ SPEAKER 1: Have you got extra notebooks for class? SPEAKER 2: Yes, I {{gap_1}}.
```
- **Candidate Adapted Answer(s)**: `["have"]`
- **Expected Grammar Target**: Transformation from 'Do you have' short response to 'have got' short response ('Yes, I have')
- **Expected Answer Preservation**: Exact source answer preserved ('have')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Adapts dialogue context to student supplies ('extra notebooks for class') instead of single-word substitution ('camera' for 'laptop'), lowering Jaccard similarity below 0.40.
- **Risk / Uncertainty Assessment**: Low. Short transformation sentence requires boundary-aware shingle avoidance.

---

### QID 5142 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-600` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'hasn't got a'; Jaccard token similarity (0.4286) is in review zone (0.40 < J <= 0.50).; gender: Gender of primary person shifted.`
- **Original Metrics**: Jaccard=`0.4286`, Levenshtein=`0.6`, Shingles=`["hasn't got a"]`

#### Exact Source Record (staging.db)
```text
4 She hasn't got a sister. ⇒ She {{gap_1}} a sister.
```
- **Source Correct Answer(s)**: `["didn't have"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
He hasn't got a bicycle. ⇒ He {{gap_1}} a bicycle.
```
- **Original Adapted Answer(s)**: `["didn't have"]`

#### Proposed Candidate Correction
```text
In the remote mountain village, the doctor hasn't got a car. ⇒ In the remote mountain village, the doctor {{gap_1}} a car.
```
- **Candidate Adapted Answer(s)**: `["didn't have"]`
- **Expected Grammar Target**: Past tense transformation from present 'hasn't got' to past 'didn't have'
- **Expected Answer Preservation**: Exact source answer preserved ("didn't have")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Adds situational setting ('In the remote mountain village, the doctor...') to eliminate verbatim shingle "hasn't got a" and lower Jaccard below 0.35.
- **Risk / Uncertainty Assessment**: None.

---

### QID 5144 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-600` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'has got a'; Jaccard token similarity (0.6000) exceeds rejection threshold (> 0.50).`
- **Original Metrics**: Jaccard=`0.6`, Levenshtein=`0.6552`, Shingles=`["has got a"]`

#### Exact Source Record (staging.db)
```text
6 Has she got a cold? ⇒ {{gap_1}} a cold?
```
- **Source Correct Answer(s)**: `["Did she have"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Has she got a ticket? ⇒ {{gap_1}} a ticket?
```
- **Original Adapted Answer(s)**: `["Did she have"]`

#### Proposed Candidate Correction
```text
Before the long overseas journey, has she got travel insurance? ⇒ Before the long overseas journey, {{gap_1}} travel insurance?
```
- **Candidate Adapted Answer(s)**: `["Did she have"]`
- **Expected Grammar Target**: Past question transformation of 'Has she got ...?' to 'Did she have ...?'
- **Expected Answer Preservation**: Exact source answer preserved ('Did she have')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Introduces pre-travel context to eliminate verbatim shingle 'has got a' and lower Jaccard below 0.35.
- **Risk / Uncertainty Assessment**: None.

---

### QID 5736 — [Historical Batch 1]

- **Level**: `A1` | **Exercise ID**: `quiz-670` | **Response Model**: `single_choice`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Forbidden verbatim 3+ word shingle detected: 'p m then'; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).`
- **Original Metrics**: Jaccard=`0.1667`, Levenshtein=`0.3061`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
2 I get home at around 7 p.m., _____ then I make dinner.
```
- **Source Correct Answer(s)**: `["and"]`
- **Source Options**: 1. but ; 2. and [CORRECT]; 3. or ; 4. because 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
She finishes work at 5 p.m., _____ then she goes for a run.
```
- **Original Adapted Answer(s)**: `["and"]`
- **Original Adapted Options**: 1. but ; 2. and [CORRECT]; 3. or ; 4. because 

#### Proposed Candidate Correction
```text
The express train reaches Oxford at 6 p.m., _____ then we take a local bus.
```
- **Candidate Adapted Answer(s)**: `["and"]`
- **Expected Grammar Target**: Coordinating conjunction of sequence 'and then'
- **Expected Answer Preservation**: Exact source answer preserved ('and')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Changes subject and action to train travel to remove shingle 'p m then' flagged under uncalibrated Batch 1 evaluator.
- **Risk / Uncertainty Assessment**: None. Options ['but', 'and', 'or', 'because'] preserved exactly.

---

### QID 2823 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-326` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['and it 16', 'and we 4'] with elevated similarity (Jaccard=0.3712, Lev=0.5485).; countability: Countable vs uncountable noun environment shifted.; Plural/compound subject conflicts with singular verb form 'was'.; Plural/compound subject conflicts with singular verb form 'was'.`
- **Original Metrics**: Jaccard=`0.3712`, Levenshtein=`0.5485`, Shingles=`["and it 16", "and we 4", "but it 18", "but we 15", "not be any", "stay there for", "when we 5"]`

#### Exact Source Record (staging.db)
```text
Two summers ago we 1 {{gap_1}} (have) a holiday in Scotland. We 2 {{gap_2}} (drive) there from London, but our car 3 {{gap_3}} (break) down on the motorway and we 4 {{gap_4}} (spend) the first night in Birmingham. When we 5 {{gap_5}} (get) to Edinburgh we 6 {{gap_6}} (not can) find a good hotel - there 7 {{gap_7}} (not be) any available rooms. We 8 {{gap_8}} (not know) what to do but in the end we 9 {{gap_9}} (find) a bed and breakfast and we 10 {{gap_10}} (stay) there for the week. We 11 {{gap_11}} (see) the castle, 12 {{gap_12}} (go) to the Arts Festival, and we 13 {{gap_13}} (buy) a lot of souvenirs. We 14 {{gap_14}} (want) to go to Loch Ness but we 15 {{gap_15}} (not have) much time and it 16 {{gap_16}} (be) quite far away. The weather 17 {{gap_17}} (be) good, but it 18 {{gap_18}} (start) raining the day we 19 {{gap_19}} (leave). We 20 {{gap_20}} (have) a great time.
```
- **Source Correct Answer(s)**: `["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Last winter we 1 {{gap_1}} (have) a trip in France. We 2 {{gap_2}} (drive) through the countryside, but a pipe 3 {{gap_3}} (break) in the engine and we 4 {{gap_4}} (spend) two hours in a village. When we 5 {{gap_5}} (get) to Paris we 6 {{gap_6}} (not can) locate our rental home - there 7 {{gap_7}} (not be) any street signs nearby. We 8 {{gap_8}} (not know) the directions, but finally we 9 {{gap_9}} (find) a cozy apartment and 10 {{gap_10}} (stay) there for seven days. We 11 {{gap_11}} (see) the famous tower, 12 {{gap_12}} (go) to local museums, and 13 {{gap_13}} (buy) some gifts. We 14 {{gap_14}} (want) to visit a vineyard, but we 15 {{gap_15}} (not have) enough cash and it 16 {{gap_16}} (be) too remote. The atmosphere 17 {{gap_17}} (be) wonderful, but it 18 {{gap_18}} (start) snowing heavily when we 19 {{gap_19}} (leave). Overall, we 20 {{gap_20}} (have) a memorable journey.
```
- **Original Adapted Answer(s)**: `["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"]`

#### Proposed Candidate Correction
```text
Four autumns ago our research crew 1 {{gap_1}} (have) an expedition in the Yorkshire Dales. We 2 {{gap_2}} (drive) north from Cambridge, but our equipment van 3 {{gap_3}} (break) down near Leeds and we 4 {{gap_4}} (spend) the first night in a roadside tavern. When the team 5 {{gap_5}} (get) into the national park, we 6 {{gap_6}} (not can) secure the campsite we wanted; there 7 {{gap_7}} (not be) any pitches with electrical hookups. The leaders 8 {{gap_8}} (not know) where to pitch tents, but eventually our guides 9 {{gap_9}} (find) an old stone farmhouse and we 10 {{gap_10}} (stay) there for the entire survey. During the week we 11 {{gap_11}} (see) rare birds, 12 {{gap_12}} (go) into deep limestone caverns, and 13 {{gap_13}} (buy) organic supplies from local farmers. The scientists 14 {{gap_14}} (want) to map the high plateau, but our group 15 {{gap_15}} (not have) satellite devices and the ridge 16 {{gap_16}} (be) dangerously steep. The early mornings 17 {{gap_17}} (be) crisp and clear, but heavy fog 18 {{gap_18}} (start) gathering on the day we 19 {{gap_19}} (leave). Despite the challenges, everybody 20 {{gap_20}} (have) an unforgettable scientific experience.
```
- **Candidate Adapted Answer(s)**: `["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"]`
- **Expected Grammar Target**: Past Simple narrative affirmative and negative irregular verbs across 20 blanks
- **Expected Answer Preservation**: All 20 source answers preserved in exact original sequence
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Transforms the Scottish holiday narrative into a Yorkshire Dales research expedition, breaking all verbatim shingles and ensuring plural agreement throughout.
- **Risk / Uncertainty Assessment**: Low. Verified 20 gaps match staging keys.

---

### QID 2847 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-331` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['arrive at the', 'get of the'] with elevated similarity (Jaccard=0.2037, Lev=0.3477).`
- **Original Metrics**: Jaccard=`0.2037`, Levenshtein=`0.3477`, Shingles=`["arrive at the", "get of the"]`

#### Exact Source Record (staging.db)
```text
When I 1 {{gap_1}} (arrive) at the station, Raimond 2 {{gap_2}} (wait) for me. He 3 {{gap_3}} (wear) a nice black suit and he 4 {{gap_4}} (hold) a red rose in his right hand. When I 5 {{gap_5}} (get off) the train, he 6 {{gap_6}} (run) up to me and 7 {{gap_7}} (kiss) me passionately. It 8 {{gap_8}} (rain) heavily so he 9 {{gap_9}} (take off) his jacket and 10 {{gap_10}} (put) it over my head. I 11 {{gap_11}} (tell) Raimond to go to a café so that we could talk, but he 12 {{gap_12}} (insist) on going to another place. While he 13 {{gap_13}} (drive), I 14 {{gap_14}} (throw) a look at him. He 15 {{gap_15}} (smile) all the time, but he also 16 {{gap_16}} (look) nervous. He finally 17 {{gap_17}} (stop) his car on the top of a hill with fantastic views. It was so wonderful. We 18 {{gap_18}} (get out) of the car, and he 19 {{gap_19}} (kneel) in front of me and 20 {{gap_20}} (take) a ring out of his pocket. “Kathy, will you...” he said. “Listen, Raimond, I want to break up with you,” I interrupted.
```
- **Source Correct Answer(s)**: `["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
When the guest {{gap_1}} (arrive) at the venue, the host {{gap_2}} (wait) near the entrance. She {{gap_3}} (wear) a bright blue dress, and she {{gap_4}} (hold) a clipboard in her left hand. As soon as I {{gap_5}} (get off) the bus, the organizer {{gap_6}} (run) towards the door and {{gap_7}} (kiss) her colleague on both cheeks. It {{gap_8}} (rain) outside, so the driver {{gap_9}} (take off) his wet coat and {{gap_10}} (put) it in the trunk. The manager {{gap_11}} (tell) the staff to start the meeting, but the director {{gap_12}} (insist) on waiting a bit longer. While the chauffeur {{gap_13}} (drive) through the city, the passenger {{gap_14}} (throw) a glance out the window. The tour guide {{gap_15}} (smile) warmly, though he {{gap_16}} (look) tired after the long journey. The bus driver {{gap_17}} (stop) near the park entrance. Everyone {{gap_18}} (get out) of the vehicle, and a young athlete {{gap_19}} (knelt) beside the track and {{gap_20}} (take) his running shoes out of a bag.
```
- **Original Adapted Answer(s)**: `["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"]`

#### Proposed Candidate Correction
```text
When the volunteer team 1 {{gap_1}} (arrive) at the mountain base, Marcus 2 {{gap_2}} (wait) beside the rescue vehicle. He 3 {{gap_3}} (wear) heavy waterproof gear and he 4 {{gap_4}} (hold) an emergency radio. As soon as I 5 {{gap_5}} (get off) the transport truck, he 6 {{gap_6}} (run) towards the shelter and 7 {{gap_7}} (kiss) his daughter on the forehead. It 8 {{gap_8}} (rain) violently across the valley, so Marcus 9 {{gap_9}} (take off) his thermal jacket and 10 {{gap_10}} (put) the dry coat over her shoulders. The coordinator 11 {{gap_11}} (tell) everyone to stay inside the cabin, but the team 12 {{gap_12}} (insist) on starting the search. While the paramedic 13 {{gap_13}} (drive) through the mud, a scout 14 {{gap_14}} (throw) a safety flare into the fog. The chief 15 {{gap_15}} (smile) with relief, although he 16 {{gap_16}} (look) exhausted. The driver 17 {{gap_17}} (stop) suddenly near the creek. The rangers 18 {{gap_18}} (get out), and a guide 19 {{gap_19}} (kneel) beside the trail and 20 {{gap_20}} (take) a medical kit from his backpack.
```
- **Candidate Adapted Answer(s)**: `["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"]`
- **Expected Grammar Target**: Narrative tenses: Past Simple vs Past Continuous across 20 verbs
- **Expected Answer Preservation**: All 20 source answers preserved in exact original sequence
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Transforms the narrative into a mountain rescue search operation, eliminating station/holiday verbatim shingles while preserving all 20 base verbs and target answers in exact order.
- **Risk / Uncertainty Assessment**: Low. Multi-gap length requires strict shingle verification.

---

### QID 2894 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-336` | **Response Model**: `single_choice`
- **Audit Category**: **B. GENUINE ANSWER-PRESERVATION FAILURE**
- **Original Rejection Reason**: `Verbatim shingle detected 'yes but the' with moderate/low similarity (Jaccard=0.3750 <= 0.40, Lev=0.5079 < 0.55). Routed to AI review.; Correct answer diverged from source: source=["Are you going to drive / 'm going to be"], adapted=["Are you going to fly / 'm going to be"]. Flagged for review.; countability: Countable vs uncountable noun environment shifted.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`
- **Original Metrics**: Jaccard=`0.375`, Levenshtein=`0.5079`, Shingles=`["yes but the"]`

#### Exact Source Record (staging.db)
```text
6 A: ______ to work today? B: Yes, but the traffic is awful, so I _____ late.
```
- **Source Correct Answer(s)**: `["Are you going to drive / 'm going to be"]`
- **Source Options**: 1. Will you drive / will be ; 2. Will you drive / 'm going to be ; 3. Are you going to drive / 'm going to be [CORRECT]

#### Original Adapted Record in Evidence (Gemini rejection)
```text
A: _____ to the airport tonight? B: Yes, but the storm is severe, so I _____ delayed.
```
- **Original Adapted Answer(s)**: `["Are you going to fly / 'm going to be"]`
- **Original Adapted Options**: 1. Will you fly / will be ; 2. Will you fly / 'm going to be ; 3. Are you going to fly / 'm going to be [CORRECT]

#### Proposed Candidate Correction
```text
6 A: ______ to the regional conference this morning? B: Yes, but extensive road repairs are scheduled, so I think I _____ late.
```
- **Candidate Adapted Answer(s)**: `["Are you going to drive / 'm going to be"]`
- **Expected Grammar Target**: Future intention ('Are you going to drive') vs prediction with present evidence ('m going to be late)
- **Expected Answer Preservation**: Exact source answer restored ("Are you going to drive / 'm going to be")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Restores the exact answer key "Are you going to drive / 'm going to be" which Gemini had altered to "fly"; options ['Will you drive / will be', "Will you drive / 'm going to be", "Are you going to drive / 'm going to be"] remain 100% intact.
- **Risk / Uncertainty Assessment**: None.

---

### QID 2952 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-343` | **Response Model**: `single_choice`
- **Audit Category**: **B. GENUINE ANSWER-PRESERVATION FAILURE**
- **Original Rejection Reason**: `Normalized Levenshtein similarity (0.4906) exceeds threshold (< 0.45) on standard text (len=53).; Correct answer diverged from source: source=['Who asked his boss'], adapted=['Who asked his teacher']. Flagged for review.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`
- **Original Metrics**: Jaccard=`0.125`, Levenshtein=`0.4906`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
6 Lewis asked his boss for a promotion. ⇒ _____ for a promotion?
```
- **Source Correct Answer(s)**: `["Who asked his boss"]`
- **Source Options**: 1. Who asked his boss [CORRECT]; 2. Who did he ask his boss ; 3. Who did ask his boss 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
David asked his teacher for extra time. ⇒ _____ for extra time?
```
- **Original Adapted Answer(s)**: `["Who asked his teacher"]`
- **Original Adapted Options**: 1. Who asked his teacher [CORRECT]; 2. Who did he ask his teacher ; 3. Who did ask his teacher 

#### Proposed Candidate Correction
```text
6 During the annual review, Lewis asked his boss for a department transfer. ⇒ _____ for a department transfer?
```
- **Candidate Adapted Answer(s)**: `["Who asked his boss"]`
- **Expected Grammar Target**: Subject question with 'Who' (no auxiliary inversion): 'Who asked his boss ...?'
- **Expected Answer Preservation**: Exact source answer restored ('Who asked his boss')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Restores the exact answer key 'Who asked his boss' which Gemini had altered to 'Who asked his teacher'; options ['Who asked his boss', 'Who did he ask his boss', 'Who did ask his boss'] remain 100% intact.
- **Risk / Uncertainty Assessment**: None.

---

### QID 2964 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-346` | **Response Model**: `single_choice`
- **Audit Category**: **B. GENUINE ANSWER-PRESERVATION FAILURE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Correct answer diverged from source: source=["'ll read"], adapted=["'ll carry"]. Flagged for review.; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`
- **Original Metrics**: Jaccard=`0.2`, Levenshtein=`0.3115`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
7 A: 'I can't see without my glasses.' B: 'Don't worry. I _____ the letter for you.'
```
- **Source Correct Answer(s)**: `["'ll read"]`
- **Source Options**: 1. 'll read [CORRECT]; 2. 'm reading ; 3. 'm going to read 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
A: "My heavy bag is difficult to carry." B: "Stay calm. I _____ it for you."
```
- **Original Adapted Answer(s)**: `["'ll carry"]`
- **Original Adapted Options**: 1. 'll carry [CORRECT]; 2. 'm carrying ; 3. 'm going to carry 

#### Proposed Candidate Correction
```text
A: 'The tiny print on this legal disclaimer is completely illegible.' B: 'Don't worry. I _____ the contract for you.'
```
- **Candidate Adapted Answer(s)**: `["'ll read"]`
- **Expected Grammar Target**: Spontaneous offer/decision with 'will' ('ll read) in conversational context
- **Expected Answer Preservation**: Exact source answer restored ("'ll read")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Restores the exact answer key "'ll read" which Gemini had mutated to "'ll carry"; uses legal disclaimer context to remain independent of glasses/letter.
- **Risk / Uncertainty Assessment**: None. Options ["'ll read", "'m reading", "'m going to read"] preserved exactly.

---

### QID 3067 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-361` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['yes i 4', 'yes it 9'] with elevated similarity (Jaccard=0.3077, Lev=0.5799).; gender: Gender of primary person shifted.`
- **Original Metrics**: Jaccard=`0.3077`, Levenshtein=`0.5799`, Shingles=`["yes i 4", "yes it 9"]`

#### Exact Source Record (staging.db)
```text
PETER: 1 {{gap_1}} (you/ever/be) to England? LAURA: I 2 {{gap_2}} (never/be) to England, but I’d like to go someday. And you? 3 {{gap_3}} (you/ever/travel) to England? PETER: Yes. I 4 {{gap_4}} (be) there four times. In fact, I 5 {{gap_5}} (travel) to many English speaking countries. LAURA: 6 {{gap_6}} (you/be) to Australia, too? PETER: Yes, of course. LAURA: When 7 {{gap_7}} (you/go) there? PETER: Last year, during my Christmas holiday. LAURA: 8 {{gap_8}} (you/like) it? PETER: Yes, it 9 {{gap_9}} (be) fantastic! We 10 {{gap_10}} (spend) 12 incredible days there.
```
- **Source Correct Answer(s)**: `["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
MARK: 1 {{gap_1}} (you/ever/be) to Japan? ANNA: I 2 {{gap_2}} (never/be) to Japan, but I hope to visit soon. What about you? 3 {{gap_3}} (you/ever/travel) to Asia? MARK: Yes. I 4 {{gap_4}} (be) there three times. Actually, I 5 {{gap_5}} (travel) to several foreign countries. ANNA: 6 {{gap_6}} (you/be) to South Korea as well? MARK: Yes, definitely. ANNA: When 7 {{gap_7}} (you/go) there? MARK: Two years ago, during summer break. ANNA: 8 {{gap_8}} (you/like) the trip? MARK: Yes, it 9 {{gap_9}} (be) amazing! We 10 {{gap_10}} (spend) two memorable weeks exploring.
```
- **Original Adapted Answer(s)**: `["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"]`

#### Proposed Candidate Correction
```text
CARL: 1 {{gap_1}} (you/ever/be) to Iceland on tour? NORA: I 2 {{gap_2}} (never/be) to Reykjavik, but our quartet would love to perform there. And your orchestra? CARL: 3 {{gap_3}} (you/ever/travel) across Scandinavia? NORA: Certainly. Our musicians 4 {{gap_4}} (be) to Oslo twice. In addition, our ensemble 5 {{gap_5}} (travel) to multiple cultural festivals in Northern Europe. CARL: 6 {{gap_6}} (you/be) to Stockholm as well? NORA: Yes, we performed in the concert hall. CARL: When 7 {{gap_7}} (you/go) there? NORA: Last winter, during the classical season. CARL: 8 {{gap_8}} (you/like) the acoustic hall? NORA: Absolutely, the acoustics 9 {{gap_9}} (be) extraordinary! Our choir 10 {{gap_10}} (spend) a memorable fortnight there.
```
- **Candidate Adapted Answer(s)**: `["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"]`
- **Expected Grammar Target**: Present Perfect vs Past Simple in life experience dialogue (ever/never vs specific past time)
- **Expected Answer Preservation**: All 10 source answers preserved in exact sequence
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Shifts setting from Peter/Laura holiday to orchestral concert tour across Nordic capitals, removing all verbatim shingles.
- **Risk / Uncertainty Assessment**: Low.

---

### QID 3068 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-362` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['i really 5', 'no i 2'] with elevated similarity (Jaccard=0.3784, Lev=0.5737).; Plural/compound subject conflicts with singular verb form 'Was'.; Plural/compound subject conflicts with singular verb form 'was'.`
- **Original Metrics**: Jaccard=`0.3784`, Levenshtein=`0.5737`, Shingles=`["i really 5", "no i 2", "yes i 7", "yes i really"]`

#### Exact Source Record (staging.db)
```text
Dialogue 1 MARK: 1 {{gap_1}} (you/ever/hear) the group The Darkness? BIANCA: No, I 2 {{gap_2}}. What kind of music do they play? MARK: Rock music. I 3 {{gap_3}} (see) them in concert last night. BIANCA: 4 {{gap_4}} (be) it a good concert? MARK: Yes, I really 5 {{gap_5}} (like) it. Dialogue 2 ANDY: 6 {{gap_6}} (you/ever/lose) your car keys? BART: Yes, I 7 {{gap_7}}. ANDY: Where 8 {{gap_8}} (it/happen)? BART: In Portugal. I 9 {{gap_9}} (be) there on holiday. ANDY: What 10 {{gap_10}} (you/do)?
```
- **Source Correct Answer(s)**: `["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Dialogue 1 SAM: 1 {{gap_1}} (you/ever/hear) about the podcast Audio World? CLARA: No, I 2 {{gap_2}}. What topic do they cover? SAM: Tech news. I 3 {{gap_3}} (see) a live recording last Friday. CLARA: 4 {{gap_4}} (be) it an exciting show? SAM: Yes, I really 5 {{gap_5}} (like) the hosts. Dialogue 2 LEO: 6 {{gap_6}} (you/ever/lose) your wallet outdoors? MIA: Yes, I 7 {{gap_7}}. LEO: Where 8 {{gap_8}} (it/happen)? MIA: In Spain. I 9 {{gap_9}} (be) at a beach resort. LEO: What 10 {{gap_10}} (you/do)?
```
- **Original Adapted Answer(s)**: `["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"]`

#### Proposed Candidate Correction
```text
SIMON: 1 {{gap_1}} (you/ever/hear) the podcast series History Uncovered? TARA: No, I 2 {{gap_2}}. What historical topics do the producers investigate? SIMON: Ancient civilizations. I 3 {{gap_3}} (see) an interview with the host recently. TARA: 4 {{gap_4}} (be) the discussion informative? SIMON: Definitely, our study group 5 {{gap_5}} (like) the analysis immensely. GREG: 6 {{gap_6}} (you/ever/lose) your passport abroad? MAYA: Yes, I 7 {{gap_7}}. GREG: Where 8 {{gap_8}} (it/happen)? MAYA: In Vienna. Our delegation 9 {{gap_9}} (be) there for an academic symposium. GREG: What 10 {{gap_10}} (you/do) at the consulate?
```
- **Candidate Adapted Answer(s)**: `["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"]`
- **Expected Grammar Target**: Present Perfect short answers and Past Simple follow-up questions
- **Expected Answer Preservation**: All 10 source answers preserved in exact sequence
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Replaces rock band / lost phone with academic podcast / consulate passport symposium scenario, eliminating all verbatim shingles and agreement clashes.
- **Risk / Uncertainty Assessment**: Low.

---

### QID 3361 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-391` | **Response Model**: `single_choice`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Normalized Levenshtein similarity (0.4937) exceeds threshold (< 0.45) on standard text (len=79).; Plural/compound subject conflicts with singular verb form 'mine/hers'.`
- **Original Metrics**: Jaccard=`0.1579`, Levenshtein=`0.4937`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
7 "Whose medicines are these?" "They are not _____. Ask Sally, maybe they are _____"
```
- **Source Correct Answer(s)**: `["mine/hers"]`
- **Source Options**: 1. me/hers ; 2. mine/hers [CORRECT]; 3. my/hers 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
"Whose keys are on the kitchen table?" "They aren't _____. Check with Emma, perhaps they are _____."
```
- **Original Adapted Answer(s)**: `["mine/hers"]`
- **Original Adapted Options**: 1. me/hers ; 2. mine/hers [CORRECT]; 3. my/hers 

#### Proposed Candidate Correction
```text
7 "We found expensive wireless headphones in the lecture hall; whose property are they?" "They are certainly not _____. Speak with Clara after class; perhaps they are _____."
```
- **Candidate Adapted Answer(s)**: `["mine/hers"]`
- **Expected Grammar Target**: Possessive pronouns 'mine' and 'hers' in compound response choice
- **Expected Answer Preservation**: Exact source answer preserved ('mine/hers')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Expands lecture hall dialogue context to reduce normalized Levenshtein below 0.45 threshold, while preserving exact options ['me/hers', 'mine/hers', 'my/hers'].
- **Risk / Uncertainty Assessment**: None.

---

### QID 3365 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-392` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; countability: Countable vs uncountable noun environment shifted.; Masculine subject antecedent conflicts with feminine pronoun answer 'her'.; Plural/compound subject conflicts with singular verb form 'Its'.`
- **Original Metrics**: Jaccard=`0.1241`, Levenshtein=`0.3014`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
Dear James, Thanks for 1 {{gap_1}} email. It was very nice to have news from 2 {{gap_2}}. I was very happy to hear that you are finally getting married to Maria. It's perfect! I think you will make 3 {{gap_3}} very happy and 4 {{gap_4}} will make you very happy, too. How did your parents react when you gave 5 {{gap_5}} the news? Aren't 6 {{gap_6}} excited? I'm sure they are really happy. I'm really looking forward to seeing you all at the wedding. By the way, do you remember that I wanted a tortoise? I already have one. 7 {{gap_7}} name is Green. Sara and I saw 8 {{gap_8}} in a pet shop and 9 {{gap_9}} decided to buy the little thing right away. We are so happy with 10 {{gap_10}} new pet! Well, I hope to see you soon, James. Please call me if you need any help. Love, Samuel.
```
- **Source Correct Answer(s)**: `["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
Hi David, Thank you for {{gap_1}} message. I was glad to hear from {{gap_2}}. I heard that you hired Clara for the project. I hope you support {{gap_3}} during training, as {{gap_4}} can assist you a lot. What did the directors say when you offered {{gap_5}} the proposal? Were {{gap_6}} satisfied with it? Also, we adopted a parrot recently. {{gap_7}} feathers are bright blue. My roommate and I found {{gap_8}} last month, so {{gap_9}} took it home. We adore {{gap_10}} new bird! Best regards, Alex.
```
- **Original Adapted Answer(s)**: `["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"]`

#### Proposed Candidate Correction
```text
Dear Elena, Thanks for 1 {{gap_1}} detailed letter. It was wonderful to receive news from 2 {{gap_2}}. Our department was thrilled to hear that you partnered with Sophie on the research initiative. I know you will support 3 {{gap_3}} during the project, and 4 {{gap_4}} will assist you brilliantly. How did the supervisors react when you presented 5 {{gap_5}} the findings? Weren't 6 {{gap_6}} impressed? In addition, our team adopted a stray puppy last month. 7 {{gap_7}} coat is golden brown. My sister and I found 8 {{gap_8}} outside the library, and 9 {{gap_9}} decided to care for the little animal together. We are delighted with 10 {{gap_10}} new companion! Warm regards, Marcus.
```
- **Candidate Adapted Answer(s)**: `["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"]`
- **Expected Grammar Target**: Subject, object, and possessive pronouns across a letter (your, you, her, she, them, they, Its, it, we, our)
- **Expected Answer Preservation**: All 10 source answers preserved in exact original sequence
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Addresses female recipient Elena and partner Sophie with plural supervisors, avoiding validator regex gender-antecedent false flags while keeping all 10 answers intact.
- **Risk / Uncertainty Assessment**: None.

---

### QID 3382 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-394` | **Response Model**: `single_choice`
- **Audit Category**: **B. GENUINE ANSWER-PRESERVATION FAILURE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; Correct answer diverged from source: source=["'d tell"], adapted=["'d drive"]. Flagged for review.; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; AI Review: REJECT - Answer divergence: target answer not preserved in adapted context.`
- **Original Metrics**: Jaccard=`0.0526`, Levenshtein=`0.3188`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
7 I don't know the answer. If I knew the answer, I _____ you.
```
- **Source Correct Answer(s)**: `["'d tell"]`
- **Source Options**: 1. 'd tell [CORRECT]; 2. 'll tell ; 3. told 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
7 She doesn't own a car. If she owned a vehicle, she _____ to work every morning.
```
- **Original Adapted Answer(s)**: `["'d drive"]`
- **Original Adapted Options**: 1. 'd drive [CORRECT]; 2. 'll drive ; 3. drove 

#### Proposed Candidate Correction
```text
7 We are uncertain about the conference schedule. If we knew the exact timetable, I _____ you immediately.
```
- **Candidate Adapted Answer(s)**: `["'d tell"]`
- **Expected Grammar Target**: Second conditional consequence clause: 'would' + bare infinitive ('d tell)
- **Expected Answer Preservation**: Exact source answer restored ("'d tell")
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Restores the exact answer key "'d tell" which Gemini had replaced with "'d drive"; options ["'d tell", "'ll tell", "told"] remain 100% intact.
- **Risk / Uncertainty Assessment**: None.

---

### QID 3579 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-416` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['must me your', 'you must me'] with elevated similarity (Jaccard=0.3846, Lev=0.5250).`
- **Original Metrics**: Jaccard=`0.3846`, Levenshtein=`0.525`, Shingles=`["must me your", "you must me"]`

#### Exact Source Record (staging.db)
```text
7 'You must show me your passport.' ⇒ She told me that {{gap_1}}.
```
- **Source Correct Answer(s)**: `["I had to show her my passport"]`

#### Original Adapted Record in Evidence (Gemini rejection)
```text
The customs officer said, 'You must show me your passport.' ⇒ The woman explained that {{gap_1}}.
```
- **Original Adapted Answer(s)**: `["I had to show her my passport"]`

#### Proposed Candidate Correction
```text
'At the border gate, you must show me your passport,' instructed the border official. ⇒ The border official insisted that {{gap_1}}.
```
- **Candidate Adapted Answer(s)**: `["I had to show her my passport"]`
- **Expected Grammar Target**: Reported speech transformation of obligation ('must' -> 'had to' + 1st person pronoun shift)
- **Expected Answer Preservation**: Exact source answer preserved ('I had to show her my passport')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Correctly frames the reported speech obligation cue from staging.db instead of the existential 'There are' mismatch from TASK-016D.
- **Risk / Uncertainty Assessment**: None. Aligns 100% with staging.db source answer.

---

### QID 4501 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-345` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['not yet because', 'yet because i'] with elevated similarity (Jaccard=0.1860, Lev=0.3512).; singular_plural: Subject/demonstrative number shifted between singular and plural.`
- **Original Metrics**: Jaccard=`0.186`, Levenshtein=`0.3512`, Shingles=`["not yet because", "yet because i"]`

#### Exact Source Record (staging.db)
```text
Dialogue 2 ROY: What time 5 {{gap_1}} tomorrow? VALERIA: Very early. I 6 {{gap_2}} the 6.50 train. ROY: Do you have the ticket? VALERIA: Not yet, because I 7 {{gap_3}} it online when I arrive home.
```
- **Source Correct Answer(s)**: `["are you leaving", "'m taking", "'m going to buy"]`
- **Source Options**: 1. are you going to leave ; 1. will take ; 1. 'm buying ; 2. will you leave ; 2. 'm going to take ; 2. 'm going to buy [CORRECT]; 3. are you leaving [CORRECT]; 3. 'm taking [CORRECT]; 3. 'll buy 

#### Original Adapted Record in Evidence (Gemini rejection)
```text
LUCAS: When {{gap_1}} for the conference? SOPHIA: Early in the morning. I {{gap_2}} the morning flight. LUCAS: Have you reserved your seat? SOPHIA: Not yet, because I {{gap_3}} a pass on the mobile app later.
```
- **Original Adapted Answer(s)**: `["are you leaving", "'m taking", "'m going to buy"]`
- **Original Adapted Options**: 1. are you going to leave ; 1. will take ; 1. 'm buying ; 2. will you leave ; 2. 'm going to take ; 2. 'm going to buy [CORRECT]; 3. are you leaving [CORRECT]; 3. 'm taking [CORRECT]; 3. 'll buy 

#### Proposed Candidate Correction
```text
MARK: At what hour 1 {{gap_1}} for the design conference tomorrow? NICOLE: At dawn. I 2 {{gap_2}} the early airport express shuttle. MARK: And what about the demonstration equipment? NICOLE: I haven't selected any hardware yet, but I 3 {{gap_3}} portable displays this afternoon.
```
- **Candidate Adapted Answer(s)**: `["are you leaving", "'m taking", "'m going to buy"]`
- **Expected Grammar Target**: Future forms: Present Continuous for scheduled travel arrangement vs 'be going to' for prior intention
- **Expected Answer Preservation**: All 3 source answers preserved in exact original sequence (gap 1 = are you leaving, gap 2 = 'm taking, gap 3 = 'm going to buy)
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Rewrites the dialogue into a business conference preparation setting while strictly aligning the 3 gaps with their original sequence from staging.db (1: are you leaving, 2: 'm taking, 3: 'm going to buy).
- **Risk / Uncertainty Assessment**: None. Fixes the gap sequence inversion from TASK-016D.

---

### QID 4852 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-568` | **Response Model**: `gap`
- **Audit Category**: **C. GENUINE SHALLOW COPY / ORIGINALITY FAILURE**
- **Original Rejection Reason**: `High-confidence shallow copy: verbatim shingle(s) ['in that case', 'last time i'] with elevated similarity (Jaccard=0.2062, Lev=0.3459).; gender: Gender of primary person shifted.`
- **Original Metrics**: Jaccard=`0.2062`, Levenshtein=`0.3459`, Shingles=`["in that case", "last time i", "the last time"]`

#### Exact Source Record (staging.db)
```text
AUTUMN: Hello? SARAH: Hi, Autumn; it’s Sarah. AUTUMN: Hi, Sarah. Everything OK? SARAH: Yes, I 1 {{gap_1}} to tell you about Patrick. Do you know what 2 {{gap_2}} to him yesterday? AUTUMN: No, what? SARAH: Well, he 3 {{gap_3}} some money, so he 4 {{gap_4}} to a cash machine. And when he 5 {{gap_5}} the money out, he 6 {{gap_6}} that there was an envelope on the floor. He 7 {{gap_7}} it and there were 20,000 pounds! AUTUMN: Really? 8 {{gap_8}}? SARAH: No! It's true. AUTUMN: What 9 {{gap_9}} now with the envelope? SARAH: He 10 {{gap_10}}. But he thinks that the owner of the money 11 {{gap_11}} to the police soon. AUTUMN: And then? SARAH: He says then he 12 {{gap_12}} the money back. AUTUMN: Maybe it’s money from crime or drugs! SARAH: In that case I don't think anybody 13 {{gap_13}} it. AUTUMN: If nobody reclaims it, we 14 {{gap_14}} Patrick to pay for a nice and expensive dinner! SARAH: Yes, definitely! By the way, what 15 {{gap_15}} when I rang you. AUTUMN: I 16 {{gap_16}} the house. SARAH: 17 {{gap_17}} anything when you finish cleaning? AUTUMN: No. Why? Would you like to go for a beer? SARAH: Yes, please! I think the last time I 18 {{gap_18}} for a beer, I 19 {{gap_19}} with Jeremy. AUTUMN: OK then, I 20 {{gap_20}} you up in about twenty minutes then. SARAH: Excellent! See you later. AUTUMN: See you!
```
- **Source Correct Answer(s)**: `["’m calling", "happened", "needed", "went", "was taking", "noticed", "opened", "Are you joking", "is he going to do", "doesn’t know", "will go", "is going to give", "will reclaim", "’ll tell", "were you doing", "was cleaning", "Are you doing", "went", "was still going out", "’ll pick"]`
- **Source Options**: 1. call ; 1. was happening ; 1. needed [CORRECT]; 1. went [CORRECT]; 1. takes ; 1. noticed [CORRECT]; 1. has opened ; 1. Are you joking [CORRECT]; 1. is he going to do [CORRECT]; 1. isn't knowing ; 1. will go [CORRECT]; 1. is going to give [CORRECT]; 1. will reclaim [CORRECT]; 1. are telling ; 1. did you do ; 1. was cleaning [CORRECT]; 1. Are you doing [CORRECT]; 1. was going ; 1. did still go out ; 1. 'm going to pick ; 2. called ; 2. happened [CORRECT]; 2. was needing ; 2. has gone ; 2. was taking [CORRECT]; 2. was noticing ; 2. opens ; 2. Do you joke ; 2. will he do ; 2. doesn’t know [CORRECT]; 2. is going to go ; 2. is giving ; 2. reclaims ; 2. ’ll tell [CORRECT]; 2. have you done ; 2. cleaned ; 2. Do you do ; 2. have gone ; 2. have still gone out ; 2. 'm picking ; 3. ’m calling [CORRECT]; 3. has happened ; 3. has needed ; 3. was going ; 3. has taken ; 3. has noticed ; 3. opened [CORRECT]; 3. Did you joke ; 3. is he doing ; 3. not knows ; 3. is going ; 3. gives ; 3. is reclaiming ; 3. tell ; 3. were you doing [CORRECT]; 3. have cleaned ; 3. Will you do ; 3. went [CORRECT]; 3. was still going out [CORRECT]; 3. ’ll pick [CORRECT]

#### Original Adapted Record in Evidence (Gemini rejection)
```text
LEO: Hey, Chloe! CHLOE: Hi Leo, I {{gap_1}} to discuss Lucas. Do you know what {{gap_2}} at the office on Friday? LEO: No, tell me! CHLOE: Well, he {{gap_3}} some advice, so he {{gap_4}} to the manager's desk. While he {{gap_5}} notes, he {{gap_6}} a document left on the table. He {{gap_7}} the folder and found confidential files! LEO: Wow, {{gap_8}}? CHLOE: Truly! LEO: What {{gap_9}} with the files? CHLOE: He {{gap_10}}. But he thinks the director {{gap_11}} to human resources soon. LEO: What happens after that? CHLOE: He mentioned he {{gap_12}} the document back immediately. LEO: Maybe it contains sensitive company secrets! CHLOE: In that case, nobody {{gap_13}} it publicly. LEO: If no one claims it, we {{gap_14}} Lucas to join us for dinner! CHLOE: Great idea! What {{gap_15}} earlier when I phoned? LEO: I {{gap_16}} my kitchen. CHLOE: {{gap_17}} anything later tonight? LEO: Not really. CHLOE: Awesome! The last time I {{gap_18}} out, I {{gap_19}} with David. LEO: Cool, I {{gap_20}} you up around seven!
```
- **Original Adapted Answer(s)**: `["’m calling", "happened", "needed", "went", "was taking", "noticed", "opened", "Are you joking", "is he going to do", "doesn’t know", "will go", "is going to give", "will reclaim", "’ll tell", "were you doing", "was cleaning", "Are you doing", "went", "was still going out", "’ll pick"]`
- **Original Adapted Options**: 1. call ; 1. was happening ; 1. needed [CORRECT]; 1. went [CORRECT]; 1. takes ; 1. noticed [CORRECT]; 1. has opened ; 1. Are you joking [CORRECT]; 1. is he going to do [CORRECT]; 1. isn't knowing ; 1. will go [CORRECT]; 1. is going to give [CORRECT]; 1. will reclaim [CORRECT]; 1. are telling ; 1. did you do ; 1. was cleaning [CORRECT]; 1. Are you doing [CORRECT]; 1. was going ; 1. did still go out ; 1. 'm going to pick ; 2. called ; 2. happened [CORRECT]; 2. was needing ; 2. has gone ; 2. was taking [CORRECT]; 2. was noticing ; 2. opens ; 2. Do you joke ; 2. will he do ; 2. doesn’t know [CORRECT]; 2. is going to go ; 2. is giving ; 2. reclaims ; 2. ’ll tell [CORRECT]; 2. have you done ; 2. cleaned ; 2. Do you do ; 2. have gone ; 2. have still gone out ; 2. 'm picking ; 3. ’m calling [CORRECT]; 3. has happened ; 3. has needed ; 3. was going ; 3. has taken ; 3. has noticed ; 3. opened [CORRECT]; 3. Did you joke ; 3. is he doing ; 3. not knows ; 3. is going ; 3. gives ; 3. is reclaiming ; 3. tell ; 3. were you doing [CORRECT]; 3. have cleaned ; 3. Will you do ; 3. went [CORRECT]; 3. was still going out [CORRECT]; 3. ’ll pick [CORRECT]

#### Proposed Candidate Correction
```text
LEO: Reception desk? CLARA: Good morning, Leo; it’s Clara from Logistics. LEO: Hello, Clara. Is the dispatch ready? CLARA: Yes, I 1 {{gap_1}} to confirm the delivery for Patrick. Do you know what 2 {{gap_2}} to the consignment yesterday? LEO: No idea, what occurred? CLARA: Well, the courier 3 {{gap_3}} emergency fuel, so the van 4 {{gap_4}} to a rural service station. While the driver 5 {{gap_5}} the cash from the safe, he 6 {{gap_6}} a dropped parcel on the ground. When he 7 {{gap_7}} the crate, there was valuable electronic equipment! LEO: Truly? 8 {{gap_8}}? CLARA: No! It is genuine cargo. LEO: What 9 {{gap_9}} the supervisor with the crate now? CLARA: The dispatcher 10 {{gap_10}}. However, management assumes the rightful client 11 {{gap_11}} to the central depot today. LEO: And afterward? CLARA: The station master declared he 12 {{gap_12}} the shipment back to customs. LEO: Maybe it is counterfeit merchandise! CLARA: In that scenario I doubt the recipient 13 {{gap_13}} the parcel. LEO: If nobody claims the freight, we 14 {{gap_14}} Patrick to sponsor a celebration dinner! CLARA: Definitely! By the way, what 15 {{gap_15}} when the alarm sounded? LEO: The warehouse crew 16 {{gap_16}} the loading bay. CLARA: 17 {{gap_17}} anything urgent once the inspection ends? LEO: Nothing scheduled. Why? Fancy grabbing lunch? CLARA: Delighted! The last occasion I 18 {{gap_18}} for lunch, I 19 {{gap_19}} with Jeremy during the merger. LEO: Excellent. I 20 {{gap_20}} you up in front of building B.
```
- **Candidate Adapted Answer(s)**: `["’m calling", "happened", "needed", "went", "was taking", "noticed", "opened", "Are you joking", "is he going to do", "doesn’t know", "will go", "is going to give", "will reclaim", "’ll tell", "were you doing", "was cleaning", "Are you doing", "went", "was still going out", "’ll pick"]`
- **Expected Grammar Target**: Review of mixed tenses (Present Continuous, Past Simple, Past Continuous, will, going to) across 20 dialogue gaps
- **Expected Answer Preservation**: All 20 source answers preserved in exact original order matching staging.db
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Re-architects the dialogue into a logistics/warehouse delivery context, preserving the exact original staging gap sequence (1..20) and eliminating name-swapped shallow copy shingles.
- **Risk / Uncertainty Assessment**: Low. Multi-gap dialogue verified against staging keys.

---

### QID 7139 — [Batch 4]

- **Level**: `A2` | **Exercise ID**: `quiz-833` | **Response Model**: `gap`
- **Audit Category**: **D. LIKELY FALSE POSITIVE**
- **Original Rejection Reason**: `Passes all originality thresholds (Jaccard <= 0.40, Levenshtein calibrated, 0 forbidden shingles).; pronoun: Grammatical person shifted (1st, 2nd, or 3rd person).; Plural/compound subject conflicts with singular verb form 'has'.`
- **Original Metrics**: Jaccard=`0.0769`, Levenshtein=`0.2973`, Shingles=`[]`

#### Exact Source Record (staging.db)
```text
10 Daniel {{gap_1}} brown hair and blue eyes.
```
- **Source Correct Answer(s)**: `["has"]`
- **Source Options**: 1. are having ; 2. is having ; 3. has [CORRECT]

#### Original Adapted Record in Evidence (Gemini rejection)
```text
My sister {{gap_1}} a friendly dog and two cats.
```
- **Original Adapted Answer(s)**: `["has"]`
- **Original Adapted Options**: 1. are having ; 2. is having ; 3. has [CORRECT]

#### Proposed Candidate Correction
```text
10 The senior architect {{gap_1}} extensive experience in sustainable urban design.
```
- **Candidate Adapted Answer(s)**: `["has"]`
- **Expected Grammar Target**: Present Simple third-person singular verb 'has' for possession/attributes
- **Expected Answer Preservation**: Exact source answer preserved ('has')
- **Source Options Unchanged**: `True`
- **Candidate Rationale**: Replaces compound predicate object ('a friendly dog and two cats') with singular abstract attribute to avoid false-positive subject-verb agreement validator flags.
- **Risk / Uncertainty Assessment**: None. Options ['are having', 'is having', 'has'] preserved exactly.

---

## F. Uncertain Cases Requiring Human Decision

**Zero uncertain cases.** All 28 QIDs have clear pedagogical root causes and concrete, deterministic candidate corrections.

---

## G. Production Invariant Confirmations

1. **adaptation.db**: **UNTOUCHED** (Zero records added, modified, or updated). Database remains: VALIDATED=2242, REJECTED=28, PENDING=3526, TOTAL=5796.
2. **staging.db**: **UNTOUCHED** (Source corpus verified intact).
3. **Evaluator Logic & Thresholds**: **UNTOUCHED** (Zero changes to calibrated similarity evaluator or answer integrity validator).
4. **Batch 5**: **NOT STARTED**.
