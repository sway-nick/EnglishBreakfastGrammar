import { StorageService } from '../services/storageService.js';
import { t } from '../services/i18n.js';

export function renderHeader(onBurgerClick, onLogoClick, onThemeToggle) {
  const xp = StorageService.getXP();
  const streak = StorageService.getStreak();
  const currentTheme = StorageService.getTheme();

  return `
    <header class="mobile-header">
      <div class="header-left" id="btn-header-home">
        <div class="header-logo-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 54 58" width="100%" height="100%">
            <!-- Steam in light-green -->
            <path d="M12,16 C7,12 17,8 12,4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <path d="M22,16 C17,12 27,8 22,2" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <path d="M32,16 C27,12 37,8 32,4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" fill="none"/>
            <!-- Green Cup -->
            <path d="M4,28 C4,46 12,54 22,54 C32,54 40,46 40,28 Z" fill="#22c55e"/>
            <path d="M40,32 C48,32 48,45 35,45" stroke="#22c55e" stroke-width="4.5" fill="none" stroke-linecap="round"/>
            <path d="M5,30 Q13.5,27 22,30 Q30.5,27 39,30 L39,20 Q30.5,17 22,20 Q13.5,17 5,20 Z" fill="#FFF" stroke="#16a34a" stroke-width="1.8"/>
            <path d="M22,23 Q13.5,20 8,23" stroke="#22c55e" stroke-width="1.2" fill="none"/>
            <path d="M22,26 Q13.5,23 8,26" stroke="#22c55e" stroke-width="1.2" fill="none"/>
            <path d="M22,23 Q30.5,20 36,23" stroke="#22c55e" stroke-width="1.2" fill="none"/>
            <path d="M22,26 Q30.5,23 36,26" stroke="#22c55e" stroke-width="1.2" fill="none"/>
            <line x1="22" y1="20" x2="22" y2="30" stroke="#16a34a" stroke-width="1.8"/>
            <text x="22" y="45" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="900" font-size="14" fill="#FFF" text-anchor="middle">EN</text>
          </svg>
        </div>
        <div class="header-brand-wrap">
          <div class="header-title">
            English <span class="header-title-highlight">Breakfast</span>
          </div>
          <span class="header-subtitle-badge">${t('app_subtitle')}</span>
        </div>
      </div>

      <div class="header-right">
        <div class="header-stat-badge streak-badge" title="${t('streak_label')}">
          <span>🔥</span>
          <span id="header-streak-val">${streak}</span>
        </div>
        <div class="header-stat-badge xp-badge" title="${t('xp_label')}">
          <span>⚡</span>
          <span id="header-xp-val">${xp}</span>
        </div>
        <button class="icon-btn" id="btn-theme-toggle" title="Переключить тему">
          ${currentTheme === 'dark' ? '☀️' : '🌙'}
        </button>
        <button class="icon-btn" id="btn-burger-menu" title="Меню">
          ☰
        </button>
      </div>
    </header>
  `;
}
