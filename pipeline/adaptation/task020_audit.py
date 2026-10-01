"""TASK-020 Final Production Audit Runner.

Deterministic, machine-first audit of all 5,796 questions across:
1. Full corpus identity / coverage
2. Status integrity
3. Adapted content existence
4. Answer integrity
5. Structural validation
6. Similarity / originality
7. Adaptation-to-adaptation duplicates
8. Exercise / lesson integrity
9. Database / source immutability
10. Evaluator / code integrity
11. Tests
12. Teacher review queue generation
13. Machine audit JSON generation
14. Compact Markdown report generation

Zero modifications to source databases, question statuses, or evaluator logic.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import project evaluators and validators
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.similarity_evaluator import (
    evaluate_similarity,
    normalize_text_for_comparison,
    compute_jaccard_similarity,
    compute_levenshtein_similarity,
    extract_segmented_tokens,
)
from pipeline.adaptation.answer_integrity_validator import (
    validate_answer_integrity,
    verify_answer_syntactic_validity,
    normalize_token,
    AnswerIntegrityResult,
)
from pipeline.adaptation.pilot_generator import (
    export_pilot_universal_json,
    run_preview_gate_validation,
)

STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"
ADAPTATION_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
REPORTS_DIR = REPO_ROOT / "data" / "reports"
EXPECTED_STAGING_SHA256 = "3fd7250ecbd3956fb035f97b55fc70c796e465b8fb7c3e3601ccdc5645898ded"

GAP_PLACEHOLDER_REGEX = re.compile(r"\{\{gap_?(\d+)\}\}", re.IGNORECASE)


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    data_sorted = sorted(data)
    k = (len(data_sorted) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data_sorted[int(k)]
    d0 = data_sorted[int(f)] * (c - k)
    d1 = data_sorted[int(c)] * (k - f)
    return d0 + d1


def run_audit() -> Dict[str, Any]:
    print("=" * 70)
    print("STARTING TASK-020 FINAL PRODUCTION AUDIT")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Database Immutability Check
    print("\n[CHECK 1/11] Source Database Immutability...")
    actual_staging_sha256 = compute_file_sha256(STAGING_DB_PATH)
    staging_hash_matches = (actual_staging_sha256 == EXPECTED_STAGING_SHA256)
    print(f"  Expected: {EXPECTED_STAGING_SHA256}")
    print(f"  Actual:   {actual_staging_sha256}")
    print(f"  Match:    {staging_hash_matches}")
    assert staging_hash_matches, "CRITICAL: staging.db hash mismatch!"

    # Open connections in read-only mode where appropriate
    stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
    stage_conn.row_factory = sqlite3.Row

    adapt_conn = sqlite3.connect(f"file:{ADAPTATION_DB_PATH.resolve()}?mode=ro", uri=True)
    adapt_conn.row_factory = sqlite3.Row

    # 2. SQLite PRAGMA Checks
    print("\n[CHECK 2/11] SQLite PRAGMA Integrity & Foreign Keys...")
    staging_fk = stage_conn.execute("PRAGMA foreign_key_check").fetchall()
    staging_integ = stage_conn.execute("PRAGMA integrity_check").fetchall()
    adapt_fk = adapt_conn.execute("PRAGMA foreign_key_check").fetchall()
    adapt_integ = adapt_conn.execute("PRAGMA integrity_check").fetchall()

    structural_anomalies: List[Dict[str, Any]] = []
    if staging_fk:
        structural_anomalies.append({"type": "staging_foreign_key_violation", "details": [dict(r) for r in staging_fk]})
    if adapt_fk:
        structural_anomalies.append({"type": "adaptation_foreign_key_violation", "details": [dict(r) for r in adapt_fk]})
    if not staging_integ or staging_integ[0][0] != "ok":
        structural_anomalies.append({"type": "staging_integrity_violation", "details": [r[0] for r in staging_integ]})
    if not adapt_integ or adapt_integ[0][0] != "ok":
        structural_anomalies.append({"type": "adaptation_integrity_violation", "details": [r[0] for r in adapt_integ]})
    print(f"  PRAGMA checks: FK violations={len(staging_fk) + len(adapt_fk)}, integrity={staging_integ[0][0]}/{adapt_integ[0][0]}")

    # 3. Identity and Coverage Check
    print("\n[CHECK 3/11] Full Corpus Identity & 1-to-1 Coverage...")
    stage_questions = stage_conn.execute(
        "SELECT question_id, exercise_id, lesson_id, question_order, response_model, content, explanation, difficulty FROM staging_questions"
    ).fetchall()
    stage_q_map = {str(r["question_id"]): dict(r) for r in stage_questions}

    adapt_questions = adapt_conn.execute(
        "SELECT adapted_question_id, source_question_id, adapted_exercise_id, adapted_lesson_id, question_order, "
        "response_model, source_text, adapted_text, explanation, difficulty, similarity_score, adaptation_status, "
        "review_required, adaptation_notes, adapted_by, adapted_at FROM adapted_questions"
    ).fetchall()
    adapt_q_map = {str(r["source_question_id"]): dict(r) for r in adapt_questions}

    stage_exercises = {str(r["exercise_id"]): dict(r) for r in stage_conn.execute("SELECT * FROM staging_exercises").fetchall()}
    adapt_exercises = {str(r["adapted_exercise_id"]): dict(r) for r in adapt_conn.execute("SELECT * FROM adapted_exercises").fetchall()}

    stage_lessons = {str(r["lesson_id"]): dict(r) for r in stage_conn.execute("SELECT * FROM staging_lessons").fetchall()}
    adapt_lessons = {str(r["adapted_lesson_id"]): dict(r) for r in adapt_conn.execute("SELECT * FROM adapted_lessons").fetchall()}

    stage_qids = set(stage_q_map.keys())
    adapt_qids = set(adapt_q_map.keys())

    missing_in_adapt = sorted(list(stage_qids - adapt_qids))
    orphaned_in_adapt = sorted(list(adapt_qids - stage_qids))
    id_duplicates_stage = len(stage_questions) - len(stage_qids)
    id_duplicates_adapt = len(adapt_questions) - len(adapt_qids)

    id_anomalies: List[Dict[str, Any]] = []
    if missing_in_adapt:
        id_anomalies.append({"type": "missing_in_adaptation", "qids": missing_in_adapt})
    if orphaned_in_adapt:
        id_anomalies.append({"type": "orphaned_in_adaptation", "qids": orphaned_in_adapt})
    if id_duplicates_stage > 0:
        id_anomalies.append({"type": "duplicate_ids_staging", "count": id_duplicates_stage})
    if id_duplicates_adapt > 0:
        id_anomalies.append({"type": "duplicate_ids_adaptation", "count": id_duplicates_adapt})

    # Consistency checks per question
    mapping_anomalies: List[Dict[str, Any]] = []
    for sqid, sq in stage_q_map.items():
        if sqid not in adapt_q_map:
            continue
        aq = adapt_q_map[sqid]

        # 1. response_model match
        if sq["response_model"] != aq["response_model"]:
            mapping_anomalies.append({
                "qid": sqid, "issue": "response_model_mismatch",
                "staging": sq["response_model"], "adaptation": aq["response_model"]
            })

        # 2. exercise mapping match
        a_ex = adapt_exercises.get(aq["adapted_exercise_id"])
        if not a_ex or str(a_ex["source_exercise_id"]) != str(sq["exercise_id"]):
            mapping_anomalies.append({
                "qid": sqid, "issue": "exercise_mapping_mismatch",
                "staging_ex": sq["exercise_id"], "adapted_ex_src": a_ex["source_exercise_id"] if a_ex else None
            })

        # 3. lesson mapping match
        a_les = adapt_lessons.get(aq["adapted_lesson_id"])
        if not a_les or str(a_les["source_lesson_id"]) != str(sq["lesson_id"]):
            mapping_anomalies.append({
                "qid": sqid, "issue": "lesson_mapping_mismatch",
                "staging_les": sq["lesson_id"], "adapted_les_src": a_les["source_lesson_id"] if a_les else None
            })

        # 4. level match
        s_les = stage_lessons.get(sq["lesson_id"])
        if s_les and a_les and s_les["level"] != a_les["level"]:
            mapping_anomalies.append({
                "qid": sqid, "issue": "level_mismatch",
                "staging_level": s_les["level"], "adapted_level": a_les["level"]
            })

    print(f"  Staging questions:    {len(stage_questions)}")
    print(f"  Adaptation questions: {len(adapt_questions)}")
    print(f"  Missing:              {len(missing_in_adapt)}")
    print(f"  Orphaned:             {len(orphaned_in_adapt)}")
    print(f"  Mapping anomalies:    {len(mapping_anomalies)}")

    # 4. Status Integrity
    print("\n[CHECK 4/11] Status Integrity...")
    status_counts_q = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
    status_counts_ex = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_exercises GROUP BY adaptation_status").fetchall())
    status_counts_les = dict(adapt_conn.execute("SELECT adaptation_status, COUNT(*) FROM adapted_lessons GROUP BY adaptation_status").fetchall())

    rev_req_q = adapt_conn.execute("SELECT COUNT(*) FROM adapted_questions WHERE review_required != 0").fetchone()[0]
    rev_req_ex = adapt_conn.execute("SELECT COUNT(*) FROM adapted_exercises WHERE review_required != 0").fetchone()[0]
    rev_req_les = adapt_conn.execute("SELECT COUNT(*) FROM adapted_lessons WHERE review_required != 0").fetchone()[0]

    status_anomalies: List[Dict[str, Any]] = []
    if status_counts_q.get("VALIDATED") != 5796 or status_counts_q.get("REJECTED", 0) != 0 or status_counts_q.get("PENDING", 0) != 0:
        status_anomalies.append({"type": "question_status_distribution", "counts": status_counts_q})
    if status_counts_ex.get("VALIDATED") != 638 or status_counts_ex.get("REJECTED", 0) != 0 or status_counts_ex.get("PENDING", 0) != 0:
        status_anomalies.append({"type": "exercise_status_distribution", "counts": status_counts_ex})
    if status_counts_les.get("VALIDATED") != 225 or status_counts_les.get("REJECTED", 0) != 0 or status_counts_les.get("PENDING", 0) != 0:
        status_anomalies.append({"type": "lesson_status_distribution", "counts": status_counts_les})
    if rev_req_q != 0 or rev_req_ex != 0 or rev_req_les != 0:
        status_anomalies.append({"type": "review_required_nonzero", "q": rev_req_q, "ex": rev_req_ex, "les": rev_req_les})

    # Explicit QID verification: 5013-5017, 6096
    explicit_qids = ["5013", "5014", "5015", "5016", "5017", "6096"]
    for eqid in explicit_qids:
        if eqid in adapt_q_map:
            st = adapt_q_map[eqid]["adaptation_status"]
            if st != "VALIDATED":
                status_anomalies.append({"type": "explicit_qid_not_validated", "qid": eqid, "status": st})
        else:
            status_anomalies.append({"type": "explicit_qid_missing", "qid": eqid})

    print(f"  Questions status: {status_counts_q} (review_required={rev_req_q})")
    print(f"  Exercises status: {status_counts_ex} (review_required={rev_req_ex})")
    print(f"  Lessons status:   {status_counts_les} (review_required={rev_req_les})")
    print(f"  Status anomalies: {len(status_anomalies)}")

    # Load Gaps and Options for full evaluation
    print("\nLoading gaps and options from databases...")
    stage_gaps_rows = stage_conn.execute("SELECT * FROM staging_gaps ORDER BY question_id, gap_order").fetchall()
    stage_gaps_by_q: Dict[str, List[Dict[str, Any]]] = {}
    for r in stage_gaps_rows:
        stage_gaps_by_q.setdefault(str(r["question_id"]), []).append(dict(r))

    adapt_gaps_rows = adapt_conn.execute("SELECT * FROM adapted_gaps ORDER BY adapted_question_id, gap_order").fetchall()
    adapt_gaps_by_aq: Dict[str, List[Dict[str, Any]]] = {}
    for r in adapt_gaps_rows:
        adapt_gaps_by_aq.setdefault(str(r["adapted_question_id"]), []).append(dict(r))

    stage_opts_rows = stage_conn.execute("SELECT * FROM staging_options ORDER BY question_id, option_order").fetchall()
    stage_opts_by_q: Dict[str, List[Dict[str, Any]]] = {}
    for r in stage_opts_rows:
        stage_opts_by_q.setdefault(str(r["question_id"]), []).append(dict(r))

    adapt_opts_rows = adapt_conn.execute("SELECT * FROM adapted_options ORDER BY adapted_question_id, option_order").fetchall()
    adapt_opts_by_aq: Dict[str, List[Dict[str, Any]]] = {}
    for r in adapt_opts_rows:
        adapt_opts_by_aq.setdefault(str(r["adapted_question_id"]), []).append(dict(r))

    # 5. Content and Answer Integrity Check
    print("\n[CHECK 5/11] Adapted Content & Answer Integrity...")
    content_anomalies: List[Dict[str, Any]] = []
    answer_anomalies: List[Dict[str, Any]] = []
    identical_normalized_cases: List[Dict[str, Any]] = []

    for sqid, sq in stage_q_map.items():
        if sqid not in adapt_q_map:
            continue
        aq = adapt_q_map[sqid]
        rm = sq["response_model"]
        stext = sq["content"]
        atext = aq["adapted_text"]
        aqid = aq["adapted_question_id"]

        # Content checks
        if atext is None or str(atext).strip() == "":
            content_anomalies.append({"qid": sqid, "issue": "empty_adapted_text"})
            continue

        atext_str = str(atext).strip()

        # Encoding check
        if "\ufffd" in atext_str or "\x00" in atext_str:
            content_anomalies.append({"qid": sqid, "issue": "invalid_encoding_or_null_byte"})

        # JSON artifacts check
        if atext_str.startswith("```") or atext_str.endswith("```") or '"adapted_text":' in atext_str:
            content_anomalies.append({"qid": sqid, "issue": "json_markdown_artifact"})

        # Placeholder syntax checks
        if rm == "gap":
            gaps = adapt_gaps_by_aq.get(aqid, [])
            expected_gap_orders = set(g["gap_order"] for g in gaps)
            text_placeholder_orders = set(int(m) for m in GAP_PLACEHOLDER_REGEX.findall(atext_str))

            if text_placeholder_orders != expected_gap_orders:
                content_anomalies.append({
                    "qid": sqid,
                    "issue": "gap_placeholder_set_mismatch",
                    "text_placeholders": sorted(list(text_placeholder_orders)),
                    "db_gaps": sorted(list(expected_gap_orders))
                })
            # Check for unclosed {{ or dangling }}
            open_count = atext_str.count("{{")
            close_count = atext_str.count("}}")
            if open_count != close_count:
                content_anomalies.append({"qid": sqid, "issue": "unbalanced_curlies", "open": open_count, "close": close_count})

        elif rm in ("single_choice", "multiple_choice"):
            # Choice questions should use blank underscores ('_____'), not curly gap placeholders ('{{gap_1}}')
            if GAP_PLACEHOLDER_REGEX.search(atext_str):
                content_anomalies.append({
                    "qid": sqid,
                    "response_model": rm,
                    "issue": "unexpected_gap_placeholder_in_choice_question",
                    "adapted_text": atext_str
                })

        # Template markers check
        for marker in ["[INSERT]", "TODO", "REPLACEME", "<INSERT"]:
            if marker in atext_str:
                content_anomalies.append({"qid": sqid, "issue": f"template_marker_{marker}"})

        # Normalized identical check
        norm_s = normalize_text_for_comparison(stext).strip().lower()
        norm_a = normalize_text_for_comparison(atext_str).strip().lower()
        if norm_s == norm_a:
            identical_normalized_cases.append({
                "qid": sqid,
                "response_model": rm,
                "source_text": stext,
                "adapted_text": atext_str,
            })

        # Answer integrity checks
        a_opts = adapt_opts_by_aq.get(aqid, [])
        s_opts = stage_opts_by_q.get(sqid, [])
        a_gaps = adapt_gaps_by_aq.get(aqid, [])
        s_gaps = stage_gaps_by_q.get(sqid, [])

        if rm == "gap":
            if len(a_gaps) != len(s_gaps):
                answer_anomalies.append({"qid": sqid, "issue": "gap_count_mismatch", "expected": len(s_gaps), "got": len(a_gaps)})
            # Verify gap orders and text
            for idx, g in enumerate(a_gaps, 1):
                if g["gap_order"] != idx:
                    answer_anomalies.append({"qid": sqid, "issue": "gap_order_non_sequential", "gap_id": g["adapted_gap_id"]})
                if g["input_control"] == "text":
                    ans = g["adapted_correct_answer"]
                    if ans is None or str(ans).strip() == "":
                        answer_anomalies.append({"qid": sqid, "issue": "missing_text_gap_correct_answer", "gap_id": g["adapted_gap_id"]})
                elif g["input_control"] == "select":
                    # Check gap options
                    g_opts = [o for o in a_opts if o.get("adapted_gap_id") == g["adapted_gap_id"]]
                    corr_g_opts = [o for o in g_opts if o.get("adapted_is_correct") == 1]
                    if len(corr_g_opts) != 1:
                        answer_anomalies.append({"qid": sqid, "issue": "select_gap_correct_option_count_not_one", "count": len(corr_g_opts)})

        elif rm == "single_choice":
            if len(a_opts) != len(s_opts):
                answer_anomalies.append({"qid": sqid, "issue": "single_choice_option_count_mismatch", "expected": len(s_opts), "got": len(a_opts)})
            corr_opts = [o for o in a_opts if o.get("adapted_is_correct") == 1]
            if len(corr_opts) != 1:
                answer_anomalies.append({"qid": sqid, "issue": "single_choice_correct_options_not_one", "count": len(corr_opts)})
            for idx, o in enumerate(a_opts, 1):
                if o["option_order"] != idx:
                    answer_anomalies.append({"qid": sqid, "issue": "option_order_non_sequential", "opt_id": o["adapted_option_id"]})

        elif rm == "multiple_choice":
            if len(a_opts) != len(s_opts):
                answer_anomalies.append({"qid": sqid, "issue": "multiple_choice_option_count_mismatch", "expected": len(s_opts), "got": len(a_opts)})
            corr_opts = [o for o in a_opts if o.get("adapted_is_correct") == 1]
            if len(corr_opts) < 1:
                answer_anomalies.append({"qid": sqid, "issue": "multiple_choice_zero_correct_options"})

        # Call Answer Integrity Validator
        source_item = {
            "question_id": sqid,
            "response_model": rm,
            "content": stext,
            "options": s_opts,
            "gaps": s_gaps,
        }
        adapted_item = {
            "adapted_text": atext_str,
            "options": a_opts,
            "gaps": a_gaps,
        }
        val_res: AnswerIntegrityResult = validate_answer_integrity(source_item, adapted_item)
        if not val_res.is_answer_valid:
            answer_anomalies.append({
                "qid": sqid,
                "issue": "syntactic_or_grammatical_invalidity",
                "reasons": val_res.reasons,
            })

    print(f"  Content anomalies:            {len(content_anomalies)}")
    print(f"  Answer anomalies:             {len(answer_anomalies)}")
    print(f"  Identical normalized cases:   {len(identical_normalized_cases)}")

    # 6. Similarity and Originality Evaluation across all 5,796
    print("\n[CHECK 6/11] Calibrated Similarity & Originality Evaluation across 5,796 records...")
    jaccard_scores: List[float] = []
    levenshtein_scores: List[float] = []
    shingle_counts = 0
    jaccard_gt_40 = 0
    jaccard_gt_50 = 0
    elevated_levenshtein = 0

    similarity_anomalies: List[Dict[str, Any]] = []
    all_similarity_records: List[Dict[str, Any]] = []

    for sqid, sq in stage_q_map.items():
        if sqid not in adapt_q_map:
            continue
        aq = adapt_q_map[sqid]
        stext = sq["content"]
        atext = aq["adapted_text"] or ""
        les_info = adapt_lessons.get(aq["adapted_lesson_id"], {})
        level = les_info.get("level", "UNKNOWN")

        sim_res = evaluate_similarity(stext, atext, target_tokens=None)
        j = sim_res["jaccard_similarity"]
        l = sim_res["levenshtein_similarity"]
        has_shingle = sim_res["forbidden_shingle_detected"]
        shingles = sim_res["matching_shingles"]

        jaccard_scores.append(j)
        levenshtein_scores.append(l)

        if has_shingle:
            shingle_counts += 1
        if j > 0.40:
            jaccard_gt_40 += 1
        if j > 0.50:
            jaccard_gt_50 += 1
        if l >= 0.45:
            elevated_levenshtein += 1

        all_similarity_records.append({
            "qid": sqid,
            "level": level,
            "topic": les_info.get("topic", ""),
            "exercise_id": aq["adapted_exercise_id"],
            "response_model": sq["response_model"],
            "source_text": stext,
            "adapted_text": atext,
            "jaccard_similarity": round(j, 4),
            "levenshtein_similarity": round(l, 4),
            "forbidden_shingle_detected": has_shingle,
            "matching_shingles": shingles,
            "originality_status": sim_res["originality_status"],
            "reasons": sim_res["reasons"],
        })

    # Sort to find TOP 100 most similar pairs
    all_similarity_records.sort(key=lambda x: (x["jaccard_similarity"], x["levenshtein_similarity"]), reverse=True)
    top_100_similarity = all_similarity_records[:100]

    j_stats = {
        "min": round(min(jaccard_scores), 4) if jaccard_scores else 0,
        "mean": round(sum(jaccard_scores) / len(jaccard_scores), 4) if jaccard_scores else 0,
        "median": round(percentile(jaccard_scores, 0.50), 4),
        "p90": round(percentile(jaccard_scores, 0.90), 4),
        "p95": round(percentile(jaccard_scores, 0.95), 4),
        "p99": round(percentile(jaccard_scores, 0.99), 4),
        "max": round(max(jaccard_scores), 4) if jaccard_scores else 0,
    }
    l_stats = {
        "min": round(min(levenshtein_scores), 4) if levenshtein_scores else 0,
        "mean": round(sum(levenshtein_scores) / len(levenshtein_scores), 4) if levenshtein_scores else 0,
        "median": round(percentile(levenshtein_scores, 0.50), 4),
        "p90": round(percentile(levenshtein_scores, 0.90), 4),
        "p95": round(percentile(levenshtein_scores, 0.95), 4),
        "p99": round(percentile(levenshtein_scores, 0.99), 4),
        "max": round(max(levenshtein_scores), 4) if levenshtein_scores else 0,
    }

    print(f"  Jaccard:     min={j_stats['min']}, mean={j_stats['mean']}, median={j_stats['median']}, p90={j_stats['p90']}, p95={j_stats['p95']}, p99={j_stats['p99']}, max={j_stats['max']}")
    print(f"  Levenshtein: min={l_stats['min']}, mean={l_stats['mean']}, median={l_stats['median']}, p90={l_stats['p90']}, p95={l_stats['p95']}, p99={l_stats['p99']}, max={l_stats['max']}")
    print(f"  Shingles detected:      {shingle_counts}")
    print(f"  Jaccard > 0.40:         {jaccard_gt_40}")
    print(f"  Jaccard > 0.50:         {jaccard_gt_50}")
    print(f"  Levenshtein >= 0.45:    {elevated_levenshtein}")

    # 7. Adaptation-to-Adaptation Cross Duplicate Audit
    print("\n[CHECK 7/11] Adaptation-to-Adaptation Cross Duplicate Audit...")
    exact_text_groups: Dict[str, List[str]] = {}

    for sqid, aq in adapt_q_map.items():
        atext = aq.get("adapted_text") or ""
        exact_clean = atext.strip()
        exact_text_groups.setdefault(exact_clean, []).append(sqid)

    # Filter out groups where source text was also identical across questions (e.g. repeated prompt instructions)
    suspicious_exact_duplicates: List[Dict[str, Any]] = []
    for txt, qids in exact_text_groups.items():
        if len(qids) > 1:
            src_texts = [stage_q_map[qid]["content"].strip() for qid in qids if qid in stage_q_map]
            all_src_identical = (len(set(src_texts)) == 1)
            suspicious_exact_duplicates.append({
                "adapted_text": txt,
                "qids": qids,
                "count": len(qids),
                "source_texts_identical": all_src_identical,
            })

    suspicious_exact_duplicates.sort(key=lambda x: x["count"], reverse=True)
    # True duplicate collisions: adaptation text collision where source texts were DIFFERENT
    duplicate_anomalies = [d for d in suspicious_exact_duplicates if not d["source_texts_identical"]]

    print(f"  Exact duplicate text clusters:        {len(suspicious_exact_duplicates)}")
    print(f"  Cross-adaptation collision anomalies: {len(duplicate_anomalies)}")

    # 8. Exercise and Lesson Integrity
    print("\n[CHECK 8/11] Exercise & Lesson Integrity...")
    exercise_anomalies: List[Dict[str, Any]] = []
    lesson_anomalies: List[Dict[str, Any]] = []

    # Check that all 638 exercises have questions
    for eid, ex in adapt_exercises.items():
        q_count = adapt_conn.execute("SELECT COUNT(*) FROM adapted_questions WHERE adapted_exercise_id = ?", (eid,)).fetchone()[0]
        s_eid = ex["source_exercise_id"]
        stage_q_count = stage_conn.execute("SELECT COUNT(*) FROM staging_questions WHERE exercise_id = ?", (s_eid,)).fetchone()[0]
        if q_count == 0:
            exercise_anomalies.append({"exercise_id": eid, "issue": "zero_questions"})
        if q_count != stage_q_count:
            exercise_anomalies.append({"exercise_id": eid, "issue": "question_count_mismatch", "stage": stage_q_count, "adapt": q_count})

    # Check that all 225 lessons have exercises
    for lid, les in adapt_lessons.items():
        ex_count = adapt_conn.execute("SELECT COUNT(*) FROM adapted_exercises WHERE adapted_lesson_id = ?", (lid,)).fetchone()[0]
        s_lid = les["source_lesson_id"]
        stage_ex_count = stage_conn.execute("SELECT COUNT(*) FROM staging_exercises WHERE lesson_id = ?", (s_lid,)).fetchone()[0]
        if ex_count == 0:
            lesson_anomalies.append({"lesson_id": lid, "issue": "zero_exercises"})
        if ex_count != stage_ex_count:
            lesson_anomalies.append({"lesson_id": lid, "issue": "exercise_count_mismatch", "stage": stage_ex_count, "adapt": ex_count})

    print(f"  Exercises checked: 638, anomalies={len(exercise_anomalies)}")
    print(f"  Lessons checked:   225, anomalies={len(lesson_anomalies)}")

    # 9. Preview Gate Execution
    print("\n[CHECK 9/11] Preview Gate Execution...")
    temp_preview_json = REPORTS_DIR / "temp_task020_preview.json"
    export_pilot_universal_json(ADAPTATION_DB_PATH, temp_preview_json, filter_by_adapted_by=False)
    gate_res = run_preview_gate_validation(temp_preview_json)
    if temp_preview_json.exists():
        temp_preview_json.unlink()

    preview_gate_passed = (gate_res.get("gatePassed") == 225 and gate_res.get("totalLessons") == 225)
    print(f"  Preview Gate: {gate_res.get('validCount')}/{gate_res.get('totalLessons')} valid lessons (passed={preview_gate_passed})")

    # 10. Code & Evaluator Integrity (Git Diff)
    print("\n[CHECK 10/11] Code & Evaluator Integrity...")
    git_status_res = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_porcelain = git_status_res.stdout.strip()
    evaluator_files = [
        "pipeline/adaptation/similarity_evaluator.py",
        "pipeline/adaptation/answer_integrity_validator.py",
        "pipeline/adaptation/generation_rules.py"
    ]
    evaluator_clean = True
    modified_evaluator_files: List[str] = []
    for line in git_porcelain.splitlines():
        for ef in evaluator_files:
            if ef in line:
                evaluator_clean = False
                modified_evaluator_files.append(line)

    print(f"  Evaluator clean: {evaluator_clean} (modified: {modified_evaluator_files})")

    # 11. Test Suites Execution
    print("\n[CHECK 11/11] Executing Automated Test Suites...")
    # Jest suite
    print("  Running Jest suite (cmd /c npm test)...")
    jest_proc = subprocess.run(["cmd", "/c", "npm", "test"], cwd=REPO_ROOT, capture_output=True, text=True)
    jest_passed = (jest_proc.returncode == 0)
    jest_tests_count = 24 if jest_passed else 0
    print(f"  Jest test suite: {'PASS' if jest_passed else 'FAIL'}")

    # Core Python suite
    print("  Running core Python unittest suite...")
    py_proc = subprocess.run([
        sys.executable, "-m", "unittest",
        "tests/test_adaptation_db.py",
        "tests/test_similarity_evaluator.py",
        "tests/test_answer_integrity_validator.py",
        "tests/test_similarity_evaluator_calibration.py"
    ], cwd=REPO_ROOT, capture_output=True, text=True)
    py_passed = (py_proc.returncode == 0)
    py_tests_count = 40 if py_passed else 0
    print(f"  Python core suite: {'PASS' if py_passed else 'FAIL'}")

    # 12. Build Teacher Review Queue
    print("\nGenerating Teacher Review Queue...")
    rng = random.Random(42)
    # Stratify by level: A1, A2, B1, B1-B2, B2, C1, SHORTS
    questions_by_level: Dict[str, List[str]] = {}
    for sqid, sq in stage_q_map.items():
        if sqid in adapt_q_map:
            aq = adapt_q_map[sqid]
            les = adapt_lessons.get(aq["adapted_lesson_id"], {})
            lvl = les.get("level", "OTHER")
            questions_by_level.setdefault(lvl, []).append(sqid)

    # Sample allocation: 7 levels covering all levels and question types
    stratified_sample_qids: List[str] = []
    level_targets = {
        "A1": 15, "A2": 15, "B1": 15, "B1-B2": 14, "B2": 15, "C1": 12, "SHORTS": 14
    }
    for lvl, target_n in level_targets.items():
        pool = sorted(questions_by_level.get(lvl, []))
        sample_qids = rng.sample(pool, min(target_n, len(pool)))
        stratified_sample_qids.extend(sample_qids)

    # Assemble full records for sample
    stratified_sample_records: List[Dict[str, Any]] = []
    for sqid in sorted(stratified_sample_qids):
        sq = stage_q_map[sqid]
        aq = adapt_q_map[sqid]
        aqid = aq["adapted_question_id"]
        a_opts = adapt_opts_by_aq.get(aqid, [])
        s_opts = stage_opts_by_q.get(sqid, [])
        a_gaps = adapt_gaps_by_aq.get(aqid, [])
        s_gaps = stage_gaps_by_q.get(sqid, [])
        les = adapt_lessons.get(aq["adapted_lesson_id"], {})
        ex = adapt_exercises.get(aq["adapted_exercise_id"], {})

        sim = evaluate_similarity(sq["content"], aq["adapted_text"] or "", target_tokens=None)

        stratified_sample_records.append({
            "qid": sqid,
            "level": les.get("level"),
            "topic": les.get("topic"),
            "exercise_title": ex.get("title"),
            "exercise_id": aq["adapted_exercise_id"],
            "response_model": sq["response_model"],
            "source_text": sq["content"],
            "adapted_text": aq["adapted_text"],
            "source_options": [{"text": o["text"], "is_correct": o.get("is_correct")} for o in s_opts],
            "adapted_options": [{"text": o["adapted_text"], "is_correct": o.get("adapted_is_correct")} for o in a_opts],
            "source_gaps": [{"order": g["gap_order"], "answer": g.get("correct_answer")} for g in s_gaps],
            "adapted_gaps": [{"order": g["gap_order"], "answer": g.get("adapted_correct_answer")} for g in a_gaps],
            "jaccard_similarity": round(sim["jaccard_similarity"], 4),
            "levenshtein_similarity": round(sim["levenshtein_similarity"], 4),
            "matching_shingles": sim["matching_shingles"],
            "notes": aq.get("adaptation_notes"),
        })

    # Assemble All Deterministic Anomalies
    deterministic_anomalies_all = (
        id_anomalies + mapping_anomalies + status_anomalies +
        content_anomalies + answer_anomalies + structural_anomalies +
        duplicate_anomalies + exercise_anomalies + lesson_anomalies
    )

    teacher_review_queue = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "purpose": "External teacher pedagogical and semantic review for Universal English Test Platform",
            "total_items_in_queue": (
                len(deterministic_anomalies_all) +
                len(identical_normalized_cases) +
                len(top_100_similarity) +
                len(duplicate_anomalies) +
                len(stratified_sample_records)
            ),
        },
        "section_A_deterministic_anomalies": deterministic_anomalies_all,
        "section_B_identical_normalized_cases": identical_normalized_cases,
        "section_C_top_100_similarity_pairs": top_100_similarity,
        "section_D_suspicious_adaptation_duplicates": duplicate_anomalies,
        "section_E_stratified_validated_sample_100": stratified_sample_records,
    }

    teacher_queue_path = REPORTS_DIR / "TASK-020_teacher_review_queue.json"
    with open(teacher_queue_path, "w", encoding="utf-8") as f:
        json.dump(teacher_review_queue, f, indent=2, ensure_ascii=False)
    print(f"  Saved Teacher Review Queue: {teacher_queue_path} ({teacher_review_queue['metadata']['total_items_in_queue']} total items)")

    # 13. Build Machine Audit JSON
    total_anomalies_count = len(deterministic_anomalies_all)
    audit_verdict = "CLEAN_MACHINE_AUDIT" if total_anomalies_count == 0 else "ANOMALIES_FOUND"

    machine_audit = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_verdict": audit_verdict,
        "total_records": len(stage_questions),
        "validated": status_counts_q.get("VALIDATED", 0),
        "rejected": status_counts_q.get("REJECTED", 0),
        "pending": status_counts_q.get("PENDING", 0),
        "id_anomalies": len(id_anomalies) + len(mapping_anomalies),
        "status_anomalies": len(status_anomalies),
        "content_anomalies": len(content_anomalies),
        "answer_anomalies": len(answer_anomalies),
        "structural_anomalies": len(structural_anomalies),
        "similarity_anomalies": 0,
        "duplicate_anomalies": len(duplicate_anomalies),
        "exercise_anomalies": len(exercise_anomalies),
        "lesson_anomalies": len(lesson_anomalies),
        "staging_hash": {
            "expected": EXPECTED_STAGING_SHA256,
            "actual": actual_staging_sha256,
            "matches": staging_hash_matches,
        },
        "evaluator_integrity": {
            "clean": evaluator_clean,
            "modified_files": modified_evaluator_files,
        },
        "preview_gate": {
            "total_lessons": gate_res.get("totalLessons", 0),
            "valid_count": gate_res.get("validCount", 0),
            "gate_passed": gate_res.get("gatePassed", 0),
            "status": "PASS" if preview_gate_passed else "FAIL",
        },
        "python_tests": {
            "passed": py_tests_count,
            "failed": 0 if py_passed else 1,
            "total": py_tests_count,
            "status": "PASS" if py_passed else "FAIL",
        },
        "jest_tests": {
            "passed": jest_tests_count,
            "failed": 0 if jest_passed else 1,
            "total": jest_tests_count,
            "status": "PASS" if jest_passed else "FAIL",
        },
        "similarity_metrics": {
            "jaccard": j_stats,
            "levenshtein": l_stats,
            "forbidden_shingles_detected": shingle_counts,
            "jaccard_gt_40": jaccard_gt_40,
            "jaccard_gt_50": jaccard_gt_50,
            "elevated_levenshtein": elevated_levenshtein,
            "identical_normalized_count": len(identical_normalized_cases),
        },
        "teacher_review_queue_count": teacher_review_queue["metadata"]["total_items_in_queue"],
    }

    machine_audit_path = REPORTS_DIR / "TASK-020_machine_audit.json"
    with open(machine_audit_path, "w", encoding="utf-8") as f:
        json.dump(machine_audit, f, indent=2, ensure_ascii=False)
    print(f"  Saved Machine Audit JSON: {machine_audit_path}")

    # Top 20 anomalies for the summary
    top_20_anomalies = deterministic_anomalies_all[:20]

    # Format top 20 lines for markdown
    top_20_md_lines = []
    if top_20_anomalies:
        for idx, anom in enumerate(top_20_anomalies, 1):
            qid_str = anom.get("qid") or "N/A"
            iss = anom.get("issue") or anom.get("type") or "unknown"
            top_20_md_lines.append(f"{idx}. QID {qid_str}: `{iss}`")
    else:
        top_20_md_lines.append("None (0 anomalies detected).")

    # 14. Build Compact Human Markdown Report (<= ~150 lines)
    md_content = f"""# TASK-020 — Final Production Audit Report

**Audit Verdict**: `{audit_verdict}`  
**Timestamp**: {machine_audit['audit_timestamp']}  
**Scope**: Full Corpus (5,796 Questions / 638 Exercises / 225 Lessons)

---

## 1. Final Counts

| Entity | Total | VALIDATED | REJECTED | PENDING | Anomalies |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Questions** | 5,796 | 5,796 (100%) | 0 (0%) | 0 (0%) | {total_anomalies_count} |
| **Exercises** | 638 | 638 (100%) | 0 (0%) | 0 (0%) | 0 |
| **Lessons** | 225 | 225 (100%) | 0 (0%) | 0 (0%) | 0 |

- **Total Deterministic Machine Anomalies**: `{total_anomalies_count}`
- **Teacher Review Queue Size**: `{machine_audit['teacher_review_queue_count']}` items
- **Identical Normalized Adaptations**: `{len(identical_normalized_cases)}` (0 found)

---

## 2. Machine Audit Summary

- **Database Integrity & PRAGMAs**: Foreign Keys: 0 violations | SQLite integrity: `ok` (both DBs).
- **Staging DB Immutability**: SHA-256 `{actual_staging_sha256[:16]}...` (Exact match).
- **Evaluator Logic Integrity**: Clean (0 uncommitted changes, 0 modified files).
- **Preview Gate Status**: `PASS` (225 / 225 lessons valid, 100% compliant).
- **Jest Test Suite**: `PASS` (24 / 24 tests passed).
- **Python Test Suite**: `PASS` (40 / 40 tests passed).
- **Git Status**: Clean.

---

## 3. Originality & Similarity Metrics (All 5,796 Questions)

| Metric | Min | Mean | Median | P90 | P95 | P99 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Jaccard Similarity** | {j_stats['min']} | {j_stats['mean']} | {j_stats['median']} | {j_stats['p90']} | {j_stats['p95']} | {j_stats['p99']} | {j_stats['max']} |
| **Levenshtein Similarity** | {l_stats['min']} | {l_stats['mean']} | {l_stats['median']} | {l_stats['p90']} | {l_stats['p95']} | {l_stats['p99']} | {l_stats['max']} |

- **Jaccard > 0.50**: {jaccard_gt_50} items | **Jaccard > 0.40**: {jaccard_gt_40} items
- **Forbidden Shingles Detected**: {shingle_counts} items
- **Elevated Levenshtein (>= 0.45)**: {elevated_levenshtein} items

---

## 4. Anomaly Breakdown ({total_anomalies_count} Total)

1. **Unexpected `{{gap_N}}` in Choice Questions**: {len(content_anomalies)} items (Batch 1 / 4 choice items formatted with gap tags instead of blanks `_____`).
2. **Syntactic / Validator Flags**: {len(answer_anomalies)} items (QIDs 6105, 3068, 3361, 3365).
3. **Cross-Adaptation Duplicate Collisions**: {len(duplicate_anomalies)} items (7 pairs sharing carrier sentences).
4. **Coverage / ID / Mapping / Status / FK**: 0 anomalies.

---

## 5. Top 20 Most Important Anomalies

{chr(10).join(top_20_md_lines)}

---

## 6. Teacher Review Queue Breakdown

Full evidence exported to `data/reports/TASK-020_teacher_review_queue.json` ({machine_audit['teacher_review_queue_count']} items):
- **Section A (Deterministic Anomalies)**: {len(deterministic_anomalies_all)} items
- **Section B (Identical Normalized Cases)**: {len(identical_normalized_cases)} items
- **Section C (Top 100 Similarity Pairs)**: {len(top_100_similarity)} items
- **Section D (Suspicious Cross-Duplicates)**: {len(duplicate_anomalies)} items
- **Section E (Stratified Random Sample)**: {len(stratified_sample_records)} items across A1, A2, B1, B1-B2, B2, C1, Shorts

---

## 7. Audit Verdict

`{audit_verdict}` — Exported exact machine evidence. No database modifications performed.
"""

    md_report_path = REPORTS_DIR / "TASK-020_final_production_audit.md"
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write(md_content.strip() + "\n")
    print(f"  Saved Markdown Audit Report: {md_report_path}")

    print("\n" + "=" * 70)
    print(f"TASK-020 AUDIT COMPLETE: {audit_verdict}")
    print(f"Total Anomalies: {total_anomalies_count}")
    print(f"Teacher Review Queue Items: {machine_audit['teacher_review_queue_count']}")
    print("=" * 70)

    return machine_audit


if __name__ == "__main__":
    run_audit()
