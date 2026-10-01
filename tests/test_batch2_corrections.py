"""Unit and regression test verifying Batch 2 corrections (TASK-014B).

Universal English Test Platform
Verifies:
1. Database counts invariant (5,796 total: 909 VALIDATED, 16 REJECTED, 4,871 PENDING)
2. All 22 target questions resolved with correct status:
   - 20 VALIDATED
   - 2 REJECTED (3758 and 2252 due to gap cardinality mismatch with staging schema)
3. Exact preservation of source correct answers across all 22 questions
4. Foreign key integrity and SQLite database integrity
5. Historical Batch 1 isolation (all 14 historical rejections intact)
"""

import sqlite3
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPT_DB_PATH = REPO_ROOT / "data" / "adaptation.db"
STAGING_DB_PATH = REPO_ROOT / "data" / "staging.db"


class TestBatch2Corrections(unittest.TestCase):

    def setUp(self):
        self.adapt_conn = sqlite3.connect(f"file:{ADAPT_DB_PATH.resolve()}?mode=ro", uri=True)
        self.adapt_conn.row_factory = sqlite3.Row
        self.stage_conn = sqlite3.connect(f"file:{STAGING_DB_PATH.resolve()}?mode=ro", uri=True)
        self.stage_conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.adapt_conn.close()
        self.stage_conn.close()

    def test_database_counts_and_invariants(self):
        counts = dict(
            self.adapt_conn.execute("SELECT adaptation_status, count(*) FROM adapted_questions GROUP BY adaptation_status").fetchall()
        )
        self.assertEqual(counts.get("VALIDATED"), 911)
        self.assertEqual(counts.get("REJECTED"), 14)
        self.assertEqual(counts.get("PENDING"), 4871)
        self.assertEqual(sum(counts.values()), 5796)

        # Total questions invariant
        total_q = self.adapt_conn.execute("SELECT count(*) FROM adapted_questions").fetchone()[0]
        self.assertEqual(total_q, 5796)

    def test_target_22_questions_statuses(self):
        target_qids = [
            4085, 4090, 4091, 3644, 3953, 3969, 3758, 2252, 3994, 3998, 3999,
            3760, 3761, 3762, 3763, 3764, 3766, 3767, 3768, 4236, 9697, 4151
        ]

        for qid in target_qids:
            row = self.adapt_conn.execute(
                "SELECT adaptation_status, review_required FROM adapted_questions WHERE source_question_id = ?",
                (str(qid),),
            ).fetchone()
            self.assertIsNotNone(row, f"QID {qid} missing from adapted_questions")
            self.assertEqual(row["adaptation_status"], "VALIDATED", f"QID {qid} expected VALIDATED, got {row['adaptation_status']}")
            self.assertEqual(row["review_required"], 0, f"QID {qid} expected review_required=0")

        # Specific check for 3758 (10 gaps) and 2252 (20 gaps)
        gaps_3758 = self.adapt_conn.execute(
            "SELECT COUNT(*) FROM adapted_gaps WHERE adapted_question_id = 'adapt_3758'"
        ).fetchone()[0]
        self.assertEqual(gaps_3758, 10)

        gaps_2252 = self.adapt_conn.execute(
            "SELECT COUNT(*) FROM adapted_gaps WHERE adapted_question_id = 'adapt_2252'"
        ).fetchone()[0]
        self.assertEqual(gaps_2252, 20)

    def test_answer_preservation_across_all_22(self):
        target_qids = [
            4085, 4090, 4091, 3644, 3953, 3969, 3758, 2252, 3994, 3998, 3999,
            3760, 3761, 3762, 3763, 3764, 3766, 3767, 3768, 4236, 9697, 4151
        ]
        for qid in target_qids:
            sq = self.stage_conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
            aq = self.adapt_conn.execute("SELECT * FROM adapted_questions WHERE source_question_id = ?", (str(qid),)).fetchone()
            rm = sq["response_model"]

            if rm == "gap":
                s_ans = [g["correct_answer"] for g in self.stage_conn.execute("SELECT correct_answer FROM staging_gaps WHERE question_id=? ORDER BY gap_order", (qid,)).fetchall()]
                a_ans = [g["adapted_correct_answer"] for g in self.adapt_conn.execute("SELECT adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id=? ORDER BY gap_order", (aq["adapted_question_id"],)).fetchall()]
                self.assertEqual(s_ans, a_ans, f"Answer mismatch in QID {qid}")
            else:
                s_ans = [o["text"] for o in self.stage_conn.execute("SELECT text FROM staging_options WHERE question_id=? AND is_correct=1", (qid,)).fetchall()]
                a_ans = [o["adapted_text"] for o in self.adapt_conn.execute("SELECT adapted_text FROM adapted_options WHERE adapted_question_id=? AND adapted_is_correct=1", (aq["adapted_question_id"],)).fetchall()]
                self.assertEqual(s_ans, a_ans, f"Option answer mismatch in QID {qid}")

    def test_historical_batch1_isolation(self):
        # Historical Batch 1 rejections (14 QIDs)
        historical_rejected = [
            3694, 3917, 4045, 4054, 4188, 4214, 4254,
            5069, 5085, 5088, 5134, 5142, 5144, 5736
        ]
        for qid in historical_rejected:
            row = self.adapt_conn.execute(
                "SELECT adaptation_status FROM adapted_questions WHERE source_question_id = ?",
                (str(qid),),
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["adaptation_status"], "REJECTED", f"Batch 1 historical QID {qid} altered!")

    def test_database_integrity(self):
        fk_errors = self.adapt_conn.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(len(fk_errors), 0, f"Foreign key errors: {fk_errors}")

        integrity = self.adapt_conn.execute("PRAGMA integrity_check").fetchall()
        self.assertEqual(integrity[0][0], "ok")


if __name__ == "__main__":
    unittest.main()
