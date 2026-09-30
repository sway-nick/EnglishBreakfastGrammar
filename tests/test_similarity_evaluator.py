import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from adaptation.similarity_evaluator import (
    extract_non_target_tokens,
    compute_jaccard_similarity,
    compute_shingle_overlap,
    compute_levenshtein_distance,
    compute_levenshtein_similarity,
    evaluate_similarity,
)


class TestSimilarityEvaluator(unittest.TestCase):

    def test_identical_text(self):
        src = "1 We bought some cheese and ham. {{gap_1}} was delicious."
        adp = "1 We bought some cheese and ham. {{gap_1}} was delicious."
        res = evaluate_similarity(src, adp)

        self.assertEqual(res["originality_status"], "REJECTED")
        self.assertEqual(res["jaccard_similarity"], 1.0)
        self.assertEqual(res["levenshtein_similarity"], 1.0)
        self.assertTrue(any("Identical text" in r for r in res["reasons"]))

    def test_trivial_one_or_two_word_replacement(self):
        # Only 'cheese' -> 'bread' replaced, rest of sentence identical
        src = "We bought some cheese and ham at the grocery store."
        adp = "We bought some bread and ham at the grocery store."
        res = evaluate_similarity(src, adp)

        self.assertEqual(res["originality_status"], "REJECTED")
        self.assertTrue(res["forbidden_shingle_detected"])
        self.assertGreater(res["jaccard_similarity"], 0.50)

    def test_large_rewrite(self):
        # Completely reimagined setting, scenario, and words
        src = "1 We bought some cheese and ham. {{gap_1}} was delicious."
        adp = "1 Last night my family ordered authentic Italian pasta. {{gap_1}} tasted wonderful."
        res = evaluate_similarity(src, adp)

        self.assertEqual(res["originality_status"], "VALIDATED")
        self.assertLessEqual(res["jaccard_similarity"], 0.40)
        self.assertLess(res["levenshtein_similarity"], 0.45)
        self.assertFalse(res["forbidden_shingle_detected"])
        self.assertEqual(len(res["matching_shingles"]), 0)

    def test_preserved_grammar_words(self):
        # Target grammar words (e.g. 'always', 'when') excluded from non-target calculation
        src = "You {{gap_1}} your nose when you were little."
        adp = "My younger brother {{gap_1}} strange noises when he was young."
        # Target tokens for quiz-1472 past continuous with always
        target_tokens = ["always", "when"]

        res_without = evaluate_similarity(src, adp)
        res_with = evaluate_similarity(src, adp, target_tokens=target_tokens)

        # Non-target tokens should exclude 'when'
        self.assertNotIn("when", res_with["source_tokens"])
        self.assertNotIn("when", res_with["adapted_tokens"])
        self.assertIn("when", res_without["source_tokens"])

    def test_verbatim_shingle_detection(self):
        # Even if some words are changed, a 3+ word verbatim sequence of content words triggers rejection
        src = "She worked in the quiet library all afternoon without interruption."
        adp = "They walked into the quiet library all afternoon while studying."
        res = evaluate_similarity(src, adp)

        self.assertTrue(res["forbidden_shingle_detected"])
        self.assertEqual(res["originality_status"], "REJECTED")
        self.assertIn("the quiet library", res["matching_shingles"])

    def test_punctuation_and_case_normalization(self):
        # Case, trailing punctuation, and leading numbering should normalize
        src = "10. He didn't want to go! {{gap_1}}?"
        adp = "he didn't want to go {{gap1}}"
        res = evaluate_similarity(src, adp)

        self.assertEqual(res["jaccard_similarity"], 1.0)
        self.assertEqual(res["originality_status"], "REJECTED")

    def test_empty_and_short_text(self):
        res_empty = evaluate_similarity("", "")
        self.assertEqual(res_empty["originality_status"], "REJECTED")

        res_one_empty = evaluate_similarity("Hello world", "")
        self.assertEqual(res_one_empty["originality_status"], "REJECTED")

    def test_threshold_boundaries_jaccard(self):
        # 1. Clean pass (Jaccard <= 0.40, Lev < 0.45, 0 shingles)
        tok_src = ["alpha", "bravo", "charlie", "delta", "echo"]
        tok_adp = ["foxtrot", "golf", "hotel", "india", "alpha"]
        j = compute_jaccard_similarity(tok_src, tok_adp)
        # 1 shared / 9 union = 0.1111 <= 0.40
        self.assertLessEqual(j, 0.40)

        # 2. Review range (0.40 < Jaccard <= 0.50): exactly 3 shared / 7 union = 0.4286
        src_text = "brave knights defended castles carefully"
        adp_text = "defended castles brave warriors fought"
        res_rev = evaluate_similarity(src_text, adp_text)
        self.assertAlmostEqual(res_rev["jaccard_similarity"], 0.4286, places=3)
        self.assertLess(res_rev["levenshtein_similarity"], 0.45)
        self.assertFalse(res_rev["forbidden_shingle_detected"])
        self.assertEqual(res_rev["originality_status"], "REVIEW_REQUIRED")
        self.assertTrue(any("review zone" in r for r in res_rev["reasons"]))

        # 3. Rejection range (Jaccard > 0.50)
        tok_high_a = ["w1", "w2", "w3", "w4"]
        tok_high_b = ["w1", "w2", "w3", "w5"]
        j_high = compute_jaccard_similarity(tok_high_a, tok_high_b)  # 3/5 = 0.60
        self.assertGreater(j_high, 0.50)

        src_high = "brave knights carefully defended castles"
        adp_high = "castles knights proudly defended brave"
        res_high = evaluate_similarity(src_high, adp_high)
        self.assertGreater(res_high["jaccard_similarity"], 0.50)
        self.assertEqual(res_high["originality_status"], "REJECTED")

    def test_levenshtein_distance_and_similarity(self):
        self.assertEqual(compute_levenshtein_distance("kitten", "sitting"), 3)
        sim = compute_levenshtein_similarity("kitten", "sitting")
        # 1 - 3/7 = 4/7 = 0.5714
        self.assertEqual(sim, 0.5714)

        self.assertEqual(compute_levenshtein_similarity("apple", "apple"), 1.0)
        self.assertEqual(compute_levenshtein_similarity("abc", "xyz"), 0.0)


if __name__ == "__main__":
    unittest.main()
