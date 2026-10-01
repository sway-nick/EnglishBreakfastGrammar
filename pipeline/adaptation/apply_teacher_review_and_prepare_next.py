"""Apply Teacher Review Decisions for Batch 0001-0050 and Prepare Next 50 Questions (0051-0100).

Performs:
1. Applies exact teacher fixes for QID 2252 and QID 3587 to data/adaptation.db.
2. Marks 48 questions as REVIEWED_PASS and 2 questions (2252, 3587) as REVIEWED_FIX in:
   - TEACHER_REVIEW_REGISTRY.json
   - TASK-025_full_teacher_review_queue.json
   - review_batch_0001_0050.json / .md
3. Selects the next 50 UNREVIEWED questions (indices 51-100) in canonical order.
4. Marks them PREPARED in registry and queue.
5. Extracts and generates:
   - data/reports/teacher_review_batches/review_batch_0051_0100.json
   - data/reports/teacher_review_batches/review_batch_0051_0100.md
6. Updates data/reports/VERIFICATION_REGISTRY.json.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.similarity_evaluator import evaluate_similarity

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
BATCHES_DIR = REPORTS_DIR / "teacher_review_batches"
TASK021_EVIDENCE_PATH = REPORTS_DIR / "TASK-021_anomaly_evidence.json"

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


def hash_options(options: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    if not options:
        return None
    canonical_repr = json.dumps(options, sort_keys=True)
    return hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()


def load_task021_anomaly_qids() -> Set[str]:
    if not TASK021_EVIDENCE_PATH.exists():
        return set()
    with open(TASK021_EVIDENCE_PATH, "r", encoding="utf-8") as f:
        ev21 = json.load(f)
    anom_qids = set()
    for r in ev21.get("records", []):
        cat = r.get("anomaly_category", "")
        if cat == "CATEGORY_C_COLLISION_PAIR_EVIDENCE":
            anom_qids.add(str(r.get("qid_a")))
            anom_qids.add(str(r.get("qid_b")))
        else:
            anom_qids.add(str(r.get("qid")))
    return anom_qids


def worker_extract_question_details(worker_id: int, items_chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parallel read-only extraction worker."""
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    results = []
    for item in items_chunk:
        qid = item["qid"]
        rev_idx = item["review_index"]
        is_anom = item["priority_anomaly"]

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
            "review_index": rev_idx,
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
                "similarity_score": aq["similarity_score"],
                "adaptation_status": aq["adaptation_status"],
            },
            "priority_anomaly": is_anom,
        }
        results.append(payload)

    stage_conn.close()
    adapt_conn.close()
    return results


def main() -> None:
    now_ts = datetime.now(timezone.utc).isoformat()
    print("=" * 70)
    print("TEACHER REVIEW: APPLY BATCH 0001-0050 REVIEWS & PREPARE NEXT 50 (0051-0100)")
    print("=" * 70)

    # 1. Load registry and queue
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registry_items = registry_data["questions"]

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
    queue_entries = queue_data["queue"]

    # 2. Apply fixes to adaptation.db
    adapt_conn = sqlite3.connect(ADAPTATION_DB_PATH)
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)

    # Fetch source questions for similarity recomputation
    sq_2252 = stage_conn.execute("SELECT content FROM staging_questions WHERE question_id = '2252'").fetchone()[0]
    sq_3587 = stage_conn.execute("SELECT content FROM staging_questions WHERE question_id = '3587'").fetchone()[0]

    # Fix QID 2252
    aq_2252_old = adapt_conn.execute("SELECT adapted_text FROM adapted_questions WHERE source_question_id = '2252'").fetchone()[0]
    target_phrase_old = "My role {{gap_5}} registration host."
    target_phrase_new = "My role {{gap_5}} a registration host."
    assert target_phrase_old in aq_2252_old, f"Old phrase '{target_phrase_old}' not found in 2252 adapted_text"
    aq_2252_new = aq_2252_old.replace(target_phrase_old, target_phrase_new)
    sim_2252_res = evaluate_similarity(sq_2252, aq_2252_new)
    sim_2252 = sim_2252_res["jaccard_similarity"]

    # Fix QID 3587
    aq_3587_new = "Maria comes from Madrid. ⇒ {{gap_1}} from Madrid originally."
    sim_3587_res = evaluate_similarity(sq_3587, aq_3587_new)
    sim_3587 = sim_3587_res["jaccard_similarity"]

    print(f"\n[APPLY FIX 2252] Sim score: {sim_2252:.4f}")
    print(f"  New text: {aq_2252_new}")
    print(f"\n[APPLY FIX 3587] Sim score: {sim_3587:.4f}")
    print(f"  New text: {aq_3587_new}")

    with adapt_conn:
        adapt_conn.execute("""
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adapted_by = 'HQ_TEACHER_FIX', adapted_at = ?
            WHERE source_question_id = '2252'
        """, (aq_2252_new, sim_2252, now_ts))

        adapt_conn.execute("""
            UPDATE adapted_questions
            SET adapted_text = ?, similarity_score = ?, adapted_by = 'HQ_TEACHER_FIX', adapted_at = ?
            WHERE source_question_id = '3587'
        """, (aq_3587_new, sim_3587, now_ts))

    print("\n[DB] Successfully committed fixes for QIDs 2252 and 3587 to adaptation.db")

    # 3. Update Registry and Queue for Batch 1 (QIDs in review_batch_0001_0050)
    batch1_json_path = BATCHES_DIR / "review_batch_0001_0050.json"
    with open(batch1_json_path, "r", encoding="utf-8") as f:
        batch1_data = json.load(f)

    batch1_qids = [q["qid"] for q in batch1_data["questions"]]
    assert len(batch1_qids) == 50, f"Expected 50 QIDs in batch 1, got {len(batch1_qids)}"

    for qid in batch1_qids:
        if qid == "2252":
            registry_items[qid]["status"] = "REVIEWED_FIX"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = "Changed 'My role {{gap_5}} registration host.' to 'My role {{gap_5}} a registration host.'. Answer 'is' kept."
            registry_items[qid]["adapted_content_hash"] = hash_text(aq_2252_new)
        elif qid == "3587":
            registry_items[qid]["status"] = "REVIEWED_FIX"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = "Replaced adapted_text with 'Maria comes from Madrid. ⇒ {{gap_1}} from Madrid originally.'. Answer 'She\'s' kept."
            registry_items[qid]["adapted_content_hash"] = hash_text(aq_3587_new)
        else:
            registry_items[qid]["status"] = "REVIEWED_PASS"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = "PASS"

    # Update batch 1 JSON with review results
    batch1_data["metadata"]["status"] = "REVIEWED"
    batch1_data["metadata"]["teacher_reviewed"] = True
    batch1_data["metadata"]["reviewed_at"] = now_ts
    batch1_data["metadata"]["review_summary"] = {
        "PASS_count": 48,
        "FIX_count": 2,
        "fixed_qids": ["2252", "3587"]
    }
    # Update items in batch1 JSON
    for q in batch1_data["questions"]:
        if q["qid"] == "2252":
            q["review_status"] = "REVIEWED_FIX"
            q["adapted_text"] = aq_2252_new
            q["relevant_machine_flags"]["similarity_score"] = sim_2252
        elif q["qid"] == "3587":
            q["review_status"] = "REVIEWED_FIX"
            q["adapted_text"] = aq_3587_new
            q["relevant_machine_flags"]["similarity_score"] = sim_3587
        else:
            q["review_status"] = "REVIEWED_PASS"

    with open(batch1_json_path, "w", encoding="utf-8") as f:
        json.dump(batch1_data, f, indent=2, ensure_ascii=False)

    # Also update Queue status for batch 1 items
    batch1_qid_set = set(batch1_qids)
    for q_entry in queue_entries:
        if q_entry["qid"] in batch1_qid_set:
            if q_entry["qid"] == "2252":
                q_entry["status"] = "REVIEWED_FIX"
            elif q_entry["qid"] == "3587":
                q_entry["status"] = "REVIEWED_FIX"
            else:
                q_entry["status"] = "REVIEWED_PASS"

    # 4. Prepare Next 50 UNREVIEWED questions
    # Next 50 unreviewed questions in canonical order
    unreviewed_candidates = [
        item for item in queue_entries
        if item["status"] == "UNREVIEWED"
    ]
    assert len(unreviewed_candidates) >= 50, f"Not enough unreviewed questions: {len(unreviewed_candidates)}"
    next_50_items = unreviewed_candidates[:50]
    next_50_qids = {item["qid"] for item in next_50_items}
    start_idx = next_50_items[0]["review_index"]
    end_idx = next_50_items[-1]["review_index"]
    batch2_id = f"review_batch_{start_idx:04d}_{end_idx:04d}"
    batch2_json_filename = f"{batch2_id}.json"
    batch2_md_filename = f"{batch2_id}.md"
    batch2_json_path = BATCHES_DIR / batch2_json_filename
    batch2_md_path = BATCHES_DIR / batch2_md_filename

    print(f"\n[NEXT BATCH] Preparing {batch2_id} (Indices {start_idx} to {end_idx}, count: {len(next_50_items)})")

    # Mark next 50 as PREPARED in registry and queue
    for qid in next_50_qids:
        registry_items[qid]["status"] = "PREPARED"
        registry_items[qid]["batch_id"] = batch2_id
        registry_items[qid]["batch_path"] = f"data/reports/teacher_review_batches/{batch2_json_filename}"
        registry_items[qid]["prepared_at"] = now_ts

    for q_entry in queue_entries:
        if q_entry["qid"] in next_50_qids:
            q_entry["status"] = "PREPARED"

    # 5. Extract Details for Next 50 using Parallel Workers
    anomaly_qids = load_task021_anomaly_qids()
    prep_chunk_inputs = [
        {
            "qid": item["qid"],
            "review_index": item["review_index"],
            "priority_anomaly": item["qid"] in anomaly_qids
        }
        for item in next_50_items
    ]

    worker_count = 5
    chunk_size = 10
    chunks = [prep_chunk_inputs[i: i + chunk_size] for i in range(0, 50, chunk_size)]

    extracted_records: List[Dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(worker_extract_question_details, idx + 1, chunk): idx + 1 for idx, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            w_idx = futures[future]
            res = future.result()
            print(f"  Worker {w_idx} extracted {len(res)} items")
            extracted_records.extend(res)

    extracted_records.sort(key=lambda x: x["review_index"])
    assert len(extracted_records) == 50, f"Expected 50 extracted records, got {len(extracted_records)}"

    # 6. Save Batch 2 JSON and MD
    batch2_payload = {
        "metadata": {
            "batch_id": batch2_id,
            "generated_at": now_ts,
            "start_index": start_idx,
            "end_index": end_idx,
            "item_count": 50,
            "status": "PREPARED",
            "teacher_reviewed": False,
            "queue_source": "data/reports/TASK-025_full_teacher_review_queue.json",
            "notes": f"Next 50 unreviewed questions in canonical source order (indices {start_idx} to {end_idx})."
        },
        "questions": extracted_records,
    }

    with open(batch2_json_path, "w", encoding="utf-8") as f:
        json.dump(batch2_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Next Batch JSON: {batch2_json_path}")

    # Build Markdown for Batch 2
    md_lines: List[str] = [
        f"# Teacher Review Packet — Batch {start_idx:04d}–{end_idx:04d}",
        "",
        f"**Generated**: {now_ts}  ",
        "**Status**: `PREPARED (PENDING HQ TEACHER REVIEW)`  ",
        f"**Range**: Queue Index `{start_idx}` to `{end_idx}` (50 questions from full corpus)  ",
        f"**Batch ID**: `{batch2_id}`  ",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Index | QID | Level | Response Model | Exercise | Topic | Correct Answer(s) | Priority Anomaly |",
        "| :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |",
    ]

    for q in extracted_records:
        ans_str = ", ".join(q["adapted_correct_answer"]) if len(q["adapted_correct_answer"]) <= 2 else f"{q['adapted_correct_answer'][0]}... ({len(q['adapted_correct_answer'])})"
        md_lines.append(
            f"| {q['review_index']} | **{q['qid']}** | `{q['level']}` | `{q['response_model']}` | `{q['exercise_id']}` | {q['grammar_target']} | `{ans_str}` | `{'YES' if q['priority_anomaly'] else 'NO'}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Questions for HQ Review",
        "",
    ])

    for q in extracted_records:
        md_lines.append(f"### Item #{q['review_index']} — QID {q['qid']} ({q['level']})")
        md_lines.append(f"- **Exercise**: `{q['exercise_id']}` ({q['exercise_title']}) | **Topic**: `{q['grammar_target']}`")
        md_lines.append(f"- **Response Model**: `{q['response_model']}` | **Correct Answer**: `{q['adapted_correct_answer']}`")
        if q["adapted_options"]:
            opts_summary = [f"{o['text']} ({'✓' if o['is_correct'] else '✗'})" for o in q["adapted_options"]]
            md_lines.append(f"- **Options**: {', '.join(opts_summary)}")
        md_lines.append(f"- **Adapted Text**:\n  > {q['adapted_text'].replace(chr(10), ' ')}")
        md_lines.append(f"- **Source Text**:\n  > {q['source_text'].replace(chr(10), ' ')}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(batch2_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Next Batch Markdown: {batch2_md_path}")

    # 7. Update Metrics & Save Registry
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

    print("\n[UPDATED REGISTRY METRICS]")
    for k, v in status_counts.items():
        print(f"  {k}: {v}")
    print(f"  teacher_review_completed: {completed_count}")
    print(f"  teacher_review_remaining: {remaining_count}")

    registry_data["metadata"]["updated_at"] = now_ts
    registry_data["metadata"]["metrics"] = {
        **status_counts,
        "teacher_review_completed": completed_count,
        "teacher_review_remaining": remaining_count,
    }
    registry_data["metadata"]["active_batch"] = {
        "batch_id": batch2_id,
        "start_index": start_idx,
        "end_index": end_idx,
        "item_count": 50,
        "status": "PREPARED",
    }
    registry_data["metadata"]["last_completed_batch"] = {
        "batch_id": "review_batch_0001_0050",
        "start_index": 1,
        "end_index": 50,
        "item_count": 50,
        "status": "REVIEWED",
        "review_results": {
            "REVIEWED_PASS": 48,
            "REVIEWED_FIX": 2,
        },
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated TEACHER_REVIEW_REGISTRY.json")

    # Update Queue Metadata & Save Queue
    queue_data["metadata"]["last_updated"] = now_ts
    queue_data["metadata"]["status_summary"] = status_counts
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated TASK-025_full_teacher_review_queue.json")

    # 8. Update VERIFICATION_REGISTRY.json
    with open(VERIFICATION_REGISTRY_PATH, "r", encoding="utf-8") as f:
        ver_reg = json.load(f)

    adapt_hash_new = compute_sha256(ADAPTATION_DB_PATH)
    ver_reg["metadata"]["last_updated"] = now_ts
    ver_reg["verifications"]["adaptation_database_state"]["sha256"] = adapt_hash_new
    ver_reg["verifications"]["teacher_review_batch_0001_0050"] = {
        "status": "COMMITTED",
        "reviewed_at": now_ts,
        "pass_count": 48,
        "fix_count": 2,
        "fixed_qids": ["2252", "3587"],
    }
    ver_reg["verifications"]["teacher_review_batch_0051_0100"] = {
        "status": "PREPARED",
        "prepared_at": now_ts,
        "item_count": 50,
        "batch_file": f"data/reports/teacher_review_batches/{batch2_json_filename}",
    }

    with open(VERIFICATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(ver_reg, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated VERIFICATION_REGISTRY.json (new adaptation sha256: {adapt_hash_new})")

    stage_conn.close()
    adapt_conn.close()
    print("\n" + "=" * 70)
    print("ALL FIXES APPLIED & NEXT BATCH 0051-0100 PREPARED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
