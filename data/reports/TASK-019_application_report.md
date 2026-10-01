# TASK-019: Application Report — All 28 Approved Corrections

**Generated**: 2026-10-01T08:55:02.205651+00:00  
**Execution Mode**: `ATOMIC COMMIT`  
**Transaction Result**: `COMMITTED`  

---

## 1. Executive Summary & Database State

| Database Status | Counts Before | Counts After | Expected Final | Status |
| :--- | :---: | :---: | :---: | :---: |
| **VALIDATED** | 2,242 | **2,270** | 2,270 | MATCH |
| **REJECTED** | 28 | **0** | 0 | MATCH |
| **PENDING** | 3,526 | **3,526** | 3,526 | MATCH |
| **TOTAL** | 5,796 | **5,796** | 5,796 | MATCH |

- **Exact Modified Records**: 28 QIDs (`2823, 2847, 2894, 2952, 2964, 3067, 3068, 3361, 3365, 3382, 3579, 3694, 3917, 4045, 4054, 4188, 4214, 4254, 4501, 4852, 5069, 5085, 5088, 5134, 5142, 5144, 5736, 7139`)
- **Unexpected Modifications**: **0**
- **Preview Gate**: **12 / 12 PASSED**
- **Python Regression Tests**: **PASSED**
- **Jest Domain Tests**: **PASSED**

---

## 2. All 28 Applied Corrections (Summary Table)

| QID | Batch | Level | Old Status | New Status | Candidate Source | Evaluator Status | AI / Teacher Review | Final Verdict |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2823** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **2847** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **2894** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **2952** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **2964** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `REVIEW_REQUIRED` | `APPROVED_BY_TEACHER` | **PASS** |
| **3067** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **3068** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **3361** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **3365** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **3382** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **3579** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **3694** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **3917** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **4045** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **4054** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `REVIEW_REQUIRED` | `APPROVED_BY_TEACHER` | **PASS** |
| **4188** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `REVIEW_REQUIRED` | `APPROVED_BY_TEACHER` | **PASS** |
| **4214** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **4254** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **4501** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **4852** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **5069** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **5085** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **5088** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **5134** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018B` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **5142** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `REVIEW_REQUIRED` | `APPROVED_BY_TEACHER` | **PASS** |
| **5144** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `NOT_REQUIRED` | **PASS** |
| **5736** | Historical Batch 1 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |
| **7139** | Batch 4 | A1/A2 | REJECTED | **VALIDATED** | `TASK-018` | `VALIDATED` | `APPROVED_BY_TEACHER` | **PASS** |

---

## 3. Side-by-Side Content Diffs (All 28 QIDs)

### QID 2823 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['had', 'drove', 'broke', 'spent', 'got', "couldn't", "weren't", "didn't know", 'found', 'stayed', 'saw', 'went', 'bought', 'wanted', "didn't have", 'was', 'was', 'started', 'left', 'had']`
- **Applied Answer**: `['had', 'drove', 'broke', 'spent', 'got', "couldn't", "weren't", "didn't know", 'found', 'stayed', 'saw', 'went', 'bought', 'wanted', "didn't have", 'was', 'was', 'started', 'left', 'had']`
- **Evaluator Metrics**: Jaccard = `0.2157`, Levenshtein = `0.3491`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
Last autumn our university department 1 {{gap_1}} (have) an intensive ecological expedition. Researchers 2 {{gap_2}} (drive) heavy rental vans across northern Yorkshire, however an axle 3 {{gap_3}} (break) unexpectedly on rural backroads, so the biologists 4 {{gap_4}} (spend) that opening evening inside an emergency hostel. Upon arrival at the valley station, fieldworkers 5 {{gap_5}} (get) into severe difficulties; supervisors 6 {{gap_6}} (not can) locate reliable heating equipment, as there 7 {{gap_7}} (not be) sufficient functional radiators in the dormitory. Initially students 8 {{gap_8}} (not know) how to resolve logistical issues, yet eventually team leaders 9 {{gap_9}} (find) insulated mountain cabins where the entire crew 10 {{gap_10}} (stay) throughout the field project. During surveys, scientists 11 {{gap_11}} (see) rare raptors soaring overhead, regularly 12 {{gap_12}} (go) into dense woodland reserves, and later 13 {{gap_13}} (buy) specialized sample kits from local suppliers. Faculty staff 14 {{gap_14}} (want) to explore remote peaks, although researchers 15 {{gap_15}} (not have) spare daylight hours because terrain navigation 16 {{gap_16}} (be) especially demanding. Overall mountain climate 17 {{gap_17}} (be) remarkably crisp, until blizzards suddenly 18 {{gap_18}} (start) howling hours before departure. When researchers finally 19 {{gap_19}} (leave) the remote valley, everyone agreed our expedition members 20 {{gap_20}} (have) an outstanding educational journey.
```

---

### QID 2847 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['arrived', 'was waiting', 'was wearing', 'was holding', 'got off', 'ran', 'kissed', 'was raining', 'took off', 'put', 'told', 'insisted', 'was driving', 'threw', 'was smiling', 'looked', 'stopped', 'got out', 'knelt', 'took']`
- **Applied Answer**: `['arrived', 'was waiting', 'was wearing', 'was holding', 'got off', 'ran', 'kissed', 'was raining', 'took off', 'put', 'told', 'insisted', 'was driving', 'threw', 'was smiling', 'looked', 'stopped', 'got out', 'knelt', 'took']`
- **Evaluator Metrics**: Jaccard = `0.2426`, Levenshtein = `0.3886`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018B: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
When the visiting director 1 {{gap_1}} (arrive) inside studio three, producer Marcus 2 {{gap_2}} (wait) patiently near backstage. He 3 {{gap_3}} (wear) a formal theatrical costume and 4 {{gap_4}} (hold) an antique ceremonial dagger in his left palm. As the lead actor 5 {{gap_5}} (get off) a tour shuttle, an eager understudy 6 {{gap_6}} (run) across the courtyard and 7 {{gap_7}} (kiss) both cheeks in dramatic greeting. Because icy sleet 8 {{gap_8}} (rain) upon the set, stagehands quickly 9 {{gap_9}} (take off) protective tarp coverings and 10 {{gap_10}} (put) dry blankets over camera gear. The director 11 {{gap_11}} (tell) technicians to move inside the soundstage, yet producers 12 {{gap_12}} (insist) on filming outdoors. While the stunt coordinator 13 {{gap_13}} (drive) the vintage limousine, cameramen 14 {{gap_14}} (throw) anxious glances toward gathering storm clouds. The performer 15 {{gap_15}} (smile) serenely throughout rehearsals, though lighting assistants 16 {{gap_16}} (look) visibly exhausted. The driver eventually 17 {{gap_17}} (stop) near an old stone gatehouse. Both actors 18 {{gap_18}} (get out) onto wet cobblestones, where the villain character 19 {{gap_19}} (kneel) gracefully on stage and 20 {{gap_20}} (take) a silver prop medallion from inside a velvet pouch. Bravo, that scene was brilliant, the director announced.
```

---

### QID 2894 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["Are you going to drive / 'm going to be"]`
- **Applied Answer**: `["Are you going to drive / 'm going to be"]`
- **Evaluator Metrics**: Jaccard = `0.3000`, Levenshtein = `0.3627`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
6 A: ______ to the regional conference this morning? B: Yes, but extensive road repairs are scheduled, so I think I _____ late.
```

---

### QID 2952 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['Who asked his boss']`
- **Applied Answer**: `['Who asked his boss']`
- **Evaluator Metrics**: Jaccard = `0.0526`, Levenshtein = `0.2179`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
In yesterday's staff conference, Lewis directly approached the company boss about annual leave policy. Choose the correct question structure: _____ about annual leave policy?
```

---

### QID 2964 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["'ll read"]`
- **Applied Answer**: `["'ll read"]`
- **Evaluator Metrics**: Jaccard = `0.2727`, Levenshtein = `0.4227`, Shingles = `["don't worry i"]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
A: 'The tiny print on this legal disclaimer is completely illegible.' B: 'Don't worry. I _____ the contract for you.'
```

---

### QID 3067 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['Have you ever been', 'have never been', 'have you ever travelled', 'have been', 'have travelled', 'Have you been', 'did you go', 'Did you like', 'was', 'spent']`
- **Applied Answer**: `['Have you ever been', 'have never been', 'have you ever travelled', 'have been', 'have travelled', 'Have you been', 'did you go', 'Did you like', 'was', 'spent']`
- **Evaluator Metrics**: Jaccard = `0.1441`, Levenshtein = `0.3469`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
LIAM: 1 {{gap_1}} (ever/you/be) inside the Royal Botanic greenhouses?
SOPHIA: Personally, I 2 {{gap_2}} (never/be) among those historic conservatories, though I would love seeing exotic plants. What about your field expeditions? 3 {{gap_3}} (ever/you/travel) across equatorial South America?
LIAM: Yes, indeed. I 4 {{gap_4}} (be) across the Amazon basin repeatedly. Moreover, I 5 {{gap_5}} (travel) through seven rainforest conservation zones.
SOPHIA: 6 {{gap_6}} (you/be) aboard riverboat expeditions as well?
LIAM: Naturally!
SOPHIA: At what point 7 {{gap_7}} (you/go) navigating along the Rio Negro?
LIAM: Two winters ago, during my sabbatical research leave.
SOPHIA: 8 {{gap_8}} (you/like) camping beside jungle tributaries?
LIAM: Enormously; the biodiversity 9 {{gap_9}} (be) extraordinary! My scientific colleagues 10 {{gap_10}} (spend) nearly three weeks recording nocturnal wildlife.
```

---

### QID 3068 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['Have you ever heard', "haven't", 'saw', 'Was', 'liked', 'Have you ever lost', 'have', 'did it happen', 'was', 'did you do']`
- **Applied Answer**: `['Have you ever heard', "haven't", 'saw', 'Was', 'liked', 'Have you ever lost', 'have', 'did it happen', 'was', 'did you do']`
- **Evaluator Metrics**: Jaccard = `0.2000`, Levenshtein = `0.3424`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018B: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
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

---

### QID 3361 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['mine/hers']`
- **Applied Answer**: `['mine/hers']`
- **Evaluator Metrics**: Jaccard = `0.1538`, Levenshtein = `0.3113`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
7 "We found expensive wireless headphones in the lecture hall; whose property are they?" "They are certainly not _____. Speak with Clara after class; perhaps they are _____."
```

---

### QID 3365 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['your', 'you', 'her', 'she', 'them', 'they', 'Its', 'it', 'we', 'our']`
- **Applied Answer**: `['your', 'you', 'her', 'she', 'them', 'they', 'Its', 'it', 'we', 'our']`
- **Evaluator Metrics**: Jaccard = `0.1200`, Levenshtein = `0.2665`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018B: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
Greetings Robert!
I thoroughly appreciated receiving 1 {{gap_1}} thoughtful post-conference dispatch; discovering latest updates regarding 2 {{gap_2}} brought immense satisfaction. Our entire laboratory praised Dr. Angela's fellowship appointment; colleagues respect 3 {{gap_3}} tremendously, and everyone knows 4 {{gap_4}} will direct department research with remarkable vision. Did board trustees approve project proposals once coordinators presented 5 {{gap_5}} the revised budget? Surely 6 {{gap_6}} recognize how crucial institutional funding remains.
Additionally, our institute recently installed a solar observatory dome; 7 {{gap_7}} official designation is Helios Peak. Elena and I evaluated 8 {{gap_8}} during field trials, whereupon 9 {{gap_9}} resolved to finalize procurement without hesitation. Faculty members take immense pride in 10 {{gap_10}} innovative facility!
Warmest wishes, Nicholas
```

---

### QID 3382 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["'d tell"]`
- **Applied Answer**: `["'d tell"]`
- **Evaluator Metrics**: Jaccard = `0.2941`, Levenshtein = `0.3684`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
7 We are uncertain about the conference schedule. If we knew the exact timetable, I _____ you immediately.
```

---

### QID 3579 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['I had to show her my passport']`
- **Applied Answer**: `['I had to show her my passport']`
- **Evaluator Metrics**: Jaccard = `0.1786`, Levenshtein = `0.1702`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
Immigration counter: The female official firmly instructed, 'Sir, you must promptly show that passport of yours to me!' Report what she instructed: The officer explained to the traveler that {{gap_1}} before crossing the international terminal boundary.
```

---

### QID 3694 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['an', 'elephants']`
- **Applied Answer**: `['an', 'elephants']`
- **Evaluator Metrics**: Jaccard = `0.1667`, Levenshtein = `0.2424`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
In the wildlife park: {{gap_1}} elephant ⇒ two {{gap_2}}
```

---

### QID 3917 (Historical Batch 1 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['often make mistakes']`
- **Applied Answer**: `['often make mistakes']`
- **Evaluator Metrics**: Jaccard = `0.0588`, Levenshtein = `0.2180`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
When practicing new piano pieces, you certainly make careless mistakes. With (often): As a beginner pianist, you {{gap_1}} until your fingers adapt.
```

---

### QID 4045 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['him']`
- **Applied Answer**: `['him']`
- **Evaluator Metrics**: Jaccard = `0.0476`, Levenshtein = `0.2778`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
Our new department manager is Mr. Harris. We invited {{gap_1}} to the company dinner.
```

---

### QID 4054 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['They', 'her']`
- **Applied Answer**: `['They', 'her']`
- **Evaluator Metrics**: Jaccard = `0.2308`, Levenshtein = `0.5323`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
Lisa and Mark visit their aunt every Sunday. ⇒ {{gap_1}} visit {{gap_2}} every Sunday.
```

---

### QID 4188 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['many']`
- **Applied Answer**: `['many']`
- **Evaluator Metrics**: Jaccard = `0.1481`, Levenshtein = `0.3434`, Shingles = `['two or three']`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
Because the bakery was nearly closed, we didn't find {{gap_1}} fresh croissants on display; perhaps two or three.
```

---

### QID 4214 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['noisier than']`
- **Applied Answer**: `['noisier than']`
- **Evaluator Metrics**: Jaccard = `0.1667`, Levenshtein = `0.3636`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
Our downtown cafeteria is {{gap_1}} (noisy) the quiet cafés near the university library.
```

---

### QID 4254 (Historical Batch 1 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['Are you going to visit', 'are going to have', 'is going to be', 'am going to find', 'are going to pay', "isn't going to be", 'is going to travel', 'are going to fly', 'are going to go', "aren't going to come"]`
- **Applied Answer**: `['Are you going to visit', 'are going to have', 'is going to be', 'am going to find', 'are going to pay', "isn't going to be", 'is going to travel', 'are going to fly', 'are going to go', "aren't going to come"]`
- **Evaluator Metrics**: Jaccard = `0.0862`, Levenshtein = `0.3409`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018B: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
Hello Marcus, {{gap_1}} (you/visit) our research laboratory this October? Soon we {{gap_2}} (have) an open exhibition. The event {{gap_3}} (be) delightful for university students. Because our team needs technical assistance, I {{gap_4}} (find) a skilled web programmer. Department sponsors {{gap_5}} (pay) for equipment rentals. Doctor Hayes {{gap_6}} (not be) present throughout Friday since he {{gap_7}} (travel) abroad for medical conferences. The keynote speakers stated they {{gap_8}} (fly) directly into Edinburgh; subsequently they {{gap_9}} (go) toward Aberdeen by ferry. Regrettably, two invited panelists {{gap_10}} (not come) due to scheduling conflicts. Warm regards, Oliver
```

---

### QID 4501 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['are you leaving', "'m taking", "'m going to buy"]`
- **Applied Answer**: `['are you leaving', "'m taking", "'m going to buy"]`
- **Evaluator Metrics**: Jaccard = `0.1321`, Levenshtein = `0.3067`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
MARK: At what hour 1 {{gap_1}} for the design conference tomorrow? NICOLE: At dawn. I 2 {{gap_2}} the early airport express shuttle. MARK: And what about the demonstration equipment? NICOLE: I haven't selected any hardware yet, but I 3 {{gap_3}} portable displays this afternoon.
```

---

### QID 4852 (Batch 4 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['’m calling', 'happened', 'needed', 'went', 'was taking', 'noticed', 'opened', 'Are you joking', 'is he going to do', 'doesn’t know', 'will go', 'is going to give', 'will reclaim', '’ll tell', 'were you doing', 'was cleaning', 'Are you doing', 'went', 'was still going out', '’ll pick']`
- **Applied Answer**: `['’m calling', 'happened', 'needed', 'went', 'was taking', 'noticed', 'opened', 'Are you joking', 'is he going to do', 'doesn’t know', 'will go', 'is going to give', 'will reclaim', '’ll tell', 'were you doing', 'was cleaning', 'Are you doing', 'went', 'was still going out', '’ll pick']`
- **Evaluator Metrics**: Jaccard = `0.1815`, Levenshtein = `0.3191`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018B: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
MIRANDA: Central Archives department?
JULIAN: Good afternoon, Miranda. Glad I reached your line.
MIRANDA: Hello Julian! Is everything orderly today?
JULIAN: Mostly, though I 1 {{gap_1}} to discuss a surprising development concerning Marcus. Can you guess what 2 {{gap_2}} during his cataloging shift earlier?
MIRANDA: I have no idea; what occurred?
JULIAN: Apparently, the curator 3 {{gap_3}} archived manuscript blueprints; consequently Marcus 4 {{gap_4}} down toward basement storage vaults. While he 5 {{gap_5}} historic parchment folios from shelving racks, he 6 {{gap_6}} a forgotten leather briefcase tucked behind storage cabinets. When staff 7 {{gap_7}} the fasteners, ancient golden coins tumbled across the desk!
MIRANDA: Incredible! 8 {{gap_8}}?
JULIAN: Completely serious; security guards logged the discovery.
MIRANDA: And what 9 {{gap_9}} with such rare antiquities?
JULIAN: Marcus 10 {{gap_10}} yet. However, museum administrators suspect academic historians 11 {{gap_11}} into deep provenance verification soon.
MIRANDA: And afterward?
JULIAN: He confirmed the director 12 {{gap_12}} full custody to national heritage conservators.
MIRANDA: Perhaps smugglers left the case decades ago!
JULIAN: If true, nobody legitimate 13 {{gap_13}} ownership.
MIRANDA: Should that happen, we 14 {{gap_14}} Marcus that our restoration team deserves an extravagant celebration dinner!
JULIAN: Agreed! Switching subjects: what activity 15 {{gap_15}} prior to this phone call?
MIRANDA: I 16 {{gap_16}} microscope lenses in the laboratory.
JULIAN: 17 {{gap_17}} anything urgent once laboratory sanitization finishes?
MIRANDA: Nothing urgent. Shall we grab artisanal coffee across the square?
JULIAN: Splendid idea! The previous occasion I 18 {{gap_18}} for roasted espresso, I 19 {{gap_19}} with Brenda.
MIRANDA: Wonderful. I 20 {{gap_20}} you outside the west rotunda in fifteen minutes.
JULIAN: Fantastic; see you shortly.
MIRANDA: Farewell!
```

---

### QID 5069 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["Let's go"]`
- **Applied Answer**: `["Let's go"]`
- **Evaluator Metrics**: Jaccard = `0.1053`, Levenshtein = `0.2571`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
The heavy rain has finally stopped. _____ for a walk in the botanical gardens.
```

---

### QID 5085 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["don't open"]`
- **Applied Answer**: `["don't open"]`
- **Evaluator Metrics**: Jaccard = `0.1364`, Levenshtein = `0.3300`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
EMMA: "I will open the balcony window." LIAM: "Please {{gap_1}} the window right now; the freezing wind is too strong."
```

---

### QID 5088 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["let's not talk"]`
- **Applied Answer**: `["let's not talk"]`
- **Evaluator Metrics**: Jaccard = `0.1000`, Levenshtein = `0.2626`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
CLARA: "Should we discuss office problems tonight?" DAN: "No, {{gap_1}} about office problems; let's enjoy our weekend."
```

---

### QID 5134 (Historical Batch 1 - TASK-018B)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['have']`
- **Applied Answer**: `['have']`
- **Evaluator Metrics**: Jaccard = `0.2500`, Levenshtein = `0.3176`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
Receptionist: Excuse me, sir, have you already got your boarding voucher? Passenger: Yes, I {{gap_1}}.
```

---

### QID 5142 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `["didn't have"]`
- **Applied Answer**: `["didn't have"]`
- **Evaluator Metrics**: Jaccard = `0.2500`, Levenshtein = `0.2571`, Shingles = `["hasn't got a"]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
In the remote mountain village, the doctor hasn't got a car. ⇒ In the remote mountain village, the doctor {{gap_1}} a car.
```

---

### QID 5144 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['Did she have']`
- **Applied Answer**: `['Did she have']`
- **Evaluator Metrics**: Jaccard = `0.1818`, Levenshtein = `0.1982`, Shingles = `[]`
- **AI / Teacher Review**: `NOT_REQUIRED` (N/A)

**Adapted Text Applied**:
```text
Before the long overseas journey, has she got travel insurance? ⇒ Before the long overseas journey, {{gap_1}} travel insurance?
```

---

### QID 5736 (Historical Batch 1 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['and']`
- **Applied Answer**: `['and']`
- **Evaluator Metrics**: Jaccard = `0.1429`, Levenshtein = `0.3385`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
The express train reaches Oxford at 6 p.m., _____ then we take a local bus.
```

---

### QID 7139 (Batch 4 - TASK-018)

- **Old Status**: `REJECTED` ⇒ **New Status**: `VALIDATED`
- **Source Answer**: `['has']`
- **Applied Answer**: `['has']`
- **Evaluator Metrics**: Jaccard = `0.0000`, Levenshtein = `0.2029`, Shingles = `[]`
- **AI / Teacher Review**: `APPROVED_BY_TEACHER` (Approved teacher-reviewed correction from TASK-018: syntactic heuristic warnings/similarity markers audited and validated.)

**Adapted Text Applied**:
```text
10 The senior architect {{gap_1}} extensive experience in sustainable urban design.
```

---

## 4. Isolation & Integrity Check Confirmations

- [x] **QIDs 5013–5017 Isolation**: Confirmed PENDING and unchanged (`{'5013': 'PENDING', '5014': 'PENDING', '5015': 'PENDING', '5016': 'PENDING', '5017': 'PENDING'}`).
- [x] **QID 6096 Isolation**: Confirmed VALIDATED and unchanged (`VALIDATED`).
- [x] **Batch 2 & 3 Records**: Confirmed unchanged.
- [x] **Staging Database Integrity**: Hash unchanged (`3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded`).
- [x] **Evaluator Code Integrity**: Logic and calibrated thresholds unchanged.
- [x] **SQLite Referential Integrity**: `adaptation.db` integrity = `[('ok',)]`, FK violations = `[]`.
- [x] **Preview Gate Validation**: `12 / 12 passed (0 blocked)`.
- [x] **Regression Test Suites**: Python = `PASSED`, Jest = `PASSED`.
