import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderLessonList(levelId, catalog) {
  const levelInfo = (catalog.levels || []).find(l => l.id === levelId) || { id: levelId, title: levelId, color: '#22c55e' };
  const lessons = (catalog.lessons || []).filter(l => l.level === levelId);
  const completedMap = StorageService.getCompletedLessons();

  const lessonsHtml = lessons.map(lesson => {
    const isDone = Boolean(completedMap[lesson.lesson_id]);
    const score = isDone ? completedMap[lesson.lesson_id].score : null;

    return `
      <div class="lesson-card" data-lesson-id="${lesson.lesson_id}">
        <div class="lesson-info">
          <div class="lesson-title">${lesson.title}</div>
          <div class="lesson-meta">
            <span>${lesson.questions_count || 10} ${t('questions_count')}</span>
            <span class="lesson-badge-status ${isDone ? 'completed' : ''}">
              ${isDone ? `✓ ${t('status_completed')} (${score}%)` : t('status_new')}
            </span>
          </div>
        </div>
        <div class="lesson-arrow">›</div>
      </div>
    `;
  }).join('');

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
