import unittest
from pathlib import Path
import sqlite3
import tempfile

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "adaptation_schema.sql"


class TestAdaptationSchema(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_adaptation.db"
        self.assertTrue(SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_creation_and_integrity(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON;")

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cursor.fetchall()]
        expected_tables = [
            "adaptation_runs",
            "adapted_exercises",
            "adapted_gaps",
            "adapted_lessons",
            "adapted_options",
            "adapted_questions",
        ]
        for t in expected_tables:
            self.assertIn(t, tables, f"Expected table '{t}' was not created")

        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_autoindex%';")
        indexes = [r[0] for r in cursor.fetchall()]
        expected_indexes = [
            "idx_adapted_lessons_source",
            "idx_adapted_exercises_lesson",
            "idx_adapted_exercises_source",
            "idx_adapted_questions_exercise",
            "idx_adapted_questions_source",
            "idx_adapted_questions_status",
            "idx_adapted_gaps_question",
            "idx_adapted_gaps_source",
            "idx_adapted_options_question",
            "idx_adapted_options_gap",
            "idx_adapted_options_source",
        ]
        for idx in expected_indexes:
            self.assertIn(idx, indexes, f"Expected index '{idx}' was not created")

        # Insert sample record hierarchy
        cursor.execute("""
            INSERT INTO adapted_lessons (adapted_lesson_id, source_lesson_id, title, level, adaptation_status)
            VALUES ('L_ADAPT_001', 'L_SRC_001', 'Present Simple Forms', 'A1', 'PENDING');
        """)

        cursor.execute("""
            INSERT INTO adapted_exercises (adapted_exercise_id, source_exercise_id, adapted_lesson_id, exercise_order)
            VALUES ('E_ADAPT_001', 'E_SRC_001', 'L_ADAPT_001', 1);
        """)

        cursor.execute("""
            INSERT INTO adapted_questions (
                adapted_question_id, source_question_id, adapted_exercise_id, adapted_lesson_id,
                question_order, response_model, source_text, adapted_text, adaptation_status
            )
            VALUES (
                'Q_ADAPT_001', 'Q_SRC_001', 'E_ADAPT_001', 'L_ADAPT_001',
                1, 'gap', '1 We bought some cheese. {{gap_1}} was good.',
                '1 We purchased a fresh cake. {{gap_1}} was delicious.', 'GENERATED'
            );
        """)

        cursor.execute("""
            INSERT INTO adapted_gaps (
                adapted_gap_id, source_gap_id, adapted_question_id, gap_order, input_control,
                source_correct_answer, adapted_correct_answer
            )
            VALUES ('G_ADAPT_001', 'G_SRC_001', 'Q_ADAPT_001', 1, 'select', 'The', 'It');
        """)

        cursor.execute("""
            INSERT INTO adapted_options (
                adapted_option_id, source_option_id, adapted_question_id, adapted_gap_id,
                option_order, source_text, adapted_text, source_is_correct, adapted_is_correct
            )
            VALUES ('O_ADAPT_001', 'O_SRC_001', 'Q_ADAPT_001', 'G_ADAPT_001', 1, 'The', 'It', 1, 1);
        """)

        conn.commit()

        # Query back
        cursor.execute("SELECT adapted_text, adaptation_status FROM adapted_questions WHERE adapted_question_id='Q_ADAPT_001';")
        row = cursor.fetchone()
        self.assertEqual(row, ('1 We purchased a fresh cake. {{gap_1}} was delicious.', 'GENERATED'))

        conn.close()


if __name__ == "__main__":
    unittest.main()
