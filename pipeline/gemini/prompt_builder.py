from __future__ import annotations

from models import ExerciseBatch, GapData, OptionData, QuestionData


# ============================================================
# PROMPT BUILDER
# ============================================================

SYSTEM_PROMPT = """\
You are an English grammar answer key generator.
Your task is to identify the correct answers for a grammar exercise.
Do NOT add explanations. Return ONLY the JSON object.\
"""


def build_prompt(batch: ExerciseBatch) -> str:
    """
    Builds a prompt string for one exercise batch.
    The prompt contains lesson/exercise context plus all questions,
    gaps, and options needed for Gemini to determine correct answers.

    Rules stated in the prompt:
    - SELECT gaps: answer must be exact text of one of the listed options.
    - TEXT gaps: return all grammatically valid answers for this specific task.
    - SINGLE_CHOICE: exactly one option must be correct.
    - Preserve original capitalization for SELECT/SINGLE_CHOICE.
    """

    lines = []

    # --------------------------------------------------------
    # CONTEXT HEADER
    # --------------------------------------------------------

    lines.append("=" * 60)
    lines.append(f"LESSON: {batch.lesson_title}")
    lines.append(f"EXERCISE: {batch.exercise_id}")

    if batch.exercise_title:
        lines.append(f"TITLE: {batch.exercise_title}")

    if batch.instruction:
        lines.append(f"INSTRUCTION: {batch.instruction}")

    if batch.example_source:
        if batch.example_target:
            lines.append(
                f"EXAMPLE: {batch.example_source} → {batch.example_target}"
            )
        else:
            lines.append(f"EXAMPLE: {batch.example_source}")

    lines.append("=" * 60)
    lines.append("")

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    lines.append("QUESTIONS:")
    lines.append("")

    for q in batch.questions:

        lines.append(
            f"[Q{q.question_id}] \"{q.content}\""
        )

        # ---- GAP question ----
        if q.response_model == "gap":

            for gap in q.gaps:

                if gap.input_control == "select":

                    options_str = " | ".join(
                        f'"{o.text}"'
                        for o in gap.options
                    )
                    lines.append(
                        f"  {gap.gap_id} [SELECT] → options: {options_str}"
                    )

                elif gap.input_control == "text":

                    lines.append(
                        f"  {gap.gap_id} [TEXT] → free input"
                    )

        # ---- SINGLE_CHOICE question ----
        elif q.response_model == "single_choice":

            options_str = " | ".join(
                f'"{o.text}"'
                for o in q.options
            )
            lines.append(
                f"  [SINGLE_CHOICE] → options: {options_str}"
            )
            # Expose individual option IDs for the response
            for o in q.options:
                lines.append(
                    f"    {o.option_id}: \"{o.text}\""
                )

        lines.append("")

    # --------------------------------------------------------
    # RULES
    # --------------------------------------------------------

    lines.append("=" * 60)
    lines.append("RULES:")
    lines.append(
        "1. SELECT gaps: correct_answer MUST exactly match one of "
        "the listed option texts, preserving capitalization."
    )
    lines.append(
        "2. TEXT gaps: return all grammatically valid answers that "
        "fit the specific blank in this sentence. Do not invent "
        "alternative phrasings that change the sentence structure."
    )
    lines.append(
        "3. SINGLE_CHOICE: exactly one option must be correct."
    )
    lines.append(
        "4. For SELECT and SINGLE_CHOICE: set true for the correct "
        "option_id in \"options\", false for all others."
    )
    lines.append(
        "5. For TEXT gaps: leave \"options\" empty for those gaps."
    )
    lines.append(
        "6. Every gap_id in this exercise must appear in \"gaps\"."
    )
    lines.append("=" * 60)

    return "\n".join(lines)
