import { StorageService } from '../services/storageService.js';

export function renderHeader() {
  const xp = StorageService.getXP() || 0;
  const completedMap = StorageService.getCompletedLessons();
  const completedCount = Object.keys(completedMap).length;

  return `
    <div class="safe-area-top-fill" aria-hidden="true"></div>
    <header class="mobile-header">
      <div class="brand" id="brand-logo" style="cursor: pointer; flex: 1 1 auto; min-width: 0; max-width: calc(100% - 130px); overflow: hidden; display: flex; align-items: center;" title="Перейти на главную">
        <div style="display: flex; align-items: center; gap: 7px;">
          <img src="./assets/icons/mug_icon.webp" alt="English Breakfast" class="header-mug-img" style="width: 33px; height: 33px; object-fit: contain; flex-shrink: 0;" />
          <div style="display: flex; flex-direction: column; justify-content: center; line-height: 1.1;">
            <div class="brand-title">
              <span>English</span> <span class="brass">Breakfast</span>
            </div>
            <span style="font-size: 12px; font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 3px; white-space: nowrap; margin-top: 1px;">
              Grammar<span id="header-user-status" style="color: #22c55e; font-weight: 700; font-size: 11.5px;">• 🎁 ${completedCount}/50</span>
            </span>
          </div>
        </div>
      </div>
      
      <div class="header-right-actions">
        <button class="header-xp-badge" id="header-xp-btn" title="Лига недели. Нажмите, чтобы открыть рейтинг">
          <span class="xp-badge-level" id="header-xp-icon">Lv -</span>
          <span class="xp-badge-text"><span id="header-xp-val">${xp}</span>&nbsp;XP</span>
        </button>
        <button class="header-burger-btn" id="header-burger-btn" title="Меню" aria-label="Открыть меню" style="position: relative;">
          <svg class="burger-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" style="color: var(--text-main);">
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
          <span class="sync-status-badge" id="header-burger-sync-badge" style="display: block;"></span>
        </button>
      </div>
    </header>
  `;
}
