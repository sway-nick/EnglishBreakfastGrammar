"""Pilot Content Adaptation Generator (TASK-011C)

Universal English Test Platform
Executes pilot adaptation generation for exactly 20 exercises (200 questions)
from data/staging.db into data/adaptation.db.

Pipeline:
source
  -> generate adaptation
  -> write adaptation records
  -> similarity evaluator
  -> structural validation
  -> answer-semantic validation
  -> Preview Gate
  -> status assignment
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_db import get_connection, verify_integrity
from pipeline.adaptation.pilot_data import PILOT_DATA
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

DEFAULT_ADAPTATION_DB = Path("data/adaptation.db")
DEFAULT_STAGING_DB = Path("data/staging.db")
PILOT_RUN_ID = "pilot_run_20260930_20ex"


def run_pilot_adaptation(
    adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    staging_db_path: Union[str, Path] = DEFAULT_STAGING_DB,
    run_id: str = PILOT_RUN_ID,
) -> Dict[str, Any]:
    """Execute adaptation generation and evaluation for the 20 pilot exercises."""
    adapt_path = Path(adaptation_db_path)
    staging_path = Path(staging_db_path)

    if not adapt_path.exists():
        raise FileNotFoundError(f"Adaptation database not found at: {adapt_path}")
    if not staging_path.exists():
        raise FileNotFoundError(f"Staging database not found at: {staging_path}")

    adapt_conn = get_connection(adapt_path)
    staging_conn = sqlite3.connect(f"file:{staging_path.resolve()}?mode=ro", uri=True)
    staging_conn.row_factory = sqlite3.Row

    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    metrics = {
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": None,
        "exercises_processed": 0,
        "questions_generated": 0,
        "gaps_generated": 0,
        "options_generated": 0,
        "status_counts": {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0},
        "model_distribution": {},
        "levels_represented": set(),
        "exercises_detail": [],
        "failures": [],
    }

    try:
        with adapt_conn:
            # Iterate through each pilot exercise in PILOT_DATA
            for eid, ex_data in PILOT_DATA.items():
                metrics["exercises_processed"] += 1

                # 1. Fetch staging exercise and lesson
                stage_ex = staging_conn.execute(
                    "SELECT exercise_id, lesson_id, exercise_order, page, title, instruction FROM staging_exercises WHERE exercise_id = ?",
                    (eid,),
                ).fetchone()
                if not stage_ex:
                    raise ValueError(f"Exercise {eid} not found in staging!")

                stage_lesson = staging_conn.execute(
                    "SELECT lesson_id, title, level, topic FROM staging_lessons WHERE lesson_id = ?",
                    (stage_ex["lesson_id"],),
                ).fetchone()

                level = stage_lesson["level"]
                metrics["levels_represented"].add(level)

                adapted_ex_id = f"adapt_{eid}"
                adapted_lesson_id = f"adapt_{stage_ex['lesson_id']}"

                ex_statuses = []
                ex_review_req = 0

                # 2. Process each question
                for q_spec in ex_data["questions"]:
                    metrics["questions_generated"] += 1
                    qid = str(q_spec["question_id"])
                    adapted_q_id = f"adapt_{qid}"

                    # Fetch staging question
                    stage_q = staging_conn.execute(
                        "SELECT question_id, exercise_id, response_model, content, explanation, difficulty FROM staging_questions WHERE question_id = ?",
                        (qid,),
                    ).fetchone()
                    if not stage_q:
                        raise ValueError(f"Question {qid} not found in staging!")

                    rm = stage_q["response_model"]
                    metrics["model_distribution"][rm] = metrics["model_distribution"].get(rm, 0) + 1

                    # Fetch staging gaps and options
                    stage_gaps = staging_conn.execute(
                        "SELECT gap_id, gap_order, input_control, correct_answer, accepted_answers FROM staging_gaps WHERE question_id = ? ORDER BY gap_order",
                        (qid,),
                    ).fetchall()
                    stage_opts = staging_conn.execute(
                        "SELECT option_id, gap_id, option_order, text, value, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order",
                        (qid,),
                    ).fetchall()

                    # Cardinality checks
                    if len(q_spec.get("gaps", [])) != len(stage_gaps):
                        err = f"Question {qid}: gap count mismatch (spec={len(q_spec.get('gaps', []))}, staging={len(stage_gaps)})"
                        metrics["failures"].append(err)
                        raise ValueError(err)

                    if len(q_spec.get("options", [])) != len(stage_opts):
                        err = f"Question {qid}: option count mismatch (spec={len(q_spec.get('options', []))}, staging={len(stage_opts)})"
                        metrics["failures"].append(err)
                        raise ValueError(err)

                    # Similarity evaluation
                    target_tokens = q_spec.get("target_tokens", [])
                    sim_res = evaluate_similarity(stage_q["content"], q_spec["adapted_text"], target_tokens)
                    q_status = sim_res["originality_status"]
                    q_jaccard = sim_res["jaccard_similarity"]
                    q_notes = "; ".join(sim_res["reasons"])

                    # Rule: Never mark APPROVED automatically
                    if q_status == "APPROVED":
                        q_status = "VALIDATED"

                    q_review_req = 1 if q_status == "REVIEW_REQUIRED" else 0
                    if q_review_req:
                        ex_review_req = 1

                    metrics["status_counts"][q_status] = metrics["status_counts"].get(q_status, 0) + 1
                    ex_statuses.append(q_status)

                    # Update adapted_questions
                    adapt_conn.execute(
                        """
                        UPDATE adapted_questions
                        SET adapted_text = ?,
                            similarity_score = ?,
                            adaptation_status = ?,
                            review_required = ?,
                            adaptation_notes = ?,
                            adapted_by = 'pilot_generator',
                            adapted_at = ?
                        WHERE adapted_question_id = ?
                        """,
                        (
                            q_spec["adapted_text"],
                            q_jaccard,
                            q_status,
                            q_review_req,
                            q_notes,
                            started_at,
                            adapted_q_id,
                        ),
                    )

                    # Update adapted_gaps if present
                    spec_gaps = q_spec.get("gaps", [])
                    for g_idx, g_spec in enumerate(spec_gaps):
                        metrics["gaps_generated"] += 1
                        stage_g = stage_gaps[g_idx]
                        adapted_g_id = f"adapt_{stage_g['gap_id']}"
                        acc_json = json.dumps(g_spec.get("accepted_answers", [g_spec["correct_answer"]]))

                        adapt_conn.execute(
                            """
                            UPDATE adapted_gaps
                            SET adapted_correct_answer = ?,
                                adapted_accepted_answers = ?,
                                review_required = ?,
                                adaptation_notes = ?
                            WHERE adapted_gap_id = ?
                            """,
                            (
                                g_spec["correct_answer"],
                                acc_json,
                                q_review_req,
                                f"Adapted from '{stage_g['correct_answer']}'",
                                adapted_g_id,
                            ),
                        )

                    # Update adapted_options if present
                    spec_opts = q_spec.get("options", [])
                    for o_idx, o_spec in enumerate(spec_opts):
                        metrics["options_generated"] += 1
                        stage_o = stage_opts[o_idx]
                        adapted_o_id = f"adapt_{stage_o['option_id']}"

                        adapt_conn.execute(
                            """
                            UPDATE adapted_options
                            SET adapted_text = ?,
                                adapted_value = ?,
                                adapted_is_correct = ?,
                                review_required = ?,
                                adaptation_notes = ?
                            WHERE adapted_option_id = ?
                            """,
                            (
                                o_spec["text"],
                                o_spec["text"],
                                o_spec["is_correct"],
                                q_review_req,
                                f"Option {o_idx + 1} adapted",
                                adapted_o_id,
                            ),
                        )

                # Determine exercise-level status (worst status among questions)
                if "REJECTED" in ex_statuses:
                    ex_status = "REJECTED"
                elif "REVIEW_REQUIRED" in ex_statuses:
                    ex_status = "REVIEW_REQUIRED"
                else:
                    ex_status = "VALIDATED"

                adapt_conn.execute(
                    """
                    UPDATE adapted_exercises
                    SET adaptation_status = ?,
                        review_required = ?,
                        adaptation_notes = ?
                    WHERE adapted_exercise_id = ?
                    """,
                    (
                        ex_status,
                        ex_review_req,
                        f"Pilot generated: {len(ex_data['questions'])} questions ({ex_status})",
                        adapted_ex_id,
                    ),
                )

                # Update lesson status
                adapt_conn.execute(
                    """
                    UPDATE adapted_lessons
                    SET adaptation_status = ?,
                        review_required = ?,
                        adapted_by = 'pilot_generator',
                        adapted_at = ?,
                        adaptation_notes = 'Pilot generation active'
                    WHERE adapted_lesson_id = ?
                    """,
                    (
                        ex_status,
                        ex_review_req,
                        started_at,
                        adapted_lesson_id,
                    ),
                )

                metrics["exercises_detail"].append({
                    "exercise_id": eid,
                    "level": level,
                    "title": stage_lesson["title"],
                    "questions_count": len(ex_data["questions"]),
                    "status": ex_status,
                    "review_required": ex_review_req,
                })

            # Record run in adaptation_runs
            completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            metrics["completed_at"] = completed_at

            adapt_conn.execute(
                """
                INSERT OR REPLACE INTO adaptation_runs (
                    run_id, started_at, completed_at, model_name, target_level, status,
                    total_items, generated_count, validated_count, rejected_count, notes
                ) VALUES (?, ?, ?, 'pilot_curated_engine', 'A1+A2', 'completed', ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    started_at,
                    completed_at,
                    metrics["questions_generated"],
                    metrics["questions_generated"],
                    metrics["status_counts"]["VALIDATED"],
                    metrics["status_counts"]["REJECTED"],
                    f"Pilot completed: 20 exercises, {metrics['questions_generated']} Qs (Validated: {metrics['status_counts']['VALIDATED']}, Review: {metrics['status_counts']['REVIEW_REQUIRED']}, Rejected: {metrics['status_counts']['REJECTED']})",
                ),
            )

    finally:
        staging_conn.close()
        adapt_conn.close()

    metrics["levels_represented"] = sorted(list(metrics["levels_represented"]))
    return metrics


def export_pilot_universal_json(
    adaptation_db_path: Union[str, Path] = DEFAULT_ADAPTATION_DB,
    output_path: Union[str, Path] = Path("data/pilot_adapted_lessons.json"),
    filter_by_adapted_by: bool = True,
) -> Path:
    """Export adapted pilot exercises into canonical Universal Lesson JSON format."""
    adapt_conn = get_connection(adaptation_db_path)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    clause = "q.adapted_by IN ('pilot_generator', 'pilot_revision_TASK-011H')" if filter_by_adapted_by else "q.adapted_text IS NOT NULL"
    sub_clause = "adapted_by IN ('pilot_generator', 'pilot_revision_TASK-011H')" if filter_by_adapted_by else "adapted_text IS NOT NULL"

    try:
        # Fetch adapted lessons that have adapted questions
        lessons_rows = adapt_conn.execute(
            f"""
            SELECT DISTINCT l.adapted_lesson_id, l.title, l.level, l.topic, l.description
            FROM adapted_lessons l
            JOIN adapted_exercises e ON e.adapted_lesson_id = l.adapted_lesson_id
            JOIN adapted_questions q ON q.adapted_exercise_id = e.adapted_exercise_id
            WHERE {clause}
            ORDER BY l.adapted_lesson_id
            """
        ).fetchall()

        universal_lessons = []

        for l_row in lessons_rows:
            l_id = l_row["adapted_lesson_id"]
            lesson_obj = {
                "id": l_id,
                "title": l_row["title"],
                "level": l_row["level"],
                "topic": l_row["topic"] or "",
                "status": "draft",
                "exercises": [],
            }

            ex_rows = adapt_conn.execute(
                f"""
                SELECT adapted_exercise_id, exercise_order, page, title, instruction
                FROM adapted_exercises
                WHERE adapted_lesson_id = ? AND adapted_exercise_id IN (
                    SELECT DISTINCT adapted_exercise_id FROM adapted_questions WHERE {sub_clause}
                )
                ORDER BY exercise_order
                """,
                (l_id,),
            ).fetchall()

            for ex_row in ex_rows:
                ex_id = ex_row["adapted_exercise_id"]
                ex_obj = {
                    "id": ex_id,
                    "lessonId": l_id,
                    "order": ex_row["exercise_order"],
                    "title": ex_row["title"] or f"Exercise {ex_row['exercise_order']}",
                    "instruction": ex_row["instruction"] or "",
                    "questions": [],
                }

                q_rows = adapt_conn.execute(
                    f"""
                    SELECT adapted_question_id, question_order, response_model, adapted_text, explanation, difficulty
                    FROM adapted_questions
                    WHERE adapted_exercise_id = ? AND {sub_clause}
                    ORDER BY question_order
                    """,
                    (ex_id,),
                ).fetchall()

                for q_row in q_rows:
                    qid = q_row["adapted_question_id"]
                    rm = q_row["response_model"]

                    # Map response_model to QuestionType
                    # In src/models/index.js: QuestionType = { GAP_TEXT: 'gap_text', GAP_SELECT: 'gap_select', SINGLE_CHOICE: 'single_choice', MULTIPLE_CHOICE: 'multiple_choice' }
                    q_gaps = adapt_conn.execute(
                        "SELECT adapted_gap_id, gap_order, input_control, adapted_correct_answer, adapted_accepted_answers FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order",
                        (qid,),
                    ).fetchall()

                    q_opts = adapt_conn.execute(
                        "SELECT adapted_option_id, adapted_gap_id, option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order",
                        (qid,),
                    ).fetchall()

                    if rm == "single_choice":
                        q_type = "single_choice"
                    elif rm == "multiple_choice":
                        q_type = "multiple_choice"
                    elif rm == "gap":
                        if q_gaps and q_gaps[0]["input_control"] == "select":
                            q_type = "gap_select"
                        else:
                            q_type = "gap_text"
                    else:
                        q_type = rm

                    # Build question JSON
                    norm_text = re.sub(r"\{\{gap_?(\d+)\}\}", r"{{gap\1}}", q_row["adapted_text"] or "")
                    q_obj: Dict[str, Any] = {
                        "id": qid,
                        "order": q_row["question_order"],
                        "type": q_type,
                        "text": norm_text,
                    }

                    if q_type in ("single_choice", "multiple_choice"):
                        q_obj["options"] = [
                            {
                                "id": opt["adapted_option_id"],
                                "order": opt["option_order"],
                                "value": opt["adapted_text"],
                                "is_correct": bool(opt["adapted_is_correct"]),
                            }
                            for opt in q_opts
                        ]
                    elif q_type in ("gap_select", "gap_text"):
                        q_obj["gaps"] = []
                        for g in q_gaps:
                            gid = g["adapted_gap_id"]
                            gap_opts = [o for o in q_opts if o["adapted_gap_id"] == gid]
                            g_entry: Dict[str, Any] = {
                                "id": gid,
                                "order": g["gap_order"],
                                "placeholder": f"{{{{gap{g['gap_order']}}}}}",
                            }
                            if q_type == "gap_select":
                                g_entry["options"] = [
                                    {
                                        "id": o["adapted_option_id"],
                                        "order": o["option_order"],
                                        "value": o["adapted_text"],
                                        "is_correct": bool(o["adapted_is_correct"]),
                                    }
                                    for o in gap_opts
                                ]
                            elif q_type == "gap_text":
                                try:
                                    acc = json.loads(g["adapted_accepted_answers"])
                                except Exception:
                                    acc = [g["adapted_correct_answer"]]
                                g_entry["correct_answer"] = g["adapted_correct_answer"]
                                g_entry["accepted_answers"] = acc
                            q_obj["gaps"].append(g_entry)

                    ex_obj["questions"].append(q_obj)

                lesson_obj["exercises"].append(ex_obj)

            universal_lessons.append(lesson_obj)

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(universal_lessons, f, ensure_ascii=False, indent=2)

    finally:
        adapt_conn.close()

    return out_file


def run_preview_gate_validation(universal_json_path: Union[str, Path]) -> Dict[str, Any]:
    """Execute Preview Gate & JS validator over the exported adapted lessons."""
    json_path = Path(universal_json_path).resolve().as_posix()
    node_script = f"""
    import fs from 'fs';
    import {{ validate }} from './src/validation/index.js';
    import {{ checkPreviewGate }} from './src/preview/server.js';

    const raw = fs.readFileSync('{json_path}', 'utf-8');
    const lessons = JSON.parse(raw);

    let totalLessons = lessons.length;
    let validCount = 0;
    let gatePassed = 0;
    let errors = [];

    for (const lesson of lessons) {{
        const vResult = validate(lesson, {{ allowUnresolved: false }});
        if (vResult.valid) {{
            validCount++;
        }} else {{
            errors.push({{ id: lesson.id, errors: vResult.errors }});
        }}

        const gate = checkPreviewGate(lesson, {{ allowUnresolved: false }});
        if (!gate.shouldBlock) {{
            gatePassed++;
        }}
    }}

    console.log(JSON.stringify({{
        totalLessons,
        validCount,
        gatePassed,
        errors
    }}));
    """

    res = subprocess.run(
        ["node", "--experimental-vm-modules", "-e", node_script],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Node Preview Gate validation failed: {res.stderr}\nOutput: {res.stdout}")

    return json.loads(res.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Pilot Adaptation Generation CLI (TASK-011C)")
    parser.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    parser.add_argument("--staging", default=str(DEFAULT_STAGING_DB), help="Path to staging.db")
    parser.add_argument("--run-id", default=PILOT_RUN_ID, help="Dedicated run ID")
    parser.add_argument("--skip-gate", action="store_true", help="Skip preview gate validation")

    args = parser.parse_args()

    print("=" * 65)
    print(" PILOT CONTENT ADAPTATION GENERATION (TASK-011C)")
    print("=" * 65)

    # 1. Run pilot generation
    print(f"\n[1/4] Running pilot adaptation for 20 exercises (run_id: {args.run_id})...")
    metrics = run_pilot_adaptation(args.db, args.staging, args.run_id)

    print(f"  Exercises processed: {metrics['exercises_processed']}")
    print(f"  Questions generated: {metrics['questions_generated']}")
    print(f"  Gaps generated     : {metrics['gaps_generated']}")
    print(f"  Options generated  : {metrics['options_generated']}")
    print(f"  Levels represented : {', '.join(metrics['levels_represented'])}")
    print(f"  Model distribution : {metrics['model_distribution']}")
    print(f"  Status breakdown   :")
    print(f"    VALIDATED       : {metrics['status_counts']['VALIDATED']}")
    print(f"    REVIEW_REQUIRED : {metrics['status_counts']['REVIEW_REQUIRED']}")
    print(f"    REJECTED        : {metrics['status_counts']['REJECTED']}")

    # 2. Database integrity verification
    print("\n[2/4] Verifying adaptation database referential integrity...")
    integrity = verify_integrity(args.db, args.staging)
    print(f"  Integrity valid    : {integrity['is_valid']}")
    print(f"  FK Violations      : {integrity['foreign_key_violations']}")
    print(f"  Orphan Questions   : {integrity['orphan_questions']}")
    if not integrity["is_valid"]:
        print("  Errors:", integrity["errors"])
        sys.exit(1)

    # 3. Export to Universal Lesson JSON
    print("\n[3/4] Exporting adapted exercises to canonical Universal Lesson JSON...")
    out_json = export_pilot_universal_json(args.db)
    print(f"  Saved to           : {out_json} ({out_json.stat().st_size:,} bytes)")

    # 4. Preview Gate Validation
    if not args.skip_gate:
        print("\n[4/4] Executing Preview Gate and JS Domain Validation...")
        gate_res = run_preview_gate_validation(out_json)
        print(f"  Total lessons      : {gate_res['totalLessons']}")
        print(f"  Strict Validations : {gate_res['validCount']} / {gate_res['totalLessons']} PASSED")
        print(f"  Preview Gate       : {gate_res['gatePassed']} / {gate_res['totalLessons']} PASSED (0 blocked)")
        if gate_res["errors"]:
            print("  Gate Errors:")
            for err in gate_res["errors"]:
                print(f"    - {err}")
            sys.exit(1)

    print("\n" + "=" * 65)
    print(" PILOT ADAPTATION COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
