"""TASK-024 Apply Teacher-Approved Candidate Decisions.

Applies the 5 teacher-approved candidate decisions:
1. QID 3068: Sentence 4 updated to 'Was the sound quality in the auditorium satisfactory?' (Answer: 'Was')
2. QID 5054: 'Sophie is standing {{gap_1}} Liam in the ticket queue.' (Answer: 'behind')
3. QID 5165: 'We _____ reading novels in the park on sunny afternoons.' (Answer: 'like')
4. QID 7513: 'The technician finished repairing the laptop {{gap_1}} for my online presentation.' (Answer: 'in time')
5. QID 6742: 'Engineers constructed a _____ tunnel beneath the Alpine ridge.' (Answer: '50-kilometre')

Rules:
- Read-only parallel worker validation for preparation.
- Coordinator merges results and applies atomic transaction to adaptation.db.
- Zero modifications to staging.db, evaluator logic, or unrelated questions.
- Targeted verification only; reuse verified global results from TASK-020/022.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.similarity_evaluator import evaluate_similarity

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
EXPECTED_STAGING_SHA256 = "3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded"
EXPECTED_ADAPT_SHA256_BEFORE = "2756ad757b816cf53975d0357eaa3738fa2a0f8a812ae81674e52e394c79e4cd"

CANDIDATE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "3068": {
        "worker": "Worker A",
        "category": "SEMANTIC_COPULAR_AGREEMENT",
        "old_text": (
            "Part 1\n"
            "LEO: 1 {{gap_1}} (ever/you/hear) broadcasts by the Cambridge Baroque Quartet?\n"
            "TARA: Truly, I 2 {{gap_2}}. Which musical repertoire do they perform?\n"
            "LEO: Classical chamber works. In fact, my family 3 {{gap_3}} (see) their ensemble performing live last Friday.\n"
            "TARA: 4 {{gap_4}} (be) the auditorium acoustics satisfactory?\n"
            "LEO: Exceptionally; audiences 5 {{gap_5}} (like) each symphony.\n\n"
            "Part 2\n"
            "FELIX: At busy airport terminals, 6 {{gap_6}} (ever/you/lose) international travel documents?\n"
            "NINA: Regrettably, I 7 {{gap_7}}.\n"
            "FELIX: Along which flight corridor 8 {{gap_8}} (it/happen)?\n"
            "NINA: In Zurich; an oversized boarding envelope 9 {{gap_9}} (be) misplaced during customs transfers.\n"
            "FELIX: Afterward, what emergency procedures 10 {{gap_10}} (you/do)?"
        ),
        "approved_text": (
            "Part 1\n"
            "LEO: 1 {{gap_1}} (ever/you/hear) broadcasts by the Cambridge Baroque Quartet?\n"
            "TARA: Truly, I 2 {{gap_2}}. Which musical repertoire do they perform?\n"
            "LEO: Classical chamber works. In fact, my family 3 {{gap_3}} (see) their ensemble performing live last Friday.\n"
            "TARA: 4 {{gap_4}} (be) the sound quality in the auditorium satisfactory?\n"
            "LEO: Exceptionally; audiences 5 {{gap_5}} (like) each symphony.\n\n"
            "Part 2\n"
            "FELIX: At busy airport terminals, 6 {{gap_6}} (ever/you/lose) international travel documents?\n"
            "NINA: Regrettably, I 7 {{gap_7}}.\n"
            "FELIX: Along which flight corridor 8 {{gap_8}} (it/happen)?\n"
            "NINA: In Zurich; an oversized boarding envelope 9 {{gap_9}} (be) misplaced during customs transfers.\n"
            "FELIX: Afterward, what emergency procedures 10 {{gap_10}} (you/do)?"
        ),
        "expected_answers": [
            "Have you ever heard", "haven't", "saw", "Was", "liked",
            "Have you ever lost", "have", "did it happen", "was", "did you do"
        ],
        "response_model": "gap",
        "gap_count": 10,
        "option_count": 0,
        "gap_4_sentence": "Was the sound quality in the auditorium satisfactory?",
        "gap_4_answer": "Was",
        "teacher_decision": "STATUS: NEEDS FIX -> Candidate sentence 4 replaced with teacher approved wording 'Was the sound quality in the auditorium satisfactory?'. Preserved grammar target, answer 'Was', all other 9 gaps, all answer keys, gap ordering, and response model."
    },
    "5054": {
        "worker": "Worker B",
        "category": "SUSPICIOUS_DUPLICATE_CROSS_EXERCISE",
        "old_text": "The cat is hiding {{gap_1}} the sofa.",
        "approved_text": "Sophie is standing {{gap_1}} Liam in the ticket queue.",
        "expected_answers": ["behind"],
        "response_model": "gap",
        "gap_count": 1,
        "option_count": 0,
        "teacher_decision": "STATUS: APPROVED -> Applied approved candidate text 'Sophie is standing {{gap_1}} Liam in the ticket queue.' (Answer: 'behind'). Breaks carrier collision with QID 5038."
    },
    "5165": {
        "worker": "Worker C",
        "category": "GENUINE_DUPLICATE_SAME_EXERCISE",
        "old_text": "They _____ listening to music in the evening.",
        "approved_text": "We _____ reading novels in the park on sunny afternoons.",
        "expected_answers": ["like"],
        "response_model": "single_choice",
        "gap_count": 0,
        "option_count": 3,
        "expected_options": ["'d like", "like", "'d like to"],
        "teacher_decision": "STATUS: APPROVED -> Applied approved candidate text 'We _____ reading novels in the park on sunny afternoons.' (Answer: 'like'). Breaks duplicate carrier with QID 5160. Preserved original options exactly."
    },
    "7513": {
        "worker": "Worker D",
        "category": "SUSPICIOUS_DUPLICATE_CROSS_EXERCISE",
        "old_text": "We arrived at the station {{gap_1}} to catch the last train.",
        "approved_text": "The technician finished repairing the laptop {{gap_1}} for my online presentation.",
        "expected_answers": ["in time"],
        "response_model": "gap",
        "gap_count": 1,
        "option_count": 0,
        "teacher_decision": "STATUS: APPROVED -> Applied approved candidate text 'The technician finished repairing the laptop {{gap_1}} for my online presentation.' (Answer: 'in time'). Breaks carrier collision with QID 7493."
    },
    "6742": {
        "worker": "Worker E",
        "category": "GENUINE_DUPLICATE_SAME_EXERCISE",
        "old_text": "They completed a _____ hike through the national park.",
        "approved_text": "Engineers constructed a _____ tunnel beneath the Alpine ridge.",
        "expected_answers": ["50-kilometre"],
        "response_model": "single_choice",
        "gap_count": 0,
        "option_count": 3,
        "expected_options": ["50-kilometre", "50-kilometres", "50 kilometres"],
        "teacher_decision": "STATUS: APPROVED -> Applied approved candidate text 'Engineers constructed a _____ tunnel beneath the Alpine ridge.' (Answer: '50-kilometre'). Breaks duplicate carrier with QID 6739. Preserved original options exactly."
    }
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def worker_validate_qid(qid: str) -> Dict[str, Any]:
    """Parallel read-only worker validating assigned QID."""
    cfg = CANDIDATE_CONFIGS[qid]
    worker_name = cfg["worker"]
    old_text = cfg["old_text"]
    approved_text = cfg["approved_text"]
    expected_answers = cfg["expected_answers"]
    expected_rm = cfg["response_model"]

    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row
    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    sq = stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
    aq = adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
    s_ex = stage_conn.execute("SELECT * FROM staging_exercises WHERE exercise_id = ?", (sq["exercise_id"],)).fetchone()
    s_les = stage_conn.execute("SELECT * FROM staging_lessons WHERE lesson_id = ?", (sq["lesson_id"],)).fetchone()

    s_gaps = stage_conn.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)).fetchall()
    a_gaps = adapt_conn.execute("SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aq["adapted_question_id"],)).fetchall()
    s_opts = stage_conn.execute("SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order", (qid,)).fetchall()
    a_opts = adapt_conn.execute("SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order", (aq["adapted_question_id"],)).fetchall()

    stage_conn.close()
    adapt_conn.close()

    validation_errors: List[str] = []

    # 1. source_question_id unchanged
    if str(sq["question_id"]) != qid or str(aq["source_question_id"]) != qid:
        validation_errors.append(f"source_question_id mismatch: sq={sq['question_id']}, aq={aq['source_question_id']}, expected={qid}")

    # 2. response_model unchanged
    if sq["response_model"] != expected_rm or aq["response_model"] != expected_rm:
        validation_errors.append(f"response_model mismatch: sq={sq['response_model']}, aq={aq['response_model']}, expected={expected_rm}")

    # 3. answer unchanged
    if expected_rm == "gap":
        s_answers = [g["correct_answer"] for g in s_gaps]
        a_answers = [g["adapted_correct_answer"] for g in a_gaps]
    else:
        s_answers = [o["text"] for o in s_opts if o["is_correct"]]
        a_answers = [o["adapted_text"] for o in a_opts if o["adapted_is_correct"]]

    if s_answers != expected_answers or a_answers != expected_answers:
        validation_errors.append(f"Answer mismatch: source={s_answers}, adapted={a_answers}, expected={expected_answers}")

    # 4. options unchanged (for choice questions)
    if expected_rm in ("single_choice", "multiple_choice"):
        s_opt_texts = [o["text"] for o in s_opts]
        a_opt_texts = [o["adapted_text"] for o in a_opts]
        if s_opt_texts != cfg["expected_options"] or a_opt_texts != cfg["expected_options"]:
            validation_errors.append(f"Options mismatch: source={s_opt_texts}, adapted={a_opt_texts}, expected={cfg['expected_options']}")

    # 5. gap count & order unchanged
    if expected_rm == "gap":
        if len(s_gaps) != cfg["gap_count"] or len(a_gaps) != cfg["gap_count"]:
            validation_errors.append(f"Gap count mismatch: source={len(s_gaps)}, adapted={len(a_gaps)}, expected={cfg['gap_count']}")
        found_gaps = re.findall(r"\{\{gap_(\d+)\}\}", approved_text)
        expected_gap_indices = [str(i) for i in range(1, cfg["gap_count"] + 1)]
        if found_gaps != expected_gap_indices:
            validation_errors.append(f"Gap indices/ordering mismatch in approved text: found={found_gaps}, expected={expected_gap_indices}")
    elif expected_rm in ("single_choice", "multiple_choice"):
        if "{{" in approved_text or "gap" in approved_text:
            validation_errors.append("Choice question approved text contains illegal gap syntax")
        if "_____" not in approved_text:
            validation_errors.append("Choice question approved text missing fill blank '_____'")

    # 6. Candidate text valid and non-empty
    if not approved_text or len(approved_text.strip()) < 10:
        validation_errors.append("Candidate text is empty or invalid")

    # 7. Calibrated similarity evaluator passes
    sim_res = evaluate_similarity(sq["content"], approved_text)
    if sim_res["originality_status"] != "VALIDATED":
        validation_errors.append(f"Similarity evaluator failed: status={sim_res['originality_status']}, reasons={sim_res['reasons']}")
    if sim_res["forbidden_shingle_detected"]:
        validation_errors.append(f"Forbidden shingles detected: {sim_res['matching_shingles']}")
    if sim_res["jaccard_similarity"] > 0.40:
        validation_errors.append(f"Jaccard similarity exceeds threshold: {sim_res['jaccard_similarity']}")

    # 8. QID 3068 specific grammatical verification
    if qid == "3068":
        target_s = cfg["gap_4_sentence"]
        if not target_s.startswith("Was"):
            validation_errors.append(f"QID 3068 sentence must start with 'Was': {target_s}")
        if "sound quality" not in target_s:
            validation_errors.append(f"QID 3068 sentence missing singular head noun 'sound quality': {target_s}")
        # Verify all other 9 gaps in text are preserved
        old_lines = old_text.splitlines()
        new_lines = approved_text.splitlines()
        if len(old_lines) != len(new_lines):
            validation_errors.append(f"QID 3068 line count mismatch: old={len(old_lines)}, new={len(new_lines)}")
        else:
            for line_idx, (o_line, n_line) in enumerate(zip(old_lines, new_lines)):
                if line_idx == 4:
                    expected_line = "TARA: 4 {{gap_4}} (be) the sound quality in the auditorium satisfactory?"
                    if n_line != expected_line:
                        validation_errors.append(f"QID 3068 line 4 mismatch: got '{n_line}', expected '{expected_line}'")
                else:
                    if o_line != n_line:
                        validation_errors.append(f"QID 3068 unintended line alteration at line {line_idx}: '{o_line}' -> '{n_line}'")

    validation_passed = len(validation_errors) == 0

    return {
        "worker": worker_name,
        "qid": qid,
        "category": cfg["category"],
        "level": s_les["level"],
        "exercise_id": sq["exercise_id"],
        "exercise_title": s_ex["title"],
        "lesson_id": sq["lesson_id"],
        "topic": s_les["topic"],
        "response_model": expected_rm,
        "old_adapted_text": old_text,
        "new_adapted_text": approved_text,
        "source_text": sq["content"],
        "expected_answers": expected_answers,
        "answer_preserved": True if validation_passed else False,
        "similarity_metrics": {
            "jaccard_similarity": round(sim_res["jaccard_similarity"], 4),
            "levenshtein_similarity": round(sim_res["levenshtein_similarity"], 4),
            "forbidden_shingle_detected": sim_res["forbidden_shingle_detected"],
            "matching_shingles": sim_res["matching_shingles"],
            "originality_status": sim_res["originality_status"],
        },
        "teacher_decision": cfg["teacher_decision"],
        "validation_passed": validation_passed,
        "validation_errors": validation_errors,
    }


def execute_task024() -> Dict[str, Any]:
    print("=" * 70)
    print("TASK-024: APPLY 5 TEACHER-APPROVED CANDIDATE DECISIONS")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # 1. Staging Immutability Pre-Check
    staging_hash = compute_sha256(STAGING_DB_PATH)
    assert staging_hash == EXPECTED_STAGING_SHA256, f"Staging hash mismatch: {staging_hash}"
    print(f"[CHECK] Staging DB SHA-256 verified immutable: {staging_hash}")

    # 2. Adaptation DB Pre-Check
    adapt_hash_current = compute_sha256(ADAPTATION_DB_PATH)
    print(f"[SNAPSHOT] adaptation.db current SHA-256: {adapt_hash_current}")

    read_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    q_counts_before = dict(read_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
    ex_counts_before = dict(read_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_exercises GROUP BY adaptation_status").fetchall())
    les_counts_before = dict(read_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_lessons GROUP BY adaptation_status").fetchall())
    read_conn.close()

    assert q_counts_before == {"VALIDATED": 5796}, f"Questions before mismatch: {q_counts_before}"
    assert ex_counts_before == {"VALIDATED": 638}, f"Exercises before mismatch: {ex_counts_before}"
    assert les_counts_before == {"VALIDATED": 225}, f"Lessons before mismatch: {les_counts_before}"
    print("[PRE-CHECK] Confirmed baseline counts: Questions=5,796 (VALIDATED), Exercises=638, Lessons=225")

    # 3. Parallel Worker Execution
    target_qids = ["3068", "5054", "5165", "7513", "6742"]
    print(f"\n[PARALLEL] Running 5 parallel read-only validation workers for QIDs: {target_qids}")

    worker_results: Dict[str, Dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=5) as executor:
        future_to_qid = {executor.submit(worker_validate_qid, q): q for q in target_qids}
        for future in as_completed(future_to_qid):
            qid = future_to_qid[future]
            res = future.result()
            worker_results[qid] = res
            status_str = "PASS" if res["validation_passed"] else f"FAIL: {res['validation_errors']}"
            print(f"  [{res['worker']}] QID {qid} ({res['category']}): {status_str}")

    # 4. Coordinator Validation Verification
    all_passed = all(worker_results[q]["validation_passed"] for q in target_qids)
    if not all_passed:
        failed_qids = [q for q in target_qids if not worker_results[q]["validation_passed"]]
        print(f"\n[ABORT] Validation failed for QIDs {failed_qids}. NO DATABASE CHANGES MADE.")
        raise RuntimeError(f"Validation failed for QIDs: {failed_qids}")

    print("\n[COORDINATOR] All 5 workers passed strict validation. Proceeding to atomic transaction.")

    # 5. Atomic Transaction Commit to adaptation.db
    write_conn = sqlite3.connect(ADAPTATION_DB_PATH)
    write_conn.row_factory = sqlite3.Row
    transaction_succeeded = False

    try:
        write_conn.execute("BEGIN IMMEDIATE")
        for qid in target_qids:
            res = worker_results[qid]
            write_conn.execute(
                """UPDATE adapted_questions
                   SET adapted_text = ?,
                       similarity_score = ?,
                       adaptation_notes = ?
                   WHERE source_question_id = ?""",
                (
                    res["new_adapted_text"],
                    res["similarity_metrics"]["jaccard_similarity"],
                    f"TASK-024 Teacher Decision: {res['teacher_decision']}",
                    qid,
                ),
            )

        # In-transaction checks
        fk_check = write_conn.execute("PRAGMA foreign_key_check").fetchall()
        assert len(fk_check) == 0, f"Foreign key check failed: {fk_check}"

        integ_check = write_conn.execute("PRAGMA integrity_check").fetchall()
        assert len(integ_check) == 1 and integ_check[0][0] == "ok", f"Integrity check failed: {integ_check}"

        # Verify all 5 updated in place with VALIDATED status
        for qid in target_qids:
            row = write_conn.execute("SELECT adapted_text, adaptation_status, similarity_score FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
            assert row["adapted_text"] == worker_results[qid]["new_adapted_text"], f"QID {qid} text not updated"
            assert row["adaptation_status"] == "VALIDATED", f"QID {qid} status altered"

        # Verify database totals inside transaction
        q_cnt = dict(write_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
        assert q_cnt == {"VALIDATED": 5796}, f"Post-update question count mismatch: {q_cnt}"

        write_conn.commit()
        transaction_succeeded = True
        print("[COMMIT] Atomic transaction successfully committed for all 5 QIDs.")
    except Exception as exc:
        write_conn.rollback()
        print(f"[ROLLBACK] Transaction rolled back due to error: {exc}")
        raise
    finally:
        write_conn.close()

    # 6. Post-Commit Verification
    adapt_hash_after = compute_sha256(ADAPTATION_DB_PATH)
    print(f"[POST-SNAPSHOT] adaptation.db SHA-256 after: {adapt_hash_after}")

    # Check totals post commit
    check_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    check_conn.row_factory = sqlite3.Row
    q_counts_after = dict(check_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
    ex_counts_after = dict(check_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_exercises GROUP BY adaptation_status").fetchall())
    les_counts_after = dict(check_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_lessons GROUP BY adaptation_status").fetchall())

    # Check affected exercises and lessons
    affected_exercise_ids = sorted(list({worker_results[q]["exercise_id"] for q in target_qids}))
    affected_lesson_ids = sorted(list({worker_results[q]["lesson_id"] for q in target_qids}))

    for ex_id in affected_exercise_ids:
        ex_row = check_conn.execute("SELECT * FROM adapted_exercises WHERE source_exercise_id = ?", (ex_id,)).fetchone()
        assert ex_row["adaptation_status"] == "VALIDATED", f"Exercise {ex_id} not VALIDATED"

    for les_id in affected_lesson_ids:
        les_row = check_conn.execute("SELECT * FROM adapted_lessons WHERE source_lesson_id = ?", (les_id,)).fetchone()
        assert les_row["adaptation_status"] == "VALIDATED", f"Lesson {les_id} not VALIDATED"

    check_conn.close()

    assert q_counts_after == {"VALIDATED": 5796}, f"Final question counts mismatch: {q_counts_after}"
    assert ex_counts_after == {"VALIDATED": 638}, f"Final exercise counts mismatch: {ex_counts_after}"
    assert les_counts_after == {"VALIDATED": 225}, f"Final lesson counts mismatch: {les_counts_after}"

    print(f"[POST-CHECK] Database counts perfectly maintained:")
    print(f"  Questions: {q_counts_after}")
    print(f"  Exercises: {ex_counts_after}")
    print(f"  Lessons:   {les_counts_after}")

    # 7. Generate Reports
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ordered_records = [worker_results[q] for q in target_qids]

    json_report = {
        "metadata": {
            "task": "TASK-024",
            "action": "APPLY_5_TEACHER_APPROVED_CANDIDATE_DECISIONS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_qids": target_qids,
            "target_count": 5,
            "transaction_status": "COMMITTED" if transaction_succeeded else "FAILED",
            "reused_verifications": {
                "full_corpus_audit": "REUSED_FROM_TASK-020",
                "preview_gate": "REUSED_FROM_TASK-022_PASS_225_OF_225",
                "staging_hash": f"VERIFIED_{EXPECTED_STAGING_SHA256}",
                "test_suites": "REUSED_FROM_TASK-022_JEST_24_OF_24_PY_40_OF_40"
            }
        },
        "database_snapshot": {
            "staging_sha256": staging_hash,
            "adaptation_sha256_before": EXPECTED_ADAPT_SHA256_BEFORE,
            "adaptation_sha256_after": adapt_hash_after,
            "counts": {
                "questions": q_counts_after,
                "exercises": ex_counts_after,
                "lessons": les_counts_after,
            }
        },
        "affected_scopes": {
            "exercises": affected_exercise_ids,
            "lessons": affected_lesson_ids,
        },
        "records": [
            {
                "qid": r["qid"],
                "worker": r["worker"],
                "category": r["category"],
                "level": r["level"],
                "exercise_id": r["exercise_id"],
                "lesson_id": r["lesson_id"],
                "response_model": r["response_model"],
                "old_text": r["old_adapted_text"],
                "new_text": r["new_adapted_text"],
                "answer_preserved": r["answer_preserved"],
                "expected_answers": r["expected_answers"],
                "similarity_metrics": r["similarity_metrics"],
                "teacher_decision": r["teacher_decision"],
                "validation_passed": r["validation_passed"],
                "validation_errors": r["validation_errors"],
            }
            for r in ordered_records
        ]
    }

    out_json_path = REPORTS_DIR / "TASK-024_teacher_decision_application.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    print(f"\n[OUTPUT] Saved JSON report: {out_json_path}")

    # Build Markdown report
    md_lines: List[str] = [
        "# TASK-024 — Teacher Decision Application Report",
        "",
        f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}  ",
        "**Status**: `SUCCESS — COMMITTED ATOMICALLY`  ",
        f"**Transaction Result**: `COMMITTED` (5 of 5 applied)  ",
        "",
        "---",
        "",
        "## 1. Database State & Counts",
        "",
        "- **Questions**: **5,796** `VALIDATED` (0 REJECTED, 0 PENDING)",
        "- **Exercises**: **638** `VALIDATED` (0 REJECTED, 0 PENDING)",
        "- **Lessons**: **225** `VALIDATED` (0 REJECTED, 0 PENDING)",
        f"- **Staging DB SHA-256**: `{staging_hash}` (100% UNCHANGED)",
        f"- **Adaptation DB SHA-256 Before**: `{EXPECTED_ADAPT_SHA256_BEFORE}`",
        f"- **Adaptation DB SHA-256 After**: `{adapt_hash_after}`",
        "- **SQLite Checks**: `PRAGMA foreign_key_check` = 0 violations | `PRAGMA integrity_check` = `ok`",
        "",
        "---",
        "",
        "## 2. Affected Scopes",
        "",
        f"- **Affected Exercises ({len(affected_exercise_ids)})**: `{', '.join(affected_exercise_ids)}`",
        f"- **Affected Lessons ({len(affected_lesson_ids)})**: `{', '.join(affected_lesson_ids)}`",
        "",
        "---",
        "",
        "## 3. The 5 Applied Records",
        "",
        "| QID | Level | Response Model | Category | Target Answer(s) | Similarity (Jaccard) | Status |",
        "| :---: | :---: | :---: | :--- | :--- | :---: | :---: |",
    ]

    for r in ordered_records:
        ans_str = ", ".join(r["expected_answers"]) if len(r["expected_answers"]) <= 3 else f"{r['expected_answers'][0]}... ({len(r['expected_answers'])} answers)"
        md_lines.append(f"| **{r['qid']}** | `{r['level']}` | `{r['response_model']}` | {r['category']} | `{ans_str}` | {r['similarity_metrics']['jaccard_similarity']} | `VALIDATED` |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Exact Before / After Evidence",
        "",
    ])

    for r in ordered_records:
        md_lines.append(f"### QID {r['qid']} — {r['category']} ({r['worker']})")
        md_lines.append(f"- **Exercise**: `{r['exercise_id']}` | **Lesson**: `{r['lesson_id']}`")
        md_lines.append(f"- **Response Model**: `{r['response_model']}` | **Answer Preserved**: `YES` (`{r['expected_answers']}`)")
        md_lines.append(f"- **Teacher Decision**: {r['teacher_decision']}")
        md_lines.append(f"- **Similarity**: Jaccard `{r['similarity_metrics']['jaccard_similarity']}`, Levenshtein `{r['similarity_metrics']['levenshtein_similarity']}`, Forbidden Shingles: `0`")
        md_lines.append("- **Old Adapted Text**:")
        md_lines.append("```")
        md_lines.append(r["old_adapted_text"])
        md_lines.append("```")
        md_lines.append("- **New Adapted Text**:")
        md_lines.append("```")
        md_lines.append(r["new_adapted_text"])
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    out_md_path = REPORTS_DIR / "TASK-024_teacher_decision_application.md"
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines).strip() + "\n")
    print(f"[OUTPUT] Saved Markdown report: {out_md_path}")

    print("\n" + "=" * 70)
    print("TASK-024 EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return json_report


if __name__ == "__main__":
    execute_task024()
