import json
import os
import openpyxl
import re
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def export_grammar_data():
    """
    Builds the full runtime dataset:
    - 225 individual lessons with exercises and full grammar theory
    - grammar_catalog.json with level hierarchy and lesson summaries
    - 18 localized rules packages (ru, en, uk, de, es, fr, pl, it, tr, pt, ro, bg, cs, sk, hu, el, et, lt)
    """
    print("[INFO] Exporting full runtime grammar data...")
    os.makedirs('frontend/assets/data/lessons', exist_ok=True)
    os.makedirs('frontend/assets/data/rules', exist_ok=True)

    # 1. Load Universal Lessons
    enriched_path = 'data/cms/universal_lessons_final_enriched.json'
    with open(enriched_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        lessons = raw_data.get('lessons', raw_data) if isinstance(raw_data, dict) else raw_data

    # 2. Load Master Rules from Excel if available, or JSON fallback
    master_excel = 'data/cms/grammar_rules_master.xlsx'
    master_json = 'data/json/grammar_rules_master.json'

    rules_by_lang_and_key = {}
    ru_rules_list = []

    if os.path.exists(master_excel):
        wb = openpyxl.load_workbook(master_excel, data_only=True)
        ws_master = wb['Rules_Master']
        rows = list(ws_master.iter_rows(values_only=True))[1:]
        for r in rows:
            if not any(r): continue
            rule_dict = {
                'Rule ID': r[0],
                'Level': r[1],
                'Lesson #': r[2],
                'Lesson / Topic': r[3],
                'Lang': r[4],
                'Language': r[5],
                'Status': r[6],
                'Core idea': r[7],
                'Main rule / explanation': r[8],
                'Form / structure': r[9],
                'When / why we use it': r[10],
                'Examples': r[11],
                'Special cases / exceptions': r[12],
                'Common mistakes': r[13],
                "Don't confuse with": r[14],
                'Quick summary / memory hook': r[15],
                'Source URL': r[16],
                'QA / notes': r[17]
            }
            lang = r[4]
            if lang not in rules_by_lang_and_key:
                rules_by_lang_and_key[lang] = []
            rules_by_lang_and_key[lang].append(rule_dict)
            if lang == 'ru':
                ru_rules_list.append(rule_dict)
    elif os.path.exists(master_json):
        with open(master_json, 'r', encoding='utf-8') as f:
            all_rules = json.load(f)
        for r in all_rules:
            lang = r.get('Lang')
            if lang not in rules_by_lang_and_key:
                rules_by_lang_and_key[lang] = []
            rules_by_lang_and_key[lang].append(r)
            if lang == 'ru':
                ru_rules_list.append(r)

    def norm(t):
        if not t: return ''
        t = str(t).lower()
        t = re.sub(r'[\'\u2018\u2019\u201c\u201d\":,–\-–—/()_.]', ' ', t)
        return re.sub(r'\s+', ' ', t).strip()

    def find_rule_for_lesson(l_obj):
        lvl = str(l_obj.get('level', '')).strip().upper()
        ltitle = l_obj.get('title') or l_obj.get('topic') or ''
        lid = l_obj.get('id') or l_obj.get('lesson_id') or ''
        norm_ltitle = norm(ltitle)
        norm_lid = norm(lid)

        target_lvl = lvl
        if lvl == 'B1-B2':
            target_lvl = 'B1+'
        elif lvl == 'SHORTS':
            target_lvl = 'GRAMMAR SHORTS'

        candidates = [r for r in ru_rules_list if str(r['Level']).strip().upper() in (target_lvl, lvl)]

        for r in candidates:
            norm_rtopic = norm(r['Lesson / Topic'])
            if norm_rtopic == norm_ltitle or norm_rtopic == norm_lid:
                return r

        for r in candidates:
            norm_rtopic = norm(r['Lesson / Topic'])
            if norm_rtopic in norm_ltitle or norm_ltitle in norm_rtopic:
                return r

        w_l = set(norm_ltitle.split())
        best = None
        max_overlap = 0
        for r in candidates:
            norm_rtopic = norm(r['Lesson / Topic'])
            w_r = set(norm_rtopic.split())
            overlap = len(w_l & w_r)
            if overlap > max_overlap and overlap >= 2:
                max_overlap = overlap
                best = r

        return best

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

    for item in lessons:
        lesson_id = item.get('id') or item.get('lesson_id')
        level = item.get('level', 'A1')
        title = item.get('title') or item.get('topic') or lesson_id
        exercises = item.get('exercises', [])
        q_count = sum(len(ex.get('questions', [])) for ex in exercises)

        rule_match = find_rule_for_lesson(item)
        if rule_match:
            description = rule_match.get('Core idea') or f"Практический тест и правила по теме: {title}"
            theory = {
                'rule_id': rule_match['Rule ID'],
                'lesson_num': rule_match['Lesson #'],
                'title': f"Правила: {title}",
                'level': level,
                'overview': rule_match.get('Core idea'),
                'main_rule': rule_match.get('Main rule / explanation'),
                'form': rule_match.get('Form / structure'),
                'when_why': rule_match.get('When / why we use it'),
                'examples': rule_match.get('Examples'),
                'special_cases': rule_match.get('Special cases / exceptions'),
                'common_mistakes': rule_match.get('Common mistakes'),
                'dont_confuse': rule_match.get("Don't confuse with"),
                'quick_summary': rule_match.get('Quick summary / memory hook')
            }
        else:
            description = f"Практический тест и правила по теме: {title}"
            theory = {
                'title': f"Правила: {title}",
                'level': level,
                'overview': description
            }

        catalog['lessons'].append({
            'lesson_id': lesson_id,
            'level': level,
            'title': title,
            'description': description,
            'questions_count': q_count,
            'exercises_count': len(exercises)
        })

        runtime_lesson = {
            'lesson_id': lesson_id,
            'level': level,
            'title': title,
            'description': description,
            'theory': theory,
            'exercises': exercises
        }

        with open(f"frontend/assets/data/lessons/{lesson_id}.json", 'w', encoding='utf-8') as lf:
            json.dump(runtime_lesson, lf, ensure_ascii=False, indent=2)

    with open('frontend/assets/data/grammar_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    for lang, rlist in rules_by_lang_and_key.items():
        with open(f"frontend/assets/data/rules/rules_{lang}.json", 'w', encoding='utf-8') as rf:
            json.dump(rlist, rf, ensure_ascii=False, indent=2)

    print(f"✅ Full export completed: 225 lessons and {len(rules_by_lang_and_key)} localized rule packages generated.")

if __name__ == '__main__':
    export_grammar_data()
