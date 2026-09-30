"""
staging_importer.py
Imports preliminary Universal JSON dataset into project SQLite staging database.

Enforces:
1. Strict relational constraints with PRAGMA foreign_keys = ON.
2. Complete data coverage across all 225 topics, 638 exercises, 5,796 questions,
   4,733 gaps, 13,052 options.
3. Stable IDs preservation (zero duplicates, zero orphaned records).
4. Rule 12A unresolved answers: correct_answer=NULL, is_correct=NULL.
5. Full response model preservation (gap=3,674, single_choice=1,957, multiple_choice=165).
"""

from pathlib import Path
import argparse
import datetime
import json
import logging
import sqlite3
import sys
from typing import Dict, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SOURCE = REPO_ROOT / "data" / "cms" / "universal_lessons_preliminary.json"
DEFAULT_DB = REPO_ROOT / "data" / "staging.db"
SCHEMA_PATH = REPO_ROOT / "schemas" / "staging_schema.sql"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("staging_importer")


def init_database(db_path: Path) -> sqlite3.Connection:
    """Connect to SQLite database, enable foreign keys, and run schema DDL."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    
    if SCHEMA_PATH.exists():
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
    else:
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
        
    return conn


def import_corpus_to_staging(source_json_path: Path, db_path: Path) -> Dict[str, Any]:
    """Imports the full preliminary JSON into staging tables inside a single transaction."""
    logger.info(f"Loading source dataset: {source_json_path}")
    with open(source_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lessons = data.get("lessons", [])
    logger.info(f"Found {len(lessons)} lessons to import.")

    conn = init_database(db_path)
    cursor = conn.cursor()

    import_id = f"import_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    imported_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        cursor.execute("BEGIN TRANSACTION;")

        # Clear existing staging records to ensure clean idempotent staging state
        cursor.execute("DELETE FROM staging_options;")
        cursor.execute("DELETE FROM staging_gaps;")
        cursor.execute("DELETE FROM staging_questions;")
        cursor.execute("DELETE FROM staging_exercises;")
        cursor.execute("DELETE FROM staging_lessons;")
        cursor.execute("DELETE FROM staging_import_runs;")

        topics_count = 0
        exercises_count = 0
        questions_count = 0
        gaps_count = 0
        options_count = 0

        for lesson in lessons:
            lesson_id = lesson["lesson_id"]
            title = lesson.get("title", "")
            level = lesson.get("level", "")
            topic = lesson.get("topic", "")
            desc = lesson.get("description", "")
            source_info = lesson.get("source", {})
            source_provider = source_info.get("provider", "Test-English")
            source_url = source_info.get("source_url", "")
            pages = lesson.get("pages", [])

            cursor.execute("""
                INSERT INTO staging_lessons (
                    lesson_id, title, level, topic, status, description,
                    source_provider, source_url, pages_count
                ) VALUES (?, ?, ?, ?, 'staging', ?, ?, ?, ?)
            """, (
                lesson_id, title, level, topic, desc,
                source_provider, source_url, len(pages)
            ))
            topics_count += 1

            for page_obj in pages:
                page_num = page_obj.get("page", 1)
                source_file = page_obj.get("source_file", "")
                page_source_url = page_obj.get("source_url", "")

                for ex in page_obj.get("exercises", []):
                    exercise_id = ex["exercise_id"]
                    ex_title = ex.get("title", "")
                    ex_instruction = ex.get("instruction", "")
                    ex_order = ex.get("order", 1)
                    example_obj = ex.get("example") or {}
                    ex_src = example_obj.get("source", "")
                    ex_tgt = example_obj.get("target", "")

                    cursor.execute("""
                        INSERT INTO staging_exercises (
                            exercise_id, lesson_id, page, exercise_order, title,
                            instruction, example_source, example_target, status,
                            source_file, source_url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'staging', ?, ?)
                    """, (
                        exercise_id, lesson_id, page_num, ex_order, ex_title,
                        ex_instruction, ex_src, ex_tgt, source_file, page_source_url
                    ))
                    exercises_count += 1

                    for q in ex.get("questions", []):
                        question_id = q["question_id"]
                        q_order = q.get("order", 1)
                        response_model = q.get("response_model", "")
                        content = q.get("content", "")

                        cursor.execute("""
                            INSERT INTO staging_questions (
                                question_id, exercise_id, lesson_id, question_order,
                                response_model, content, explanation, difficulty, status
                            ) VALUES (?, ?, ?, ?, ?, ?, '', '', 'staging')
                        """, (
                            question_id, exercise_id, lesson_id, q_order,
                            response_model, content
                        ))
                        questions_count += 1

                        # Question options (single_choice, multiple_choice)
                        for opt_idx, opt in enumerate(q.get("options", []), start=1):
                            opt_id = opt.get("option_id", f"{question_id}_{opt_idx}")
                            opt_order = opt.get("order", opt_idx)
                            opt_text = opt.get("text", "")
                            opt_val = opt.get("value", "")

                            cursor.execute("""
                                INSERT INTO staging_options (
                                    option_id, question_id, gap_id, option_order,
                                    text, value, is_correct
                                ) VALUES (?, ?, NULL, ?, ?, ?, NULL)
                            """, (
                                opt_id, question_id, opt_order, opt_text, opt_val
                            ))
                            options_count += 1

                        # Gaps
                        for gap_idx, gap in enumerate(q.get("gaps", []), start=1):
                            gap_id = gap["gap_id"]
                            gap_order = gap.get("gap_order", gap_idx)
                            input_control = gap.get("input_control", "text")
                            accepted = json.dumps(gap.get("accepted_answers", []))

                            cursor.execute("""
                                INSERT INTO staging_gaps (
                                    gap_id, question_id, gap_order, input_control,
                                    correct_answer, accepted_answers, case_sensitive,
                                    feedback_correct, feedback_incorrect
                                ) VALUES (?, ?, ?, ?, NULL, ?, 0, '', '')
                            """, (
                                gap_id, question_id, gap_order, input_control, accepted
                            ))
                            gaps_count += 1

                            # Gap options (select)
                            for g_opt_idx, g_opt in enumerate(gap.get("options", []), start=1):
                                g_opt_id = g_opt.get("option_id", f"{gap_id}_{g_opt_idx}")
                                g_opt_order = g_opt.get("order", g_opt_idx)
                                g_opt_text = g_opt.get("text", "")
                                g_opt_val = g_opt.get("value", "")

                                cursor.execute("""
                                    INSERT INTO staging_options (
                                        option_id, question_id, gap_id, option_order,
                                        text, value, is_correct
                                    ) VALUES (?, ?, ?, ?, ?, ?, NULL)
                                """, (
                                    g_opt_id, question_id, gap_id, g_opt_order,
                                    g_opt_text, g_opt_val
                                ))
                                options_count += 1

        # Record import run metadata
        cursor.execute("""
            INSERT INTO staging_import_runs (
                import_id, imported_at, source_file, topics_count,
                exercises_count, questions_count, gaps_count, options_count, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
        """, (
            import_id, imported_at, str(source_json_path), topics_count,
            exercises_count, questions_count, gaps_count, options_count
        ))

        conn.commit()
        logger.info("Import transaction committed successfully.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Import failed, rolled back: {e}")
        raise
    finally:
        conn.close()

    # Verify after import
    return verify_staging_database(db_path)


def verify_staging_database(db_path: Path) -> Dict[str, Any]:
    """Runs strict relational, model, and count validation on the staging database."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    report: Dict[str, Any] = {}

    # 1. Total counts
    cursor.execute("SELECT COUNT(*) FROM staging_lessons;")
    report["total_topics"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_exercises;")
    report["total_exercises"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_questions;")
    report["total_questions"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_gaps;")
    report["total_gaps"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_options;")
    report["total_options"] = cursor.fetchone()[0]

    # 2. Response models breakdown
    cursor.execute("""
        SELECT response_model, COUNT(*)
        FROM staging_questions
        GROUP BY response_model
    """)
    report["response_models"] = dict(cursor.fetchall())

    # 3. Orphan checks (foreign key integrity)
    cursor.execute("""
        SELECT COUNT(*) FROM staging_exercises
        WHERE lesson_id NOT IN (SELECT lesson_id FROM staging_lessons);
    """)
    report["orphaned_exercises"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM staging_questions
        WHERE exercise_id NOT IN (SELECT exercise_id FROM staging_exercises)
           OR lesson_id NOT IN (SELECT lesson_id FROM staging_lessons);
    """)
    report["orphaned_questions"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM staging_gaps
        WHERE question_id NOT IN (SELECT question_id FROM staging_questions);
    """)
    report["orphaned_gaps"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM staging_options
        WHERE question_id NOT IN (SELECT question_id FROM staging_questions);
    """)
    report["orphaned_options_q"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM staging_options
        WHERE gap_id IS NOT NULL AND gap_id NOT IN (SELECT gap_id FROM staging_gaps);
    """)
    report["orphaned_options_gap"] = cursor.fetchone()[0]

    report["total_orphans"] = (
        report["orphaned_exercises"] +
        report["orphaned_questions"] +
        report["orphaned_gaps"] +
        report["orphaned_options_q"] +
        report["orphaned_options_gap"]
    )

    # 4. Duplicate checks
    for table, col in [
        ("staging_lessons", "lesson_id"),
        ("staging_exercises", "exercise_id"),
        ("staging_questions", "question_id"),
        ("staging_gaps", "gap_id"),
        ("staging_options", "option_id")
    ]:
        cursor.execute(f"SELECT {col}, COUNT(*) FROM {table} GROUP BY {col} HAVING COUNT(*) > 1;")
        dups = cursor.fetchall()
        report[f"duplicate_{col}"] = len(dups)

    report["total_duplicates"] = sum(
        report[f"duplicate_{col}"] for col in [
            "lesson_id", "exercise_id", "question_id", "gap_id", "option_id"
        ]
    )

    # 5. Rule 12A unresolved answers check
    cursor.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NOT NULL;")
    report["resolved_gaps"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NOT NULL;")
    report["resolved_options"] = cursor.fetchone()[0]

    report["unresolved_answers_count"] = (
        (report["total_gaps"] - report["resolved_gaps"]) +
        (report["total_options"] - report["resolved_options"])
    )

    # 6. Status check (all staging)
    cursor.execute("SELECT COUNT(*) FROM staging_lessons WHERE status != 'staging';")
    report["non_staging_lessons"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging_questions WHERE status != 'staging';")
    report["non_staging_questions"] = cursor.fetchone()[0]

    conn.close()
    return report


def main():
    parser = argparse.ArgumentParser(description="Import preliminary corpus into SQLite staging database.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Path to preliminary Universal JSON")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing database without re-importing")
    args = parser.parse_args()

    if args.verify_only:
        report = verify_staging_database(args.db)
    else:
        report = import_corpus_to_staging(args.source, args.db)

    print("\n" + "=" * 60)
    print("STAGING DATABASE VERIFICATION REPORT")
    print("=" * 60)
    for k, v in report.items():
        print(f"  {k}: {v}")
    print("=" * 60)

    # Assertions for script exit code
    assert report["total_topics"] == 225, f"Expected 225 topics, got {report['total_topics']}"
    assert report["total_exercises"] == 638, f"Expected 638 exercises, got {report['total_exercises']}"
    assert report["total_questions"] == 5796, f"Expected 5,796 questions, got {report['total_questions']}"
    assert report["total_gaps"] == 4733, f"Expected 4,733 gaps, got {report['total_gaps']}"
    assert report["total_options"] == 13052, f"Expected 13,052 options, got {report['total_options']}"
    assert report["total_orphans"] == 0, f"Found {report['total_orphans']} orphaned references"
    assert report["total_duplicates"] == 0, f"Found {report['total_duplicates']} duplicate IDs"
    assert report["response_models"] == {"gap": 3674, "single_choice": 1957, "multiple_choice": 165}
    print("ALL STAGING ASSERTIONS PASSED!\n")


if __name__ == "__main__":
    main()
