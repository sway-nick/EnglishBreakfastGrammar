/**
 * Universal Content Models
 *
 * These are the SOLE source of truth for the internal data structure.
 * All parsers, adapters, and the Test Engine use ONLY these models.
 * No external source (Test-English, WatuPRO, etc.) IDs or structures
 * should ever leak into these definitions.
 */

// ---------------------------------------------------------------------------
// ENUMS
// ---------------------------------------------------------------------------

export const QuestionType = Object.freeze({
  GAP_SELECT:      'gap_select',      // Dropdown / click to select
  GAP_TEXT:        'gap_text',        // Free-text fill-in
  SINGLE_CHOICE:   'single_choice',   // Radio — one correct answer
  MULTIPLE_CHOICE: 'multiple_choice', // Checkboxes — several correct answers
  TEXT_INPUT:      'text_input',      // Open text answer
  TRUE_FALSE:      'true_false',      // True / False
  MATCHING:        'matching',        // Match pairs
  ORDERING:        'ordering',        // Put in correct order
});

export const ContentStatus = Object.freeze({
  DRAFT:     'draft',
  REVIEW:    'review',
  PUBLISHED: 'published',
  ARCHIVED:  'archived',
});

export const Level = Object.freeze({
  A1: 'A1',
  A2: 'A2',
  B1: 'B1',
  B2: 'B2',
  C1: 'C1',
  C2: 'C2',
});

// ---------------------------------------------------------------------------
// SOURCE METADATA
// Tracks where content was imported from.
// This is informational only — never use sourceId as our internal ID.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} SourceMeta
 * @property {string}  provider        - e.g. 'test-english', 'manual', 'watuPRO'
 * @property {string}  [url]           - Original URL of the page
 * @property {string}  [sourceId]      - Source-site's own identifier (read-only reference)
 * @property {string}  [importedAt]    - ISO 8601 timestamp of import
 * @property {string}  [importVersion] - Version of the parser that created this
 */

// ---------------------------------------------------------------------------
// OPTION
// One selectable answer within a Gap or a Choice question.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Option
 * @property {string}        id         - Internal ID, e.g. 'O001'
 * @property {number}        order      - Display order (1-based)
 * @property {string}        value      - Display text shown to the user
 * @property {boolean|null}  is_correct - TRUE/FALSE after AI processing; null = not yet reviewed
 * @property {string}        [feedback] - Optional per-option feedback
 */

/**
 * Creates a new Option object with defaults.
 * NOTE (Rule 12A): Parser must NOT set is_correct = true/false.
 * is_correct is always null after import; filled only by AI Answer Processing step.
 * @param {Partial<Option>} data
 * @returns {Option}
 */
export function createOption(data = {}) {
  return {
    id:         data.id         ?? '',
    order:      data.order      ?? 1,
    value:      data.value      ?? '',
    is_correct: data.is_correct ?? null,   // null = awaiting AI processing
    feedback:   data.feedback   ?? '',
  };
}

// ---------------------------------------------------------------------------
// GAP
// A single blank/placeholder within a question text.
// One Question may contain multiple Gaps.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Gap
 * @property {string}        id               - Internal ID, e.g. 'G001'
 * @property {number}        order            - Position of this gap in the question (1-based)
 * @property {string}        placeholder      - Token used in question text, e.g. '{{gap1}}'
 * @property {Option[]}      options          - Available choices (for gap_select); empty for gap_text
 * @property {string|null}   correct_answer   - Primary correct answer; null = awaiting AI processing
 * @property {string[]}      accepted_answers - All acceptable answers
 * @property {boolean}       review_required  - Flagged when AI cannot determine answer reliably
 */

/**
 * Creates a new Gap object with defaults.
 * NOTE (Rule 12A): Parser must NOT set correct_answer.
 * correct_answer / accepted_answers are null/[] after import; filled by AI Answer Processing.
 * @param {Partial<Gap>} data
 * @returns {Gap}
 */
export function createGap(data = {}) {
  return {
    id:               data.id               ?? '',
    order:            data.order             ?? 1,
    placeholder:      data.placeholder       ?? `{{gap${data.order ?? 1}}}`,
    options:          Array.isArray(data.options) ? data.options : [],
    correct_answer:   data.correct_answer    ?? null,   // null = awaiting AI processing
    accepted_answers: Array.isArray(data.accepted_answers) ? data.accepted_answers : [],
    review_required:  data.review_required   ?? false,
  };
}

// ---------------------------------------------------------------------------
// QUESTION
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Question
 * @property {string}     id          - Internal ID, e.g. 'Q001'
 * @property {number}     order       - Position within parent Exercise (1-based)
 * @property {string}     type        - One of QuestionType values
 * @property {string}     text        - Question text. Gaps are marked as {{gap1}}, {{gap2}}, etc.
 * @property {Gap[]}      gaps        - List of gaps (for gap_select / gap_text questions)
 * @property {Option[]}   options     - For single_choice / multiple_choice / true_false (no gaps)
 * @property {string}     hint        - Optional hint shown to the user before answering
 * @property {string}     feedback    - General feedback shown after answering
 * @property {string}     explanation - Grammar explanation text (from Explanation tab)
 * @property {SourceMeta} [source]    - Import metadata
 */

/**
 * Creates a new Question object with defaults.
 * @param {Partial<Question>} data
 * @returns {Question}
 */
export function createQuestion(data = {}) {
  return {
    id:          data.id          ?? '',
    order:       data.order       ?? 1,
    type:        data.type        ?? QuestionType.GAP_SELECT,
    text:        data.text        ?? '',
    gaps:        Array.isArray(data.gaps)    ? data.gaps    : [],
    options:     Array.isArray(data.options) ? data.options : [],
    hint:        data.hint        ?? '',
    feedback:    data.feedback    ?? '',
    explanation: data.explanation ?? '',
    source:      data.source      ?? null,
  };
}

// ---------------------------------------------------------------------------
// EXERCISE
// A group of questions within a lesson, typically with a shared instruction.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Exercise
 * @property {string}     id          - Internal ID, e.g. 'E001'
 * @property {string}     lessonId    - Parent Lesson ID
 * @property {number}     order       - Position within parent Lesson (1-based)
 * @property {string}     title       - Exercise title (may be empty)
 * @property {string}     instruction - Instructions shown above the questions
 * @property {string}     status      - One of ContentStatus values
 * @property {Question[]} questions   - Ordered list of questions
 * @property {SourceMeta} [source]    - Import metadata
 */

/**
 * Creates a new Exercise object with defaults.
 * @param {Partial<Exercise>} data
 * @returns {Exercise}
 */
export function createExercise(data = {}) {
  return {
    id:          data.id          ?? '',
    lessonId:    data.lessonId    ?? '',
    order:       data.order       ?? 1,
    title:       data.title       ?? '',
    instruction: data.instruction ?? '',
    status:      data.status      ?? ContentStatus.DRAFT,
    questions:   Array.isArray(data.questions) ? data.questions : [],
    source:      data.source      ?? null,
  };
}

// ---------------------------------------------------------------------------
// LESSON
// Top-level content unit.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Lesson
 * @property {string}     id          - Internal ID, e.g. 'L001'
 * @property {string}     title       - Lesson title, e.g. 'Present Simple'
 * @property {string}     level       - One of Level values
 * @property {string}     description - Long description / learning objectives
 * @property {string}     status      - One of ContentStatus values
 * @property {number}     order       - Display order in the course
 * @property {number}     version     - Content version (integer, starts at 1)
 * @property {Exercise[]} exercises   - Ordered list of exercises
 * @property {SourceMeta} [source]    - Import metadata
 */

/**
 * Creates a new Lesson object with defaults.
 * @param {Partial<Lesson>} data
 * @returns {Lesson}
 */
export function createLesson(data = {}) {
  return {
    id:          data.id          ?? '',
    title:       data.title       ?? '',
    level:       data.level       ?? '',
    description: data.description ?? '',
    status:      data.status      ?? ContentStatus.DRAFT,
    order:       data.order       ?? 1,
    version:     data.version     ?? 1,
    exercises:   Array.isArray(data.exercises) ? data.exercises : [],
    source:      data.source      ?? null,
  };
}

// ---------------------------------------------------------------------------
// ID HELPERS
// ---------------------------------------------------------------------------

/**
 * Simple sequential ID counter — used only during parsing/import.
 * In production, IDs should be stable and stored persistently.
 */
export class IdCounter {
  #counters = {};

  /**
   * @param {string} prefix - e.g. 'L', 'E', 'Q', 'G', 'O'
   * @param {number} [padLength=3]
   * @returns {string}
   */
  next(prefix, padLength = 3) {
    this.#counters[prefix] = (this.#counters[prefix] ?? 0) + 1;
    return `${prefix}${String(this.#counters[prefix]).padStart(padLength, '0')}`;
  }

  /** Reset a specific prefix counter or all counters. */
  reset(prefix) {
    if (prefix) {
      delete this.#counters[prefix];
    } else {
      this.#counters = {};
    }
  }

  /** Seed a counter to continue from an existing max value. */
  seed(prefix, value) {
    this.#counters[prefix] = value;
  }
}
