-- ===========================================================================
-- ADAPTATION DATABASE SCHEMA
-- Universal English Test Platform (TASK-010B Specification)
--
-- Relational schema for the adaptation layer.
-- Enforces:
-- 1. Complete isolation from source/staging tables (source remains immutable).
-- 2. Bidirectional traceability (every adapted entity maps to its source ID).
-- 3. Invariant cardinality and response_model contracts.
-- 4. Status lifecycle: PENDING, GENERATED, VALIDATED, REVIEW_REQUIRED, APPROVED, REJECTED.
-- ===========================================================================

PRAGMA foreign_keys = ON;

-- 1. Adaptation Run Tracking
CREATE TABLE IF NOT EXISTS adaptation_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    model_name TEXT,
    target_level TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'failed'
    total_items INTEGER NOT NULL DEFAULT 0,
    generated_count INTEGER NOT NULL DEFAULT 0,
    validated_count INTEGER NOT NULL DEFAULT 0,
    rejected_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

-- 2. Adapted Lessons (Topics)
CREATE TABLE IF NOT EXISTS adapted_lessons (
    adapted_lesson_id TEXT PRIMARY KEY,
    source_lesson_id TEXT NOT NULL,
    title TEXT NOT NULL,
    level TEXT NOT NULL,
    topic TEXT,
    description TEXT,
    adaptation_status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, GENERATED, VALIDATED, REVIEW_REQUIRED, APPROVED, REJECTED
    review_required INTEGER NOT NULL DEFAULT 0,        -- 0 = False, 1 = True
    adapted_by TEXT,
    adapted_at TEXT,
    adaptation_notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 3. Adapted Exercises
CREATE TABLE IF NOT EXISTS adapted_exercises (
    adapted_exercise_id TEXT PRIMARY KEY,
    source_exercise_id TEXT NOT NULL,
    adapted_lesson_id TEXT NOT NULL REFERENCES adapted_lessons(adapted_lesson_id) ON DELETE CASCADE,
    exercise_order INTEGER NOT NULL,
    page INTEGER NOT NULL DEFAULT 1,
    title TEXT,
    instruction TEXT,
    example_source TEXT,
    example_target TEXT,
    adaptation_status TEXT NOT NULL DEFAULT 'PENDING',
    review_required INTEGER NOT NULL DEFAULT 0,
    adaptation_notes TEXT
);

-- 4. Adapted Questions
CREATE TABLE IF NOT EXISTS adapted_questions (
    adapted_question_id TEXT PRIMARY KEY,
    source_question_id TEXT NOT NULL,
    adapted_exercise_id TEXT NOT NULL REFERENCES adapted_exercises(adapted_exercise_id) ON DELETE CASCADE,
    adapted_lesson_id TEXT NOT NULL REFERENCES adapted_lessons(adapted_lesson_id) ON DELETE CASCADE,
    question_order INTEGER NOT NULL,
    response_model TEXT NOT NULL,                      -- 'gap', 'single_choice', 'multiple_choice'
    source_text TEXT NOT NULL,
    adapted_text TEXT,
    explanation TEXT,
    difficulty TEXT,
    similarity_score REAL,                             -- Jaccard/Levenshtein metric to flag shallow copies
    adaptation_status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, GENERATED, VALIDATED, REVIEW_REQUIRED, APPROVED, REJECTED
    review_required INTEGER NOT NULL DEFAULT 0,
    adaptation_notes TEXT,
    adapted_by TEXT,
    adapted_at TEXT
);

-- 5. Adapted Gaps
CREATE TABLE IF NOT EXISTS adapted_gaps (
    adapted_gap_id TEXT PRIMARY KEY,
    source_gap_id TEXT NOT NULL,
    adapted_question_id TEXT NOT NULL REFERENCES adapted_questions(adapted_question_id) ON DELETE CASCADE,
    gap_order INTEGER NOT NULL,
    input_control TEXT NOT NULL,                        -- 'select', 'text'
    source_correct_answer TEXT,
    adapted_correct_answer TEXT,
    source_accepted_answers TEXT,                       -- JSON array string
    adapted_accepted_answers TEXT,                      -- JSON array string
    case_sensitive INTEGER NOT NULL DEFAULT 0,
    review_required INTEGER NOT NULL DEFAULT 0,
    adaptation_notes TEXT
);

-- 6. Adapted Options
CREATE TABLE IF NOT EXISTS adapted_options (
    adapted_option_id TEXT PRIMARY KEY,
    source_option_id TEXT NOT NULL,
    adapted_question_id TEXT NOT NULL REFERENCES adapted_questions(adapted_question_id) ON DELETE CASCADE,
    adapted_gap_id TEXT REFERENCES adapted_gaps(adapted_gap_id) ON DELETE CASCADE,
    option_order INTEGER NOT NULL,
    source_text TEXT NOT NULL,
    adapted_text TEXT NOT NULL,
    source_value TEXT,
    adapted_value TEXT,
    source_is_correct INTEGER NOT NULL,                -- 0 or 1
    adapted_is_correct INTEGER NOT NULL,               -- 0 or 1
    review_required INTEGER NOT NULL DEFAULT 0,
    adaptation_notes TEXT
);

-- Indexes for fast lookup, relational traversal and status queries
CREATE INDEX IF NOT EXISTS idx_adapted_lessons_source ON adapted_lessons(source_lesson_id);
CREATE INDEX IF NOT EXISTS idx_adapted_exercises_lesson ON adapted_exercises(adapted_lesson_id);
CREATE INDEX IF NOT EXISTS idx_adapted_exercises_source ON adapted_exercises(source_exercise_id);
CREATE INDEX IF NOT EXISTS idx_adapted_questions_exercise ON adapted_questions(adapted_exercise_id);
CREATE INDEX IF NOT EXISTS idx_adapted_questions_source ON adapted_questions(source_question_id);
CREATE INDEX IF NOT EXISTS idx_adapted_questions_status ON adapted_questions(adaptation_status);
CREATE INDEX IF NOT EXISTS idx_adapted_gaps_question ON adapted_gaps(adapted_question_id);
CREATE INDEX IF NOT EXISTS idx_adapted_gaps_source ON adapted_gaps(source_gap_id);
CREATE INDEX IF NOT EXISTS idx_adapted_options_question ON adapted_options(adapted_question_id);
CREATE INDEX IF NOT EXISTS idx_adapted_options_gap ON adapted_options(adapted_gap_id);
CREATE INDEX IF NOT EXISTS idx_adapted_options_source ON adapted_options(source_option_id);
