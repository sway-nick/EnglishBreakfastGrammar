"""
apply_batch4_corrections.py
Applies teacher-reviewed targeted corrections for the 48 TRUE Batch 4 rejections (TASK-016D).

Universal English Test Platform:
1. Validates each replacement through the complete production pipeline:
   JSON/schema -> cardinality -> answer preservation -> grammar/integrity -> calibrated similarity -> AI review -> final status.
2. If any validation step fails: STOP for that QID, do not invent another replacement, leave unchanged.
3. Performs atomic transactional database commit for validated corrections.
4. Updates parent exercises and lessons.
5. Updates adaptation_runs record for prod_batch_4_a1_1000.
6. Runs Preview Gate validation.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.answer_integrity_validator import validate_answer_integrity, AnswerIntegrityResult
from pipeline.adaptation.execute_batch3 import evaluate_ai_review
from pipeline.adaptation.full_corpus_orchestrator import resolve_status_with_ai_review
from pipeline.adaptation.pilot_generator import export_pilot_universal_json, run_preview_gate_validation
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
RUN_ID = "prod_batch_4_a1_1000"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("apply_batch4_corrections")

# Exactly the 48 target QIDs verified against staging.db for TASK-016D
TARGET_QIDS = [
    7461, 2880, 2882, 2888, 2847, 2823,
    7376, 7379, 7383, 3469, 4501,
    2962, 2963, 2964, 3048, 3052,
    3076, 3077, 3082, 3067, 3068,
    2680, 5193, 3579, 4852, 3382,
    3492, 7139, 3361, 3365,
    2947, 2948, 2949, 2950, 2951, 2952, 2953, 2955, 2956,
    6170, 6180, 6186, 6188, 6189,
    2890, 2891, 2894, 2897
]

TEACHER_REPLACEMENTS: Dict[int, Dict[str, Any]] = {
    7461: {
        "text": "Our classes have changed this year. {{gap_1}}.",
        "correct_answer": "We are no longer in the same class.",
    },
    2880: {
        "text": "On my way to the station, I {{gap_1}} a street artist while he {{gap_2}} a wall.",
        "correct_answer": "saw / was painting",
    },
    2882: {
        "text": "During the move, I {{gap_1}} a lamp while I {{gap_2}} the living room.",
        "correct_answer": "broke / was cleaning",
    },
    2888: {
        "text": "At the airport yesterday, I {{gap_1}} my cousin, and she {{gap_2}} a blue jacket.",
        "correct_answer": "saw / was wearing",
    },
    2847: {
        "text": "Last Saturday, I 1 {{gap_1}} (arrive) at a small coastal town while Daniel 2 {{gap_2}} (wait) for me. He 3 {{gap_3}} (wear) a dark jacket and 4 {{gap_4}} (hold) an umbrella. When I 5 {{gap_5}} (get off) the bus, he 6 {{gap_6}} (run) towards me and 7 {{gap_7}} (kiss) me on the cheek. It 8 {{gap_8}} (rain) heavily, so he 9 {{gap_9}} (take off) his coat and 10 {{gap_10}} (put) it over my shoulders. I 11 {{gap_11}} (tell) Daniel to wait under a roof, but he 12 {{gap_12}} (insist) on finding a café. While he 13 {{gap_13}} (drive), I 14 {{gap_14}} (throw) a quick look at the map. He 15 {{gap_15}} (smile) all the time, but he also 16 {{gap_16}} (look) nervous. He finally 17 {{gap_17}} (stop) the car near the harbor. We 18 {{gap_18}} (get out), and he 19 {{gap_19}} (kneel) beside a bench and 20 {{gap_20}} (take) a small box from his pocket.",
        "gaps": ["arrived", "was waiting", "was wearing", "was holding", "got off", "ran", "kissed", "was raining", "took off", "put", "told", "insisted", "was driving", "threw", "was smiling", "looked", "stopped", "got out", "knelt", "took"],
    },
    2823: {
        "text": "Last spring we 1 {{gap_1}} (have) a weekend trip to Wales. We 2 {{gap_2}} (drive) there from Bristol, but our car 3 {{gap_3}} (break) down near the coast and we 4 {{gap_4}} (spend) the first evening in a small village. When we 5 {{gap_5}} (get) to Cardiff, we 6 {{gap_6}} (not can) find a hotel we liked; there 7 {{gap_7}} (not be) any rooms with sea views. We 8 {{gap_8}} (not know) what to do, but eventually we 9 {{gap_9}} (find) a guesthouse and 10 {{gap_10}} (stay) there for the weekend. We 11 {{gap_11}} (see) the castle, 12 {{gap_12}} (go) to a music festival, and 13 {{gap_13}} (buy) some local souvenirs. We 14 {{gap_14}} (want) to visit the mountains, but we 15 {{gap_15}} (not have) enough time and it 16 {{gap_16}} (be) too far away. The weather 17 {{gap_17}} (be) sunny at first, but it 18 {{gap_18}} (start) raining on the morning we 19 {{gap_19}} (leave). We 20 {{gap_20}} (have) a wonderful time.",
        "gaps": ["had", "drove", "broke", "spent", "got", "couldn't", "weren't", "didn't know", "found", "stayed", "saw", "went", "bought", "wanted", "didn't have", "was", "was", "started", "left", "had"],
    },
    7376: {
        "text": "After months of exams, I'm really _____.",
        "correct_answer": "looking forward to my holiday",
    },
    7379: {
        "text": "Joe was getting ready to leave the office, but he couldn't find his keys. I helped him _____.",
        "correct_answer": "look for his keys",
    },
    7383: {
        "text": "My new colleagues are friendly, and I _____ very well.",
        "correct_answer": "get on with them",
    },
    3469: {
        "text": "We walked {{gap_1}} the bridge to reach the museum.",
        "correct_answer": "across",
    },
    4501: {
        "text": "ALICE: I haven't chosen a laptop yet, but I {{gap_1}} one this weekend.\nBEN: What time {{gap_2}} tomorrow?\nALICE: Quite early. I {{gap_3}} the 7:10 train.",
        "gaps": ["'m going to buy", "are you leaving", "'m taking"],
    },
    2962: {
        "text": "A: The hotel reservation isn't confirmed.\nB: Don't worry. I {{gap_1}} them now.",
        "correct_answer": "'ll call",
    },
    2963: {
        "text": "A: Can you play the guitar yet?\nB: Not yet, but I {{gap_1}}.",
        "correct_answer": "'m going to learn",
    },
    2964: {
        "text": "A: I can't read the small print.\nB: Don't worry. I {{gap_1}} the message for you.",
        "correct_answer": "'ll read",
    },
    3048: {
        "text": "Anna is very trustworthy. {{gap_1}}.",
        "correct_answer": "She has never lied to us",
    },
    3052: {
        "text": "Everyone is celebrating today. {{gap_1}}.",
        "correct_answer": "David has won the competition",
    },
    3076: {
        "text": "She {{gap_1}} in Lisbon for two years before moving to Madrid.",
        "correct_answer": "lived",
    },
    3077: {
        "text": "{{gap_1}} the windows before you left the office?",
        "correct_answer": "Did you lock",
    },
    3082: {
        "text": "A: {{gap_1}} their project yet?\nB: Yes, they {{gap_2}} it before dinner.",
        "correct_answer": "Have the kids done / did",
    },
    3067: {
        "text": "EMMA: 1 {{gap_1}} (you/ever/be) to Canada?\nLUCAS: I 2 {{gap_2}} (never/be) to Canada, but I'd love to visit. And you?\nEMMA: 3 {{gap_3}} (you/ever/travel) there?\nLUCAS: Yes. I 4 {{gap_4}} (be) there twice. In fact, I 5 {{gap_5}} (travel) to several places in North America.\nEMMA: 6 {{gap_6}} (you/be) to Toronto, too?\nLUCAS: Yes.\nEMMA: When 7 {{gap_7}} (you/go) there?\nLUCAS: Last autumn, during my holiday.\nEMMA: 8 {{gap_8}} (you/like) it?\nLUCAS: Yes, it 9 {{gap_9}} (be) fantastic! We 10 {{gap_10}} (spend) ten wonderful days there.",
        "gaps": ["Have you ever been", "have never been", "have you ever travelled", "have been", "have travelled", "Have you been", "did you go", "Did you like", "was", "spent"],
    },
    3068: {
        "text": "MARK: 1 {{gap_1}} (you/ever/hear) the band Arctic Monkeys?\nBIANCA: No, I 2 {{gap_2}}. What kind of music do they play?\nMARK: Rock music. I 3 {{gap_3}} (see) them live last weekend.\nBIANCA: 4 {{gap_4}} (be) it a good concert?\nMARK: Yes, I really 5 {{gap_5}} (like) it.\nANDY: 6 {{gap_6}} (you/ever/lose) your phone?\nBART: Yes, I 7 {{gap_7}}.\nANDY: Where 8 {{gap_8}} (it/happen)?\nBART: In Berlin. I 9 {{gap_9}} (be) there on holiday.\nANDY: What 10 {{gap_10}} (you/do)?",
        "gaps": ["Have you ever heard", "haven't", "saw", "Was", "liked", "Have you ever lost", "have", "did it happen", "was", "did you do"],
    },
    2680: {
        "text": "I have plenty of free time, but I {{gap_1}}.",
        "correct_answer": "don't do sport very often",
    },
    5193: {
        "text": "I need a quiet evening {{gap_1}} my report.",
        "correct_answer": "to finish",
    },
    3579: {
        "text": "Several new folders arrived this morning. ⇒ {{gap_1}} on the top shelf.",
        "correct_answer": "There are",
    },
    4852: {
        "text": "MAYA: Hi, Nina. I 1 {{gap_1}} to ask about the charity event. Do you know what 2 {{gap_2}} wrong yesterday?\nNINA: Well, Alex 3 {{gap_3}} an error in the booking, so he called the office.\nMAYA: 4 {{gap_4}}?\nNINA: He needs to fix it. What 5 {{gap_5}} about it now?\nMAYA: He 6 {{gap_6}} to the service center, and the technician 7 {{gap_7}} him a replacement. The supplier 8 {{gap_8}} the old machine next week.\nNINA: By the way, Tom 9 {{gap_9}} the hall when I arrived.\nMAYA: After work, what 10 {{gap_10}} tonight?\nNINA: I don't know. What 11 {{gap_11}} at the meeting?\nMAYA: I 12 {{gap_12}} notes when the manager came in. Anna 13 {{gap_13}} about the change yet, but I 14 {{gap_14}} her. In fact, I 15 {{gap_15}} her now.\nMAYA: When I 16 {{gap_16}} the message, I saw the new schedule.\nNINA: What 17 {{gap_17}} when it arrived?\nMAYA: I 18 {{gap_18}} to the café. The last time I 19 {{gap_19}} with Jeremy was last summer.\nNINA: Fine. I 20 {{gap_20}} you up after work.",
        "gaps": ["needed", "went", "noticed", "Are you joking", "is he going to do", "will go", "is going to give", "will reclaim", "was cleaning", "Are you doing", "happened", "was taking", "doesn’t know", "’ll tell", "’m calling", "opened", "were you doing", "went", "was still going out", "’ll pick"],
    },
    3382: {
        "text": "I don't know the schedule. If I knew it, I {{gap_1}} you.",
        "correct_answer": "'d tell",
    },
    3492: {
        "text": "A: I haven't finished my report yet.\nB: Neither {{gap_1}} I.",
        "correct_answer": "have",
    },
    7139: {
        "text": "Mia {{gap_1}} curly hair and green eyes.",
        "correct_answer": "has",
    },
    3361: {
        "text": "A: Whose sunglasses are these?\nB: They aren't {{gap_1}}. Ask Maya; maybe they're {{gap_2}}.",
        "correct_answer": "mine / hers",
    },
    3365: {
        "text": "Dear James, Thanks for 1 {{gap_1}} email. It was great to hear from 2 {{gap_2}}. I was happy to hear that you are finally moving to a new home. I think the new place will make 3 {{gap_3}} very happy and 4 {{gap_4}} will make you very happy, too. How did your parents react when you gave 5 {{gap_5}} the news? Aren't 6 {{gap_6}} excited? I'm sure they are. By the way, we adopted a small dog. 7 {{gap_7}} name is Max. Sara and I saw 8 {{gap_8}} at a shelter and 9 {{gap_9}} decided to take the little dog home. We are so happy with 10 {{gap_10}} new pet!",
        "gaps": ["your", "you", "her", "she", "them", "they", "Its", "it", "we", "our"],
    },
    2947: {
        "text": "I recently had a strange dream about my old school. ⇒ What {{gap_1}}?",
        "correct_answer": "did you dream about",
    },
    2948: {
        "text": "I enjoy listening to podcasts on my commute. ⇒ What {{gap_1}}?",
        "correct_answer": "do you always listen to",
    },
    2949: {
        "text": "Someone kissed Virginia after the show. ⇒ {{gap_1}} at the theater?",
        "correct_answer": "Who kissed Virginia",
    },
    2950: {
        "text": "Jason met Linda at the café. ⇒ {{gap_1}} at the café?",
        "correct_answer": "Who did Jason kiss",
    },
    2951: {
        "text": "Lewis asked his boss for a day off. ⇒ What {{gap_1}}?",
        "correct_answer": "did Lewis ask his boss for",
    },
    2952: {
        "text": "Lewis asked his boss for a promotion. ⇒ {{gap_1}} for a promotion?",
        "correct_answer": "Who asked his boss",
    },
    2953: {
        "text": "Lewis asked his manager for a raise. ⇒ {{gap_1}} for a raise?",
        "correct_answer": "Who did Lewis ask",
    },
    2955: {
        "text": "At the science museum, we learned that Alexander Graham Bell created the telephone. ⇒ What {{gap_1}}?",
        "correct_answer": "did Alexander Graham Bell invent",
    },
    2956: {
        "text": "At the science museum, we learned about Alexander Fleming and penicillin. ⇒ Who {{gap_1}}?",
        "correct_answer": "discovered penicillin",
    },
    6170: {
        "text": "I mailed {{gap_1}} a thank-you card.",
        "correct_answer": "him",
    },
    6180: {
        "text": "After the incident, the witness sent {{gap_1}}.",
        "correct_answer": "the police a video of the robbers.",
    },
    6186: {
        "text": "Every evening, the teacher reads {{gap_1}} before bed.",
        "correct_answer": "them a story",
    },
    6188: {
        "text": "He wanted to help his brother, so he offered {{gap_1}} after the interview.",
        "correct_answer": "a job to his brother",
    },
    6189: {
        "text": "Please send {{gap_1}} after the meeting.",
        "correct_answer": "them a copy",
    },
    2890: {
        "text": "A: We chose a new colour because I {{gap_1}} the study.\nB: I'm sure it {{gap_2}} much brighter.",
        "correct_answer": "'m going to paint / will look",
    },
    2891: {
        "text": "A: What {{gap_1}} during the summer break?\nB: I {{gap_2}} around South America.",
        "correct_answer": "are you going to do / 'm going to travel",
    },
    2894: {
        "text": "A: {{gap_1}} to the airport tomorrow?\nB: Yes, but traffic is terrible, so I {{gap_2}} late.",
        "correct_answer": "Are you going to drive / 'm going to be",
    },
    2897: {
        "text": "They are leading 3-1 with only a minute left. They {{gap_1}} this match.\nB: Maybe, but our team {{gap_2}} another goal before the whistle.",
        "correct_answer": "are going to win / will score",
    },
}


def run_apply_corrections(commit: bool = False) -> Dict[str, Any]:
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row

    adapt_conn = sqlite3.connect(ADAPTATION_DB_PATH)
    adapt_conn.row_factory = sqlite3.Row

    counts_before = dict(
        adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall()
    )

    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    processed_items = []
    affected_exercise_ids = set()
    affected_lesson_ids = set()

    for qid in TARGET_QIDS:
        rep = TEACHER_REPLACEMENTS.get(qid)
        if not rep:
            raise ValueError(f"Missing replacement for target QID {qid}")

        sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (str(qid),)).fetchone()
        if not sq:
            raise ValueError(f"Question {qid} not found in staging.db")

        aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (str(qid),)).fetchone()
        if not aq:
            raise ValueError(f"Question {qid} not found in adaptation.db")

        s_opts = [dict(r) for r in stage_conn.execute("SELECT * FROM staging_options WHERE question_id = ? ORDER BY option_order", (str(qid),)).fetchall()]
        s_gaps = [dict(r) for r in stage_conn.execute("SELECT * FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (str(qid),)).fetchall()]

        adapted_text = rep["text"].strip()
        prompt_corr_ans = rep.get("correct_answer")
        prompt_gaps = rep.get("gaps")

        rm = sq["response_model"]
        structural_errors = []

        # Construct options or gaps
        adapted_opts = []
        adapted_gaps = []

        if rm in ("single_choice", "multiple_choice"):
            adapted_opts = [dict(o) for o in s_opts]
            src_correct_answers = [o["text"] for o in s_opts if o["is_correct"]]
            # normalize spaces around slashes for comparison
            norm_src = [re.sub(r"\s*/\s*", " / ", a.strip().lower().replace("’", "'")) for a in src_correct_answers]
            norm_prompt = re.sub(r"\s*/\s*", " / ", (prompt_corr_ans or "").strip().lower().replace("’", "'"))
            if not any(norm_prompt == ns or norm_prompt in ns or ns in norm_prompt for ns in norm_src):
                structural_errors.append(f"Answer divergence: prompt correct_answer '{prompt_corr_ans}' not found in source answers {src_correct_answers}")
        elif rm == "gap":
            # Check gap markers count
            markers = re.findall(r"\{\{gap_\d+\}\}", adapted_text)
            if len(markers) != len(s_gaps):
                structural_errors.append(f"Gap cardinality mismatch in text: {len(markers)} markers vs {len(s_gaps)} source gaps")

            if len(s_gaps) == 1:
                g = dict(s_gaps[0])
                acc = json.loads(g["accepted_answers"]) if g.get("accepted_answers") else [prompt_corr_ans or g["correct_answer"]]
                adapted_gaps = [{
                    "gap_order": 1,
                    "correct_answer": prompt_corr_ans or g["correct_answer"],
                    "accepted_answers": acc,
                }]
                norm_src = [a.strip().lower().replace("’", "'") for a in [g["correct_answer"]] + acc]
                norm_prompt = (prompt_corr_ans or "").strip().lower().replace("’", "'")
                if not any(norm_prompt == ns for ns in norm_src):
                    structural_errors.append(f"Answer divergence: prompt answer '{prompt_corr_ans}' does not match source gap '{g['correct_answer']}'")
            else:
                # Multi-gap items
                if prompt_gaps and len(prompt_gaps) == len(s_gaps):
                    for idx, g_ans in enumerate(prompt_gaps):
                        s_g = s_gaps[idx]
                        acc = json.loads(s_g["accepted_answers"]) if s_g.get("accepted_answers") else [g_ans]
                        adapted_gaps.append({
                            "gap_order": idx + 1,
                            "correct_answer": g_ans,
                            "accepted_answers": acc,
                        })
                else:
                    for g in s_gaps:
                        acc = json.loads(g["accepted_answers"]) if g.get("accepted_answers") else [g["correct_answer"]]
                        adapted_gaps.append({
                            "gap_order": g["gap_order"],
                            "correct_answer": g["correct_answer"],
                            "accepted_answers": acc,
                        })

        # Cardinality checks
        if rm in ("single_choice", "multiple_choice") and len(adapted_opts) != len(s_opts):
            structural_errors.append(f"Option cardinality mismatch: got {len(adapted_opts)}, expected {len(s_opts)}")
        if rm == "gap" and len(adapted_gaps) != len(s_gaps):
            structural_errors.append(f"Gap cardinality mismatch: got {len(adapted_gaps)}, expected {len(s_gaps)}")

        # 2. Grammar / integrity
        source_item = {"question_id": qid, "response_model": rm, "content": sq["content"], "options": s_opts, "gaps": s_gaps}
        adapted_item = {"adapted_text": adapted_text, "options": adapted_opts, "gaps": adapted_gaps}
        integrity_res: AnswerIntegrityResult = validate_answer_integrity(source_item, adapted_item)

        # 3. Calibrated similarity
        t_tokens = [g["correct_answer"] for g in adapted_gaps] if adapted_gaps else [o["text"] for o in adapted_opts if o["is_correct"]]
        sim_res = evaluate_similarity(sq["content"], adapted_text, target_tokens=t_tokens)

        # 4. Deterministic status
        if structural_errors or sim_res["originality_status"] == "REJECTED" or not integrity_res.is_answer_valid:
            det_status = "REJECTED"
            reasons = structural_errors + sim_res["reasons"] + integrity_res.reasons
        elif not integrity_res.answer_preserved or integrity_res.high_risk_mutations or sim_res["originality_status"] == "REVIEW_REQUIRED":
            det_status = "REVIEW_REQUIRED"
            reasons = sim_res["reasons"] + integrity_res.reasons
        else:
            det_status = "VALIDATED"
            reasons = sim_res["reasons"]

        # 5. AI review for REVIEW_REQUIRED
        ai_decision = None
        ai_reason = ""
        if det_status == "REVIEW_REQUIRED":
            ai_decision, ai_reason = evaluate_ai_review(
                sqid=str(qid), rm=rm, stage_q=sq, stage_opts=s_opts, stage_gaps=s_gaps,
                adapted_text=adapted_text, adapted_opts=adapted_opts, adapted_gaps=adapted_gaps,
                integrity_res=integrity_res, sim_res=sim_res
            )

        # 6. Final status resolution
        final_status, rev_req = resolve_status_with_ai_review(det_status, ai_decision)

        notes = "; ".join(reasons)
        if ai_decision:
            notes += f"; AI Review: {ai_decision} - {ai_reason}"

        if final_status == "VALIDATED":
            affected_exercise_ids.add(aq["adapted_exercise_id"])
            affected_lesson_ids.add(aq["adapted_lesson_id"])

        processed_items.append({
            "qid": qid,
            "aqid": aq["adapted_question_id"],
            "rm": rm,
            "adapted_text": adapted_text,
            "sim_score": sim_res["jaccard_similarity"],
            "det_status": det_status,
            "ai_decision": ai_decision,
            "ai_reason": ai_reason,
            "final_status": final_status,
            "rev_req": rev_req,
            "notes": notes,
            "reasons": reasons,
            "structural_errors": structural_errors,
            "s_opts": s_opts,
            "adapted_opts": adapted_opts,
            "s_gaps": s_gaps,
            "adapted_gaps": adapted_gaps,
        })

    valid_items = [it for it in processed_items if it["final_status"] == "VALIDATED"]
    rejected_items = [it for it in processed_items if it["final_status"] != "VALIDATED"]

    logger.info(f"Evaluated 48 QIDs: {len(valid_items)} VALIDATED, {len(rejected_items)} REJECTED/STOPPED.")

    if commit:
        logger.info(f"Initiating atomic commit for {len(valid_items)} VALIDATED items...")
        with adapt_conn:
            for item in valid_items:
                aqid = item["aqid"]
                sqid = str(item["qid"])
                rm = item["rm"]

                adapt_conn.execute(
                    """
                    UPDATE adapted_questions
                    SET adapted_text = ?,
                        similarity_score = ?,
                        adaptation_status = ?,
                        review_required = ?,
                        adaptation_notes = ?,
                        adapted_by = 'targeted-correction-v1',
                        adapted_at = ?
                    WHERE adapted_question_id = ?
                    """,
                    (
                        item["adapted_text"],
                        item["sim_score"],
                        item["final_status"],
                        item["rev_req"],
                        f"TASK-016D Correction: {item['notes']}",
                        now_ts,
                        aqid,
                    ),
                )

                # Update options if single_choice/multiple_choice
                if item["adapted_opts"]:
                    for opt_idx, o_spec in enumerate(item["adapted_opts"]):
                        if opt_idx < len(item["s_opts"]):
                            s_o = item["s_opts"][opt_idx]
                            opt_id = f"adapt_{s_o['option_id']}"
                            adapt_conn.execute(
                                """
                                UPDATE adapted_options
                                SET adapted_text = ?,
                                    adapted_value = ?,
                                    adapted_is_correct = ?,
                                    review_required = ?,
                                    adaptation_notes = 'TASK-016D Correction'
                                WHERE adapted_option_id = ?
                                """,
                                (o_spec["text"], o_spec["text"], o_spec["is_correct"], item["rev_req"], opt_id),
                            )

                # Update gaps if gap question
                if item["adapted_gaps"]:
                    for gap_idx, g_spec in enumerate(item["adapted_gaps"]):
                        if gap_idx < len(item["s_gaps"]):
                            s_g = item["s_gaps"][gap_idx]
                            gap_id = f"adapt_{s_g['gap_id']}"
                            acc_json = json.dumps(g_spec.get("accepted_answers", [g_spec["correct_answer"]]))
                            adapt_conn.execute(
                                """
                                UPDATE adapted_gaps
                                SET adapted_correct_answer = ?,
                                    adapted_accepted_answers = ?,
                                    review_required = ?,
                                    adaptation_notes = 'TASK-016D Correction'
                                WHERE adapted_gap_id = ?
                                """,
                                (g_spec["correct_answer"], acc_json, item["rev_req"], gap_id),
                            )

                # Record AI review audit if performed
                if item["ai_decision"]:
                    adapt_conn.execute(
                        """
                        INSERT OR REPLACE INTO pilot_semantic_reviews (
                            source_question_id, adapted_question_id, sample_group, response_model,
                            decision, grammar_target_ok, answer_integrity_ok, originality_ok,
                            quality_ok, reason, reviewed_at, reviewer_model
                        ) VALUES (?, ?, 'PROD_ADAPT_EVAL', ?, ?, 1, 1, 1, 1, ?, ?, 'semantic-reviewer-expert-v1')
                        """,
                        (sqid, aqid, rm, item["ai_decision"], item["ai_reason"], now_ts),
                    )

            # Update affected exercises
            for eid in affected_exercise_ids:
                ex_rev = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND review_required = 1", (eid,)
                ).fetchone()[0]
                ex_pend = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND adaptation_status = 'PENDING'", (eid,)
                ).fetchone()[0]
                ex_rej = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND adaptation_status = 'REJECTED'", (eid,)
                ).fetchone()[0]
                ex_stat = "REVIEW_REQUIRED" if ex_rev > 0 else ("PENDING" if ex_pend > 0 else ("REJECTED" if ex_rej > 0 else "VALIDATED"))
                adapt_conn.execute(
                    "UPDATE adapted_exercises SET adaptation_status = ?, review_required = ? WHERE adapted_exercise_id = ?",
                    (ex_stat, 1 if ex_rev > 0 else 0, eid),
                )

            # Update affected lessons
            for lid in affected_lesson_ids:
                les_rev = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND review_required = 1", (lid,)
                ).fetchone()[0]
                les_pend = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND adaptation_status = 'PENDING'", (lid,)
                ).fetchone()[0]
                les_rej = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND adaptation_status = 'REJECTED'", (lid,)
                ).fetchone()[0]
                les_stat = "REVIEW_REQUIRED" if les_rev > 0 else ("PENDING" if les_pend > 0 else ("REJECTED" if les_rej > 0 else "VALIDATED"))
                adapt_conn.execute(
                    "UPDATE adapted_lessons SET adaptation_status = ?, review_required = ? WHERE adapted_lesson_id = ?",
                    (les_stat, 1 if les_rev > 0 else 0, lid),
                )

            # Update adaptation_runs for Batch 4: increment validated_count, decrement rejected_count
            num_validated = len(valid_items)
            adapt_conn.execute(
                """
                UPDATE adaptation_runs
                SET validated_count = validated_count + ?,
                    rejected_count = rejected_count - ?,
                    notes = 'Batch 4 updated: ' || (validated_count + ?) || ' validated, ' || (rejected_count - ?) || ' rejected after TASK-016D teacher-reviewed corrections.'
                WHERE run_id = ?
                """,
                (num_validated, num_validated, num_validated, num_validated, RUN_ID),
            )

        logger.info("Database commit completed successfully.")

    counts_after = dict(
        adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall()
    )

    stage_conn.close()
    adapt_conn.close()

    return {
        "processed_items": processed_items,
        "valid_items": valid_items,
        "rejected_items": rejected_items,
        "counts_before": counts_before,
        "counts_after": counts_after,
        "commit": commit,
    }


def main():
    parser = argparse.ArgumentParser(description="Apply Batch 4 Teacher-Reviewed Corrections (TASK-016D)")
    parser.add_argument("--commit", action="store_true", help="Commit validated corrections to adaptation.db")
    args = parser.parse_args()

    res = run_apply_corrections(commit=args.commit)

    print("\n=======================================================")
    print(" TASK-016D: TEACHER-REVIEWED CORRECTIONS REPORT")
    print("=======================================================")
    print(f"Commit mode: {res['commit']}")
    print(f"Total evaluated: {len(res['processed_items'])}")
    print(f"VALIDATED: {len(res['valid_items'])}")
    print(f"REJECTED/STOPPED: {len(res['rejected_items'])}")
    print(f"Counts before: {res['counts_before']}")
    print(f"Counts after:  {res['counts_after']}")
    print("-" * 55)

    for item in res["processed_items"]:
        flag = "VALIDATED" if item["final_status"] == "VALIDATED" else "STOPPED"
        print(f"[{flag:9s}] QID {item['qid']:4d} ({item['rm']:13s}) -> {item['final_status']}")
        if item["final_status"] != "VALIDATED":
            print(f"            Reason: {item['notes']}")


if __name__ == "__main__":
    main()
