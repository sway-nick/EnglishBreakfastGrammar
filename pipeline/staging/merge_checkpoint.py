"""
merge_checkpoint.py
Merges verified 182-question Gemini enrichment checkpoint into data/staging.db.

STRICT CONTRACT:
1. Does NOT call Gemini API.
2. Does NOT modify the source checkpoint XLSX.
3. Does NOT alter question text, options, gaps, or explanations.
4. Populates correct_answer, accepted_answers, and is_correct strictly for the 182 questions.
5. All updates execute in a single atomic database transaction (full rollback on error).
6. Asserts 0 changes outside the 182-question scope.
"""

from pathlib import Path
import argparse
import json
import logging
import sqlite3
import sys
from typing import Dict, Any, List, Tuple
import openpyxl

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CHECKPOINT = Path.home() / "Desktop" / "english_cms_gemini_all_182.xlsx"
DEFAULT_DB = REPO_ROOT / "data" / "staging.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("merge_checkpoint")


def load_checkpoint_data(xlsx_path: Path) -> List[Dict[str, Any]]:
    """Loads and validates the 182 rows from the Gemini enrichment workbook."""
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Checkpoint XLSX not found at: {xlsx_path}")

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    if "Gemini_Enrichment" not in wb.sheetnames:
        raise ValueError(f"Missing 'Gemini_Enrichment' sheet in {xlsx_path}. Found: {wb.sheetnames}")

    ws = wb["Gemini_Enrichment"]
    rows = list(ws.iter_rows(values_only=True))[2:]  # Row 1=title, 2=headers, 3+=data

    checkpoint_records = []
    for idx, r in enumerate(rows, start=3):
        if r[0] is None:
            continue
        qid = str(int(r[0]))
        exercise_id = str(r[1] or "")
        lesson_id = str(r[2] or "")
        order = int(r[3] or 0)
        response_model = str(r[4] or "").strip()
        instruction = str(r[5] or "")
        sentence = str(r[6] or "")
        options_context = str(r[7] or "")
        # Raw value can be in column 9 (raw) or column 8 (formula result)
        val = r[9] if r[9] is not None else r[8]
        if val is None:
            raise ValueError(f"Row {idx} (QID {qid}) has null answer value")

        val_str = str(val).strip()
        try:
            parsed_answer = json.loads(val_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Row {idx} (QID {qid}) invalid JSON: {val_str}") from exc

        checkpoint_records.append({
            "row_idx": idx,
            "question_id": qid,
            "exercise_id": exercise_id,
            "lesson_id": lesson_id,
            "order": order,
            "response_model": response_model,
            "instruction": instruction,
            "sentence": sentence,
            "options_context": options_context,
            "parsed_answer": parsed_answer,
        })

    return checkpoint_records


def merge_checkpoint_into_staging(
    checkpoint_path: Path,
    db_path: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Merges checkpoint answers into SQLite staging database within an atomic transaction."""
    records = load_checkpoint_data(checkpoint_path)
    logger.info(f"Loaded {len(records)} records from checkpoint.")
    if len(records) != 182:
        logger.warning(f"Expected 182 records, found {len(records)}")

    if not db_path.exists():
        raise FileNotFoundError(f"Staging database not found at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    report: Dict[str, Any] = {
        "checkpoint_questions": len(records),
        "matched_questions": 0,
        "unmatched_questions": 0,
        "answered_gaps": 0,
        "answered_options": 0,
        "remaining_unanswered_questions": 0,
        "remaining_unanswered_gaps": 0,
        "remaining_unanswered_options": 0,
        "validation_errors": []
    }

    try:
        cursor.execute("BEGIN TRANSACTION;")

        checkpoint_qids = []

        for item in records:
            qid = item["question_id"]
            model = item["response_model"]
            parsed_ans = item["parsed_answer"]
            checkpoint_qids.append(qid)

            # 1. Verify question exists in staging
            cursor.execute(
                "SELECT question_id, response_model FROM staging_questions WHERE question_id = ?;",
                (qid,)
            )
            q_row = cursor.fetchone()
            if not q_row:
                err = f"Question ID {qid} not found in staging_questions"
                report["validation_errors"].append(err)
                report["unmatched_questions"] += 1
                continue

            report["matched_questions"] += 1
            db_model = q_row[1]

            # 2. Process by model
            if model == "gap":
                cursor.execute(
                    "SELECT gap_id, gap_order, input_control FROM staging_gaps WHERE question_id = ? ORDER BY gap_order;",
                    (qid,)
                )
                db_gaps = cursor.fetchall()
                if not db_gaps:
                    err = f"No gaps found in staging for gap question {qid}"
                    report["validation_errors"].append(err)
                    continue

                for g_key, g_ans in parsed_ans.items():
                    # Parse expected gap order from key e.g. "gap_1" -> 1
                    try:
                        g_order = int(g_key.replace("gap_", "")) if "gap_" in g_key else int(g_key)
                    except ValueError:
                        g_order = 1

                    # Match gap by order or gap_id
                    matched_gap = None
                    for dg in db_gaps:
                        if dg[1] == g_order or dg[0] == g_key:
                            matched_gap = dg
                            break

                    if not matched_gap:
                        err = f"Gap key '{g_key}' for QID {qid} could not be matched to staging gaps"
                        report["validation_errors"].append(err)
                        continue

                    gap_id, gap_order, input_control = matched_gap
                    accepted_json = json.dumps([g_ans])

                    # Update gap
                    cursor.execute("""
                        UPDATE staging_gaps
                        SET correct_answer = ?, accepted_answers = ?
                        WHERE gap_id = ?;
                    """, (str(g_ans), accepted_json, gap_id))
                    report["answered_gaps"] += 1

                    # If select, update options
                    if input_control == "select":
                        cursor.execute(
                            "SELECT option_id, text, value FROM staging_options WHERE gap_id = ?;",
                            (gap_id,)
                        )
                        gap_opts = cursor.fetchall()
                        matched_opt = False
                        for opt_id, opt_text, opt_val in gap_opts:
                            is_correct = 1 if (opt_text == str(g_ans) or opt_val == str(g_ans)) else 0
                            if is_correct == 1:
                                matched_opt = True
                            cursor.execute("""
                                UPDATE staging_options
                                SET is_correct = ?
                                WHERE option_id = ?;
                            """, (is_correct, opt_id))
                            report["answered_options"] += 1

                        if not matched_opt and gap_opts:
                            err = f"QID {qid} Gap {gap_id}: Answer '{g_ans}' does not match any available option {[o[1] for o in gap_opts]}"
                            report["validation_errors"].append(err)

            elif model in ("single_choice", "multiple_choice"):
                # Answer can be string or list/dict
                if isinstance(parsed_ans, dict):
                    ans_val = parsed_ans.get("answer") or parsed_ans.get("selected") or list(parsed_ans.values())[0]
                else:
                    ans_val = parsed_ans

                correct_set = set([ans_val] if isinstance(ans_val, str) else ans_val)

                cursor.execute(
                    "SELECT option_id, text, value FROM staging_options WHERE question_id = ?;",
                    (qid,)
                )
                q_opts = cursor.fetchall()
                if not q_opts:
                    err = f"No options found in staging for choice question {qid}"
                    report["validation_errors"].append(err)
                    continue

                matched_any = False
                for opt_id, opt_text, opt_val in q_opts:
                    is_correct = 1 if (opt_text in correct_set or opt_val in correct_set) else 0
                    if is_correct == 1:
                        matched_any = True
                    cursor.execute("""
                        UPDATE staging_options
                        SET is_correct = ?
                        WHERE option_id = ?;
                    """, (is_correct, opt_id))
                    report["answered_options"] += 1

                if not matched_any and q_opts:
                    err = f"QID {qid}: Answer '{correct_set}' does not match any available option {[o[1] for o in q_opts]}"
                    report["validation_errors"].append(err)

        # 3. Post-merge boundary check (strictly no modifications outside 182 questions)
        placeholders = ",".join("?" * len(checkpoint_qids))
        cursor.execute(f"""
            SELECT COUNT(*) FROM staging_gaps
            WHERE question_id NOT IN ({placeholders}) AND correct_answer IS NOT NULL;
        """, checkpoint_qids)
        external_gaps = cursor.fetchone()[0]
        if external_gaps > 0:
            report["validation_errors"].append(f"CRITICAL: {external_gaps} gaps outside 182-question scope were modified!")

        cursor.execute(f"""
            SELECT COUNT(*) FROM staging_options
            WHERE question_id NOT IN ({placeholders}) AND is_correct IS NOT NULL;
        """, checkpoint_qids)
        external_opts = cursor.fetchone()[0]
        if external_opts > 0:
            report["validation_errors"].append(f"CRITICAL: {external_opts} options outside 182-question scope were modified!")

        # 4. Total and remaining counts
        cursor.execute("SELECT COUNT(*) FROM staging_questions;")
        total_questions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM staging_gaps;")
        total_gaps = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM staging_options;")
        total_options = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NULL;")
        report["remaining_unanswered_gaps"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NULL;")
        report["remaining_unanswered_options"] = cursor.fetchone()[0]

        report["remaining_unanswered_questions"] = total_questions - report["matched_questions"]

        if report["validation_errors"]:
            logger.error(f"Validation failed with {len(report['validation_errors'])} errors. Rolling back transaction.")
            cursor.execute("ROLLBACK;")
            raise RuntimeError(f"Merge aborted due to validation errors: {report['validation_errors'][:5]}")

        if dry_run:
            logger.info("Dry run requested — rolling back transaction.")
            cursor.execute("ROLLBACK;")
        else:
            conn.commit()
            logger.info("Checkpoint merge committed successfully.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction rolled back: {e}")
        raise
    finally:
        conn.close()

    return report


def main():
    parser = argparse.ArgumentParser(description="Merge 182-question Gemini checkpoint into staging database.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT, help="Path to checkpoint XLSX")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite staging DB")
    parser.add_argument("--dry-run", action="store_true", help="Validate without committing changes")
    args = parser.parse_args()

    report = merge_checkpoint_into_staging(args.checkpoint, args.db, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("CHECKPOINT MERGE REPORT")
    print("=" * 60)
    for k, v in report.items():
        if k != "validation_errors":
            print(f"  {k}: {v}")
    print(f"  validation_errors_count: {len(report['validation_errors'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
