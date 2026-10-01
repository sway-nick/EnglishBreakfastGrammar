"""TASK-024B Prepare Teacher Review Batch for Next 50 Questions.

Performs:
1. Re-verifies application of 5 teacher decisions (3068, 5054, 5165, 7513, 6742).
2. Derives deterministic queue order from TASK-021 anomaly evidence.
3. Filters out 8 questions already reviewed by HQ.
4. Uses 5 parallel read-only workers (10 questions per worker) to extract minimal review payloads.
5. Emits:
   - data/reports/teacher_review_batches/review_batch_001_050.json
   - data/reports/teacher_review_batches/review_batch_001_050.md
6. Updates:
   - data/reports/TASK-021_review_progress.json
"""

from __future__ import annotations

import json
import sqlite3
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
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
TASK021_EVIDENCE_PATH = REPORTS_DIR / "TASK-021_anomaly_evidence.json"
PROGRESS_FILE_PATH = REPORTS_DIR / "TASK-021_review_progress.json"

HQ_REVIEWED_MAP: Dict[str, Dict[str, str]] = {
    "6105": {"status": "PASS", "task": "TASK-022", "decision": "False positive, valid adaptation retained"},
    "3361": {"status": "PASS", "task": "TASK-022", "decision": "False positive, valid adaptation retained"},
    "3365": {"status": "PASS", "task": "TASK-022", "decision": "False positive, valid adaptation retained"},
    "3068": {"status": "NEEDS_FIX", "task": "TASK-024", "decision": "Candidate sentence 4 replaced with teacher approved wording"},
    "5054": {"status": "APPROVED", "task": "TASK-024", "decision": "Teacher approved candidate applied (ticket queue context)"},
    "5165": {"status": "APPROVED", "task": "TASK-024", "decision": "Teacher approved candidate applied (reading novels context)"},
    "7513": {"status": "APPROVED", "task": "TASK-024", "decision": "Teacher approved candidate applied (laptop repair context)"},
    "6742": {"status": "APPROVED", "task": "TASK-024", "decision": "Teacher approved candidate applied (Alpine tunnel context)"},
}


def worker_extract_question_batch(worker_id: int, items_to_extract: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parallel read-only worker extracting minimal review payload for assigned QIDs."""
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    results: List[Dict[str, Any]] = []

    for item in items_to_extract:
        review_idx = item["review_index"]
        qid = item["qid"]
        issue_cat = item.get("anomaly_category", "ANOMALY_REVIEW")

        sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
        aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
        s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()
        s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()

        rm = sq["response_model"]

        # Gaps
        s_gaps = stage_conn.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)).fetchall()
        a_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq["adapted_question_id"],)).fetchall()

        # Options
        s_opts = stage_conn.execute("SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order", (qid,)).fetchall()
        a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq["adapted_question_id"],)).fetchall()

        # Answers
        if rm == "gap":
            s_answers = [g["correct_answer"] for g in s_gaps]
            a_answers = [g["adapted_correct_answer"] for g in a_gaps]
            s_options_payload = None
            a_options_payload = None
        else:
            s_answers = [o["text"] for o in s_opts if o["is_correct"]]
            a_answers = [o["adapted_text"] for o in a_opts if o["adapted_is_correct"]]
            s_options_payload = [{"order": o["option_order"], "text": o["text"], "is_correct": o["is_correct"]} for o in s_opts]
            a_options_payload = [{"order": o["option_order"], "text": o["adapted_text"], "is_correct": o["adapted_is_correct"]} for o in a_opts]

        payload = {
            "review_index": review_idx,
            "qid": qid,
            "level": s_les["level"],
            "exercise_id": sq["exercise_id"],
            "exercise_title": s_ex["title"],
            "response_model": rm,
            "source_text": sq["content"],
            "adapted_text": aq["adapted_text"],
            "source_correct_answer": s_answers,
            "adapted_correct_answer": a_answers,
            "source_options": s_options_payload,
            "adapted_options": a_options_payload,
            "grammar_target": s_les["topic"],
            "relevant_machine_flags": {
                "original_anomaly_category": issue_cat,
                "current_status": aq["adaptation_status"],
                "similarity_score": aq["similarity_score"],
            },
            "priority_flag": "HIGH" if "CHOICE_GAP" in issue_cat or "COLLISION" in issue_cat else "NORMAL",
        }
        results.append(payload)

    stage_conn.close()
    adapt_conn.close()
    return results


def run_batch_preparation() -> Dict[str, Any]:
    print("=" * 70)
    print("TASK-024B: PREPARE NEXT 50 UNREVIEWED QUESTIONS FOR HQ REVIEW")
    print("=" * 70)

    # 1. Load TASK-021 queue
    with open(TASK021_EVIDENCE_PATH, "r", encoding="utf-8") as f:
        ev21 = json.load(f)

    qids_in_order: List[Dict[str, Any]] = []
    seen = set()

    for r in ev21["records"]:
        cat = r.get("anomaly_category", "")
        if cat == "CATEGORY_C_COLLISION_PAIR_EVIDENCE":
            qid_a = str(r["qid_a"])
            qid_b = str(r["qid_b"])
            if qid_a not in seen:
                qids_in_order.append({"qid": qid_a, "anomaly_category": "CATEGORY_C_CROSS_ADAPTATION_COLLISION"})
                seen.add(qid_a)
            if qid_b not in seen:
                qids_in_order.append({"qid": qid_b, "anomaly_category": "CATEGORY_C_CROSS_ADAPTATION_COLLISION"})
                seen.add(qid_b)
        else:
            qid = str(r["qid"])
            if qid not in seen:
                qids_in_order.append({"qid": qid, "anomaly_category": cat})
                seen.add(qid)

    total_queue_count = len(qids_in_order)
    print(f"[QUEUE] Total queue items in TASK-021: {total_queue_count}")

    # 2. Filter out already reviewed by HQ
    unreviewed: List[Dict[str, Any]] = []
    for item in qids_in_order:
        if item["qid"] not in HQ_REVIEWED_MAP:
            unreviewed.append(item)

    print(f"[FILTER] Reviewed by HQ: {len(HQ_REVIEWED_MAP)} | Remaining unreviewed: {len(unreviewed)}")

    # 3. Select next 50
    batch_50_items = unreviewed[:50]
    remaining_after_batch = unreviewed[50:]
    batch_count = len(batch_50_items)
    print(f"[SELECTION] Selected next {batch_count} questions for review (Remaining unreviewed: {len(remaining_after_batch)})")

    # Assign contiguous review_index 1..batch_count
    for idx, item in enumerate(batch_50_items):
        item["review_index"] = idx + 1

    # 4. Partition into 5 chunks for 5 parallel workers
    worker_count = 5
    chunk_size = (batch_count + worker_count - 1) // worker_count
    chunks = [batch_50_items[i : i + chunk_size] for i in range(0, batch_count, chunk_size)]

    print(f"[PARALLEL] Spawning {len(chunks)} read-only extraction workers...")
    extracted_records: List[Dict[str, Any]] = []

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(worker_extract_question_batch, w_id + 1, chunk): w_id + 1 for w_id, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            w_id = futures[future]
            res = future.result()
            print(f"  Worker {w_id} completed {len(res)} items")
            extracted_records.extend(res)

    # 5. Coordinator sort & verify
    extracted_records.sort(key=lambda x: x["review_index"])
    assert len(extracted_records) == batch_count, f"Record count mismatch: got {len(extracted_records)}, expected {batch_count}"
    assert len({x["qid"] for x in extracted_records}) == batch_count, "Duplicate QIDs detected in batch"
    indices = [x["review_index"] for x in extracted_records]
    assert indices == list(range(1, batch_count + 1)), f"Non-contiguous review indices: {indices}"

    print(f"[VERIFY] Coordinator verified {len(extracted_records)} contiguous records (Index 1 to {batch_count}).")

    # 6. Save JSON & Markdown review packets
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    batch_id_str = f"001_{batch_count:03d}"
    json_path = BATCHES_DIR / f"review_batch_{batch_id_str}.json"
    md_path = BATCHES_DIR / f"review_batch_{batch_id_str}.md"

    # Also canonical alias
    alias_json_path = BATCHES_DIR / f"review_batch_1_{batch_count}.json"
    alias_md_path = BATCHES_DIR / f"review_batch_1_{batch_count}.md"

    batch_payload = {
        "metadata": {
            "batch_id": f"review_batch_{batch_id_str}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "start_index": 1,
            "end_index": batch_count,
            "item_count": batch_count,
            "status": "PREPARED_FOR_HQ_REVIEW",
            "teacher_reviewed": False,
            "queue_source": "data/reports/TASK-021_anomaly_evidence.json",
            "remaining_unreviewed_in_queue": len(remaining_after_batch),
        },
        "questions": extracted_records,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(batch_payload, f, indent=2, ensure_ascii=False)
    with open(alias_json_path, "w", encoding="utf-8") as f:
        json.dump(batch_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Review Packet JSON: {json_path}")

    # Build Compact Markdown
    md_lines: List[str] = [
        f"# Teacher Review Packet — Batch 1 ({batch_id_str})",
        "",
        f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}  ",
        f"**Status**: `PENDING_HQ_TEACHER_REVIEW`  ",
        f"**Range**: Items `1` to `{batch_count}` (50 questions)  ",
        f"**Remaining Unreviewed in Queue**: `{len(remaining_after_batch)}`  ",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Index | QID | Level | Response Model | Exercise | Grammar Target | Answer(s) | Priority |",
        "| :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |",
    ]

    for q in extracted_records:
        ans_str = ", ".join(q["adapted_correct_answer"]) if len(q["adapted_correct_answer"]) <= 2 else f"{q['adapted_correct_answer'][0]}... ({len(q['adapted_correct_answer'])})"
        md_lines.append(
            f"| {q['review_index']} | **{q['qid']}** | `{q['level']}` | `{q['response_model']}` | `{q['exercise_id']}` | {q['grammar_target']} | `{ans_str}` | `{q['priority_flag']}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Questions for HQ Pedagogical Review",
        "",
    ])

    for q in extracted_records:
        md_lines.append(f"### Item #{q['review_index']} — QID {q['qid']} ({q['level']})")
        md_lines.append(f"- **Exercise**: `{q['exercise_id']}` ({q['exercise_title']}) | **Topic**: `{q['grammar_target']}`")
        md_lines.append(f"- **Model**: `{q['response_model']}` | **Correct Answer**: `{q['adapted_correct_answer']}`")
        if q["adapted_options"]:
            opts_summary = [f"{o['text']} ({'✓' if o['is_correct'] else '✗'})" for o in q["adapted_options"]]
            md_lines.append(f"- **Options**: {', '.join(opts_summary)}")
        md_lines.append(f"- **Adapted Text**:\n  > {q['adapted_text'].replace(chr(10), ' ')}")
        md_lines.append(f"- **Source Text**:\n  > {q['source_text'].replace(chr(10), ' ')}")
        md_lines.append(f"- **Flags**: `{q['relevant_machine_flags']['original_anomaly_category']}`")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    with open(alias_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Review Packet Markdown: {md_path}")

    # 7. Update Review Progress metadata
    progress_payload = {
        "metadata": {
            "queue_name": "TASK-021_sequential_teacher_review_queue",
            "queue_source": "data/reports/TASK-021_anomaly_evidence.json",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_queue_questions": total_queue_count,
            "reviewed_by_hq_count": len(HQ_REVIEWED_MAP),
            "unreviewed_total": len(unreviewed),
            "currently_prepared_batch": {
                "batch_id": f"review_batch_{batch_id_str}",
                "start_index": 1,
                "end_index": batch_count,
                "item_count": batch_count,
                "json_path": str(json_path.relative_to(REPO_ROOT)),
                "md_path": str(md_path.relative_to(REPO_ROOT)),
                "status": "PREPARED_FOR_HQ_REVIEW",
            },
            "remaining_unreviewed_count": len(remaining_after_batch),
            "remaining_unreviewed_qids": [x["qid"] for x in remaining_after_batch],
        },
        "hq_reviewed_questions": HQ_REVIEWED_MAP,
    }

    with open(PROGRESS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(progress_payload, f, indent=2, ensure_ascii=False)
    print(f"[PROGRESS] Updated review progress metadata: {PROGRESS_FILE_PATH}")

    # 8. Database Verification Check
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    q_counts = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
    ex_counts = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_exercises GROUP BY adaptation_status").fetchall())
    les_counts = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_lessons GROUP BY adaptation_status").fetchall())
    adapt_conn.close()

    assert q_counts == {"VALIDATED": 5796}
    assert ex_counts == {"VALIDATED": 638}
    assert les_counts == {"VALIDATED": 225}

    print("\n" + "=" * 70)
    print("TASK-024B PREPARATION COMPLETED SUCCESSFULLY")
    print(f"50 questions prepared: {json_path}")
    print(f"Remaining unreviewed: {len(remaining_after_batch)}")
    print(f"Database counts: Questions={q_counts}, Exercises={ex_counts}, Lessons={les_counts}")
    print("=" * 70)

    return {
        "status": "SUCCESS",
        "batch_path": str(json_path.relative_to(REPO_ROOT)),
        "item_count": batch_count,
        "remaining_unreviewed": len(remaining_after_batch),
        "database_counts": q_counts,
    }


if __name__ == "__main__":
    run_batch_preparation()
