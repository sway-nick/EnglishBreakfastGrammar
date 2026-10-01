import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderLessonList(levelId, catalog) {
  const isFavorites = levelId === 'favorites';
  const completedMap = StorageService.getCompletedLessons();
  const favorites = StorageService.getFavorites();

  let levelInfo;
  let lessons;

  if (isFavorites) {
    levelInfo = { id: '⭐', title: 'Favorites', color: '#f59e0b' };
    lessons = (catalog.lessons || []).filter(l => favorites.includes(l.lesson_id));
  } else {
    levelInfo = (catalog.levels || []).find(l => l.id === levelId) || { id: levelId, title: levelId, color: '#22c55e' };
    lessons = (catalog.lessons || []).filter(l => l.level === levelId);
  }

  let lessonsHtml = '';

  if (lessons.length === 0) {
    if (isFavorites) {
      lessonsHtml = `
        <div class="empty-state-card" style="text-align: center; padding: 40px 20px; background: var(--card-bg); border: 1.5px solid var(--border-color); border-radius: 16px;">
          <div style="font-size: 40px; margin-bottom: 12px;">⭐</div>
          <h3 style="font-size: 17px; font-weight: 800; margin-bottom: 6px; color: var(--text-main);">Нет избранных тем</h3>
          <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.5; max-width: 280px; margin: 0 auto;">
            Нажмите на звёздочку ⭐ в правом верхнем углу любого урока, чтобы добавить его сюда.
          </p>
        </div>
      `;
    } else {
      lessonsHtml = `
        <div class="empty-state-card" style="text-align: center; padding: 30px; background: var(--card-bg); border-radius: 16px;">
          <p style="color: var(--text-muted);">Уроки скоро появятся</p>
        </div>
      `;
    }
  } else {
    lessonsHtml = lessons.map(lesson => {
      const isDone = Boolean(completedMap[lesson.lesson_id]);
      const score = isDone ? completedMap[lesson.lesson_id].score : null;
      const isFav = favorites.includes(lesson.lesson_id);

      return `
        <div class="lesson-card" data-lesson-id="${lesson.lesson_id}">
          <div class="lesson-info">
            <div class="lesson-title">${lesson.title}</div>
            <div class="lesson-meta">
              <span>${lesson.questions_count || 10} ${t('questions_count')}</span>
              <span class="lesson-badge-status ${isDone ? 'completed' : ''}">
                ${isDone ? `✓ ${t('status_completed')} (${score}%)` : t('status_new')}
              </span>
              ${isFav ? `<span style="color: #f59e0b; font-size: 12px;">⭐</span>` : ''}
            </div>
          </div>
          <div class="lesson-arrow">›</div>
        </div>
      `;
    }).join('');
  }

  return `
    <div class="screen-view">
      <div class="screen-header-nav">
        <button class="back-btn" id="btn-back-to-levels">
          ← ${t('back_to_levels')}
        </button>
      </div>
      <div style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="level-badge" style="background-color: ${levelInfo.color};">${levelInfo.id}</span>
          <h2 class="screen-title" style="font-size: 18px;">${levelInfo.title}</h2>
        </div>
        <p class="screen-subtitle">${lessons.length} ${t('lessons_count')}</p>
      </div>
      <div class="lessons-grid">
        ${lessonsHtml}
      </div>
    </div>
  `;
}
