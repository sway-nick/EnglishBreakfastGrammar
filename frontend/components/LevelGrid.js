import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderLevelGrid(catalog) {
  const completedMap = StorageService.getCompletedLessons();
  const favorites = StorageService.getFavorites();
  const levels = (catalog && catalog.levels) || [];
  const allLessons = (catalog && catalog.lessons) || [];

  const levelCardsHtml = levels.map(lvl => {
    const lvlLessons = allLessons.filter(l => l.level === lvl.id);
    const completedInLevel = lvlLessons.filter(l => completedMap[l.lesson_id]).length;
    const totalInLevel = lvlLessons.length || 1;
    const percent = Math.round((completedInLevel / totalInLevel) * 100);

    return `
      <div class="level-card" data-level-id="${lvl.id}">
        <div class="level-card-top">
          <span class="level-badge" style="background-color: ${lvl.color};">${lvl.id}</span>
        </div>
        <div class="level-card-title">${lvl.title}</div>
        <div class="level-card-progress">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${percent}%; background-color: ${lvl.color};"></div>
          </div>
          <div class="level-card-meta">
            <span>${completedInLevel}/${lvlLessons.length}</span>
            <span>${percent}%</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Favorites Tile
  const favLessons = allLessons.filter(l => favorites.includes(l.lesson_id));
  const favCount = favLessons.length;
  const favCardHtml = `
    <div class="level-card level-card-favorites" data-level-id="favorites">
      <div class="level-card-top">
        <span class="level-badge" style="background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);">⭐</span>
      </div>
      <div class="level-card-title">Favorites</div>
      <div class="level-card-progress">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${favCount > 0 ? '100%' : '0%'}; background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);"></div>
        </div>
        <div class="level-card-meta">
          <span>${favCount} ${t('lessons_count') || 'уроков'}</span>
          <span>⭐</span>
        </div>
      </div>
    </div>
  `;

  return `
    <div class="screen-view">
      <div class="level-grid">
        ${levelCardsHtml}
        ${favCardHtml}
      </div>
    </div>
  `;
}
