"""
test_batch4_execution.py
Unit and regression test verifying Batch 4 execution integrity (TASK-016).
"""

import sqlite3
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPT_DB_PATH = REPO_ROOT / "data" / "adaptation.db"


class TestBatch4Execution(unittest.TestCase):

    def test_database_counts_and_invariant(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        counts = dict(conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall())
        self.assertEqual(counts.get("VALIDATED"), 2208)
        self.assertEqual(counts.get("REJECTED"), 62)
        self.assertEqual(counts.get("PENDING"), 3526)
        self.assertEqual(sum(counts.values()), 5796)

        # Verify Batch 4 run record in adaptation_runs
        run_rec = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_4_a1_1000'").fetchone()
        self.assertIsNotNone(run_rec)
        self.assertEqual(run_rec["status"], "completed")
        self.assertEqual(run_rec["total_items"], 1000)
        self.assertEqual(run_rec["generated_count"], 995)
        self.assertEqual(run_rec["validated_count"], 947)
        self.assertEqual(run_rec["rejected_count"], 48)

        # Verify previous batch run records remain intact
        b3_run = conn.execute("SELECT * FROM adaptation_runs WHERE run_id = 'prod_batch_3_a1_350'").fetchone()
        self.assertIsNotNone(b3_run)
        self.assertEqual(b3_run["status"], "completed")

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

    def test_historical_isolation(self):
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

        # QID 6096 must still be VALIDATED
        q6096 = conn.execute(
            "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = '6096'"
        ).fetchone()
        self.assertEqual(q6096["adaptation_status"], "VALIDATED")

        # QIDs 5013-5017 must remain strictly PENDING
        for qid in ["5013", "5014", "5015", "5016", "5017"]:
            row = conn.execute("SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
            self.assertEqual(row["adaptation_status"], "PENDING", f"QID {qid} must remain PENDING")

        conn.close()

    def test_task016b_corrections(self):
        conn = sqlite3.connect(f"file:{ADAPT_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        # 7 corrected QIDs must now be VALIDATED
        corrected_qids = ["2861", "3249", "3253", "5008", "5010", "5011", "5012"]
        for qid in corrected_qids:
            row = conn.execute("SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?", (qid,)).fetchone()
            self.assertEqual(row["adaptation_status"], "VALIDATED", f"QID {qid} should be VALIDATED")

        conn.close()


if __name__ == "__main__":
    unittest.main()
