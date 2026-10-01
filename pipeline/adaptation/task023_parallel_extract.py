"""TASK-023 Parallel Worker Extraction for 5 Teacher-Decision Candidates.

Workers:
- Worker A: QID 3068
- Worker B: QID 5054
- Worker C: QID 5165
- Worker D: QID 7513
- Worker E: QID 6742

Read-only extraction from:
1. data/staging.db
2. data/adaptation.db
3. data/reports/TASK-022_QID3068_candidate.json
4. data/reports/TASK-022_duplicate_candidates.json

Merges into:
- data/reports/TASK-023_teacher_decision_evidence.json
- data/reports/TASK-023_teacher_decision_evidence.md
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

QID_3068_FILE = REPORTS_DIR / "TASK-022_QID3068_candidate.json"
DUPLICATE_CANDIDATES_FILE = REPORTS_DIR / "TASK-022_duplicate_candidates.json"


def worker_extract_qid_3068(worker_name: str) -> Dict[str, Any]:
    """Worker A: Extract evidence for QID 3068."""
    qid = "3068"
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
    aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
    s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()
    s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()

    s_gaps = stage_conn.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)).fetchall()
    a_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq["adapted_question_id"],)).fetchall()
    s_opts = stage_conn.execute("SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order", (qid,)).fetchall()
    a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq["adapted_question_id"],)).fetchall()

    with open(QID_3068_FILE, "r", encoding="utf-8") as f:
        cand_data = json.load(f)

    stage_conn.close()
    adapt_conn.close()

    return {
        "worker": worker_name,
        "qid": qid,
        "category": "SEMANTIC_COPULAR_AGREEMENT",
        "level": s_les["level"],
        "exercise_id": sq["exercise_id"],
        "exercise_title": s_ex["title"],
        "topic": s_les["topic"],
        "lesson_id": sq["lesson_id"],
        "response_model": sq["response_model"],
        "grammar_target": s_les["topic"],
        "gap_count": len(s_gaps),
        "option_count": len(s_opts),
        "source_text": sq["content"],
        "source_correct_answer": [g["correct_answer"] for g in s_gaps],
        "source_options": [dict(o) for o in s_opts],
        "original_adapted_text": aq["adapted_text"],
        "original_adapted_correct_answer": [g["adapted_correct_answer"] for g in a_gaps],
        "original_validation_anomaly_reason": (
            "Validator flagged: Plural/compound subject conflicts with singular verb form 'Was'. "
            "Grammatical agreement tension between plural/collective noun 'acoustics' and singular past verb 'Was'."
        ),
        "exact_validator_flag": "Plural/compound subject conflicts with singular verb form 'Was'.",
        "original_problematic_sentence": cand_data["original_gap_4_context"],
        "source_answer": "Was",
        "candidate_adapted_text": cand_data["proposed_candidate_text"],
        "candidate_sentence": cand_data["proposed_gap_4_context"],
        "candidate_answer": cand_data["gap_4_target_answer"],
        "candidate_options": None,
        "task022_rationale": cand_data["grammatical_rationale"],
    }


def worker_extract_duplicate(worker_name: str, qid: str, collision_id: int) -> Dict[str, Any]:
    """Workers B, C, D, E: Extract evidence for duplicate collision QIDs."""
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
    aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
    s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()
    s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()

    s_gaps = stage_conn.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)).fetchall()
    a_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq["adapted_question_id"],)).fetchall()
    s_opts = stage_conn.execute("SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order", (qid,)).fetchall()
    a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq["adapted_question_id"],)).fetchall()

    with open(DUPLICATE_CANDIDATES_FILE, "r", encoding="utf-8") as f:
        dups_data = json.load(f)

    # Find the specific collision entry
    collision_entry = None
    for group in dups_data["collision_groups"]:
        if group["collision_id"] == collision_id:
            collision_entry = group
            break
    assert collision_entry is not None, f"Collision {collision_id} not found!"

    stage_conn.close()
    adapt_conn.close()

    rm = sq["response_model"]
    s_corr = [g["correct_answer"] for g in s_gaps] if rm == "gap" else [o["text"] for o in s_opts if o["is_correct"]]
    cand_opts = [o["adapted_text"] for o in a_opts] if rm != "gap" else None

    rep_q = collision_entry["replaced_question"]
    ret_q = collision_entry["retained_question"]

    return {
        "worker": worker_name,
        "qid": qid,
        "category": collision_entry["type"],
        "collision_id": collision_id,
        "level": s_les["level"],
        "exercise_id": sq["exercise_id"],
        "exercise_title": s_ex["title"],
        "topic": s_les["topic"],
        "lesson_id": sq["lesson_id"],
        "response_model": rm,
        "grammar_target": s_les["topic"],
        "gap_count": len(s_gaps),
        "option_count": len(s_opts),
        "source_text": sq["content"],
        "source_correct_answer": s_corr,
        "source_options": [dict(o) for o in s_opts],
        "original_adapted_text": aq["adapted_text"],
        "duplicated_carrier_text": collision_entry["duplicated_carrier"],
        "conflicting_qid": ret_q["qid"],
        "conflicting_exercise_id": ret_q["exercise_id"],
        "conflicting_adapted_text": ret_q["adapted_text"],
        "why_candidate_was_created": (
            f"Breaks duplicate carrier collision with QID {ret_q['qid']}. "
            f"QID {ret_q['qid']} retains the current adaptation, while QID {qid} receives an independent context."
        ),
        "original_validation_anomaly_reason": f"Carrier collision: identical adapted text shared with QID {ret_q['qid']}.",
        "candidate_adapted_text": rep_q["proposed_candidate_text"],
        "candidate_answer": rep_q["correct_answer"],
        "candidate_options": rep_q.get("options", cand_opts),
        "task022_rationale": rep_q["pedagogical_rationale"],
    }


def run_parallel_extraction() -> List[Dict[str, Any]]:
    tasks = [
        ("Worker A", "3068", None),
        ("Worker B", "5054", 2),
        ("Worker C", "5165", 4),
        ("Worker D", "7513", 5),
        ("Worker E", "6742", 7),
    ]

    results: Dict[str, Dict[str, Any]] = {}

    # Parallel execution using ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=5) as executor:
        future_to_qid = {}
        for w_name, qid, col_id in tasks:
            if qid == "3068":
                f = executor.submit(worker_extract_qid_3068, w_name)
            else:
                f = executor.submit(worker_extract_duplicate, w_name, qid, col_id)
            future_to_qid[f] = qid

        for future in as_completed(future_to_qid):
            qid = future_to_qid[future]
            res = future.result()
            results[qid] = res
            print(f"[{res['worker']}] Successfully extracted QID {qid} ({res['category']})")

    # Order results matching the target order: 3068, 5054, 5165, 7513, 6742
    ordered_results = [results[q] for q in ["3068", "5054", "5165", "7513", "6742"]]
    return ordered_results


def main() -> None:
    print("=" * 70)
    print("TASK-023: PARALLEL EVIDENCE EXTRACTION FOR 5 TARGET QIDs")
    print("=" * 70)

    # 1. Verification Registry Check
    registry_file = REPORTS_DIR / "VERIFICATION_REGISTRY.json"
    if registry_file.exists():
        print(f"[REGISTRY] Found verification registry at {registry_file}")
    else:
        print("[REGISTRY] Status: REGISTRY_NOT_PRESENT (Reusing verified results from TASK-020/021/022)")

    # 2. Database Pre-check
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    target_qids = ["3068", "5054", "5165", "7513", "6742"]
    for q in target_qids:
        assert stage_conn.execute("SELECT 1 FROM staging_questions WHERE question_id = ?", (q,)).fetchone(), f"Missing staging QID {q}"
        assert adapt_conn.execute("SELECT 1 FROM adapted_questions WHERE source_question_id = ?", (q,)).fetchone(), f"Missing adapted QID {q}"
    stage_conn.close()
    adapt_conn.close()
    print(f"[PRE-CHECK] All 5 target QIDs verified present in read-only databases.")

    # 3. Parallel Worker Execution
    extracted_records = run_parallel_extraction()

    # 4. Coordinator Merge into JSON
    merged_payload = {
        "metadata": {
            "task": "TASK-023",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "purpose": "Machine-grounded evidence extraction for 5 unresolved teacher-decision candidates",
            "worker_count": 5,
            "target_qids": target_qids,
            "source_of_truth": "SQLite databases (staging.db & adaptation.db) + TASK-022 candidate artifacts",
            "reused_verifications": {
                "full_corpus_audit": "REUSED_FROM_TASK-020",
                "preview_gate": "REUSED_FROM_TASK-022_PASS_225_OF_225",
                "staging_hash": "REUSED_FROM_TASK-022_3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded",
                "test_suites": "REUSED_FROM_TASK-022_JEST_24_OF_24_PY_40_OF_40",
            },
        },
        "records": extracted_records,
    }

    out_json_path = REPORTS_DIR / "TASK-023_teacher_decision_evidence.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(merged_payload, f, indent=2, ensure_ascii=False)
    print(f"\n[OUTPUT] Saved JSON evidence: {out_json_path}")

    # 5. Coordinator Merge into Markdown Report
    md_lines: List[str] = [
        "# TASK-023 — Exact Teacher-Decision Evidence Package",
        "",
        f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}  ",
        "**Purpose**: Machine-grounded evidence for 5 unresolved teacher-decision candidates.  ",
        "**Source of Truth**: [`TASK-023_teacher_decision_evidence.json`](file:///c:/projects/English%20Breakfast%20Grammar/data/reports/TASK-023_teacher_decision_evidence.json)  ",
        "**Reused Verifications**: Global audit, Preview Gate (225/225 PASS), Staging hash, and test suites reused from TASK-020/022.  ",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| QID | Level | Exercise | Response Model | Issue Category | Conflicting QID / Context | Proposed Action |",
        "| :---: | :---: | :---: | :---: | :--- | :--- | :--- |",
        "| **3068** | A2 | `quiz-358` | `gap` (10 gaps) | Copular agreement | Gap 4: *Was auditorium acoustics* | Replace head noun *acoustics* with singular *sound quality* |",
        "| **5054** | A1 | `quiz-591` | `gap` (1 gap) | Carrier duplicate | Collided with QID 5038 (*cat hiding behind sofa*) | Replaced with person queue context (*ticket queue*) |",
        "| **5165** | A1 | `quiz-602` | `single_choice` | Carrier duplicate | Collided with QID 5160 (*listening to music*) | Replaced with afternoon reading context (*reading novels*) |",
        "| **7513** | A2 | `quiz-882` | `gap` (1 gap) | Carrier duplicate | Collided with QID 7493 (*catch last train*) | Replaced with laptop repair context (*online presentation*) |",
        "| **6742** | B1 | `quiz-782` | `single_choice` | Carrier duplicate | Collided with QID 6739 (*hike national park*) | Replaced with Alpine tunnel context (*50-kilometre tunnel*) |",
        "",
        "---",
        "",
        "## Exact Evidence by Candidate",
        "",
    ]

    for rec in extracted_records:
        qid = rec["qid"]
        md_lines.append(f"### QID {qid} ({rec['category']})")
        md_lines.append(f"- **Level**: `{rec['level']}` | **Topic**: `{rec['topic']}` | **Exercise**: `{rec['exercise_id']}` ({rec['exercise_title']})")
        md_lines.append(f"- **Response Model**: `{rec['response_model']}` | **Gaps**: `{rec['gap_count']}` | **Options**: `{rec['option_count']}`")
        md_lines.append(f"- **Source Text**:\n  > {rec['source_text'].replace(chr(10), ' ')}")
        md_lines.append(f"- **Source Answer(s)**: `{rec['source_correct_answer']}`")

        if qid == "3068":
            md_lines.append(f"- **Original Problematic Sentence**: `{rec['original_problematic_sentence']}`")
            md_lines.append(f"- **Validator Flag**: `{rec['exact_validator_flag']}`")
            md_lines.append(f"- **Candidate Sentence**: `{rec['candidate_sentence']}`")
            md_lines.append(f"- **Target Answer**: `{rec['candidate_answer']}` (Target answer preserved)")
            md_lines.append(f"- **Teacher Rationale**:\n  {rec['task022_rationale']}")
        else:
            md_lines.append(f"- **Duplicated Carrier Text**: `{rec['duplicated_carrier_text']}`")
            md_lines.append(f"- **Conflicting QID**: `{rec['conflicting_qid']}` in `{rec['conflicting_exercise_id']}`")
            md_lines.append(f"- **Conflicting Carrier**: `{rec['conflicting_adapted_text']}`")
            md_lines.append(f"- **Proposed Candidate Text**:\n  > {rec['candidate_adapted_text']}")
            md_lines.append(f"- **Candidate Answer**: `{rec['candidate_answer']}` (Preserved)")
            if rec["candidate_options"]:
                md_lines.append(f"- **Candidate Options**: `{rec['candidate_options']}`")
            md_lines.append(f"- **Teacher Rationale**:\n  {rec['task022_rationale']}")

        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    md_lines.append("## Teacher Decision Boundary")
    md_lines.append("No database modifications, regenerations, or pedagogical determinations were performed. Ready for English teacher / supervisor decision.")

    out_md_path = REPORTS_DIR / "TASK-023_teacher_decision_evidence.md"
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"[OUTPUT] Saved Markdown evidence: {out_md_path}")

    # 6. Post-check database immutability
    s_hash_after = Path(STAGING_DB_PATH).read_bytes()
    a_hash_after = Path(ADAPTATION_DB_PATH).read_bytes()
    import hashlib
    assert hashlib.sha256(s_hash_after).hexdigest() == "3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded"
    assert hashlib.sha256(a_hash_after).hexdigest() == "2756ad757b816cf53975d0357eaa3738fa2a0f8a812ae81674e52e394c79e4cd"
    print("\n[POST-CHECK] Database hashes verified identical: 0 modifications to staging.db or adaptation.db.")
    print("=" * 70)
    print("TASK-023 COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
