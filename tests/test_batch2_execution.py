"""
test_batch2_execution.py
Unit and regression test verifying Batch 2 execution integrity (TASK-014).
"""

import sqlite3
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPT_DB_PATH = REPO_ROOT / "data" / "adaptation.db"


class TestBatch2Execution(unittest.TestCase):

    def test_database_counts_and_invariant(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        counts = dict(conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
        self.assertEqual(counts.get("VALIDATED"), 889)
        self.assertEqual(counts.get("REJECTED"), 36)
        self.assertEqual(counts.get("PENDING"), 4871)
        self.assertEqual(sum(counts.values()), 5796)

        # Verify Batch 2 run record in adaptation_runs
        run_rec = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_2_a1_350'").fetchone()
        self.assertIsNotNone(run_rec)
        self.assertEqual(run_rec["status"], "completed")
        self.assertEqual(run_rec["generated_count"], 350)
        self.assertEqual(run_rec["validated_count"], 328)
        self.assertEqual(run_rec["rejected_count"], 22)

        # Integrity checks
        fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(len(fk_errors), 0)
        integrity = conn.execute("PRAGMA integrity_check").fetchall()
        self.assertEqual(integrity[0][0], "ok")

        conn.close()


if __name__ == "__main__":
    unittest.main()
