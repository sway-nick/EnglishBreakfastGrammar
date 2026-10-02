import { t, getLanguage } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderGrammarRuleView(lesson) {
  const isFav = StorageService.isFavorite(lesson.lesson_id);
  const locRule = lesson._localizedRule;

  let rulesHtml = '';

  if (locRule) {
    const sections = [];

    if (locRule['Core idea']) {
      sections.push(`
        <div class="rule-card" style="border-left: 4px solid var(--primary-color);">
          <div class="rule-heading">
            <span>💡</span>
            <span>${getLanguage() === 'ru' ? 'Суть правила' : (getLanguage() === 'uk' ? 'Суть правила' : 'Core Idea')}</span>
          </div>
          <div class="rule-text" style="font-size: 15px; font-weight: 500; line-height: 1.5;">${locRule['Core idea']}</div>
        </div>
      `);
    }

    if (locRule['Main rule / explanation']) {
      sections.push(`
        <div class="rule-card">
          <div class="rule-heading">
            <span>📖</span>
            <span>${getLanguage() === 'ru' ? 'Объяснение и правила' : (getLanguage() === 'uk' ? 'Пояснення та правила' : 'Main Explanation')}</span>
          </div>
          <div class="rule-text" style="white-space: pre-line; line-height: 1.55;">${locRule['Main rule / explanation']}</div>
        </div>
      `);
    }

    if (locRule['Form / structure']) {
      sections.push(`
        <div class="rule-card" style="background: var(--bg-hover);">
          <div class="rule-heading">
            <span>📐</span>
            <span>${getLanguage() === 'ru' ? 'Формула / Конструкция' : (getLanguage() === 'uk' ? 'Формула / Конструкція' : 'Form & Structure')}</span>
          </div>
          <div class="rule-text" style="font-family: monospace; font-size: 14px; background: rgba(0,0,0,0.04); padding: 10px; border-radius: 8px; white-space: pre-line;">${locRule['Form / structure']}</div>
        </div>
      `);
    }

    if (locRule['When / why we use it']) {
      sections.push(`
        <div class="rule-card">
          <div class="rule-heading">
            <span>🎯</span>
            <span>${getLanguage() === 'ru' ? 'Когда и зачем используем' : (getLanguage() === 'uk' ? 'Коли та навіщо використовуємо' : 'When to Use')}</span>
          </div>
          <div class="rule-text" style="white-space: pre-line; line-height: 1.5;">${locRule['When / why we use it']}</div>
        </div>
      `);
    }

    if (locRule['Examples']) {
      const lines = String(locRule['Examples']).split('\n').filter(l => l.trim());
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

    if (locRule['Common mistakes']) {
      const mistakeLines = String(locRule['Common mistakes']).split('\n').filter(l => l.trim());
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

    if (locRule["Don't confuse with"]) {
      sections.push(`
        <div class="rule-card" style="border-left: 4px solid #f59e0b;">
          <div class="rule-heading" style="color: #d97706;">
            <span>🔍</span>
            <span>${getLanguage() === 'ru' ? 'С чем не путать' : (getLanguage() === 'uk' ? 'З чим не плутати' : "Don't Confuse With")}</span>
          </div>
          <div class="rule-text" style="white-space: pre-line;">${locRule["Don't confuse with"]}</div>
        </div>
      `);
    }

    if (locRule['Special cases / exceptions']) {
      sections.push(`
        <div class="rule-card">
          <div class="rule-heading">
            <span>✨</span>
            <span>${getLanguage() === 'ru' ? 'Особые случаи и исключения' : (getLanguage() === 'uk' ? 'Особливі випадки та винятки' : 'Special Cases & Exceptions')}</span>
          </div>
          <div class="rule-text" style="white-space: pre-line;">${locRule['Special cases / exceptions']}</div>
        </div>
      `);
    }

    if (locRule['Quick summary / memory hook']) {
      sections.push(`
        <div class="rule-card" style="border: 1px dashed var(--primary-color); background: rgba(34, 197, 94, 0.05);">
          <div class="rule-heading" style="color: var(--primary-color);">
            <span>📌</span>
            <span>${getLanguage() === 'ru' ? 'Краткая памятка' : (getLanguage() === 'uk' ? 'Коротка пам’ятка' : 'Quick Summary')}</span>
          </div>
          <div class="rule-text" style="white-space: pre-line; font-weight: 500;">${locRule['Quick summary / memory hook']}</div>
        </div>
      `);
    }

    rulesHtml = sections.join('');
  } else {
    // Fallback theory
    const theory = (lesson && lesson.theory) || {};
    const fallbackRules = theory.rules || [];
    rulesHtml = fallbackRules.map((r, idx) => `
      <div class="rule-card">
        <div class="rule-heading">
          <span>📖</span>
          <span>${r.heading || `Правило #${idx + 1}`}</span>
        </div>
        <div class="rule-text">${r.content || ''}</div>
      </div>
    `).join('');
  }

  const overviewText = locRule ? locRule['Core idea'] : (lesson.theory?.overview || lesson.description || '');

  return `
    <div class="screen-view">
      <div class="screen-header-nav" style="display: flex; justify-content: space-between; align-items: center;">
        <button class="back-btn" id="btn-back-to-lesson-list">
          ← ${t('back_to_lessons')}
        </button>
        <button id="btn-toggle-favorite" class="header-fav-btn" data-lesson-id="${lesson.lesson_id}" style="background: var(--bg-hover); border: 1px solid var(--border-color); border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; color: ${isFav ? '#f59e0b' : 'var(--text-muted)'};" title="Добавить в Избранное">
          ${isFav ? '⭐' : '☆'}
        </button>
      </div>

      <div style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="level-badge" style="background-color: var(--primary-color);">${lesson.level}</span>
          <h1 class="screen-title" style="font-size: 18px;">${lesson.title}</h1>
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
