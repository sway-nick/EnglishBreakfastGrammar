"""Apply Teacher Review Decisions for Batch 0101-0150 and Prepare Anomaly-Only Packet (54 items).

Performs:
1. Applies exact teacher fixes for 6 QIDs: 3682, 3698, 3699, 3720, 3721, 3723 in data/adaptation.db.
2. Marks 44 questions as REVIEWED_PASS and 6 questions as REVIEWED_FIX in:
   - TEACHER_REVIEW_REGISTRY.json
   - TASK-025_full_teacher_review_queue.json
   - review_batch_0101_0150.json / .md
3. Selects all 54 remaining UNREVIEWED anomaly questions from TASK-021 auto-audit.
4. Marks them PREPARED in registry and queue.
5. Extracts and generates:
   - data/reports/teacher_review_batches/review_batch_anomalies_0054.json
   - data/reports/teacher_review_batches/review_batch_anomalies_0054.md
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


def load_task021_ordered_anomalies() -> List[Dict[str, Any]]:
    with open(TASK021_EVIDENCE_PATH, "r", encoding="utf-8") as f:
        ev21 = json.load(f)
    records = []
    seen = set()
    for r in ev21.get("records", []):
        cat = r.get("anomaly_category", "")
        if cat == "CATEGORY_C_COLLISION_PAIR_EVIDENCE":
            for k in ["qid_a", "qid_b"]:
                qid = str(r.get(k))
                if qid not in seen:
                    records.append({"qid": qid, "anomaly_category": "CATEGORY_C_CROSS_ADAPTATION_COLLISION"})
                    seen.add(qid)
        else:
            qid = str(r.get("qid"))
            if qid not in seen:
                records.append({"qid": qid, "anomaly_category": cat})
                seen.add(qid)
    return records


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
        anom_cat = item.get("anomaly_category", "ANOMALY")

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
                "anomaly_category": anom_cat,
                "similarity_score": aq["similarity_score"],
                "adaptation_status": aq["adaptation_status"],
            },
            "priority_anomaly": True,
        }
        results.append(payload)

    stage_conn.close()
    adapt_conn.close()
    return results


def main() -> None:
    now_ts = datetime.now(timezone.utc).isoformat()
    print("=" * 70)
    print("TEACHER REVIEW: APPLY BATCH 0101-0150 & PREPARE 54 AUTO-AUDIT ANOMALIES")
    print("=" * 70)

    # 1. Load registry and queue
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registry_items = registry_data["questions"]

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
    queue_entries = queue_data["queue"]

    # 2. Apply 6 fixes to adaptation.db
    adapt_conn = sqlite3.connect(ADAPTATION_DB_PATH)
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)

    fixes = {
        "3682": {
            "new_text": "7 a wooden match ⇒ wooden {{gap_1}}",
            "decision": "Changed adapted_text to '7 a wooden match ⇒ wooden {{gap_1}}'. Answer 'matches' kept.",
        },
        "3698": {
            "new_text": "3 {{gap_1}} with the recent promotion?",
            "decision": "Changed adapted_text to '3 {{gap_1}} with the recent promotion?'. Answer 'Is he satisfied' kept.",
        },
        "3699": {
            "new_text": "4 Maria started {{gap_1}}.",
            "decision": "Changed adapted_text to '4 Maria started {{gap_1}}.'. Answer 'an exciting career' kept.",
        },
        "3720": {
            "new_text": "The view from the mountain {{gap_1}}. Everyone agrees it is {{gap_2}}.",
            "decision": "Changed adapted_text to 'The view from the mountain {{gap_1}}. Everyone agrees it is {{gap_2}}.'. Answers 'is amazing', 'an amazing view' kept.",
        },
        "3721": {
            "new_text": "The situation at work {{gap_1}}. It has become {{gap_2}}.",
            "decision": "Changed adapted_text to 'The situation at work {{gap_1}}. It has become {{gap_2}}.'. Answers 'is difficult', 'a difficult situation' kept.",
        },
        "3723": {
            "new_text": "Gotham is {{gap_1}}. This city {{gap_2}}.",
            "decision": "Changed adapted_text to 'Gotham is {{gap_1}}. This city {{gap_2}}.'. Answers 'a dangerous city', 'is dangerous' kept.",
        },
    }

    new_sims = {}
    with adapt_conn:
        for qid, fix_info in fixes.items():
            sq_txt = stage_conn.execute("SELECT content FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()[0]
            new_text = fix_info["new_text"]
            sim_res = evaluate_similarity(sq_txt, new_text)
            sim_score = sim_res["jaccard_similarity"]
            new_sims[qid] = sim_score

            adapt_conn.execute("""
                UPDATE adapted_questions
                SET adapted_text = ?, similarity_score = ?, adapted_by = 'HQ_TEACHER_FIX', adapted_at = ?
                WHERE source_question_id = ?
            """, (new_text, sim_score, now_ts, qid))

            print(f"[APPLY FIX {qid}] Sim: {sim_score:.4f} | New text: {new_text}")

    print("\n[DB] Successfully committed 6 fixes to adaptation.db")

    # 3. Update Registry and Queue for Batch 3 (QIDs in review_batch_0101_0150)
    batch3_json_path = BATCHES_DIR / "review_batch_0101_0150.json"
    with open(batch3_json_path, "r", encoding="utf-8") as f:
        batch3_data = json.load(f)

    batch3_qids = [q["qid"] for q in batch3_data["questions"]]
    assert len(batch3_qids) == 50, f"Expected 50 QIDs in batch 3, got {len(batch3_qids)}"

    for qid in batch3_qids:
        if qid in fixes:
            registry_items[qid]["status"] = "REVIEWED_FIX"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = fixes[qid]["decision"]
            registry_items[qid]["adapted_content_hash"] = hash_text(fixes[qid]["new_text"])
        else:
            registry_items[qid]["status"] = "REVIEWED_PASS"
            registry_items[qid]["reviewed_by"] = "HQ"
            registry_items[qid]["reviewed_at"] = now_ts
            registry_items[qid]["teacher_decision"] = "PASS"

    # Update batch 3 JSON
    batch3_data["metadata"]["status"] = "REVIEWED"
    batch3_data["metadata"]["teacher_reviewed"] = True
    batch3_data["metadata"]["reviewed_at"] = now_ts
    batch3_data["metadata"]["review_summary"] = {
        "PASS_count": 44,
        "FIX_count": 6,
        "fixed_qids": list(fixes.keys()),
    }
    for q in batch3_data["questions"]:
        qid = q["qid"]
        if qid in fixes:
            q["review_status"] = "REVIEWED_FIX"
            q["adapted_text"] = fixes[qid]["new_text"]
            q["relevant_machine_flags"]["similarity_score"] = new_sims[qid]
        else:
            q["review_status"] = "REVIEWED_PASS"

    with open(batch3_json_path, "w", encoding="utf-8") as f:
        json.dump(batch3_data, f, indent=2, ensure_ascii=False)

    batch3_qid_set = set(batch3_qids)
    for q_entry in queue_entries:
        if q_entry["qid"] in batch3_qid_set:
            if q_entry["qid"] in fixes:
                q_entry["status"] = "REVIEWED_FIX"
            else:
                q_entry["status"] = "REVIEWED_PASS"

    # 4. Prepare Anomaly-Only Batch (54 Questions)
    ordered_anomalies = load_task021_ordered_anomalies()
    unreviewed_anomalies = [
        item for item in ordered_anomalies
        if registry_items.get(item["qid"], {}).get("status") in ["UNREVIEWED", "PREPARED"]
    ]
    print(f"\n[ANOMALIES] Remaining unreviewed anomalies count: {len(unreviewed_anomalies)}")

    # Map review_index from queue
    queue_idx_map = {item["qid"]: item["review_index"] for item in queue_entries}
    prep_anomaly_items = []
    for item in unreviewed_anomalies:
        qid = item["qid"]
        prep_anomaly_items.append({
            "qid": qid,
            "review_index": queue_idx_map.get(qid, 0),
            "anomaly_category": item["anomaly_category"],
            "priority_anomaly": True,
        })

    anom_batch_id = f"review_batch_anomalies_{len(prep_anomaly_items):04d}"
    anom_json_filename = f"{anom_batch_id}.json"
    anom_md_filename = f"{anom_batch_id}.md"
    anom_json_path = BATCHES_DIR / anom_json_filename
    anom_md_path = BATCHES_DIR / anom_md_filename

    # Mark anomalies as PREPARED
    anom_qid_set = {item["qid"] for item in prep_anomaly_items}
    for qid in anom_qid_set:
        registry_items[qid]["status"] = "PREPARED"
        registry_items[qid]["batch_id"] = anom_batch_id
        registry_items[qid]["batch_path"] = f"data/reports/teacher_review_batches/{anom_json_filename}"
        registry_items[qid]["prepared_at"] = now_ts

    for q_entry in queue_entries:
        if q_entry["qid"] in anom_qid_set:
            q_entry["status"] = "PREPARED"

    # 5. Extract Anomaly Payloads using Parallel Workers
    worker_count = 5
    chunk_size = 11
    chunks = [prep_anomaly_items[i: i + chunk_size] for i in range(0, len(prep_anomaly_items), chunk_size)]

    extracted_records: List[Dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(worker_extract_question_details, idx + 1, chunk): idx + 1 for idx, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            w_idx = futures[future]
            res = future.result()
            print(f"  Worker {w_idx} extracted {len(res)} items")
            extracted_records.extend(res)

    # Sort in order of presentation
    extracted_records.sort(key=lambda x: (x["relevant_machine_flags"]["anomaly_category"], x["review_index"]))
    assert len(extracted_records) == len(prep_anomaly_items)

    # 6. Save Anomaly Batch JSON and MD
    anom_payload = {
        "metadata": {
            "batch_id": anom_batch_id,
            "generated_at": now_ts,
            "item_count": len(extracted_records),
            "status": "PREPARED",
            "teacher_reviewed": False,
            "focus": "AUTO-AUDIT ANOMALIES ONLY (TASK-021 Flagged Questions)",
            "queue_source": "data/reports/TASK-021_anomaly_evidence.json",
            "notes": "All 54 remaining questions flagged during automated audits for teacher evaluation."
        },
        "questions": extracted_records,
    }

    with open(anom_json_path, "w", encoding="utf-8") as f:
        json.dump(anom_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Anomaly Batch JSON: {anom_json_path}")

    # Build Markdown
    md_lines: List[str] = [
        f"# Teacher Review Packet — Auto-Audit Anomalies ({len(extracted_records)} Questions)",
        "",
        f"**Generated**: {now_ts}  ",
        "**Status**: `PREPARED (PENDING HQ TEACHER REVIEW)`  ",
        f"**Focus**: Auto-Audit Flagged Questions (TASK-021)  ",
        f"**Batch ID**: `{anom_batch_id}`  ",
        f"**Total Questions**: {len(extracted_records)}  ",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| # | QID | Level | Response Model | Anomaly Category | Exercise | Topic | Correct Answer(s) |",
        "| :---: | :---: | :---: | :---: | :--- | :---: | :--- | :--- |",
    ]

    for idx, q in enumerate(extracted_records, 1):
        ans_str = ", ".join(q["adapted_correct_answer"]) if len(q["adapted_correct_answer"]) <= 2 else f"{q['adapted_correct_answer'][0]}... ({len(q['adapted_correct_answer'])})"
        cat_short = q["relevant_machine_flags"]["anomaly_category"].replace("CATEGORY_", "").replace("_", " ")
        md_lines.append(
            f"| {idx} | **{q['qid']}** | `{q['level']}` | `{q['response_model']}` | `{cat_short}` | `{q['exercise_id']}` | {q['grammar_target']} | `{ans_str}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Questions for HQ Review",
        "",
    ])

    for idx, q in enumerate(extracted_records, 1):
        cat_short = q["relevant_machine_flags"]["anomaly_category"].replace("CATEGORY_", "").replace("_", " ")
        md_lines.append(f"### Item #{idx} — QID {q['qid']} ({q['level']}) — [{cat_short}]")
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

    with open(anom_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Anomaly Batch Markdown: {anom_md_path}")

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
        "batch_id": anom_batch_id,
        "item_count": len(extracted_records),
        "status": "PREPARED",
        "focus": "AUTO-AUDIT ANOMALIES",
    }
    registry_data["metadata"]["last_completed_batch"] = {
        "batch_id": "review_batch_0101_0150",
        "start_index": 101,
        "end_index": 150,
        "item_count": 50,
        "status": "REVIEWED",
        "review_results": {
            "REVIEWED_PASS": 44,
            "REVIEWED_FIX": 6,
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
    ver_reg["verifications"]["teacher_review_batch_0101_0150"] = {
        "status": "COMMITTED",
        "reviewed_at": now_ts,
        "pass_count": 44,
        "fix_count": 6,
        "fixed_qids": list(fixes.keys()),
    }
    ver_reg["verifications"]["teacher_review_batch_anomalies_0054"] = {
        "status": "PREPARED",
        "prepared_at": now_ts,
        "item_count": len(extracted_records),
        "batch_file": f"data/reports/teacher_review_batches/{anom_json_filename}",
    }

    with open(VERIFICATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(ver_reg, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Updated VERIFICATION_REGISTRY.json (new adaptation sha256: {adapt_hash_new})")

    stage_conn.close()
    adapt_conn.close()
    print("\n" + "=" * 70)
    print("ALL 6 FIXES COMMITTED & 54 AUTO-AUDIT ANOMALIES PREPARED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
