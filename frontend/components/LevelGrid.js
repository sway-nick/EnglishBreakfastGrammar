import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderLevelGrid(catalog) {
  const completedMap = StorageService.getCompletedLessons();
  const levels = catalog.levels || [];
  const allLessons = catalog.lessons || [];

  const cardsHtml = levels.map(lvl => {
    const lvlLessons = allLessons.filter(l => l.level === lvl.id);
    const completedInLevel = lvlLessons.filter(l => completedMap[l.lesson_id]).length;
    const totalInLevel = lvlLessons.length || 1;
    const percent = Math.round((completedInLevel / totalInLevel) * 100);

    return `
      <div class="level-card" data-level-id="${lvl.id}">
        <div class="level-card-top">
          <span class="level-badge" style="background-color: ${lvl.color};">${lvl.id}</span>
          <span class="level-icon">${lvl.icon}</span>
        </div>
        <div>
          <div class="level-card-title">${lvl.title}</div>
          <div class="level-card-desc">${lvl.description}</div>
        </div>
        <div class="level-card-progress">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${percent}%; background-color: ${lvl.color};"></div>
          </div>
          <div class="level-card-meta">
            <span>${completedInLevel} / ${lvlLessons.length} ${t('lessons_count')}</span>
            <span>${percent}%</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="screen-view">
      <div class="screen-header-nav" style="margin-bottom: 20px;">
        <div>
          <h1 class="screen-title">${t('levels_title')}</h1>
          <p class="screen-subtitle">${t('levels_subtitle')}</p>
        </div>
      </div>
      <div class="level-grid">
        ${cardsHtml}
      </div>
    </div>
  `;
}
