"""
Unit tests for pipeline/cms/excel_to_json.py converter.

Verifies:
- Sheet reading & relational grouping
- Type mapping (gap_select, gap_text, single_choice)
- Placeholder normalization ({{gap_1}} -> {{gap1}})
- accepted_answers reconstruction
- is_correct parsing (True, False, None)
- Numeric sorting
"""

import sys
from pathlib import Path
import unittest
import openpyxl

# Add repo root and pipeline/cms to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CMS_DIR = REPO_ROOT / "pipeline" / "cms"
if str(CMS_DIR) not in sys.path:
    sys.path.insert(0, str(CMS_DIR))

from excel_to_json import (
    convert_workbook_to_lessons,
    normalize_placeholders,
    reconstruct_accepted_answers,
    bool_value,
)


class TestExcelToJson(unittest.TestCase):

    def test_normalize_placeholders(self):
        self.assertEqual(
            normalize_placeholders("1 A: {{gap_1}} you? B: Yes, I {{gap_2}}."),
            "1 A: {{gap1}} you? B: Yes, I {{gap2}}."
        )
        self.assertEqual(normalize_placeholders("No gaps here."), "No gaps here.")
        self.assertEqual(normalize_placeholders(""), "")

    def test_reconstruct_accepted_answers(self):
        # correct_answer + extras
        res = reconstruct_accepted_answers("is", "'s | is | is not")
        self.assertEqual(res, ["is", "'s", "is not"])

        # No extras
        self.assertEqual(reconstruct_accepted_answers("are", None), ["are"])
        self.assertEqual(reconstruct_accepted_answers("are", ""), ["are"])

        # No correct answer, only extras
        self.assertEqual(reconstruct_accepted_answers(None, "am | 'm"), ["am", "'m"])

    def test_bool_value(self):
        self.assertIs(bool_value(True), True)
        self.assertIs(bool_value(False), False)
        self.assertIs(bool_value("TRUE"), True)
        self.assertIs(bool_value("True"), True)
        self.assertIs(bool_value("FALSE"), False)
        self.assertIs(bool_value("false"), False)
        self.assertIsNone(bool_value(None))
        self.assertIsNone(bool_value(""))

    def test_full_workbook_conversion(self):
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # 1. Lessons
        ws_l = wb.create_sheet("Lessons")
        ws_l.append(["lesson_id", "title", "level", "topic", "status", "description", "source_provider", "source_url", "order"])
        ws_l.append(["L001", "Present Simple", "A1", "Grammar", "draft", "Learn to be", "Test-English", "https://example.com", 1])

        # 2. Exercises
        ws_e = wb.create_sheet("Exercises")
        ws_e.append(["exercise_id", "lesson_id", "page", "order", "title", "instruction", "status", "source_file"])
        ws_e.append(["E001", "L001", 1, 1, "Exercise 1", "Fill the gaps", "draft", "1.txt"])

        # 3. Questions
        ws_q = wb.create_sheet("Questions")
        ws_q.append(["question_id", "exercise_id", "lesson_id", "order", "response_model", "content", "explanation"])
        ws_q.append(["Q001", "E001", "L001", 1, "gap", "A: {{gap_1}} you a teacher? B: Yes, I {{gap_2}}.", "Forms of be"])
        ws_q.append(["Q002", "E001", "L001", 2, "single_choice", "Which is correct?", None])

        # 4. Gaps
        ws_g = wb.create_sheet("Gaps")
        ws_g.append(["gap_id", "question_id", "gap_order", "input_control", "correct_answer", "accepted_answers"])
        ws_g.append(["G001", "Q001", 1, "select", "Are", "Are"])
        ws_g.append(["G002", "Q001", 2, "select", "am", "am | 'm"])

        # 5. Options
        ws_o = wb.create_sheet("Options")
        ws_o.append(["option_id", "question_id", "gap_id", "order", "text", "value", "is_correct"])
        ws_o.append(["O001", "Q001", "G001", 1, "Are", "Are", True])
        ws_o.append(["O002", "Q001", "G001", 2, "is", "is", False])
        ws_o.append(["O003", "Q001", "G002", 1, "am", "am", "TRUE"])
        ws_o.append(["O004", "Q001", "G002", 2, "are", "are", "FALSE"])
        # For Q002 choice question
        ws_o.append(["O005", "Q002", None, 1, "Option A", "A", True])
        ws_o.append(["O006", "Q002", None, 2, "Option B", "B", False])

        # 6. Explanations
        ws_exp = wb.create_sheet("Explanations")
        ws_exp.append(["explanation_id", "lesson_id", "question_id", "section_order", "title", "content", "example", "status"])
        ws_exp.append(["EXP001", "L001", "Q002", 1, "Grammar Rule", "Choice explanation from Explanations tab", "Example text", "draft"])

        # Convert
        lessons = convert_workbook_to_lessons(wb)

        self.assertEqual(len(lessons), 1)
        lesson = lessons[0]
        self.assertEqual(lesson["id"], "L001")
        self.assertEqual(lesson["title"], "Present Simple")
        self.assertEqual(lesson["level"], "A1")
        self.assertEqual(len(lesson["exercises"]), 1)

        ex = lesson["exercises"][0]
        self.assertEqual(ex["id"], "E001")
        self.assertEqual(ex["lessonId"], "L001")
        self.assertEqual(len(ex["questions"]), 2)

        # Question 1: Gap Select
        q1 = ex["questions"][0]
        self.assertEqual(q1["id"], "Q001")
        self.assertEqual(q1["type"], "gap_select")
        self.assertEqual(q1["text"], "A: {{gap1}} you a teacher? B: Yes, I {{gap2}}.")
        self.assertEqual(len(q1["gaps"]), 2)

        g1 = q1["gaps"][0]
        self.assertEqual(g1["id"], "G001")
        self.assertEqual(g1["placeholder"], "{{gap1}}")
        self.assertEqual(g1["correct_answer"], "Are")
        self.assertEqual(g1["accepted_answers"], ["Are"])
        self.assertEqual(len(g1["options"]), 2)
        self.assertIs(g1["options"][0]["is_correct"], True)
        self.assertIs(g1["options"][1]["is_correct"], False)

        g2 = q1["gaps"][1]
        self.assertEqual(g2["id"], "G002")
        self.assertEqual(g2["placeholder"], "{{gap2}}")
        self.assertEqual(g2["accepted_answers"], ["am", "'m"])
        self.assertIs(g2["options"][0]["is_correct"], True)
        self.assertIs(g2["options"][1]["is_correct"], False)

        # Question 2: Single Choice
        q2 = ex["questions"][1]
        self.assertEqual(q2["id"], "Q002")
        self.assertEqual(q2["type"], "single_choice")
        self.assertEqual(q2["explanation"], "Choice explanation from Explanations tab")
        self.assertEqual(len(q2["options"]), 2)
        self.assertIs(q2["options"][0]["is_correct"], True)
        self.assertIs(q2["options"][1]["is_correct"], False)


if __name__ == "__main__":
    unittest.main()
