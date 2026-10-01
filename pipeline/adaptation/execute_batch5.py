"""
Production Adaptation Batch 5 Executor.

Universal English Test Platform
Executes Batch 5 adaptation import for exactly 1,000 PENDING questions (rows 2053–3052):
- Strict answer-preservation strategy
- Calibrated boundary-aware similarity evaluation
- Automatic AI semantic review flow for REVIEW_REQUIRED
- Atomic transactional commits
- Preview Gate validation
- Extraction of compact REJECTED EVIDENCE PACKET
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import openpyxl

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_db import get_connection, verify_integrity
from pipeline.adaptation.answer_integrity_validator import validate_answer_integrity, AnswerIntegrityResult
from pipeline.adaptation.execute_batch3 import evaluate_ai_review
from pipeline.adaptation.full_corpus_orchestrator import resolve_status_with_ai_review
from pipeline.adaptation.import_adaptation_results import parse_adaptation_json
from pipeline.adaptation.pilot_generator import export_pilot_universal_json, run_preview_gate_validation
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

DEFAULT_RESULTS_PATH = Path.home() / "Desktop" / "english_adaptation_gemini_5571.xlsx"
FALLBACK_RESULTS_PATH = REPO_ROOT / "data" / "adaptation" / "english_adaptation_gemini_5571.xlsx"
DEFAULT_ADAPTATION_DB = REPO_ROOT / "data" / "adaptation.db"
DEFAULT_STAGING_DB = REPO_ROOT / "data" / "staging.db"
RUN_ID = "prod_batch_5_a1_1000"
BATCH_SIZE = 1000
START_ROW = 2053
END_ROW = 3052

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("execute_batch5")


def run_batch5(
    results_path: Optional[Path] = None,
    adaptation_db_path: Path = DEFAULT_ADAPTATION_DB,
    staging_db_path: Path = DEFAULT_STAGING_DB,
    batch_size: int = BATCH_SIZE,
    start_row: int = START_ROW,
    end_row: int = END_ROW,
    dry_run: bool = True,
) -> Dict[str, Any]:
    if results_path is None:
        results_path = DEFAULT_RESULTS_PATH
    if not results_path.exists():
        if FALLBACK_RESULTS_PATH.exists():
            results_path = FALLBACK_RESULTS_PATH
        else:
            raise FileNotFoundError(f"Workbook not found at {results_path} or {FALLBACK_RESULTS_PATH}")

    logger.info(f"Opening workbook: {results_path}")
    wb = openpyxl.load_workbook(results_path, read_only=True, data_only=True)
    ws = wb["Gemini_Adaptation"]

    adapt_conn = get_connection(adaptation_db_path)
    adapt_conn.row_factory = sqlite3.Row
    stage_conn = sqlite3.connect(f"file:{staging_db_path.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row

    # Get set of all currently PENDING question IDs
    pending_rows = adapt_conn.execute(
        "SELECT source_question_id, adapted_question_id, adapted_exercise_id, adapted_lesson_id, response_model "
        "FROM adapted_questions WHERE adaptation_status = 'PENDING'"
    ).fetchall()
    pending_map = {str(r["source_question_id"]): dict(r) for r in pending_rows}
    logger.info(f"Found {len(pending_map)} PENDING questions in adaptation.db")

    # Counts before
    counts_before = dict(adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())

    # Get sets of already finalized (VALIDATED or REJECTED) QIDs
    finalized_qids = set(
        r[0] for r in adapt_conn.execute("SELECT source_question_id FROM adapted_questions WHERE adaptation_status IN ('VALIDATED', 'REJECTED')").fetchall()
    )

    # Select exactly the batch_size rows starting at start_row
    selected_items: List[Dict[str, Any]] = []
    for row_idx, r in enumerate(ws.iter_rows(min_row=start_row, max_row=end_row, values_only=True), start=start_row):
        if r[0] is None:
            continue
        sqid = str(int(r[0]))
        if sqid in pending_map:
            val = r[10] if len(r) > 10 and r[10] is not None and str(r[10]).strip() != "" else (r[9] if len(r) > 9 else None)
            selected_items.append({
                "row_idx": row_idx,
                "sqid": sqid,
                "db_record": pending_map[sqid],
                "val": val,
            })
            if len(selected_items) == batch_size:
                break

    logger.info(f"Selected {len(selected_items)} PENDING questions for Batch 5.")
    if len(selected_items) != batch_size:
        raise ValueError(f"Expected to select exactly {batch_size} questions, but selected {len(selected_items)}")

    # Pre-processing Safety Verification
    selected_qids = [item["sqid"] for item in selected_items]
    assert len(selected_qids) == 1000, "Must be exactly 1,000 QIDs"
    for qid in selected_qids:
        assert qid in pending_map, f"QID {qid} was not PENDING!"
        assert qid not in finalized_qids, f"QID {qid} is already finalized!"
        assert qid != "6096", "QID 6096 must not be selected!"

    stats: Dict[str, Any] = {
        "run_id": RUN_ID,
        "batch_size": len(selected_items),
        "first_row": selected_items[0]["row_idx"],
        "last_row": selected_items[-1]["row_idx"],
        "first_sqid": selected_items[0]["sqid"],
        "last_sqid": selected_items[-1]["sqid"],
        "selected_qids": selected_qids,
        "parsed_valid_count": 0,
        "parsed_invalid_count": 0,
        "prompt_echo_count": 0,
        "retryable_count": 0,
        "deterministic_distribution": {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0},
        "final_distribution": {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0, "PENDING": 0},
        "ai_reviews_count": 0,
        "ai_review_results": {"APPROVE": 0, "REVISE": 0, "REJECT": 0},
        "answer_divergence_count": 0,
        "high_risk_mutations_count": 0,
        "similarity_stats": {
            "jaccard_sum": 0.0,
            "levenshtein_sum": 0.0,
            "count": 0,
            "max_jaccard": 0.0,
            "max_levenshtein": 0.0,
            "shingles_detected_count": 0,
        },
        "failures": [],
        "rejected_evidence_packets": [],
        "counts_before": counts_before,
        "counts_after": {},
        "preview_gate_passed": False,
    }

    processed_questions: List[Dict[str, Any]] = []
    affected_exercise_ids: Set[str] = set()
    affected_lesson_ids: Set[str] = set()
    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for item in selected_items:
        row_idx = item["row_idx"]
        sqid = item["sqid"]
        db_rec = item["db_record"]
        aqid = db_rec["adapted_question_id"]
        eid = db_rec["adapted_exercise_id"]
        lid = db_rec["adapted_lesson_id"]
        rm = db_rec["response_model"]
        val = item["val"]

        affected_exercise_ids.add(eid)
        affected_lesson_ids.add(lid)

        # Stage details
        stage_q = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (sqid,)).fetchone()
        stage_opts = [dict(o) for o in stage_conn.execute("SELECT * FROM staging_options WHERE question_id = ? ORDER BY option_order", (sqid,)).fetchall()]
        stage_gaps = [dict(g) for g in stage_conn.execute("SELECT * FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (sqid,)).fetchall()]

        stage_correct = [o["text"] for o in stage_opts if o["is_correct"]] if stage_opts else [g["correct_answer"] for g in stage_gaps]

        parsed = parse_adaptation_json(val)
        if not parsed or not isinstance(parsed, dict) or "adapted_text" not in parsed:
            is_prompt_echo = str(val or "").strip().startswith("Task: Adapt")
            if is_prompt_echo:
                stats["prompt_echo_count"] += 1
                fail_note = "RETRYABLE: Prompt text returned without Gemini JSON output"
            else:
                stats["parsed_invalid_count"] += 1
                fail_note = f"Parse Failure: {val}"
            stats["retryable_count"] += 1
            stats["final_distribution"]["PENDING"] += 1
            stats["failures"].append({"row": row_idx, "question_id": sqid, "error": fail_note})

            if not dry_run:
                adapt_conn.execute(
                    """
                    UPDATE adapted_questions
                    SET adaptation_notes = ?,
                        review_required = 1
                    WHERE adapted_question_id = ?
                    """,
                    (fail_note, aqid),
                )
            continue

        stats["parsed_valid_count"] += 1
        adapted_text = str(parsed.get("adapted_text", "")).strip()
        adapted_opts = parsed.get("options", [])
        adapted_gaps = parsed.get("gaps", [])
        target_tokens = parsed.get("target_tokens", [])

        # 1. Structural validation
        structural_errors = []
        if not adapted_text:
            structural_errors.append("Empty adapted text")
        if rm in ("single_choice", "multiple_choice"):
            if len(adapted_opts) != len(stage_opts):
                structural_errors.append(f"Option cardinality mismatch: got {len(adapted_opts)}, expected {len(stage_opts)}")
        if rm == "gap":
            if len(adapted_gaps) != len(stage_gaps):
                structural_errors.append(f"Gap cardinality mismatch: got {len(adapted_gaps)}, expected {len(stage_gaps)}")

        # 2. Answer integrity validation
        source_item = {
            "question_id": sqid,
            "response_model": rm,
            "content": stage_q["content"],
            "options": stage_opts,
            "gaps": stage_gaps,
        }
        adapted_item = {
            "adapted_text": adapted_text,
            "options": adapted_opts,
            "gaps": adapted_gaps,
        }
        integrity_res: AnswerIntegrityResult = validate_answer_integrity(source_item, adapted_item)

        if not integrity_res.answer_preserved:
            stats["answer_divergence_count"] += 1
        if integrity_res.high_risk_mutations:
            stats["high_risk_mutations_count"] += 1

        # 3. Similarity evaluation (calibrated boundary-aware)
        sim_res = evaluate_similarity(stage_q["content"], adapted_text, target_tokens=target_tokens)
        j = sim_res["jaccard_similarity"]
        l = sim_res["levenshtein_similarity"]
        stats["similarity_stats"]["jaccard_sum"] += j
        stats["similarity_stats"]["levenshtein_sum"] += l
        stats["similarity_stats"]["count"] += 1
        stats["similarity_stats"]["max_jaccard"] = max(stats["similarity_stats"]["max_jaccard"], j)
        stats["similarity_stats"]["max_levenshtein"] = max(stats["similarity_stats"]["max_levenshtein"], l)
        if sim_res["forbidden_shingle_detected"]:
            stats["similarity_stats"]["shingles_detected_count"] += 1

        # 4. Deterministic status evaluation
        if structural_errors or sim_res["originality_status"] == "REJECTED" or not integrity_res.is_answer_valid:
            deterministic_status = "REJECTED"
            reasons = structural_errors + sim_res["reasons"] + integrity_res.reasons
        elif not integrity_res.answer_preserved or integrity_res.high_risk_mutations or sim_res["originality_status"] == "REVIEW_REQUIRED":
            deterministic_status = "REVIEW_REQUIRED"
            reasons = sim_res["reasons"] + integrity_res.reasons
        else:
            deterministic_status = "VALIDATED"
            reasons = sim_res["reasons"]

        stats["deterministic_distribution"][deterministic_status] += 1

        # 5. AI Semantic Review (for all deterministic REVIEW_REQUIRED)
        ai_decision = None
        ai_reason = ""
        if deterministic_status == "REVIEW_REQUIRED":
            stats["ai_reviews_count"] += 1
            ai_decision, ai_reason = evaluate_ai_review(
                sqid=sqid,
                rm=rm,
                stage_q=stage_q,
                stage_opts=stage_opts,
                stage_gaps=stage_gaps,
                adapted_text=adapted_text,
                adapted_opts=adapted_opts,
                adapted_gaps=adapted_gaps,
                integrity_res=integrity_res,
                sim_res=sim_res,
            )
            stats["ai_review_results"][ai_decision] = stats["ai_review_results"].get(ai_decision, 0) + 1

        # 6. Automatic status resolution
        final_status, rev_req = resolve_status_with_ai_review(deterministic_status, ai_decision)
        stats["final_distribution"][final_status] += 1

        notes = "; ".join(reasons)
        if ai_decision:
            notes += f"; AI Review: {ai_decision} - {ai_reason}"

        # If rejected, construct Compact Evidence Packet
        if final_status == "REJECTED":
            adapted_correct = [o["text"] for o in adapted_opts if o.get("is_correct")] if adapted_opts else [g["correct_answer"] for g in adapted_gaps]
            rejection_stage = "deterministic_evaluator" if deterministic_status == "REJECTED" else "ai_semantic_review"
            exact_rejection_reason = "; ".join(reasons) if deterministic_status == "REJECTED" else ai_reason

            packet: Dict[str, Any] = {
                "qid": sqid,
                "model": rm,
                "rejection_stage": rejection_stage,
                "exact_rejection_reason": exact_rejection_reason,
                "source_text": stage_q["content"],
                "adapted_text": adapted_text,
                "source_correct_answer": stage_correct,
                "adapted_correct_answer": adapted_correct,
                "jaccard": round(j, 4),
                "levenshtein": round(l, 4),
                "matching_shingles": sim_res.get("matching_shingles", []),
                "high_risk_mutations": integrity_res.high_risk_mutations,
            }
            if rm == "gap":
                packet["gap_count_source"] = len(stage_gaps)
                packet["gap_count_adapted"] = len(adapted_gaps)
            else:
                packet["source_options"] = [o["text"] for o in stage_opts]
                packet["adapted_options"] = [o["text"] for o in adapted_opts]
            stats["rejected_evidence_packets"].append(packet)

        processed_questions.append({
            "sqid": sqid,
            "aqid": aqid,
            "eid": eid,
            "lid": lid,
            "adapted_text": adapted_text,
            "similarity_score": j,
            "final_status": final_status,
            "rev_req": rev_req,
            "notes": notes,
            "stage_opts": stage_opts,
            "adapted_opts": adapted_opts,
            "stage_gaps": stage_gaps,
            "adapted_gaps": adapted_gaps,
            "ai_decision": ai_decision,
            "ai_reason": ai_reason,
            "rm": rm,
        })

    # Execute Transactional Commit if not dry-run
    if not dry_run:
        logger.info(f"Committing Batch 5 transaction ({len(processed_questions)} questions)...")
        with adapt_conn:
            # 1. Update adaptation_runs
            adapt_conn.execute(
                """
                INSERT OR REPLACE INTO adaptation_runs (
                    run_id, started_at, model_name, target_level, status,
                    total_items, generated_count, validated_count, rejected_count, notes
                ) VALUES (?, ?, 'gemini-2.5-flash', 'A1', 'in_progress', ?, ?, 0, 0, 'Production Batch 5 started')
                """,
                (RUN_ID, now_ts, BATCH_SIZE, len(processed_questions)),
            )

            # 2. Update adapted_questions, adapted_options, adapted_gaps, and pilot_semantic_reviews
            for q_data in processed_questions:
                aqid = q_data["aqid"]
                sqid = q_data["sqid"]
                rm = q_data["rm"]
                final_status = q_data["final_status"]
                rev_req = q_data["rev_req"]
                notes = q_data["notes"]
                adapted_text = q_data["adapted_text"]
                sim_score = q_data["similarity_score"]
                adapted_opts = q_data["adapted_opts"]
                stage_opts = q_data["stage_opts"]
                adapted_gaps = q_data["adapted_gaps"]
                stage_gaps = q_data["stage_gaps"]
                ai_decision = q_data["ai_decision"]
                ai_reason = q_data["ai_reason"]

                adapt_conn.execute(
                    """
                    UPDATE adapted_questions
                    SET adapted_text = ?,
                        similarity_score = ?,
                        adaptation_status = ?,
                        review_required = ?,
                        adaptation_notes = ?,
                        adapted_by = 'gemini-2.5-flash',
                        adapted_at = ?
                    WHERE adapted_question_id = ?
                    """,
                    (adapted_text, sim_score, final_status, rev_req, notes, now_ts, aqid),
                )

                # Commit options
                if adapted_opts:
                    for opt_idx, o_spec in enumerate(adapted_opts):
                        if opt_idx < len(stage_opts):
                            stage_o = stage_opts[opt_idx]
                            opt_id = f"adapt_{stage_o['option_id']}"
                            adapt_conn.execute(
                                """
                                UPDATE adapted_options
                                SET adapted_text = ?,
                                    adapted_value = ?,
                                    adapted_is_correct = ?,
                                    review_required = ?,
                                    adaptation_notes = 'TASK-020 Batch 5'
                                WHERE adapted_option_id = ?
                                """,
                                (o_spec["text"], o_spec["text"], o_spec["is_correct"], rev_req, opt_id),
                            )

                # Commit gaps
                if adapted_gaps:
                    for gap_idx, g_spec in enumerate(adapted_gaps):
                        if gap_idx < len(stage_gaps):
                            stage_g = stage_gaps[gap_idx]
                            gap_id = f"adapt_{stage_g['gap_id']}"
                            acc_json = json.dumps(g_spec.get("accepted_answers", [g_spec["correct_answer"]]))
                            adapt_conn.execute(
                                """
                                UPDATE adapted_gaps
                                SET adapted_correct_answer = ?,
                                    adapted_accepted_answers = ?,
                                    review_required = ?,
                                    adaptation_notes = 'TASK-020 Batch 5'
                                WHERE adapted_gap_id = ?
                                """,
                                (g_spec["correct_answer"], acc_json, rev_req, gap_id),
                            )

                # Record AI review audit
                if ai_decision:
                    adapt_conn.execute(
                        """
                        INSERT OR REPLACE INTO pilot_semantic_reviews (
                            source_question_id, adapted_question_id, sample_group, response_model,
                            decision, grammar_target_ok, answer_integrity_ok, originality_ok,
                            quality_ok, reason, reviewed_at, reviewer_model
                        ) VALUES (?, ?, 'PROD_ADAPT_EVAL', ?, ?, 1, 1, 1, 1, ?, ?, 'semantic-reviewer-expert-v1')
                        """,
                        (sqid, aqid, rm, ai_decision, ai_reason, now_ts),
                    )

            # 3. Update affected exercises
            for eid in affected_exercise_ids:
                ex_rev_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND review_required = 1", (eid,)
                ).fetchone()[0]
                ex_pend_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND adaptation_status = 'PENDING'", (eid,)
                ).fetchone()[0]
                ex_rej_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND adaptation_status = 'REJECTED'", (eid,)
                ).fetchone()[0]
                ex_stat = "REVIEW_REQUIRED" if ex_rev_cnt > 0 else ("PENDING" if ex_pend_cnt > 0 else ("REJECTED" if ex_rej_cnt > 0 else "VALIDATED"))
                adapt_conn.execute(
                    "UPDATE adapted_exercises SET adaptation_status = ?, review_required = ? WHERE adapted_exercise_id = ?",
                    (ex_stat, 1 if ex_rev_cnt > 0 else 0, eid),
                )

            # 4. Update affected lessons
            for lid in affected_lesson_ids:
                les_rev_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND review_required = 1", (lid,)
                ).fetchone()[0]
                les_pend_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND adaptation_status = 'PENDING'", (lid,)
                ).fetchone()[0]
                les_rej_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_lesson_id = ? AND adaptation_status = 'REJECTED'", (lid,)
                ).fetchone()[0]
                les_stat = "REVIEW_REQUIRED" if les_rev_cnt > 0 else ("PENDING" if les_pend_cnt > 0 else ("REJECTED" if les_rej_cnt > 0 else "VALIDATED"))
                adapt_conn.execute(
                    "UPDATE adapted_lessons SET adaptation_status = ?, review_required = ? WHERE adapted_lesson_id = ?",
                    (les_stat, 1 if les_rev_cnt > 0 else 0, lid),
                )

            # 5. Finalize adaptation_runs
            val_count = stats["final_distribution"]["VALIDATED"]
            rej_count = stats["final_distribution"]["REJECTED"]
            adapt_conn.execute(
                """
                UPDATE adaptation_runs
                SET status = 'completed',
                    completed_at = ?,
                    generated_count = ?,
                    validated_count = ?,
                    rejected_count = ?,
                    notes = ?
                WHERE run_id = ?
                """,
                (
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    len(processed_questions),
                    val_count,
                    rej_count,
                    f"Batch 5 completed: {val_count} validated, {rej_count} rejected.",
                    RUN_ID,
                ),
            )

    # Counts after
    counts_after = dict(adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
    stats["counts_after"] = counts_after

    stage_conn.close()
    adapt_conn.close()

    # Export rejection evidence packets to report if any
    report_path = REPO_ROOT / "data" / "reports" / "prod_batch_5_rejected_evidence.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(stats["rejected_evidence_packets"], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(stats['rejected_evidence_packets'])} rejected evidence packets to {report_path}")

    # Preview Gate validation
    if not dry_run and stats["final_distribution"]["VALIDATED"] > 0:
        logger.info("Running Preview Gate validation on exported universal JSON...")
        temp_json = REPO_ROOT / "data" / "adaptation" / "temp_production_preview.json"
        export_pilot_universal_json(adaptation_db_path, temp_json, filter_by_adapted_by=False)
        gate_res = run_preview_gate_validation(temp_json)
        stats["preview_gate_passed"] = (gate_res["gatePassed"] == gate_res["totalLessons"]) and (gate_res["validCount"] == gate_res["totalLessons"])
        stats["preview_gate_result"] = gate_res
        if temp_json.exists():
            temp_json.unlink()

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute Production Adaptation Batch 5")
    parser.add_argument("--commit", action="store_true", help="Commit changes to database (default is dry-run)")
    args = parser.parse_args()

    results = run_batch5(dry_run=not args.commit)
    print("\n--- BATCH 5 SUMMARY ---")
    print(f"Run ID: {results.get('run_id')}")
    print(f"Batch size: {results.get('batch_size')}")
    print(f"Rows: {results.get('first_row')} - {results.get('last_row')}")
    print(f"QIDs: {results.get('first_sqid')} - {results.get('last_sqid')}")
    print(f"Parsed valid: {results.get('parsed_valid_count')} / {results.get('batch_size')}")
    print(f"Deterministic distribution: {results.get('deterministic_distribution')}")
    print(f"AI Reviews: {results.get('ai_reviews_count')} {results.get('ai_review_results')}")
    print(f"Final distribution: {results.get('final_distribution')}")
    print(f"Counts before: {results.get('counts_before')}")
    print(f"Counts after: {results.get('counts_after')}")
    if results.get("similarity_stats", {}).get("count", 0) > 0:
        cnt = results["similarity_stats"]["count"]
        mean_j = results["similarity_stats"]["jaccard_sum"] / cnt
        mean_l = results["similarity_stats"]["levenshtein_sum"] / cnt
        print(f"Similarity: Mean Jaccard={mean_j:.4f}, Max Jaccard={results['similarity_stats']['max_jaccard']:.4f}")
        print(f"Similarity: Mean Lev={mean_l:.4f}, Max Lev={results['similarity_stats']['max_levenshtein']:.4f}")
        print(f"Shingles detected: {results['similarity_stats']['shingles_detected_count']}")
    print(f"Preview Gate passed: {results.get('preview_gate_passed')}")
    print(f"Rejected count: {len(results.get('rejected_evidence_packets', []))}")
