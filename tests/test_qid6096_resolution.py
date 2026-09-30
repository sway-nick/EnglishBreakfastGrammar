"""
test_qid6096_resolution.py
Verifies the successful resolution, validation, and isolation of QID 6096 (TASK-013H).
"""

import sqlite3
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPT_DB_PATH = REPO_ROOT / "data" / "adaptation.db"


class TestQID6096Resolution(unittest.TestCase):

    def test_qid6096_database_record(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        q = conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = 6096").fetchone()
        self.assertIsNotNone(q)
        self.assertEqual(q["adaptation_status"], "VALIDATED")
        self.assertEqual(q["review_required"], 0)
        self.assertEqual(q["adapted_text"], "She completed {{gap_1}}.")
        self.assertEqual(q["similarity_score"], 0.0)

        # Gaps
        g = conn.execute("SELECT * FROM adapted_gaps WHERE adapted_question_id = ?", (q["adapted_question_id"],)).fetchone()
        self.assertIsNotNone(g)
        self.assertEqual(g["adapted_correct_answer"], "the exam very quickly")
        self.assertEqual(g["adapted_accepted_answers"], '["the exam very quickly"]')

        # Exercise status
        ex = conn.execute("SELECT * FROM adapted_exercises WHERE adapted_exercise_id = 'adapt_quiz-712'").fetchone()
        self.assertEqual(ex["adaptation_status"], "VALIDATED")
        self.assertEqual(ex["review_required"], 0)

        # Database invariant counts
        counts = dict(conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
        self.assertEqual(counts.get("VALIDATED"), 561)
        self.assertEqual(counts.get("REJECTED"), 14)
        self.assertEqual(counts.get("PENDING"), 5221)
        self.assertEqual(sum(counts.values()), 5796)

        conn.close()


if __name__ == "__main__":
    unittest.main()
