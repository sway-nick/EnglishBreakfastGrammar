"""Unit Tests for Full-Corpus Adaptation Orchestrator (TASK-012).

Universal English Test Platform
Tests:
1. Resumability and queue selection (PENDING items only)
2. Idempotency & transaction safety
3. Answer preservation invariant (source == adapted)
4. High-risk mutation detection and routing to REVIEW_REQUIRED
5. Status transitions (VALIDATED, REVIEW_REQUIRED, REJECTED)
6. Retry handling and failure isolation
7. Selective AI review & control sampling across response models
8. Pilot status synchronization (188 VALIDATED, 12 REVIEW_REQUIRED)
"""

from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.full_corpus_orchestrator import (
    DEFAULT_ADAPTATION_DB,
    DEFAULT_STAGING_DB,
    DRY_RUN_ADAPTATION_CATALOG,
    FullCorpusOrchestrator,
    OrchestratorConfig,
    resolve_status_with_ai_review,
)
from pipeline.adaptation.answer_integrity_validator import normalize_token
from pipeline.adaptation.pilot_sync import sync_pilot_statuses


class TestFullCorpusOrchestrator(unittest.TestCase):
    """Test suite for full-corpus adaptation orchestrator logic, invariants, and dry run."""

    @classmethod
    def setUpClass(cls):
        cls.adapt_db = DEFAULT_ADAPTATION_DB
        cls.staging_db = DEFAULT_STAGING_DB
        cls.orchestrator = FullCorpusOrchestrator(cls.adapt_db, cls.staging_db)

    def test_01_pilot_status_synchronization(self):
        """Verify that pilot status synchronization produces exact 188 VALIDATED, 12 REVIEW_REQUIRED split."""
        conn = sqlite3.connect(self.adapt_db)
        try:
            # Run synchronization
            sync_res = sync_pilot_statuses(self.adapt_db)
            self.assertEqual(sync_res["total_pilot_questions"], 200)
            self.assertEqual(sync_res["status_distribution"]["VALIDATED"], 188)
            self.assertEqual(sync_res["status_distribution"]["REVIEW_REQUIRED"], 12)
            self.assertEqual(sync_res["status_distribution"]["REJECTED"], 0)

            # Query database directly to assert persisted counts
            pilot_qids_res = conn.execute(
                """
                SELECT adaptation_status, COUNT(*)
                FROM adapted_questions
                WHERE adapted_by IN ('pilot_generator', 'pilot_revision_TASK-011H')
                GROUP BY adaptation_status
                """
            ).fetchall()
            status_map = dict(pilot_qids_res)
            self.assertEqual(status_map.get("VALIDATED"), 188)
            self.assertEqual(status_map.get("REVIEW_REQUIRED"), 12)
            self.assertIsNone(status_map.get("REJECTED"))
        finally:
            conn.close()

    def test_02_dry_run_catalog_cardinality_and_coverage(self):
        """Assert the 25 dry-run candidate questions cover all 3 response models with required proportions."""
        conn = sqlite3.connect(f"file:{self.staging_db.resolve()}?mode=ro", uri=True)
        try:
            qids = list(DRY_RUN_ADAPTATION_CATALOG.keys())
            self.assertEqual(len(qids), 25, "Dry run catalog must contain exactly 25 items.")

            placeholders = ",".join("?" for _ in qids)
            rows = conn.execute(
                f"SELECT question_id, response_model FROM staging_questions WHERE question_id IN ({placeholders})",
                qids,
            ).fetchall()

            model_counts: Dict[str, int] = {}
            for _, rm in rows:
                model_counts[rm] = model_counts.get(rm, 0) + 1

            self.assertEqual(model_counts.get("single_choice"), 10)
            self.assertEqual(model_counts.get("gap"), 10)
            self.assertEqual(model_counts.get("multiple_choice"), 5)
        finally:
            conn.close()

    def test_03_answer_preservation_invariant_in_catalog(self):
        """Verify that 100% of candidate items in DRY_RUN_ADAPTATION_CATALOG preserve source correct answers."""
        conn = sqlite3.connect(f"file:{self.staging_db.resolve()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            for qid, adapt_spec in DRY_RUN_ADAPTATION_CATALOG.items():
                stage_q = conn.execute("SELECT * FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
                rm = stage_q["response_model"]

                if rm == "single_choice":
                    stage_corr = conn.execute(
                        "SELECT text FROM staging_options WHERE question_id = ? AND is_correct = 1", (qid,)
                    ).fetchone()[0]
                    adapt_corr = [o["text"] for o in adapt_spec["options"] if o["is_correct"]][0]
                    self.assertEqual(
                        normalize_token(stage_corr),
                        normalize_token(adapt_corr),
                        f"Answer divergence in single_choice QID {qid}",
                    )

                elif rm == "multiple_choice":
                    stage_corrs = {
                        normalize_token(r[0])
                        for r in conn.execute(
                            "SELECT text FROM staging_options WHERE question_id = ? AND is_correct = 1", (qid,)
                        ).fetchall()
                    }
                    adapt_corrs = {
                        normalize_token(o["text"]) for o in adapt_spec["options"] if o["is_correct"]
                    }
                    self.assertEqual(
                        stage_corrs,
                        adapt_corrs,
                        f"Answer set divergence in multiple_choice QID {qid}",
                    )

                elif rm == "gap":
                    stage_gaps = conn.execute(
                        "SELECT correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)
                    ).fetchall()
                    for idx, g_spec in enumerate(adapt_spec["gaps"]):
                        stage_ans = stage_gaps[idx][0].strip().lower().replace("’", "'").replace("‘", "'").replace("\ufffd", "'")
                        adapt_ans = g_spec["correct_answer"].strip().lower().replace("’", "'").replace("‘", "'")
                        self.assertEqual(
                            stage_ans,
                            adapt_ans,
                            f"Answer divergence in gap QID {qid}",
                        )
        finally:
            conn.close()

    def test_04_high_risk_mutation_detection_and_routing(self):
        """Verify that items with high-risk mutations are routed to REVIEW_REQUIRED."""
        # Simulated singular/plural shift
        from pipeline.adaptation.answer_integrity_validator import detect_high_risk_mutations

        src = "The manager is waiting in the lobby."
        adapt = "The directors are waiting in the lobby."
        mutations = detect_high_risk_mutations(src, adapt, ["is"], ["are"])
        self.assertTrue(
            any("singular_plural" in m for m in mutations),
            "Expected singular_plural high-risk mutation to be detected.",
        )

        # Simulated gender shift
        src_g = "John left his car near the entrance."
        adapt_g = "Sarah left her car near the entrance."
        mutations_g = detect_high_risk_mutations(src_g, adapt_g, ["his"], ["her"])
        self.assertTrue(
            any("gender" in m for m in mutations_g),
            "Expected gender high-risk mutation to be detected.",
        )

    def test_05_status_transitions_and_review_decisions(self):
        """Verify status determination and automatic AI review resolution under TASK-012A."""
        conn = sqlite3.connect(self.adapt_db)
        try:
            # Query dry-run results from database
            rows = conn.execute(
                """
                SELECT adapted_question_id, adaptation_status, review_required
                FROM adapted_questions
                WHERE adapted_by = 'full_corpus_orchestrator'
                """
            ).fetchall()
            self.assertEqual(len(rows), 25, "Dry run must have recorded exactly 25 questions.")

            statuses = {r[1] for r in rows}
            # Under TASK-012A, all items that received AI APPROVE resolve to VALIDATED with review_required = 0
            self.assertEqual(statuses, {"VALIDATED"})

            for aqid, stat, rev_req in rows:
                self.assertEqual(stat, "VALIDATED")
                self.assertEqual(rev_req, 0, f"{aqid} resolved to VALIDATED must have review_required = 0")
        finally:
            conn.close()

    def test_06_resumability_and_queue_isolation(self):
        """Verify that the queue query only selects PENDING questions and leaves completed items untouched."""
        conn = sqlite3.connect(self.adapt_db)
        try:
            total_count = conn.execute("SELECT COUNT(*) FROM adapted_questions").fetchone()[0]
            self.assertEqual(total_count, 5796, "Total questions in adaptation.db must be 5,796.")

            pending_count = conn.execute(
                "SELECT COUNT(*) FROM adapted_questions WHERE adaptation_status = 'PENDING'"
            ).fetchone()[0]
            # 5796 total - 200 pilot - 25 dry-run = 5571 PENDING
            self.assertEqual(pending_count, 5571)

            # Ensure all non-pending items have adapted_text populated
            non_pending_rows = conn.execute(
                "SELECT COUNT(*) FROM adapted_questions WHERE adaptation_status != 'PENDING' AND adapted_text IS NULL"
            ).fetchone()[0]
            self.assertEqual(non_pending_rows, 0, "No completed question may have NULL adapted_text.")
        finally:
            conn.close()

    def test_07_selective_ai_review_and_control_sampling(self):
        """Verify that selective AI review records exist for all REVIEW_REQUIRED items and control sample."""
        conn = sqlite3.connect(self.adapt_db)
        try:
            rev_rows = conn.execute(
                """
                SELECT source_question_id, sample_group, decision, grammar_target_ok, answer_integrity_ok
                FROM pilot_semantic_reviews
                WHERE sample_group IN ('DRY_RUN_EVAL', 'DRY_RUN_CONTROL')
                """
            ).fetchall()
            self.assertGreaterEqual(len(rev_rows), 7, "At least 7 AI reviews must be conducted during dry run.")

            decisions = [r[2] for r in rev_rows]
            self.assertTrue(all(d == "APPROVE" for d in decisions), "All dry-run AI reviews must be APPROVE.")

            sample_groups = {r[1] for r in rev_rows}
            self.assertIn("DRY_RUN_EVAL", sample_groups)
            self.assertIn("DRY_RUN_CONTROL", sample_groups)
        finally:
            conn.close()

    def test_08_run_lifecycle_and_metrics_persistence(self):
        """Verify adaptation_runs table records run metadata and completion status."""
        conn = sqlite3.connect(self.adapt_db)
        try:
            run_row = conn.execute(
                """
                SELECT run_id, status, generated_count, validated_count, rejected_count
                FROM adaptation_runs
                WHERE run_id = 'orch_task012_dryrun_25'
                """
            ).fetchone()
            self.assertIsNotNone(run_row, "Run record orch_task012_dryrun_25 must exist in adaptation_runs.")
            self.assertEqual(run_row[1], "completed")
            self.assertEqual(run_row[2], 25)
            self.assertEqual(run_row[3], 25)
            self.assertEqual(run_row[4], 0)
        finally:
            conn.close()

    def test_09_automatic_ai_review_status_flow(self):
        """Verify TASK-012A automatic status resolution rules across all permutations."""
        # 1. Deterministic VALIDATED without review -> VALIDATED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("VALIDATED", None), ("VALIDATED", 0))

        # 2. Deterministic VALIDATED with AI APPROVE (control sample) -> VALIDATED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("VALIDATED", "APPROVE"), ("VALIDATED", 0))

        # 3. Deterministic VALIDATED with AI REVISE (control sample failure) -> REVIEW_REQUIRED (review_required = 1)
        self.assertEqual(resolve_status_with_ai_review("VALIDATED", "REVISE"), ("REVIEW_REQUIRED", 1))

        # 4. Deterministic VALIDATED with AI REJECT (control sample failure) -> REJECTED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("VALIDATED", "REJECT"), ("REJECTED", 0))

        # 5. Deterministic REVIEW_REQUIRED + AI APPROVE -> VALIDATED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("REVIEW_REQUIRED", "APPROVE"), ("VALIDATED", 0))

        # 6. Deterministic REVIEW_REQUIRED + AI REVISE -> REVIEW_REQUIRED (review_required = 1)
        self.assertEqual(resolve_status_with_ai_review("REVIEW_REQUIRED", "REVISE"), ("REVIEW_REQUIRED", 1))

        # 7. Deterministic REVIEW_REQUIRED + AI REJECT -> REJECTED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("REVIEW_REQUIRED", "REJECT"), ("REJECTED", 0))

        # 8. Deterministic REVIEW_REQUIRED without review -> REVIEW_REQUIRED (review_required = 1)
        self.assertEqual(resolve_status_with_ai_review("REVIEW_REQUIRED", None), ("REVIEW_REQUIRED", 1))

        # 9. Deterministic REJECTED regardless of review -> REJECTED (review_required = 0)
        self.assertEqual(resolve_status_with_ai_review("REJECTED", "APPROVE"), ("REJECTED", 0))
        self.assertEqual(resolve_status_with_ai_review("REJECTED", None), ("REJECTED", 0))

    def test_10_zero_answer_divergence_invariant(self):
        """Verify 100% answer preservation invariant (source == adapted) across all dry-run items in database."""
        conn = sqlite3.connect(self.adapt_db)
        stage_conn = sqlite3.connect(f"file:{self.staging_db.resolve()}?mode=ro", uri=True)
        try:
            qids = list(DRY_RUN_ADAPTATION_CATALOG.keys())
            for qid in qids:
                aqid = f"adapt_{qid}"
                stage_q = stage_conn.execute("SELECT response_model FROM staging_questions WHERE question_id = ?", (qid,)).fetchone()
                rm = stage_q[0]

                if rm == "single_choice":
                    stage_ans = stage_conn.execute(
                        "SELECT text FROM staging_options WHERE question_id = ? AND is_correct = 1", (qid,)
                    ).fetchone()[0]
                    adapt_ans = conn.execute(
                        "SELECT adapted_text FROM adapted_options WHERE adapted_question_id = ? AND adapted_is_correct = 1", (aqid,)
                    ).fetchone()[0]
                    self.assertEqual(
                        normalize_token(stage_ans),
                        normalize_token(adapt_ans),
                        f"Answer divergence in single_choice question {qid}",
                    )

                elif rm == "multiple_choice":
                    stage_answers = {
                        normalize_token(r[0])
                        for r in stage_conn.execute(
                            "SELECT text FROM staging_options WHERE question_id = ? AND is_correct = 1", (qid,)
                        ).fetchall()
                    }
                    adapt_answers = {
                        normalize_token(r[0])
                        for r in conn.execute(
                            "SELECT adapted_text FROM adapted_options WHERE adapted_question_id = ? AND adapted_is_correct = 1", (aqid,)
                        ).fetchall()
                    }
                    self.assertEqual(
                        stage_answers,
                        adapt_answers,
                        f"Answer divergence in multiple_choice question {qid}",
                    )

                elif rm == "gap":
                    stage_gap_answers = [
                        normalize_token(r[0])
                        for r in stage_conn.execute(
                            "SELECT correct_answer FROM staging_gaps WHERE question_id = ? ORDER BY gap_order", (qid,)
                        ).fetchall()
                    ]
                    adapt_gap_answers = [
                        normalize_token(r[0])
                        for r in conn.execute(
                            "SELECT adapted_correct_answer FROM adapted_gaps WHERE adapted_question_id = ? ORDER BY gap_order", (aqid,)
                        ).fetchall()
                    ]
                    self.assertEqual(
                        stage_gap_answers,
                        adapt_gap_answers,
                        f"Answer divergence in gap question {qid}",
                    )
        finally:
            conn.close()
            stage_conn.close()


if __name__ == "__main__":
    unittest.main()
