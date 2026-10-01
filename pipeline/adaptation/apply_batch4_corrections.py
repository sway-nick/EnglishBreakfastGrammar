"""
apply_batch4_corrections.py
Applies prepared targeted corrections for the TRUE Batch 4 rejections (TASK-016B-FINAL).

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

# Prepared replacements for all 55 true Batch 4 rejections as specified in TASK-016B-FINAL
PREPARED_REPLACEMENTS: Dict[int, Dict[str, Any]] = {
    2861: {
        "text": "The children can start the game _____ their coach gives permission.",
        "correct_answer": "as soon as",
    },
    3249: {
        "text": "Some students avoid _____ chess after midnight.",
        "correct_answer": "playing",
    },
    3253: {
        "text": "The children have a free afternoon. What would they like _____ together?",
        "correct_answer": "to do",
    },
    5008: {
        "text": "Take a bottle of water on the hike.",
        "correct_answer": "You might get dehydrated.",
    },
    5010: {
        "text": "We haven't cooked anything for dinner.",
        "correct_answer": "There is a new restaurant we want to try.",
    },
    5011: {
        "text": "Sally hasn't arrived at the office yet.",
        "correct_answer": "She might be stuck in traffic.",
    },
    5012: {
        "text": "I'm exhausted after the long day.",
        "correct_answer": "I might not go to the party tonight.",
    },
    7461: {
        "text": "A: Look at that painting. B: Yes, it {{gap_1}} beautiful. (look)",
        "correct_answer": "looks",
    },
    2880: {
        "text": "When I called, the children _____ drums in the next room.",
        "correct_answer": "were playing",
    },
    2882: {
        "text": "She missed a step and _____ down the stairs.",
        "correct_answer": "fell",
    },
    2888: {
        "text": "At the moment I opened the curtains, it _____ outside.",
        "correct_answer": "was raining",
    },
    2847: {
        "text": "At the crowded station, I lost sight of my friends. Did you see {{gap_1}} near the ticket office? (anyone / someone)",
        "correct_answer": "anyone",
    },
    2823: {
        "text": "After the concert, I couldn't find my sister. Did you see {{gap_1}} near the exit? (anyone / someone)",
        "correct_answer": "anyone",
    },
    7376: {
        "text": "A: What does the new coach look like? B: He _____.",
        "correct_answer": "is tall and thin",
    },
    7379: {
        "text": "A: What is the new head teacher like? B: She _____.",
        "correct_answer": "is very strict",
    },
    7383: {
        "text": "A: What does your cousin look like? B: He _____.",
        "correct_answer": "looks like our father",
    },
    3469: {
        "text": "Those fresh strawberries {{gap_1}} sweet. (smell)",
        "correct_answer": "smell",
    },
    4501: {
        "text": "Your work schedule for next week is not clear. ⇒ {{gap_1}} next week?",
        "correct_answer": "Where are you working",
    },
    2962: {
        "text": "The new house _____ five bedrooms.",
        "correct_answer": "has got",
    },
    2963: {
        "text": "I _____ a sore throat today.",
        "correct_answer": "have",
    },
    2964: {
        "text": "We _____ lunch right now.",
        "correct_answer": "are having",
    },
    3048: {
        "text": "Our department was under pressure, but it {{gap_1}} several urgent requests. (have)",
        "correct_answer": "had",
    },
    3052: {
        "text": "I called you earlier but missed you. ⇒ {{gap_1}} earlier?",
        "correct_answer": "Where were you",
    },
    3076: {
        "text": "My cousin often _____ to podcasts while cooking.",
        "correct_answer": "listens",
    },
    3077: {
        "text": "Look! The child _____.",
        "correct_answer": "is smiling",
    },
    3082: {
        "text": "My sister is at home today. She _____ at the office.",
        "correct_answer": "isn't working",
    },
    3067: {
        "text": "I prefer tea before breakfast. ⇒ I {{gap_1}} tea before breakfast. (drink)",
        "correct_answer": "drink",
    },
    3068: {
        "text": "Look at Tom during lunch. He is having soup. ⇒ He {{gap_1}} soup. (eat)",
        "correct_answer": "is eating",
    },
    2680: {
        "text": "For the morning commute, which bus _____ to the airport?",
        "correct_answer": "goes",
    },
    5193: {
        "text": "We have fresh juice ready for lunch. Would you like _____ juice?",
        "correct_answer": "some",
    },
    3579: {
        "text": "A few new folders arrived this morning. ⇒ {{gap_1}} folders on the shelf.",
        "correct_answer": "There are",
    },
    4852: {
        "text": "We need more printer paper. ⇒ {{gap_1}} any in the supply room?",
        "correct_answer": "Is there",
    },
    3382: {
        "text": "The soup doesn't contain {{gap_1}} salt.",
        "correct_answer": "much",
    },
    3492: {
        "text": "Our classroom is short of storage space. ⇒ We {{gap_1}} enough shelves.",
        "correct_answer": "haven't got",
    },
    7139: {
        "text": "The boxes are ready for the move. ⇒ {{gap_1}} blue boxes near the door.",
        "correct_answer": "They are",
    },
    3361: {
        "text": "For tonight's event, how many chairs _____ in the hall?",
        "correct_answer": "are there",
    },
    3365: {
        "text": "At the community meeting yesterday, there {{gap_1}} many empty seats. (not be)",
        "correct_answer": "weren't",
    },
    2947: {
        "text": "My sister _____ nature documentaries on weekends.",
        "correct_answer": "watches",
    },
    2948: {
        "text": "Local students _____ to the museum by bus.",
        "correct_answer": "go",
    },
    2949: {
        "text": "My brother _____ lunch at noon.",
        "correct_answer": "has",
    },
    2950: {
        "text": "The children _____ volleyball after school.",
        "correct_answer": "play",
    },
    2951: {
        "text": "Her aunt _____ at a pharmacy.",
        "correct_answer": "works",
    },
    2952: {
        "text": "I _____ understand German.",
        "correct_answer": "don't",
    },
    2953: {
        "text": "Where _____ your parents live?",
        "correct_answer": "do",
    },
    2955: {
        "text": "When _____ the lesson begin?",
        "correct_answer": "does",
    },
    2956: {
        "text": "How often _____ your cousins visit you?",
        "correct_answer": "do",
    },
    6170: {
        "text": "Look at these items in the suitcase. ⇒ {{gap_1}} travel bags.",
        "correct_answer": "These are",
    },
    6180: {
        "text": "I found one book on the desk. ⇒ This is {{gap_1}}.",
        "correct_answer": "my book",
    },
    6186: {
        "text": "That vehicle belongs to my brother. ⇒ That is {{gap_1}}.",
        "correct_answer": "his car",
    },
    6188: {
        "text": "Several pens belong to the students. ⇒ These are {{gap_1}}.",
        "correct_answer": "their pens",
    },
    6189: {
        "text": "We left two coats by the door. ⇒ Those are {{gap_1}}.",
        "correct_answer": "our coats",
    },
    2890: {
        "text": "She _____ dinner when the doorbell rang.",
        "correct_answer": "was cooking",
    },
    2891: {
        "text": "The lights went out suddenly. What _____ when that happened?",
        "correct_answer": "were you doing",
    },
    2894: {
        "text": "While they _____ through Italy, they took many photos.",
        "correct_answer": "were travelling",
    },
    2897: {
        "text": "As she _____ toward the station, she saw a neighbor.",
        "correct_answer": "was walking",
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

    for qid, rep in sorted(PREPARED_REPLACEMENTS.items()):
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

        rm = sq["response_model"]
        structural_errors = []

        # 1. Answer preservation verification against source staging data
        src_correct_answers = [o["text"] for o in s_opts if o["is_correct"]] + [g["correct_answer"] for g in s_gaps]
        answer_preserved = (prompt_corr_ans in src_correct_answers)
        if not answer_preserved:
            structural_errors.append(f"Answer divergence: prompt correct_answer '{prompt_corr_ans}' not found in source answers {src_correct_answers}")

        # Construct options or gaps
        adapted_opts = []
        adapted_gaps = []

        if rm in ("single_choice", "multiple_choice"):
            adapted_opts = [dict(o) for o in s_opts]
            # Ensure blank exists in text only if source had a blank
            if ("_____" in sq["content"] or "{{gap_1}}" in sq["content"]) and ("_____" not in adapted_text and "{{gap_1}}" not in adapted_text):
                structural_errors.append("Missing blank placeholder in choice question text")
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
            "structural_errors": structural_errors,
            "s_opts": s_opts,
            "adapted_opts": adapted_opts,
            "s_gaps": s_gaps,
            "adapted_gaps": adapted_gaps,
        })

    valid_items = [it for it in processed_items if it["final_status"] == "VALIDATED"]
    rejected_items = [it for it in processed_items if it["final_status"] != "VALIDATED"]

    logger.info(f"Evaluated 55 QIDs: {len(valid_items)} VALIDATED, {len(rejected_items)} REJECTED/FAILED.")

    if commit:
        logger.info(f"Committing {len(valid_items)} validated corrections to adaptation.db...")
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
                        f"TASK-016B Correction: {item['notes']}",
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
                                    adaptation_notes = 'TASK-016B Correction'
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
                                    adaptation_notes = 'TASK-016B Correction'
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
                    notes = 'Batch 4 updated: ' || (validated_count + ?) || ' validated, ' || (rejected_count - ?) || ' rejected after TASK-016B targeted corrections.'
                WHERE run_id = ?
                """,
                (num_validated, num_validated, num_validated, num_validated, RUN_ID),
            )

    counts_after = dict(
        adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall()
    )

    stage_conn.close()
    adapt_conn.close()

    preview_gate_passed = False
    if commit:
        logger.info("Running Preview Gate validation...")
        temp_json = REPO_ROOT / "data" / "adaptation" / "temp_production_preview.json"
        export_pilot_universal_json(ADAPTATION_DB_PATH, temp_json, filter_by_adapted_by=False)
        gate_res = run_preview_gate_validation(temp_json)
        preview_gate_passed = (gate_res["gatePassed"] == gate_res["totalLessons"]) and (gate_res["validCount"] == gate_res["totalLessons"])
        if temp_json.exists():
            temp_json.unlink()

    return {
        "processed_items": processed_items,
        "valid_items": valid_items,
        "rejected_items": rejected_items,
        "counts_before": counts_before,
        "counts_after": counts_after,
        "preview_gate_passed": preview_gate_passed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply Batch 4 targeted corrections")
    parser.add_argument("--commit", action="store_true", help="Commit changes to database")
    args = parser.parse_args()

    res = run_apply_corrections(commit=args.commit)
    print("\n===============================")
    print("TASK-016B CORRECTIONS SUMMARY")
    print("===============================")
    print(f"Total evaluated: {len(res['processed_items'])}")
    print(f"VALIDATED: {len(res['valid_items'])}")
    print(f"FAILED/REJECTED: {len(res['rejected_items'])}")
    print("\n--- VALIDATED ITEMS ---")
    for it in res["valid_items"]:
        print(f"QID {it['qid']}: {it['det_status']} (AI={it['ai_decision']}) -> VALIDATED")
    print("\n--- FAILED/REJECTED ITEMS ---")
    for it in res["rejected_items"]:
        print(f"QID {it['qid']}: {it['det_status']} (AI={it['ai_decision']}) -> {it['final_status']}")
        print(f"   Notes: {it['notes']}")
    print(f"\nCounts before: {res['counts_before']}")
    print(f"Counts after: {res['counts_after']}")
    print(f"Preview Gate passed: {res['preview_gate_passed']}")
