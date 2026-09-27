from pathlib import Path
import json
import subprocess
import sys
import re


# ============================================================
# НАСТРОЙКИ
# ============================================================

PARSER = Path(r"C:\Users\user\test_english_parser.py")

INPUT_DIR = Path(r"C:\Users\user\Desktop\list")

TEMP_JSON = Path(
    r"C:\Users\user\Desktop\parsed_lesson.json"
)

OUTPUT_JSON = Path(
    r"C:\Users\user\Desktop\universal_lessons.json"
)


# ============================================================
# ЗАПУСК ПАРСЕРА
# ============================================================

def run_parser(input_file):

    print()
    print("=" * 70)
    print(f"PROCESSING: {input_file.name}")
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(PARSER),
            str(input_file),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    print(result.stdout)

    if result.returncode != 0:

        print(result.stderr)

        raise RuntimeError(
            f"Parser failed for {input_file.name}"
        )

    if not TEMP_JSON.exists():

        raise FileNotFoundError(
            f"Parser did not create: {TEMP_JSON}"
        )

    with TEMP_JSON.open(
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# ОЧИСТКА НАЗВАНИЯ УРОКА
# ============================================================

def normalize_lesson_title(title):

    if not title:
        return ""

    title = title.strip()

    # Убираем "- Page X of Y"
    title = re.sub(
        r"\s*-\s*Page\s+\d+\s+of\s+\d+",
        "",
        title,
        flags=re.IGNORECASE
    )

    # Убираем "- Test-English"
    title = re.sub(
        r"\s*-\s*Test-English\s*$",
        "",
        title,
        flags=re.IGNORECASE
    )

    return title.strip()


# ============================================================
# СОЗДАНИЕ УНИКАЛЬНОГО ID УРОКА
# ============================================================

def make_lesson_id(title, existing_ids):

    base = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        title.lower()
    ).strip("_")

    if not base:
        base = "lesson"

    lesson_id = base

    counter = 2

    while lesson_id in existing_ids:

        lesson_id = f"{base}_{counter}"

        counter += 1

    return lesson_id


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("UNIVERSAL LESSON COLLECTOR")
    print("=" * 70)

    # --------------------------------------------------------
    # Проверка parser
    # --------------------------------------------------------

    if not PARSER.exists():

        print(
            f"ERROR: parser not found: {PARSER}"
        )

        return

    # --------------------------------------------------------
    # Получаем TXT-файлы
    # --------------------------------------------------------

    files = sorted(
        INPUT_DIR.glob("*.txt"),
        key=lambda p:
            int(p.stem)
            if p.stem.isdigit()
            else 999999
    )

    if not files:

        print(
            f"ERROR: no TXT files found in {INPUT_DIR}"
        )

        return

    print(
        f"Files found: {len(files)}"
    )

    # ========================================================
    # СТРУКТУРА УРОКОВ
    # ========================================================

    lessons = {}

    lesson_ids = set()

    # ========================================================
    # ОБРАБОТКА ФАЙЛОВ
    # ========================================================

    for file_number, input_file in enumerate(
        files,
        start=1
    ):

        lesson = run_parser(
            input_file
        )

        # ----------------------------------------------------
        # Получаем исходное название
        # ----------------------------------------------------

        raw_title = lesson.get(
            "title",
            ""
        )

        # ----------------------------------------------------
        # Получаем нормализованное название
        # ----------------------------------------------------

        lesson_title = normalize_lesson_title(
            raw_title
        )

        if not lesson_title:

            print(
                f"WARNING: empty lesson title in {input_file.name}"
            )

            continue

        # ----------------------------------------------------
        # Если такого урока ещё нет — создаём
        # ----------------------------------------------------

        if lesson_title not in lessons:

            lesson_id = make_lesson_id(
                lesson_title,
                lesson_ids
            )

            lesson_ids.add(
                lesson_id
            )

            lessons[lesson_title] = {

                "lesson_id": lesson_id,

                "title": lesson_title,

                "level": "",

                "topic": "",

                "status": "parsed",

                "pages": [],

                "explanation": {
                    "sections": []
                },

                "media": [],

                "source": {

                    "provider": "Test-English",

                    "source_directory": str(
                        INPUT_DIR
                    ),

                    "pages_collected": 0,

                    "source_files": [],
                },
            }

        # ----------------------------------------------------
        # Получаем текущий урок
        # ----------------------------------------------------

        current_lesson = lessons[
            lesson_title
        ]

        # ----------------------------------------------------
        # Получаем страницы из parser
        # ----------------------------------------------------

        parsed_pages = lesson.get(
            "pages",
            []
        )

        if not parsed_pages:

            print(
                f"WARNING: no pages found in {input_file.name}"
            )

            continue

        # ====================================================
        # Каждый TXT-файл = одна страница
        # ====================================================

        exercises = parsed_pages[0].get(
            "exercises",
            []
        )

        # ----------------------------------------------------
        # Устанавливаем номер страницы
        # ----------------------------------------------------

        page_number = len(
            current_lesson["pages"]
        ) + 1

        # ----------------------------------------------------
        # Исправляем page у exercises
        # ----------------------------------------------------

        for exercise in exercises:

            exercise["page"] = page_number

        # ----------------------------------------------------
        # Создаём страницу
        # ----------------------------------------------------

        page = {

            "page": page_number,

            "source_file": input_file.name,

            "exercises": exercises,
        }

        current_lesson["pages"].append(
            page
        )

        # ----------------------------------------------------
        # Обновляем source
        # ----------------------------------------------------

        current_lesson["source"][
            "source_files"
        ].append(
            input_file.name
        )

        current_lesson["source"][
            "pages_collected"
        ] = len(
            current_lesson["pages"]
        )

    # ========================================================
    # ФОРМИРУЕМ ИТОГОВЫЙ JSON
    # ========================================================

    result = {

        "version": "1.0",

        "provider": "Test-English",

        "lessons": list(
            lessons.values()
        ),
    }

    # ========================================================
    # СОХРАНЕНИЕ
    # ========================================================

    OUTPUT_JSON.write_text(

        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"
    )

    # ========================================================
    # СТАТИСТИКА
    # ========================================================

    total_pages = 0

    total_exercises = 0

    total_questions = 0

    total_gaps = 0

    total_options = 0

    print()
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Lessons: {len(lessons)}"
    )

    for current_lesson in lessons.values():

        lesson_pages = len(
            current_lesson["pages"]
        )

        lesson_exercises = sum(

            len(
                page["exercises"]
            )

            for page in current_lesson[
                "pages"
            ]
        )

        lesson_questions = sum(

            len(
                exercise.get(
                    "questions",
                    []
                )
            )

            for page in current_lesson[
                "pages"
            ]

            for exercise in page[
                "exercises"
            ]
        )

        lesson_gaps = sum(

            len(
                question.get(
                    "gaps",
                    []
                )
            )

            for page in current_lesson[
                "pages"
            ]

            for exercise in page[
                "exercises"
            ]

            for question in exercise.get(
                "questions",
                []
            )
        )

        lesson_options = sum(

            len(
                question.get(
                    "options",
                    []
                )
            )

            +

            sum(

                len(
                    gap.get(
                        "options",
                        []
                    )
                )

                for gap in question.get(
                    "gaps",
                    []
                )

            )

            for page in current_lesson[
                "pages"
            ]

            for exercise in page[
                "exercises"
            ]

            for question in exercise.get(
                "questions",
                []
            )
        )

        total_pages += lesson_pages

        total_exercises += lesson_exercises

        total_questions += lesson_questions

        total_gaps += lesson_gaps

        total_options += lesson_options

        print()
        print(
            f"Lesson: {current_lesson['title']}"
        )

        print(
            f"  Pages: {lesson_pages}"
        )

        print(
            f"  Exercises: {lesson_exercises}"
        )

        print(
            f"  Questions: {lesson_questions}"
        )

        print(
            f"  Gaps: {lesson_gaps}"
        )

        print(
            f"  Options: {lesson_options}"
        )

    print()
    print("-" * 70)

    print(
        f"TOTAL LESSONS: {len(lessons)}"
    )

    print(
        f"TOTAL PAGES: {total_pages}"
    )

    print(
        f"TOTAL EXERCISES: {total_exercises}"
    )

    print(
        f"TOTAL QUESTIONS: {total_questions}"
    )

    print(
        f"TOTAL GAPS: {total_gaps}"
    )

    print(
        f"TOTAL OPTIONS: {total_options}"
    )

    print()
    print(
        "JSON saved:"
    )

    print(
        OUTPUT_JSON
    )

    print("=" * 70)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()