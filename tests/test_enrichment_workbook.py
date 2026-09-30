import unittest
from pathlib import Path
import tempfile
import sqlite3
import openpyxl
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from gemini.enrichment_workbook_builder import (
    fetch_unresolved_questions,
    create_enrichment_workbook,
    validate_enrichment_workbook,
    DEFAULT_DB,
    DESKTOP_OUTPUT,
    LOCAL_OUTPUT,
)


class TestEnrichmentWorkbook(unittest.TestCase):
    def test_fetch_unresolved_questions(self):
        self.assertTrue(DEFAULT_DB.exists(), f"Staging DB not found at {DEFAULT_DB}")
        conn = sqlite3.connect(str(DEFAULT_DB))
        items = fetch_unresolved_questions(conn)
        conn.close()

        self.assertEqual(len(items), 5614)

        models = {}
        for it in items:
            m = it["response_model"]
            models[m] = models.get(m, 0) + 1

        self.assertEqual(models, {"gap": 3522, "single_choice": 1927, "multiple_choice": 165})

    def test_generated_workbooks_exist_and_valid(self):
        self.assertTrue(LOCAL_OUTPUT.exists(), f"Project copy not found at {LOCAL_OUTPUT}")
        self.assertTrue(DESKTOP_OUTPUT.exists(), f"Desktop copy not found at {DESKTOP_OUTPUT}")

        conn = sqlite3.connect(str(DEFAULT_DB))
        items = fetch_unresolved_questions(conn)
        report = validate_enrichment_workbook(items, LOCAL_OUTPUT, conn)
        conn.close()

        self.assertEqual(report["total_rows"], 5614)
        self.assertEqual(report["already_answered_count"], 0)
        self.assertEqual(report["duplicate_qids"], 0)
        self.assertEqual(report["missing_qids_in_staging"], 0)
        self.assertEqual(report["missing_response_models"], 0)
        self.assertEqual(report["empty_sentence_count"], 0)
        self.assertEqual(len(report["validation_errors"]), 0)


if __name__ == "__main__":
    unittest.main()
