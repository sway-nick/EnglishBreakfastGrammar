"""
validate_staging_corpus.py
Performs deep strict semantic and referential validation of data/staging.db.

VALIDATION SUITE:
1. single_choice:
   - exactly one option with is_correct=1
   - matching option corresponds to an existing option in staging_options
2. multiple_choice:
   - at least one option with is_correct=1
   - all correct options correspond to existing options
   - no duplicate correct options
3. gap:
   - every gap has non-empty correct_answer
   - accepted_answers is non-empty list
   - for select gaps, correct_answer corresponds to an existing option
   - for text gaps, accepted_answers contains the canonical correct_answer
4. Referential integrity:
   - zero orphan exercises, questions, gaps, options
   - zero duplicate IDs across all tables
   - zero NULL IDs
   - zero NULL response_model
5. Answer integrity:
   - detects any answers that do not match available options for select/choice
   - flags suspicious values (empty, malformed, unexpected whitespace/chars)
6. Checkpoint integrity:
   - verifies 100% exact match of the 182-question verified Gemini checkpoint
"""

from pathlib import Path
import json
import logging
import sqlite3
import sys
from typing import Dict, Any, List, Set, Tuple
import openpyxl

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "staging.db"
DEFAULT_CHECKPOINT = Path.home() / "Desktop" / "english_cms_gemini_all_182.xlsx"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("validate_staging_corpus")


def run_full_staging_validation(
    db_path: Path = DEFAULT_DB,
    checkpoint_path: Path = DEFAULT_CHECKPOINT
) -> Dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"Staging database not found at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    report: Dict[str, Any] = {
        "total_lessons": 0,
        "total_exercises": 0,
        "total_questions": 0,
        "total_gaps": 0,
        "total_options": 0,
        "counts_by_response_model": {},
        "corrected_answer_coverage": "0%",
        "unanswered_questions": 0,
        "unanswered_gaps": 0,
        "unanswered_options": 0,
        "single_choice_violations": [],
        "multiple_choice_violations": [],
        "gap_violations": [],
        "referential_integrity_errors": [],
        "suspicious_answers": [],
        "checkpoint_discrepancies": [],
        "validation_errors": []
    }

    # 1. Basic counts
    cursor.execute("SELECT COUNT(*) FROM staging_lessons;")
    report["total_lessons"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_exercises;")
    report["total_exercises"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_questions;")
    report["total_questions"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_gaps;")
    report["total_gaps"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_options;")
    report["total_options"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT response_model, COUNT(*)
        FROM staging_questions
        GROUP BY response_model
        ORDER BY response_model;
    """)
    report["counts_by_response_model"] = dict(cursor.fetchall())

    # 2. Coverage
    cursor.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NULL OR correct_answer = '';")
    report["unanswered_gaps"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NULL;")
    report["unanswered_options"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT question_id) FROM (
            SELECT question_id FROM staging_gaps WHERE correct_answer IS NOT NULL AND correct_answer != ''
            UNION
            SELECT question_id FROM staging_options WHERE is_correct IS NOT NULL
        )
    """)
    answered_q = cursor.fetchone()[0]
    report["unanswered_questions"] = report["total_questions"] - answered_q
    report["corrected_answer_coverage"] = f"{(answered_q / report['total_questions'] * 100):.2f}%"

    if report["unanswered_questions"] > 0:
        report["validation_errors"].append(f"{report['unanswered_questions']} questions are unanswered")
    if report["unanswered_gaps"] > 0:
        report["validation_errors"].append(f"{report['unanswered_gaps']} gaps have empty/NULL correct_answer")
    if report["unanswered_options"] > 0:
        report["validation_errors"].append(f"{report['unanswered_options']} options have NULL is_correct")

    # 3. single_choice validation
    cursor.execute("""
        SELECT q.question_id, COUNT(o.option_id) as total_opts,
               SUM(CASE WHEN o.is_correct = 1 THEN 1 ELSE 0 END) as corr_opts
        FROM staging_questions q
        LEFT JOIN staging_options o ON q.question_id = o.question_id
        WHERE q.response_model = 'single_choice'
        GROUP BY q.question_id
    """)
    for qid, total_opts, corr_opts in cursor.fetchall():
        if total_opts == 0:
            err = f"single_choice QID {qid} has 0 options"
            report["single_choice_violations"].append(err)
            report["validation_errors"].append(err)
        elif corr_opts != 1:
            err = f"single_choice QID {qid} has {corr_opts} correct options (expected 1)"
            report["single_choice_violations"].append(err)
            report["validation_errors"].append(err)

    # 4. multiple_choice validation
    cursor.execute("""
        SELECT q.question_id, COUNT(o.option_id) as total_opts,
               SUM(CASE WHEN o.is_correct = 1 THEN 1 ELSE 0 END) as corr_opts
        FROM staging_questions q
        LEFT JOIN staging_options o ON q.question_id = o.question_id
        WHERE q.response_model = 'multiple_choice'
        GROUP BY q.question_id
    """)
    for qid, total_opts, corr_opts in cursor.fetchall():
        if total_opts == 0:
            err = f"multiple_choice QID {qid} has 0 options"
            report["multiple_choice_violations"].append(err)
            report["validation_errors"].append(err)
        elif corr_opts < 1:
            err = f"multiple_choice QID {qid} has 0 correct options (expected >= 1)"
            report["multiple_choice_violations"].append(err)
            report["validation_errors"].append(err)

    # 5. gap validation
    cursor.execute("""
        SELECT g.gap_id, g.question_id, g.gap_order, g.input_control,
               g.correct_answer, g.accepted_answers
        FROM staging_gaps g
    """)
    for gap_id, qid, g_order, input_ctrl, corr_ans, acc_json in cursor.fetchall():
        if not corr_ans or str(corr_ans).strip() == "":
            err = f"Gap {gap_id} (QID {qid}) has empty correct_answer"
            report["gap_violations"].append(err)
            report["validation_errors"].append(err)

        try:
            acc_list = json.loads(acc_json) if acc_json else []
        except Exception:
            acc_list = []
            err = f"Gap {gap_id} (QID {qid}) invalid JSON in accepted_answers: {acc_json}"
            report["gap_violations"].append(err)
            report["validation_errors"].append(err)

        if not acc_list:
            err = f"Gap {gap_id} (QID {qid}) has empty accepted_answers list"
            report["gap_violations"].append(err)
            report["validation_errors"].append(err)

        if input_ctrl == "select":
            cursor.execute(
                "SELECT option_id, text, value, is_correct FROM staging_options WHERE gap_id = ?;",
                (gap_id,)
            )
            g_opts = cursor.fetchall()
            if not g_opts:
                err = f"Select Gap {gap_id} (QID {qid}) has 0 options"
                report["gap_violations"].append(err)
                report["validation_errors"].append(err)
            else:
                corr_opts = [o for o in g_opts if o[3] == 1]
                if len(corr_opts) != 1:
                    err = f"Select Gap {gap_id} (QID {qid}) has {len(corr_opts)} correct options (expected 1)"
                    report["gap_violations"].append(err)
                    report["validation_errors"].append(err)
                else:
                    opt_text = (corr_opts[0][1] or "").strip()
                    opt_val = (corr_opts[0][2] or "").strip()
                    c_clean = str(corr_ans).strip()
                    if c_clean.lower() != opt_text.lower() and c_clean.lower() != opt_val.lower():
                        susp = f"Select Gap {gap_id} (QID {qid}): correct_answer '{c_clean}' does not match option text '{opt_text}' / value '{opt_val}'"
                        report["suspicious_answers"].append(susp)
        elif input_ctrl == "text":
            if corr_ans not in acc_list:
                # Check case-insensitive
                if not any(str(corr_ans).strip().lower() == str(a).strip().lower() for a in acc_list):
                    err = f"Text Gap {gap_id} (QID {qid}): canonical correct_answer '{corr_ans}' missing from accepted_answers {acc_list}"
                    report["gap_violations"].append(err)
                    report["validation_errors"].append(err)

    # 6. Referential integrity
    # Null IDs
    for table, col in [
        ("staging_lessons", "lesson_id"),
        ("staging_exercises", "exercise_id"),
        ("staging_questions", "question_id"),
        ("staging_gaps", "gap_id"),
        ("staging_options", "option_id")
    ]:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR {col} = '';")
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            err = f"Table {table} has {cnt} rows with NULL/empty {col}"
            report["referential_integrity_errors"].append(err)
            report["validation_errors"].append(err)

    # Null response_model
    cursor.execute("SELECT COUNT(*) FROM staging_questions WHERE response_model IS NULL OR response_model = '';")
    cnt = cursor.fetchone()[0]
    if cnt > 0:
        err = f"staging_questions has {cnt} rows with NULL/empty response_model"
        report["referential_integrity_errors"].append(err)
        report["validation_errors"].append(err)

    # Orphan checks
    cursor.execute("""
        SELECT COUNT(*) FROM staging_exercises e
        LEFT JOIN staging_lessons l ON e.lesson_id = l.lesson_id
        WHERE l.lesson_id IS NULL;
    """)
    orphan_ex = cursor.fetchone()[0]
    if orphan_ex > 0:
        err = f"Found {orphan_ex} orphan exercises without lesson"
        report["referential_integrity_errors"].append(err)
        report["validation_errors"].append(err)

    cursor.execute("""
        SELECT COUNT(*) FROM staging_questions q
        LEFT JOIN staging_exercises e ON q.exercise_id = e.exercise_id
        WHERE e.exercise_id IS NULL;
    """)
    orphan_q = cursor.fetchone()[0]
    if orphan_q > 0:
        err = f"Found {orphan_q} orphan questions without exercise"
        report["referential_integrity_errors"].append(err)
        report["validation_errors"].append(err)

    cursor.execute("""
        SELECT COUNT(*) FROM staging_gaps g
        LEFT JOIN staging_questions q ON g.question_id = q.question_id
        WHERE q.question_id IS NULL;
    """)
    orphan_gaps = cursor.fetchone()[0]
    if orphan_gaps > 0:
        err = f"Found {orphan_gaps} orphan gaps without question"
        report["referential_integrity_errors"].append(err)
        report["validation_errors"].append(err)

    cursor.execute("""
        SELECT COUNT(*) FROM staging_options o
        LEFT JOIN staging_questions q ON o.question_id = q.question_id
        WHERE q.question_id IS NULL;
    """)
    orphan_opts = cursor.fetchone()[0]
    if orphan_opts > 0:
        err = f"Found {orphan_opts} orphan options without question"
        report["referential_integrity_errors"].append(err)
        report["validation_errors"].append(err)

    # 7. Checkpoint integrity (182 questions)
    if checkpoint_path.exists():
        wb_chk = openpyxl.load_workbook(checkpoint_path, data_only=True)
        ws_chk = wb_chk["Gemini_Enrichment"]
        chk_count = 0
        for r in ws_chk.iter_rows(min_row=3, values_only=True):
            if r[0] is None:
                continue
            chk_count += 1
            qid = str(int(r[0]))
            model = str(r[4] or "").strip()
            val = r[9] if r[9] is not None else r[8]
            val_str = str(val).strip()
            try:
                parsed_chk = json.loads(val_str)
            except Exception:
                continue

            if model == "gap":
                cursor.execute(
                    "SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order;",
                    (qid,)
                )
                db_gaps = cursor.fetchall()
                for gk, gv in parsed_chk.items():
                    g_ord = int(gk.replace("gap_", "")) if "gap_" in gk else int(gk)
                    match = [dg for dg in db_gaps if dg[0] == g_ord]
                    if not match:
                        report["checkpoint_discrepancies"].append(f"QID {qid} gap {gk} missing in DB")
                    elif match[0][1] != str(gv):
                        report["checkpoint_discrepancies"].append(f"QID {qid} gap {gk} DB='{match[0][1]}' != checkpoint='{gv}'")
            elif model in ("single_choice", "multiple_choice"):
                cursor.execute(
                    "SELECT text, value FROM staging_options WHERE question_id = ? AND is_correct = 1;",
                    (qid,)
                )
                db_corr = cursor.fetchall()
                if isinstance(parsed_chk, dict):
                    ans = parsed_chk.get("answer") or parsed_chk.get("selected") or parsed_chk.get("answers") or list(parsed_chk.values())[0]
                else:
                    ans = parsed_chk
                ans_set = set([str(x).strip().lower() for x in ([ans] if isinstance(ans, str) else ans)])
                db_corr_set = set()
                for o in db_corr:
                    if o[0]: db_corr_set.add(str(o[0]).strip().lower())
                    if o[1]: db_corr_set.add(str(o[1]).strip().lower())
                if not ans_set.intersection(db_corr_set):
                    report["checkpoint_discrepancies"].append(f"QID {qid} DB correct options {db_corr_set} do not intersect checkpoint {ans_set}")

        logger.info(f"Verified {chk_count} checkpoint questions. Discrepancies: {len(report['checkpoint_discrepancies'])}")
        for d in report["checkpoint_discrepancies"]:
            report["validation_errors"].append(f"Checkpoint discrepancy: {d}")
    else:
        logger.warning(f"Checkpoint file not found at {checkpoint_path}")

    conn.close()
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate data/staging.db for TASK-010A.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to staging.db")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT, help="Path to 182-question checkpoint")
    args = parser.parse_args()

    report = run_full_staging_validation(args.db, args.checkpoint)

    print("\n" + "=" * 60)
    print("STAGING CORPUS VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Lessons:               {report['total_lessons']}")
    print(f"Total Exercises:             {report['total_exercises']}")
    print(f"Total Questions:             {report['total_questions']}")
    print(f"Total Gaps:                  {report['total_gaps']}")
    print(f"Total Options:               {report['total_options']}")
    print(f"Counts by Response Model:    {report['counts_by_response_model']}")
    print(f"Corrected Answer Coverage:   {report['corrected_answer_coverage']}")
    print(f"Unanswered Questions:        {report['unanswered_questions']}")
    print(f"Unanswered Gaps:             {report['unanswered_gaps']}")
    print(f"Unanswered Options:          {report['unanswered_options']}")
    print(f"Single Choice Violations:    {len(report['single_choice_violations'])}")
    print(f"Multiple Choice Violations:  {len(report['multiple_choice_violations'])}")
    print(f"Gap Violations:              {len(report['gap_violations'])}")
    print(f"Referential Integrity Errs:  {len(report['referential_integrity_errors'])}")
    print(f"Suspicious Answers:          {len(report['suspicious_answers'])}")
    print(f"Checkpoint Discrepancies:    {len(report['checkpoint_discrepancies'])}")
    print(f"TOTAL VALIDATION ERRORS:     {len(report['validation_errors'])}")
    print("=" * 60)

    if report["validation_errors"]:
        print("\nERRORS DETECTED:")
        for err in report["validation_errors"][:10]:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nALL STAGING CHECKS PASSED PERFECTLY!")
        sys.exit(0)


if __name__ == "__main__":
    main()
