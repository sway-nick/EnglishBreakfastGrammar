"""Adaptation Database & Queue Manager (TASK-011B)

Universal English Test Platform
Manages the adaptation database (data/adaptation.db) according to
schemas/adaptation_schema.sql and docs/TASK-010B_ADAPTATION_SPEC.md.

Enforces:
1. Total isolation from source/staging tables (data/staging.db remains immutable).
2. Bidirectional traceability (source_*_id mapped to adapted_*_id).
3. PRAGMA foreign_keys = ON with full referential integrity.
4. Idempotent queue population (no duplicates or overwrites of existing adaptations).
5. Queue status tracking and integrity verification.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_ADAPTATION_DB = Path("data/adaptation.db")
DEFAULT_STAGING_DB = Path("data/staging.db")
DEFAULT_SCHEMA_PATH = Path("schemas/adaptation_schema.sql")


def get_connection(db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB) -> sqlite3.Connection:
    """Connect to SQLite database and enforce foreign keys."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(
    db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    schema_path: Union[str, Path] = DEFAULT_SCHEMA_PATH,
) -> bool:
    """Initialize the adaptation database with the canonical DDL schema."""
    target_path = Path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise FileNotFoundError(f"Adaptation schema not found at: {schema_file}")

    with open(schema_file, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    conn = get_connection(target_path)
    try:
        conn.executescript(ddl_script)
        conn.commit()
    finally:
        conn.close()

    return True


def populate_queue(
    staging_db_path: Union[str, Path] = DEFAULT_STAGING_DB,
    adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    target_level: Optional[str] = None,
    run_id: Optional[str] = None,
    model_name: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Populate the adaptation queue from the staging corpus idempotently.

    Existing items are never overwritten.
    """
    staging_path = Path(staging_db_path)
    adaptation_path = Path(adaptation_db_path)

    if not staging_path.exists():
        raise FileNotFoundError(f"Staging database not found at: {staging_path}")
    if not adaptation_path.exists():
        raise FileNotFoundError(f"Adaptation database not found at: {adaptation_path}. Run init first.")

    # Connect to staging read-only
    staging_conn = sqlite3.connect(f"file:{staging_path.resolve()}?mode=ro", uri=True)
    staging_conn.row_factory = sqlite3.Row
    adapt_conn = get_connection(adaptation_path)

    stats = {
        "lessons_inserted": 0,
        "lessons_skipped": 0,
        "exercises_inserted": 0,
        "exercises_skipped": 0,
        "questions_inserted": 0,
        "questions_skipped": 0,
        "gaps_inserted": 0,
        "gaps_skipped": 0,
        "options_inserted": 0,
        "options_skipped": 0,
        "target_level": target_level or "ALL",
        "run_id": run_id,
    }

    try:
        # 1. Fetch staging lessons
        level_filter = ""
        params: List[Any] = []
        if target_level and target_level.upper() != "ALL":
            level_filter = "WHERE level = ?"
            params.append(target_level)

        staging_lessons = staging_conn.execute(
            f"SELECT lesson_id, title, level, topic, description FROM staging_lessons {level_filter} ORDER BY lesson_id",
            params,
        ).fetchall()

        lesson_ids = [row["lesson_id"] for row in staging_lessons]
        if not lesson_ids:
            return stats

        # 2. Populate adapted_lessons
        with adapt_conn:
            for l_row in staging_lessons:
                adapted_id = f"adapt_{l_row['lesson_id']}"
                cur = adapt_conn.execute(
                    """
                    INSERT OR IGNORE INTO adapted_lessons (
                        adapted_lesson_id, source_lesson_id, title, level, topic, description,
                        adaptation_status, review_required
                    ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', 0)
                    """,
                    (
                        adapted_id,
                        l_row["lesson_id"],
                        l_row["title"],
                        l_row["level"],
                        l_row["topic"],
                        l_row["description"],
                    ),
                )
                if cur.rowcount > 0:
                    stats["lessons_inserted"] += 1
                else:
                    stats["lessons_skipped"] += 1

        # 3. Populate adapted_exercises for these lessons
        placeholders = ",".join("?" for _ in lesson_ids)
        staging_exercises = staging_conn.execute(
            f"""
            SELECT exercise_id, lesson_id, exercise_order, page, title, instruction,
                   example_source, example_target
            FROM staging_exercises
            WHERE lesson_id IN ({placeholders})
            ORDER BY lesson_id, exercise_order
            """,
            lesson_ids,
        ).fetchall()

        exercise_ids = [row["exercise_id"] for row in staging_exercises]

        with adapt_conn:
            for ex_row in staging_exercises:
                adapted_ex_id = f"adapt_{ex_row['exercise_id']}"
                adapted_lesson_id = f"adapt_{ex_row['lesson_id']}"
                cur = adapt_conn.execute(
                    """
                    INSERT OR IGNORE INTO adapted_exercises (
                        adapted_exercise_id, source_exercise_id, adapted_lesson_id,
                        exercise_order, page, title, instruction, example_source, example_target,
                        adaptation_status, review_required
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0)
                    """,
                    (
                        adapted_ex_id,
                        ex_row["exercise_id"],
                        adapted_lesson_id,
                        ex_row["exercise_order"],
                        ex_row["page"] or 1,
                        ex_row["title"],
                        ex_row["instruction"],
                        ex_row["example_source"],
                        ex_row["example_target"],
                    ),
                )
                if cur.rowcount > 0:
                    stats["exercises_inserted"] += 1
                else:
                    stats["exercises_skipped"] += 1

        # 4. Populate adapted_questions
        staging_questions = staging_conn.execute(
            f"""
            SELECT question_id, exercise_id, lesson_id, question_order, response_model,
                   content, explanation, difficulty
            FROM staging_questions
            WHERE lesson_id IN ({placeholders})
            ORDER BY lesson_id, exercise_id, question_order
            """,
            lesson_ids,
        ).fetchall()

        question_ids = [row["question_id"] for row in staging_questions]

        with adapt_conn:
            for q_row in staging_questions:
                adapted_q_id = f"adapt_{q_row['question_id']}"
                adapted_ex_id = f"adapt_{q_row['exercise_id']}"
                adapted_lesson_id = f"adapt_{q_row['lesson_id']}"
                cur = adapt_conn.execute(
                    """
                    INSERT OR IGNORE INTO adapted_questions (
                        adapted_question_id, source_question_id, adapted_exercise_id, adapted_lesson_id,
                        question_order, response_model, source_text, adapted_text, explanation, difficulty,
                        similarity_score, adaptation_status, review_required
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, NULL, 'PENDING', 0)
                    """,
                    (
                        adapted_q_id,
                        q_row["question_id"],
                        adapted_ex_id,
                        adapted_lesson_id,
                        q_row["question_order"],
                        q_row["response_model"],
                        q_row["content"],
                        q_row["explanation"],
                        q_row["difficulty"],
                    ),
                )
                if cur.rowcount > 0:
                    stats["questions_inserted"] += 1
                else:
                    stats["questions_skipped"] += 1

        # 5. Populate adapted_gaps
        # To avoid query parameter limits on very large sets, chunk question_ids
        def chunked_iterable(iterable: List[Any], size: int = 900):
            for i in range(0, len(iterable), size):
                yield iterable[i : i + size]

        staging_gaps: List[sqlite3.Row] = []
        for q_chunk in chunked_iterable(question_ids, 800):
            q_placeholders = ",".join("?" for _ in q_chunk)
            gaps_chunk = staging_conn.execute(
                f"""
                SELECT gap_id, question_id, gap_order, input_control, correct_answer,
                       accepted_answers, case_sensitive
                FROM staging_gaps
                WHERE question_id IN ({q_placeholders})
                ORDER BY question_id, gap_order
                """,
                q_chunk,
            ).fetchall()
            staging_gaps.extend(gaps_chunk)

        with adapt_conn:
            for g_row in staging_gaps:
                adapted_g_id = f"adapt_{g_row['gap_id']}"
                adapted_q_id = f"adapt_{g_row['question_id']}"
                cur = adapt_conn.execute(
                    """
                    INSERT OR IGNORE INTO adapted_gaps (
                        adapted_gap_id, source_gap_id, adapted_question_id, gap_order,
                        input_control, source_correct_answer, adapted_correct_answer,
                        source_accepted_answers, adapted_accepted_answers, case_sensitive,
                        review_required
                    ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?, 0)
                    """,
                    (
                        adapted_g_id,
                        g_row["gap_id"],
                        adapted_q_id,
                        g_row["gap_order"],
                        g_row["input_control"],
                        g_row["correct_answer"],
                        g_row["accepted_answers"],
                        g_row["case_sensitive"] or 0,
                    ),
                )
                if cur.rowcount > 0:
                    stats["gaps_inserted"] += 1
                else:
                    stats["gaps_skipped"] += 1

        # 6. Populate adapted_options
        staging_options: List[sqlite3.Row] = []
        for q_chunk in chunked_iterable(question_ids, 800):
            q_placeholders = ",".join("?" for _ in q_chunk)
            opts_chunk = staging_conn.execute(
                f"""
                SELECT option_id, question_id, gap_id, option_order, text, value, is_correct
                FROM staging_options
                WHERE question_id IN ({q_placeholders})
                ORDER BY question_id, option_order
                """,
                q_chunk,
            ).fetchall()
            staging_options.extend(opts_chunk)

        with adapt_conn:
            for opt_row in staging_options:
                adapted_opt_id = f"adapt_{opt_row['option_id']}"
                adapted_q_id = f"adapt_{opt_row['question_id']}"
                adapted_g_id = f"adapt_{opt_row['gap_id']}" if opt_row["gap_id"] else None

                cur = adapt_conn.execute(
                    """
                    INSERT OR IGNORE INTO adapted_options (
                        adapted_option_id, source_option_id, adapted_question_id, adapted_gap_id,
                        option_order, source_text, adapted_text, source_value, adapted_value,
                        source_is_correct, adapted_is_correct, review_required
                    ) VALUES (?, ?, ?, ?, ?, ?, '', ?, NULL, ?, ?, 0)
                    """,
                    (
                        adapted_opt_id,
                        opt_row["option_id"],
                        adapted_q_id,
                        adapted_g_id,
                        opt_row["option_order"],
                        opt_row["text"] or "",
                        opt_row["value"],
                        opt_row["is_correct"] or 0,
                        opt_row["is_correct"] or 0,
                    ),
                )
                if cur.rowcount > 0:
                    stats["options_inserted"] += 1
                else:
                    stats["options_skipped"] += 1

        # 7. Record run if requested
        if run_id:
            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with adapt_conn:
                adapt_conn.execute(
                    """
                    INSERT OR REPLACE INTO adaptation_runs (
                        run_id, started_at, model_name, target_level, status,
                        total_items, generated_count, validated_count, rejected_count, notes
                    ) VALUES (?, ?, ?, ?, 'in_progress', ?, 0, 0, 0, ?)
                    """,
                    (
                        run_id,
                        now_str,
                        model_name or "pending_assignment",
                        target_level or "ALL",
                        stats["questions_inserted"],
                        notes or "Queue initialized",
                    ),
                )

    finally:
        staging_conn.close()
        adapt_conn.close()

    return stats


def get_status(adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB) -> Dict[str, Any]:
    """Retrieve counts and status breakdown of the adaptation database."""
    target_path = Path(adaptation_db_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Adaptation database not found at: {target_path}")

    conn = get_connection(target_path)
    status_report: Dict[str, Any] = {}

    try:
        # Table counts
        table_counts = {}
        for tbl in ["adapted_lessons", "adapted_exercises", "adapted_questions", "adapted_gaps", "adapted_options"]:
            cur = conn.execute(f"SELECT COUNT(*) FROM {tbl}")
            table_counts[tbl] = cur.fetchone()[0]
        status_report["table_counts"] = table_counts

        # Question status breakdown
        status_counts = {}
        cur = conn.execute(
            """
            SELECT adaptation_status, COUNT(*) as cnt
            FROM adapted_questions
            GROUP BY adaptation_status
            ORDER BY cnt DESC
            """
        )
        for row in cur.fetchall():
            status_counts[row["adaptation_status"]] = row["cnt"]
        status_report["question_statuses"] = status_counts

        # Question level breakdown
        level_counts = {}
        cur = conn.execute(
            """
            SELECT l.level, COUNT(q.adapted_question_id) as cnt
            FROM adapted_questions q
            JOIN adapted_lessons l ON q.adapted_lesson_id = l.adapted_lesson_id
            GROUP BY l.level
            ORDER BY l.level
            """
        )
        for row in cur.fetchall():
            level_counts[row["level"]] = row["cnt"]
        status_report["questions_by_level"] = level_counts

        # Question response_model breakdown
        model_counts = {}
        cur = conn.execute(
            """
            SELECT response_model, COUNT(*) as cnt
            FROM adapted_questions
            GROUP BY response_model
            ORDER BY cnt DESC
            """
        )
        for row in cur.fetchall():
            model_counts[row["response_model"]] = row["cnt"]
        status_report["questions_by_response_model"] = model_counts

        # Review required counts
        cur = conn.execute("SELECT COUNT(*) FROM adapted_questions WHERE review_required = 1")
        status_report["questions_review_required"] = cur.fetchone()[0]

        # Recent runs
        cur = conn.execute(
            """
            SELECT run_id, started_at, completed_at, model_name, target_level, status,
                   total_items, generated_count, validated_count, rejected_count
            FROM adaptation_runs
            ORDER BY started_at DESC
            LIMIT 10
            """
        )
        status_report["recent_runs"] = [dict(row) for row in cur.fetchall()]

    finally:
        conn.close()

    return status_report


def verify_integrity(
    adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    staging_db_path: Union[str, Path] = DEFAULT_STAGING_DB,
) -> Dict[str, Any]:
    """Verify referential integrity, lack of orphans, and source consistency."""
    target_path = Path(adaptation_db_path)
    staging_path = Path(staging_db_path)

    if not target_path.exists():
        raise FileNotFoundError(f"Adaptation DB not found: {target_path}")
    if not staging_path.exists():
        raise FileNotFoundError(f"Staging DB not found: {staging_path}")

    adapt_conn = get_connection(target_path)
    staging_conn = sqlite3.connect(f"file:{staging_path.resolve()}?mode=ro", uri=True)

    verification = {
        "foreign_key_violations": 0,
        "orphan_exercises": 0,
        "orphan_questions": 0,
        "orphan_gaps": 0,
        "orphan_options": 0,
        "orphan_options_gap_fk": 0,
        "unmatched_source_lessons": 0,
        "unmatched_source_exercises": 0,
        "unmatched_source_questions": 0,
        "unmatched_source_gaps": 0,
        "unmatched_source_options": 0,
        "duplicate_source_questions": 0,
        "is_valid": True,
        "errors": [],
    }

    try:
        # 1. PRAGMA foreign_key_check
        fk_checks = adapt_conn.execute("PRAGMA foreign_key_check").fetchall()
        verification["foreign_key_violations"] = len(fk_checks)
        if fk_checks:
            for fk in fk_checks:
                verification["errors"].append(f"Foreign key violation: table={fk[0]}, rowid={fk[1]}, parent={fk[2]}")

        # 2. Direct orphan checks
        orphan_ex = adapt_conn.execute(
            """
            SELECT COUNT(*) FROM adapted_exercises
            WHERE adapted_lesson_id NOT IN (SELECT adapted_lesson_id FROM adapted_lessons)
            """
        ).fetchone()[0]
        verification["orphan_exercises"] = orphan_ex

        orphan_q = adapt_conn.execute(
            """
            SELECT COUNT(*) FROM adapted_questions
            WHERE adapted_exercise_id NOT IN (SELECT adapted_exercise_id FROM adapted_exercises)
               OR adapted_lesson_id NOT IN (SELECT adapted_lesson_id FROM adapted_lessons)
            """
        ).fetchone()[0]
        verification["orphan_questions"] = orphan_q

        orphan_g = adapt_conn.execute(
            """
            SELECT COUNT(*) FROM adapted_gaps
            WHERE adapted_question_id NOT IN (SELECT adapted_question_id FROM adapted_questions)
            """
        ).fetchone()[0]
        verification["orphan_gaps"] = orphan_g

        orphan_opt = adapt_conn.execute(
            """
            SELECT COUNT(*) FROM adapted_options
            WHERE adapted_question_id NOT IN (SELECT adapted_question_id FROM adapted_questions)
            """
        ).fetchone()[0]
        verification["orphan_options"] = orphan_opt

        orphan_opt_gap = adapt_conn.execute(
            """
            SELECT COUNT(*) FROM adapted_options
            WHERE adapted_gap_id IS NOT NULL
              AND adapted_gap_id NOT IN (SELECT adapted_gap_id FROM adapted_gaps)
            """
        ).fetchone()[0]
        verification["orphan_options_gap_fk"] = orphan_opt_gap

        # 3. Check for duplicates in source IDs
        dup_q = adapt_conn.execute(
            """
            SELECT source_question_id, COUNT(*) as cnt
            FROM adapted_questions
            GROUP BY source_question_id
            HAVING cnt > 1
            """
        ).fetchall()
        verification["duplicate_source_questions"] = len(dup_q)

        # 4. Check that all source IDs exist in staging
        # Lesson sources
        adapt_l_sources = set(r[0] for r in adapt_conn.execute("SELECT source_lesson_id FROM adapted_lessons"))
        stage_l_ids = set(r[0] for r in staging_conn.execute("SELECT lesson_id FROM staging_lessons"))
        verification["unmatched_source_lessons"] = len(adapt_l_sources - stage_l_ids)

        # Exercise sources
        adapt_ex_sources = set(r[0] for r in adapt_conn.execute("SELECT source_exercise_id FROM adapted_exercises"))
        stage_ex_ids = set(r[0] for r in staging_conn.execute("SELECT exercise_id FROM staging_exercises"))
        verification["unmatched_source_exercises"] = len(adapt_ex_sources - stage_ex_ids)

        # Question sources
        adapt_q_sources = set(r[0] for r in adapt_conn.execute("SELECT source_question_id FROM adapted_questions"))
        stage_q_ids = set(r[0] for r in staging_conn.execute("SELECT question_id FROM staging_questions"))
        verification["unmatched_source_questions"] = len(adapt_q_sources - stage_q_ids)

        # Gap sources
        adapt_g_sources = set(r[0] for r in adapt_conn.execute("SELECT source_gap_id FROM adapted_gaps"))
        stage_g_ids = set(r[0] for r in staging_conn.execute("SELECT gap_id FROM staging_gaps"))
        verification["unmatched_source_gaps"] = len(adapt_g_sources - stage_g_ids)

        # Option sources
        adapt_opt_sources = set(r[0] for r in adapt_conn.execute("SELECT source_option_id FROM adapted_options"))
        stage_opt_ids = set(r[0] for r in staging_conn.execute("SELECT option_id FROM staging_options"))
        verification["unmatched_source_options"] = len(adapt_opt_sources - stage_opt_ids)

        # Summary decision
        has_errors = (
            verification["foreign_key_violations"] > 0
            or verification["orphan_exercises"] > 0
            or verification["orphan_questions"] > 0
            or verification["orphan_gaps"] > 0
            or verification["orphan_options"] > 0
            or verification["orphan_options_gap_fk"] > 0
            or verification["unmatched_source_lessons"] > 0
            or verification["unmatched_source_exercises"] > 0
            or verification["unmatched_source_questions"] > 0
            or verification["unmatched_source_gaps"] > 0
            or verification["unmatched_source_options"] > 0
            or verification["duplicate_source_questions"] > 0
        )
        verification["is_valid"] = not has_errors

    finally:
        adapt_conn.close()
        staging_conn.close()

    return verification


def reset_queue(
    adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    level: Optional[str] = None,
    reset_all: bool = False,
) -> int:
    """Reset question and gap adaptations back to PENDING.

    Clears generated text, scores, and resets statuses to PENDING.
    """
    target_path = Path(adaptation_db_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Adaptation DB not found: {target_path}")

    conn = get_connection(target_path)
    count_reset = 0

    try:
        with conn:
            if level and level.upper() != "ALL":
                # Find matching question IDs
                cur = conn.execute(
                    """
                    SELECT q.adapted_question_id
                    FROM adapted_questions q
                    JOIN adapted_lessons l ON q.adapted_lesson_id = l.adapted_lesson_id
                    WHERE l.level = ?
                    """,
                    (level,),
                )
                q_ids = [row["adapted_question_id"] for row in cur.fetchall()]
                count_reset = len(q_ids)

                for i in range(0, len(q_ids), 800):
                    chunk = q_ids[i : i + 800]
                    placeholders = ",".join("?" for _ in chunk)
                    conn.execute(
                        f"""
                        UPDATE adapted_questions
                        SET adapted_text = NULL,
                            similarity_score = NULL,
                            adaptation_status = 'PENDING',
                            review_required = 0,
                            adaptation_notes = NULL,
                            adapted_by = NULL,
                            adapted_at = NULL
                        WHERE adapted_question_id IN ({placeholders})
                        """,
                        chunk,
                    )
                    conn.execute(
                        f"""
                        UPDATE adapted_gaps
                        SET adapted_correct_answer = NULL,
                            adapted_accepted_answers = NULL,
                            review_required = 0,
                            adaptation_notes = NULL
                        WHERE adapted_question_id IN ({placeholders})
                        """,
                        chunk,
                    )
                    conn.execute(
                        f"""
                        UPDATE adapted_options
                        SET adapted_text = '',
                            adapted_value = NULL,
                            review_required = 0,
                            adaptation_notes = NULL
                        WHERE adapted_question_id IN ({placeholders})
                        """,
                        chunk,
                    )
            elif reset_all:
                cur = conn.execute("SELECT COUNT(*) FROM adapted_questions")
                count_reset = cur.fetchone()[0]

                conn.execute(
                    """
                    UPDATE adapted_questions
                    SET adapted_text = NULL,
                        similarity_score = NULL,
                        adaptation_status = 'PENDING',
                        review_required = 0,
                        adaptation_notes = NULL,
                        adapted_by = NULL,
                        adapted_at = NULL
                    """
                )
                conn.execute(
                    """
                    UPDATE adapted_gaps
                    SET adapted_correct_answer = NULL,
                        adapted_accepted_answers = NULL,
                        review_required = 0,
                        adaptation_notes = NULL
                    """
                )
                conn.execute(
                    """
                    UPDATE adapted_options
                    SET adapted_text = '',
                        adapted_value = NULL,
                        review_required = 0,
                        adaptation_notes = NULL
                    """
                )
    finally:
        conn.close()

    return count_reset


def print_status(status_report: Dict[str, Any]) -> None:
    """Pretty-print the status report."""
    print("=" * 65)
    print(" ADAPTATION DATABASE & QUEUE STATUS")
    print("=" * 65)

    print("\n[TABLE TOTALS]")
    for tbl, cnt in status_report["table_counts"].items():
        print(f"  {tbl:<25}: {cnt:>6,}")

    print("\n[QUESTION STATUS BREAKDOWN]")
    for st, cnt in status_report["question_statuses"].items():
        print(f"  {st:<20}: {cnt:>6,}")

    print(f"\n[REVIEW REQUIRED] : {status_report['questions_review_required']}")

    print("\n[QUESTIONS BY LEVEL]")
    for lvl, cnt in status_report["questions_by_level"].items():
        print(f"  {lvl:<10}: {cnt:>6,}")

    print("\n[QUESTIONS BY RESPONSE MODEL]")
    for rm, cnt in status_report["questions_by_response_model"].items():
        print(f"  {rm:<20}: {cnt:>6,}")

    if status_report["recent_runs"]:
        print("\n[RECENT ADAPTATION RUNS]")
        for r in status_report["recent_runs"]:
            print(
                f"  Run ID: {r['run_id']} | Level: {r['target_level']} | Model: {r['model_name']} | Status: {r['status']} | Items: {r['total_items']}"
            )
    print("=" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(description="Adaptation Database & Queue Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize adaptation database from schema")
    p_init.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    p_init.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Path to adaptation_schema.sql")

    # populate
    p_pop = subparsers.add_parser("populate", help="Populate adaptation queue from staging database")
    p_pop.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    p_pop.add_argument("--staging", default=str(DEFAULT_STAGING_DB), help="Path to staging.db")
    p_pop.add_argument("--level", default=None, help="Filter by CEFR level (e.g. A1, B1, etc.) or ALL")
    p_pop.add_argument("--run-id", default=None, help="Optional run identifier to record in adaptation_runs")
    p_pop.add_argument("--model", default=None, help="Model name for run record")
    p_pop.add_argument("--notes", default=None, help="Notes for run record")

    # status
    p_stat = subparsers.add_parser("status", help="Show queue status and metrics")
    p_stat.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")

    # verify
    p_ver = subparsers.add_parser("verify", help="Verify referential integrity and source mapping")
    p_ver.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    p_ver.add_argument("--staging", default=str(DEFAULT_STAGING_DB), help="Path to staging.db")

    # reset
    p_rst = subparsers.add_parser("reset", help="Reset questions back to PENDING")
    p_rst.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    p_rst.add_argument("--level", default=None, help="Reset only specific CEFR level")
    p_rst.add_argument("--all", action="store_true", help="Reset all questions")

    args = parser.parse_args()

    if args.command == "init":
        init_db(args.db, args.schema)
        print(f"Successfully initialized adaptation database at {args.db}")

    elif args.command == "populate":
        stats = populate_queue(
            staging_db_path=args.staging,
            adaptation_db_path=args.db,
            target_level=args.level,
            run_id=args.run_id,
            model_name=args.model,
            notes=args.notes,
        )
        print("Queue population finished:")
        print(f"  Target level       : {stats['target_level']}")
        print(f"  Lessons inserted   : {stats['lessons_inserted']} (skipped: {stats['lessons_skipped']})")
        print(f"  Exercises inserted : {stats['exercises_inserted']} (skipped: {stats['exercises_skipped']})")
        print(f"  Questions inserted : {stats['questions_inserted']} (skipped: {stats['questions_skipped']})")
        print(f"  Gaps inserted      : {stats['gaps_inserted']} (skipped: {stats['gaps_skipped']})")
        print(f"  Options inserted   : {stats['options_inserted']} (skipped: {stats['options_skipped']})")

    elif args.command == "status":
        st = get_status(args.db)
        print_status(st)

    elif args.command == "verify":
        v = verify_integrity(args.db, args.staging)
        print("Integrity verification report:")
        print(f"  Valid              : {v['is_valid']}")
        print(f"  FK Violations      : {v['foreign_key_violations']}")
        print(f"  Orphan Exercises   : {v['orphan_exercises']}")
        print(f"  Orphan Questions   : {v['orphan_questions']}")
        print(f"  Orphan Gaps        : {v['orphan_gaps']}")
        print(f"  Orphan Options     : {v['orphan_options']}")
        print(f"  Orphan Option Gaps : {v['orphan_options_gap_fk']}")
        print(f"  Duplicate Q sources: {v['duplicate_source_questions']}")
        print(f"  Unmatched Lessons  : {v['unmatched_source_lessons']}")
        print(f"  Unmatched Exercises: {v['unmatched_source_exercises']}")
        print(f"  Unmatched Questions: {v['unmatched_source_questions']}")
        print(f"  Unmatched Gaps     : {v['unmatched_source_gaps']}")
        print(f"  Unmatched Options  : {v['unmatched_source_options']}")
        if not v["is_valid"]:
            print("Errors:")
            for err in v["errors"]:
                print(f"  - {err}")
            sys.exit(1)

    elif args.command == "reset":
        if not args.all and not args.level:
            print("Error: Specify --level <LEVEL> or --all to confirm reset.")
            sys.exit(1)
        count = reset_queue(args.db, level=args.level, reset_all=args.all)
        print(f"Reset {count} questions back to PENDING.")


if __name__ == "__main__":
    main()
