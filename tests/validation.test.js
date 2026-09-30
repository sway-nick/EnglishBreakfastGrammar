/**
 * Validation tests — verifies that the validation module works correctly.
 * Verifies strict validation (default) and allowUnresolved mode (Rule 12A).
 * Run: npm test
 */

import { validate } from '../src/validation/index.js';
import {
  createLesson,
  createExercise,
  createQuestion,
  createGap,
  createOption,
  QuestionType,
  ContentStatus,
} from '../src/models/index.js';

// ── Helpers ───────────────────────────────────────────────────────────────

function makeValidGapLesson() {
  return createLesson({
    id: 'L001',
    title: 'Present Simple',
    level: 'A1',
    status: ContentStatus.DRAFT,
    exercises: [
      createExercise({
        id: 'E001',
        lessonId: 'L001',
        order: 1,
        questions: [
          createQuestion({
            id: 'Q001',
            order: 1,
            type: QuestionType.GAP_SELECT,
            text: 'A: {{gap1}} you a teacher? B: Yes, I {{gap2}}.',
            gaps: [
              createGap({
                id: 'G001',
                order: 1,
                placeholder: '{{gap1}}',
                options: [
                  createOption({ id: 'O001', order: 1, value: 'Are', is_correct: true }),
                  createOption({ id: 'O002', order: 2, value: 'is',  is_correct: false }),
                ],
              }),
              createGap({
                id: 'G002',
                order: 2,
                placeholder: '{{gap2}}',
                options: [
                  createOption({ id: 'O003', order: 1, value: 'am',  is_correct: true }),
                  createOption({ id: 'O004', order: 2, value: 'are', is_correct: false }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function makeUnresolvedGapLesson() {
  return createLesson({
    id: 'L001',
    title: 'Present Simple Draft',
    level: 'A1',
    status: ContentStatus.DRAFT,
    exercises: [
      createExercise({
        id: 'E001',
        lessonId: 'L001',
        order: 1,
        questions: [
          createQuestion({
            id: 'Q001',
            order: 1,
            type: QuestionType.GAP_SELECT,
            text: 'A: {{gap1}} you a teacher? B: Yes, I {{gap2}}.',
            gaps: [
              createGap({
                id: 'G001',
                order: 1,
                placeholder: '{{gap1}}',
                options: [
                  createOption({ id: 'O001', order: 1, value: 'Are', is_correct: null }),
                  createOption({ id: 'O002', order: 2, value: 'is',  is_correct: null }),
                ],
              }),
              createGap({
                id: 'G002',
                order: 2,
                placeholder: '{{gap2}}',
                options: [
                  createOption({ id: 'O003', order: 1, value: 'am',  is_correct: null }),
                  createOption({ id: 'O004', order: 2, value: 'are', is_correct: null }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

// ── Tests ─────────────────────────────────────────────────────────────────

describe('validate() — Strict Mode (Default)', () => {
  test('valid gap_select lesson passes', () => {
    const result = validate(makeValidGapLesson());
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('missing lesson ID → ERROR', () => {
    const lesson = makeValidGapLesson();
    lesson.id = '';
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'LESSON_NO_ID')).toBe(true);
  });

  test('gap with no correct answer → ERROR', () => {
    const lesson = makeValidGapLesson();
    lesson.exercises[0].questions[0].gaps[0].options.forEach(o => { o.is_correct = false; });
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'GAP_NO_CORRECT')).toBe(true);
  });

  test('placeholder in text but no gap → ERROR', () => {
    const lesson = makeValidGapLesson();
    lesson.exercises[0].questions[0].text = 'A: {{gap1}} you? B: Yes, I {{gap3}}.';
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'QUESTION_PLACEHOLDER_WITHOUT_GAP')).toBe(true);
  });

  test('duplicate option values → ERROR', () => {
    const lesson = makeValidGapLesson();
    lesson.exercises[0].questions[0].gaps[0].options[1].value = 'Are';
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'GAP_DUPLICATE_OPTION')).toBe(true);
  });

  test('single_choice with 2 correct → ERROR', () => {
    const lesson = createLesson({
      id: 'L002', title: 'Test', level: 'A1', status: ContentStatus.DRAFT,
      exercises: [createExercise({
        id: 'E001', lessonId: 'L002', order: 1,
        questions: [createQuestion({
          id: 'Q001', order: 1,
          type: QuestionType.SINGLE_CHOICE,
          text: 'Which is correct?',
          options: [
            createOption({ id: 'O001', order: 1, value: 'A', is_correct: true }),
            createOption({ id: 'O002', order: 2, value: 'B', is_correct: true }),
          ],
        })],
      })],
    });
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'QUESTION_SINGLE_CHOICE_MULTIPLE_CORRECT')).toBe(true);
  });

  test('unresolved answers (is_correct: null) fail in strict mode → ERROR', () => {
    const lesson = makeUnresolvedGapLesson();
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'OPTION_INVALID_IS_CORRECT')).toBe(true);
  });
});

describe('validate() — allowUnresolved Mode (Rule 12A / Raw Imports)', () => {
  test('unresolved draft lesson passes with allowUnresolved: true', () => {
    const lesson = makeUnresolvedGapLesson();
    const result = validate(lesson, { allowUnresolved: true });
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.infos.some(i => i.code === 'GAP_UNRESOLVED_ANSWERS')).toBe(true);
  });

  test('allowUnresolved: true still rejects duplicate options → ERROR', () => {
    const lesson = makeUnresolvedGapLesson();
    lesson.exercises[0].questions[0].gaps[0].options[1].value = 'Are';
    const result = validate(lesson, { allowUnresolved: true });
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'GAP_DUPLICATE_OPTION')).toBe(true);
  });

  test('allowUnresolved: true still rejects missing lesson ID → ERROR', () => {
    const lesson = makeUnresolvedGapLesson();
    lesson.id = '';
    const result = validate(lesson, { allowUnresolved: true });
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'LESSON_NO_ID')).toBe(true);
  });

  test('allowUnresolved: true still rejects placeholder in text without gap → ERROR', () => {
    const lesson = makeUnresolvedGapLesson();
    lesson.exercises[0].questions[0].text = 'A: {{gap1}} you? B: Yes, I {{gap99}}.';
    const result = validate(lesson, { allowUnresolved: true });
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'QUESTION_PLACEHOLDER_WITHOUT_GAP')).toBe(true);
  });

  test('allowUnresolved: true still rejects single_choice with multiple correct answers → ERROR', () => {
    const lesson = createLesson({
      id: 'L003', title: 'Test Choice', level: 'A1', status: ContentStatus.DRAFT,
      exercises: [createExercise({
        id: 'E001', lessonId: 'L003', order: 1,
        questions: [createQuestion({
          id: 'Q001', order: 1,
          type: QuestionType.SINGLE_CHOICE,
          text: 'Choose one:',
          options: [
            createOption({ id: 'O001', order: 1, value: 'A', is_correct: true }),
            createOption({ id: 'O002', order: 2, value: 'B', is_correct: true }),
          ],
        })],
      })],
    });
    const result = validate(lesson, { allowUnresolved: true });
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'QUESTION_SINGLE_CHOICE_MULTIPLE_CORRECT')).toBe(true);
  });
});
