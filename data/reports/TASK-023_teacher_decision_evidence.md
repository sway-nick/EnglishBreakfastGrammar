# TASK-023 — Exact Teacher-Decision Evidence Package

**Timestamp**: 2026-10-01T12:02:18.138653+00:00  
**Purpose**: Machine-grounded evidence for 5 unresolved teacher-decision candidates.  
**Source of Truth**: [`TASK-023_teacher_decision_evidence.json`](file:///c:/projects/English%20Breakfast%20Grammar/data/reports/TASK-023_teacher_decision_evidence.json)  
**Reused Verifications**: Global audit, Preview Gate (225/225 PASS), Staging hash, and test suites reused from TASK-020/022.  

---

## Summary Table

| QID | Level | Exercise | Response Model | Issue Category | Conflicting QID / Context | Proposed Action |
| :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **3068** | A2 | `quiz-358` | `gap` (10 gaps) | Copular agreement | Gap 4: *Was auditorium acoustics* | Replace head noun *acoustics* with singular *sound quality* |
| **5054** | A1 | `quiz-591` | `gap` (1 gap) | Carrier duplicate | Collided with QID 5038 (*cat hiding behind sofa*) | Replaced with person queue context (*ticket queue*) |
| **5165** | A1 | `quiz-602` | `single_choice` | Carrier duplicate | Collided with QID 5160 (*listening to music*) | Replaced with afternoon reading context (*reading novels*) |
| **7513** | A2 | `quiz-882` | `gap` (1 gap) | Carrier duplicate | Collided with QID 7493 (*catch last train*) | Replaced with laptop repair context (*online presentation*) |
| **6742** | B1 | `quiz-782` | `single_choice` | Carrier duplicate | Collided with QID 6739 (*hike national park*) | Replaced with Alpine tunnel context (*50-kilometre tunnel*) |

---

## Exact Evidence by Candidate

### QID 3068 (SEMANTIC_COPULAR_AGREEMENT)
- **Level**: `A2` | **Topic**: `Present perfect or past simple?` | **Exercise**: `quiz-362` (Exercise 4)
- **Response Model**: `gap` | **Gaps**: `10` | **Options**: `0`
- **Source Text**:
  > Dialogue 1 MARK: 1 {{gap_1}} (you/ever/hear) the group The Darkness? BIANCA: No, I 2 {{gap_2}}. What kind of music do they play? MARK: Rock music. I 3 {{gap_3}} (see) them in concert last night. BIANCA: 4 {{gap_4}} (be) it a good concert? MARK: Yes, I really 5 {{gap_5}} (like) it. Dialogue 2 ANDY: 6 {{gap_6}} (you/ever/lose) your car keys? BART: Yes, I 7 {{gap_7}}. ANDY: Where 8 {{gap_8}} (it/happen)? BART: In Portugal. I 9 {{gap_9}} (be) there on holiday. ANDY: What 10 {{gap_10}} (you/do)?
- **Source Answer(s)**: `['Have you ever heard', "haven't", 'saw', 'Was', 'liked', 'Have you ever lost', 'have', 'did it happen', 'was', 'did you do']`
- **Original Problematic Sentence**: `TARA: 4 {{gap_4}} (be) the auditorium acoustics satisfactory?`
- **Validator Flag**: `Plural/compound subject conflicts with singular verb form 'Was'.`
- **Candidate Sentence**: `TARA: 4 {{gap_4}} (be) the auditorium sound quality satisfactory?`
- **Target Answer**: `Was` (Target answer preserved)
- **Teacher Rationale**:
  In standard English, 'acoustics' (acoustic properties of a hall) functions as a plural noun requiring 'Were'. Changing the head noun to the singular compound 'auditorium sound quality' makes the target answer 'Was' ('Was the auditorium sound quality satisfactory?') grammatically flawless, natural, and unambiguous, without altering the target answer key or any other gap.

---

### QID 5054 (SUSPICIOUS_DUPLICATE_CROSS_EXERCISE)
- **Level**: `A1` | **Topic**: `Next to, under, between, in front of, behind, over, etc.` | **Exercise**: `quiz-591` (Exercise 3)
- **Response Model**: `gap` | **Gaps**: `1` | **Options**: `0`
- **Source Text**:
  > 5 Martha is standing {{gap_1}} David (4).
- **Source Answer(s)**: `['behind']`
- **Duplicated Carrier Text**: `The cat is hiding {{gap_1}} the sofa.`
- **Conflicting QID**: `5038` in `quiz-589`
- **Conflicting Carrier**: `The cat is hiding {{gap_1}} the sofa.`
- **Proposed Candidate Text**:
  > Sophie is standing {{gap_1}} Liam in the ticket queue.
- **Candidate Answer**: `behind` (Preserved)
- **Teacher Rationale**:
  Source prompt features people standing in sequence ('Martha standing behind David'). New carrier uses person queue context, breaking carrier collision with cat/sofa in quiz-589 while matching A1 preposition pedagogy.

---

### QID 5165 (GENUINE_DUPLICATE_SAME_EXERCISE)
- **Level**: `A1` | **Topic**: `Would you like...? I'd like...` | **Exercise**: `quiz-602` (Exercise 2)
- **Response Model**: `single_choice` | **Gaps**: `0` | **Options**: `3`
- **Source Text**:
  > 7 We _____ watching TV during dinner.
- **Source Answer(s)**: `['like']`
- **Duplicated Carrier Text**: `They _____ listening to music in the evening.`
- **Conflicting QID**: `5160` in `quiz-602`
- **Conflicting Carrier**: `They _____ listening to music in the evening.`
- **Proposed Candidate Text**:
  > We _____ reading novels in the park on sunny afternoons.
- **Candidate Answer**: `like` (Preserved)
- **Candidate Options**: `["'d like", 'like', "'d like to"]`
- **Teacher Rationale**:
  Both questions occur in quiz-602. Replaced question 7 receives a fresh gerund complement context ('reading novels in the park') testing habitual preference ('like' + -ing), preserving exact options and answer.

---

### QID 7513 (SUSPICIOUS_DUPLICATE_CROSS_EXERCISE)
- **Level**: `A2` | **Topic**: `On time vs In time, At the end vs In the end` | **Exercise**: `quiz-882` (Exercise 3)
- **Response Model**: `gap` | **Gaps**: `1` | **Options**: `0`
- **Source Text**:
  > 8 The pie will be ready {{gap_1}} for dinner.
- **Source Answer(s)**: `['in time']`
- **Duplicated Carrier Text**: `We arrived at the station {{gap_1}} to catch the last train.`
- **Conflicting QID**: `7493` in `quiz-880`
- **Conflicting Carrier**: `We arrived at the station {{gap_1}} to catch the last train.`
- **Proposed Candidate Text**:
  > The technician finished repairing the laptop {{gap_1}} for my online presentation.
- **Candidate Answer**: `in time` (Preserved)
- **Teacher Rationale**:
  Source prompt tests 'in time for [event/deadline]'. New carrier ('finished repairing the laptop in time for my online presentation') avoids train-station duplicate while preserving exact grammar usage.

---

### QID 6742 (GENUINE_DUPLICATE_SAME_EXERCISE)
- **Level**: `B1` | **Topic**: `Compound adjectives with numbers: 'a two-day trip'` | **Exercise**: `quiz-782` (Exercise 1)
- **Response Model**: `single_choice` | **Gaps**: `0` | **Options**: `3`
- **Source Text**:
  > 9 The Channel Tunnel is a _____ tunnel that connects England with France.
- **Source Answer(s)**: `['50-kilometre']`
- **Duplicated Carrier Text**: `They completed a _____ hike through the national park.`
- **Conflicting QID**: `6739` in `quiz-782`
- **Conflicting Carrier**: `They completed a _____ hike through the national park.`
- **Proposed Candidate Text**:
  > Engineers constructed a _____ tunnel beneath the Alpine ridge.
- **Candidate Answer**: `50-kilometre` (Preserved)
- **Candidate Options**: `['50-kilometre', '50-kilometres', '50 kilometres']`
- **Teacher Rationale**:
  Both items exist in quiz-782. Retained item tests '10-mile hike'; replaced item tests '50-kilometre tunnel beneath the Alpine ridge'. Breaks intra-exercise collision cleanly while preserving options and answer.

---

## Teacher Decision Boundary
No database modifications, regenerations, or pedagogical determinations were performed. Ready for English teacher / supervisor decision.
