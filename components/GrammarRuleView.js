import { t, getLanguage } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderGrammarRuleView(lesson) {
  const lessonObj = lesson || {};
  const isFav = StorageService.isFavorite(lessonObj.lesson_id);
  const rData = lessonObj._localizedRule || lessonObj.theory || {};

  const coreIdea = rData['Core idea'] || rData.overview || '';
  const mainRule = rData['Main rule / explanation'] || rData.main_rule || (rData.rules && rData.rules[0]?.content) || '';
  const formStructure = rData['Form / structure'] || rData.form || '';
  const whenWhy = rData['When / why we use it'] || rData.when_why || '';
  const examplesData = rData['Examples'] || rData.examples || '';
  const commonMistakes = rData['Common mistakes'] || rData.common_mistakes || '';
  const dontConfuse = rData["Don't confuse with"] || rData.dont_confuse || '';
  const specialCases = rData['Special cases / exceptions'] || rData.special_cases || '';
  const quickSummary = rData['Quick summary / memory hook'] || rData.quick_summary || '';

  const sections = [];

  if (coreIdea) {
    sections.push(`
      <div class="rule-card" style="border-left: 4px solid var(--primary-color);">
        <div class="rule-heading">
          <span>💡</span>
          <span>${getLanguage() === 'ru' ? 'Суть правила' : (getLanguage() === 'uk' ? 'Суть правила' : 'Core Idea')}</span>
        </div>
        <div class="rule-text" style="font-size: 15px; font-weight: 500; line-height: 1.5;">${coreIdea}</div>
      </div>
    `);
  }

  if (mainRule) {
    sections.push(`
      <div class="rule-card">
        <div class="rule-heading">
          <span>📖</span>
          <span>${getLanguage() === 'ru' ? 'Объяснение и правила' : (getLanguage() === 'uk' ? 'Пояснення та правила' : 'Main Explanation')}</span>
        </div>
        <div class="rule-text" style="white-space: pre-line; line-height: 1.55;">${mainRule}</div>
      </div>
    `);
  }

  if (formStructure) {
    sections.push(`
      <div class="rule-card" style="background: var(--bg-hover);">
        <div class="rule-heading">
          <span>📐</span>
          <span>${getLanguage() === 'ru' ? 'Формула / Конструкция' : (getLanguage() === 'uk' ? 'Формула / Конструкція' : 'Form & Structure')}</span>
        </div>
        <div class="rule-text" style="font-family: monospace; font-size: 14px; background: rgba(0,0,0,0.04); padding: 10px; border-radius: 8px; white-space: pre-line;">${formStructure}</div>
      </div>
    `);
  }

  if (whenWhy) {
    sections.push(`
      <div class="rule-card">
        <div class="rule-heading">
          <span>🎯</span>
          <span>${getLanguage() === 'ru' ? 'Когда и зачем используем' : (getLanguage() === 'uk' ? 'Коли та навіщо використовуємо' : 'When to Use')}</span>
        </div>
        <div class="rule-text" style="white-space: pre-line; line-height: 1.5;">${whenWhy}</div>
      </div>
    `);
  }

  if (examplesData) {
    const lines = String(examplesData).split('\n').filter(l => l.trim());
    const examplesHtml = lines.map(line => {
      if (line.includes('→')) {
        const [en, trans] = line.split('→').map(s => s.trim());
        return `
          <div style="margin-bottom: 8px; padding: 8px 10px; background: rgba(59, 130, 246, 0.07); border-radius: 8px;">
            <div style="font-weight: 700; color: var(--text-main); font-size: 14.5px;">${en}</div>
            <div style="color: var(--text-muted); font-size: 13.5px; margin-top: 2px;">${trans}</div>
          </div>
        `;
      }
      return `<div style="margin-bottom: 6px; font-size: 14px;">${line}</div>`;
    }).join('');

    sections.push(`
      <div class="rule-card">
        <div class="rule-heading">
          <span>💬</span>
          <span>${getLanguage() === 'ru' ? 'Примеры употребления' : (getLanguage() === 'uk' ? 'Приклади вживання' : 'Examples')}</span>
        </div>
        <div class="rule-text">${examplesHtml}</div>
      </div>
    `);
  }

  if (commonMistakes) {
    const mistakeLines = String(commonMistakes).split('\n').filter(l => l.trim());
    const mistakesListHtml = mistakeLines.map(line => {
      return `<div style="margin-bottom: 6px; font-size: 13.5px; line-height: 1.4;">${line}</div>`;
    }).join('');

    sections.push(`
      <div class="rule-card" style="border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.04);">
        <div class="rule-heading" style="color: #ef4444;">
          <span>⚠️</span>
          <span>${getLanguage() === 'ru' ? 'Типичные ошибки' : (getLanguage() === 'uk' ? 'Типові помилки' : 'Common Mistakes')}</span>
        </div>
        <div class="rule-text">${mistakesListHtml}</div>
      </div>
    `);
  }

  if (dontConfuse) {
    sections.push(`
      <div class="rule-card" style="border-left: 4px solid #f59e0b;">
        <div class="rule-heading" style="color: #d97706;">
          <span>🔍</span>
          <span>${getLanguage() === 'ru' ? 'С чем не путать' : (getLanguage() === 'uk' ? 'З чим не плутати' : "Don't Confuse With")}</span>
        </div>
        <div class="rule-text" style="white-space: pre-line;">${dontConfuse}</div>
      </div>
    `);
  }

  if (specialCases) {
    sections.push(`
      <div class="rule-card">
        <div class="rule-heading">
          <span>✨</span>
          <span>${getLanguage() === 'ru' ? 'Особые случаи и исключения' : (getLanguage() === 'uk' ? 'Особливі випадки та винятки' : 'Special Cases & Exceptions')}</span>
        </div>
        <div class="rule-text" style="white-space: pre-line;">${specialCases}</div>
      </div>
    `);
  }

  if (quickSummary) {
    sections.push(`
      <div class="rule-card" style="border: 1px dashed var(--primary-color); background: rgba(34, 197, 94, 0.05);">
        <div class="rule-heading" style="color: var(--primary-color);">
          <span>📌</span>
          <span>${getLanguage() === 'ru' ? 'Краткая памятка' : (getLanguage() === 'uk' ? 'Коротка пам’ятка' : 'Quick Summary')}</span>
        </div>
        <div class="rule-text" style="white-space: pre-line; font-weight: 500;">${quickSummary}</div>
      </div>
    `);
  }

  const rulesHtml = sections.length > 0 ? sections.join('') : `
    <div class="rule-card">
      <div class="rule-heading"><span>📖</span><span>${lessonObj.title || 'Правила урока'}</span></div>
      <div class="rule-text">Изучите конструкции и переходите к выполнению тестов.</div>
    </div>
  `;

  const overviewText = coreIdea || lessonObj.description || '';

  return `
    <div class="screen-view">
      <div class="screen-header-nav" style="display: flex; justify-content: space-between; align-items: center;">
        <button class="back-btn" id="btn-back-to-lesson-list">
          ← ${t('back_to_lessons')}
        </button>
        <button id="btn-toggle-favorite" class="header-fav-btn" data-lesson-id="${lessonObj.lesson_id || ''}" style="background: var(--bg-hover); border: 1px solid var(--border-color); border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; color: ${isFav ? '#f59e0b' : 'var(--text-muted)'};" title="Добавить в Избранное">
          ${isFav ? '⭐' : '☆'}
        </button>
      </div>

      <div style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="level-badge" style="background-color: var(--primary-color);">${lessonObj.level || 'A1'}</span>
          <h1 class="screen-title" style="font-size: 18px;">${lessonObj.title || 'Урок'}</h1>
        </div>
        <p class="screen-subtitle">${overviewText}</p>
      </div>

      <div class="theory-container" style="display: flex; flex-direction: column; gap: 14px;">
        ${rulesHtml}
      </div>

      <div class="bottom-floating-bar" style="margin-top: 24px;">
        <button class="btn-primary" id="btn-start-test-action" style="width: 100%; height: 48px; font-size: 16px; font-weight: 700; border-radius: 12px; background: var(--primary-color); color: #fff; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
          <span>⚡</span>
          <span>${t('start_test')}</span>
        </button>
      </div>
    </div>
  `;
}
