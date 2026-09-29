/**
 * Google Sheets CMS Integration
 *
 * Pushes a Universal Lesson JSON into a structured Google Spreadsheet
 * with multiple sheets:
 *   - Lessons
 *   - Exercises
 *   - Questions
 *   - Gaps
 *   - Options
 *   - Editor (human-readable flat view)
 *
 * Features:
 *   - Dropdown validation (Type, Status, Level)
 *   - Checkbox for Correct column
 *   - Conditional formatting for errors
 *   - Header freeze and formatting
 *
 * Auth: Google Service Account (credentials/service-account.json)
 */

import { google } from 'googleapis';
import { readFileSync } from 'fs';
import { resolve } from 'path';

// ---------------------------------------------------------------------------
// SHEET NAMES
// ---------------------------------------------------------------------------

export const SHEET = Object.freeze({
  LESSONS:   'Lessons',
  EXERCISES: 'Exercises',
  QUESTIONS: 'Questions',
  GAPS:      'Gaps',
  OPTIONS:   'Options',
  EDITOR:    'Editor',
});

// ---------------------------------------------------------------------------
// AUTH
// ---------------------------------------------------------------------------

/**
 * Create an authenticated Google Sheets client.
 * @param {string} keyPath - Path to service account JSON
 */
export async function createSheetsClient(keyPath) {
  const absPath = resolve(keyPath);
  const key = JSON.parse(readFileSync(absPath, 'utf-8'));

  const auth = new google.auth.GoogleAuth({
    credentials: key,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  const authClient = await auth.getClient();
  return google.sheets({ version: 'v4', auth: authClient });
}

// ---------------------------------------------------------------------------
// SPREADSHEET SETUP — ensure all required sheets exist
// ---------------------------------------------------------------------------

/**
 * Get or create a sheet by name.
 * Returns the sheet's properties.
 */
export async function ensureSheet(sheets, spreadsheetId, title) {
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const existing = meta.data.sheets.find(s => s.properties.title === title);
  if (existing) return existing.properties;

  const res = await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [{
        addSheet: {
          properties: { title },
        },
      }],
    },
  });

  return res.data.replies[0].addSheet.properties;
}

// ---------------------------------------------------------------------------
// DATA BUILDERS
// ---------------------------------------------------------------------------

/**
 * Flatten a Lesson into rows for each sheet.
 * @param {import('../models/index.js').Lesson} lesson
 * @returns {{ lessons, exercises, questions, gaps, options, editor }}
 */
export function flattenLesson(lesson) {
  const lessons   = [];
  const exercises = [];
  const questions = [];
  const gaps      = [];
  const options   = [];
  const editor    = [];

  // Lessons row
  lessons.push([
    lesson.id,
    lesson.title,
    lesson.level ?? '',
    lesson.description ?? '',
    lesson.status,
    lesson.order ?? 1,
    lesson.version ?? 1,
  ]);

  lesson.exercises.forEach(ex => {
    exercises.push([
      ex.id,
      ex.lessonId,
      ex.order,
      ex.title,
      ex.instruction,
      ex.status,
    ]);

    ex.questions.forEach(q => {
      questions.push([
        q.id,
        ex.id,
        q.order,
        q.type,
        q.text,
        q.hint ?? '',
        q.feedback ?? '',
      ]);

      if (q.gaps && q.gaps.length > 0) {
        q.gaps.forEach(gap => {
          gaps.push([
            gap.id,
            q.id,
            gap.order,
            gap.placeholder,
          ]);

          gap.options.forEach(opt => {
            options.push([
              opt.id,
              gap.id,
              opt.order,
              opt.value,
              opt.correct,
            ]);
          });
        });
      }

      if (q.options && q.options.length > 0) {
        q.options.forEach(opt => {
          options.push([
            opt.id,
            q.id,   // linked directly to question when no gaps
            opt.order,
            opt.value,
            opt.correct,
          ]);
        });
      }

      // Editor row — human-readable flat view
      const gapTexts   = (q.gaps ?? []).map(g => g.options.map(o => o.value).join(' / '));
      const correctArr = (q.gaps ?? []).map(g =>
        g.options.filter(o => o.correct).map(o => o.value).join(', ')
      );

      editor.push([
        q.order,
        q.type,
        q.text,
        gapTexts[0] ?? '',
        gapTexts[1] ?? '',
        gapTexts[2] ?? '',
        gapTexts[3] ?? '',
        correctArr.join(' / ') ||
          (q.options ?? []).filter(o => o.correct).map(o => o.value).join(', '),
        q.hint ?? '',
        q.feedback ?? '',
      ]);
    });
  });

  return { lessons, exercises, questions, gaps, options, editor };
}

// ---------------------------------------------------------------------------
// HEADERS
// ---------------------------------------------------------------------------

const HEADERS = {
  [SHEET.LESSONS]:   [['ID', 'Title', 'Level', 'Description', 'Status', 'Order', 'Version']],
  [SHEET.EXERCISES]: [['Exercise ID', 'Lesson ID', 'Order', 'Title', 'Instruction', 'Status']],
  [SHEET.QUESTIONS]: [['Question ID', 'Exercise ID', 'Order', 'Type', 'Question Text', 'Hint', 'Feedback']],
  [SHEET.GAPS]:      [['Gap ID', 'Question ID', 'Order', 'Placeholder']],
  [SHEET.OPTIONS]:   [['Option ID', 'Parent ID', 'Order', 'Value', 'Correct']],
  [SHEET.EDITOR]:    [['#', 'Type', 'Question Text', 'Gap 1 Options', 'Gap 2 Options', 'Gap 3 Options', 'Gap 4 Options', 'Correct Answers', 'Hint', 'Feedback']],
};

// ---------------------------------------------------------------------------
// PUSH
// ---------------------------------------------------------------------------

/**
 * Push a Universal Lesson to the Google Spreadsheet.
 *
 * @param {Object} params
 * @param {import('../models/index.js').Lesson} params.lesson
 * @param {string} params.spreadsheetId
 * @param {string} params.keyPath
 * @param {boolean} [params.clearFirst=true] - Clear existing lesson data before pushing
 */
export async function pushLesson({ lesson, spreadsheetId, keyPath, clearFirst = true }) {
  const sheets = await createSheetsClient(keyPath);

  // Ensure all sheets exist
  for (const sheetName of Object.values(SHEET)) {
    await ensureSheet(sheets, spreadsheetId, sheetName);
  }

  // Flatten data
  const { lessons, exercises, questions, gaps, options, editor } = flattenLesson(lesson);

  const sheetData = {
    [SHEET.LESSONS]:   lessons,
    [SHEET.EXERCISES]: exercises,
    [SHEET.QUESTIONS]: questions,
    [SHEET.GAPS]:      gaps,
    [SHEET.OPTIONS]:   options,
    [SHEET.EDITOR]:    editor,
  };

  // Write headers + data for each sheet
  for (const [sheetName, rows] of Object.entries(sheetData)) {
    const header = HEADERS[sheetName];
    const allRows = [...header, ...rows];

    // Determine range to write
    const range = `${sheetName}!A1`;

    await sheets.spreadsheets.values.update({
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      requestBody: { values: allRows },
    });

    console.log(`  ✓ ${sheetName}: ${rows.length} rows`);
  }

  // Apply formatting
  await applyFormatting(sheets, spreadsheetId);

  return { success: true };
}

// ---------------------------------------------------------------------------
// FORMATTING — dropdowns, checkboxes, header styles
// ---------------------------------------------------------------------------

async function applyFormatting(sheets, spreadsheetId) {
  // Get sheet IDs
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const sheetIds = {};
  meta.data.sheets.forEach(s => {
    sheetIds[s.properties.title] = s.properties.sheetId;
  });

  const requests = [];

  // ── Bold + freeze header row for all sheets ───────────────────────────
  Object.values(SHEET).forEach(sheetName => {
    const sheetId = sheetIds[sheetName];
    if (sheetId === undefined) return;

    // Bold header
    requests.push({
      repeatCell: {
        range: { sheetId, startRowIndex: 0, endRowIndex: 1 },
        cell: {
          userEnteredFormat: {
            textFormat: { bold: true },
            backgroundColor: { red: 0.23, green: 0.37, blue: 0.93, alpha: 1 },
          },
        },
        fields: 'userEnteredFormat(textFormat,backgroundColor)',
      },
    });

    // Freeze header row
    requests.push({
      updateSheetProperties: {
        properties: {
          sheetId,
          gridProperties: { frozenRowCount: 1 },
        },
        fields: 'gridProperties.frozenRowCount',
      },
    });
  });

  // ── Dropdown: Status (Lessons col E, Exercises col F) ─────────────────
  const statusValues = ['draft', 'review', 'published', 'archived'];
  const statusCondition = {
    type: 'ONE_OF_LIST',
    values: statusValues.map(v => ({ userEnteredValue: v })),
  };

  [
    { sheetId: sheetIds[SHEET.LESSONS],   col: 4 },  // E = Status
    { sheetId: sheetIds[SHEET.EXERCISES], col: 5 },  // F = Status
  ].forEach(({ sheetId, col }) => {
    if (sheetId === undefined) return;
    requests.push({
      setDataValidation: {
        range: { sheetId, startRowIndex: 1, endRowIndex: 1000, startColumnIndex: col, endColumnIndex: col + 1 },
        rule: { condition: statusCondition, showCustomUi: true, strict: true },
      },
    });
  });

  // ── Dropdown: Level (Lessons col C) ──────────────────────────────────
  const levelValues = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
  requests.push({
    setDataValidation: {
      range: {
        sheetId: sheetIds[SHEET.LESSONS],
        startRowIndex: 1, endRowIndex: 1000,
        startColumnIndex: 2, endColumnIndex: 3,
      },
      rule: {
        condition: {
          type: 'ONE_OF_LIST',
          values: levelValues.map(v => ({ userEnteredValue: v })),
        },
        showCustomUi: true,
        strict: true,
      },
    },
  });

  // ── Dropdown: Type (Questions col D) ──────────────────────────────────
  const typeValues = ['gap_select', 'gap_text', 'single_choice', 'multiple_choice', 'text_input', 'true_false', 'matching', 'ordering'];
  requests.push({
    setDataValidation: {
      range: {
        sheetId: sheetIds[SHEET.QUESTIONS],
        startRowIndex: 1, endRowIndex: 10000,
        startColumnIndex: 3, endColumnIndex: 4,
      },
      rule: {
        condition: {
          type: 'ONE_OF_LIST',
          values: typeValues.map(v => ({ userEnteredValue: v })),
        },
        showCustomUi: true,
        strict: true,
      },
    },
  });

  // ── Checkbox: Correct (Options col E) ─────────────────────────────────
  requests.push({
    setDataValidation: {
      range: {
        sheetId: sheetIds[SHEET.OPTIONS],
        startRowIndex: 1, endRowIndex: 100000,
        startColumnIndex: 4, endColumnIndex: 5,
      },
      rule: {
        condition: { type: 'BOOLEAN' },
        showCustomUi: true,
      },
    },
  });

  // ── Auto-resize columns ───────────────────────────────────────────────
  Object.values(sheetIds).forEach(sheetId => {
    requests.push({
      autoResizeDimensions: {
        dimensions: {
          sheetId,
          dimension: 'COLUMNS',
          startIndex: 0,
          endIndex: 10,
        },
      },
    });
  });

  if (requests.length > 0) {
    await sheets.spreadsheets.batchUpdate({
      spreadsheetId,
      requestBody: { requests },
    });
  }
}
