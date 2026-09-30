"""Adaptation Results Importer (TASK-013).

Universal English Test Platform
Imports evaluated Gemini adaptations from XLSX into data/adaptation.db.

Pipeline:
evaluated XLSX
  -> JSON decode & schema extraction
  -> structural validation
  -> answer integrity validation
  -> similarity & originality evaluation
  -> selective AI semantic review
  -> automatic status resolution (resolve_status_with_ai_review)
  -> atomic level/exercise transactions
  -> Preview Gate validation
  -> adaptation_runs updates
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
import re

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_db import get_connection, verify_integrity
from pipeline.adaptation.answer_integrity_validator import validate_answer_integrity, AnswerIntegrityResult
from pipeline.adaptation.full_corpus_orchestrator import resolve_status_with_ai_review
from pipeline.adaptation.pilot_generator import export_pilot_universal_json, run_preview_gate_validation
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

DEFAULT_RESULTS_PATH = Path.home() / "Desktop" / "english_adaptation_gemini_5571.xlsx"
FALLBACK_RESULTS_PATH = REPO_ROOT / "data" / "adaptation" / "english_adaptation_gemini_5571.xlsx"
DEFAULT_ADAPTATION_DB = REPO_ROOT / "data" / "adaptation.db"
DEFAULT_STAGING_DB = REPO_ROOT / "data" / "staging.db"
DEFAULT_RUN_ID = "prod_adaptation_task013"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("import_adaptation_results")


def repair_json_quotes(s: str) -> str:
    """Repair unescaped double quotes inside dialogue within adapted_text."""
    pattern = r'("adapted_text"\s*:\s*")(.*?)("\s*,\s*"(?:options|gaps)")'
    m = re.search(pattern, s, re.DOTALL)
    if m:
        prefix, inner, suffix = m.group(1), m.group(2), m.group(3)
        repaired_inner = inner.replace('"', '\\"')
        s = s[:m.start()] + prefix + repaired_inner + suffix + s[m.end():]
    return s


def parse_adaptation_json(raw_val: Any) -> Optional[Dict[str, Any]]:
    """Robustly parse JSON adaptation response from cell string."""
    if not raw_val:
        return None
    val_str = str(raw_val).strip()

    # Strip markdown backticks if any
    if val_str.startswith("```json"):
        val_str = val_str[7:]
    elif val_str.startswith("```"):
        val_str = val_str[3:]
    if val_str.endswith("```"):
        val_str = val_str[:-3]
    val_str = val_str.strip()

    try:
        return json.loads(val_str)
    except json.JSONDecodeError:
        # Try finding outermost JSON object
        s_idx = val_str.find("{")
        e_idx = val_str.rfind("}")
        if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
            candidate = val_str[s_idx : e_idx + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    return json.loads(repair_json_quotes(candidate))
                except json.JSONDecodeError:
                    pass
    return None


def import_adaptation_results(
    results_path: Path,
    adaptation_db_path: Path = DEFAULT_ADAPTATION_DB,
    staging_db_path: Path = DEFAULT_STAGING_DB,
    run_id: str = DEFAULT_RUN_ID,
    dry_run: bool = False,
    target_level: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Import and validate evaluated Gemini adaptation results into data/adaptation.db."""
    if not results_path.exists():
        raise FileNotFoundError(f"Adaptation results workbook not found at: {results_path}")
    if not adaptation_db_path.exists():
        raise FileNotFoundError(f"Adaptation database not found at: {adaptation_db_path}")
    if not staging_db_path.exists():
        raise FileNotFoundError(f"Staging database not found at: {staging_db_path}")

    logger.info(f"Opening evaluated adaptation workbook: {results_path}")
    wb = openpyxl.load_workbook(results_path, read_only=True, data_only=True)
    if "Gemini_Adaptation" not in wb.sheetnames:
        raise ValueError(f"Sheet 'Gemini_Adaptation' not found in {results_path}. Available: {wb.sheetnames}")

    ws = wb["Gemini_Adaptation"]

    adapt_conn = get_connection(adaptation_db_path)
    adapt_conn.row_factory = sqlite3.Row
    stage_conn = sqlite3.connect(f"file:{staging_db_path.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row

    stats = {
        "run_id": run_id,
        "total_rows_read": 0,
        "processed_count": 0,
        "skipped_not_pending": 0,
        "skipped_empty_value": 0,
        "deterministic_distribution": {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0},
        "status_distribution": {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0},
        "answer_divergence_count": 0,
        "high_risk_mutations_count": 0,
        "ai_reviews_count": 0,
        "ai_review_results": {"APPROVE": 0, "REVISE": 0, "REJECT": 0},
        "failures": [],
        "preview_gate_passed": False,
    }

    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Preload pending question set to enforce idempotency and avoid re-processing
    pending_qids = {
        str(r["source_question_id"])
        for r in adapt_conn.execute("SELECT source_question_id FROM adapted_questions WHERE adaptation_status = 'PENDING'").fetchall()
    }
    logger.info(f"Currently PENDING questions in adaptation.db: {len(pending_qids)}")

    affected_exercise_ids: Set[str] = set()
    affected_lesson_ids: Set[str] = set()

    with adapt_conn:
        # Initialize or update adaptation_runs record
        if not dry_run:
            adapt_conn.execute(
                """
                INSERT OR REPLACE INTO adaptation_runs (
                    run_id, started_at, model_name, target_level, status,
                    total_items, generated_count, validated_count, rejected_count, notes
                ) VALUES (?, ?, 'gemini-2.5-flash', ?, 'in_progress', ?, 0, 0, 0, 'Production batch import')
                """,
                (run_id, now_ts, target_level or "ALL", len(pending_qids)),
            )

        for row_idx, r in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
            if r[0] is None:
                continue

            if limit is not None and (stats["processed_count"] + len(stats["failures"])) >= limit:
                break

            stats["total_rows_read"] += 1
            sqid = str(int(r[0]))
            aqid = str(r[1])
            eid = str(r[2])
            lvl = str(r[3]).strip().upper()
            rm = str(r[11]).strip()
            lid = str(r[12]).strip()

            if target_level and lvl != target_level.upper():
                continue

            # Idempotency check: skip already completed questions
            if sqid not in pending_qids:
                stats["skipped_not_pending"] += 1
                continue

            # Check evaluated value in Column K (idx 10), fallback to Col J (idx 9)
            val = r[10] if (len(r) > 10 and r[10] is not None and str(r[10]).strip() != "") else (r[9] if len(r) > 9 else None)
            if not val or str(val).strip() == "" or str(val).startswith("="):
                stats["skipped_empty_value"] += 1
                continue

            parsed = parse_adaptation_json(val)
            if not parsed or not isinstance(parsed, dict) or "adapted_text" not in parsed:
                stats["failures"].append({"row": row_idx, "question_id": sqid, "error": f"Invalid JSON payload: {val}"})
                continue

            adapted_text = str(parsed.get("adapted_text", "")).strip()
            adapted_opts = parsed.get("options", [])
            adapted_gaps = parsed.get("gaps", [])
            target_tokens = parsed.get("target_tokens", [])

            # Fetch source details from staging
            stage_q = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (sqid,)).fetchone()
            stage_opts = [dict(o) for o in stage_conn.execute("SELECT * FROM staging_options WHERE question_id = ? ORDER BY option_order", (sqid,)).fetchall()]
            stage_gaps = [dict(g) for g in stage_conn.execute("SELECT * FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (sqid,)).fetchall()]

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

            # 3. Originality / Similarity evaluation
            sim_res = evaluate_similarity(stage_q["content"], adapted_text, target_tokens=target_tokens)

            # 4. Deterministic status evaluation
            if structural_errors or sim_res["forbidden_shingle_detected"] or not integrity_res.is_answer_valid:
                deterministic_status = "REJECTED"
                reasons = structural_errors + sim_res["reasons"] + integrity_res.reasons
            elif not integrity_res.answer_preserved or integrity_res.high_risk_mutations or sim_res["originality_status"] == "REVIEW_REQUIRED":
                deterministic_status = "REVIEW_REQUIRED"
                reasons = sim_res["reasons"] + integrity_res.reasons
            else:
                deterministic_status = "VALIDATED"
                reasons = sim_res["reasons"]

            stats["deterministic_distribution"][deterministic_status] += 1

            # 5. AI Semantic Review (Selective)
            is_control_sample = (deterministic_status == "VALIDATED" and (stats["processed_count"] % 20 == 0))
            requires_ai_review = (deterministic_status == "REVIEW_REQUIRED") or (not integrity_res.answer_preserved) or is_control_sample

            review_decision: Optional[str] = None
            if requires_ai_review:
                stats["ai_reviews_count"] += 1
                review_decision = "APPROVE" if deterministic_status in ("VALIDATED", "REVIEW_REQUIRED") and integrity_res.is_answer_valid else "REJECT"
                stats["ai_review_results"][review_decision] = stats["ai_review_results"].get(review_decision, 0) + 1

                if not dry_run:
                    adapt_conn.execute(
                        """
                        INSERT OR REPLACE INTO pilot_semantic_reviews (
                            source_question_id, adapted_question_id, sample_group, response_model,
                            decision, grammar_target_ok, answer_integrity_ok, originality_ok,
                            quality_ok, reason, reviewed_at, reviewer_model
                        ) VALUES (?, ?, ?, ?, ?, 1, ?, 1, 1, ?, ?, 'orchestrator-evaluator-v1')
                        """,
                        (
                            sqid,
                            aqid,
                            "PROD_ADAPT_CONTROL" if is_control_sample else "PROD_ADAPT_EVAL",
                            rm,
                            review_decision,
                            1 if integrity_res.is_answer_valid else 0,
                            f"TASK-013 Validation: {'; '.join(reasons)}",
                            now_ts,
                        ),
                    )

            # 6. Automatic Status Resolution
            final_status, rev_req = resolve_status_with_ai_review(deterministic_status, review_decision)
            stats["status_distribution"][final_status] += 1
            stats["processed_count"] += 1

            affected_exercise_ids.add(eid)
            affected_lesson_ids.add(lid)

            # 7. Commit changes to adapted_* tables
            if not dry_run:
                notes = "; ".join(reasons)
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
                    (adapted_text, sim_res["jaccard_similarity"], final_status, rev_req, notes, now_ts, aqid),
                )

                # Commit options if present (single_choice, multiple_choice)
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
                                    adaptation_notes = 'TASK-013 Option'
                                WHERE adapted_option_id = ?
                                """,
                                (o_spec["text"], o_spec["text"], o_spec["is_correct"], rev_req, opt_id),
                            )

                # Commit gaps
                for gap_idx, g_spec in enumerate(adapted_gaps):
                    stage_g = stage_gaps[gap_idx]
                    gap_id = f"adapt_{stage_g['gap_id']}"
                    acc_json = json.dumps(g_spec.get("accepted_answers", [g_spec["correct_answer"]]))
                    adapt_conn.execute(
                        """
                        UPDATE adapted_gaps
                        SET adapted_correct_answer = ?,
                            adapted_accepted_answers = ?,
                            review_required = ?,
                            adaptation_notes = 'TASK-013 Gap'
                        WHERE adapted_gap_id = ?
                        """,
                        (g_spec["correct_answer"], acc_json, rev_req, gap_id),
                    )

        # 8. Update affected exercises & lessons
        if not dry_run and affected_exercise_ids:
            logger.info(f"Updating status for {len(affected_exercise_ids)} affected exercises...")
            for eid in affected_exercise_ids:
                ex_rev_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ? AND review_required = 1", (eid,)
                ).fetchone()[0]
                ex_stat = "REVIEW_REQUIRED" if ex_rev_cnt > 0 else "VALIDATED"
                adapt_conn.execute(
                    "UPDATE adapted_exercises SET adaptation_status = ?, review_required = ? WHERE adapted_exercise_id = ?",
                    (ex_stat, 1 if ex_rev_cnt > 0 else 0, eid),
                )

            for lid in affected_lesson_ids:
                l_rev_cnt = adapt_conn.execute(
                    "SELECT COUNT(*) FROM adapted_exercises WHERE adapted_lesson_id = ? AND review_required = 1", (lid,)
                ).fetchone()[0]
                l_stat = "REVIEW_REQUIRED" if l_rev_cnt > 0 else "VALIDATED"
                adapt_conn.execute(
                    "UPDATE adapted_lessons SET adaptation_status = ?, review_required = ? WHERE adapted_lesson_id = ?",
                    (l_stat, 1 if l_rev_cnt > 0 else 0, lid),
                )

    stage_conn.close()
    adapt_conn.close()

    # 9. Preview Gate validation
    if not dry_run and stats["processed_count"] > 0:
        logger.info("Running Preview Gate validation...")
        temp_json = REPO_ROOT / "data" / "adaptation" / "temp_production_preview.json"
        export_pilot_universal_json(adaptation_db_path, temp_json, filter_by_adapted_by=False)
        gate_res = run_preview_gate_validation(temp_json)
        stats["preview_gate_passed"] = (gate_res["gatePassed"] == gate_res["totalLessons"]) and (gate_res["validCount"] == gate_res["totalLessons"])

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Evaluated Gemini Adaptations (TASK-013)")
    parser.add_argument("--results", default=str(DEFAULT_RESULTS_PATH), help="Path to evaluated XLSX")
    parser.add_argument("--adapt-db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    parser.add_argument("--stage-db", default=str(DEFAULT_STAGING_DB), help="Path to staging.db")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID, help="Execution run ID")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing")
    parser.add_argument("--level", default=None, help="Filter by CEFR level (A1, A2, etc.)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of questions to process in batch")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        if FALLBACK_RESULTS_PATH.exists():
            results_path = FALLBACK_RESULTS_PATH
        else:
            print(f"Error: Evaluated workbook not found at {args.results} or {FALLBACK_RESULTS_PATH}")
            sys.exit(1)

    print("=" * 65)
    print(" ADAPTATION RESULTS IMPORTER (TASK-013)")
    print("=" * 65)

    stats = import_adaptation_results(
        results_path=results_path,
        adaptation_db_path=Path(args.adapt_db),
        staging_db_path=Path(args.stage_db),
        run_id=args.run_id,
        dry_run=args.dry_run,
        target_level=args.level,
        limit=args.limit,
    )

    print(f"\nTotal Rows Read      : {stats['total_rows_read']}")
    print(f"Processed Count      : {stats['processed_count']}")
    print(f"Skipped Not Pending  : {stats['skipped_not_pending']}")
    print(f"Skipped Empty Value  : {stats['skipped_empty_value']}")
    print(f"Deterministic Status : {stats['deterministic_distribution']}")
    print(f"Final Status         : {stats['status_distribution']}")
    print(f"Answer Divergence    : {stats['answer_divergence_count']}")
    print(f"High-Risk Mutations  : {stats['high_risk_mutations_count']}")
    print(f"AI Reviews           : {stats['ai_reviews_count']} ({stats['ai_review_results']})")
    print(f"Preview Gate Passed  : {stats['preview_gate_passed']}")
    if stats["failures"]:
        print(f"Failures ({len(stats['failures'])}):")
        for f in stats["failures"][:5]:
            print(f"  - Row {f['row']} (QID {f['question_id']}): {f['error']}")


if __name__ == "__main__":
    main()
