import { StorageService } from '../services/storageService.js';

export function renderHeader() {
  const xp = StorageService.getXP() || 0;
  const completedMap = StorageService.getCompletedLessons();
  const completedCount = Object.keys(completedMap).length;

  return `
    <div class="safe-area-top-fill" aria-hidden="true"></div>
    <header class="mobile-header">
      <div class="brand" id="brand-logo" style="cursor: pointer; flex: 1 1 auto; min-width: 0; max-width: calc(100% - 130px); overflow: hidden; display: flex; align-items: center;" title="Перейти на главную">
        <!-- SVG Cup-with-Book Logo in Light-Green -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 270 56" style="display: block; width: 100%; max-width: 180px; height: 38px; min-width: 130px;">
          <!-- Steam lines in light-green -->
          <path d="M12,16 C7,12 17,8 12,4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
          <path d="M22,16 C17,12 27,8 22,2" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
          <path d="M32,16 C27,12 37,8 32,4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
          <!-- Cup body -->
          <path d="M4,28 C4,46 12,54 22,54 C32,54 40,46 40,28 Z" fill="#22c55e"/>
          <!-- Handle -->
          <path d="M40,32 C48,32 48,45 35,45" stroke="#22c55e" stroke-width="4.5" fill="none" stroke-linecap="round"/>
          <!-- Stacked open book pages with green borders -->
          <path d="M5,30 Q13.5,27 22,30 Q30.5,27 39,30 L39,20 Q30.5,17 22,20 Q13.5,17 5,20 Z" fill="#FFF" stroke="#16a34a" stroke-width="1.8"/>
          <!-- Page lines left -->
          <path d="M22,23 Q13.5,20 8,23" stroke="#22c55e" stroke-width="1.2" fill="none"/>
          <path d="M22,26 Q13.5,23 8,26" stroke="#22c55e" stroke-width="1.2" fill="none"/>
          <!-- Page lines right -->
          <path d="M22,23 Q30.5,20 36,23" stroke="#22c55e" stroke-width="1.2" fill="none"/>
          <path d="M22,26 Q30.5,23 36,26" stroke="#22c55e" stroke-width="1.2" fill="none"/>
          <!-- Center Spine Line -->
          <line x1="22" y1="20" x2="22" y2="30" stroke="#16a34a" stroke-width="1.8"/>
          <!-- EN Text -->
          <text x="22" y="45" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="14" fill="#FFF" text-anchor="middle">EN</text>
          <!-- Brand Text (English Breakfast) -->
          <text x="56" y="27" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="20.5" fill="var(--text-main)">English <tspan fill="#22c55e">Breakfast</tspan></text>
          <!-- Subtitle (Grammar + inline Demo) exactly matching Vocabulary typography -->
          <text x="56" y="49" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="500" font-size="16" fill="var(--text-muted)">Grammar<tspan id="header-user-status" fill="#22c55e" font-weight="700" font-size="14.5">• 🎁 ${completedCount}/50</tspan></text>
        </svg>
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
