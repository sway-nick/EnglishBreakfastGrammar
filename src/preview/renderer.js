/**
 * Preview HTML Renderer
 *
 * Takes a Universal Lesson object and produces a fully self-contained HTML
 * preview page with an embedded Test Engine (JavaScript).
 *
 * The Test Engine in this file is deliberately simple — it demonstrates
 * the universal model working correctly. It does NOT depend on Test-English
 * IDs, WatuPRO, Google Sheets, or Firebase.
 */

import { QuestionType } from '../models/index.js';

/**
 * @param {import('../models/index.js').Lesson} lesson
 * @returns {string} Full HTML page
 */
export function renderPreviewHTML(lesson) {
  const exercisesHTML = lesson.exercises.map(renderExercise).join('\n');

  return /* html */`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Preview: ${esc(lesson.title)}</title>
  <style>
    /* ─── Reset & Base ────────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f7fa;
      color: #1a1a2e;
      min-height: 100vh;
    }

    /* ─── Layout ──────────────────────────────────────────────── */
    .preview-banner {
      background: #2563eb;
      color: #fff;
      text-align: center;
      padding: 8px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: .5px;
    }
    .lesson-header {
      background: #fff;
      border-bottom: 2px solid #e5e7eb;
      padding: 24px 32px;
    }
    .lesson-title { font-size: 26px; font-weight: 700; }
    .lesson-meta  { margin-top: 6px; font-size: 14px; color: #6b7280; }
    .lesson-meta span { margin-right: 16px; }

    .main { max-width: 800px; margin: 32px auto; padding: 0 16px 80px; }

    /* ─── Exercise ────────────────────────────────────────────── */
    .exercise {
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
      margin-bottom: 32px;
      padding: 28px 32px;
    }
    .exercise-title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
    .exercise-instruction {
      font-size: 14px;
      color: #4b5563;
      background: #f9fafb;
      border-left: 3px solid #2563eb;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      margin-bottom: 20px;
    }

    /* ─── Question ────────────────────────────────────────────── */
    .question { margin-bottom: 18px; }
    .question-text {
      font-size: 16px;
      line-height: 1.8;
    }
    .question-text select {
      font-size: 15px;
      padding: 2px 6px;
      border: 2px solid #d1d5db;
      border-radius: 6px;
      background: #fff;
      cursor: pointer;
      transition: border-color .15s;
    }
    .question-text select:focus {
      outline: none;
      border-color: #2563eb;
    }
    .question-text input[type=text] {
      font-size: 15px;
      padding: 2px 8px;
      border: 2px solid #d1d5db;
      border-radius: 6px;
      width: 120px;
      transition: border-color .15s;
    }
    .question-text input[type=text]:focus {
      outline: none;
      border-color: #2563eb;
    }

    /* Choice questions */
    .options-list { list-style: none; margin-top: 10px; }
    .options-list li { margin-bottom: 8px; }
    .options-list label {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 8px 12px;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      transition: border-color .15s, background .15s;
    }
    .options-list label:hover { background: #f0f4ff; border-color: #93c5fd; }

    /* ─── Feedback states ─────────────────────────────────────── */
    .gap-correct   { border-color: #22c55e !important; background: #f0fdf4 !important; }
    .gap-incorrect { border-color: #ef4444 !important; background: #fef2f2 !important; }
    .opt-correct   { background: #f0fdf4; border-color: #22c55e; }
    .opt-incorrect { background: #fef2f2; border-color: #ef4444; }
    .opt-missed    { background: #fffbeb; border-color: #f59e0b; }

    /* ─── Actions ─────────────────────────────────────────────── */
    .exercise-actions { margin-top: 20px; display: flex; gap: 12px; }
    .btn {
      padding: 10px 22px;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity .15s;
    }
    .btn:hover { opacity: .9; }
    .btn-primary { background: #2563eb; color: #fff; }
    .btn-secondary { background: #f3f4f6; color: #374151; }

    /* ─── Score ───────────────────────────────────────────────── */
    .score-panel {
      display: none;
      margin-top: 20px;
      padding: 18px 20px;
      background: #f9fafb;
      border-radius: 10px;
      border: 1px solid #e5e7eb;
    }
    .score-panel.show { display: block; }
    .score-total { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
    .score-breakdown { font-size: 14px; color: #6b7280; }
    .score-breakdown span { margin-right: 16px; }
  </style>
</head>
<body>

<div class="preview-banner">🔍 PREVIEW MODE — Data from local JSON, not Firebase</div>

<header class="lesson-header">
  <div class="lesson-title">${esc(lesson.title)}</div>
  <div class="lesson-meta">
    ${lesson.level ? `<span>📊 ${esc(lesson.level)}</span>` : ''}
    <span>📚 ${lesson.exercises.length} exercise${lesson.exercises.length !== 1 ? 's' : ''}</span>
    <span>❓ ${lesson.exercises.reduce((s, e) => s + e.questions.length, 0)} questions</span>
    <span style="color:#f59e0b">Status: ${esc(lesson.status)}</span>
  </div>
</header>

<main class="main">
  <div id="app">
    ${exercisesHTML}
  </div>
</main>

<script>
// ════════════════════════════════════════════════════════════════════════════
// Embedded Test Engine — reads the rendered DOM, not any external source.
// Source-agnostic: works with any Universal Model structure.
// ════════════════════════════════════════════════════════════════════════════

const LESSON = ${JSON.stringify(lesson, null, 0)};

function checkExercise(exerciseId) {
  const exercise = LESSON.exercises.find(e => e.id === exerciseId);
  if (!exercise) return;

  const panel = document.querySelector(\`#score-\${exerciseId}\`);
  let correct = 0, incorrect = 0, unanswered = 0;

  exercise.questions.forEach(q => {
    if (q.type === 'gap_select' || q.type === 'gap_text') {
      q.gaps.forEach(gap => {
        const el = document.querySelector(\`[data-gap-id="\${gap.id}"]\`);
        if (!el) return;
        const userValue = el.value?.trim() ?? '';
        const correctOption = gap.options.find(o => o.is_correct);
        const correctValue  = correctOption?.value ?? '';

        if (!userValue) {
          unanswered++;
          el.classList.remove('gap-correct', 'gap-incorrect');
        } else if (userValue.toLowerCase() === correctValue.toLowerCase()) {
          correct++;
          el.classList.add('gap-correct');
          el.classList.remove('gap-incorrect');
        } else {
          incorrect++;
          el.classList.add('gap-incorrect');
          el.classList.remove('gap-correct');
        }
      });
    }

    if (q.type === 'single_choice' || q.type === 'multiple_choice') {
      const inputs = document.querySelectorAll(\`[data-question-id="\${q.id}"] input\`);
      const correctIds = new Set(q.options.filter(o => o.is_correct).map(o => o.id));
      const selectedIds = new Set([...inputs].filter(i => i.checked).map(i => i.dataset.optionId));

      let questionCorrect = true;
      inputs.forEach(input => {
        const optId = input.dataset.optionId;
        const label = input.closest('label') || input.parentNode;
        label.classList.remove('opt-correct', 'opt-incorrect', 'opt-missed');

        const isCorrect  = correctIds.has(optId);
        const isSelected = selectedIds.has(optId);

        if (isSelected && isCorrect)    label.classList.add('opt-correct');
        if (isSelected && !isCorrect)  { label.classList.add('opt-incorrect'); questionCorrect = false; }
        if (!isSelected && isCorrect)   label.classList.add('opt-missed');
      });

      if (selectedIds.size === 0) {
        unanswered++;
      } else if (questionCorrect && selectedIds.size === correctIds.size) {
        correct++;
      } else {
        incorrect++;
      }
    }
  });

  const total = correct + incorrect + unanswered;
  panel.querySelector('.score-total').textContent = \`Score: \${correct} / \${total - unanswered}\`;
  panel.querySelector('.score-breakdown').innerHTML =
    \`<span>✅ Correct: \${correct}</span>\` +
    \`<span>❌ Incorrect: \${incorrect}</span>\` +
    \`<span>⬜ Unanswered: \${unanswered}</span>\`;
  panel.classList.add('show');
}

function resetExercise(exerciseId) {
  const exercise = LESSON.exercises.find(e => e.id === exerciseId);
  if (!exercise) return;

  exercise.questions.forEach(q => {
    if (q.type === 'gap_select' || q.type === 'gap_text') {
      q.gaps.forEach(gap => {
        const el = document.querySelector(\`[data-gap-id="\${gap.id}"]\`);
        if (el) {
          el.value = el.tagName === 'SELECT' ? '' : '';
          el.classList.remove('gap-correct', 'gap-incorrect');
        }
      });
    }
    if (q.type === 'single_choice' || q.type === 'multiple_choice') {
      document.querySelectorAll(\`[data-question-id="\${q.id}"] input\`).forEach(i => {
        i.checked = false;
        const label = i.closest('label') || i.parentNode;
        label.classList.remove('opt-correct', 'opt-incorrect', 'opt-missed');
      });
    }
  });

  document.querySelector(\`#score-\${exerciseId}\`).classList.remove('show');
}
</script>
</body>
</html>`;
}

// ── Exercise renderer ─────────────────────────────────────────────────────

function renderExercise(exercise) {
  const questionsHTML = exercise.questions.map(renderQuestion).join('\n');

  return /* html */`
<section class="exercise" id="ex-${esc(exercise.id)}">
  ${exercise.title ? `<h2 class="exercise-title">${esc(exercise.title)}</h2>` : ''}
  ${exercise.instruction ? `<div class="exercise-instruction">${esc(exercise.instruction)}</div>` : ''}
  <div class="questions">
    ${questionsHTML}
  </div>
  <div class="exercise-actions">
    <button class="btn btn-primary" onclick="checkExercise('${esc(exercise.id)}')">Check Answers</button>
    <button class="btn btn-secondary" onclick="resetExercise('${esc(exercise.id)}')">Reset</button>
  </div>
  <div class="score-panel" id="score-${esc(exercise.id)}">
    <div class="score-total"></div>
    <div class="score-breakdown"></div>
  </div>
</section>`;
}

// ── Question renderers ────────────────────────────────────────────────────

function renderQuestion(q) {
  switch (q.type) {
    case QuestionType.GAP_SELECT:
    case QuestionType.GAP_TEXT:
      return renderGapQuestion(q);
    case QuestionType.SINGLE_CHOICE:
    case QuestionType.MULTIPLE_CHOICE:
      return renderChoiceQuestion(q);
    default:
      return `<div class="question"><em>[Question type "${esc(q.type)}" preview not yet implemented]</em></div>`;
  }
}

function renderGapQuestion(q) {
  let html = esc(q.text);

  // Replace each {{gapN}} placeholder with the appropriate input
  q.gaps.forEach(gap => {
    const placeholder = gap.placeholder || `{{gap${gap.order}}}`;
    const inputHTML   = gap.options.length > 0
      ? renderSelectGap(gap)
      : renderTextGap(gap);

    html = html.replace(esc(placeholder), inputHTML);
  });

  return /* html */`
<div class="question" data-question-id="${esc(q.id)}" data-type="${esc(q.type)}">
  <div class="question-text">${html}</div>
  ${q.feedback ? `<div class="question-feedback" style="display:none">${esc(q.feedback)}</div>` : ''}
</div>`;
}

function renderSelectGap(gap) {
  const options = gap.options
    .map(o => `<option value="${esc(o.value)}">${esc(o.value)}</option>`)
    .join('');
  return `<select data-gap-id="${esc(gap.id)}"><option value="">—</option>${options}</select>`;
}

function renderTextGap(gap) {
  return `<input type="text" data-gap-id="${esc(gap.id)}" placeholder="…" autocomplete="off">`;
}

function renderChoiceQuestion(q) {
  const inputType = q.type === QuestionType.SINGLE_CHOICE ? 'radio' : 'checkbox';
  const groupName = `q-${q.id}`;

  const optionsHTML = q.options.map(o => /* html */`
    <li>
      <label>
        <input type="${inputType}" name="${esc(groupName)}" data-option-id="${esc(o.id)}" value="${esc(o.value)}">
        ${esc(o.value)}
      </label>
    </li>`
  ).join('');

  return /* html */`
<div class="question" data-question-id="${esc(q.id)}" data-type="${esc(q.type)}">
  <div class="question-text">${esc(q.text)}</div>
  <ul class="options-list">${optionsHTML}</ul>
  ${q.feedback ? `<div class="question-feedback" style="display:none">${esc(q.feedback)}</div>` : ''}
</div>`;
}

// ── Utility ───────────────────────────────────────────────────────────────

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
