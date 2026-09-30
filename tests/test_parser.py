import unittest
from pathlib import Path
from bs4 import BeautifulSoup
import sys

# Ensure pipeline is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from parser.test_english_parser import (
    clean_text,
    get_question_id,
    get_response_model,
    parse_gap,
    parse_question,
    parse_exercise,
    parse_lesson_from_html,
)


class TestEnglishParserUnit(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("  hello   world  "), "hello world")
        self.assertEqual(clean_text("word , punctuation !"), "word, punctuation!")
        self.assertEqual(clean_text(None), "")

    def test_get_response_model_radio(self):
        html = '<div class="watu-question"><input type="hidden" class="watupro-question-id" value="10" /><input type="hidden" id="answerType10" value="radio" /></div>'
        soup = BeautifulSoup(html, "html.parser").div
        self.assertEqual(get_response_model(soup), "single_choice")

    def test_get_response_model_checkbox(self):
        html = '<div class="watu-question"><input type="hidden" class="watupro-question-id" value="20" /><input type="hidden" id="answerType20" value="checkbox" /></div>'
        soup = BeautifulSoup(html, "html.parser").div
        self.assertEqual(get_response_model(soup), "multiple_choice")

    def test_get_response_model_gaps(self):
        html = '<div class="watu-question"><input type="hidden" class="watupro-question-id" value="30" /><input type="hidden" id="answerType30" value="gaps" /></div>'
        soup = BeautifulSoup(html, "html.parser").div
        self.assertEqual(get_response_model(soup), "gap")

    def test_parse_gap_select(self):
        html = '<select name="gap_1"><option value=""></option><option value="am">am</option><option value="is">is</option></select>'
        soup = BeautifulSoup(html, "html.parser").select_one("select")
        gap = parse_gap(soup, 1)
        self.assertEqual(gap["gap_id"], "gap_1")
        self.assertEqual(gap["input_control"], "select")
        self.assertEqual(gap["correct_answer"], None)
        self.assertEqual(len(gap["options"]), 2)
        self.assertIsNone(gap["options"][0]["is_correct"])

    def test_parse_multiple_choice_question(self):
        html = '''
        <div class="watu-question watupro-question-id-500">
            <input type="hidden" class="watupro-question-id" value="500" />
            <input type="hidden" id="answerType500" value="checkbox" />
            <div class="question-content">Choose TWO correct options: He _____ there.</div>
            <ul class="watu-options">
                <li><input type="checkbox" id="opt1" value="101" /><label for="opt1">was</label></li>
                <li><input type="checkbox" id="opt2" value="102" /><label for="opt2">has been</label></li>
                <li><input type="checkbox" id="opt3" value="103" /><label for="opt3">were</label></li>
            </ul>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser").select_one(".watu-question")
        q = parse_question(soup, 1)
        self.assertEqual(q["question_id"], "500")
        self.assertEqual(q["response_model"], "multiple_choice")
        self.assertEqual(len(q["options"]), 3)
        self.assertEqual(q["options"][0]["text"], "was")
        self.assertIsNone(q["options"][0]["is_correct"])

    def test_parse_lesson_from_html(self):
        html = '''
        <html>
        <head><title>Test Lesson - Test-English</title></head>
        <body>
            <form id="quiz-999">
                <div class="watu-question watupro-question-id-1">
                    <input type="hidden" class="watupro-question-id" value="1" />
                    <input type="hidden" id="answerType1" value="radio" />
                    <div class="question-content">Select correct: I _____ happy.</div>
                    <input type="radio" id="r1" value="am" /><label for="r1">am</label>
                    <input type="radio" id="r2" value="is" /><label for="r2">is</label>
                </div>
            </form>
        </body>
        </html>
        '''
        lesson = parse_lesson_from_html(html, source_file="sample.html", page=1)
        self.assertEqual(lesson["title"], "Test Lesson - Test-English")
        self.assertEqual(len(lesson["pages"]), 1)
        self.assertEqual(len(lesson["pages"][0]["exercises"]), 1)
        self.assertEqual(lesson["pages"][0]["exercises"][0]["exercise_id"], "quiz-999")
        self.assertEqual(len(lesson["pages"][0]["exercises"][0]["questions"]), 1)


if __name__ == "__main__":
    unittest.main()
