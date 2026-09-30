"""Unit tests for Semantic Reviewer (TASK-011G)

Universal English Test Platform
Validates:
- Execution of independent semantic review on 34 pilot questions (14 REVIEW_REQUIRED + 20 VALIDATED_CONTROL)
- Strict JSON structure and decision contract
- Decision rules: APPROVE requires all 4 checks to be True
- Persistence in separate SQLite table 'pilot_semantic_reviews' without modifying core adaptation tables
- Preservation of original adaptation records
"""

import json
from pathlib import Path
import sqlite3
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent

from pipeline.adaptation.semantic_reviewer import (
    DEFAULT_ADAPTATION_DB,
    DEFAULT_STAGING_DB,
    run_semantic_review,
)


class TestSemanticReviewer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_json_output = REPO_ROOT / "data" / "adaptation" / "test_semantic_review_34.json"
        cls.payload = run_semantic_review(
            adaptation_db_path=REPO_ROOT / DEFAULT_ADAPTATION_DB,
            staging_db_path=REPO_ROOT / DEFAULT_STAGING_DB,
            output_json_path=cls.test_json_output,
        )

    @classmethod
    def tearDownClass(cls):
        if cls.test_json_output.exists():
            try:
                cls.test_json_output.unlink()
            except Exception:
                pass

    def test_scope_and_counts(self):
        """Assert exactly 34 questions are reviewed (14 review required + 20 validated control)."""
        self.assertEqual(self.payload["metadata"]["total_reviewed"], 34)
        self.assertEqual(self.payload["metadata"]["review_required_count"], 14)
        self.assertEqual(self.payload["metadata"]["validated_control_count"], 20)

        questions = self.payload["questions"]
        self.assertEqual(len(questions), 34)

        group_counts = self.payload["summary"]["by_group"]
        self.assertEqual(group_counts["REVIEW_REQUIRED"]["TOTAL"], 14)
        self.assertEqual(group_counts["VALIDATED_CONTROL"]["TOTAL"], 20)

    def test_strict_json_contract(self):
        """Assert every review record conforms to strict decision JSON schema."""
        for item in self.payload["questions"]:
            rev = item["review"]
            self.assertIn(rev["decision"], ["APPROVE", "REVISE", "REJECT"])
            self.assertIsInstance(rev["grammar_target_ok"], bool)
            self.assertIsInstance(rev["answer_integrity_ok"], bool)
            self.assertIsInstance(rev["originality_ok"], bool)
            self.assertIsInstance(rev["quality_ok"], bool)
            self.assertIsInstance(rev["reason"], str)
            self.assertTrue(len(rev["reason"].strip()) > 10)

    def test_decision_logic_rules(self):
        """Assert decision rules: APPROVE iff all four major checks are True."""
        for item in self.payload["questions"]:
            rev = item["review"]
            all_checks_true = (
                rev["grammar_target_ok"]
                and rev["answer_integrity_ok"]
                and rev["originality_ok"]
                and rev["quality_ok"]
            )
            if rev["decision"] == "APPROVE":
                self.assertTrue(all_checks_true, f"QID {item['source_question_id']} APPROVED but has failing checks: {rev}")
            elif rev["decision"] == "REVISE":
                self.assertFalse(all_checks_true, f"QID {item['source_question_id']} marked REVISE but all checks are True")

    def test_sqlite_table_persistence(self):
        """Assert separate SQLite review table is created and populated with 34 rows."""
        conn = sqlite3.connect(REPO_ROOT / DEFAULT_ADAPTATION_DB)
        c = conn.cursor()
        count = c.execute("SELECT COUNT(*) FROM pilot_semantic_reviews").fetchone()[0]
        self.assertEqual(count, 34)

        # Check column values
        row = c.execute("SELECT source_question_id, decision, reviewer_model FROM pilot_semantic_reviews LIMIT 1").fetchone()
        self.assertTrue(bool(row[0]))
        self.assertIn(row[1], ["APPROVE", "REVISE", "REJECT"])
        self.assertEqual(row[2], "semantic-reviewer-expert-v1")
        conn.close()

    def test_adaptation_records_counts(self):
        """Assert adaptation records in adapted_questions reflect pilot status (TASK-011H: 127 VALIDATED, 73 REVIEW_REQUIRED, 0 APPROVED)."""
        conn = sqlite3.connect(REPO_ROOT / DEFAULT_ADAPTATION_DB)
        c = conn.cursor()
        statuses = dict(c.execute("SELECT adaptation_status, COUNT(*) FROM adapted_questions WHERE adapted_text IS NOT NULL GROUP BY adaptation_status").fetchall())
        self.assertEqual(statuses.get("VALIDATED"), 127)
        self.assertEqual(statuses.get("REVIEW_REQUIRED"), 73)
        self.assertEqual(statuses.get("APPROVED"), None)
        conn.close()


if __name__ == "__main__":
    unittest.main()
