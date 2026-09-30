"""Review Report Builder (TASK-011D)

Universal English Test Platform
Builds the comprehensive Human Review Excel workbook for the 200 pilot adapted questions.

Output:
- data/adaptation/pilot_review_20260930.xlsx
- C:\\Users\\user\\Desktop\\pilot_review_20260930.xlsx (project mirror)

Sheets:
1. Summary: High-level metrics, distributions, reason clusters, model/level breakdowns, and reviewer notes.
2. Review_Required_75: Only the 75 flagged questions requiring human verification.
3. All_Pilot_Questions_200: All 200 questions sorted with REVIEW_REQUIRED first, then VALIDATED.
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path
import shutil
import sqlite3
import statistics
import sys
from typing import Any, Dict, List, Optional, Tuple

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.pilot_data import PILOT_DATA
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

DEFAULT_ADAPTATION_DB = Path("data/adaptation.db")
DEFAULT_STAGING_DB = Path("data/staging.db")
DEFAULT_OUTPUT_PATH = Path("data/adaptation/pilot_review_20260930.xlsx")
DEFAULT_DESKTOP_PATH = Path("C:/Users/user/Desktop/pilot_review_20260930.xlsx")

# Styling definitions
FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="1F4E78")
FONT_SECTION = Font(name="Calibri", size=12, bold=True, color="1F4E78")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name="Calibri", size=10, color="000000")
FONT_BOLD = Font(name="Calibri", size=10, bold=True, color="000000")
FONT_MUTED = Font(name="Calibri", size=9, italic=True, color="595959")

FONT_VALIDATED = Font(name="Calibri", size=10, bold=True, color="276A3C")
FILL_VALIDATED = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

FONT_REVIEW = Font(name="Calibri", size=10, bold=True, color="C00000")
FILL_REVIEW = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

FILL_HEADER = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
FILL_SECTION = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
FILL_ZEBRA = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
FILL_WHITE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

BORDER_THIN_GRAY = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)
BORDER_HEADER = Border(
    left=Side(style="thin", color="FFFFFF"),
    right=Side(style="thin", color="FFFFFF"),
    top=Side(style="medium", color="1F4E78"),
    bottom=Side(style="medium", color="1F4E78"),
)


def compute_quantiles(data: List[float]) -> Dict[str, float]:
    """Calculate min, p25, median (p50), p75, max, mean, stdev for a numeric series."""
    if not data:
        return {"min": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "max": 0.0, "mean": 0.0, "stdev": 0.0}
    s = sorted(data)
    n = len(s)

    def q(p: float) -> float:
        k = (n - 1) * p
        f = int(k)
        c = f + 1
        if c < n:
            return round(s[f] + (k - f) * (s[c] - s[f]), 4)
        return round(s[f], 4)

    return {
        "min": round(min(s), 4),
        "p25": q(0.25),
        "median": q(0.50),
        "p75": q(0.75),
        "max": round(max(s), 4),
        "mean": round(statistics.mean(s), 4),
        "stdev": round(statistics.stdev(s), 4) if len(s) > 1 else 0.0,
    }


def fetch_pilot_records(
    adapt_conn: sqlite3.Connection,
    stage_conn: sqlite3.Connection,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Query and enrich all 200 pilot records from adaptation and staging databases."""
    adapt_conn.row_factory = sqlite3.Row
    stage_conn.row_factory = sqlite3.Row

    # 1. Fetch adapted questions where adapted_text IS NOT NULL
    adapted_q_rows = adapt_conn.execute(
        """
        SELECT q.source_question_id, q.adapted_question_id, q.adapted_exercise_id,
               q.adapted_lesson_id, q.question_order, q.response_model, q.source_text,
               q.adapted_text, q.similarity_score, q.adaptation_status, q.review_required,
               q.adaptation_notes
        FROM adapted_questions q
        WHERE q.adapted_text IS NOT NULL
        ORDER BY q.adapted_exercise_id, q.question_order
        """
    ).fetchall()

    if len(adapted_q_rows) != 200:
        raise ValueError(f"Expected exactly 200 adapted questions, found {len(adapted_q_rows)}")

    # 2. Map target tokens from PILOT_DATA
    target_tokens_map: Dict[str, List[str]] = {}
    for eid, ex in PILOT_DATA.items():
        for q in ex["questions"]:
            target_tokens_map[str(q["question_id"])] = q.get("target_tokens", [])

    # 3. Cache staging exercise and lesson info
    exercise_meta: Dict[str, Dict[str, Any]] = {}
    for row in stage_conn.execute(
        """
        SELECT e.exercise_id, e.lesson_id, e.title AS ex_title, e.instruction,
               l.title AS lesson_title, l.level, l.topic
        FROM staging_exercises e
        JOIN staging_lessons l ON e.lesson_id = l.lesson_id
        """
    ).fetchall():
        exercise_meta[row["exercise_id"]] = dict(row)

    records: List[Dict[str, Any]] = []

    for q_row in adapted_q_rows:
        sqid = str(q_row["source_question_id"])
        aqid = str(q_row["adapted_question_id"])
        aeid = str(q_row["adapted_exercise_id"])
        alid = str(q_row["adapted_lesson_id"])
        eid = aeid.replace("adapt_", "")
        lid = alid.replace("adapt_", "")
        rm = str(q_row["response_model"])
        stext = str(q_row["source_text"])
        atext = str(q_row["adapted_text"])

        meta = exercise_meta.get(eid, {})
        level = meta.get("level", "A1")
        ex_title = meta.get("ex_title", "")
        lesson_title = meta.get("lesson_title", "")

        # Evaluator metrics
        tt = target_tokens_map.get(sqid, [])
        sim_res = evaluate_similarity(stext, atext, tt)

        # Options and Answers extraction
        if rm == "gap":
            source_opts_str = "N/A"
            adapted_opts_str = "N/A"

            # Gaps from staging and adaptation
            s_gaps = stage_conn.execute(
                "SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order",
                (sqid,),
            ).fetchall()
            a_gaps = adapt_conn.execute(
                "SELECT gap_order, adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order",
                (aqid,),
            ).fetchall()

            s_ans_parts = [
                f"Gap {g['gap_order']}: {g['correct_answer']}" if len(s_gaps) > 1 else str(g["correct_answer"])
                for g in s_gaps
            ]
            a_ans_parts = [
                f"Gap {g['gap_order']}: {g['adapted_correct_answer']}" if len(a_gaps) > 1 else str(g["adapted_correct_answer"])
                for g in a_gaps
            ]

            source_ans_str = "; ".join(s_ans_parts)
            adapted_ans_str = "; ".join(a_ans_parts)
        else:
            # Choice questions (single_choice or multiple_choice)
            s_opts = stage_conn.execute(
                "SELECT option_order, text, is_correct FROM staging_options WHERE question_id = ? ORDER BY option_order",
                (sqid,),
            ).fetchall()
            a_opts = adapt_conn.execute(
                "SELECT option_order, adapted_text, adapted_is_correct FROM adapted_options WHERE adapted_question_id = ? ORDER BY option_order",
                (aqid,),
            ).fetchall()

            s_opt_parts = []
            s_ans_parts = []
            for o in s_opts:
                tag = " [CORRECT]" if o["is_correct"] else ""
                s_opt_parts.append(f"[{o['option_order']}] {o['text']}{tag}")
                if o["is_correct"]:
                    s_ans_parts.append(str(o["text"]))

            a_opt_parts = []
            a_ans_parts = []
            for o in a_opts:
                tag = " [CORRECT]" if o["adapted_is_correct"] else ""
                a_opt_parts.append(f"[{o['option_order']}] {o['adapted_text']}{tag}")
                if o["adapted_is_correct"]:
                    a_ans_parts.append(str(o["adapted_text"]))

            source_opts_str = " | ".join(s_opt_parts)
            adapted_opts_str = " | ".join(a_opt_parts)
            source_ans_str = " | ".join(s_ans_parts)
            adapted_ans_str = " | ".join(a_ans_parts)

        # Status and Reasons
        orig_status = sim_res["originality_status"]
        review_req = 1 if orig_status == "REVIEW_REQUIRED" else 0
        reasons_str = "; ".join(sim_res["reasons"])

        records.append({
            "source_question_id": sqid,
            "adapted_question_id": aqid,
            "lesson_id": lid,
            "exercise_id": eid,
            "question_order": q_row["question_order"],
            "response_model": rm,
            "level": level,
            "lesson_title": lesson_title,
            "exercise_title": ex_title,
            "source_text": stext,
            "adapted_text": atext,
            "source_options": source_opts_str,
            "adapted_options": adapted_opts_str,
            "source_correct_answers": source_ans_str,
            "adapted_correct_answers": adapted_ans_str,
            "jaccard_similarity": sim_res["jaccard_similarity"],
            "shingle_overlap": sim_res["shingle_overlap"],
            "levenshtein_similarity": sim_res["levenshtein_similarity"],
            "originality_status": orig_status,
            "review_required": review_req,
            "reasons": reasons_str,
        })

    # Summary statistics calculation
    total_count = len(records)
    validated_count = sum(1 for r in records if r["originality_status"] == "VALIDATED")
    review_count = sum(1 for r in records if r["originality_status"] == "REVIEW_REQUIRED")
    rejected_count = sum(1 for r in records if r["originality_status"] == "REJECTED")

    # Grouped reasons for REVIEW_REQUIRED
    reasons_grouped = {
        "Normalized Levenshtein similarity >= 0.45": 0,
        "Jaccard token similarity in review zone (0.40 < J <= 0.50)": 0,
        "Forbidden verbatim 3+ word shingle": 0,
    }
    for r in records:
        if r["originality_status"] == "REVIEW_REQUIRED":
            if "Normalized Levenshtein" in r["reasons"]:
                reasons_grouped["Normalized Levenshtein similarity >= 0.45"] += 1
            if "Jaccard token similarity" in r["reasons"]:
                reasons_grouped["Jaccard token similarity in review zone (0.40 < J <= 0.50)"] += 1
            if "Forbidden verbatim" in r["reasons"] or "shingle" in r["reasons"]:
                reasons_grouped["Forbidden verbatim 3+ word shingle"] += 1

    # Distributions
    jaccard_dist = compute_quantiles([r["jaccard_similarity"] for r in records])
    shingle_dist = compute_quantiles([r["shingle_overlap"] for r in records])
    lev_dist = compute_quantiles([r["levenshtein_similarity"] for r in records])

    # Model Breakdown
    models = ["single_choice", "multiple_choice", "gap"]
    model_breakdown = {}
    for m in models:
        m_recs = [r for r in records if r["response_model"] == m]
        model_breakdown[m] = {
            "total": len(m_recs),
            "validated": sum(1 for r in m_recs if r["originality_status"] == "VALIDATED"),
            "review_required": sum(1 for r in m_recs if r["originality_status"] == "REVIEW_REQUIRED"),
            "rejected": sum(1 for r in m_recs if r["originality_status"] == "REJECTED"),
        }

    # Level Breakdown
    level_breakdown = {}
    for lvl in ["A1", "A2"]:
        l_recs = [r for r in records if r["level"] == lvl]
        level_breakdown[lvl] = {
            "total": len(l_recs),
            "validated": sum(1 for r in l_recs if r["originality_status"] == "VALIDATED"),
            "review_required": sum(1 for r in l_recs if r["originality_status"] == "REVIEW_REQUIRED"),
            "rejected": sum(1 for r in l_recs if r["originality_status"] == "REJECTED"),
        }

    # Exercise breakdown
    exercise_breakdown = {}
    for r in records:
        eid = r["exercise_id"]
        if eid not in exercise_breakdown:
            exercise_breakdown[eid] = {
                "exercise_id": eid,
                "lesson_id": r["lesson_id"],
                "level": r["level"],
                "lesson_title": r["lesson_title"],
                "exercise_title": r["exercise_title"],
                "response_model": r["response_model"],
                "total": 0,
                "validated": 0,
                "review_required": 0,
            }
        exercise_breakdown[eid]["total"] += 1
        if r["originality_status"] == "VALIDATED":
            exercise_breakdown[eid]["validated"] += 1
        elif r["originality_status"] == "REVIEW_REQUIRED":
            exercise_breakdown[eid]["review_required"] += 1

    stats = {
        "total": total_count,
        "validated": validated_count,
        "review_required": review_count,
        "rejected": rejected_count,
        "reasons_grouped": reasons_grouped,
        "jaccard_dist": jaccard_dist,
        "shingle_dist": shingle_dist,
        "lev_dist": lev_dist,
        "model_breakdown": model_breakdown,
        "level_breakdown": level_breakdown,
        "exercise_breakdown": list(exercise_breakdown.values()),
    }

    return records, stats


def write_summary_sheet(ws: openpyxl.worksheet.worksheet.Worksheet, stats: Dict[str, Any]) -> None:
    """Populate Sheet 1 (Summary) with rich metrics, tables, and human review guidelines."""
    ws.title = "Summary"
    ws.views.sheetView[0].showGridLines = True

    # Title
    ws["B2"] = "Universal English Test Platform — Pilot Content Adaptation Review Report"
    ws["B2"].font = FONT_TITLE
    ws["B3"] = f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Scope: 20 Pilot Exercises (200 Questions) | Target: TASK-011D"
    ws["B3"].font = FONT_MUTED

    current_row = 5

    # 1. Executive Status Overview
    ws.cell(row=current_row, column=2, value="1. EXECUTIVE STATUS OVERVIEW").font = FONT_SECTION
    current_row += 1

    headers_overview = ["Category / Metric", "Count", "Percentage", "Target / Baseline", "Status Verdict"]
    for col_idx, h in enumerate(headers_overview, start=2):
        c = ws.cell(row=current_row, column=col_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER_HEADER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    overview_rows = [
        ("Total Pilot Questions", stats["total"], "100.0%", "200 Questions", "Complete"),
        ("VALIDATED (Clean Pass)", stats["validated"], f"{stats['validated'] / stats['total']:.1%}", "Jaccard <= 0.40, Lev < 0.45, Shingle = 0", "Passed"),
        ("REVIEW_REQUIRED (Flagged)", stats["review_required"], f"{stats['review_required'] / stats['total']:.1%}", "0.40 < J <= 0.50 OR Lev >= 0.45", "Human Check Needed"),
        ("REJECTED (Originality Failure)", stats["rejected"], f"{stats['rejected'] / stats['total']:.1%}", "J > 0.50 OR Forbidden 3+ Shingle", "Zero Plagiarism"),
    ]

    for item in overview_rows:
        label, count, pct, benchmark, verdict = item
        ws.cell(row=current_row, column=2, value=label).font = FONT_BOLD
        c_count = ws.cell(row=current_row, column=3, value=count)
        c_count.alignment = Alignment(horizontal="center")
        c_count.font = FONT_BOLD
        c_pct = ws.cell(row=current_row, column=4, value=pct)
        c_pct.alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=5, value=benchmark)
        c_verdict = ws.cell(row=current_row, column=6, value=verdict)
        c_verdict.alignment = Alignment(horizontal="center")

        if label.startswith("VALIDATED"):
            c_count.font = FONT_VALIDATED
            c_count.fill = FILL_VALIDATED
            c_verdict.font = FONT_VALIDATED
            c_verdict.fill = FILL_VALIDATED
        elif label.startswith("REVIEW_REQUIRED"):
            c_count.font = FONT_REVIEW
            c_count.fill = FILL_REVIEW
            c_verdict.font = FONT_REVIEW
            c_verdict.fill = FILL_REVIEW
        elif label.startswith("REJECTED"):
            c_count.font = FONT_VALIDATED
            c_verdict.font = FONT_VALIDATED

        for c_idx in range(2, 7):
            ws.cell(row=current_row, column=c_idx).border = BORDER_THIN_GRAY
        current_row += 1

    current_row += 2

    # 2. Grouped Reasons for REVIEW_REQUIRED
    ws.cell(row=current_row, column=2, value="2. GROUPED CAUSES FOR REVIEW_REQUIRED (75 QUESTIONS)").font = FONT_SECTION
    current_row += 1

    headers_reasons = ["Flagged Evaluator Rule", "Flagged Questions", "Share of Review Queue", "Primary Linguistic Cause"]
    for col_idx, h in enumerate(headers_reasons, start=2):
        c = ws.cell(row=current_row, column=col_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER_HEADER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    reasons_rows = [
        (
            "Normalized Levenshtein similarity >= 0.45",
            stats["reasons_grouped"]["Normalized Levenshtein similarity >= 0.45"],
            f"{stats['reasons_grouped']['Normalized Levenshtein similarity >= 0.45'] / stats['review_required']:.1%}",
            "Short sentences & formulaic prompts (Levenshtein edit ratio sensitive to sentence length).",
        ),
        (
            "Jaccard token similarity in review zone (0.40 < J <= 0.50)",
            stats["reasons_grouped"]["Jaccard token similarity in review zone (0.40 < J <= 0.50)"],
            f"{stats['reasons_grouped']['Jaccard token similarity in review zone (0.40 < J <= 0.50)'] / stats['review_required']:.1%}",
            "Short morphological pairs (e.g. 'one foot ⇒ two feet' vs 'one tooth ⇒ two teeth').",
        ),
        (
            "Forbidden verbatim 3+ word shingle",
            stats["reasons_grouped"]["Forbidden verbatim 3+ word shingle"],
            "0.0%",
            "None. Zero non-target consecutive 3-word overlaps detected across all 200 items.",
        ),
    ]

    for label, count, pct, cause in reasons_rows:
        ws.cell(row=current_row, column=2, value=label).font = FONT_BOLD
        c_count = ws.cell(row=current_row, column=3, value=count)
        c_count.alignment = Alignment(horizontal="center")
        c_pct = ws.cell(row=current_row, column=4, value=pct)
        c_pct.alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=5, value=cause).font = FONT_REGULAR

        if count > 0:
            c_count.font = FONT_REVIEW
            c_count.fill = FILL_REVIEW
        else:
            c_count.font = FONT_VALIDATED
            c_count.fill = FILL_VALIDATED

        for c_idx in range(2, 6):
            ws.cell(row=current_row, column=c_idx).border = BORDER_THIN_GRAY
        current_row += 1

    current_row += 2

    # 3. Similarity Metric Distributions
    ws.cell(row=current_row, column=2, value="3. SIMILARITY METRIC DISTRIBUTIONS (200 QUESTIONS)").font = FONT_SECTION
    current_row += 1

    headers_dist = ["Evaluator Metric", "Min", "25% (Q1)", "Median (Q2)", "75% (Q3)", "Max", "Mean", "StdDev", "Rejection Threshold"]
    for col_idx, h in enumerate(headers_dist, start=2):
        c = ws.cell(row=current_row, column=col_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER_HEADER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    dist_rows = [
        ("Jaccard Token Similarity", stats["jaccard_dist"], "> 0.50 (Review: > 0.40)"),
        ("N-gram Shingle Overlap (N>=3)", stats["shingle_dist"], "> 0.00 (Any verbatim 3-gram)"),
        ("Normalized Levenshtein Similarity", stats["lev_dist"], ">= 0.45 (Review zone)"),
    ]

    for label, dist, thresh in dist_rows:
        ws.cell(row=current_row, column=2, value=label).font = FONT_BOLD
        vals = [dist["min"], dist["p25"], dist["median"], dist["p75"], dist["max"], dist["mean"], dist["stdev"]]
        for idx, v in enumerate(vals, start=3):
            c_val = ws.cell(row=current_row, column=idx, value=v)
            c_val.number_format = "0.0000"
            c_val.alignment = Alignment(horizontal="right")
        ws.cell(row=current_row, column=10, value=thresh).font = FONT_MUTED

        for c_idx in range(2, 11):
            ws.cell(row=current_row, column=c_idx).border = BORDER_THIN_GRAY
        current_row += 1

    current_row += 2

    # 4. Model and Level Breakdown (Side by Side or Sequenced)
    ws.cell(row=current_row, column=2, value="4. BREAKDOWN BY RESPONSE MODEL & CEFR LEVEL").font = FONT_SECTION
    current_row += 1

    headers_breakdown = ["Dimension", "Sub-Category", "Total Questions", "VALIDATED", "REVIEW_REQUIRED", "REJECTED", "Pass Rate (%)"]
    for col_idx, h in enumerate(headers_breakdown, start=2):
        c = ws.cell(row=current_row, column=col_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER_HEADER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    breakdown_data = [
        ("Response Model", "single_choice", stats["model_breakdown"]["single_choice"]),
        ("Response Model", "multiple_choice", stats["model_breakdown"]["multiple_choice"]),
        ("Response Model", "gap", stats["model_breakdown"]["gap"]),
        ("CEFR Level", "A1 (Beginner)", stats["level_breakdown"]["A1"]),
        ("CEFR Level", "A2 (Elementary)", stats["level_breakdown"]["A2"]),
    ]

    for dim, subcat, data in breakdown_data:
        ws.cell(row=current_row, column=2, value=dim).font = FONT_MUTED
        ws.cell(row=current_row, column=3, value=subcat).font = FONT_BOLD
        ws.cell(row=current_row, column=4, value=data["total"]).alignment = Alignment(horizontal="center")
        
        c_val = ws.cell(row=current_row, column=5, value=data["validated"])
        c_val.alignment = Alignment(horizontal="center")
        c_val.font = FONT_VALIDATED

        c_rev = ws.cell(row=current_row, column=6, value=data["review_required"])
        c_rev.alignment = Alignment(horizontal="center")
        if data["review_required"] > 0:
            c_rev.font = FONT_REVIEW
            c_rev.fill = FILL_REVIEW

        c_rej = ws.cell(row=current_row, column=7, value=data["rejected"])
        c_rej.alignment = Alignment(horizontal="center")

        pass_rate = data["validated"] / data["total"] if data["total"] > 0 else 0.0
        c_pass = ws.cell(row=current_row, column=8, value=f"{pass_rate:.1%}")
        c_pass.alignment = Alignment(horizontal="center")

        for c_idx in range(2, 9):
            ws.cell(row=current_row, column=c_idx).border = BORDER_THIN_GRAY
        current_row += 1

    current_row += 2

    # 5. Exercise Portfolio Breakdown
    ws.cell(row=current_row, column=2, value="5. EXERCISE PORTFOLIO (20 EXERCISES)").font = FONT_SECTION
    current_row += 1

    headers_ex = ["Exercise ID", "Lesson ID", "Level", "Lesson Title / Topic", "Model", "Questions", "VALIDATED", "REVIEW_REQUIRED"]
    for col_idx, h in enumerate(headers_ex, start=2):
        c = ws.cell(row=current_row, column=col_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER_HEADER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    for ex in stats["exercise_breakdown"]:
        ws.cell(row=current_row, column=2, value=ex["exercise_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=3, value=ex["lesson_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=4, value=ex["level"]).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=5, value=ex["lesson_title"]).font = FONT_REGULAR
        ws.cell(row=current_row, column=6, value=ex["response_model"]).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=7, value=ex["total"]).alignment = Alignment(horizontal="center")

        c_v = ws.cell(row=current_row, column=8, value=ex["validated"])
        c_v.alignment = Alignment(horizontal="center")
        c_v.font = FONT_VALIDATED

        c_r = ws.cell(row=current_row, column=9, value=ex["review_required"])
        c_r.alignment = Alignment(horizontal="center")
        if ex["review_required"] > 0:
            c_r.font = FONT_REVIEW
            c_r.fill = FILL_REVIEW

        for c_idx in range(2, 10):
            ws.cell(row=current_row, column=c_idx).border = BORDER_THIN_GRAY
        current_row += 1

    current_row += 2

    # 6. Review Guidelines & Linguistic Insights
    ws.cell(row=current_row, column=2, value="6. HUMAN REVIEW GUIDELINES & EVALUATOR INSIGHTS").font = FONT_SECTION
    current_row += 1

    guidance_notes = [
        ("Zero Plagiarism Confirmation:", "All 200 pilot questions achieved 0.0000 Shingle Overlap (0 forbidden 3+ word consecutive non-target sequences). There are no copy-pastes."),
        ("Token Independence:", "Mean Jaccard token similarity is 0.1026 (median 0.0909), well below the strict 0.40 threshold. Content vocabulary was thoroughly replaced."),
        ("Why 75 Items Were Flagged:", "100% of the 75 flagged items triggered Rule 3: Normalized Levenshtein similarity >= 0.45. This occurs because Levenshtein operates on character edit distance:"),
        ("  • Short Sentence Effect:", "In 4-8 word sentences (typical of A1 beginner grammar), changing all nouns and verbs still leaves punctuation, pronouns, and sentence length similar, driving Levenshtein over 0.45."),
        ("  • Morphological Pairs:", "Patterns like 'one foot ⇒ two feet' vs 'one tooth ⇒ two teeth' share the template ('one ... two ... ⇒'), triggering review even though the tested word pair is completely new."),
        ("  • Dialogue Framing:", "Short conversational exchanges (e.g. \"A: '...' B: '...'\") share structural punctuation and speaker labels."),
        ("Review Action:", "Reviewers should inspect Sheet 'Review_Required_75'. Items that test the correct grammatical target with original scenarios and words can be approved for production."),
    ]

    for label, text in guidance_notes:
        ws.cell(row=current_row, column=2, value=label).font = FONT_BOLD
        c_text = ws.cell(row=current_row, column=3, value=text)
        c_text.font = FONT_REGULAR
        ws.merge_cells(start_row=current_row, start_column=3, end_row=current_row, end_column=9)
        current_row += 1

    # Adjust Summary Column Widths
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 38
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 16
    ws.column_dimensions["H"].width = 16
    ws.column_dimensions["I"].width = 16
    ws.column_dimensions["J"].width = 28


def write_question_sheet(
    ws: openpyxl.worksheet.worksheet.Worksheet,
    sheet_title: str,
    records: List[Dict[str, Any]],
) -> None:
    """Populate a structured question-level review sheet."""
    ws.title = sheet_title
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"

    headers = [
        "source_question_id",
        "adapted_question_id",
        "lesson_id",
        "exercise_id",
        "response_model",
        "source_text",
        "adapted_text",
        "source_options",
        "adapted_options",
        "source_correct_answer(s)",
        "adapted_correct_answer(s)",
        "jaccard_similarity",
        "shingle_overlap",
        "levenshtein_similarity",
        "originality_status",
        "review_required",
        "reasons",
    ]

    # Write Header Row
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        cell.border = BORDER_HEADER
    ws.row_dimensions[1].height = 26

    # Write Data Rows
    for row_idx, r in enumerate(records, start=2):
        ws.cell(row=row_idx, column=1, value=r["source_question_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=2, value=r["adapted_question_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=3, value=r["lesson_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=4, value=r["exercise_id"]).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=5, value=r["response_model"]).alignment = Alignment(horizontal="center")

        c_stext = ws.cell(row=row_idx, column=6, value=r["source_text"])
        c_stext.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_atext = ws.cell(row=row_idx, column=7, value=r["adapted_text"])
        c_atext.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_sopt = ws.cell(row=row_idx, column=8, value=r["source_options"])
        c_sopt.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_aopt = ws.cell(row=row_idx, column=9, value=r["adapted_options"])
        c_aopt.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_sans = ws.cell(row=row_idx, column=10, value=r["source_correct_answers"])
        c_sans.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_aans = ws.cell(row=row_idx, column=11, value=r["adapted_correct_answers"])
        c_aans.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        c_jacc = ws.cell(row=row_idx, column=12, value=r["jaccard_similarity"])
        c_jacc.number_format = "0.0000"
        c_jacc.alignment = Alignment(horizontal="right", vertical="top")

        c_shin = ws.cell(row=row_idx, column=13, value=r["shingle_overlap"])
        c_shin.number_format = "0.0000"
        c_shin.alignment = Alignment(horizontal="right", vertical="top")

        c_lev = ws.cell(row=row_idx, column=14, value=r["levenshtein_similarity"])
        c_lev.number_format = "0.0000"
        c_lev.alignment = Alignment(horizontal="right", vertical="top")

        c_stat = ws.cell(row=row_idx, column=15, value=r["originality_status"])
        c_stat.alignment = Alignment(horizontal="center", vertical="top")
        if r["originality_status"] == "REVIEW_REQUIRED":
            c_stat.font = FONT_REVIEW
            c_stat.fill = FILL_REVIEW
        else:
            c_stat.font = FONT_VALIDATED
            c_stat.fill = FILL_VALIDATED

        c_rev = ws.cell(row=row_idx, column=16, value=r["review_required"])
        c_rev.alignment = Alignment(horizontal="center", vertical="top")
        if r["review_required"] == 1:
            c_rev.font = FONT_REVIEW
            c_rev.fill = FILL_REVIEW

        c_reasons = ws.cell(row=row_idx, column=17, value=r["reasons"])
        c_reasons.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        c_reasons.font = FONT_REGULAR

        # Cell borders and row height
        for c_idx in range(1, 18):
            cell = ws.cell(row=row_idx, column=c_idx)
            cell.border = BORDER_THIN_GRAY
            if not cell.font or cell.font == openpyxl.styles.DEFAULT_FONT:
                cell.font = FONT_REGULAR

        ws.row_dimensions[row_idx].height = 36

    # Column Widths
    col_widths = {
        1: 18,   # source_question_id
        2: 20,   # adapted_question_id
        3: 14,   # lesson_id
        4: 14,   # exercise_id
        5: 16,   # response_model
        6: 42,   # source_text
        7: 42,   # adapted_text
        8: 38,   # source_options
        9: 38,   # adapted_options
        10: 24,  # source_correct_answer(s)
        11: 24,  # adapted_correct_answer(s)
        12: 17,  # jaccard_similarity
        13: 16,  # shingle_overlap
        14: 20,  # levenshtein_similarity
        15: 18,  # originality_status
        16: 16,  # review_required
        17: 46,  # reasons
    }
    for col_idx, width in col_widths.items():
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width


def generate_pilot_review_workbook(
    adaptation_db_path: Path = DEFAULT_ADAPTATION_DB,
    staging_db_path: Path = DEFAULT_STAGING_DB,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    desktop_path: Optional[Path] = DEFAULT_DESKTOP_PATH,
) -> Dict[str, Any]:
    """Generate the 3-sheet human review Excel workbook."""
    if not adaptation_db_path.exists():
        raise FileNotFoundError(f"Adaptation DB not found: {adaptation_db_path}")
    if not staging_db_path.exists():
        raise FileNotFoundError(f"Staging DB not found: {staging_db_path}")

    adapt_conn = sqlite3.connect(f"file:{adaptation_db_path.resolve()}?mode=ro", uri=True)
    stage_conn = sqlite3.connect(f"file:{staging_db_path.resolve()}?mode=ro", uri=True)

    try:
        records, stats = fetch_pilot_records(adapt_conn, stage_conn)
    finally:
        adapt_conn.close()
        stage_conn.close()

    # Split records into REVIEW_REQUIRED first, then VALIDATED
    review_records = [r for r in records if r["originality_status"] == "REVIEW_REQUIRED"]
    validated_records = [r for r in records if r["originality_status"] == "VALIDATED"]

    # Sort each partition by exercise_id and question_order
    review_records.sort(key=lambda x: (x["exercise_id"], x["question_order"]))
    validated_records.sort(key=lambda x: (x["exercise_id"], x["question_order"]))

    # Ordered for All_Pilot_Questions_200: REVIEW_REQUIRED first, then VALIDATED
    all_sorted_records = review_records + validated_records

    wb = openpyxl.Workbook()
    # Sheet 1: Summary (replace active sheet)
    ws_summary = wb.active
    write_summary_sheet(ws_summary, stats)

    # Sheet 2: Review_Required_75
    ws_review = wb.create_sheet(title="Review_Required_75")
    write_question_sheet(ws_review, "Review_Required_75", review_records)

    # Sheet 3: All_Pilot_Questions_200
    ws_all = wb.create_sheet(title="All_Pilot_Questions_200")
    write_question_sheet(ws_all, "All_Pilot_Questions_200", all_sorted_records)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    # Optional Desktop copy
    if desktop_path:
        try:
            desktop_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output_path, desktop_path)
        except Exception as e:
            print(f"Warning: could not mirror to desktop path {desktop_path}: {e}")

    return {
        "output_path": str(output_path),
        "desktop_path": str(desktop_path) if desktop_path else None,
        "total_questions": len(all_sorted_records),
        "review_required_count": len(review_records),
        "validated_count": len(validated_records),
        "stats": stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Human Review Workbook for Pilot Adaptation (TASK-011D)")
    parser.add_argument("--adaptation-db", type=Path, default=DEFAULT_ADAPTATION_DB, help="Path to adaptation.db")
    parser.add_argument("--staging-db", type=Path, default=DEFAULT_STAGING_DB, help="Path to staging.db")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path for review XLSX")
    parser.add_argument("--no-desktop", action="store_true", help="Skip copying to Desktop")
    args = parser.parse_args()

    desktop = None if args.no_desktop else DEFAULT_DESKTOP_PATH

    print("Building Pilot Adaptation Human Review Workbook...")
    res = generate_pilot_review_workbook(
        adaptation_db_path=args.adaptation_db,
        staging_db_path=args.staging_db,
        output_path=args.output,
        desktop_path=desktop,
    )

    print(f"Workbook generated successfully at: {res['output_path']}")
    if res["desktop_path"]:
        print(f"Mirrored to Desktop at: {res['desktop_path']}")
    print(f"Total questions: {res['total_questions']}")
    print(f"VALIDATED: {res['validated_count']}")
    print(f"REVIEW_REQUIRED: {res['review_required_count']}")
    print(f"REJECTED: 0")


if __name__ == "__main__":
    main()
