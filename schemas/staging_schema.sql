-- ===========================================================================
-- STAGING DATABASE SCHEMA
-- Universal English Test Platform
--
-- Minimum relational schema extension for staging imported raw corpus content.
-- Enforces:
-- 1. Primary keys on all entities (zero duplicate IDs).
-- 2. Foreign keys with PRAGMA foreign_keys = ON (zero orphaned references).
-- 3. Staging isolation: explicit status = 'staging' prevents publishing to users.
-- 4. Rule 12A compatibility: correct_answer and is_correct remain NULL.
-- ===========================================================================

PRAGMA foreign_keys = ON;

-- 1. Import Run Metadata
CREATE TABLE IF NOT EXISTS staging_import_runs (
    import_id TEXT PRIMARY KEY,
    imported_at TEXT NOT NULL,
    source_file TEXT NOT NULL,
    topics_count INTEGER NOT NULL,
    exercises_count INTEGER NOT NULL,
    questions_count INTEGER NOT NULL,
    gaps_count INTEGER NOT NULL,
    options_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed'
);

-- 2. Staging Lessons (Topics)
CREATE TABLE IF NOT EXISTS staging_lessons (
    lesson_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    level TEXT NOT NULL,
    topic TEXT,
    status TEXT NOT NULL DEFAULT 'staging',
    description TEXT,
    source_provider TEXT NOT NULL DEFAULT 'Test-English',
    source_url TEXT,
    pages_count INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 3. Staging Exercises
CREATE TABLE IF NOT EXISTS staging_exercises (
    exercise_id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL REFERENCES staging_lessons(lesson_id) ON DELETE CASCADE,
    page INTEGER NOT NULL,
    exercise_order INTEGER NOT NULL,
    title TEXT,
    instruction TEXT,
    example_source TEXT,
    example_target TEXT,
    status TEXT NOT NULL DEFAULT 'staging',
    source_file TEXT,
    source_url TEXT
);

-- 4. Staging Questions
CREATE TABLE IF NOT EXISTS staging_questions (
    question_id TEXT PRIMARY KEY,
    exercise_id TEXT NOT NULL REFERENCES staging_exercises(exercise_id) ON DELETE CASCADE,
    lesson_id TEXT NOT NULL REFERENCES staging_lessons(lesson_id) ON DELETE CASCADE,
    question_order INTEGER NOT NULL,
    response_model TEXT NOT NULL, -- 'gap', 'single_choice', 'multiple_choice'
    content TEXT NOT NULL,
    explanation TEXT,
    difficulty TEXT,
    status TEXT NOT NULL DEFAULT 'staging'
);

-- 5. Staging Gaps
CREATE TABLE IF NOT EXISTS staging_gaps (
    gap_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL REFERENCES staging_questions(question_id) ON DELETE CASCADE,
    gap_order INTEGER NOT NULL,
    input_control TEXT NOT NULL, -- 'select', 'text'
    correct_answer TEXT,        -- NULL during staging (Rule 12A)
    accepted_answers TEXT,      -- JSON array string (e.g. '[]')
    case_sensitive INTEGER NOT NULL DEFAULT 0,
    feedback_correct TEXT,
    feedback_incorrect TEXT
);

-- 6. Staging Options
CREATE TABLE IF NOT EXISTS staging_options (
    option_id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL REFERENCES staging_questions(question_id) ON DELETE CASCADE,
    gap_id TEXT REFERENCES staging_gaps(gap_id) ON DELETE CASCADE,
    option_order INTEGER NOT NULL,
    text TEXT NOT NULL,
    value TEXT,
    is_correct INTEGER          -- NULL during staging (Rule 12A)
);

-- Indexes for fast relational lookup and hierarchy traversal
CREATE INDEX IF NOT EXISTS idx_staging_exercises_lesson ON staging_exercises(lesson_id);
CREATE INDEX IF NOT EXISTS idx_staging_questions_exercise ON staging_questions(exercise_id);
CREATE INDEX IF NOT EXISTS idx_staging_questions_lesson ON staging_questions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_staging_gaps_question ON staging_gaps(question_id);
CREATE INDEX IF NOT EXISTS idx_staging_options_question ON staging_options(question_id);
CREATE INDEX IF NOT EXISTS idx_staging_options_gap ON staging_options(gap_id);
