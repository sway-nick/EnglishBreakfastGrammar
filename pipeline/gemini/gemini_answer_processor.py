"""
gemini_answer_processor.py

Reads english_cms.xlsx, sends each exercise to Gemini API,
validates the response, and writes answers to english_cms_answered.xlsx.

NEVER modifies the original english_cms.xlsx.

Usage:
    python pipeline/gemini/gemini_answer_processor.py
    python pipeline/gemini/gemini_answer_processor.py --input custom.xlsx
    python pipeline/gemini/gemini_answer_processor.py --dry-run

Environment variables (from .env):
    GEMINI_API_KEY  - required
    GEMINI_MODEL    - optional, default: gemini-2.5-flash
    CMS_INPUT_FILE  - optional, default: C:\\Users\\user\\Desktop\\english_cms.xlsx
    CMS_OUTPUT_FILE - optional, default: C:\\Users\\user\\Desktop\\english_cms_answered.xlsx
    LOG_FILE        - optional, default: data/logs/gemini_processor.log
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

# ============================================================
# LOAD .env (before any other imports that may need the vars)
# ============================================================

def _load_dotenv(env_file: Path) -> None:
    """Minimal .env loader — no external dependency needed."""
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key   = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(Path(__file__).parents[2] / ".env")

# ============================================================
# THIRD-PARTY IMPORTS (after env load)
# ============================================================

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("ERROR: google-genai not installed.")
    print("Run: pip install google-genai")
    sys.exit(1)

try:
    from openpyxl import load_workbook
except ImportError:
    print("ERROR: openpyxl not installed.")
    print("Run: pip install openpyxl")
    sys.exit(1)

# ============================================================
# LOCAL IMPORTS
# ============================================================

from models import (
    ExerciseBatch,
    GapData,
    OptionData,
    QuestionData,
)
from prompt_builder import SYSTEM_PROMPT, build_prompt
from response_validator import validate
from excel_writer import write_results

# ============================================================
# CONFIG
# ============================================================

GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL    = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

DEFAULT_INPUT   = Path(r"C:\Users\user\Desktop\english_cms.xlsx")
DEFAULT_OUTPUT  = Path(r"C:\Users\user\Desktop\english_cms_answered.xlsx")
DEFAULT_LOG     = Path(__file__).parents[2] / "data" / "logs" / "gemini_processor.log"

# Delay between API calls (seconds) to stay within rate limits
API_CALL_DELAY  = 1.0

# Gemini response schema
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "gaps": {
            "type": "OBJECT",
            "description": (
                "Map of gap_id to correct answer text. "
                "For SELECT gaps: exact text of one of the options. "
                "For TEXT gaps: the primary correct answer."
            ),
        },
        "options": {
            "type": "OBJECT",
            "description": (
                "Map of option_id to boolean. "
                "True for correct option, false for incorrect. "
                "Only for SELECT gaps and single_choice questions."
            ),
        },
        "accepted_answers": {
            "type": "OBJECT",
            "description": (
                "Optional. Map of gap_id to list of all accepted answers. "
                "Only for TEXT gaps when multiple valid answers exist."
            ),
        },
    },
    "required": ["gaps", "options"],
}

# ============================================================
# LOGGING
# ============================================================

def _setup_logger(log_file: Path) -> logging.Logger:

    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("gemini_processor")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler — full detail
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler — INFO and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# ============================================================
# CMS LOADER
# ============================================================

def _norm(v) -> str:
    return str(v).strip() if v is not None else ""


def load_cms(input_file: Path) -> dict:
    """Loads all 6 sheets from the CMS Excel into plain dicts."""

    wb = load_workbook(input_file, data_only=True)

    def read_sheet(name: str) -> list[dict]:
        ws   = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        hdrs = [_norm(h) for h in rows[0]]
        return [dict(zip(hdrs, row)) for row in rows[1:]]

    return {
        "lessons":      read_sheet("Lessons"),
        "exercises":    read_sheet("Exercises"),
        "questions":    read_sheet("Questions"),
        "gaps":         read_sheet("Gaps"),
        "options":      read_sheet("Options"),
        "explanations": read_sheet("Explanations"),
    }


# ============================================================
# BATCH BUILDER
# ============================================================

def build_batches(cms: dict) -> list[ExerciseBatch]:
    """
    Groups CMS data into ExerciseBatch objects.
    One batch = one exercise.
    """

    # Index lookups
    lesson_map = {
        _norm(l["lesson_id"]): l
        for l in cms["lessons"]
        if _norm(l.get("lesson_id"))
    }

    gaps_by_q: dict[str, list[dict]] = defaultdict(list)
    for g in cms["gaps"]:
        qid = _norm(g.get("question_id"))
        if qid:
            gaps_by_q[qid].append(g)

    opts_by_gap: dict[str, list[dict]] = defaultdict(list)
    opts_by_q:   dict[str, list[dict]] = defaultdict(list)
    for o in cms["options"]:
        gid = _norm(o.get("gap_id"))
        qid = _norm(o.get("question_id"))
        if gid:
            opts_by_gap[gid].append(o)
        if qid:
            opts_by_q[qid].append(o)

    questions_by_ex: dict[str, list[dict]] = defaultdict(list)
    for q in cms["questions"]:
        eid = _norm(q.get("exercise_id"))
        if eid:
            questions_by_ex[eid].append(q)

    batches: list[ExerciseBatch] = []

    for ex in cms["exercises"]:

        eid     = _norm(ex.get("exercise_id"))
        lid     = _norm(ex.get("lesson_id"))
        lesson  = lesson_map.get(lid, {})

        ex_questions_raw = sorted(
            questions_by_ex.get(eid, []),
            key=lambda q: int(_norm(q.get("order")) or 0),
        )

        questions: list[QuestionData] = []

        for q_raw in ex_questions_raw:

            qid   = _norm(q_raw.get("question_id"))
            model = _norm(q_raw.get("response_model"))

            # ---- Build gaps ----
            gaps_raw = sorted(
                gaps_by_q.get(qid, []),
                key=lambda g: int(_norm(g.get("gap_order")) or 0),
            )

            gaps: list[GapData] = []

            for g_raw in gaps_raw:

                gid = _norm(g_raw.get("gap_id"))

                gap_opts_raw = sorted(
                    opts_by_gap.get(gid, []),
                    key=lambda o: int(_norm(o.get("order")) or 0),
                )

                gap_options = [
                    OptionData(
                        option_id=_norm(o.get("option_id")),
                        order=int(_norm(o.get("order")) or 0),
                        text=_norm(o.get("text")),
                    )
                    for o in gap_opts_raw
                ]

                # Q-P2: gap is "already filled" only if correct_answer
                # is non-empty and passes basic check
                ca = _norm(g_raw.get("correct_answer"))
                already_filled = bool(ca)

                gaps.append(GapData(
                    gap_id=gid,
                    gap_order=int(_norm(g_raw.get("gap_order")) or 0),
                    input_control=_norm(g_raw.get("input_control")),
                    options=gap_options,
                    already_filled=already_filled,
                ))

            # ---- Build question-level options (single_choice) ----
            sc_opts_raw = sorted(
                [
                    o for o in opts_by_q.get(qid, [])
                    if not _norm(o.get("gap_id"))
                ],
                key=lambda o: int(_norm(o.get("order")) or 0),
            )

            sc_options = [
                OptionData(
                    option_id=_norm(o.get("option_id")),
                    order=int(_norm(o.get("order")) or 0),
                    text=_norm(o.get("text")),
                )
                for o in sc_opts_raw
            ]

            questions.append(QuestionData(
                question_id=qid,
                order=int(_norm(q_raw.get("order")) or 0),
                response_model=model,
                content=_norm(q_raw.get("content")),
                gaps=gaps,
                options=sc_options,
            ))

        # ---- Build example ----
        ex_source = _norm(ex.get("example_source")) or None
        ex_target = _norm(ex.get("example_target")) or None

        batch = ExerciseBatch(
            lesson_title=_norm(lesson.get("title")),
            lesson_id=lid,
            exercise_id=eid,
            exercise_title=_norm(ex.get("title")),
            instruction=_norm(ex.get("instruction")),
            example_source=ex_source,
            example_target=ex_target,
            questions=questions,
        )

        batches.append(batch)

    return batches


# ============================================================
# GEMINI API CALL
# ============================================================

def call_gemini(
    client:  genai.Client,
    model:   str,
    prompt:  str,
    logger:  logging.Logger,
) -> dict | None:
    """
    Calls the Gemini API with structured output.
    Returns parsed dict or None on failure.
    """

    logger.debug(f"[PROMPT]\n{prompt}\n")

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=prompt)],
                )
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=RESPONSE_SCHEMA,
                temperature=0,   # deterministic — grammar has one correct answer
            ),
        )

        raw_text = response.text
        logger.debug(f"[GEMINI RESPONSE]\n{raw_text}\n")

        if hasattr(response, "usage_metadata") and response.usage_metadata:
            meta = response.usage_metadata
            logger.info(
                f"[USAGE] Prompt tokens: {getattr(meta, 'prompt_token_count', 'N/A')}, "
                f"Candidates tokens: {getattr(meta, 'candidates_token_count', 'N/A')}, "
                f"Total tokens: {getattr(meta, 'total_token_count', 'N/A')}"
            )

        parsed = json.loads(raw_text)
        return parsed

    except json.JSONDecodeError as e:
        logger.error(
            f"[API] JSON decode error: {e}\n"
            f"Raw response: {getattr(response, 'text', 'N/A')}"
        )
        return None

    except Exception as e:
        logger.error(f"[API] Gemini call failed: {e}")
        return None


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    # --------------------------------------------------------
    # Args
    # --------------------------------------------------------

    parser = argparse.ArgumentParser(
        description="Gemini Answer Processor for English CMS"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input CMS Excel file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output Excel file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help=f"Log file path (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build prompts and validate without calling Gemini or writing Excel",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of exercises/batches to process",
    )
    args = parser.parse_args()

    # --------------------------------------------------------
    # Logger
    # --------------------------------------------------------

    logger = _setup_logger(args.log)

    logger.info("=" * 70)
    logger.info("GEMINI ANSWER PROCESSOR")
    logger.info("=" * 70)
    logger.info(f"Input:   {args.input}")
    logger.info(f"Output:  {args.output}")
    logger.info(f"Model:   {GEMINI_MODEL}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("")

    # --------------------------------------------------------
    # Validate config
    # --------------------------------------------------------

    if not args.dry_run and not GEMINI_API_KEY:
        logger.error(
            "GEMINI_API_KEY not set. "
            "Add it to .env or set as environment variable."
        )
        sys.exit(1)

    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    # --------------------------------------------------------
    # Load CMS
    # --------------------------------------------------------

    logger.info("Loading CMS Excel...")
    cms = load_cms(args.input)

    logger.info(
        f"Loaded: {len(cms['lessons'])} lessons, "
        f"{len(cms['exercises'])} exercises, "
        f"{len(cms['questions'])} questions, "
        f"{len(cms['gaps'])} gaps, "
        f"{len(cms['options'])} options"
    )
    logger.info("")

    # --------------------------------------------------------
    # Build batches
    # --------------------------------------------------------

    batches = build_batches(cms)
    logger.info(f"Batches built: {len(batches)}")

    if args.limit and args.limit > 0:
        batches = batches[:args.limit]
        logger.info(f"Batches limited to first {len(batches)} batch(es)")

    # --------------------------------------------------------
    # Copy input → output (work on the copy)
    # --------------------------------------------------------

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.input, args.output)
        logger.info(f"Copied input to output: {args.output}")

        wb = load_workbook(args.output)

    # --------------------------------------------------------
    # Gemini client
    # --------------------------------------------------------

    if not args.dry_run:
        client = genai.Client(api_key=GEMINI_API_KEY)

    # --------------------------------------------------------
    # Process batches
    # --------------------------------------------------------

    stats = {
        "total":    len(batches),
        "skipped":  0,
        "processed": 0,
        "errors":   0,
        "gaps_written":    0,
        "options_written": 0,
    }

    for i, batch in enumerate(batches, start=1):

        logger.info(
            f"[{i}/{stats['total']}] Exercise: {batch.exercise_id} "
            f"| Lesson: {batch.lesson_id}"
        )

        # Q-P2: skip if already complete
        if batch.is_complete():
            logger.info(f"  SKIPPED (already filled)")
            stats["skipped"] += 1
            continue

        # Build prompt
        prompt = build_prompt(batch)

        if args.dry_run:
            logger.info(f"  DRY RUN -- prompt built ({len(prompt)} chars)")
            logger.debug(f"[PROMPT PREVIEW]\n{prompt[:500]}...")
            stats["processed"] += 1
            continue

        # Call Gemini
        raw = call_gemini(client, GEMINI_MODEL, prompt, logger)

        if raw is None:
            logger.error(
                f"  → ERROR: Gemini call returned None for {batch.exercise_id}"
            )
            stats["errors"] += 1
            time.sleep(API_CALL_DELAY)
            continue

        # Validate
        result = validate(raw, batch)

        if result.errors:
            for err in result.errors:
                logger.error(f"  [VALIDATION] {err}")

        if not result.questions:
            logger.error(
                f"  → ERROR: no valid questions in {batch.exercise_id} — skipping write"
            )
            stats["errors"] += 1
            time.sleep(API_CALL_DELAY)
            continue

        # Write to workbook
        g_written, o_written = write_results(result, wb, logger)

        stats["processed"]      += 1
        stats["gaps_written"]    += g_written
        stats["options_written"] += o_written

        logger.info(
            f"  → OK: {len(result.questions)} questions, "
            f"{g_written} gaps, {o_written} options written"
        )

        time.sleep(API_CALL_DELAY)

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    if not args.dry_run:
        wb.save(args.output)
        logger.info("")
        logger.info(f"Saved: {args.output}")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    logger.info("")
    logger.info("=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total batches:    {stats['total']}")
    logger.info(f"Processed:        {stats['processed']}")
    logger.info(f"Skipped:          {stats['skipped']}")
    logger.info(f"Errors:           {stats['errors']}")
    logger.info(f"Gaps written:     {stats['gaps_written']}")
    logger.info(f"Options written:  {stats['options_written']}")
    logger.info("=" * 70)

    if stats["errors"] > 0:
        logger.info(f"Completed with {stats['errors']} error(s). See log: {args.log}")
        sys.exit(1)
    else:
        logger.info("DONE — no errors.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
