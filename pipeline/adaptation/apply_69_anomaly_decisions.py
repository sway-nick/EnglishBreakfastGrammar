"""Apply 69-Question Anomaly Review HQ Decisions and Prepare Next Main Sequential Batch.

Performs:
1. Applies exact 15 fixes to data/adaptation.db.
2. Verifies all 15 changed records deterministically.
3. Marks 15 QIDs as REVIEWED_FIX and 54 QIDs as REVIEWED_PASS in:
   - TEACHER_REVIEW_REGISTRY.json
   - TASK-025_full_teacher_review_queue.json
   - review_batch_unreviewed_anomalies_0069.json
4. Prepares next 50 UNREVIEWED questions from the MAIN queue only.
5. Emits review batch JSON & MD for the next main packet.
6. Updates VERIFICATION_REGISTRY.json.
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
        is_anom = item.get("priority_anomaly", False)

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
    print("APPLY 69-QUESTION ANOMALY REVIEW & PREPARE NEXT MAIN SEQUENTIAL BATCH")
    print("=" * 70)

    # 1. Load registry and queue
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registry_items = registry_data["questions"]

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
    queue_entries = queue_data["queue"]

    # 2. Define the 15 fixes
    fixes = {
        "141": {
            "text": "The old cabin was damaged in the flood. (badly, last summer) ⇒ The cabin {{gap_1}}.",
            "answer": "was badly damaged in the flood last summer",
            "decision": "Changed adapted_text to 'The old cabin was damaged in the flood. (badly, last summer) ⇒ The cabin {{gap_1}}.'. Answer 'was badly damaged in the flood last summer' kept.",
        },
        "143": {
            "gap_1_answer": "Ethan sometimes stays at his cousin's apartment in the evening.",
            "decision": "Changed adapted_correct_answer to 'Ethan sometimes stays at his cousin's apartment in the evening.'.",
        },
        "1955": {
            "text": "LEO: Hello Mark. Provided you {{gap_1}} spare moments, could you collect Sarah's parcel? If the train departs promptly, her transport {{gap_2}} shortly. MARK: I {{gap_3}} up the parcel willingly, but another appointment is scheduled. LEO: Can you shift the timing? MARK: A postponement sounds awkward if I {{gap_4}} our director about rescheduling. The venture succeeds provided each detail {{gap_5}} smoothly. Why not collect it yourself? LEO: I would pick up the delivery if the scooter {{gap_6}} damaged. The mechanic {{gap_7}} the engine today without replacement parts; work stalls until staff {{gap_8}} the correct bolt. MARK: How regrettable. Are you worried that Sarah {{gap_9}} irritated? LEO: In her position, I {{gap_10}} upset.",
            "answers": ["have", "will arrive", "would pick", "told", "goes", "wasn't", "won't repair", "find", "will get", "wouldn't get"],
            "decision": "Updated adapted_text with teacher approved text. All 10 answers kept.",
        },
        "2006": {
            "correct_option_text": "where I had parked",
            "decision": "Changed adapted_correct_answer to 'where I had parked'.",
        },
        "2020": {
            "gap_1_answer": "had to tell Ted that she would attend the meeting",
            "decision": "Changed adapted_correct_answer to 'had to tell Ted that she would attend the meeting'.",
        },
        "2085": {
            "text": "much many lot few little any no X: How {{gap_1}} books are in your collection? Y: I own a {{gap_2}} of them; around five hundred. However, among those novels, very {{gap_3}} are true classics. How about you? X: Well, I have {{gap_4}} interest in literature since I prefer cinema. Thus I don't read {{gap_5}} novels nowadays. Y: I don't pay {{gap_6}} attention to reading either because of my busy career. lots plenty little few X: We have {{gap_7}} tasks left today and extremely {{gap_8}} energy remaining. Y: What project are you managing? X: Accounting. Y: Relax! I have {{gap_9}} of experience with numbers, plus I have a {{gap_10}} minutes available right now. Shall we collaborate?",
            "answers": ["many", "lot", "few", "no", "any", "much", "lots of", "little", "plenty", "few"],
            "decision": "Updated adapted_text with teacher approved text. All 10 answers kept.",
        },
        "2954": {
            "text": "8 You are happy about the news. ⇒ What _____?",
            "answer": "are you happy about",
            "decision": "Changed adapted_text to '8 You are happy about the news. ⇒ What _____?'. Answer 'are you happy about' kept.",
        },
        "3528": {
            "text": "First the bell rang. Second, we had lunch. ⇒ When the bell rang, we {{gap_1}} lunch.",
            "answer": "had",
            "decision": "Changed adapted_text to 'First the bell rang. Second, we had lunch. ⇒ When the bell rang, we {{gap_1}} lunch.'. Answer 'had' kept.",
        },
        "3749": {
            "gap_1_answer": "Do you speak English at home",
            "decision": "Changed adapted_correct_answer to 'Do you speak English at home'.",
        },
        "3792": {
            "gap_1_answer": "What colour is his automobile",
            "decision": "Changed adapted_correct_answer to 'What colour is his automobile'.",
        },
        "3919": {
            "gap_1_answer": "usually practices yoga twice a day",
            "decision": "Changed adapted_correct_answer to 'usually practices yoga twice a day'.",
        },
        "4016": {
            "gap_1_answer": "why were you angry yesterday",
            "decision": "Changed adapted_correct_answer to 'why were you angry yesterday'.",
        },
        "5145": {
            "gap_1_answer": "Do you have",
            "decision": "Changed adapted_correct_answer to 'Do you have'.",
        },
        "6858": {
            "text": "Despite the dark clouds, the weather forecast predicts that Sunday will be a warm day. (still) ‣ {{gap_1}}.",
            "answer": "Sunday will still be a warm day",
            "decision": "Changed adapted_text to 'Despite the dark clouds, the weather forecast predicts that Sunday will be a warm day. (still) ‣ {{gap_1}}.'. Answer 'Sunday will still be a warm day' kept.",
        },
        "13586": {
            "text": "The mountain tunnel was damaged in the storm and remained closed for several weeks. {{gap_1}}, the mountain tunnel remained closed for several weeks.",
            "answer": "Damaged in the storm",
            "decision": "Changed adapted_text to 'The mountain tunnel was damaged in the storm and remained closed for several weeks. {{gap_1}}, the mountain tunnel remained closed for several weeks.'. Answer 'Damaged in the storm' kept.",
        },
    }

    # 3. Apply changes to adaptation.db
    adapt_conn = sqlite3.connect(ADAPTATION_DB_PATH)
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)

    with adapt_conn:
        for qid, f_data in fixes.items():
            aq_id = f"adapt_{qid}"
            sq_txt = stage_conn.execute("SELECT content FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()[0]

            if "text" in f_data:
                new_text = f_data["text"]
                sim_res = evaluate_similarity(sq_txt, new_text)
                sim_score = sim_res["jaccard_similarity"]
                adapt_conn.execute("""
                    UPDATE adapted_questions
                    SET adapted_text = ?, similarity_score = ?, adapted_by = 'HQ_TEACHER_FIX', adapted_at = ?
                    WHERE source_question_id = ?
                """, (new_text, sim_score, now_ts, qid))

            if "gap_1_answer" in f_data:
                adapt_conn.execute("""
                    UPDATE adapted_gaps
                    SET adapted_correct_answer = ?
                    WHERE adapted_question_id = ? AND gap_order = 1
                """, (f_data["gap_1_answer"], aq_id))

            if "correct_option_text" in f_data:
                adapt_conn.execute("""
                    UPDATE adapted_options
                    SET adapted_text = ?
                    WHERE adapted_question_id = ? AND adapted_is_correct = 1
                """, (f_data["correct_option_text"], aq_id))

    print("[DB] Committed 15 fixes to adaptation.db")

    # 4. Deterministic Verification of the 15 changed records
    print("\n[VERIFICATION] Verifying 15 changed records...")
    for qid, f_data in fixes.items():
        aq_id = f"adapt_{qid}"
        row = adapt_conn.execute("SELECT adapted_text, response_model FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
        rm = row[1]
        if "text" in f_data:
            assert row[0] == f_data["text"], f"Mismatch in text for QID {qid}"
        if "gap_1_answer" in f_data:
            g1 = adapt_conn.execute("SELECT adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? AND gap_order = 1", (aq_id,)).fetchone()[0]
            assert g1 == f_data["gap_1_answer"], f"Mismatch in gap 1 for QID {qid}: {g1} vs {f_data['gap_1_answer']}"
        if "correct_option_text" in f_data:
            opt = adapt_conn.execute("SELECT adapted_text FROM adapted_options WHERE adapted_question_id = ? AND adapted_is_correct = 1", (aq_id,)).fetchone()[0]
            assert opt == f_data["correct_option_text"], f"Mismatch in correct option for QID {qid}: {opt} vs {f_data['correct_option_text']}"
        print(f"  ✓ QID {qid} verified deterministically.")

    # 5. Load and update review_batch_unreviewed_anomalies_0069.json
    anom_json_path = BATCHES_DIR / "review_batch_unreviewed_anomalies_0069.json"
    with open(anom_json_path, "r", encoding="utf-8") as f:
        anom_data = json.load(f)

    anom_qids = [q["qid"] for q in anom_data["questions"]]
    assert len(anom_qids) == 69, f"Expected 69 QIDs in batch, got {len(anom_qids)}"

    for qid in anom_qids:
        curr_text = adapt_conn.execute("SELECT adapted_text FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()[0]
        if qid in fixes:
            registry_items[qid]["status"] = "REVIEWED_FIX"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = fixes[qid]["decision"]
            registry_items[qid]["adapted_content_hash"] = hash_text(curr_text)
        else:
            registry_items[qid]["status"] = "REVIEWED_PASS"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = "PASS (Valid carrier/grammar verified by HQ)"

    anom_data["metadata"]["status"] = "REVIEWED"
    anom_data["metadata"]["teacher_reviewed"] = True
    anom_data["metadata"]["reviewed_at"] = now_ts
    anom_data["metadata"]["review_summary"] = {
        "PASS_count": 54,
        "FIX_count": 15,
        "fixed_qids": list(fixes.keys()),
    }

    for q in anom_data["questions"]:
        qid = q["qid"]
        if qid in fixes:
            q["review_status"] = "REVIEWED_FIX"
        else:
            q["review_status"] = "REVIEWED_PASS"

    with open(anom_json_path, "w", encoding="utf-8") as f:
        json.dump(anom_data, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated {anom_json_path}")

    # Update Queue for the 69 anomaly items
    anom_qid_set = set(anom_qids)
    for q_entry in queue_entries:
        if q_entry["qid"] in anom_qid_set:
            if q_entry["qid"] in fixes:
                q_entry["status"] = "REVIEWED_FIX"
            else:
                q_entry["status"] = "REVIEWED_PASS"

    # 6. Prepare Next 50 UNREVIEWED Questions from MAIN Queue Only
    unreviewed_main = [
        item for item in queue_entries
        if item["status"] == "UNREVIEWED"
    ]
    assert len(unreviewed_main) >= 50, f"Not enough unreviewed items: {len(unreviewed_main)}"
    next_50_items = unreviewed_main[:50]
    next_50_qids = {item["qid"] for item in next_50_items}
    start_idx = next_50_items[0]["review_index"]
    end_idx = next_50_items[-1]["review_index"]
    batch_next_id = f"review_batch_{start_idx:04d}_{end_idx:04d}"
    batch_next_json_filename = f"{batch_next_id}.json"
    batch_next_md_filename = f"{batch_next_id}.md"
    batch_next_json_path = BATCHES_DIR / batch_next_json_filename
    batch_next_md_path = BATCHES_DIR / batch_next_md_filename

    print(f"\n[NEXT MAIN BATCH] Preparing {batch_next_id} (Indices {start_idx} to {end_idx}, count: {len(next_50_items)})")

    for qid in next_50_qids:
        registry_items[qid]["status"] = "PREPARED"
        registry_items[qid]["batch_id"] = batch_next_id
        registry_items[qid]["batch_path"] = f"data/reports/teacher_review_batches/{batch_next_json_filename}"
        registry_items[qid]["prepared_at"] = now_ts

    for q_entry in queue_entries:
        if q_entry["qid"] in next_50_qids:
            q_entry["status"] = "PREPARED"

    # Extract payloads for the next 50 using parallel workers
    prep_chunk_inputs = [
        {
            "qid": item["qid"],
            "review_index": item["review_index"],
            "priority_anomaly": False,
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

    batch_next_payload = {
        "metadata": {
            "batch_id": batch_next_id,
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

    with open(batch_next_json_path, "w", encoding="utf-8") as f:
        json.dump(batch_next_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Next Batch JSON: {batch_next_json_path}")

    # Build Markdown for Next Main Batch
    md_lines: List[str] = [
        f"# Teacher Review Packet — Batch {start_idx:04d}–{end_idx:04d}",
        "",
        f"**Generated**: {now_ts}  ",
        "**Status**: `PREPARED (PENDING HQ TEACHER REVIEW)`  ",
        f"**Range**: Queue Index `{start_idx}` to `{end_idx}` (50 questions from full corpus)  ",
        f"**Batch ID**: `{batch_next_id}`  ",
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

    with open(batch_next_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Next Batch Markdown: {batch_next_md_path}")

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
        "batch_id": batch_next_id,
        "start_index": start_idx,
        "end_index": end_idx,
        "item_count": 50,
        "status": "PREPARED",
    }
    registry_data["metadata"]["deep_scan_anomaly_review_completed"] = {
        "batch_id": "review_batch_unreviewed_anomalies_0069",
        "item_count": 69,
        "status": "REVIEWED",
        "review_results": {
            "REVIEWED_PASS": 54,
            "REVIEWED_FIX": 15,
        },
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated TEACHER_REVIEW_REGISTRY.json")

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
    ver_reg["verifications"]["teacher_review_deep_scan_anomalies_0069"] = {
        "status": "COMMITTED",
        "reviewed_at": now_ts,
        "pass_count": 54,
        "fix_count": 15,
        "fixed_qids": list(fixes.keys()),
    }
    ver_reg["verifications"]["teacher_review_batch_active"] = {
        "batch_id": batch_next_id,
        "status": "PREPARED",
        "prepared_at": now_ts,
        "item_count": 50,
        "batch_file": f"data/reports/teacher_review_batches/{batch_next_json_filename}",
    }

    with open(VERIFICATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(ver_reg, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated VERIFICATION_REGISTRY.json (new adaptation sha256: {adapt_hash_new})")

    stage_conn.close()
    adapt_conn.close()
    print("\n" + "=" * 70)
    print(f"ANOMALY REVIEW COMPLETED & NEXT MAIN BATCH {batch_next_id} PREPARED")
    print("=" * 70)


if __name__ == "__main__":
    main()
