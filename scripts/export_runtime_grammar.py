import json
import os
import sqlite3

def export_grammar_data():
    os.makedirs('frontend/assets/data/lessons', exist_ok=True)
    
    # 1. Load full enriched corpus or extract from staging.db
    enriched_path = 'data/cms/universal_lessons_final_enriched.json'
    if os.path.exists(enriched_path):
        with open(enriched_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            all_lessons = raw_data.get('lessons', raw_data) if isinstance(raw_data, dict) else raw_data
    else:
        # Fallback to staging.db
        conn = sqlite3.connect('data/staging.db')
        c = conn.cursor()
        lessons_raw = c.execute('SELECT lesson_id, title, level, topic, description FROM staging_lessons').fetchall()
        all_lessons = []
        for l in lessons_raw:
            all_lessons.append({
                'lesson_id': l[0],
                'title': l[1],
                'level': l[2],
                'topic': l[3],
                'description': l[4] or '',
                'exercises': []
            })

    print(f"Total lessons loaded: {len(all_lessons)}")

    catalog = {
        'levels': [
            {'id': 'A1', 'title': 'A1 Elementary', 'description': 'Основы грамматики: времена, местоимения, базовые конструкции', 'color': '#22c55e', 'icon': '🌱'},
            {'id': 'A2', 'title': 'A2 Pre-Intermediate', 'description': 'Прошедшие времена, модальные глаголы, сравнения', 'color': '#3b82f6', 'icon': '📘'},
            {'id': 'B1', 'title': 'B1 Intermediate', 'description': 'Совершенные времена, пассивный залог, условные предложения', 'color': '#f59e0b', 'icon': '⚡'},
            {'id': 'B1-B2', 'title': 'B1+ Upper-Intermediate', 'description': 'Сложные грамматические структуры, герундий и инфинитив', 'color': '#8b5cf6', 'icon': '🎯'},
            {'id': 'B2', 'title': 'B2 Pre-Advanced', 'description': 'Инверсия, смешанные условные, идиоматическая грамматика', 'color': '#ec4899', 'icon': '🔥'},
            {'id': 'C1', 'title': 'C1 Advanced', 'description': 'Продвинутый уровень: нюансы стилистики, акцентные конструкции', 'color': '#06b6d4', 'icon': '👑'},
            {'id': 'SHORTS', 'title': 'Grammar Shorts', 'description': 'Короткие тесты и правила на частые ошибки', 'color': '#10b981', 'icon': '💡'}
        ],
        'lessons': []
    }

    # Format each lesson for runtime
    for item in all_lessons:
        lesson_id = item.get('id') or item.get('lesson_id')
        level = item.get('level', 'A1')
        title = item.get('title') or item.get('topic') or lesson_id
        description = item.get('description') or f"Практический тест и правила по теме: {title}"
        exercises = item.get('exercises', [])
        
        q_count = sum(len(ex.get('questions', [])) for ex in exercises)
        
        catalog['lessons'].append({
            'lesson_id': lesson_id,
            'level': level,
            'title': title,
            'description': description,
            'questions_count': q_count,
            'exercises_count': len(exercises)
        })

        # Save individual lesson JSON file for fast on-demand fetching
        lesson_file = f"frontend/assets/data/lessons/{lesson_id}.json"
        
        # Build clean runtime lesson
        runtime_lesson = {
            'lesson_id': lesson_id,
            'level': level,
            'title': title,
            'description': description,
            'theory': {
                'title': f"Правила и грамматика: {title}",
                'level': level,
                'overview': f"В этом уроке мы разберем ключевые правила и нюансы употребления грамматической конструкции «{title}».",
                'rules': [
                    {
                        'heading': 'Основные правила использования',
                        'content': f"Конструкция «{title}» используется для выражения ключевых временных и смысловых отношений в английском языке. Обратите внимание на согласование подлежащего и сказуемого.",
                        'table': {
                            'headers': ['Форма', 'Пример (EN)', 'Перевод (RU)'],
                            'rows': [
                                ['Утверждение (+)', 'I / You / We / They work hard.', 'Я / Ты / Мы / Они усердно работаем.'],
                                ['Отрицание (-)', 'He / She / It does not (doesn\'t) work.', 'Он / Она / Оно не работает.'],
                                ['Вопрос (?)', 'Do you work here? — Yes, I do.', 'Ты работаешь здесь? — Да.']
                            ]
                        }
                    },
                    {
                        'heading': 'Важные нюансы и подсказки',
                        'content': 'Обращайте внимание на маркеры времени и контекст предложения при выборе правильной формы глагола.',
                        'tips': [
                            'Внимательно читайте всё предложение до конца перед ответом.',
                            'Внимательно проверяйте краткие формы (сокращения с апострофом, например: isn\'t, don\'t, \'ve).'
                        ]
                    }
                ]
            },
            'exercises': exercises
        }
        
        with open(lesson_file, 'w', encoding='utf-8') as lf:
            json.dump(runtime_lesson, lf, ensure_ascii=False, indent=2)

    with open('frontend/assets/data/grammar_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print("Export complete: grammar_catalog.json and lessons created.")

if __name__ == '__main__':
    export_grammar_data()
