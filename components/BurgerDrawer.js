import { t, getLanguage, setLanguage } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderBurgerDrawer(onNavigate, onClose) {
  const currentLang = getLanguage();
  const currentTheme = StorageService.getTheme();

  return `
    <div class="drawer-backdrop" id="drawer-backdrop">
      <div class="drawer-content" onclick="event.stopPropagation()">
        <div>
          <div class="drawer-header">
            <div style="font-size: 18px; font-weight: 800; color: var(--text-main);">
              English Breakfast
            </div>
            <button class="icon-btn" id="btn-close-drawer">✕</button>
          </div>

          <div class="drawer-links">
            <button class="drawer-btn" id="btn-nav-levels">
              <span>📚</span>
              <span>${t('levels_title')}</span>
            </button>
            <button class="drawer-btn" id="btn-nav-leaderboard">
              <span>🏆</span>
              <span>${t('leaderboard_title')}</span>
            </button>
            
            <div style="margin-top: 16px;">
              <label style="font-size: 12px; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 6px;">
                ${t('language_select')}
              </label>
              <select id="select-language" style="width: 100%; padding: 10px; border-radius: var(--radius-md); border: 1.5px solid var(--border-color); background: var(--bg-hover); color: var(--text-main); font-weight: 700; outline: none; cursor: pointer;">
                <option value="ru" ${currentLang === 'ru' ? 'selected' : ''}>🇷🇺 Русский</option>
                <option value="en" ${currentLang === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                <option value="uk" ${currentLang === 'uk' ? 'selected' : ''}>🇺🇦 Українська</option>
                <option value="es" ${currentLang === 'es' ? 'selected' : ''}>🇪🇸 Español</option>
              </select>
            </div>
          </div>
        </div>

        <div>
          <button class="drawer-btn" id="btn-reset-demo" style="background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.2); color: #ef4444; width: 100%;">
            <span>🔄</span>
            <span>Сбросить демо-прогресс</span>
          </button>
        </div>
      </div>
    </div>
  `;
}
