import { t } from '../services/i18n.js';
import { GrammarService } from '../services/grammarService.js';
import { StorageService } from '../services/storageService.js';

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function replaceGapInText(text, gap, gapIdx, inputHtml) {
  const gapNum = gap.order || (gapIdx + 1);
  const patterns = [];

  if (gap.placeholder && gap.placeholder.trim()) {
    patterns.push(new RegExp(escapeRegex(gap.placeholder.trim()), 'i'));
  }
  patterns.push(new RegExp('\\{\\{\\s*gap' + gapNum + '\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\[\\s*gap' + gapNum + '\\s*\\]', 'i'));
  patterns.push(new RegExp('\\[\\s*' + gapNum + '\\s*\\]', 'i'));
  patterns.push(new RegExp('\\{\\{\\s*' + gapNum + '\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\{\\{\\s*gap\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\[\\s*gap\\s*\\]', 'i'));
  patterns.push(/_{2,}/);
  patterns.push(/\{\{[^}]+\}\}/);

  for (const pat of patterns) {
    if (pat.test(text)) {
      return text.replace(pat, inputHtml);
    }
  }

  return text + ' ' + inputHtml;
}

export function renderTestEngine(lesson) {
  const lessonObj = lesson || {};
  const exercises = lessonObj.exercises || [];

  let totalQuestionsCount = 0;

  const exercisesHtml = exercises.map((ex, exIdx) => {
    const exId = ex.id || ex.exercise_id || (`ex_${exIdx + 1}`);
    const questions = ex.questions || [];
    totalQuestionsCount += questions.length;

    const questionsHtml = questions.map((q, qIdx) => {
      const qId = q.id || q.question_id || (`q_${qIdx + 1}`);
      let contentHtml = '';

      // Clean leading number like "1 ", "1. ", "1) " from sentence if present
      let rawText = q.text || q.prompt || q.sentence || '';
      let cleanText = rawText.replace(new RegExp(`^\\s*${qIdx + 1}[.)\\s]+\\s*`), '');

      // Case 1: Gap Fill questions (Text or Select)
      if (q.gaps && q.gaps.length > 0) {
        let textWithGaps = cleanText;

        q.gaps.forEach((gap, gIdx) => {
          const gapId = gap.id || gap.gap_id || (`gap_${qId}_${gIdx + 1}`);
          let inputHtml = '';

          const hasOptions = Array.isArray(gap.options) && gap.options.length > 0;
          const isSelect = gap.input_control === 'select' || (hasOptions && gap.input_control !== 'text');

          if (isSelect && hasOptions) {
            const opts = gap.options.map(opt => {
              const val = typeof opt === 'object' ? (opt.text ?? opt.value ?? '') : opt;
              return `<option value="${val}">${val}</option>`;
            }).join('');

            inputHtml = `
              <select class="gap-select inline-gap-select" data-exercise-id="${exId}" data-question-id="${qId}" data-gap-id="${gapId}">
                <option value="">— ? —</option>
                ${opts}
              </select>
            `;
          } else {
            const placeholder = gap.placeholder && !gap.placeholder.startsWith('{{') ? gap.placeholder : '...';
            inputHtml = `
              <input type="text" class="gap-input inline-gap-input" data-exercise-id="${exId}" data-question-id="${qId}" data-gap-id="${gapId}" placeholder="${placeholder}" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />
            `;
          }

          textWithGaps = replaceGapInText(textWithGaps, gap, gIdx, inputHtml);
        });

        contentHtml = `<div class="question-prompt inline-gap-prompt">${textWithGaps}</div>`;
      } 
      // Case 2: Single Choice or Multiple Choice
      else if (q.options && q.options.length > 0) {
        const isMulti = q.response_model === 'multiple_choice' || q.type === 'multiple_choice';
        const type = isMulti ? 'checkbox' : 'radio';
        const name = `q_${qId}`;

        const optsHtml = q.options.map(opt => {
          const optId = opt.id || opt.option_id || opt.value || opt.text;
          const optText = opt.text || opt.value || '';
          return `
            <label class="choice-label" data-exercise-id="${exId}" data-question-id="${qId}" data-option-id="${optId}">
              <input type="${type}" name="${name}" value="${optId}" class="choice-${type}" data-exercise-id="${exId}" data-question-id="${qId}" data-option-id="${optId}" />
              <span>${optText}</span>
            </label>
          `;
        }).join('');

        contentHtml = `
          <div class="question-prompt">${cleanText}</div>
          <div class="choice-options-grid">${optsHtml}</div>
        `;
      } else {
        contentHtml = `<div class="question-prompt">${cleanText}</div>`;
      }

      return `
        <div class="question-item" data-exercise-id="${exId}" data-question-id="${qId}">
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px;">Вопрос ${qIdx + 1}</div>
          ${contentHtml}
          <div class="answer-feedback" id="feedback-${qId}" style="display: none;"></div>
        </div>
      `;
    }).join('');

    return `
      <div class="exercise-block" data-exercise-id="${exId}">
        <div class="exercise-header" style="margin-bottom: 14px;">
          <div class="exercise-title">${ex.title || `Упражнение ${exIdx + 1}`}</div>
          ${ex.instruction ? `<div class="exercise-instruction" style="margin-bottom: 0;">${ex.instruction}</div>` : ''}
        </div>

        <div class="exercise-questions">
          ${questionsHtml}
        </div>

        <div class="exercise-actions" style="margin-top: 18px; padding-top: 14px; border-top: 1px dashed var(--border-color); display: flex; flex-direction: column; gap: 10px;">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <button class="btn-primary btn-check-exercise" data-exercise-id="${exId}" style="width: auto; min-width: 200px; padding: 10px 22px;">
              <span>✓</span>
              <span>${t('check_answers')}</span>
            </button>
            <div class="exercise-score-badge" id="ex-badge-${exId}" style="display: none; font-size: 14px; font-weight: 700; padding: 8px 14px; border-radius: 8px;"></div>
          </div>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="screen-view">
      <div class="screen-header-nav">
        <button class="back-btn" id="btn-back-to-theory">
          ← ${t('read_rules')}
        </button>
      </div>

      <div class="test-progress-header">
        <div>
          <h2 class="screen-title" style="font-size: 18px;">${lesson.title}</h2>
          <p class="screen-subtitle">Тест • ${totalQuestionsCount} ${t('questions_count')}</p>
        </div>
      </div>

      <div class="test-container" id="test-questions-container" style="display: flex; flex-direction: column; gap: 20px;">
        ${exercisesHtml}
      </div>
    </div>
  `;
}
