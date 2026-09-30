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
    normalize_text_for_comparison,
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
        self.assertLessEqual(j, 0.40)

        # 2. Review range (0.40 < Jaccard <= 0.50): exactly 3 shared / 7 union = 0.4286
        src_text = "brave knights defended castles carefully"
        adp_text = "defended castles brave warriors fought"
        res_rev = evaluate_similarity(src_text, adp_text)
        self.assertAlmostEqual(res_rev["jaccard_similarity"], 0.4286, places=3)
        self.assertFalse(res_rev["forbidden_shingle_detected"])
        self.assertEqual(res_rev["originality_status"], "REVIEW_REQUIRED")
        self.assertTrue(any("review zone" in r for r in res_rev["reasons"]))

        # 3. Rejection range (Jaccard > 0.50)
        src_high = "brave knights carefully defended castles"
        adp_high = "castles knights proudly defended brave"
        res_high = evaluate_similarity(src_high, adp_high)
        self.assertGreater(res_high["jaccard_similarity"], 0.50)
        self.assertEqual(res_high["originality_status"], "REJECTED")

    def test_levenshtein_distance_and_similarity(self):
        self.assertEqual(compute_levenshtein_distance("kitten", "sitting"), 3)
        sim = compute_levenshtein_similarity("kitten", "sitting")
        self.assertEqual(sim, 0.5714)

        self.assertEqual(compute_levenshtein_similarity("apple", "apple"), 1.0)
        self.assertEqual(compute_levenshtein_similarity("abc", "xyz"), 0.0)

    # =========================================================================
    # TASK-011E CALIBRATION TESTS (SHORT GRAMMAR ITEMS)
    # =========================================================================

    def test_short_article_exercises(self):
        """Short article items (<40 chars) must not be flagged solely by character Levenshtein."""
        # Example 1: Minimal generic article item
        src1 = "1 It's {{gap_1}} animal."
        adp1 = "1 Look over there, it is {{gap_1}} eagle."
        res1 = evaluate_similarity(src1, adp1, target_tokens=["an"])
        self.assertEqual(res1["originality_status"], "VALIDATED")
        self.assertLess(res1["jaccard_similarity"], 0.25)

        # Example 2: Short question with target noun in target tokens
        src2 = "5 Do you have {{gap_1}} umbrella?"
        adp2 = "5 Did you pack {{gap_1}} extra umbrella?"
        res2 = evaluate_similarity(src2, adp2, target_tokens=["an", "a", "umbrella"])
        self.assertEqual(res2["originality_status"], "VALIDATED")
        self.assertTrue(res2["is_short_text"])
        self.assertLess(res2["jaccard_similarity"], 0.25)

    def test_short_irregular_plural_exercises(self):
        """Short morphological templates (<40 chars) must pass when words are distinct."""
        src1 = "1 a university ⇒ {{gap_1}}"
        adp1 = "1 a dictionary ⇒ {{gap_1}}"
        res1 = evaluate_similarity(src1, adp1, target_tokens=["dictionaries"])
        self.assertEqual(res1["originality_status"], "VALIDATED")
        self.assertTrue(res1["is_short_text"])

        src2 = "2 a sandwich ⇒ {{gap_1}}"
        adp2 = "2 a beach ⇒ {{gap_1}}"
        res2 = evaluate_similarity(src2, adp2, target_tokens=["beaches"])
        self.assertEqual(res2["originality_status"], "VALIDATED")

    def test_short_preposition_exercises(self):
        """Short preposition collocations (<40 chars) must pass with low token overlap."""
        src = "1 She is _____ home."
        adp = "1 We stayed _____ school today."
        res = evaluate_similarity(src, adp, target_tokens=["at"])
        self.assertEqual(res["originality_status"], "VALIDATED")
        self.assertTrue(res["is_short_text"])

    def test_short_dialogue_exercises(self):
        """Dialogue framing (A:, B:, quotes, instructions) must be stripped before Levenshtein."""
        # Dialogue 1: Speaker labels and trailing instructions stripped
        src1 = "2 A: 'I'm not going out tonight.' B: '_____.' Choose TWO correct answers"
        adp1 = "2 A: 'I am not attending the party this evening.' B: '_____.' (Identify TWO valid responses)"
        res1 = evaluate_similarity(src1, adp1, target_tokens=["neither", "either", "am", "i"])
        self.assertEqual(res1["originality_status"], "VALIDATED")
        self.assertLess(res1["levenshtein_similarity"], 0.45)

        # Dialogue 2: Short elementary dialogue
        src2 = "1 'Where is Jennifer?' 'She's in _____ kitchen.'"
        adp2 = "1 'Where is David?' 'He is relaxing in _____ garden.'"
        res2 = evaluate_similarity(src2, adp2, target_tokens=["the"])
        self.assertEqual(res2["originality_status"], "VALIDATED")

    def test_legitimate_short_rewrites(self):
        """Independent short sentences with fresh vocabulary must pass cleanly."""
        src = "He drives very fast."
        adp = "My brother travels extremely slowly."
        res = evaluate_similarity(src, adp)
        self.assertEqual(res["originality_status"], "VALIDATED")
        self.assertEqual(res["jaccard_similarity"], 0.0)
        self.assertFalse(res["forbidden_shingle_detected"])

    def test_genuinely_similar_short_texts(self):
        """Genuinely shallow copies of short text must trigger REVIEW_REQUIRED or REJECTED."""
        # Shallow copy 1: Only 1 word changed out of 3 content words
        src1 = "Tom likes big dogs."
        adp1 = "Tom likes big cats."
        # target tokens exclude the grammar verb/adjective
        res1 = evaluate_similarity(src1, adp1, target_tokens=["likes", "big"])
        # Non-target tokens: ['tom', 'dogs'] vs ['tom', 'cats']. Shared 'tom'. Jaccard=0.3333, Lev=0.7778.
        self.assertEqual(res1["originality_status"], "REVIEW_REQUIRED")
        self.assertTrue(res1["is_short_text"])
        self.assertGreaterEqual(res1["levenshtein_similarity"], 0.45)
        self.assertGreaterEqual(res1["jaccard_similarity"], 0.25)

        # Shallow copy 2: Sentence verbatim except 1 noun with 3-word verbatim shingle
        src2 = "The cat is on the mat."
        adp2 = "The cat is on the rug."
        res2 = evaluate_similarity(src2, adp2)
        # Should be REJECTED due to verbatim shingle 'the cat is'
        self.assertEqual(res2["originality_status"], "REJECTED")
        self.assertTrue(res2["forbidden_shingle_detected"])

    def test_existing_rejection_cases_preserved(self):
        """Strict rejection rules (forbidden shingles, Jaccard > 0.50, identical text) remain inviolate."""
        # 1. Identical text
        res_id = evaluate_similarity("She plays guitar beautifully.", "She plays guitar beautifully.")
        self.assertEqual(res_id["originality_status"], "REJECTED")

        # 2. Forbidden shingle
        res_sh = evaluate_similarity(
            "The quick brown fox jumps over the lazy dog.",
            "A fast brown fox jumps over another lazy dog."
        )
        self.assertEqual(res_sh["originality_status"], "REJECTED")
        self.assertTrue(res_sh["forbidden_shingle_detected"])

        # 3. High Jaccard token overlap (> 0.50)
        res_jac = evaluate_similarity(
            "red green blue yellow purple",
            "red green blue orange yellow"
        )
        self.assertEqual(res_jac["originality_status"], "REJECTED")
        self.assertGreater(res_jac["jaccard_similarity"], 0.50)


if __name__ == "__main__":
    unittest.main()
