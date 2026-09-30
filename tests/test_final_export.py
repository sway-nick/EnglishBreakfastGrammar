import unittest
from pathlib import Path
import sqlite3
import json
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from staging.validate_staging_corpus import (
    run_full_staging_validation,
    DEFAULT_DB,
    DEFAULT_CHECKPOINT,
)
from export.export_enriched_corpus import (
    LOCAL_CMS_XLSX,
    DESKTOP_CMS_XLSX,
    LOCAL_UNIVERSAL_JSON,
    DESKTOP_UNIVERSAL_JSON,
)
from validators.cms_validator import validate_excel


class TestFinalExport(unittest.TestCase):
    def test_staging_validation(self):
        self.assertTrue(DEFAULT_DB.exists(), f"Staging DB not found at {DEFAULT_DB}")
        report = run_full_staging_validation(DEFAULT_DB, DEFAULT_CHECKPOINT)

        self.assertEqual(report["total_lessons"], 225)
        self.assertEqual(report["total_exercises"], 638)
        self.assertEqual(report["total_questions"], 5796)
        self.assertEqual(report["total_gaps"], 4733)
        self.assertEqual(report["total_options"], 13052)
        self.assertEqual(report["corrected_answer_coverage"], "100.00%")
        self.assertEqual(report["unanswered_questions"], 0)
        self.assertEqual(report["unanswered_gaps"], 0)
        self.assertEqual(report["unanswered_options"], 0)
        self.assertEqual(len(report["single_choice_violations"]), 0)
        self.assertEqual(len(report["multiple_choice_violations"]), 0)
        self.assertEqual(len(report["gap_violations"]), 0)
        self.assertEqual(len(report["referential_integrity_errors"]), 0)
        self.assertEqual(len(report["suspicious_answers"]), 0)
        self.assertEqual(len(report["checkpoint_discrepancies"]), 0)
        self.assertEqual(len(report["validation_errors"]), 0)

    def test_exported_files_exist_and_complete(self):
        self.assertTrue(LOCAL_CMS_XLSX.exists(), f"Local CMS Excel missing: {LOCAL_CMS_XLSX}")
        self.assertTrue(DESKTOP_CMS_XLSX.exists(), f"Desktop CMS Excel missing: {DESKTOP_CMS_XLSX}")
        self.assertTrue(LOCAL_UNIVERSAL_JSON.exists(), f"Local Universal JSON missing: {LOCAL_UNIVERSAL_JSON}")
        self.assertTrue(DESKTOP_UNIVERSAL_JSON.exists(), f"Desktop Universal JSON missing: {DESKTOP_UNIVERSAL_JSON}")

        self.assertGreater(LOCAL_CMS_XLSX.stat().st_size, 500000)
        self.assertGreater(LOCAL_UNIVERSAL_JSON.stat().st_size, 1000000)

        with open(LOCAL_UNIVERSAL_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["total_lessons"], 225)
        self.assertEqual(data["total_exercises"], 638)
        self.assertEqual(data["total_questions"], 5796)
        self.assertEqual(data["total_gaps"], 4733)
        self.assertEqual(data["total_options"], 13052)
        self.assertEqual(len(data["lessons"]), 225)

    def test_cms_validator_passes(self):
        code = validate_excel(str(LOCAL_CMS_XLSX))
        self.assertEqual(code, 0, "CMS validator returned non-zero code for enriched workbook")


if __name__ == "__main__":
    unittest.main()
