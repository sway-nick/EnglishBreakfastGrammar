"""
enrichment_workbook_builder.py
Generates the Google Sheets / Gemini answer enrichment workbook for all
5,614 currently unresolved questions in data/staging.db.

STRICT CONTRACT:
1. Does NOT call Gemini API.
2. Does NOT modify staging.db.
3. Does NOT modify the existing 182-question checkpoint.
4. Excludes all 182 already-answered questions (224 gaps, 258 options).
5. Populates complete question context, instruction, sentence, and options_context.
6. Tailors strict JSON prompts for gap, single_choice, and multiple_choice.
7. Writes to:
   - C:\\Users\\user\\Desktop\\english_cms_gemini_remaining_5614.xlsx
   - data/gemini/english_cms_gemini_remaining_5614.xlsx
"""

from pathlib import Path
import argparse
import json
import logging
import sqlite3
import sys
from typing import Dict, Any, List, Tuple
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "staging.db"

LOCAL_OUTPUT = REPO_ROOT / "data" / "gemini" / "english_cms_gemini_remaining_5614.xlsx"
DESKTOP_OUTPUT = Path.home() / "Desktop" / "english_cms_gemini_remaining_5614.xlsx"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("enrichment_workbook_builder")


def setup_sheet(ws, headers: List[str]):
    header_fill = PatternFill(fill_type="solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.append(headers)
    for cell in ws[2]:  # Row 2 contains headers
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    ws.freeze_panes = "A3"
    ws.row_dimensions[2].height = 28


def finish_sheet(ws):
    body_alignment = Alignment(vertical="top", wrap_text=True)
    for column_cells in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)
        for cell in column_cells:
            if cell.value is not None:
                val = str(cell.value)
                if len(val) > max_length:
                    max_length = len(val)
        width = min(max(max_length + 2, 12), 65)
        ws.column_dimensions[column_letter].width = width

    for row in ws.iter_rows(min_row=3):
        for cell in row:
            cell.alignment = body_alignment


def fetch_unresolved_questions(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Fetches all 5,614 unresolved questions with full exercise and options context."""
    cursor = conn.cursor()

    # Query all questions excluding those already answered
    query = """
        SELECT
            q.question_id,
            q.exercise_id,
            q.lesson_id,
            q.question_order,
            q.response_model,
            e.instruction,
            e.title AS exercise_title,
            q.content
        FROM staging_questions q
        JOIN staging_exercises e ON q.exercise_id = e.exercise_id
        WHERE q.question_id NOT IN (
            SELECT DISTINCT question_id FROM staging_gaps WHERE correct_answer IS NOT NULL
            UNION
            SELECT DISTINCT question_id FROM staging_options WHERE is_correct IS NOT NULL
        )
        ORDER BY q.lesson_id, q.exercise_id, q.question_order;
    """
    cursor.execute(query)
    raw_rows = cursor.fetchall()
    logger.info(f"Fetched {len(raw_rows)} unresolved question candidates from staging.db")

    unresolved_items = []
    for row in raw_rows:
        qid, ex_id, les_id, q_order, resp_model, inst, ex_title, content = row
        effective_inst = inst.strip() if (inst and inst.strip()) else (ex_title.strip() if ex_title else "")

        # Build options context based on response_model
        if resp_model == "gap":
            cursor.execute("""
                SELECT gap_id, gap_order, input_control
                FROM staging_gaps
                WHERE question_id = ?
                ORDER BY gap_order;
            """, (qid,))
            gaps = cursor.fetchall()

            gap_contexts = []
            for gid, g_order, ctrl in gaps:
                if ctrl == "select":
                    cursor.execute("""
                        SELECT text FROM staging_options
                        WHERE gap_id = ?
                        ORDER BY option_order;
                    """, (gid,))
                    opts = [r[0] for r in cursor.fetchall()]
                    opts_json = json.dumps(opts, ensure_ascii=False)
                    gap_contexts.append(f"gap_{g_order}: {opts_json}")
                else:
                    gap_contexts.append(f"gap_{g_order}: [free text input]")

            options_context = " | ".join(gap_contexts)

        elif resp_model in ("single_choice", "multiple_choice"):
            cursor.execute("""
                SELECT text FROM staging_options
                WHERE question_id = ?
                ORDER BY option_order;
            """, (qid,))
            opts = [r[0] for r in cursor.fetchall()]
            options_context = json.dumps(opts, ensure_ascii=False)

        else:
            options_context = ""

        unresolved_items.append({
            "question_id": qid,
            "exercise_id": ex_id,
            "lesson_id": les_id,
            "order": q_order,
            "response_model": resp_model,
            "instruction": effective_inst,
            "sentence": content,
            "options_context": options_context,
        })

    return unresolved_items


def build_formula(row_idx: int, response_model: str) -> str:
    """Builds model-tailored Google Sheets AI/Gemini formula for a specific row index."""
    if response_model == "gap":
        prompt = (
            f'"Task instruction: " & F{row_idx} & ". Question/Sentence: \'" & G{row_idx} & "\'. '
            f'Gaps and options: " & H{row_idx} & ". '
            'Return ONLY a valid JSON object mapping gap IDs to the exact selected option strings '
            '(e.g. {""gap_1"":""...""}). '
            'Do not return markdown, backticks, or any explanation. Output strictly valid JSON."'
        )
    elif response_model == "single_choice":
        prompt = (
            f'"Task instruction: " & F{row_idx} & ". Question: \'" & G{row_idx} & "\'. '
            f'Options: " & H{row_idx} & ". '
            'Return ONLY a valid JSON object in the exact format {""answer"":""exact option text""}. '
            'The answer must be selected from the provided options. '
            'Do not return markdown, backticks, or any explanation. Output strictly valid JSON."'
        )
    elif response_model == "multiple_choice":
        prompt = (
            f'"Task instruction: " & F{row_idx} & ". Question: \'" & G{row_idx} & "\'. '
            f'Options: " & H{row_idx} & ". '
            'Return ONLY a valid JSON object in the exact format {""answers"":[""option 1"",""option 2""]}. '
            'All answers must be selected from the provided options. '
            'Do not return markdown, backticks, or any explanation. Output strictly valid JSON."'
        )
    else:
        prompt = (
            f'"Task instruction: " & F{row_idx} & ". Question: \'" & G{row_idx} & "\'. '
            f'Context: " & H{row_idx} & ". Return ONLY valid JSON answer."'
        )

    return f'=IFERROR(GEMINI({prompt}), "")'


def create_enrichment_workbook(items: List[Dict[str, Any]], output_path: Path):
    """Creates the full workbook with Gemini_Enrichment and README sheets."""
    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    # 1. Sheet: Gemini_Enrichment
    ws = wb.create_sheet("Gemini_Enrichment")

    # Title row
    title_cell = ws.cell(row=1, column=1, value="ENGLISH CMS - FULL UNRESOLVED CORPUS ENRICHMENT WORKBOOK (5,614 QUESTIONS)")
    title_cell.font = Font(size=14, bold=True, color="1F4E78")
    ws.row_dimensions[1].height = 25

    headers = [
        "question_id",
        "exercise_id",
        "lesson_id",
        "order",
        "response_model",
        "instruction",
        "sentence",
        "options_context",
        "gemini_formula",
        "gemini_raw_values"
    ]
    setup_sheet(ws, headers)

    for idx, item in enumerate(items, start=3):
        formula = build_formula(idx, item["response_model"])
        ws.append([
            int(item["question_id"]) if item["question_id"].isdigit() else item["question_id"],
            item["exercise_id"],
            item["lesson_id"],
            item["order"],
            item["response_model"],
            item["instruction"],
            item["sentence"],
            item["options_context"],
            formula,
            ""  # Column J: raw values placeholder
        ])

    finish_sheet(ws)

    # 2. Sheet: README
    ws_readme = wb.create_sheet("README")
    readme_title = ws_readme.cell(row=1, column=1, value="FULL CORPUS ANSWER ENRICHMENT GUIDE (5,614 QUESTIONS)")
    readme_title.font = Font(size=14, bold=True, color="1F4E78")
    ws_readme.row_dimensions[1].height = 25

    readme_lines = [
        "",
        "SCOPE & PURPOSE:",
        "1. This workbook contains ONLY the 5,614 currently unresolved questions across the 225-topic Test-English corpus.",
        "2. The 182 already verified questions (224 gaps, 258 options) in data/staging.db are STRICTLY EXCLUDED and must NOT be regenerated.",
        "",
        "STEP-BY-STEP EXECUTION IN GOOGLE SHEETS:",
        "1. UPLOAD: Open Google Drive (drive.google.com) and upload this XLSX file.",
        "2. OPEN AS GOOGLE SHEET: Open the uploaded file and select 'File > Save as Google Sheets'.",
        "3. EVALUATE FORMULAS:",
        "   - Navigate to the 'Gemini_Enrichment' tab.",
        "   - Column I ('gemini_formula') contains the prompt formula.",
        "   - If your Workspace supports =GEMINI(...), formulas will evaluate automatically.",
        "   - If your Workspace uses =AI(...), press Ctrl+H (Find & Replace) and replace '=GEMINI(' with '=AI(' in column I.",
        "   - Due to the large size (5,614 rows), consider evaluating in batches of 500-1000 rows if needed.",
        "4. FREEZE AS VALUES (MANDATORY):",
        "   - Once evaluated, select all results in column I (cells I3:I5616).",
        "   - Copy with Ctrl+C.",
        "   - In column J ('gemini_raw_values'), row 3, right-click and choose 'Paste special > Paste values only' (Ctrl+Shift+V).",
        "   - Alternatively, paste values directly over column I.",
        "5. DOWNLOAD BACK:",
        "   - Go to 'File > Download > Microsoft Excel (.xlsx)'.",
        "   - Save as: C:\\Users\\user\\Desktop\\english_cms_gemini_remaining_5614_results.xlsx",
        "6. IMPORT & MERGE:",
        "   - Run the automated staging import pipeline to merge the answers into data/staging.db.",
    ]

    for line_idx, line in enumerate(readme_lines, start=2):
        cell = ws_readme.cell(row=line_idx, column=1, value=line)
        if line.startswith("SCOPE") or line.startswith("STEP-BY-STEP"):
            cell.font = Font(bold=True, size=11, color="1F4E78")
        else:
            cell.font = Font(size=10)

    ws_readme.column_dimensions["A"].width = 110

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    logger.info(f"Workbook successfully saved to: {output_path}")


def validate_enrichment_workbook(
    items: List[Dict[str, Any]],
    xlsx_path: Path,
    conn: sqlite3.Connection
) -> Dict[str, Any]:
    """Strict validation of the generated workbook and dataset."""
    cursor = conn.cursor()
    validation_report = {
        "output_file": str(xlsx_path),
        "total_rows": len(items),
        "breakdown": {},
        "already_answered_count": 0,
        "missing_qids_in_staging": 0,
        "duplicate_qids": 0,
        "missing_response_models": 0,
        "empty_sentence_count": 0,
        "validation_errors": []
    }

    # 1. Counts and breakdown
    for it in items:
        m = it["response_model"]
        validation_report["breakdown"][m] = validation_report["breakdown"].get(m, 0) + 1

    # 2. Duplicate QIDs
    qids = [it["question_id"] for it in items]
    unique_qids = set(qids)
    validation_report["duplicate_qids"] = len(qids) - len(unique_qids)

    # 3. Check against staging answered questions
    cursor.execute("""
        SELECT DISTINCT question_id FROM staging_gaps WHERE correct_answer IS NOT NULL
        UNION
        SELECT DISTINCT question_id FROM staging_options WHERE is_correct IS NOT NULL;
    """)
    answered_qids = set(r[0] for r in cursor.fetchall())
    overlap = unique_qids.intersection(answered_qids)
    validation_report["already_answered_count"] = len(overlap)
    if overlap:
        validation_report["validation_errors"].append(f"Found {len(overlap)} already-answered questions in workbook!")

    # 4. Check all QIDs exist in staging
    cursor.execute("SELECT question_id FROM staging_questions;")
    all_staging_qids = set(r[0] for r in cursor.fetchall())
    missing_in_staging = unique_qids - all_staging_qids
    validation_report["missing_qids_in_staging"] = len(missing_in_staging)
    if missing_in_staging:
        validation_report["validation_errors"].append(f"{len(missing_in_staging)} QIDs do not exist in staging_questions!")

    # 5. Missing response models or empty sentences
    for it in items:
        if not it["response_model"]:
            validation_report["missing_response_models"] += 1
        if not it["sentence"]:
            validation_report["empty_sentence_count"] += 1

    # 6. Verify written XLSX file
    wb = openpyxl.load_workbook(xlsx_path, data_only=False)
    if "Gemini_Enrichment" not in wb.sheetnames or "README" not in wb.sheetnames:
        validation_report["validation_errors"].append("Missing required sheets in generated XLSX")

    ws = wb["Gemini_Enrichment"]
    file_rows = ws.max_row - 2  # minus row 1 (title) and row 2 (headers)
    if file_rows != len(items):
        validation_report["validation_errors"].append(f"XLSX row count {file_rows} != items count {len(items)}")

    return validation_report


def main():
    parser = argparse.ArgumentParser(description="Generate full Gemini enrichment workbook for 5,614 unresolved questions.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite staging DB")
    parser.add_argument("--local-out", type=Path, default=LOCAL_OUTPUT, help="Path for project local XLSX")
    parser.add_argument("--desktop-out", type=Path, default=DESKTOP_OUTPUT, help="Path for Desktop XLSX")
    args = parser.parse_args()

    conn = sqlite3.connect(str(args.db))
    items = fetch_unresolved_questions(conn)

    assert len(items) == 5614, f"Expected exactly 5,614 questions, found {len(items)}"

    # Generate both workbooks
    create_enrichment_workbook(items, args.local_out)
    create_enrichment_workbook(items, args.desktop_out)

    # Validate
    report = validate_enrichment_workbook(items, args.desktop_out, conn)
    conn.close()

    print("\n" + "=" * 60)
    print("ENRICHMENT WORKBOOK GENERATION REPORT")
    print("=" * 60)
    print(f"  Output path (Desktop): {report['output_file']}")
    print(f"  Output path (Project): {args.local_out}")
    print(f"  Total rows: {report['total_rows']}")
    print("  Breakdown by response_model:")
    for m, c in report["breakdown"].items():
        print(f"    - {m}: {c}")
    print(f"  Already-answered questions included: {report['already_answered_count']}")
    print(f"  Duplicate QIDs: {report['duplicate_qids']}")
    print(f"  Missing QIDs in staging: {report['missing_qids_in_staging']}")
    print(f"  Missing response_model: {report['missing_response_models']}")
    print(f"  Empty sentences: {report['empty_sentence_count']}")
    print(f"  Validation errors: {len(report['validation_errors'])}")
    print("=" * 60)

    assert len(report["validation_errors"]) == 0, f"Validation failed: {report['validation_errors']}"
    assert report["breakdown"] == {"gap": 3522, "single_choice": 1927, "multiple_choice": 165}
    print("ALL ENRICHMENT WORKBOOK ASSERTIONS PASSED!\n")


if __name__ == "__main__":
    main()
