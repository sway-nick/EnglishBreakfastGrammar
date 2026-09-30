"""Apply pilot revisions for QID 4203 and QID 4211 (TASK-011H).

Universal English Test Platform
Updates only QID 4203 and QID 4211 in data/adaptation.db without modifying
the source corpus or any other question.
"""

import datetime
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_db import get_connection, verify_integrity
from pipeline.adaptation.pilot_generator import export_pilot_universal_json, run_preview_gate_validation
from pipeline.adaptation.semantic_reviewer import run_semantic_review
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

ADAPTATION_DB_PATH = Path("data/adaptation.db")
STAGING_DB_PATH = Path("data/staging.db")


def apply_revisions():
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn = get_connection(ADAPTATION_DB_PATH)

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # --- 1. QID 4203 ---
    src_4203 = stage_conn.execute(
        "SELECT content FROM staging_questions WHERE question_id = '4203'"
    ).fetchone()[0]
    text_4203 = "1 During the heavy storm, all the other passengers were far calmer than _____."
    sim_4203 = evaluate_similarity(src_4203, text_4203, ["than", "me"])
    status_4203 = sim_4203["originality_status"]
    if status_4203 == "APPROVED":
        status_4203 = "VALIDATED"
    notes_4203 = "; ".join(sim_4203["reasons"])

    # --- 2. QID 4211 ---
    src_4211 = stage_conn.execute(
        "SELECT content FROM staging_questions WHERE question_id = '4211'"
    ).fetchone()[0]
    text_4211 = "9 During the lunch break, the school cafeteria is always far _____ than the library."
    sim_4211 = evaluate_similarity(src_4211, text_4211, ["noisier", "than"])
    status_4211 = sim_4211["originality_status"]
    if status_4211 == "APPROVED":
        status_4211 = "VALIDATED"
    notes_4211 = "; ".join(sim_4211["reasons"])

    with adapt_conn:
        # Update question 4203
        adapt_conn.execute(
            """
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adaptation_status = ?, review_required = 0,
                adaptation_notes = ?, adapted_by = 'pilot_revision_TASK-011H', adapted_at = ?
            WHERE adapted_question_id = 'adapt_4203'
            """,
            (text_4203, sim_4203["jaccard_similarity"], status_4203, notes_4203, now_iso),
        )
        opts_4203 = [
            ("adapt_4203_1", "me", 1),
            ("adapt_4203_2", "mine", 0),
            ("adapt_4203_3", "my", 0),
        ]
        for opt_id, opt_text, is_corr in opts_4203:
            adapt_conn.execute(
                """
                UPDATE adapted_options
                SET adapted_text = ?, adapted_value = ?, adapted_is_correct = ?, review_required = 0,
                    adaptation_notes = 'Revised option (TASK-011H)'
                WHERE adapted_option_id = ?
                """,
                (opt_text, opt_text, is_corr, opt_id),
            )

        # Update question 4211
        adapt_conn.execute(
            """
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adaptation_status = ?, review_required = 0,
                adaptation_notes = ?, adapted_by = 'pilot_revision_TASK-011H', adapted_at = ?
            WHERE adapted_question_id = 'adapt_4211'
            """,
            (text_4211, sim_4211["jaccard_similarity"], status_4211, notes_4211, now_iso),
        )
        opts_4211 = [
            ("adapt_4211_1", "noisy", 0),
            ("adapt_4211_2", "noisier", 1),
            ("adapt_4211_3", "more noisier", 0),
        ]
        for opt_id, opt_text, is_corr in opts_4211:
            adapt_conn.execute(
                """
                UPDATE adapted_options
                SET adapted_text = ?, adapted_value = ?, adapted_is_correct = ?, review_required = 0,
                    adaptation_notes = 'Revised option (TASK-011H)'
                WHERE adapted_option_id = ?
                """,
                (opt_text, opt_text, is_corr, opt_id),
            )

    stage_conn.close()
    adapt_conn.close()

    print("[1/4] Applied question & option revisions in data/adaptation.db.")

    # Verify integrity of adaptation database
    int_res = verify_integrity(ADAPTATION_DB_PATH)
    print(f"[2/4] Database integrity check: valid={int_res['is_valid']} (FK violations: {int_res['foreign_key_violations']})")

    # Export universal JSON and validate Preview Gate
    json_path = export_pilot_universal_json(ADAPTATION_DB_PATH, "data/pilot_adapted_lessons.json")
    print(f"[3/4] Exported updated pilot lessons to {json_path}")

    gate_res = run_preview_gate_validation(json_path)
    print(f"      Preview Gate: validLessons={gate_res['validCount']}/{gate_res['totalLessons']}, passed={gate_res['gatePassed']}/{gate_res['totalLessons']}")

    # Re-run semantic review
    print("[4/4] Running independent AI semantic reviewer...")
    sem_res = run_semantic_review()
    tot = sem_res['metadata']['total_reviewed']
    dec = sem_res['summary']['by_decision']
    print(f"      Semantic Review: total={tot}, APPROVE={dec['APPROVE']}, REVISE={dec['REVISE']}, REJECT={dec['REJECT']}")

    return {
        "4203": {
            "source_text": src_4203,
            "new_text": text_4203,
            "options": opts_4203,
            "correct_answer": "me",
            "similarity": sim_4203,
            "status": status_4203,
        },
        "4211": {
            "source_text": src_4211,
            "new_text": text_4211,
            "options": opts_4211,
            "correct_answer": "noisier",
            "similarity": sim_4211,
            "status": status_4211,
        },
        "preview_gate": gate_res,
        "semantic_review": sem_res,
    }


if __name__ == "__main__":
    apply_revisions()
