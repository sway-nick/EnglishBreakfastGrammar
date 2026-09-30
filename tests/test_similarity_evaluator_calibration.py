"""
test_similarity_evaluator_calibration.py
Unit and regression tests for calibrated similarity evaluation (TASK-013E).
Verifies:
1. Shingles do not cross gap/blank placeholders ({{gap_N}}, _____).
2. Shingles do not cross dialogue speaker boundaries (A:, B:, Speaker 1:).
3. Abbreviations (p.m. / a.m.) normalize cleanly without spurious punctuation shingles.
4. Severity calibration: isolated single shingle with low/moderate similarity routes to REVIEW_REQUIRED.
5. High-confidence copy: shingles with elevated Jaccard/Levenshtein or multiple shingles route to REJECTED.
6. Regression test cases reflecting the Batch 1 audit findings across the 14 historical QIDs.
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from adaptation.similarity_evaluator import (
    extract_segmented_tokens,
    compute_boundary_aware_shingles,
    normalize_abbreviations,
    normalize_text_for_comparison,
    evaluate_similarity,
)


class TestSimilarityEvaluatorCalibration(unittest.TestCase):

    def test_shingles_do_not_cross_gap_placeholders(self):
        # In QID 4214: "is {{gap_1}} (noisy) the"
        # Without boundary awareness, "is", "noisy", "the" formed "is noisy the"
        src = "The city is {{gap_1}} the countryside."
        adp = "This avenue is noisy the whole afternoon."
        res = evaluate_similarity(src, adp, target_tokens=["noisy"])

        # "is" is before {{gap_1}}, "the countryside" is after {{gap_1}}.
        # In adp, "is noisy the" should NOT match because "is" and "the" in src are in different segments.
        self.assertNotIn("is noisy the", res["matching_shingles"])
        self.assertFalse(res["forbidden_shingle_detected"])

    def test_shingles_do_not_cross_blank_placeholders(self):
        # In QID 5736: "7 p.m., _____ then"
        src = "The train arrives at 7 p.m., _____ then we will eat."
        adp = "The meeting ends at 7 pm then we will go home."
        res = evaluate_similarity(src, adp)

        # "pm" is before blank, "then we will" is after blank
        # In adp, "pm then we" should not bridge across the blank in src
        self.assertNotIn("pm then we", res["matching_shingles"])

    def test_shingles_do_not_cross_dialogue_speaker_boundaries(self):
        # In QID 5088: "B: No, {{gap_1}} about"
        src = "A: Are you coming? B: No, {{gap_1}} about tomorrow."
        adp = "B no about that issue."
        res = evaluate_similarity(src, adp)

        # "B:" is a speaker tag, not a token 'b'. "no" is in speaker B turn.
        self.assertNotIn("b no about", res["matching_shingles"])
        self.assertFalse(res["forbidden_shingle_detected"])

    def test_abbreviation_normalization(self):
        # p.m. / a.m. normalized to pm / am
        self.assertEqual(normalize_abbreviations("at 7 p.m. today"), "at 7 pm today")
        self.assertEqual(normalize_abbreviations("at 9 a.m. sharp"), "at 9 am sharp")

        src = "We left at 7 p.m. and arrived safely."
        adp = "We arrived at 7 pm and ate dinner."
        res = evaluate_similarity(src, adp)

        # "at 7 pm" is a valid shingle if both have "at 7 pm"
        self.assertIn("at 7 pm", res["matching_shingles"])
        # Punctuation must not produce individual 'p' or 'm' tokens
        self.assertNotIn("p", res["source_tokens"])
        self.assertNotIn("m", res["source_tokens"])

    def test_isolated_functional_shingle_routes_to_review_required(self):
        # Isolated 3-word functional phrase with low Jaccard and Levenshtein
        # e.g. "two or three" (QID 4188) or "there is a" (QID 5069)
        src = "In our garden there is a beautiful cherry blossom tree that blooms each spring."
        adp = "Outside the office there is a newly opened coffee kiosk serving fresh espresso."
        res = evaluate_similarity(src, adp)

        self.assertTrue(res["forbidden_shingle_detected"])
        self.assertEqual(len(res["matching_shingles"]), 1)
        self.assertEqual(res["matching_shingles"][0], "there is a")
        self.assertLessEqual(res["jaccard_similarity"], 0.40)
        self.assertLess(res["levenshtein_similarity"], 0.55)
        # Calibrated behavior: REVIEW_REQUIRED, NOT REJECTED
        self.assertEqual(res["originality_status"], "REVIEW_REQUIRED")
        self.assertTrue(any("Routed to AI review" in r for r in res["reasons"]))

    def test_high_confidence_shallow_copy_with_elevated_similarity_rejected(self):
        # Shingle detected AND elevated similarity (Lev >= 0.55 or Jaccard > 0.40)
        # e.g. QID 5142: "hasn't got a" with Lev >= 0.55
        src = "He hasn't got a car so he takes the bus every morning."
        adp = "He hasn't got a car so he walks to work every morning."
        res = evaluate_similarity(src, adp)

        self.assertTrue(res["forbidden_shingle_detected"])
        self.assertGreaterEqual(res["levenshtein_similarity"], 0.55)
        self.assertEqual(res["originality_status"], "REJECTED")
        self.assertTrue(any("High-confidence shallow copy" in r for r in res["reasons"]))

    def test_high_confidence_shallow_copy_with_multiple_shingles_rejected(self):
        # Multiple shingles detected (>= 2 distinct shingles)
        src = "The little boy wanted to play in the park after lunch."
        adp = "The little boy decided to play in the garden before dinner."
        res = evaluate_similarity(src, adp)

        self.assertTrue(res["forbidden_shingle_detected"])
        self.assertGreaterEqual(len(res["matching_shingles"]), 2)
        self.assertEqual(res["originality_status"], "REJECTED")

    def test_jaccard_above_50_rejected_unconditionally(self):
        # High token overlap without shingles
        src = "apples bananas cherries dates elderberries figs grapes"
        adp = "figs grapes elderberries dates cherries bananas"
        res = evaluate_similarity(src, adp)

        self.assertGreater(res["jaccard_similarity"], 0.50)
        self.assertEqual(res["originality_status"], "REJECTED")

    def test_qid_5085_speaker_tag_elimination(self):
        # In QID 5085: "A: 'I will open the window.'"
        # Speaker "A:" should not create a token 'a' that bridges with "i will"
        src = "A: 'I will help you with the luggage.' B: 'Thank you.'"
        adp = "I can assist you with those heavy bags."
        res = evaluate_similarity(src, adp)

        self.assertNotIn("a i will", res["matching_shingles"])
        self.assertEqual(res["originality_status"], "VALIDATED")

    def test_qid_5079_speaker_labels_do_not_inflate_jaccard(self):
        # In QID 5079: A: ... B: ...
        src = "A: Are you ready to order? B: Yes, I would like soup."
        adp = "Customer: Are we ready to pay? Waiter: Yes, here is the bill."
        res = evaluate_similarity(src, adp)

        self.assertNotIn("a", res["source_tokens"])
        self.assertNotIn("b", res["source_tokens"])
        self.assertLessEqual(res["jaccard_similarity"], 0.40)


if __name__ == "__main__":
    unittest.main()
