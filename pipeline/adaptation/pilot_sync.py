"""Pilot Status Synchronizer (TASK-012).

Universal English Test Platform
Synchronizes the 200 pilot adapted questions in data/adaptation.db so that:
1. The calibrated originality evaluator statuses (188 VALIDATED, 12 REVIEW_REQUIRED)
   replace the obsolete historical 127/73 split.
2. The independent AI semantic review decisions (34/34 APPROVE) are harmonized with
   the database records.
3. Child gaps, options, exercises, and lessons are updated consistently.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_db import get_connection, verify_integrity
from pipeline.adaptation.full_corpus_orchestrator import resolve_status_with_ai_review
from pipeline.adaptation.pilot_data import PILOT_DATA
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

DEFAULT_ADAPTATION_DB = Path("data/adaptation.db")
DEFAULT_STAGING_DB = Path("data/staging.db")


def sync_pilot_statuses(
    adaptation_db_path: Path = DEFAULT_ADAPTATION_DB,
    staging_db_path: Path = DEFAULT_STAGING_DB,
) -> Dict[str, Any]:
    """Synchronize pilot question statuses to match the calibrated evaluator and semantic review."""
    adapt_path = Path(adaptation_db_path)
    if not adapt_path.exists():
        raise FileNotFoundError(f"Adaptation database not found: {adapt_path}")

    adapt_conn = get_connection(adapt_path)
    adapt_conn.row_factory = sqlite3.Row

    # 1. Build target tokens map from PILOT_DATA
    target_tokens_map: Dict[str, List[str]] = {}
    for eid, ex in PILOT_DATA.items():
        for q in ex["questions"]:
            target_tokens_map[str(q["question_id"])] = q.get("target_tokens", [])

    # 2. Fetch semantic review decisions
    sem_reviews: Dict[str, Dict[str, Any]] = {}
    try:
        cur = adapt_conn.execute("SELECT source_question_id, decision, reason FROM pilot_semantic_reviews")
        for row in cur.fetchall():
            sem_reviews[str(row["source_question_id"])] = {
                "decision": row["decision"],
                "reason": row["reason"],
            }
    except Exception:
        pass

    # 3. Fetch all pilot adapted questions (where adapted_text IS NOT NULL)
    pilot_q_rows = adapt_conn.execute(
        """
        SELECT adapted_question_id, source_question_id, adapted_exercise_id,
               adapted_lesson_id, source_text, adapted_text
        FROM adapted_questions
        WHERE adapted_by IN ('pilot_generator', 'pilot_revision_TASK-011H')
        ORDER BY CAST(source_question_id AS INTEGER)
        """
    ).fetchall()

    if len(pilot_q_rows) != 200:
        raise ValueError(f"Expected exactly 200 pilot questions in database, found {len(pilot_q_rows)}")

    sync_counts = {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "REJECTED": 0}
    synced_items: List[Dict[str, Any]] = []
    exercise_ids: set[str] = set()
    lesson_ids: set[str] = set()

    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with adapt_conn:
        for q in pilot_q_rows:
            sqid = str(q["source_question_id"])
            aqid = str(q["adapted_question_id"])
            eid = str(q["adapted_exercise_id"])
            lid = str(q["adapted_lesson_id"])
            exercise_ids.add(eid)
            lesson_ids.add(lid)

            tt = target_tokens_map.get(sqid, [])
            sim = evaluate_similarity(q["source_text"], q["adapted_text"], target_tokens=tt)

            orig_status = sim["originality_status"]
            if orig_status == "APPROVED":
                orig_status = "VALIDATED"

            sem_decision = sem_reviews.get(sqid, {}).get("decision")
            status, rev_req = resolve_status_with_ai_review(orig_status, sem_decision)
            sync_counts[status] = sync_counts.get(status, 0) + 1

            notes_parts = list(sim["reasons"])
            if sqid in sem_reviews:
                rev_info = sem_reviews[sqid]
                notes_parts.append(f"AI Semantic Review: {rev_info['decision']} ({rev_info['reason']})")
            notes = "; ".join(notes_parts)

            # Update adapted_questions
            adapt_conn.execute(
                """
                UPDATE adapted_questions
                SET adaptation_status = ?,
                    review_required = ?,
                    similarity_score = ?,
                    adaptation_notes = ?,
                    adapted_at = ?
                WHERE adapted_question_id = ?
                """,
                (status, rev_req, sim["jaccard_similarity"], notes, now_ts, aqid),
            )

            # Update child gaps
            adapt_conn.execute(
                """
                UPDATE adapted_gaps
                SET review_required = ?
                WHERE adapted_question_id = ?
                """,
                (rev_req, aqid),
            )

            # Update child options
            adapt_conn.execute(
                """
                UPDATE adapted_options
                SET review_required = ?
                WHERE adapted_question_id = ?
                """,
                (rev_req, aqid),
            )

            synced_items.append({
                "source_question_id": sqid,
                "adapted_question_id": aqid,
                "status": status,
                "review_required": rev_req,
                "jaccard_similarity": sim["jaccard_similarity"],
                "semantic_review_decision": sem_reviews.get(sqid, {}).get("decision", "N/A"),
            })

        # 4. Synchronize adapted_exercises
        for eid in exercise_ids:
            cur = adapt_conn.execute(
                """
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN adaptation_status = 'REVIEW_REQUIRED' THEN 1 ELSE 0 END) as rev_req_cnt
                FROM adapted_questions
                WHERE adapted_exercise_id = ? AND adapted_text IS NOT NULL
                """,
                (eid,),
            ).fetchone()

            has_rev_req = bool(cur["rev_req_cnt"] and cur["rev_req_cnt"] > 0)
            ex_status = "REVIEW_REQUIRED" if has_rev_req else "VALIDATED"
            ex_rev_req = 1 if has_rev_req else 0

            adapt_conn.execute(
                """
                UPDATE adapted_exercises
                SET adaptation_status = ?,
                    review_required = ?
                WHERE adapted_exercise_id = ?
                """,
                (ex_status, ex_rev_req, eid),
            )

        # 5. Synchronize adapted_lessons
        for lid in lesson_ids:
            cur = adapt_conn.execute(
                """
                SELECT SUM(review_required) as rev_req_cnt
                FROM adapted_exercises
                WHERE adapted_lesson_id = ?
                """,
                (lid,),
            ).fetchone()

            has_rev_req = bool(cur["rev_req_cnt"] and cur["rev_req_cnt"] > 0)
            l_status = "REVIEW_REQUIRED" if has_rev_req else "VALIDATED"
            l_rev_req = 1 if has_rev_req else 0

            adapt_conn.execute(
                """
                UPDATE adapted_lessons
                SET adaptation_status = ?,
                    review_required = ?
                WHERE adapted_lesson_id = ?
                """,
                (l_status, l_rev_req, lid),
            )

    adapt_conn.close()

    return {
        "total_pilot_questions": len(pilot_q_rows),
        "status_distribution": sync_counts,
        "semantic_reviews_available": len(sem_reviews),
        "synchronized_at": now_ts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize pilot statuses in data/adaptation.db (TASK-012)")
    parser.add_argument("--db", default=str(DEFAULT_ADAPTATION_DB), help="Path to adaptation.db")
    args = parser.parse_args()

    print("=" * 65)
    print(" PILOT STATUS SYNCHRONIZATION (TASK-012)")
    print("=" * 65)

    res = sync_pilot_statuses(Path(args.db))
    print(f"Total Pilot Questions : {res['total_pilot_questions']}")
    print(f"Status Distribution   : VALIDATED={res['status_distribution']['VALIDATED']}, REVIEW_REQUIRED={res['status_distribution']['REVIEW_REQUIRED']}, REJECTED={res['status_distribution']['REJECTED']}")
    print(f"Semantic Reviews Linked: {res['semantic_reviews_available']}")
    print("Database synchronization completed successfully!")


if __name__ == "__main__":
    main()
