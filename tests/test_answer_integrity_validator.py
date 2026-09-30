"""Unit Tests for Answer Integrity & Grammatical Dependency Validator (TASK-011H).

Universal English Test Platform
Tests:
1. Preferred context-only substitution with same correct answer
2. Dangerous gender change
3. Dangerous singular/plural change
4. Dangerous pronoun change
5. Correct answer becoming invalid
6. Multiple-choice answer-set preservation
7. Gap answer preservation
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.answer_integrity_validator import (
    validate_answer_integrity,
    detect_high_risk_mutations,
    verify_answer_syntactic_validity,
)


class TestAnswerIntegrityValidator(unittest.TestCase):
    """Test suite for answer integrity, high-risk mutation detection, and answer validity."""

    def test_preferred_context_only_substitution_with_same_correct_answer(self):
        """Test preferred context-only substitution preserving identical correct answer.
        
        Example 1:
        Source: Kate is _____ than her sister. (friendly | friendlier | more friendlier; Correct: friendlier)
        Adapted: Julia is _____ than her classmate. (friendly | friendlier | more friendlier; Correct: friendlier)
        
        Example 2:
        Source: Where is the milk? It's _____ the fridge. (at | in | on; Correct: in)
        Adapted: Where is the juice? It's _____ the cupboard. (at | in | on; Correct: in)
        """
        # Example 1
        src_1 = {
            "response_model": "single_choice",
            "content": "Kate is _____ than her sister.",
            "options": [
                {"text": "friendly", "is_correct": 0},
                {"text": "friendlier", "is_correct": 1},
                {"text": "more friendlier", "is_correct": 0},
            ],
        }
        adapt_1 = {
            "adapted_text": "Julia is _____ than her classmate.",
            "options": [
                {"text": "friendly", "is_correct": 0},
                {"text": "friendlier", "is_correct": 1},
                {"text": "more friendlier", "is_correct": 0},
            ],
        }
        res_1 = validate_answer_integrity(src_1, adapt_1)
        self.assertTrue(res_1.is_valid)
        self.assertTrue(res_1.answer_preserved)
        self.assertTrue(res_1.is_answer_valid)
        self.assertFalse(res_1.review_required)
        self.assertEqual(res_1.source_correct_answers, ["friendlier"])
        self.assertEqual(res_1.adapted_correct_answers, ["friendlier"])

        # Example 2
        src_2 = {
            "response_model": "single_choice",
            "content": "Where is the milk? It's _____ the fridge.",
            "options": [
                {"text": "at", "is_correct": 0},
                {"text": "in", "is_correct": 1},
                {"text": "on", "is_correct": 0},
            ],
        }
        adapt_2 = {
            "adapted_text": "Where is the juice? It's _____ the cupboard.",
            "options": [
                {"text": "at", "is_correct": 0},
                {"text": "in", "is_correct": 1},
                {"text": "on", "is_correct": 0},
            ],
        }
        res_2 = validate_answer_integrity(src_2, adapt_2)
        self.assertTrue(res_2.is_valid)
        self.assertTrue(res_2.answer_preserved)
        self.assertTrue(res_2.is_answer_valid)
        self.assertFalse(res_2.review_required)
        self.assertEqual(res_2.source_correct_answers, ["in"])
        self.assertEqual(res_2.adapted_correct_answers, ["in"])

    def test_dangerous_gender_change(self):
        """Test detection of dangerous gender shift affecting dependent pronouns."""
        src = {
            "response_model": "single_choice",
            "content": "Kate looked at _____ in the mirror.",
            "options": [
                {"text": "herself", "is_correct": 1},
                {"text": "himself", "is_correct": 0},
                {"text": "itself", "is_correct": 0},
            ],
        }
        # Adaptation changes female subject 'Kate' to male subject 'David',
        # but keeps feminine answer 'herself' -> creates gender contradiction!
        adapt = {
            "adapted_text": "David looked at _____ in the mirror.",
            "options": [
                {"text": "herself", "is_correct": 1},
                {"text": "himself", "is_correct": 0},
                {"text": "itself", "is_correct": 0},
            ],
        }
        res = validate_answer_integrity(src, adapt)
        # Should detect gender mutation
        gender_mutations = [m for m in res.high_risk_mutations if "gender" in m]
        self.assertTrue(len(gender_mutations) > 0, "Gender mutation must be detected")
        # Should fail syntactic validity because David cannot bind 'herself'
        self.assertFalse(res.is_answer_valid)
        self.assertTrue(res.review_required)

    def test_dangerous_singular_plural_change(self):
        """Test detection of dangerous singular to plural mutation.
        
        Example from user prompt:
        Source: Kate is _____ than her sister.
        Unpreferred adaptation: Tom and Jack are _____ than their sister.
        """
        src = {
            "response_model": "single_choice",
            "content": "Kate is _____ than her sister.",
            "options": [
                {"text": "friendlier", "is_correct": 1},
                {"text": "friendly", "is_correct": 0},
            ],
        }
        adapt = {
            "adapted_text": "Tom and Jack are _____ than their sister.",
            "options": [
                {"text": "friendlier", "is_correct": 1},
                {"text": "friendly", "is_correct": 0},
            ],
        }
        res = validate_answer_integrity(src, adapt)
        num_mutations = [m for m in res.high_risk_mutations if "singular_plural" in m]
        self.assertTrue(len(num_mutations) > 0, "Singular/plural mutation must be detected")

    def test_dangerous_pronoun_change(self):
        """Test detection of dangerous grammatical person/pronoun shift (e.g. 1st person to 3rd person)."""
        src = {
            "response_model": "single_choice",
            "content": "I usually drink coffee in the morning.",
            "options": [
                {"text": "drink", "is_correct": 1},
                {"text": "drinks", "is_correct": 0},
            ],
        }
        adapt = {
            "adapted_text": "He usually _____ tea in the morning.",
            "options": [
                {"text": "drink", "is_correct": 1},
                {"text": "drinks", "is_correct": 0},
            ],
        }
        res = validate_answer_integrity(src, adapt)
        person_mutations = [m for m in res.high_risk_mutations if "pronoun" in m]
        self.assertTrue(len(person_mutations) > 0, "Grammatical person mutation must be detected")

    def test_correct_answer_becoming_invalid(self):
        """Test failure when adapted context renders the source correct answer ungrammatical.
        
        E.g. Indefinite article 'a' followed by uncountable noun 'milk'.
        """
        src = {
            "response_model": "single_choice",
            "content": "Could you bring me _____ apple?",
            "options": [
                {"text": "an", "is_correct": 1},
                {"text": "a", "is_correct": 0},
                {"text": "some", "is_correct": 0},
            ],
        }
        # In this flawed adaptation, the author substituted 'milk' (uncountable)
        # while copying the correct answer 'a'
        adapt = {
            "adapted_text": "Could you bring me _____ milk?",
            "options": [
                {"text": "a", "is_correct": 1},
                {"text": "some", "is_correct": 0},
            ],
        }
        res = validate_answer_integrity(src, adapt)
        self.assertFalse(res.is_answer_valid, "Answer 'a' before uncountable 'milk' must be invalid")
        self.assertTrue(res.review_required, "Invalid answer must trigger review_required")
        self.assertTrue(any("uncountable" in r.lower() for r in res.reasons))

    def test_multiple_choice_answer_set_preservation(self):
        """Test multiple-choice answer-set preservation and divergence detection."""
        src = {
            "response_model": "multiple_choice",
            "content": "If you practice every afternoon, you _____ the tournament.",
            "options": [
                {"text": "'ll win", "is_correct": 1},
                {"text": "might win", "is_correct": 1},
                {"text": "win", "is_correct": 0},
            ],
        }
        # Matching set
        adapt_ok = {
            "adapted_text": "If she trains diligently, she _____ the championship.",
            "options": [
                {"text": "'ll win", "is_correct": 1},
                {"text": "might win", "is_correct": 1},
                {"text": "win", "is_correct": 0},
            ],
        }
        res_ok = validate_answer_integrity(src, adapt_ok)
        self.assertTrue(res_ok.answer_preserved)
        self.assertFalse(res_ok.review_required)

        # Divergent set (only 1 marked correct instead of 2)
        adapt_divergent = {
            "adapted_text": "If she trains diligently, she _____ the championship.",
            "options": [
                {"text": "'ll win", "is_correct": 1},
                {"text": "might win", "is_correct": 0},
                {"text": "win", "is_correct": 0},
            ],
        }
        res_div = validate_answer_integrity(src, adapt_divergent)
        self.assertFalse(res_div.answer_preserved)
        self.assertTrue(res_div.review_required)

    def test_gap_answer_preservation(self):
        """Test gap answer preservation across single-gap and multi-gap exercises."""
        # Single gap
        src_gap = {
            "response_model": "gap",
            "content": "She {{gap_1}} to school yesterday.",
            "gaps": [
                {"gap_order": 1, "correct_answer": "walked"},
            ],
        }
        adapt_gap_ok = {
            "adapted_text": "The student {{gap_1}} to the library yesterday.",
            "gaps": [
                {"gap_order": 1, "correct_answer": "walked"},
            ],
        }
        res_ok = validate_answer_integrity(src_gap, adapt_gap_ok)
        self.assertTrue(res_ok.answer_preserved)
        self.assertFalse(res_ok.review_required)

        # Divergent gap answer
        adapt_gap_div = {
            "adapted_text": "The student {{gap_1}} to the library yesterday.",
            "gaps": [
                {"gap_order": 1, "correct_answer": "drove"},
            ],
        }
        res_div = validate_answer_integrity(src_gap, adapt_gap_div)
        self.assertFalse(res_div.answer_preserved)
        self.assertTrue(res_div.review_required)


if __name__ == "__main__":
    unittest.main()
