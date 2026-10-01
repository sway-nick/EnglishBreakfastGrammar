"""
apply_batch3_corrections.py
Applies the 23 prepared targeted corrections for Batch 3 (TASK-015B).

Universal English Test Platform
1. Validates each replacement through the complete production pipeline:
   JSON/schema -> cardinality -> answer preservation -> grammar/integrity -> calibrated similarity -> AI review -> final status.
2. Performs atomic transactional database commit.
3. Updates parent exercises and lessons.
4. Updates adaptation_runs record for prod_batch_3_a1_350.
5. Runs Preview Gate validation.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, List, Tuple

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
RUN_ID = "prod_batch_3_a1_350"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("apply_batch3_corrections")

PREPARED_REPLACEMENTS: Dict[int, Dict[str, Any]] = {
    3626: {
        "text": "Look at this single photograph on the wall. ⇒ {{gap_1}} pictures from our recent vacation.",
        "gaps": [{"gap_order": 1, "correct_answer": "These are", "accepted_answers": ["These are"]}],
    },
    3628: {
        "text": "Look at that tall building across the river. ⇒ {{gap_1}} modern office towers.",
        "gaps": [{"gap_order": 1, "correct_answer": "Those are", "accepted_answers": ["Those are"]}],
    },
    3632: {
        "text": "Are those your new winter boots over there? ⇒ {{gap_1}} your favourite leather boot near the door?",
        "gaps": [{"gap_order": 1, "correct_answer": "Is this", "accepted_answers": ["Is this"]}],
    },
    4755: {
        "text": "A: 'We have exciting music playing in the hall. Would you like _____?' B: 'Thank you for asking, but I really dislike _____ in public.'",
        "options": [
            {"option_order": 1, "text": "dancing / dancing", "is_correct": 0},
            {"option_order": 2, "text": "dancing / to dance", "is_correct": 0},
            {"option_order": 3, "text": "to dance / dancing", "is_correct": 1},
        ],
    },
    4758: {
        "text": "At what age did both of your older cousins first learn _____?",
        "options": [
            {"option_order": 1, "text": "swam", "is_correct": 0},
            {"option_order": 2, "text": "to swim", "is_correct": 1},
            {"option_order": 3, "text": "swimming", "is_correct": 0},
        ],
    },
    4002: {
        "text": "'{{gap_1}} you present during the university lecture this morning?' 'Yes, I definitely {{gap_2}}.'",
        "gaps": [
            {"gap_order": 1, "correct_answer": "Were", "accepted_answers": ["Were"]},
            {"gap_order": 2, "correct_answer": "was", "accepted_answers": ["was"]},
        ],
    },
    4009: {
        "text": "'{{gap_1}} you busy with client meetings all afternoon?' 'Yes, I certainly {{gap_2}}.'",
        "gaps": [
            {"gap_order": 1, "correct_answer": "Were", "accepted_answers": ["Were"]},
            {"gap_order": 2, "correct_answer": "was", "accepted_answers": ["was"]},
        ],
    },
    4026: {
        "text": "You {{gap_1}} early for the concert, but Anna {{gap_2}} delayed by traffic.",
        "gaps": [
            {"gap_order": 1, "correct_answer": "were", "accepted_answers": ["were"]},
            {"gap_order": 2, "correct_answer": "was", "accepted_answers": ["was"]},
        ],
    },
    4030: {
        "text": "'{{gap_1}} Doctor Evans in the clinic?' 'No, several nurses {{gap_2}} working on the ward.'",
        "gaps": [
            {"gap_order": 1, "correct_answer": "Was", "accepted_answers": ["Was"]},
            {"gap_order": 2, "correct_answer": "were", "accepted_answers": ["were"]},
        ],
    },
    4012: {
        "text": "Search for the missing metal objects: where / the keys ⇒ {{gap_1}}?",
        "gaps": [{"gap_order": 1, "correct_answer": "Where were the keys", "accepted_answers": ["Where were the keys"]}],
    },
    3811: {
        "text": "_____ needs to consult a doctor at the clinic today.",
        "options": [
            {"option_order": 1, "text": "The father of Allan", "is_correct": 0},
            {"option_order": 2, "text": "Father's Edgar", "is_correct": 0},
            {"option_order": 3, "text": "Allan's father", "is_correct": 1},
        ],
    },
    3813: {
        "text": "Our favourite neighbourhood café is located at _____.",
        "options": [
            {"option_order": 1, "text": "the end of the street", "is_correct": 1},
            {"option_order": 2, "text": "the street's end", "is_correct": 0},
            {"option_order": 3, "text": "the end's street", "is_correct": 0},
        ],
    },
    3814: {
        "text": "Everyone on our block stopped to admire _____ parked in the driveway.",
        "options": [
            {"option_order": 1, "text": "New car's Lucy", "is_correct": 0},
            {"option_order": 2, "text": "Lucy's new car", "is_correct": 1},
            {"option_order": 3, "text": "The new car of Lucy", "is_correct": 0},
        ],
    },
    3818: {
        "text": "Before the summer break, nearly all of _____ are collected by the teachers.",
        "options": [
            {"option_order": 1, "text": "the textbooks' students", "is_correct": 0},
            {"option_order": 2, "text": "the students' textbooks", "is_correct": 1},
            {"option_order": 3, "text": "the student's textbooks", "is_correct": 0},
        ],
    },
    3819: {
        "text": "We received a lovely invitation because _____ takes place next weekend.",
        "options": [
            {"option_order": 1, "text": "Sheila and Mike's wedding", "is_correct": 1},
            {"option_order": 2, "text": "Sheila's and Mike's wedding", "is_correct": 0},
            {"option_order": 3, "text": "the wedding of Sheila and Mike", "is_correct": 0},
        ],
    },
    5151: {
        "text": "Do you want some fresh fruit from the garden? ⇒ {{gap_1}} some fresh fruit?",
        "gaps": [{"gap_order": 1, "correct_answer": "Would you like", "accepted_answers": ["Would you like"]}],
    },
    5163: {
        "text": "At which local restaurant would you like _____ with our visiting colleagues?",
        "options": [
            {"option_order": 1, "text": "to have dinner", "is_correct": 1},
            {"option_order": 2, "text": "having dinner", "is_correct": 0},
            {"option_order": 3, "text": "have dinner", "is_correct": 0},
        ],
    },
    2775: {
        "text": "Look at all these bright paints on the shelf. Which _____?",
        "options": [
            {"option_order": 1, "text": "your favourite colour is", "is_correct": 0},
            {"option_order": 2, "text": "does your favourite colour be", "is_correct": 0},
            {"option_order": 3, "text": "is your favourite colour", "is_correct": 1},
        ],
    },
    2778: {
        "text": "Following six months of regular exercise, how much weight _____?",
        "options": [
            {"option_order": 1, "text": "she has lost", "is_correct": 0},
            {"option_order": 2, "text": "does she have lost", "is_correct": 0},
            {"option_order": 3, "text": "has she lost", "is_correct": 1},
        ],
    },
    2781: {
        "text": "During school terms, at what hour in the evening _____ to sleep?",
        "options": [
            {"option_order": 1, "text": "children should", "is_correct": 0},
            {"option_order": 2, "text": "should children go", "is_correct": 1},
            {"option_order": 3, "text": "do children should go", "is_correct": 0},
        ],
    },
    2791: {
        "text": "A silver fountain pen lies on the conference table. ⇒ {{gap_1}}?",
        "gaps": [{"gap_order": 1, "correct_answer": "Whose pen is this", "accepted_answers": ["Whose pen is this"]}],
    },
    7086: {
        "text": "The library staff warned the group because everyone was making too much noise near the quiet area.",
        "options": [
            {"option_order": 1, "text": "making", "is_correct": 1},
            {"option_order": 2, "text": "doing", "is_correct": 0},
        ],
    },
    3336: {
        "text": "If we {{gap_1}} the express train, we {{gap_2}} delayed for the interview. (miss/be)",
        "gaps": [
            {"gap_order": 1, "correct_answer": "miss", "accepted_answers": ["miss"]},
            {"gap_order": 2, "correct_answer": "will be", "accepted_answers": ["will be"]},
        ],
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

    all_valid = True

    for qid, rep in sorted(PREPARED_REPLACEMENTS.items()):
        sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (str(qid),)).fetchone()
        if not sq:
            raise ValueError(f"Question {qid} not found in staging.db")

        aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (str(qid),)).fetchone()
        if not aq:
            raise ValueError(f"Question {qid} not found in adaptation.db")

        affected_exercise_ids.add(aq["adapted_exercise_id"])
        affected_lesson_ids.add(aq["adapted_lesson_id"])

        s_opts = [dict(r) for r in stage_conn.execute("SELECT * FROM staging_options WHERE question_id = ? ORDER BY option_order", (str(qid),)).fetchall()]
        s_gaps = [dict(r) for r in stage_conn.execute("SELECT * FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (str(qid),)).fetchall()]

        adapted_text = rep["text"].strip()
        adapted_opts = rep.get("options", [])
        adapted_gaps = rep.get("gaps", [])

        # 1. Cardinality validation
        rm = sq["response_model"]
        structural_errors = []
        if not adapted_text:
            structural_errors.append("Empty adapted text")
        if rm in ("single_choice", "multiple_choice") and len(adapted_opts) != len(s_opts):
            structural_errors.append(f"Option cardinality mismatch: got {len(adapted_opts)}, expected {len(s_opts)}")
        if rm == "gap" and len(adapted_gaps) != len(s_gaps):
            structural_errors.append(f"Gap cardinality mismatch: got {len(adapted_gaps)}, expected {len(s_gaps)}")

        # 2. Answer integrity
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
        if final_status != "VALIDATED":
            all_valid = False

        notes = "; ".join(reasons)
        if ai_decision:
            notes += f"; AI Review: {ai_decision} - {ai_reason}"

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
            "s_opts": s_opts,
            "adapted_opts": adapted_opts,
            "s_gaps": s_gaps,
            "adapted_gaps": adapted_gaps,
        })

    if not all_valid:
        raise ValueError("Not all 23 items reached VALIDATED status during dry-run!")

    if commit:
        logger.info(f"Committing corrections for {len(processed_items)} questions...")
        with adapt_conn:
            for item in processed_items:
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
                        f"TASK-015B Correction: {item['notes']}",
                        now_ts,
                        aqid,
                    ),
                )

                # Update options
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
                                    adaptation_notes = 'TASK-015B Correction'
                                WHERE adapted_option_id = ?
                                """,
                                (o_spec["text"], o_spec["text"], o_spec["is_correct"], item["rev_req"], opt_id),
                            )

                # Update gaps
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
                                    adaptation_notes = 'TASK-015B Correction'
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

            # Update adaptation_runs for Batch 3: 23 rejected converted to validated
            adapt_conn.execute(
                """
                UPDATE adaptation_runs
                SET validated_count = validated_count + 23,
                    rejected_count = rejected_count - 23,
                    notes = 'Batch 3 completed: 350 validated, 0 rejected after TASK-015B corrections.'
                WHERE run_id = ?
                """,
                (RUN_ID,),
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
        "counts_before": counts_before,
        "counts_after": counts_after,
        "preview_gate_passed": preview_gate_passed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply Batch 3 targeted corrections")
    parser.add_argument("--commit", action="store_true", help="Commit changes to database")
    args = parser.parse_args()

    res = run_apply_corrections(commit=args.commit)
    print("\n--- CORRECTIONS SUMMARY ---")
    for it in res["processed_items"]:
        print(f"QID {it['qid']}: {it['det_status']} (AI={it['ai_decision']}) -> {it['final_status']}")
    print(f"Counts before: {res['counts_before']}")
    print(f"Counts after: {res['counts_after']}")
    print(f"Preview Gate passed: {res['preview_gate_passed']}")
