import { t } from '../services/i18n.js';
import { GrammarService } from '../services/grammarService.js';
import { StorageService } from '../services/storageService.js';

export function renderTestEngine(lesson) {
  const exercises = lesson.exercises || [];

  let totalQuestionsCount = 0;

  const exercisesHtml = exercises.map((ex, exIdx) => {
    const questions = ex.questions || [];
    totalQuestionsCount += questions.length;

    const questionsHtml = questions.map((q, qIdx) => {
      let contentHtml = '';

      // Case 1: Gap Fill questions (Text or Select)
      if (q.gaps && q.gaps.length > 0) {
        let textWithGaps = q.prompt || q.sentence || q.text || '';
        
        q.gaps.forEach(gap => {
          const gapId = gap.gap_id;
          let inputHtml = '';
          if (gap.input_control === 'select' && gap.options && gap.options.length > 0) {
            const opts = gap.options.map(opt => `<option value="${opt.text || opt}">${opt.text || opt}</option>`).join('');
            inputHtml = `
              <select class="gap-select" data-question-id="${q.question_id}" data-gap-id="${gapId}">
                <option value="">— ? —</option>
                ${opts}
              </select>
            `;
          } else {
            const placeholder = gap.placeholder || '...';
            inputHtml = `
              <input type="text" class="gap-input" data-question-id="${q.question_id}" data-gap-id="${gapId}" placeholder="${placeholder}" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />
            `;
          }

          // Replace placeholder token in sentence
          const tokenRegex = new RegExp(`(\\[${gapId}\\]|\\{\\{${gapId}\\}\\}|___|\\{\\{\\s*gap\\s*\\}\\})`, 'i');
          if (tokenRegex.test(textWithGaps)) {
            textWithGaps = textWithGaps.replace(tokenRegex, inputHtml);
          } else {
            textWithGaps += ' ' + inputHtml;
          }
        });

        contentHtml = `<div class="question-prompt">${textWithGaps}</div>`;
      } 
      // Case 2: Single Choice or Multiple Choice
      else if (q.options && q.options.length > 0) {
        const isMulti = q.response_model === 'multiple_choice';
        const type = isMulti ? 'checkbox' : 'radio';
        const name = `q_${q.question_id}`;

        const optsHtml = q.options.map(opt => `
          <label class="choice-label" data-option-id="${opt.option_id}">
            <input type="${type}" name="${name}" value="${opt.option_id}" class="choice-${type}" data-question-id="${q.question_id}" data-option-id="${opt.option_id}" />
            <span>${opt.text}</span>
          </label>
        `).join('');

        contentHtml = `
          <div class="question-prompt">${q.prompt || q.text || ''}</div>
          <div class="choice-options-grid">${optsHtml}</div>
        `;
      } else {
        contentHtml = `<div class="question-prompt">${q.prompt || q.text || ''}</div>`;
      }

      return `
        <div class="question-item" data-question-id="${q.question_id}">
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px;">Вопрос ${qIdx + 1}</div>
          ${contentHtml}
          <div class="answer-feedback" id="feedback-${q.question_id}" style="display: none;"></div>
        </div>
      `;
    }).join('');

    return `
      <div class="exercise-block" data-exercise-id="${ex.exercise_id}">
        <div class="exercise-title">${ex.title || `Упражнение ${exIdx + 1}`}</div>
        <div class="exercise-instruction">${ex.instruction || 'Заполните пропуски или выберите правильный ответ.'}</div>
        ${questionsHtml}
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

      <div class="test-container" id="test-questions-container">
        ${exercisesHtml}
      </div>

      <div class="bottom-floating-bar">
        <button class="btn-primary" id="btn-check-test-answers">
          <span>✓</span>
          <span>${t('check_answers')}</span>
        </button>
      </div>
    </div>
  `;
}
