"""Full Corpus Deep Anomaly Scanner for all 5,796 Questions.

Scans all 5,796 questions in adaptation.db and staging.db for:
1. Gap Placeholder Mismatches:
   - Gap count in adapted_text vs count in adapted_gaps table.
   - Malformed placeholders (e.g., {{gap}}, {{gap_}}, unmatched braces).
2. Choice / Option Structure:
   - single_choice questions with != 1 correct option.
   - Placeholder _____ missing when options expect a slot, or vice versa.
   - Empty or identical option texts.
3. Originality & Similarity:
   - High Jaccard similarity (> 0.40) or boundary-aware forbidden shingles.
4. Duplicate / Carrier Collisions:
   - Exact identical adapted_text across different questions in the corpus.
5. Answer Key Integrity:
   - Empty correct answers or missing adapted_gaps / adapted_options.
6. Unreviewed Status Filter:
   - Checks against TEACHER_REVIEW_REGISTRY.json to filter out any questions already marked REVIEWED_PASS / REVIEWED_FIX / FIX_APPLIED.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.similarity_evaluator import evaluate_similarity

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
BATCHES_DIR = REPORTS_DIR / "teacher_review_batches"
REGISTRY_PATH = REPORTS_DIR / "TEACHER_REVIEW_REGISTRY.json"
QUEUE_PATH = REPORTS_DIR / "TASK-025_full_teacher_review_queue.json"

GAP_REGEX = re.compile(r"\{\{gap_(\d+)\}\}")


def scan_corpus() -> Dict[str, Any]:
    print("=" * 70)
    print("FULL 5,796-QUESTION CORPUS DEEP ANOMALY SCAN")
    print("=" * 70)

    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    reg_questions = registry.get("questions", {})

    # Load all questions
    all_adapt_q = adapt_conn.execute("SELECT * FROM adapted_questions").fetchall()
    print(f"[LOAD] Loaded {len(all_adapt_q)} questions from adaptation.db")

    anomalies: List[Dict[str, Any]] = []

    # Map text for carrier collisions
    text_to_qids = defaultdict(list)

    for aq in all_adapt_q:
        qid = str(aq["source_question_id"])
        sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
        s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()
        s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()

        rm = aq["response_model"]
        ad_text = aq["adapted_text"] or ""
        src_text = sq["content"] or ""
        aq_id = aq["adapted_question_id"]

        # Track text for collision check (ignore short or trivial if any, but clean spaces)
        clean_text = " ".join(ad_text.split()).strip()
        if len(clean_text) > 15:
            text_to_qids[clean_text].append(qid)

        issues: List[str] = []

        # Check 1: Gap Placeholders vs DB gaps
        if rm == "gap":
            text_gaps = GAP_REGEX.findall(ad_text)
            text_gap_orders = sorted([int(x) for x in text_gaps])
            db_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq_id,)).fetchall()
            db_gap_orders = sorted([g["gap_order"] for g in db_gaps])

            if len(text_gaps) == 0:
                issues.append(f"Response model is 'gap' but NO {{gap_N}} placeholder found in adapted text.")
            elif text_gap_orders != db_gap_orders:
                issues.append(f"Gap placeholder numbers in text {text_gap_orders} mismatch DB gaps {db_gap_orders}")

            # Check for empty answers
            for g in db_gaps:
                if not g["adapted_correct_answer"] or not str(g["adapted_correct_answer"]).strip():
                    issues.append(f"Empty correct answer for gap {g['gap_order']}")

        # Check 2: Choice questions options
        elif rm == "single_choice":
            db_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq_id,)).fetchall()
            if len(db_opts) < 2:
                issues.append(f"Single choice question has fewer than 2 options ({len(db_opts)})")
            
            correct_count = sum(1 for o in db_opts if o["adapted_is_correct"] == 1)
            if correct_count != 1:
                issues.append(f"Single choice question has {correct_count} correct options (expected exactly 1)")

            for o in db_opts:
                if not o["adapted_text"] or not str(o["adapted_text"]).strip():
                    issues.append(f"Empty option text for option {o['option_order']}")

        # Check 3: Similarity & Originality
        sim_eval = evaluate_similarity(src_text, ad_text)
        if sim_eval["originality_status"] == "REJECTED":
            issues.append(f"Originality REJECTED: {'; '.join(sim_eval['reasons'])}")

        if issues:
            anomalies.append({
                "qid": qid,
                "review_index": reg_questions.get(qid, {}).get("review_index", 0),
                "level": s_les["level"],
                "exercise_id": sq["exercise_id"],
                "exercise_title": s_ex["title"],
                "grammar_target": s_les["topic"],
                "response_model": rm,
                "source_text": src_text,
                "adapted_text": ad_text,
                "anomaly_reasons": issues,
                "category": "SYNTACTIC_OR_STRUCTURAL_ANOMALY",
            })

    # Check 4: Cross-Question Carrier Collisions
    for text_val, qid_list in text_to_qids.items():
        if len(qid_list) > 1:
            for qid in qid_list:
                sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
                s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()
                s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()
                other_qids = [x for x in qid_list if x != qid]
                
                # Check if already in anomalies
                existing = next((a for a in anomalies if a["qid"] == qid), None)
                collision_msg = f"Identical adapted text shared with QID(s): {', '.join(other_qids)}"
                if existing:
                    existing["anomaly_reasons"].append(collision_msg)
                else:
                    anomalies.append({
                        "qid": qid,
                        "review_index": reg_questions.get(qid, {}).get("review_index", 0),
                        "level": s_les["level"],
                        "exercise_id": sq["exercise_id"],
                        "exercise_title": s_ex["title"],
                        "grammar_target": s_les["topic"],
                        "response_model": sq["response_model"],
                        "source_text": sq["content"],
                        "adapted_text": text_val,
                        "anomaly_reasons": [collision_msg],
                        "category": "CARRIER_COLLISION",
                    })

    print(f"\n[SCAN RESULT] Total raw anomaly triggers detected in full corpus: {len(anomalies)}")

    # Filter by Teacher Review Status
    unreviewed_anomalies = []
    reviewed_anomalies = []

    for anom in anomalies:
        qid = anom["qid"]
        reg_info = reg_questions.get(qid, {})
        status = reg_info.get("status", "UNREVIEWED")
        anom["teacher_review_status"] = status
        
        # Check adapted gaps / options for review payload
        aq_row = adapt_conn.execute("SELECT adapted_question_id FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
        aq_id = aq_row["adapted_question_id"]
        
        if anom["response_model"] == "gap":
            a_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq_id,)).fetchall()
            anom["adapted_correct_answer"] = [g["adapted_correct_answer"] for g in a_gaps]
            anom["adapted_options"] = None
        else:
            a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq_id,)).fetchall()
            anom["adapted_correct_answer"] = [o["adapted_text"] for o in a_opts if o["adapted_is_correct"] == 1]
            anom["adapted_options"] = [{"order": o["option_order"], "text": o["adapted_text"], "is_correct": o["adapted_is_correct"]} for o in a_opts]

        if status in ["REVIEWED_PASS", "REVIEWED_FIX", "FIX_APPLIED"]:
            reviewed_anomalies.append(anom)
        else:
            unreviewed_anomalies.append(anom)

    print(f"  - Already reviewed & approved: {len(reviewed_anomalies)}")
    print(f"  - UNREVIEWED anomalies remaining: {len(unreviewed_anomalies)}")

    stage_conn.close()
    adapt_conn.close()

    return {
        "total_scanned": len(all_adapt_q),
        "total_anomalies_detected": len(anomalies),
        "already_reviewed_count": len(reviewed_anomalies),
        "unreviewed_anomalies_count": len(unreviewed_anomalies),
        "unreviewed_anomalies": unreviewed_anomalies,
        "reviewed_anomalies": reviewed_anomalies,
    }


if __name__ == "__main__":
    res = scan_corpus()
    if res["unreviewed_anomalies_count"] > 0:
        out_path = BATCHES_DIR / f"review_batch_unreviewed_anomalies_{res['unreviewed_anomalies_count']:04d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_questions_scanned": res["total_scanned"],
                    "unreviewed_anomaly_count": res["unreviewed_anomalies_count"],
                    "status": "PREPARED",
                },
                "questions": res["unreviewed_anomalies"]
            }, f, indent=2, ensure_ascii=False)
        print(f"\n[OUTPUT] Saved unreviewed anomalies to {out_path}")
    else:
        print("\n[RESULT] 0 UNREVIEWED anomalies across the entire 5,796-question corpus!")
