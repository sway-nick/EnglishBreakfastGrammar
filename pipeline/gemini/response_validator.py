from __future__ import annotations

from models import (
    ExerciseBatch,
    GapData,
    OptionData,
    QuestionData,
    ValidatedGap,
    ValidatedOption,
    ValidatedQuestion,
    ValidationResult,
)


# ============================================================
# RESPONSE VALIDATOR
# ============================================================

def validate(
    raw: dict,
    batch: ExerciseBatch,
) -> ValidationResult:
    """
    Validates the raw Gemini JSON response against the batch.

    Per-question validation rules:

    SELECT gap:
      - correct_answer must exist in gap.options[*].text (exact match)
      - exactly one option.is_correct == True per gap
      - winning option text must equal correct_answer

    TEXT gap:
      - correct_answer must be non-empty string
      - accepted_answers must be non-empty list
      - correct_answer must be contained in accepted_answers

    SINGLE_CHOICE:
      - exactly one question-level option.is_correct == True
      - gaps are not touched (must be empty)

    Returns ValidationResult with ok=True and validated questions,
    or ok=False with error list. Failed questions do NOT prevent
    other questions from being validated (per-question isolation).
    """

    raw_gaps    = raw.get("gaps",    {})
    raw_options = raw.get("options", {})

    validated_questions: list[ValidatedQuestion] = []
    result_errors:       list[str]               = []
    all_ok = True

    for q in batch.questions:

        q_errors: list[str] = []
        v_gaps:   list[ValidatedGap]   = []
        v_options: list[ValidatedOption] = []

        # ====================================================
        # GAP QUESTION
        # ====================================================

        if q.response_model == "gap":

            for gap in q.gaps:

                gid = gap.gap_id

                # ------ Check gap_id present in response ------

                if gid not in raw_gaps:
                    q_errors.append(
                        f"Q{q.question_id}: gap_id '{gid}' "
                        f"missing from Gemini response"
                    )
                    continue

                correct_answer = raw_gaps[gid]

                # ---- SELECT ----

                if gap.input_control == "select":

                    option_texts = [o.text for o in gap.options]

                    # Rule 1: correct_answer in option texts (exact)
                    if correct_answer not in option_texts:
                        q_errors.append(
                            f"Q{q.question_id} gap '{gid}': "
                            f"Gemini answer '{correct_answer}' not found in "
                            f"options {option_texts}"
                        )
                        continue

                    # Rule 2: collect is_correct from raw options
                    true_options: list[str] = []

                    for o in gap.options:
                        raw_val = raw_options.get(o.option_id)
                        if raw_val is True:
                            true_options.append(o.option_id)

                    if len(true_options) != 1:
                        q_errors.append(
                            f"Q{q.question_id} gap '{gid}': "
                            f"expected exactly 1 correct option, "
                            f"got {len(true_options)}: {true_options}"
                        )
                        continue

                    # Rule 3: winning option text must equal correct_answer
                    winning_id   = true_options[0]
                    winning_text = next(
                        o.text for o in gap.options
                        if o.option_id == winning_id
                    )

                    if winning_text != correct_answer:
                        q_errors.append(
                            f"Q{q.question_id} gap '{gid}': "
                            f"gaps answer '{correct_answer}' does not match "
                            f"winning option text '{winning_text}'"
                        )
                        continue

                    # ✅ SELECT gap OK
                    v_gaps.append(ValidatedGap(
                        gap_id=gid,
                        correct_answer=correct_answer,
                        accepted_answers=[correct_answer],
                    ))

                    for o in gap.options:
                        v_options.append(ValidatedOption(
                            option_id=o.option_id,
                            is_correct=(o.option_id == winning_id),
                        ))

                # ---- TEXT ----

                elif gap.input_control == "text":

                    # Rule 1: non-empty correct_answer
                    if not isinstance(correct_answer, str) or not correct_answer.strip():
                        q_errors.append(
                            f"Q{q.question_id} gap '{gid}': "
                            f"empty correct_answer for text gap"
                        )
                        continue

                    correct_answer = correct_answer.strip()

                    # Build accepted_answers — Gemini may return a list
                    # under the same gap_id key, or just a string.
                    # We normalise here: always a list including correct_answer.
                    raw_accepted = raw.get("accepted_answers", {}).get(gid)

                    if isinstance(raw_accepted, list):
                        accepted = [
                            str(a).strip()
                            for a in raw_accepted
                            if str(a).strip()
                        ]
                    elif isinstance(raw_accepted, str) and raw_accepted.strip():
                        accepted = [
                            s.strip()
                            for s in raw_accepted.split("|")
                            if s.strip()
                        ]
                    else:
                        accepted = []

                    # Ensure correct_answer is in accepted_answers
                    if correct_answer not in accepted:
                        accepted.insert(0, correct_answer)

                    if not accepted:
                        q_errors.append(
                            f"Q{q.question_id} gap '{gid}': "
                            f"accepted_answers is empty"
                        )
                        continue

                    # ✅ TEXT gap OK
                    v_gaps.append(ValidatedGap(
                        gap_id=gid,
                        correct_answer=correct_answer,
                        accepted_answers=accepted,
                    ))
                    # TEXT gaps have no options — nothing to write

        # ====================================================
        # SINGLE_CHOICE QUESTION
        # ====================================================

        elif q.response_model == "single_choice":

            option_ids = [o.option_id for o in q.options]

            true_options = [
                oid for oid in option_ids
                if raw_options.get(oid) is True
            ]

            if len(true_options) != 1:
                q_errors.append(
                    f"Q{q.question_id} single_choice: "
                    f"expected exactly 1 correct option, "
                    f"got {len(true_options)}: {true_options}"
                )

            else:
                # ✅ SINGLE_CHOICE OK
                winning_id = true_options[0]
                for o in q.options:
                    v_options.append(ValidatedOption(
                        option_id=o.option_id,
                        is_correct=(o.option_id == winning_id),
                    ))

        # ====================================================
        # COLLECT QUESTION RESULT
        # ====================================================

        if q_errors:
            all_ok = False
            result_errors.extend(q_errors)
            # Do NOT add this question to validated list
        else:
            validated_questions.append(ValidatedQuestion(
                question_id=q.question_id,
                gaps=v_gaps,
                options=v_options,
            ))

    return ValidationResult(
        exercise_id=batch.exercise_id,
        ok=all_ok and bool(validated_questions),
        questions=validated_questions,
        errors=result_errors,
    )
