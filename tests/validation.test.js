/**
 * Sample test — verifies that the validation module works correctly.
 * Run: node --experimental-vm-modules node_modules/.bin/jest
 */

import { validate } from '../src/validation/index.js';
import { createLesson, createExercise, createQuestion, createGap, createOption, QuestionType, ContentStatus } from '../src/models/index.js';

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
                  createOption({ id: 'O001', order: 1, value: 'Are', correct: true }),
                  createOption({ id: 'O002', order: 2, value: 'is',  correct: false }),
                ],
              }),
              createGap({
                id: 'G002',
                order: 2,
                placeholder: '{{gap2}}',
                options: [
                  createOption({ id: 'O003', order: 1, value: 'am',  correct: true }),
                  createOption({ id: 'O004', order: 2, value: 'are', correct: false }),
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

describe('validate()', () => {
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
    lesson.exercises[0].questions[0].gaps[0].options.forEach(o => { o.correct = false; });
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
            createOption({ id: 'O001', order: 1, value: 'A', correct: true }),
            createOption({ id: 'O002', order: 2, value: 'B', correct: true }),
          ],
        })],
      })],
    });
    const result = validate(lesson);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.code === 'QUESTION_SINGLE_CHOICE_MULTIPLE_CORRECT')).toBe(true);
  });
});
