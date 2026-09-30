import json
import unittest
from pathlib import Path

from pipeline.adaptation.pilot_data import PILOT_DATA
from pipeline.adaptation.pilot_generator import export_pilot_universal_json, run_preview_gate_validation
from pipeline.adaptation.similarity_evaluator import evaluate_similarity

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPilotGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(REPO_ROOT / "data" / "pilot_source_20.json", "r", encoding="utf-8") as f:
            cls.source_exercises = {ex["exercise_id"]: ex for ex in json.load(f)}

    def test_pilot_scope_and_counts(self):
        """Assert exactly 20 exercises and 200 questions are curated in pilot data."""
        self.assertEqual(len(PILOT_DATA), 20, "Pilot must contain exactly 20 exercises.")

        total_questions = sum(len(ex["questions"]) for ex in PILOT_DATA.values())
        self.assertEqual(total_questions, 200, "Pilot must contain exactly 200 questions.")

    def test_response_models_representation(self):
        """Assert all three response models (gap, single_choice, multiple_choice) are represented."""
        models = set()
        model_counts = {}
        for eid, ex in PILOT_DATA.items():
            src_ex = self.source_exercises[eid]
            src_qs = {q["question_id"]: q for q in src_ex["questions"]}
            for q in ex["questions"]:
                rm = src_qs[q["question_id"]]["response_model"]
                models.add(rm)
                model_counts[rm] = model_counts.get(rm, 0) + 1

        self.assertIn("gap", models)
        self.assertIn("single_choice", models)
        self.assertIn("multiple_choice", models)
        self.assertEqual(model_counts["multiple_choice"], 7)
        self.assertEqual(model_counts["single_choice"], 103)
        self.assertEqual(model_counts["gap"], 90)

    def test_structural_invariants(self):
        """Assert gap count, option count, and correct answer semantics are preserved."""
        for eid, ex in PILOT_DATA.items():
            src_ex = self.source_exercises[eid]
            src_qs = {q["question_id"]: q for q in src_ex["questions"]}

            for q in ex["questions"]:
                qid = q["question_id"]
                src_q = src_qs[qid]
                rm = src_q["response_model"]

                # Gap count invariant
                self.assertEqual(len(q.get("gaps", [])), len(src_q["gaps"]), f"Gap count mismatch in {eid} Q{qid}")

                # Option count invariant
                self.assertEqual(len(q.get("options", [])), len(src_q["options"]), f"Option count mismatch in {eid} Q{qid}")

                # Single choice: exactly 1 correct
                if rm == "single_choice":
                    correct_opts = [o for o in q["options"] if o["is_correct"] == 1]
                    self.assertEqual(len(correct_opts), 1, f"Single choice must have 1 correct option in {eid} Q{qid}")

                # Multiple choice: exact matching count of correct options (2)
                elif rm == "multiple_choice":
                    correct_opts = [o for o in q["options"] if o["is_correct"] == 1]
                    src_correct = [o for o in src_q["options"] if o["is_correct"] == 1]
                    self.assertEqual(len(correct_opts), len(src_correct), f"Multiple choice count mismatch in {eid} Q{qid}")
                    self.assertEqual(len(correct_opts), 2)

                # Gap select: correct answer exists in options
                for g_spec in q.get("gaps", []):
                    if q.get("options"):
                        opt_texts = [o["text"] for o in q["options"]]
                        self.assertIn(g_spec["correct_answer"], opt_texts, f"Gap answer not in options in {eid} Q{qid}")

    def test_originality_evaluator_metrics(self):
        """Assert zero rejected items and that every item is VALIDATED or REVIEW_REQUIRED."""
        validated = 0
        review_required = 0
        rejected = 0

        for eid, ex in PILOT_DATA.items():
            src_ex = self.source_exercises[eid]
            src_qs = {q["question_id"]: q for q in src_ex["questions"]}

            for q in ex["questions"]:
                qid = q["question_id"]
                src_q = src_qs[qid]
                res = evaluate_similarity(src_q["content"], q["adapted_text"], q.get("target_tokens"))
                status = res["originality_status"]

                if status == "VALIDATED":
                    validated += 1
                elif status == "REVIEW_REQUIRED":
                    review_required += 1
                else:
                    rejected += 1

        self.assertEqual(rejected, 0, f"No questions should be REJECTED, but found {rejected}")
        self.assertEqual(validated + review_required, 200)
        self.assertGreater(validated, 100, f"Expected majority to be VALIDATED, got {validated}")

    def test_preview_gate_on_pilot_export(self):
        """Assert exported Universal Lesson JSON passes strict validation and Preview Gate."""
        pilot_json_path = REPO_ROOT / "data" / "pilot_adapted_lessons.json"
        self.assertTrue(pilot_json_path.exists(), "pilot_adapted_lessons.json must exist")

        gate_res = run_preview_gate_validation(pilot_json_path)
        self.assertEqual(gate_res["totalLessons"], 12)
        self.assertEqual(gate_res["validCount"], 12)
        self.assertEqual(gate_res["gatePassed"], 12)
        self.assertEqual(len(gate_res["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
