"""
test_batch3_execution.py
Unit and regression test verifying Batch 3 execution and targeted corrections integrity (TASK-015 & TASK-015B).
"""

import sqlite3
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPT_DB_PATH = REPO_ROOT / "data" / "adaptation.db"


class TestBatch3Execution(unittest.TestCase):

    def test_database_counts_and_invariant(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        counts = dict(conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
        self.assertEqual(counts.get("VALIDATED"), 1261)
        self.assertEqual(counts.get("REJECTED"), 14)
        self.assertEqual(counts.get("PENDING"), 4521)
        self.assertEqual(sum(counts.values()), 5796)

        # Verify Batch 3 run record in adaptation_runs
        run_rec = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_3_a1_350'").fetchone()
        self.assertIsNotNone(run_rec)
        self.assertEqual(run_rec["status"], "completed")
        self.assertEqual(run_rec["total_items"], 350)
        self.assertEqual(run_rec["generated_count"], 350)
        self.assertEqual(run_rec["validated_count"], 350)
        self.assertEqual(run_rec["rejected_count"], 0)

        # Verify previous batch run records remain intact
        b2_run = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_2_a1_350'").fetchone()
        self.assertIsNotNone(b2_run)
        self.assertEqual(b2_run["status"], "completed")

        b1_run = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_1_a1_350'").fetchone()
        self.assertIsNotNone(b1_run)
        self.assertEqual(b1_run["status"], "completed")

        # Integrity checks
        fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(len(fk_errors), 0)
        integrity = conn.execute("PRAGMA integrity_check").fetchall()
        self.assertEqual(integrity[0][0], "ok")

        conn.close()

    def test_historical_batch1_batch2_isolation(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        # All 14 historical Batch 1 rejections must remain REJECTED
        hist_14_qids = [
            "3694", "3917", "4254", "4214", "5736", "5134", "5142", "5144",
            "5069", "5085", "5088", "4188", "4045", "4054"
        ]
        for qid in hist_14_qids:
            row = conn.execute(
                "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?",
                (qid,),
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["adaptation_status"], "REJECTED", f"Historical QID {qid} must remain REJECTED")

        # Batch 2 corrected questions must still be VALIDATED
        b2_target_qids = [
            4085, 4090, 4091, 3644, 3953, 3969, 3758, 2252, 3994, 3998, 3999,
            3760, 3761, 3762, 3763, 3764, 3766, 3767, 3768, 4236, 9697, 4151
        ]
        for qid in b2_target_qids:
            row = conn.execute(
                "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?",
                (str(qid),),
            ).fetchone()
            self.assertEqual(row["adaptation_status"], "VALIDATED")

        # QID 6096 must still be VALIDATED
        q6096 = conn.execute(
            "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = '6096'"
        ).fetchone()
        self.assertEqual(q6096["adaptation_status"], "VALIDATED")

        # All 23 Batch 3 corrected questions must be VALIDATED
        b3_target_qids = [
            3626, 3628, 3632, 4755, 4758, 4002, 4009, 4026, 4030, 4012,
            3811, 3813, 3814, 3818, 3819, 5151, 5163, 2775, 2778, 2781,
            2791, 7086, 3336
        ]
        for qid in b3_target_qids:
            row = conn.execute(
                "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?",
                (str(qid),),
            ).fetchone()
            self.assertEqual(row["adaptation_status"], "VALIDATED", f"Batch 3 QID {qid} must be VALIDATED")

        conn.close()


if __name__ == "__main__":
    unittest.main()
