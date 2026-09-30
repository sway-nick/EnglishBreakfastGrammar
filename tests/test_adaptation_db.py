import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline.adaptation.adaptation_db import (
    DEFAULT_SCHEMA_PATH,
    get_connection,
    get_status,
    init_db,
    populate_queue,
    reset_queue,
    verify_integrity,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestAdaptationDB(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.adapt_db_path = self.temp_path / "adaptation.db"
        self.staging_db_path = self.temp_path / "staging.db"

        # Initialize mock staging database
        self._init_mock_staging()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _init_mock_staging(self):
        conn = sqlite3.connect(str(self.staging_db_path))
        conn.executescript(
            """
            CREATE TABLE staging_lessons (
                lesson_id TEXT PRIMARY KEY,
                title TEXT,
                level TEXT,
                topic TEXT,
                description TEXT
            );
            CREATE TABLE staging_exercises (
                exercise_id TEXT PRIMARY KEY,
                lesson_id TEXT,
                exercise_order INTEGER,
                page INTEGER,
                title TEXT,
                instruction TEXT,
                example_source TEXT,
                example_target TEXT
            );
            CREATE TABLE staging_questions (
                question_id TEXT PRIMARY KEY,
                exercise_id TEXT,
                lesson_id TEXT,
                question_order INTEGER,
                response_model TEXT,
                content TEXT,
                explanation TEXT,
                difficulty TEXT
            );
            CREATE TABLE staging_gaps (
                gap_id TEXT PRIMARY KEY,
                question_id TEXT,
                gap_order INTEGER,
                input_control TEXT,
                correct_answer TEXT,
                accepted_answers TEXT,
                case_sensitive INTEGER
            );
            CREATE TABLE staging_options (
                option_id TEXT PRIMARY KEY,
                question_id TEXT,
                gap_id TEXT,
                option_order INTEGER,
                text TEXT,
                value TEXT,
                is_correct INTEGER
            );

            -- Sample data: 2 lessons (A1 and B2)
            INSERT INTO staging_lessons VALUES
                ('L1', 'Present Simple', 'A1', 'Grammar', 'Basics of present simple'),
                ('L2', 'Conditionals', 'B2', 'Grammar', 'Third conditional');

            INSERT INTO staging_exercises VALUES
                ('E1', 'L1', 1, 1, 'Ex 1', 'Fill in the blanks', NULL, NULL),
                ('E2', 'L2', 1, 1, 'Ex 2', 'Choose correct option', NULL, NULL);

            INSERT INTO staging_questions VALUES
                ('Q1', 'E1', 'L1', 1, 'gap', 'He {{gap_1}} to school.', 'Third person -s', 'easy'),
                ('Q2', 'E2', 'L2', 1, 'single_choice', 'If I had known, I _____ called.', 'Third conditional', 'hard');

            INSERT INTO staging_gaps VALUES
                ('G1', 'Q1', 1, 'text', 'goes', '["goes", "Goes"]', 0);

            INSERT INTO staging_options VALUES
                ('O1', 'Q2', NULL, 1, 'would have', 'would have', 1),
                ('O2', 'Q2', NULL, 2, 'will have', 'will have', 0),
                ('O3', 'Q2', NULL, 3, 'had', 'had', 0);
            """
        )
        conn.commit()
        conn.close()

    def test_init_db(self):
        """Test database initialization and table/index creation."""
        result = init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        self.assertTrue(result)
        self.assertTrue(self.adapt_db_path.exists())

        conn = get_connection(self.adapt_db_path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for expected in ["adaptation_runs", "adapted_lessons", "adapted_exercises", "adapted_questions", "adapted_gaps", "adapted_options"]:
            self.assertIn(expected, tables)
        conn.close()

    def test_foreign_key_enforcement(self):
        """Test that foreign key constraints are strictly enforced."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        conn = get_connection(self.adapt_db_path)

        # Attempt to insert question without parent exercise/lesson
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO adapted_questions (
                    adapted_question_id, source_question_id, adapted_exercise_id, adapted_lesson_id,
                    question_order, response_model, source_text, adaptation_status
                ) VALUES ('Q_ORPHAN', 'Q_SRC', 'E_NONEXISTENT', 'L_NONEXISTENT', 1, 'gap', 'text', 'PENDING')
                """
            )
        conn.close()

    def test_populate_queue_all(self):
        """Test populating all items from staging."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        stats = populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
            run_id="test_run_1",
            model_name="mock_model",
        )

        self.assertEqual(stats["lessons_inserted"], 2)
        self.assertEqual(stats["exercises_inserted"], 2)
        self.assertEqual(stats["questions_inserted"], 2)
        self.assertEqual(stats["gaps_inserted"], 1)
        self.assertEqual(stats["options_inserted"], 3)

        status = get_status(self.adapt_db_path)
        self.assertEqual(status["table_counts"]["adapted_lessons"], 2)
        self.assertEqual(status["table_counts"]["adapted_questions"], 2)
        self.assertEqual(status["question_statuses"]["PENDING"], 2)
        self.assertEqual(status["questions_by_level"]["A1"], 1)
        self.assertEqual(status["questions_by_level"]["B2"], 1)

    def test_populate_queue_idempotency(self):
        """Test that re-running populate does not duplicate or overwrite existing entries."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)

        # Pass 1
        stats1 = populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
        )
        self.assertEqual(stats1["questions_inserted"], 2)
        self.assertEqual(stats1["questions_skipped"], 0)

        # Modify one question to GENERATED
        conn = get_connection(self.adapt_db_path)
        conn.execute(
            """
            UPDATE adapted_questions
            SET adapted_text = 'He walks to school.', adaptation_status = 'GENERATED'
            WHERE adapted_question_id = 'adapt_Q1'
            """
        )
        conn.commit()
        conn.close()

        # Pass 2
        stats2 = populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
        )
        self.assertEqual(stats2["questions_inserted"], 0)
        self.assertEqual(stats2["questions_skipped"], 2)

        # Ensure modified question was not overwritten
        conn = get_connection(self.adapt_db_path)
        row = conn.execute("SELECT adapted_text, adaptation_status FROM adapted_questions WHERE adapted_question_id = 'adapt_Q1'").fetchone()
        self.assertEqual(row["adapted_text"], "He walks to school.")
        self.assertEqual(row["adaptation_status"], "GENERATED")
        conn.close()

    def test_populate_queue_level_filter(self):
        """Test populating only a specific CEFR level."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        stats = populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
            target_level="A1",
        )
        self.assertEqual(stats["lessons_inserted"], 1)
        self.assertEqual(stats["questions_inserted"], 1)
        self.assertEqual(stats["gaps_inserted"], 1)
        self.assertEqual(stats["options_inserted"], 0)

    def test_verify_integrity(self):
        """Test integrity verification passes on valid state and fails on corrupt state."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
        )

        v = verify_integrity(self.adapt_db_path, self.staging_db_path)
        self.assertTrue(v["is_valid"])
        self.assertEqual(v["foreign_key_violations"], 0)
        self.assertEqual(v["orphan_questions"], 0)
        self.assertEqual(v["unmatched_source_questions"], 0)

    def test_reset_queue(self):
        """Test resetting adapted items back to PENDING."""
        init_db(self.adapt_db_path, DEFAULT_SCHEMA_PATH)
        populate_queue(
            staging_db_path=self.staging_db_path,
            adaptation_db_path=self.adapt_db_path,
        )

        conn = get_connection(self.adapt_db_path)
        conn.execute(
            """
            UPDATE adapted_questions
            SET adapted_text = 'Sample rewrite', adaptation_status = 'VALIDATED', similarity_score = 0.25
            WHERE adapted_question_id = 'adapt_Q1'
            """
        )
        conn.commit()
        conn.close()

        status_before = get_status(self.adapt_db_path)
        self.assertEqual(status_before["question_statuses"].get("VALIDATED"), 1)

        # Reset
        count = reset_queue(self.adapt_db_path, reset_all=True)
        self.assertEqual(count, 2)

        status_after = get_status(self.adapt_db_path)
        self.assertEqual(status_after["question_statuses"].get("PENDING"), 2)
        self.assertNotIn("VALIDATED", status_after["question_statuses"])


if __name__ == "__main__":
    unittest.main()
