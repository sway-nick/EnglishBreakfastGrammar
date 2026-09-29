/**
 * Validation Module
 *
 * Validates a Universal Lesson JSON against the content model rules.
 * Returns structured results with ERRORs and WARNINGs.
 * Never auto-corrects — only reports.
 */

import { QuestionType, ContentStatus, Level } from '../models/index.js';

// ---------------------------------------------------------------------------
// RESULT TYPES
// ---------------------------------------------------------------------------

export const Severity = Object.freeze({
  ERROR:   'ERROR',
  WARNING: 'WARNING',
  INFO:    'INFO',
});

/**
 * @typedef {Object} ValidationIssue
 * @property {string} severity - 'ERROR' | 'WARNING' | 'INFO'
 * @property {string} code     - Short machine-readable code
 * @property {string} message  - Human-readable description
 * @property {string} [path]   - Dot-notation path to the offending field
 */

/**
 * @typedef {Object} ValidationResult
 * @property {boolean}           valid   - true only if there are zero ERRORs
 * @property {ValidationIssue[]} issues  - All collected issues
 * @property {ValidationIssue[]} errors
 * @property {ValidationIssue[]} warnings
 */

// ---------------------------------------------------------------------------
// HELPERS
// ---------------------------------------------------------------------------

function issue(severity, code, message, path = '') {
  return { severity, code, message, path };
}

const error   = (code, msg, path) => issue(Severity.ERROR,   code, msg, path);
const warning = (code, msg, path) => issue(Severity.WARNING, code, msg, path);
const info    = (code, msg, path) => issue(Severity.INFO,    code, msg, path);

const PLACEHOLDER_RE = /\{\{gap\d+\}\}/g;
const VALID_PLACEHOLDER_RE = /^\{\{gap\d+\}\}$/;

// ---------------------------------------------------------------------------
// VALIDATORS — bottom-up (Option → Gap → Question → Exercise → Lesson)
// ---------------------------------------------------------------------------

function validateOption(opt, path) {
  const issues = [];

  if (!opt.id) {
    issues.push(error('OPTION_NO_ID', 'Option is missing an ID', `${path}.id`));
  }
  if (!opt.value || !String(opt.value).trim()) {
    issues.push(error('OPTION_EMPTY_VALUE', 'Option has an empty value', `${path}.value`));
  }
  if (typeof opt.correct !== 'boolean') {
    issues.push(error('OPTION_INVALID_CORRECT', `Option 'correct' must be boolean, got: ${typeof opt.correct}`, `${path}.correct`));
  }

  return issues;
}

function validateGap(gap, path, questionText) {
  const issues = [];

  if (!gap.id) {
    issues.push(error('GAP_NO_ID', 'Gap is missing an ID', `${path}.id`));
  }

  const placeholder = gap.placeholder || `{{gap${gap.order}}}`;

  // Check placeholder exists in question text
  if (questionText && !questionText.includes(placeholder)) {
    issues.push(error(
      'GAP_PLACEHOLDER_MISSING_IN_TEXT',
      `Gap placeholder "${placeholder}" is not found in question text`,
      `${path}.placeholder`,
    ));
  }

  // Validate options
  if (!Array.isArray(gap.options) || gap.options.length === 0) {
    issues.push(error('GAP_NO_OPTIONS', 'Gap has no options', `${path}.options`));
  } else {
    // Check for duplicate values
    const values = gap.options.map(o => o.value?.toLowerCase().trim());
    const seen = new Set();
    values.forEach((v, i) => {
      if (seen.has(v)) {
        issues.push(error('GAP_DUPLICATE_OPTION', `Duplicate option value "${v}"`, `${path}.options[${i}]`));
      }
      seen.add(v);
    });

    // Check at least one correct
    const correctCount = gap.options.filter(o => o.correct).length;
    if (correctCount === 0) {
      issues.push(error('GAP_NO_CORRECT', 'Gap has no correct answer marked', `${path}.options`));
    }
    if (correctCount > 1) {
      issues.push(warning('GAP_MULTIPLE_CORRECT', `Gap has ${correctCount} correct options — is this intentional?`, `${path}.options`));
    }

    // Validate each option
    gap.options.forEach((opt, i) => {
      issues.push(...validateOption(opt, `${path}.options[${i}]`));
    });
  }

  return issues;
}

function validateQuestion(q, path) {
  const issues = [];

  if (!q.id) {
    issues.push(error('QUESTION_NO_ID', 'Question is missing an ID', `${path}.id`));
  }
  if (!q.text || !String(q.text).trim()) {
    issues.push(error('QUESTION_NO_TEXT', 'Question has no text', `${path}.text`));
  }
  if (!q.type) {
    issues.push(error('QUESTION_NO_TYPE', 'Question has no type', `${path}.type`));
  } else if (!Object.values(QuestionType).includes(q.type)) {
    issues.push(error('QUESTION_UNKNOWN_TYPE', `Unknown question type: "${q.type}"`, `${path}.type`));
  }

  const isGapType = q.type === QuestionType.GAP_SELECT || q.type === QuestionType.GAP_TEXT;

  if (isGapType) {
    // Find all placeholders in question text
    const textPlaceholders = (q.text?.match(PLACEHOLDER_RE) ?? []);
    const gapPlaceholders  = (q.gaps ?? []).map(g => g.placeholder || `{{gap${g.order}}}`);

    // Placeholder in text but no corresponding gap
    textPlaceholders.forEach(ph => {
      if (!gapPlaceholders.includes(ph)) {
        issues.push(error(
          'QUESTION_PLACEHOLDER_WITHOUT_GAP',
          `Placeholder "${ph}" found in text but has no corresponding Gap`,
          `${path}.text`,
        ));
      }
    });

    // Gap exists but not referenced in text
    gapPlaceholders.forEach(ph => {
      if (!textPlaceholders.includes(ph)) {
        issues.push(error(
          'QUESTION_GAP_NOT_IN_TEXT',
          `Gap with placeholder "${ph}" is not referenced in question text`,
          `${path}.gaps`,
        ));
      }
    });

    if (!Array.isArray(q.gaps) || q.gaps.length === 0) {
      issues.push(error('QUESTION_NO_GAPS', 'Gap-type question has no gaps', `${path}.gaps`));
    } else {
      q.gaps.forEach((gap, i) => {
        issues.push(...validateGap(gap, `${path}.gaps[${i}]`, q.text));
      });
    }
  }

  if (q.type === QuestionType.SINGLE_CHOICE || q.type === QuestionType.MULTIPLE_CHOICE ||
      q.type === QuestionType.TRUE_FALSE) {
    if (!Array.isArray(q.options) || q.options.length === 0) {
      issues.push(error('QUESTION_NO_OPTIONS', 'Choice question has no options', `${path}.options`));
    } else {
      const correctCount = q.options.filter(o => o.correct).length;
      if (correctCount === 0) {
        issues.push(error('QUESTION_NO_CORRECT', 'No correct answer in choice question', `${path}.options`));
      }
      if (q.type === QuestionType.SINGLE_CHOICE && correctCount > 1) {
        issues.push(error(
          'QUESTION_SINGLE_CHOICE_MULTIPLE_CORRECT',
          `single_choice question has ${correctCount} correct options (must have exactly 1)`,
          `${path}.options`,
        ));
      }
      q.options.forEach((opt, i) => {
        issues.push(...validateOption(opt, `${path}.options[${i}]`));
      });
    }
  }

  return issues;
}

function validateExercise(ex, path) {
  const issues = [];

  if (!ex.id) {
    issues.push(error('EXERCISE_NO_ID', 'Exercise is missing an ID', `${path}.id`));
  }
  if (!ex.lessonId) {
    issues.push(error('EXERCISE_NO_LESSON_ID', 'Exercise has no lessonId', `${path}.lessonId`));
  }
  if (!Array.isArray(ex.questions) || ex.questions.length === 0) {
    issues.push(warning('EXERCISE_NO_QUESTIONS', 'Exercise has no questions', `${path}.questions`));
  } else {
    ex.questions.forEach((q, i) => {
      issues.push(...validateQuestion(q, `${path}.questions[${i}]`));
    });
  }

  return issues;
}

function validateLesson(lesson) {
  const issues = [];
  const path = `lesson[${lesson.id}]`;

  if (!lesson.id) {
    issues.push(error('LESSON_NO_ID', 'Lesson is missing an ID', `${path}.id`));
  }
  if (!lesson.title || !String(lesson.title).trim()) {
    issues.push(error('LESSON_NO_TITLE', 'Lesson has no title', `${path}.title`));
  }
  if (lesson.level && !Object.values(Level).includes(lesson.level)) {
    issues.push(warning('LESSON_UNKNOWN_LEVEL', `Unknown level: "${lesson.level}"`, `${path}.level`));
  }
  if (lesson.status && !Object.values(ContentStatus).includes(lesson.status)) {
    issues.push(warning('LESSON_UNKNOWN_STATUS', `Unknown status: "${lesson.status}"`, `${path}.status`));
  }
  if (!Array.isArray(lesson.exercises) || lesson.exercises.length === 0) {
    issues.push(warning('LESSON_NO_EXERCISES', 'Lesson has no exercises', `${path}.exercises`));
  } else {
    lesson.exercises.forEach((ex, i) => {
      issues.push(...validateExercise(ex, `${path}.exercises[${i}]`));
    });
  }

  return issues;
}

// ---------------------------------------------------------------------------
// PUBLIC API
// ---------------------------------------------------------------------------

/**
 * Validate a Universal Lesson JSON object.
 *
 * @param {import('../models/index.js').Lesson} lesson
 * @returns {ValidationResult}
 */
export function validate(lesson) {
  const issues  = validateLesson(lesson);
  const errors  = issues.filter(i => i.severity === Severity.ERROR);
  const warnings = issues.filter(i => i.severity === Severity.WARNING);
  const infos   = issues.filter(i => i.severity === Severity.INFO);

  return {
    valid:    errors.length === 0,
    issues,
    errors,
    warnings,
    infos,
  };
}

/**
 * Format validation results for console output.
 * @param {ValidationResult} result
 * @returns {string}
 */
export function formatResult(result) {
  const lines = [];

  if (result.valid) {
    lines.push('✅ Validation PASSED');
  } else {
    lines.push('❌ Validation FAILED');
  }

  lines.push('');

  if (result.errors.length > 0) {
    lines.push(`ERRORS (${result.errors.length}):`);
    result.errors.forEach(e => {
      lines.push(`  ✗ [${e.code}] ${e.message}${e.path ? ` → ${e.path}` : ''}`);
    });
    lines.push('');
  }

  if (result.warnings.length > 0) {
    lines.push(`WARNINGS (${result.warnings.length}):`);
    result.warnings.forEach(w => {
      lines.push(`  ⚠ [${w.code}] ${w.message}${w.path ? ` → ${w.path}` : ''}`);
    });
    lines.push('');
  }

  return lines.join('\n');
}
