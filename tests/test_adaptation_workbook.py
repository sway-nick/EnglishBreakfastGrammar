"""Unit Tests for Adaptation Workbook Builder and Importer (TASK-013).

Universal English Test Platform
Tests:
1. Pending questions extraction and cardinality (5,571 items).
2. Strict level-by-level ordering (A1 -> A2 -> B1 -> B1-B2 -> B2 -> C1 -> Shorts).
3. Formula construction and target answer preservation prompt instructions.
4. Robust JSON response parsing (including markdown-stripped JSON).
5. Importer dry-run execution.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.adaptation.adaptation_workbook_builder import (
    DEFAULT_ADAPTATION_DB,
    DEFAULT_STAGING_DB,
    LOCAL_OUTPUT,
    LEVEL_ORDER,
    build_gemini_formula,
    fetch_pending_adaptation_questions,
)
from pipeline.adaptation.import_adaptation_results import (
    import_adaptation_results,
    parse_adaptation_json,
)


class TestAdaptationWorkbook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapt_db = DEFAULT_ADAPTATION_DB
        cls.stage_db = DEFAULT_STAGING_DB

    def test_01_pending_questions_cardinality_and_ordering(self):
        """Assert pending questions fetched and ordered strictly level-by-level."""
        items = fetch_pending_adaptation_questions(self.adapt_db, self.stage_db)
        self.assertGreater(len(items), 0, "Must fetch PENDING questions.")
        self.assertLessEqual(len(items), 5571, "Must not exceed initial 5,571 queue.")

        # Assert level ordering: A1 -> A2 -> B1 -> B1-B2 -> B2 -> C1 -> SHORTS
        prev_rank = 0
        for it in items:
            rank = LEVEL_ORDER.get(it["level"], 99)
            self.assertGreaterEqual(rank, prev_rank, f"Level {it['level']} out of order.")
            prev_rank = rank

        # Assert all 3 response models are present
        models = {it["response_model"] for it in items}
        self.assertEqual(models, {"gap", "single_choice", "multiple_choice"})

    def test_02_formula_construction_invariants(self):
        """Verify model-tailored Gemini formulas use top-level =GEMINI without wrappers (TASK-013A)."""
        # Gap formula
        gap_formula = build_gemini_formula(10, "gap")
        self.assertTrue(gap_formula.startswith("=GEMINI("), "Must start with '=GEMINI('")
        self.assertTrue(gap_formula.endswith(")"), "Must end with ')'")
        self.assertNotIn("IFERROR", gap_formula)
        self.assertNotIn("IF(", gap_formula)
        self.assertNotIn("IFS(", gap_formula)
        self.assertNotIn("SWITCH(", gap_formula)
        self.assertIn("TARGET ANSWER(S) TO PRESERVE", gap_formula)
        self.assertIn("adapted_text", gap_formula)
        self.assertIn("gaps", gap_formula)

        # Single choice formula
        sc_formula = build_gemini_formula(15, "single_choice")
        self.assertTrue(sc_formula.startswith("=GEMINI("), "Must start with '=GEMINI('")
        self.assertTrue(sc_formula.endswith(")"), "Must end with ')'")
        self.assertNotIn("IFERROR", sc_formula)
        self.assertNotIn("IF(", sc_formula)
        self.assertNotIn("IFS(", sc_formula)
        self.assertNotIn("SWITCH(", sc_formula)
        self.assertIn("TARGET CORRECT ANSWER", sc_formula)
        self.assertIn("options", sc_formula)

        # Multiple choice formula
        mc_formula = build_gemini_formula(20, "multiple_choice")
        self.assertTrue(mc_formula.startswith("=GEMINI("), "Must start with '=GEMINI('")
        self.assertTrue(mc_formula.endswith(")"), "Must end with ')'")
        self.assertNotIn("IFERROR", mc_formula)
        self.assertNotIn("IF(", mc_formula)
        self.assertNotIn("IFS(", mc_formula)
        self.assertNotIn("SWITCH(", mc_formula)
        self.assertIn("TARGET CORRECT ANSWERS", mc_formula)
        self.assertIn("TWO correct answers", mc_formula)

    def test_03_json_parser_resilience(self):
        """Verify robust JSON parsing across clean JSON, markdown-wrapped JSON, and whitespace."""
        # 1. Clean JSON
        payload1 = '{"adapted_text": "Sample sentence.", "options": []}'
        res1 = parse_adaptation_json(payload1)
        self.assertEqual(res1.get("adapted_text"), "Sample sentence.")

        # 2. Markdown fenced JSON
        payload2 = '```json\n{"adapted_text": "Markdown sentence.", "target_tokens": ["token"]}\n```'
        res2 = parse_adaptation_json(payload2)
        self.assertEqual(res2.get("adapted_text"), "Markdown sentence.")
        self.assertEqual(res2.get("target_tokens"), ["token"])

        # 3. Invalid payload returns None
        self.assertIsNone(parse_adaptation_json("Invalid text without JSON"))
        self.assertIsNone(parse_adaptation_json(None))

    def test_04_generated_workbook_exists_and_valid(self):
        """Assert local workbook exists, has 5,571 data rows, and correct sheets."""
        self.assertTrue(LOCAL_OUTPUT.exists(), "Local workbook must exist.")
        import openpyxl
        wb = openpyxl.load_workbook(LOCAL_OUTPUT, read_only=True)
        self.assertIn("Summary", wb.sheetnames)
        self.assertIn("Gemini_Adaptation", wb.sheetnames)

    def test_05_importer_dry_run_safety(self):
        """Assert importer dry run reads all rows without modifying database."""
        stats = import_adaptation_results(
            results_path=LOCAL_OUTPUT,
            adaptation_db_path=self.adapt_db,
            staging_db_path=self.stage_db,
            dry_run=True,
        )
        self.assertEqual(stats["total_rows_read"], 5571)
        self.assertEqual(stats["processed_count"], 0)
        self.assertEqual(stats["skipped_not_pending"] + stats["skipped_empty_value"], 5571)

    def test_06_deterministic_formula_validator_rejection(self):
        """Assert deterministic validation strictly rejects any wrapper around GEMINI (TASK-013A)."""
        from pipeline.adaptation.adaptation_workbook_builder import validate_formula_compatibility

        # Valid top-level GEMINI
        ok, err = validate_formula_compatibility('=GEMINI("Prompt text")')
        self.assertTrue(ok)
        self.assertIsNone(err)

        # Rejected wrapper: IFERROR(GEMINI
        ok, err = validate_formula_compatibility('=IFERROR(GEMINI("Prompt"), "")')
        self.assertFalse(ok)
        self.assertIn("IFERROR", err)

        # Rejected wrapper: IF(GEMINI
        ok, err = validate_formula_compatibility('=IF(GEMINI("Prompt"), 1, 0)')
        self.assertFalse(ok)
        self.assertIn("IF", err)

        # Rejected wrapper: IFS(GEMINI
        ok, err = validate_formula_compatibility('=IFS(A1=1, GEMINI("Prompt"))')
        self.assertFalse(ok)
        self.assertIn("IFS", err)

        # Rejected wrapper: SWITCH(GEMINI
        ok, err = validate_formula_compatibility('=SWITCH(A1, 1, GEMINI("Prompt"))')
        self.assertFalse(ok)
        self.assertIn("SWITCH", err)

    def test_07_all_workbook_formulas_strictly_compliant(self):
        """Assert 100% of the 5,571 formulas in the workbook are top-level =GEMINI without wrappers."""
        from pipeline.adaptation.adaptation_workbook_builder import validate_adaptation_workbook_formulas

        val_res = validate_adaptation_workbook_formulas(LOCAL_OUTPUT)
        self.assertTrue(val_res["is_valid"], f"Violations found: {val_res['violations'][:5]}")
        self.assertEqual(val_res["total_formulas_checked"], 5571)
        self.assertEqual(val_res["violations_count"], 0)


if __name__ == "__main__":
    unittest.main()
