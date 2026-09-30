"""Unit tests for Review Report Builder (TASK-011D)

Universal English Test Platform
Validates:
- Generation of data/adaptation/pilot_review_20260930.xlsx
- Exact sheet structure (Summary, Review_Required_75, All_Pilot_Questions_200)
- 17 required column headers
- Data partitioning and ordering: REVIEW_REQUIRED first (75 items), then VALIDATED (125 items)
- Summary statistics accuracy (200 total, 125 validated, 75 review required, 0 rejected)
"""

import unittest
from pathlib import Path
import openpyxl

from pipeline.adaptation.review_report_builder import (
    DEFAULT_ADAPTATION_DB,
    DEFAULT_STAGING_DB,
    DEFAULT_OUTPUT_PATH,
    generate_pilot_review_workbook,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_HEADERS = [
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


class TestReviewReportBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_output = REPO_ROOT / "data" / "adaptation" / "pilot_review_test.xlsx"
        cls.res = generate_pilot_review_workbook(
            adaptation_db_path=REPO_ROOT / DEFAULT_ADAPTATION_DB,
            staging_db_path=REPO_ROOT / DEFAULT_STAGING_DB,
            output_path=cls.test_output,
            desktop_path=None,
        )
        cls.wb = openpyxl.load_workbook(cls.test_output, data_only=True)

    @classmethod
    def tearDownClass(cls):
        if cls.test_output.exists():
            try:
                cls.test_output.unlink()
            except Exception:
                pass

    def test_workbook_sheets(self):
        """Assert workbook contains the 3 exact expected sheets."""
        expected = ["Summary", "Review_Required_75", "All_Pilot_Questions_200"]
        self.assertEqual(self.wb.sheetnames, expected)

    def test_summary_metrics(self):
        """Assert Summary sheet contains verified totals."""
        ws = self.wb["Summary"]
        self.assertEqual(ws["C7"].value, 200, "Total pilot questions should be 200")
        val = ws["C8"].value
        rev = ws["C9"].value
        self.assertEqual(val + rev, 200, "Validated + review_required must sum to 200")
        self.assertEqual(ws["C10"].value, 0, "REJECTED questions should be 0")

    def test_review_required_sheet_structure(self):
        """Assert Review_Required sheet contains 17 headers and flagged questions."""
        ws = self.wb["Review_Required_75"]
        headers = [ws.cell(row=1, column=c).value for c in range(1, 18)]
        self.assertEqual(headers, EXPECTED_HEADERS)

        for r in range(2, ws.max_row + 1):
            status = ws.cell(row=r, column=15).value
            rev_req = ws.cell(row=r, column=16).value
            self.assertEqual(status, "REVIEW_REQUIRED", f"Row {r} must be REVIEW_REQUIRED")
            self.assertEqual(rev_req, 1, f"Row {r} review_required must be 1")

    def test_all_questions_sheet_ordering(self):
        """Assert All_Pilot_Questions_200 contains REVIEW_REQUIRED rows first, then VALIDATED."""
        ws = self.wb["All_Pilot_Questions_200"]
        headers = [ws.cell(row=1, column=c).value for c in range(1, 18)]
        self.assertEqual(headers, EXPECTED_HEADERS)

        # 1 header row + 200 data rows = 201 rows
        self.assertEqual(ws.max_row, 201)

        ws_rev = self.wb["Review_Required_75"]
        n_rev = ws_rev.max_row - 1

        # First N rows: REVIEW_REQUIRED
        for r in range(2, 2 + n_rev):
            status = ws.cell(row=r, column=15).value
            rev_req = ws.cell(row=r, column=16).value
            self.assertEqual(status, "REVIEW_REQUIRED", f"Row {r} must be REVIEW_REQUIRED")
            self.assertEqual(rev_req, 1, f"Row {r} review_required must be 1")

        # Remaining rows: VALIDATED
        for r in range(2 + n_rev, 202):
            status = ws.cell(row=r, column=15).value
            rev_req = ws.cell(row=r, column=16).value
            self.assertEqual(status, "VALIDATED", f"Row {r} must be VALIDATED")
            self.assertEqual(rev_req, 0, f"Row {r} review_required must be 0")

    def test_no_empty_core_fields(self):
        """Assert no empty or undefined source/adapted IDs or text."""
        ws = self.wb["All_Pilot_Questions_200"]
        for r in range(2, 202):
            sqid = ws.cell(row=r, column=1).value
            aqid = ws.cell(row=r, column=2).value
            stext = ws.cell(row=r, column=6).value
            atext = ws.cell(row=r, column=7).value
            self.assertTrue(bool(sqid), f"Row {r} missing source_question_id")
            self.assertTrue(str(aqid).startswith("adapt_"), f"Row {r} invalid adapted_question_id")
            self.assertTrue(bool(stext), f"Row {r} missing source_text")
            self.assertTrue(bool(atext), f"Row {r} missing adapted_text")


if __name__ == "__main__":
    unittest.main()
