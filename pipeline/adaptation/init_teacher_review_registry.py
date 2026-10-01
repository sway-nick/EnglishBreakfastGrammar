"""TASK-025 Initialize the Full 5,796-Question Teacher Review Registry.

Performs:
1. Reconstructs canonical source-corpus ordering for all 5,796 questions from staging.db.
2. Preserves the 5 already completed HQ decisions (3068, 5054, 5165, 7513, 6742) as FIX_APPLIED.
3. Initializes TEACHER_REVIEW_REGISTRY.json covering all 5,796 questions with change detection hashes.
4. Initializes TASK-025_full_teacher_review_queue.json with 5,796 entries.
5. Selects the first 50 eligible questions from the full queue, marks them PREPARED.
6. Uses 5 parallel read-only workers (~10 items each) to extract the minimal review payload.
7. Emits:
   - data/reports/teacher_review_batches/review_batch_0001_0050.json
   - data/reports/teacher_review_batches/review_batch_0001_0050.md
8. Creates lightweight data/reports/VERIFICATION_REGISTRY.json.
9. Zero modifications to adaptation.db, staging.db, or question content.
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

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
BATCHES_DIR = REPORTS_DIR / "teacher_review_batches"
TASK021_EVIDENCE_PATH = REPORTS_DIR / "TASK-021_anomaly_evidence.json"

REGISTRY_PATH = REPORTS_DIR / "TEACHER_REVIEW_REGISTRY.json"
QUEUE_PATH = REPORTS_DIR / "TASK-025_full_teacher_review_queue.json"
VERIFICATION_REGISTRY_PATH = REPORTS_DIR / "VERIFICATION_REGISTRY.json"

EXPECTED_STAGING_SHA256 = "3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded"
EXPECTED_ADAPT_SHA256 = "5101bc4690e766ffb443d48dbd6348ea142cfe3720e1aab940e57b7cbf44f60b"

HQ_FIX_APPLIED_QIDS = {
    "3068": {
        "status": "FIX_APPLIED",
        "reviewed_by": "HQ",
        "review_source": "TASK-023/TASK-024",
        "review_timestamp": "2026-10-01T12:12:43.586420+00:00",
        "correction_artifact": "data/reports/TASK-024_teacher_decision_application.json",
        "note": "Teacher approved wording applied for gap 4",
    },
    "5054": {
        "status": "FIX_APPLIED",
        "reviewed_by": "HQ",
        "review_source": "TASK-023/TASK-024",
        "review_timestamp": "2026-10-01T12:12:43.586420+00:00",
        "correction_artifact": "data/reports/TASK-024_teacher_decision_application.json",
        "note": "Teacher approved candidate applied (ticket queue context)",
    },
    "5165": {
        "status": "FIX_APPLIED",
        "reviewed_by": "HQ",
        "review_source": "TASK-023/TASK-024",
        "review_timestamp": "2026-10-01T12:12:43.586420+00:00",
        "correction_artifact": "data/reports/TASK-024_teacher_decision_application.json",
        "note": "Teacher approved candidate applied (reading novels context)",
    },
    "7513": {
        "status": "FIX_APPLIED",
        "reviewed_by": "HQ",
        "review_source": "TASK-023/TASK-024",
        "review_timestamp": "2026-10-01T12:12:43.586420+00:00",
        "correction_artifact": "data/reports/TASK-024_teacher_decision_application.json",
        "note": "Teacher approved candidate applied (laptop repair context)",
    },
    "6742": {
        "status": "FIX_APPLIED",
        "reviewed_by": "HQ",
        "review_source": "TASK-023/TASK-024",
        "review_timestamp": "2026-10-01T12:12:43.586420+00:00",
        "correction_artifact": "data/reports/TASK-024_teacher_decision_application.json",
        "note": "Teacher approved candidate applied (Alpine tunnel context)",
    },
}


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
    print("=" * 70)
    print("TASK-025: INITIALIZE FULL 5,796-QUESTION TEACHER REVIEW REGISTRY")
    print("=" * 70)

    # 1. Database Immutability Check
    staging_hash = compute_sha256(STAGING_DB_PATH)
    assert staging_hash == EXPECTED_STAGING_SHA256, f"Staging hash mismatch: {staging_hash}"
    adapt_hash = compute_sha256(ADAPTATION_DB_PATH)
    assert adapt_hash == EXPECTED_ADAPT_SHA256, f"Adaptation hash mismatch: {adapt_hash}"
    print(f"[CHECK] Staging DB SHA-256 verified:    {staging_hash}")
    print(f"[CHECK] Adaptation DB SHA-256 verified: {adapt_hash}")

    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    # Verify counts
    q_count = stage_conn.execute("SELECT COUNT(*) FROM staging_questions").fetchone()[0]
    assert q_count == 5796, f"Expected 5796 questions, found {q_count}"
    print(f"[CHECK] Question count: {q_count} (100% matched)")

    # 2. Extract Canonical Source-Corpus Ordering
    # In staging.db, rowid (1..5796) strictly reflects lesson -> exercise -> question natural order
    canonical_rows = stage_conn.execute("""
        SELECT q.rowid, q.question_id, q.exercise_id, l.level, l.lesson_id, e.exercise_order, q.question_order, q.content, q.response_model
        FROM staging_questions q
        JOIN staging_exercises e ON q.exercise_id = e.exercise_id
        JOIN staging_lessons l ON q.lesson_id = l.lesson_id
        ORDER BY q.rowid
    """).fetchall()

    assert len(canonical_rows) == 5796, f"Mismatch in canonical rows count: {len(canonical_rows)}"
    anomaly_qids = load_task021_anomaly_qids()
    print(f"[CATALOG] Loaded {len(canonical_rows)} canonical questions. Anomaly QID count: {len(anomaly_qids)}")

    # 3. Build Full Sequential Review Queue & Initial Registry Entries
    queue_entries: List[Dict[str, Any]] = []
    registry_items: Dict[str, Dict[str, Any]] = {}

    # Candidate for next 50: first 50 that are NOT in HQ_FIX_APPLIED_QIDS
    eligible_for_batch_50: List[Dict[str, Any]] = []

    for row in canonical_rows:
        qid = str(row["question_id"])
        rev_idx = row["rowid"]  # 1 to 5796
        lvl = row["level"]
        ex_id = row["exercise_id"]

        # Fetch adapted data for hashing
        aq = adapt_conn.execute("SELECT adapted_text, adapted_question_id FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
        a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq["adapted_question_id"],)).fetchall()
        s_opts = stage_conn.execute("SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order", (qid,)).fetchall()

        s_hash = hash_text(row["content"])
        a_hash = hash_text(aq["adapted_text"])
        opt_hash = hash_options([dict(o) for o in a_opts]) if a_opts else None

        if qid in HQ_FIX_APPLIED_QIDS:
            hq_info = HQ_FIX_APPLIED_QIDS[qid]
            status = "FIX_APPLIED"
            registry_entry = {
                "qid": qid,
                "review_index": rev_idx,
                "level": lvl,
                "exercise_id": ex_id,
                "status": status,
                "reviewed_by": hq_info["reviewed_by"],
                "review_source": hq_info["review_source"],
                "review_timestamp": hq_info["review_timestamp"],
                "correction_artifact": hq_info["correction_artifact"],
                "teacher_decision": hq_info["note"],
                "source_content_hash": s_hash,
                "adapted_content_hash": a_hash,
                "options_hash": opt_hash,
                "priority_anomaly": qid in anomaly_qids,
            }
        else:
            status = "UNREVIEWED"
            registry_entry = {
                "qid": qid,
                "review_index": rev_idx,
                "level": lvl,
                "exercise_id": ex_id,
                "status": status,
                "source_content_hash": s_hash,
                "adapted_content_hash": a_hash,
                "options_hash": opt_hash,
                "priority_anomaly": qid in anomaly_qids,
            }
            if len(eligible_for_batch_50) < 50:
                eligible_for_batch_50.append({
                    "qid": qid,
                    "review_index": rev_idx,
                    "priority_anomaly": qid in anomaly_qids,
                })

        registry_items[qid] = registry_entry
        queue_entries.append({
            "review_index": rev_idx,
            "qid": qid,
            "level": lvl,
            "exercise_id": ex_id,
            "status": status,
        })

    stage_conn.close()
    adapt_conn.close()

    assert len(eligible_for_batch_50) == 50, f"Expected 50 eligible questions, got {len(eligible_for_batch_50)}"
    prepared_qids = {item["qid"] for item in eligible_for_batch_50}

    # Mark the 50 as PREPARED in registry and queue
    for qid in prepared_qids:
        registry_items[qid]["status"] = "PREPARED"
        registry_items[qid]["batch_id"] = "review_batch_0001_0050"
        registry_items[qid]["batch_path"] = "data/reports/teacher_review_batches/review_batch_0001_0050.json"
        registry_items[qid]["prepared_at"] = datetime.now(timezone.utc).isoformat()

    for q_entry in queue_entries:
        if q_entry["qid"] in prepared_qids:
            q_entry["status"] = "PREPARED"

    # 4. Extract Review Payload for the 50 using 5 Parallel Workers
    print(f"\n[PARALLEL] Extracting review payload for 50 questions across 5 workers...")
    worker_count = 5
    chunk_size = 10
    chunks = [eligible_for_batch_50[i : i + chunk_size] for i in range(0, 50, chunk_size)]

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
    assert [x["review_index"] for x in extracted_records] == list(range(1, 51)), "Indices mismatch"

    # 5. Calculate Status Metrics
    status_counts = {
        "TOTAL": 5796,
        "UNREVIEWED": sum(1 for v in registry_items.values() if v["status"] == "UNREVIEWED"),
        "PREPARED": sum(1 for v in registry_items.values() if v["status"] == "PREPARED"),
        "PASS": sum(1 for v in registry_items.values() if v["status"] == "PASS"),
        "NEEDS_FIX": sum(1 for v in registry_items.values() if v["status"] == "NEEDS_FIX"),
        "FIX_APPLIED": sum(1 for v in registry_items.values() if v["status"] == "FIX_APPLIED"),
        "RECHECK_REQUIRED": sum(1 for v in registry_items.values() if v["status"] == "RECHECK_REQUIRED"),
    }
    completed_count = status_counts["PASS"] + status_counts["FIX_APPLIED"]
    remaining_count = status_counts["UNREVIEWED"] + status_counts["PREPARED"] + status_counts["RECHECK_REQUIRED"]

    assert status_counts["TOTAL"] == 5796
    assert status_counts["PREPARED"] == 50
    assert status_counts["FIX_APPLIED"] == 5
    assert status_counts["UNREVIEWED"] == 5741
    assert completed_count == 5
    assert remaining_count == 5791

    print("\n[REGISTRY METRICS]")
    for k, v in status_counts.items():
        print(f"  {k}: {v}")
    print(f"  teacher_review_completed: {completed_count}")
    print(f"  teacher_review_remaining: {remaining_count}")

    # 6. Write TEACHER_REVIEW_REGISTRY.json
    registry_payload = {
        "metadata": {
            "registry_name": "TEACHER_REVIEW_REGISTRY",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_corpus": "Universal English Test Platform (5,796 questions)",
            "metrics": {
                **status_counts,
                "teacher_review_completed": completed_count,
                "teacher_review_remaining": remaining_count,
            },
            "active_batch": {
                "batch_id": "review_batch_0001_0050",
                "start_index": 1,
                "end_index": 50,
                "item_count": 50,
                "status": "PREPARED",
            },
        },
        "questions": registry_items,
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_payload, f, indent=2, ensure_ascii=False)
    print(f"\n[OUTPUT] Saved Teacher Review Registry: {REGISTRY_PATH}")

    # 7. Write TASK-025_full_teacher_review_queue.json
    queue_payload = {
        "metadata": {
            "queue_name": "TASK-025_full_teacher_review_queue",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": 5796,
            "ordering_strategy": "Canonical source-corpus rowid order (level -> lesson -> exercise_order -> question_order)",
            "status_summary": status_counts,
        },
        "queue": queue_entries,
    }

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Full Review Queue: {QUEUE_PATH}")

    # 8. Save review_batch_0001_0050.json & .md
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    batch_json_path = BATCHES_DIR / "review_batch_0001_0050.json"
    batch_md_path = BATCHES_DIR / "review_batch_0001_0050.md"

    batch_payload = {
        "metadata": {
            "batch_id": "review_batch_0001_0050",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "start_index": 1,
            "end_index": 50,
            "item_count": 50,
            "status": "PREPARED",
            "teacher_reviewed": False,
            "queue_source": "data/reports/TASK-025_full_teacher_review_queue.json",
            "notes": "First 50 questions from full 5,796-question corpus in canonical source order (Quiz 258, 259, 417, 418, 419, 420)."
        },
        "questions": extracted_records,
    }

    with open(batch_json_path, "w", encoding="utf-8") as f:
        json.dump(batch_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Review Batch JSON: {batch_json_path}")

    # Build Markdown
    md_lines: List[str] = [
        "# Teacher Review Packet — Batch 0001–0050",
        "",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}  ",
        "**Status**: `PREPARED (PENDING HQ TEACHER REVIEW)`  ",
        "**Range**: Queue Index `1` to `50` (50 questions from full corpus)  ",
        "**Total Corpus Progress**: 5 reviewed / 5,791 remaining  ",
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

    with open(batch_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Review Batch Markdown: {batch_md_path}")

    # 9. Create lightweight VERIFICATION_REGISTRY.json
    verification_payload = {
        "metadata": {
            "registry_name": "VERIFICATION_REGISTRY",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "policy": "DONE ONCE = DO NOT RECHECK unless dependencies change",
        },
        "verifications": {
            "full_corpus_audit": {
                "source_task": "TASK-020",
                "result": "PASS",
                "scope": "5,796 questions, 638 exercises, 225 lessons",
                "dependencies": ["data/staging.db", "data/adaptation.db"],
            },
            "preview_gate": {
                "source_task": "TASK-022",
                "result": "PASS (225 / 225 lessons valid)",
                "dependencies": ["data/adaptation.db"],
            },
            "python_test_suite": {
                "source_task": "TASK-022",
                "result": "PASS (40 / 40 tests)",
                "dependencies": ["pipeline/", "tests/"],
            },
            "jest_test_suite": {
                "source_task": "TASK-022",
                "result": "PASS (24 / 24 tests)",
                "dependencies": ["src/"],
            },
            "staging_database_immutability": {
                "sha256": EXPECTED_STAGING_SHA256,
                "result": "VERIFIED_UNCHANGED",
                "dependencies": ["data/staging.db"],
            },
            "adaptation_database_state": {
                "sha256": EXPECTED_ADAPT_SHA256,
                "counts": {"questions_validated": 5796, "rejected": 0, "pending": 0},
                "result": "VALIDATED",
                "dependencies": ["data/adaptation.db"],
            },
            "teacher_decisions_applied": {
                "source_task": "TASK-024",
                "result": "COMMITTED (QIDs 3068, 5054, 5165, 7513, 6742)",
                "dependencies": ["data/reports/TASK-024_teacher_decision_application.json"],
            },
        },
    }

    with open(VERIFICATION_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(verification_payload, f, indent=2, ensure_ascii=False)
    print(f"[OUTPUT] Saved Verification Registry: {VERIFICATION_REGISTRY_PATH}")

    print("\n" + "=" * 70)
    print("TASK-025 INITIALIZATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
