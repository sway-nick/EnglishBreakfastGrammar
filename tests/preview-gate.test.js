/**
 * Preview Validation Gate & Guardrails Tests (ADR-002)
 *
 * Verifies that:
 * 1. Default strict mode blocks unresolved/invalid content from preview.
 * 2. allowUnresolved=true permits Rule 12A drafts only if structurally sound.
 * 3. Structural errors (duplicate options, missing ID) remain fatal even under allowUnresolved.
 * 4. --force is treated strictly as an explicit bypass flag and marked as isBypassed.
 * 5. CLI process execution enforces the validation gate.
 */

import { checkPreviewGate } from '../src/preview/server.js';
import {
  createLesson,
  createExercise,
  createQuestion,
  createGap,
  createOption,
  QuestionType,
  ContentStatus,
} from '../src/models/index.js';
import { execFileSync } from 'child_process';
import { resolve } from 'path';

// ── Helpers ───────────────────────────────────────────────────────────────

function makeValidLesson() {
  return createLesson({
    id: 'L001',
    title: 'Valid Lesson',
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
            text: 'I {{gap1}} a student.',
            gaps: [
              createGap({
                id: 'G001',
                order: 1,
                placeholder: '{{gap1}}',
                options: [
                  createOption({ id: 'O001', order: 1, value: 'am', is_correct: true }),
                  createOption({ id: 'O002', order: 2, value: 'is', is_correct: false }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function makeUnresolvedLesson() {
  return createLesson({
    id: 'L001',
    title: 'Unresolved Draft',
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
            text: 'I {{gap1}} a student.',
            gaps: [
              createGap({
                id: 'G001',
                order: 1,
                placeholder: '{{gap1}}',
                options: [
                  createOption({ id: 'O001', order: 1, value: 'am', is_correct: null }),
                  createOption({ id: 'O002', order: 2, value: 'is', is_correct: null }),
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

describe('Preview Validation Gate — checkPreviewGate()', () => {
  test('valid lesson passes gate cleanly without force', () => {
    const lesson = makeValidLesson();
    const gate = checkPreviewGate(lesson);

    expect(gate.valid).toBe(true);
    expect(gate.shouldBlock).toBe(false);
    expect(gate.isBypassed).toBe(false);
  });

  test('unresolved draft is blocked by default strict gate', () => {
    const lesson = makeUnresolvedLesson();
    const gate = checkPreviewGate(lesson);

    expect(gate.valid).toBe(false);
    expect(gate.shouldBlock).toBe(true);
    expect(gate.isBypassed).toBe(false);
  });

  test('unresolved draft passes gate when allowUnresolved is explicitly set', () => {
    const lesson = makeUnresolvedLesson();
    const gate = checkPreviewGate(lesson, { allowUnresolved: true });

    expect(gate.valid).toBe(true);
    expect(gate.shouldBlock).toBe(false);
    expect(gate.isBypassed).toBe(false);
  });

  test('structural error (duplicate options) stays blocked even with allowUnresolved: true', () => {
    const lesson = makeUnresolvedLesson();
    lesson.exercises[0].questions[0].gaps[0].options[1].value = 'am'; // duplicate value
    const gate = checkPreviewGate(lesson, { allowUnresolved: true });

    expect(gate.valid).toBe(false);
    expect(gate.shouldBlock).toBe(true);
    expect(gate.isBypassed).toBe(false);
  });

  test('structural error (missing lesson title) stays blocked even with allowUnresolved: true', () => {
    const lesson = makeUnresolvedLesson();
    lesson.title = '';
    const gate = checkPreviewGate(lesson, { allowUnresolved: true });

    expect(gate.valid).toBe(false);
    expect(gate.shouldBlock).toBe(true);
    expect(gate.isBypassed).toBe(false);
  });

  test('force=true permits bypassed startup but marks isBypassed: true and valid: false', () => {
    const lesson = makeUnresolvedLesson();
    const gate = checkPreviewGate(lesson, { force: true });

    expect(gate.valid).toBe(false);
    expect(gate.shouldBlock).toBe(false);
    expect(gate.isBypassed).toBe(true);
  });
});

describe('Preview Server CLI Validation Gate Integration', () => {
  const serverPath = resolve('src/preview/server.js');
  const samplePath = resolve('data/json/L001.json');

  beforeAll(async () => {
    const fs = await import('fs');
    fs.mkdirSync(resolve('data/json'), { recursive: true });
    fs.writeFileSync(samplePath, JSON.stringify(makeUnresolvedLesson(), null, 2), 'utf-8');
  });

  test('CLI blocks startup on unresolved data/json/L001.json without flags (exit 1)', () => {
    let exitedWithError = false;
    try {
      execFileSync(process.execPath, [serverPath, '--input', samplePath], {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
      });
    } catch (err) {
      exitedWithError = true;
      expect(err.status).toBe(1);
      expect(err.stderr || err.stdout).toContain('Preview startup blocked: lesson failed validation');
    }
    expect(exitedWithError).toBe(true);
  });

  test('CLI rejects execution when --input argument is missing (exit 1)', () => {
    let exitedWithError = false;
    try {
      execFileSync(process.execPath, [serverPath], {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
      });
    } catch (err) {
      exitedWithError = true;
      expect(err.status).toBe(1);
    }
    expect(exitedWithError).toBe(true);
  });
});
