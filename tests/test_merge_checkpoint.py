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
    load_checkpoint_data,
    merge_checkpoint_into_staging,
    DEFAULT_CHECKPOINT,
    DEFAULT_DB,
)


class TestMergeCheckpoint(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_staging.db"
        # Populate test database with full staging content
        import_corpus_to_staging(DEFAULT_SOURCE, self.test_db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_checkpoint_data(self):
        self.assertTrue(DEFAULT_CHECKPOINT.exists(), f"Checkpoint not found at {DEFAULT_CHECKPOINT}")
        records = load_checkpoint_data(DEFAULT_CHECKPOINT)
        self.assertEqual(len(records), 182)
        # Check first record structure
        first = records[0]
        self.assertEqual(first["question_id"], "2242")
        self.assertEqual(first["response_model"], "gap")
        self.assertIn("gap_1", first["parsed_answer"])

    def test_merge_checkpoint_dry_run(self):
        report = merge_checkpoint_into_staging(
            DEFAULT_CHECKPOINT,
            self.test_db_path,
            dry_run=True
        )
        self.assertEqual(report["checkpoint_questions"], 182)
        self.assertEqual(report["matched_questions"], 182)
        self.assertEqual(report["unmatched_questions"], 0)
        self.assertEqual(report["answered_gaps"], 224)
        self.assertEqual(report["answered_options"], 258)
        self.assertEqual(len(report["validation_errors"]), 0)

        # In dry run, DB must remain untouched (0 resolved gaps)
        conn = sqlite3.connect(str(self.test_db_path))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NOT NULL;")
        self.assertEqual(c.fetchone()[0], 0)
        conn.close()

    def test_merge_checkpoint_commit(self):
        report = merge_checkpoint_into_staging(
            DEFAULT_CHECKPOINT,
            self.test_db_path,
            dry_run=False
        )
        self.assertEqual(report["checkpoint_questions"], 182)
        self.assertEqual(report["matched_questions"], 182)
        self.assertEqual(report["unmatched_questions"], 0)
        self.assertEqual(report["answered_gaps"], 224)
        self.assertEqual(report["answered_options"], 258)
        self.assertEqual(report["remaining_unanswered_questions"], 5614)
        self.assertEqual(report["remaining_unanswered_gaps"], 4509)
        self.assertEqual(report["remaining_unanswered_options"], 12794)
        self.assertEqual(len(report["validation_errors"]), 0)

        # Verify DB updates
        conn = sqlite3.connect(str(self.test_db_path))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM staging_gaps WHERE correct_answer IS NOT NULL;")
        self.assertEqual(c.fetchone()[0], 224)

        c.execute("SELECT COUNT(*) FROM staging_options WHERE is_correct IS NOT NULL;")
        self.assertEqual(c.fetchone()[0], 258)

        # Check question 2242 specifically
        c.execute("SELECT gap_order, correct_answer FROM staging_gaps WHERE question_id='2242' ORDER BY gap_order;")
        gaps_2242 = c.fetchall()
        self.assertEqual(gaps_2242, [(1, "Are"), (2, "am")])

        conn.close()


if __name__ == "__main__":
    unittest.main()
