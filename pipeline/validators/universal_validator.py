from pathlib import Path
import json
import re


INPUT_JSON = Path(
    r"C:\Users\user\Desktop\universal_lessons.json"
)


errors = []
warnings = []


def error(message):
    errors.append(message)


def warning(message):
    warnings.append(message)


def check_required(obj, fields, context):
    for field in fields:
        if field not in obj:
            error(
                f"{context}: missing field '{field}'"
            )


def validate_option(option, context):
    check_required(
        option,
        [
            "option_id",
            "order",
            "text",
            "value",
            "is_correct",
        ],
        context,
    )


def validate_gap(gap, context):
    check_required(
        gap,
        [
            "gap_id",
            "gap_order",
            "input_control",
            "options",
            "correct_answer",
            "accepted_answers",
        ],
        context,
    )

    if gap.get("input_control") not in {
        "select",
        "text",
    }:
        error(
            f"{context}: invalid input_control "
            f"'{gap.get('input_control')}'"
        )

    options = gap.get("options", [])

    if not isinstance(options, list):
        error(
            f"{context}: options must be a list"
        )
        return

    option_ids = set()

    for option_index, option in enumerate(
        options,
        start=1
    ):
        option_context = (
            f"{context}.options[{option_index}]"
        )

        if not isinstance(option, dict):
            error(
                f"{option_context}: "
                f"must be an object"
            )
            continue

        validate_option(
            option,
            option_context
        )

        option_id = option.get(
            "option_id"
        )

        if option_id:
            if option_id in option_ids:
                error(
                    f"{context}: duplicate "
                    f"option_id '{option_id}'"
                )
            option_ids.add(option_id)


def validate_question(
    question,
    context,
    global_question_ids,
    global_gap_ids,
):
    check_required(
        question,
        [
            "question_id",
            "order",
            "response_model",
            "content",
            "gaps",
            "options",
        ],
        context,
    )

    question_id = question.get(
        "question_id"
    )

    if not question_id:
        error(
            f"{context}: empty question_id"
        )
    else:
        if question_id in global_question_ids:
            error(
                f"{context}: duplicate "
                f"question_id '{question_id}'"
            )
        global_question_ids.add(
            question_id
        )

    response_model = question.get(
        "response_model"
    )

    allowed_models = {
        "gap",
        "single_choice",
    }

    if response_model not in allowed_models:
        error(
            f"{context}: invalid "
            f"response_model '{response_model}'"
        )

    content = question.get(
        "content"
    )

    if not isinstance(content, str):
        error(
            f"{context}: content must be a string"
        )
        content = ""

    gaps = question.get(
        "gaps",
        []
    )

    if not isinstance(gaps, list):
        error(
            f"{context}: gaps must be a list"
        )
        gaps = []

    options = question.get(
        "options",
        []
    )

    if not isinstance(options, list):
        error(
            f"{context}: options must be a list"
        )
        options = []

    # -------------------------------------------------
    # Check {{gap_X}} placeholders
    # -------------------------------------------------

    placeholders = re.findall(
        r"\{\{gap_(\d+)\}\}",
        content
    )

    placeholder_numbers = [
        int(number)
        for number in placeholders
    ]

    expected_numbers = list(
        range(
            1,
            len(gaps) + 1
        )
    )

    if placeholder_numbers != expected_numbers:
        error(
            f"{context}: gap placeholders "
            f"{placeholder_numbers} do not match "
            f"gaps {expected_numbers}"
        )

    # -------------------------------------------------
    # Check gaps
    # -------------------------------------------------

    gap_orders = set()

    for gap_index, gap in enumerate(
        gaps,
        start=1
    ):
        gap_context = (
            f"{context}.gaps[{gap_index}]"
        )

        if not isinstance(gap, dict):
            error(
                f"{gap_context}: "
                f"must be an object"
            )
            continue

        validate_gap(
            gap,
            gap_context
        )

        gap_order = gap.get(
            "gap_order"
        )

        if gap_order in gap_orders:
            error(
                f"{context}: duplicate "
                f"gap_order '{gap_order}'"
            )

        gap_orders.add(
            gap_order
        )

        gap_id = gap.get(
            "gap_id"
        )

        if not gap_id:
            error(
                f"{gap_context}: empty gap_id"
            )
        else:
            if gap_id in global_gap_ids:
                error(
                    f"{gap_context}: duplicate "
                    f"gap_id '{gap_id}'"
                )

            global_gap_ids.add(
                gap_id
            )

    # -------------------------------------------------
    # Check question-level options
    # -------------------------------------------------

    option_ids = set()

    for option_index, option in enumerate(
        options,
        start=1
    ):
        option_context = (
            f"{context}.options[{option_index}]"
        )

        if not isinstance(option, dict):
            error(
                f"{option_context}: "
                f"must be an object"
            )
            continue

        validate_option(
            option,
            option_context
        )

        option_id = option.get(
            "option_id"
        )

        if option_id:
            if option_id in option_ids:
                error(
                    f"{context}: duplicate "
                    f"option_id '{option_id}'"
                )

            option_ids.add(
                option_id
            )

    # -------------------------------------------------
    # Response model consistency
    # -------------------------------------------------

    if response_model == "single_choice":
        if len(gaps) != 0:
            error(
                f"{context}: "
                f"single_choice question "
                f"must not contain gaps"
            )

        if len(options) == 0:
            warning(
                f"{context}: "
                f"single_choice has no options"
            )

    if response_model == "gap":
        if len(gaps) == 0:
            error(
                f"{context}: "
                f"gap question has no gaps"
            )


def validate_exercise(
    exercise,
    context,
    expected_page,
    global_question_ids,
    global_gap_ids,
):
    check_required(
        exercise,
        [
            "exercise_id",
            "page",
            "order",
            "title",
            "instruction",
            "example",
            "questions",
        ],
        context,
    )

    exercise_page = exercise.get(
        "page"
    )

    if exercise_page != expected_page:
        error(
            f"{context}: exercise page "
            f"{exercise_page} != "
            f"parent page {expected_page}"
        )

    questions = exercise.get(
        "questions",
        []
    )

    if not isinstance(questions, list):
        error(
            f"{context}: questions "
            f"must be a list"
        )
        return

    if len(questions) == 0:
        warning(
            f"{context}: exercise "
            f"contains no questions"
        )

    question_orders = set()

    for question_index, question in enumerate(
        questions,
        start=1
    ):
        question_context = (
            f"{context}.questions[{question_index}]"
        )

        if not isinstance(question, dict):
            error(
                f"{question_context}: "
                f"must be an object"
            )
            continue

        validate_question(
            question,
            question_context,
            global_question_ids,
            global_gap_ids,
        )

        question_order = question.get(
            "order"
        )

        if question_order in question_orders:
            error(
                f"{context}: duplicate "
                f"question order "
                f"'{question_order}'"
            )

        question_orders.add(
            question_order
        )


def validate_page(
    page,
    lesson_context,
    expected_page,
    global_question_ids,
    global_gap_ids,
):
    page_context = (
        f"{lesson_context}.pages[{expected_page}]"
    )

    check_required(
        page,
        [
            "page",
            "source_file",
            "exercises",
        ],
        page_context,
    )

    actual_page = page.get(
        "page"
    )

    if actual_page != expected_page:
        error(
            f"{page_context}: page "
            f"{actual_page} != "
            f"expected {expected_page}"
        )

    source_file = page.get(
        "source_file"
    )

    if not source_file:
        error(
            f"{page_context}: "
            f"empty source_file"
        )

    exercises = page.get(
        "exercises",
        []
    )

    if not isinstance(exercises, list):
        error(
            f"{page_context}: exercises "
            f"must be a list"
        )
        return

    if len(exercises) == 0:
        warning(
            f"{page_context}: "
            f"page contains no exercises"
        )

    exercise_orders = set()

    for exercise_index, exercise in enumerate(
        exercises,
        start=1
    ):
        exercise_context = (
            f"{page_context}.exercises"
            f"[{exercise_index}]"
        )

        if not isinstance(exercise, dict):
            error(
                f"{exercise_context}: "
                f"must be an object"
            )
            continue

        validate_exercise(
            exercise,
            exercise_context,
            expected_page,
            global_question_ids,
            global_gap_ids,
        )

        exercise_order = exercise.get(
            "order"
        )

        if exercise_order in exercise_orders:
            error(
                f"{page_context}: duplicate "
                f"exercise order "
                f"'{exercise_order}'"
            )

        exercise_orders.add(
            exercise_order
        )


def validate_lesson(
    lesson,
    lesson_index,
    global_question_ids,
    global_gap_ids,
):
    context = (
        f"lessons[{lesson_index}]"
    )

    check_required(
        lesson,
        [
            "lesson_id",
            "title",
            "level",
            "topic",
            "status",
            "pages",
            "explanation",
            "media",
            "source",
        ],
        context,
    )

    if not lesson.get("lesson_id"):
        error(
            f"{context}: empty lesson_id"
        )

    if not lesson.get("title"):
        error(
            f"{context}: empty title"
        )

    pages = lesson.get(
        "pages",
        []
    )

    if not isinstance(pages, list):
        error(
            f"{context}: pages must be a list"
        )
        return

    if len(pages) == 0:
        error(
            f"{context}: lesson has no pages"
        )

    expected_page = 1

    for page in pages:
        if not isinstance(page, dict):
            error(
                f"{context}: page must "
                f"be an object"
            )
            continue

        validate_page(
            page,
            context,
            expected_page,
            global_question_ids,
            global_gap_ids,
        )

        expected_page += 1

    # -------------------------------------------------
    # Source validation
    # -------------------------------------------------

    source = lesson.get(
        "source"
    )

    if isinstance(source, dict):
        pages_collected = source.get(
            "pages_collected"
        )

        if pages_collected != len(pages):
            error(
                f"{context}: source.pages_collected "
                f"{pages_collected} != "
                f"actual pages {len(pages)}"
            )

        source_files = source.get(
            "source_files",
            []
        )

        if not isinstance(
            source_files,
            list
        ):
            error(
                f"{context}: "
                f"source.source_files "
                f"must be a list"
            )
        else:
            actual_files = [
                page.get(
                    "source_file"
                )
                for page in pages
            ]

            if source_files != actual_files:
                error(
                    f"{context}: "
                    f"source.source_files "
                    f"do not match page "
                    f"source_file values"
                )


def main():
    print("=" * 70)
    print("UNIVERSAL JSON VALIDATOR")
    print("=" * 70)

    if not INPUT_JSON.exists():
        print()
        print(
            f"ERROR: file not found:"
        )
        print(
            INPUT_JSON
        )
        return

    try:
        with INPUT_JSON.open(
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

    except json.JSONDecodeError as e:
        print()
        print(
            "ERROR: invalid JSON"
        )
        print(
            f"Line: {e.lineno}"
        )
        print(
            f"Column: {e.colno}"
        )
        print(
            e.msg
        )
        return

    except Exception as e:
        print()
        print(
            "ERROR while reading JSON:"
        )
        print(
            e
        )
        return

    # -------------------------------------------------
    # Root validation
    # -------------------------------------------------

    if not isinstance(data, dict):
        error(
            "Root JSON must be an object"
        )

    else:
        check_required(
            data,
            [
                "version",
                "provider",
                "lessons",
            ],
            "root",
        )

        if data.get("version") != "1.0":
            warning(
                "root: unexpected version "
                f"'{data.get('version')}'"
            )

        lessons = data.get(
            "lessons",
            []
        )

        if not isinstance(
            lessons,
            list
        ):
            error(
                "root.lessons must be a list"
            )
            lessons = []

        global_lesson_ids = set()
        global_question_ids = set()
        global_gap_ids = set()

        for lesson_index, lesson in enumerate(
            lessons,
            start=1
        ):
            if not isinstance(
                lesson,
                dict
            ):
                error(
                    f"lessons[{lesson_index}] "
                    f"must be an object"
                )
                continue

            lesson_id = lesson.get(
                "lesson_id"
            )

            if lesson_id:
                if lesson_id in global_lesson_ids:
                    error(
                        f"Duplicate lesson_id "
                        f"'{lesson_id}'"
                    )

                global_lesson_ids.add(
                    lesson_id
                )

            validate_lesson(
                lesson,
                lesson_index,
                global_question_ids,
                global_gap_ids,
            )

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    lessons_count = 0
    pages_count = 0
    exercises_count = 0
    questions_count = 0
    gaps_count = 0
    options_count = 0

    if isinstance(data, dict):
        lessons = data.get(
            "lessons",
            []
        )

        if isinstance(
            lessons,
            list
        ):
            lessons_count = len(
                lessons
            )

            for lesson in lessons:
                if not isinstance(
                    lesson,
                    dict
                ):
                    continue

                pages = lesson.get(
                    "pages",
                    []
                )

                if not isinstance(
                    pages,
                    list
                ):
                    continue

                pages_count += len(
                    pages
                )

                for page in pages:
                    if not isinstance(
                        page,
                        dict
                    ):
                        continue

                    exercises = page.get(
                        "exercises",
                        []
                    )

                    if not isinstance(
                        exercises,
                        list
                    ):
                        continue

                    exercises_count += len(
                        exercises
                    )

                    for exercise in exercises:
                        if not isinstance(
                            exercise,
                            dict
                        ):
                            continue

                        questions = exercise.get(
                            "questions",
                            []
                        )

                        if not isinstance(
                            questions,
                            list
                        ):
                            continue

                        questions_count += len(
                            questions
                        )

                        for question in questions:
                            if not isinstance(
                                question,
                                dict
                            ):
                                continue

                            gaps = question.get(
                                "gaps",
                                []
                            )

                            if isinstance(
                                gaps,
                                list
                            ):
                                gaps_count += len(
                                    gaps
                                )

                                for gap in gaps:
                                    if not isinstance(
                                        gap,
                                        dict
                                    ):
                                        continue

                                    options = gap.get(
                                        "options",
                                        []
                                    )

                                    if isinstance(
                                        options,
                                        list
                                    ):
                                        options_count += len(
                                            options
                                        )

                            options = question.get(
                                "options",
                                []
                            )

                            if isinstance(
                                options,
                                list
                            ):
                                options_count += len(
                                    options
                                )

    # -------------------------------------------------
    # Final report
    # -------------------------------------------------

    print()
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)

    print(
        f"Lessons:    {lessons_count}"
    )
    print(
        f"Pages:      {pages_count}"
    )
    print(
        f"Exercises:  {exercises_count}"
    )
    print(
        f"Questions:  {questions_count}"
    )
    print(
        f"Gaps:       {gaps_count}"
    )
    print(
        f"Options:    {options_count}"
    )

    print()
    print("=" * 70)
    print("VALIDATION RESULT")
    print("=" * 70)

    print(
        f"Errors:   {len(errors)}"
    )
    print(
        f"Warnings: {len(warnings)}"
    )

    if errors:
        print()
        print("ERRORS:")
        print("-" * 70)

        for index, message in enumerate(
            errors,
            start=1
        ):
            print(
                f"{index}. {message}"
            )

    if warnings:
        print()
        print("WARNINGS:")
        print("-" * 70)

        for index, message in enumerate(
            warnings,
            start=1
        ):
            print(
                f"{index}. {message}"
            )

    print()
    print("=" * 70)

    if errors:
        print(
            "VALIDATION FAILED"
        )
    else:
        print(
            "VALIDATION PASSED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()