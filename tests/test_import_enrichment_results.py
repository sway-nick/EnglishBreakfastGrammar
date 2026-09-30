import unittest
from pathlib import Path
import tempfile
import sqlite3
import json
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from staging.staging_importer import (
    init_database,
    import_corpus_to_staging,
    DEFAULT_SOURCE,
)
from staging.merge_checkpoint import (
    merge_checkpoint_into_staging,
    DEFAULT_CHECKPOINT,
)
from staging.import_enrichment_results import (
    load_enrichment_results,
    import_enrichment_results,
    DEFAULT_RESULTS,
    FALLBACK_RESULTS,
)


class TestImportEnrichmentResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_file = DEFAULT_RESULTS if DEFAULT_RESULTS.exists() else FALLBACK_RESULTS

    def setUp(self):
        self.assertTrue(self.results_file.exists(), f"Results file not found at {self.results_file}")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_staging.db"
        # 1. Populate staging corpus
        import_corpus_to_staging(DEFAULT_SOURCE, self.test_db_path)
        # 2. Merge 182 checkpoint
        merge_checkpoint_into_staging(DEFAULT_CHECKPOINT, self.test_db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_enrichment_results(self):
        records = load_enrichment_results(self.results_file)
        self.assertEqual(len(records), 5614)
        
        # Verify first record
        first = records[0]
        self.assertIn("question_id", first)
        self.assertIn("response_model", first)
        self.assertIn("parsed_answer", first)

        # Verify known overrides
        r_12660 = next(r for r in records if r["question_id"] == "12660")
        self.assertEqual(r_12660["parsed_answer"], {"gap_1": "were always picking"})

        r_187 = next(r for r in records if r["question_id"] == "187")
        self.assertEqual(r_187["parsed_answer"], {"gap_1": "when"})

    def test_dry_run_leaves_database_untouched(self):
        report = import_enrichment_results(
            self.results_file,
            self.test_db_path,
            dry_run=True
        )
        self.assertEqual(report["workbook_questions"], 5614)
        self.assertEqual(report["matched_questions"], 5614)
        self.assertEqual(report["unmatched_questions"], 0)
        self.assertEqual(len(report["validation_errors"]), 0)
        self.assertEqual(report["remaining_unanswered_questions"], 0)

        # In dry run, DB must still have 5614 unanswered questions
        conn = sqlite3.connect(str(self.test_db_path))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NULL;")
        self.assertEqual(c.fetchone()[0], 4509)
        c.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NULL;")
        self.assertEqual(c.fetchone()[0], 12794)
        conn.close()

    def test_import_commit_full_verification(self):
        report = import_enrichment_results(
            self.results_file,
            self.test_db_path,
            dry_run=False
        )
        self.assertEqual(report["workbook_questions"], 5614)
        self.assertEqual(report["matched_questions"], 5614)
        self.assertEqual(report["unmatched_questions"], 0)
        self.assertEqual(report["single_choice_questions_answered"], 1927)
        self.assertEqual(report["multiple_choice_questions_answered"], 165)
        self.assertEqual(report["gap_questions_answered"], 3522)
        self.assertEqual(report["total_gaps_answered_in_batch"], 4509)
        self.assertEqual(report["total_options_updated_in_batch"], 12794)
        self.assertEqual(report["total_answered_questions"], 5796)
        self.assertEqual(report["remaining_unanswered_questions"], 0)
        self.assertEqual(report["remaining_unanswered_gaps"], 0)
        self.assertEqual(report["remaining_unanswered_options"], 0)
        self.assertEqual(len(report["validation_errors"]), 0)

        # Verify DB directly
        conn = sqlite3.connect(str(self.test_db_path))
        c = conn.cursor()

        # Check all questions answered
        c.execute("SELECT COUNT(*) FROM staging_questions;")
        self.assertEqual(c.fetchone()[0], 5796)

        c.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NULL;")
        self.assertEqual(c.fetchone()[0], 0)

        c.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NULL;")
        self.assertEqual(c.fetchone()[0], 0)

        # Verify single_choice has exactly 1 correct option
        c.execute("""
            SELECT q.question_id, COUNT(o.option_id) as corr_count
            FROM staging_questions q
            JOIN staging_options o ON q.question_id = o.question_id
            WHERE q.response_model = 'single_choice' AND o.is_correct = 1
            GROUP BY q.question_id
            HAVING corr_count != 1
        """)
        self.assertEqual(len(c.fetchall()), 0)

        # Verify multiple_choice has at least 1 correct option
        c.execute("""
            SELECT q.question_id, COUNT(o.option_id) as corr_count
            FROM staging_questions q
            JOIN staging_options o ON q.question_id = o.question_id
            WHERE q.response_model = 'multiple_choice' AND o.is_correct = 1
            GROUP BY q.question_id
            HAVING corr_count < 1
        """)
        self.assertEqual(len(c.fetchall()), 0)

        # Verify 182-question checkpoint question 2242 is untouched
        c.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id='2242' ORDER BY gap_order;")
        self.assertEqual(c.fetchall(), [(1, "Are"), (2, "am")])

        conn.close()


if __name__ == "__main__":
    unittest.main()
