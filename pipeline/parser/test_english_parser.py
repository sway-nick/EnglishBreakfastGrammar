from pathlib import Path
import json
import re
import sys

from bs4 import BeautifulSoup


# ============================================================
# НАСТРОЙКИ
# ============================================================

INPUT_FILE = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path(r"C:\Users\user\Desktop\6.txt")
)

OUTPUT_FILE = Path(
    r"C:\Users\user\Desktop\parsed_lesson.json"
)


# ============================================================
# UTF-8
# ============================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    return text


def get_question_id(question):
    hidden = question.select_one(
        "input.watupro-question-id"
    )

    if hidden and hidden.get("value"):
        return hidden.get("value")

    wrapper = question.select_one(
        "[class*='watupro-question-id-']"
    )

    if wrapper:
        classes = wrapper.get("class", [])

        for cls in classes:
            match = re.search(
                r"watupro-question-id-(\d+)",
                cls
            )

            if match:
                return match.group(1)

    return None


def get_response_model(question):
    question_id = get_question_id(question)

    if question_id:

        answer_type = question.select_one(
            f"#answerType{question_id}"
        )

        if answer_type:

            value = answer_type.get(
                "value",
                ""
            ).lower()

            if value == "radio":
                return "single_choice"

            if value == "gaps":
                return "gap"

    if question.select_one(
        "input[type='radio']"
    ):
        return "single_choice"

    if question.select_one(
        "select.watupro-gap, "
        "input.watupro-gap, "
        "textarea.watupro-gap"
    ):
        return "gap"

    return "unknown"


# ============================================================
# GAP
# ============================================================

def parse_gap(gap_element, gap_order):

    tag_name = gap_element.name

    gap_id = (
        gap_element.get("name")
        or gap_element.get("id")
        or f"gap_{gap_order}"
    )

    gap = {
        "gap_id": gap_id,
        "gap_order": gap_order,
        "input_control": (
            "select"
            if tag_name == "select"
            else "text"
        ),
        "options": [],
        "correct_answer": None,
        "accepted_answers": []
    }

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    if tag_name == "select":

        options = gap_element.select(
            "option"
        )

        real_option_order = 0

        for option in options:

            text = clean_text(
                option.get_text(
                    " ",
                    strip=True
                )
            )

            value = (
                option.get("value")
                or text
            )

            value = clean_text(value)

            # ------------------------------------------------
            # ИСПРАВЛЕНИЕ
            #
            # Пустой option вида:
            # <option value=""></option>
            #
            # является placeholder, а не реальным
            # вариантом ответа.
            # ------------------------------------------------

            if not text and not value:
                continue

            real_option_order += 1

            # Correct answers are intentionally not inferred.
            is_correct = None

            option_data = {
                "option_id": (
                    f"{gap_id}_{real_option_order}"
                ),
                "order": real_option_order,
                "text": text,
                "value": value,
                "is_correct": is_correct
            }

            gap["options"].append(
                option_data
            )

        return gap

    # --------------------------------------------------------
    # INPUT / TEXTAREA
    # --------------------------------------------------------

    if tag_name in (
        "input",
        "textarea"
    ):

        # Do not use current HTML value as answer key.
        value = ""

        return gap

    return gap


# ============================================================
# QUESTION
# ============================================================

def parse_question(question, order):

    question_id = get_question_id(
        question
    )

    response_model = get_response_model(
        question
    )

    content_block = question.select_one(
        ".question-content"
    )

    if content_block is None:
        content_block = question

    clone = BeautifulSoup(
        str(content_block),
        "html.parser"
    )

    # --------------------------------------------------------
    # Удаляем служебные элементы
    # --------------------------------------------------------

    for element in clone.select(
        "input[type='hidden'], "
        "input.answerTypeCnt1"
    ):
        element.decompose()

    # --------------------------------------------------------
    # GAPS
    # --------------------------------------------------------

    gaps = []

    gap_elements = question.select(
        "select.watupro-gap, "
        "input.watupro-gap, "
        "textarea.watupro-gap"
    )

    for gap_order, gap_element in enumerate(
        gap_elements,
        start=1
    ):

        gaps.append(
            parse_gap(
                gap_element,
                gap_order
            )
        )

    # --------------------------------------------------------
    # PLACEHOLDERS
    # --------------------------------------------------------

    clone_gap_elements = clone.select(
        "select.watupro-gap, "
        "input.watupro-gap, "
        "textarea.watupro-gap"
    )

    for gap_order, gap_element in enumerate(
        clone_gap_elements,
        start=1
    ):

        gap_element.replace_with(
            f"{{{{gap_{gap_order}}}}}"
        )

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    content = clean_text(
        clone.get_text(
            " ",
            strip=True
        )
    )

    # --------------------------------------------------------
    # RADIO OPTIONS
    # --------------------------------------------------------

    options = []

    if response_model == "single_choice":

        radio_inputs = question.select(
            "input[type='radio']"
        )

        for option_order, radio in enumerate(
            radio_inputs,
            start=1
        ):

            value = radio.get(
                "value",
                ""
            )

            label = None

            radio_id = radio.get(
                "id"
            )

            if radio_id:

                label = question.select_one(
                    f"label[for='{radio_id}']"
                )

            if label:

                text = clean_text(
                    label.get_text(
                        " ",
                        strip=True
                    )
                )

            else:

                parent = radio.parent

                if parent:

                    text = clean_text(
                        parent.get_text(
                            " ",
                            strip=True
                        )
                    )

                    if value and text == value:
                        text = value

                else:

                    text = value

            # Correct answers are intentionally not inferred.
            is_correct = None

            options.append(
                {
                    "option_id": (
                        f"{question_id}_{option_order}"
                    ),
                    "order": option_order,
                    "text": text,
                    "value": value,
                    "is_correct": is_correct
                }
            )

    return {
        "question_id": question_id,
        "order": order,
        "response_model": response_model,
        "content": content,
        "gaps": gaps,
        "options": options
    }


# ============================================================
# EXAMPLE
# ============================================================

def get_example_from_raw_html(
    html,
    form
):

    """
    Извлекает Example непосредственно
    из исходного HTML перед текущим form.

    Это обход проблемы с некорректной HTML-структурой
    страницы Test-English.
    """

    form_id = form.get("id")

    if not form_id:
        return None

    marker = re.search(
        rf"<form[^>]+id=['\"]{re.escape(form_id)}['\"]",
        html,
        flags=re.I
    )

    if not marker:
        return None

    before_form = html[
        :marker.start()
    ]

    # Ищем последний EXAMPLE перед form
    matches = list(
        re.finditer(
            r"EXAMPLE\s*:",
            before_form,
            flags=re.I
        )
    )

    if not matches:
        return None

    example_match = matches[-1]

    # HTML-фрагмент после EXAMPLE и до form
    fragment = before_form[
        example_match.start():
    ]

    fragment_soup = BeautifulSoup(
        fragment,
        "html.parser"
    )

    text = clean_text(
        fragment_soup.get_text(
            " ",
            strip=True
        )
    )

    # Убираем всё после загрузочных сообщений
    text = re.split(
        r"\bPlease wait\.\.\.",
        text,
        maxsplit=1,
        flags=re.I
    )[0]

    text = re.split(
        r"\bLoading\.\.\.",
        text,
        maxsplit=1,
        flags=re.I
    )[0]

    text = clean_text(text)

    text = re.sub(
        r"^EXAMPLE\s*:\s*",
        "",
        text,
        flags=re.I
    )

    # Убираем возможный остаток первого вопроса
    text = re.split(
        r"\s+\d+\s+[A-ZА-Я]",
        text,
        maxsplit=1
    )[0]

    parts = re.split(
        r"\s*(?:⇒|→)\s*",
        text,
        maxsplit=1
    )

    if len(parts) == 2:

        return {
            "source": clean_text(
                parts[0]
            ),
            "target": clean_text(
                parts[1]
            )
        }

    return {
        "source": clean_text(text),
        "target": ""
    }


# ============================================================
# EXERCISE
# ============================================================

def parse_exercise(
    form,
    order,
    page,
    raw_html
):

    quiz_id = form.get(
        "id"
    )

    if quiz_id:

        quiz_id = quiz_id.replace(
            "quiz-",
            ""
        )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    previous_heading = form.find_previous(
        ["h3", "h4"]
    )

    title = ""

    if previous_heading:

        title = clean_text(
            previous_heading.get_text(
                " ",
                strip=True
            )
        )

    # --------------------------------------------------------
    # INSTRUCTION
    # --------------------------------------------------------

    instruction = ""

    h5 = form.find_previous(
        "h5"
    )

    if h5:

        instruction = clean_text(
            h5.get_text(
                " ",
                strip=True
            )
        )

    # --------------------------------------------------------
    # EXAMPLE
    # --------------------------------------------------------

    example = get_example_from_raw_html(
        raw_html,
        form
    )

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    question_nodes = form.select(
        ".watu-question"
    )

    questions = []

    for question_order, question in enumerate(
        question_nodes,
        start=1
    ):

        parsed = parse_question(
            question,
            question_order
        )

        questions.append(
            parsed
        )

    return {
        "exercise_id": (
            f"quiz-{quiz_id}"
            if quiz_id
            else f"exercise-{order}"
        ),
        "page": page,
        "order": order,
        "title": title,
        "instruction": instruction,
        "example": example,
        "questions": questions
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("TEST-ENGLISH UNIVERSAL PARSER")
    print("=" * 60)

    print()

    print(
        f"Input : {INPUT_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    if not INPUT_FILE.exists():

        print(
            f"ERROR: файл не найден: {INPUT_FILE}"
        )

        return

    # --------------------------------------------------------
    # READ HTML
    # --------------------------------------------------------

    html = INPUT_FILE.read_text(
        encoding="utf-8",
        errors="replace"
    )

    print(
        f"HTML size: {len(html):,} bytes"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_tag = soup.find(
        "title"
    )

    title = (
        clean_text(
            title_tag.get_text(
                " ",
                strip=True
            )
        )
        if title_tag
        else ""
    )

    # --------------------------------------------------------
    # FORMS
    # --------------------------------------------------------

    forms = soup.select(
        "form[id^='quiz-']"
    )

    print(
        f"Exercises found: {len(forms)}"
    )

    exercises = []

    for exercise_order, form in enumerate(
        forms,
        start=1
    ):

        exercise = parse_exercise(
            form,
            exercise_order,
            page=1,
            raw_html=html
        )

        exercises.append(
            exercise
        )

    # --------------------------------------------------------
    # LESSON
    # --------------------------------------------------------

    lesson = {
        "lesson_id": "",
        "title": title,
        "level": "",
        "topic": "",
        "status": "parsed",

        "pages": [
            {
                "page": 1,
                "exercises": exercises
            }
        ],

        "explanation": {
            "sections": []
        },

        "media": [],

        "source": {
            "provider": "Test-English",
            "source_file": str(
                INPUT_FILE
            ),
            "source_url": "",
            "page": 1
        }
    }

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    OUTPUT_FILE.write_text(
        json.dumps(
            lesson,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()

    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(
        f"Title: {title}"
    )

    print(
        f"Exercises: {len(exercises)}"
    )

    for exercise in exercises:

        print()

        print(
            f"Exercise {exercise['order']}"
        )

        print(
            f"Quiz ID: {exercise['exercise_id']}"
        )

        print(
            f"Instruction: {exercise['instruction']}"
        )

        print(
            f"Questions: {len(exercise['questions'])}"
        )

        if exercise["example"]:

            print(
                "Example:"
            )

            print(
                f"  {exercise['example']['source']} "
                f"⇒ "
                f"{exercise['example']['target']}"
            )

        for question in exercise["questions"]:

            print(
                f"  Q {question['question_id']} "
                f"| {question['response_model']} "
                f"| gaps: {len(question['gaps'])} "
                f"| options: {len(question['options'])}"
            )

            for gap in question["gaps"]:

                print(
                    f"      Gap {gap['gap_order']} "
                    f"| {gap['gap_id']} "
                    f"| control: {gap['input_control']} "
                    f"| options: {len(gap['options'])}"
                )

    print()

    print(
        f"JSON saved: {OUTPUT_FILE}"
    )

    print(
        "=" * 60
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()