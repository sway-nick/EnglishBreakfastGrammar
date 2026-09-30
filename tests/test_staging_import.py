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
    verify_staging_database,
    DEFAULT_SOURCE,
    DEFAULT_DB,
)


class TestStagingImport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_staging.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_initialization(self):
        conn = init_database(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cursor.fetchall()]
        expected_tables = [
            "staging_exercises",
            "staging_gaps",
            "staging_import_runs",
            "staging_lessons",
            "staging_options",
            "staging_questions",
        ]
        for tbl in expected_tables:
            self.assertIn(tbl, tables)
        conn.close()

    def test_foreign_key_enforcement(self):
        conn = init_database(self.test_db_path)
        cursor = conn.cursor()
        # Inserting an exercise with non-existent lesson_id must raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO staging_exercises (
                    exercise_id, lesson_id, page, exercise_order, status
                ) VALUES ('quiz-fake', 'non_existent_lesson', 1, 1, 'staging');
            """)
        conn.close()

    def test_full_corpus_staging_import(self):
        self.assertTrue(DEFAULT_SOURCE.exists(), f"Preliminary JSON not found at {DEFAULT_SOURCE}")
        report = import_corpus_to_staging(DEFAULT_SOURCE, self.test_db_path)

        self.assertEqual(report["total_topics"], 225)
        self.assertEqual(report["total_exercises"], 638)
        self.assertEqual(report["total_questions"], 5796)
        self.assertEqual(report["total_gaps"], 4733)
        self.assertEqual(report["total_options"], 13052)
        self.assertEqual(report["total_orphans"], 0)
        self.assertEqual(report["total_duplicates"], 0)
        self.assertEqual(report["response_models"]["gap"], 3674)
        self.assertEqual(report["response_models"]["single_choice"], 1957)
        self.assertEqual(report["response_models"]["multiple_choice"], 165)
        self.assertEqual(report["unresolved_answers_count"], 17785)
        self.assertEqual(report["non_staging_lessons"], 0)
        self.assertEqual(report["non_staging_questions"], 0)

    def test_production_staging_db_verified(self):
        if DEFAULT_DB.exists():
            report = verify_staging_database(DEFAULT_DB)
            self.assertEqual(report["total_topics"], 225)
            self.assertEqual(report["total_exercises"], 638)
            self.assertEqual(report["total_questions"], 5796)
            self.assertEqual(report["total_gaps"], 4733)
            self.assertEqual(report["total_options"], 13052)
            self.assertEqual(report["total_orphans"], 0)
            self.assertEqual(report["total_duplicates"], 0)


if __name__ == "__main__":
    unittest.main()
