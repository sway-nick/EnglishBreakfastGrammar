import { t } from '../services/i18n.js';

export function renderGrammarRuleView(lesson) {
  const theory = lesson.theory || {};
  const rules = theory.rules || [];

  const rulesHtml = rules.map((r, idx) => {
    let tableHtml = '';
    if (r.table && r.table.headers && r.table.rows) {
      const ths = r.table.headers.map(h => `<th>${h}</th>`).join('');
      const trs = r.table.rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('');
      tableHtml = `
        <table class="syntax-table">
          <thead><tr>${ths}</tr></thead>
          <tbody>${trs}</tbody>
        </table>
      `;
    }

    let tipsHtml = '';
    if (r.tips && r.tips.length > 0) {
      tipsHtml = `
        <div class="tips-box">
          <strong>💡 Полезно знать:</strong>
          <ul style="margin-top: 6px;">
            ${r.tips.map(tip => `<li>${tip}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    return `
      <div class="rule-card">
        <div class="rule-heading">
          <span>📖</span>
          <span>${r.heading || `Правило #${idx + 1}`}</span>
        </div>
        <div class="rule-text">${r.content || ''}</div>
        ${tableHtml}
        ${tipsHtml}
      </div>
    `;
  }).join('');

  return `
    <div class="screen-view">
      <div class="screen-header-nav">
        <button class="back-btn" id="btn-back-to-lesson-list">
          ← ${t('back_to_lessons')}
        </button>
      </div>

      <div style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="level-badge" style="background-color: var(--primary-color);">${lesson.level}</span>
          <h1 class="screen-title" style="font-size: 18px;">${lesson.title}</h1>
        </div>
        <p class="screen-subtitle">${theory.overview || lesson.description || ''}</p>
      </div>

      <div class="theory-container">
        ${rulesHtml}
      </div>

      <div class="bottom-floating-bar">
        <button class="btn-primary" id="btn-start-test-action">
          <span>⚡</span>
          <span>${t('start_test')}</span>
        </button>
      </div>
    </div>
  `;
}
