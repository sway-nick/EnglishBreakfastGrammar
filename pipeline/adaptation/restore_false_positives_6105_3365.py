"""Restore false positives QID 6105 and QID 3365 to exact previous state.

Performs:
1. Restores QID 6105 adapted_text to '7 practice / basketball / after classes / in the gym / They ⇒ They {{gap_1}}.'
   and gap answer to 'practice basketball in the gym after classes'.
2. Restores QID 3365 adapted_text to:
   "Greetings Robert!\nI thoroughly appreciated receiving 1 {{gap_1}} thoughtful post-conference dispatch; discovering latest updates regarding 2 {{gap_2}} brought immense satisfaction. Our entire laboratory praised Dr. Angela's fellowship appointment; colleagues respect 3 {{gap_3}} tremendously, and everyone knows 4 {{gap_4}} will direct department research with remarkable vision. Did board trustees approve project proposals once coordinators presented 5 {{gap_5}} the revised budget? Surely 6 {{gap_6}} recognize how crucial institutional funding remains.\nAdditionally, our institute recently installed a solar observatory dome; 7 {{gap_7}} official designation is Helios Peak. Elena and I evaluated 8 {{gap_8}} during field trials, whereupon 9 {{gap_9}} resolved to finalize procurement without hesitation. Faculty members take immense pride in 10 {{gap_10}} innovative facility!\nWarmest wishes, Nicholas"
   with original similarity_score (0.0).
3. Marks 6105 and 3365 as REVIEWED_PASS in TEACHER_REVIEW_REGISTRY.json, TASK-025_full_teacher_review_queue.json, and review_batch_anomalies_0054.json.
4. Keeps the 6 approved fixes (2948, 2949, 2950, 2955, 2956, 5047) as REVIEWED_FIX.
5. Updates VERIFICATION_REGISTRY.json.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(REPO_ROOT))

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
BATCHES_DIR = REPORTS_DIR / "teacher_review_batches"

REGISTRY_PATH = REPORTS_DIR / "TEACHER_REVIEW_REGISTRY.json"
QUEUE_PATH = REPORTS_DIR / "TASK-025_full_teacher_review_queue.json"
VERIFICATION_REGISTRY_PATH = REPORTS_DIR / "VERIFICATION_REGISTRY.json"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def hash_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    now_ts = datetime.now(timezone.utc).isoformat()
    print("=" * 70)
    print("RESTORING FALSE POSITIVES 6105 AND 3365")
    print("=" * 70)

    # 1. Database Restore
    adapt_conn = sqlite3.connect(ADAPTATION_DB_PATH)

    text_6105 = "7 practice / basketball / after classes / in the gym / They ⇒ They {{gap_1}}."
    gap_6105 = "practice basketball in the gym after classes"
    sim_6105 = 0.0

    text_3365 = (
        "Greetings Robert!\n"
        "I thoroughly appreciated receiving 1 {{gap_1}} thoughtful post-conference dispatch; discovering latest updates regarding 2 {{gap_2}} brought immense satisfaction. Our entire laboratory praised Dr. Angela's fellowship appointment; colleagues respect 3 {{gap_3}} tremendously, and everyone knows 4 {{gap_4}} will direct department research with remarkable vision. Did board trustees approve project proposals once coordinators presented 5 {{gap_5}} the revised budget? Surely 6 {{gap_6}} recognize how crucial institutional funding remains.\n"
        "Additionally, our institute recently installed a solar observatory dome; 7 {{gap_7}} official designation is Helios Peak. Elena and I evaluated 8 {{gap_8}} during field trials, whereupon 9 {{gap_9}} resolved to finalize procurement without hesitation. Faculty members take immense pride in 10 {{gap_10}} innovative facility!\n"
        "Warmest wishes, Nicholas"
    )
    sim_3365 = 0.0

    with adapt_conn:
        # Restore 6105
        adapt_conn.execute("""
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adapted_by = 'manual_correction_TASK-014B', adapted_at = ?
            WHERE source_question_id = '6105'
        """, (text_6105, sim_6105, now_ts))

        adapt_conn.execute("""
            UPDATE adapted_gaps
            SET adapted_correct_answer = ?
            WHERE adapted_question_id = 'adapt_6105' AND gap_order = 1
        """, (gap_6105,))

        # Restore 3365
        adapt_conn.execute("""
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adapted_by = 'manual_correction_TASK-014B', adapted_at = ?
            WHERE source_question_id = '3365'
        """, (text_3365, sim_3365, now_ts))

    print("[DB] Restored QID 6105 and 3365 content and gaps in adaptation.db")

    # 2. Update Registries
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registry_items = registry_data["questions"]

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
    queue_entries = queue_data["queue"]

    # 6105 -> REVIEWED_PASS
    registry_items["6105"]["status"] = "REVIEWED_PASS"
    registry_items["6105"]["reviewed_by"] = "HQ"
    registry_items["6105"]["reviewed_at"] = now_ts
    registry_items["6105"]["teacher_decision"] = "PASS (False positive confirmed by HQ)"
    registry_items["6105"]["adapted_content_hash"] = hash_text(text_6105)

    # 3365 -> REVIEWED_PASS
    registry_items["3365"]["status"] = "REVIEWED_PASS"
    registry_items["3365"]["reviewed_by"] = "HQ"
    registry_items["3365"]["reviewed_at"] = now_ts
    registry_items["3365"]["teacher_decision"] = "PASS (False positive confirmed by HQ)"
    registry_items["3365"]["adapted_content_hash"] = hash_text(text_3365)

    for q_entry in queue_entries:
        if q_entry["qid"] in ["6105", "3365"]:
            q_entry["status"] = "REVIEWED_PASS"

    # Update Anomaly Batch JSON
    anom_json_path = BATCHES_DIR / "review_batch_anomalies_0054.json"
    with open(anom_json_path, "r", encoding="utf-8") as f:
        anom_data = json.load(f)

    anom_data["metadata"]["review_summary"] = {
        "PASS_count": 48,
        "FIX_count": 6,
        "fixed_qids": ["2948", "2949", "2950", "2955", "2956", "5047"],
        "restored_false_positives": ["6105", "3365"],
    }
    for q in anom_data["questions"]:
        if q["qid"] == "6105":
            q["review_status"] = "REVIEWED_PASS"
            q["adapted_text"] = text_6105
            q["adapted_correct_answer"] = [gap_6105]
            q["relevant_machine_flags"]["similarity_score"] = sim_6105
        elif q["qid"] == "3365":
            q["review_status"] = "REVIEWED_PASS"
            q["adapted_text"] = text_3365
            q["relevant_machine_flags"]["similarity_score"] = sim_3365

    with open(anom_json_path, "w", encoding="utf-8") as f:
        json.dump(anom_data, f, indent=2, ensure_ascii=False)

    # Recount Metrics
    status_counts = {
        "TOTAL": 5796,
        "UNREVIEWED": sum(1 for v in registry_items.values() if v["status"] == "UNREVIEWED"),
        "PREPARED": sum(1 for v in registry_items.values() if v["status"] == "PREPARED"),
        "REVIEWED_PASS": sum(1 for v in registry_items.values() if v["status"] == "REVIEWED_PASS"),
        "REVIEWED_FIX": sum(1 for v in registry_items.values() if v["status"] == "REVIEWED_FIX"),
        "FIX_APPLIED": sum(1 for v in registry_items.values() if v["status"] == "FIX_APPLIED"),
        "RECHECK_REQUIRED": sum(1 for v in registry_items.values() if v["status"] == "RECHECK_REQUIRED"),
    }
    completed_count = status_counts["REVIEWED_PASS"] + status_counts["REVIEWED_FIX"] + status_counts["FIX_APPLIED"]
    remaining_count = status_counts["UNREVIEWED"] + status_counts["PREPARED"] + status_counts["RECHECK_REQUIRED"]

    registry_data["metadata"]["updated_at"] = now_ts
    registry_data["metadata"]["metrics"] = {
        **status_counts,
        "teacher_review_completed": completed_count,
        "teacher_review_remaining": remaining_count,
    }
    registry_data["metadata"]["anomaly_review_completed"]["review_results"] = {
        "REVIEWED_PASS": 48,
        "REVIEWED_FIX": 6,
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)

    queue_data["metadata"]["last_updated"] = now_ts
    queue_data["metadata"]["status_summary"] = status_counts
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, indent=2, ensure_ascii=False)

    # Update Verification Registry
    with open(VERIFICATION_REGISTRY_PATH, "r", encoding="utf-8") as f:
        ver_reg = json.load(f)

    adapt_hash_new = compute_sha256(ADAPTATION_DB_PATH)
    ver_reg["metadata"]["last_updated"] = now_ts
    ver_reg["verifications"]["adaptation_database_state"]["sha256"] = adapt_hash_new
    ver_reg["verifications"]["teacher_review_anomalies_0054"]["pass_count"] = 48
    ver_reg["verifications"]["teacher_review_anomalies_0054"]["fix_count"] = 6
    ver_reg["verifications"]["teacher_review_anomalies_0054"]["fixed_qids"] = ["2948", "2949", "2950", "2955", "2956", "5047"]

    with open(VERIFICATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(ver_reg, f, indent=2, ensure_ascii=False)

    adapt_conn.close()
    print("[DONE] Successfully restored 6105, 3365 and updated all registries.")


if __name__ == "__main__":
    main()
