# English Breakfast Grammar

Универсальная система сбора, подготовки и публикации грамматических тестов.

## Архитектура

```
Test-English (HTML)
      ↓
  1.txt, 2.txt...   ← C:\Users\user\Desktop\list\
      ↓
pipeline/parser/test_english_parser.py        ← парсит одну страницу
      ↓
pipeline/collector/universal_collector.py     ← объединяет страницы в уроки
      ↓
data/output/universal_lessons.json
      ↓
pipeline/validators/universal_validator.py    ← проверяет JSON
      ↓
pipeline/cms/google_sheets_generator.py       ← создаёт Excel CMS
      ↓
english_cms.xlsx  → Google Sheets
      ↓
Gemini Answer Processing                      ← определяет правильные ответы
      ↓
pipeline/validators/cms_validator.py          ← проверяет Excel после Gemini
      ↓
JSON Builder (в разработке)
      ↓
final_lessons.json
      ↓
Firebase / Firestore
      ↓
Test Engine / App
```

## Структура проекта

```
English Breakfast Grammar/
│
├── pipeline/
│   ├── parser/
│   │   └── test_english_parser.py       ← парсер одной HTML-страницы
│   ├── collector/
│   │   └── universal_collector.py       ← обработка всех .txt + группировка
│   ├── validators/
│   │   ├── universal_validator.py       ← валидация universal_lessons.json
│   │   └── cms_validator.py            ← валидация Excel CMS после Gemini
│   └── cms/
│       └── google_sheets_generator.py  ← генерация Excel CMS из JSON
│
├── data/
│   ├── input/                          ← исходные HTML-файлы (.txt)
│   └── output/                         ← universal_lessons.json и др.
│
├── schemas/                            ← JSON-схемы (в разработке)
│
└── app/                                ← Node.js / Frontend (Preview, Test Engine)
```

## Запуск

### 1. Сбор данных

```bash
# Парсинг всех .txt из папки list → universal_lessons.json
python pipeline/collector/universal_collector.py
```

### 2. Валидация JSON

```bash
python pipeline/validators/universal_validator.py
```

### 3. Генерация Excel CMS

```bash
python pipeline/cms/google_sheets_generator.py
```

### 4. Валидация CMS (после Gemini)

```bash
python pipeline/validators/cms_validator.py
```

## Рабочие папки (текущий прототип)

| Путь | Назначение |
|---|---|
| `C:\Users\user\Desktop\list\` | Исходные HTML-файлы (1.txt, 2.txt...) |
| `C:\Users\user\Desktop\universal_lessons.json` | Результат Collector |
| `C:\Users\user\Desktop\english_cms.xlsx` | Excel CMS |

## Принципы

- **Parser не определяет правильные ответы** — `correct_answer = null`, `is_correct = null`
- **Gemini** — единственный источник правильных ответов (отдельный этап)
- **Два валидатора**: `universal_validator` (JSON) и `cms_validator` (Excel)
- **Структура не изменяется** — Gemini только заполняет поля ответов

## Статус

| Этап | Статус |
|---|---|
| Parser | ✅ работает |
| Collector | ✅ работает |
| Universal Validator | ✅ работает |
| Google Sheets Generator | ✅ работает |
| Gemini Answer Processing | 🟡 автоматизация в разработке |
| CMS Validator | ✅ работает |
| JSON Builder | ❌ в разработке |
| Firebase Upload | ❌ в разработке |
