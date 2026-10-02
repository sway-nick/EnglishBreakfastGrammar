import { t, getLanguage, setLanguage, SUPPORTED_LANGUAGES } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderBurgerDrawer() {
  const currentLang = getLanguage();
  const currentTheme = StorageService.getTheme();

  const langOptionsHtml = SUPPORTED_LANGUAGES.map(l => 
    `<option value="${l.code}" ${currentLang === l.code ? 'selected' : ''}>${l.flag} ${l.name}</option>`
  ).join('');

  return `
    <div class="drawer-overlay" id="drawer-overlay"></div>
    <div class="burger-drawer" id="burger-drawer">
      <div class="drawer-header">
        <div class="drawer-profile" id="drawer-profile-btn" style="cursor: pointer;">
          <div class="drawer-avatar-wrapper">
            <div class="drawer-avatar-placeholder">G</div>
          </div>
          <div class="drawer-profile-info">
            <div class="drawer-username">Гость (Демо)</div>
            <div class="drawer-email">Log in to sync progress</div>
          </div>
        </div>
        <button class="drawer-close-btn" id="drawer-close-btn" aria-label="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="drawer-body" style="overflow-y: auto; display: flex; flex-direction: column; gap: 14px; padding: 4px 0 20px;">
        <!-- User Profile Card -->
        <div class="settings-card profile-card" style="display: flex; align-items: center; justify-content: space-between; gap: 10px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div class="profile-avatar-wrapper" style="position: relative;">
              <div class="profile-avatar-placeholder" style="width: 44px; height: 44px; border-radius: 50%; background: #334155; color: #fff; font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 18px;">G</div>
              <div style="position: absolute; bottom: -2px; right: -2px; width: 16px; height: 16px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff;">👤</div>
            </div>
            <div>
              <div style="font-size: 15px; font-weight: 800; color: var(--text-main);">Guest (Demo)</div>
              <div style="font-size: 12px; color: var(--text-muted);">Log in to sync progress</div>
            </div>
          </div>
          <button class="primary-button settings-auth-btn" id="register-modal-btn" style="position: relative; background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; border: none; border-radius: 12px; padding: 8px 16px; font-weight: 700; font-size: 13.5px; cursor: pointer; box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35);">
            Register
            <span class="sync-status-badge" style="display: block; top: -2px; right: -2px;"></span>
          </button>
        </div>

        <!-- Language Selection Card -->
        <div class="settings-card">
          <div class="settings-card-title" style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; font-weight: 700; margin-bottom: 10px; color: var(--text-main);">
            <span>🌐</span>
            <span>Interface Language</span>
          </div>
          <select id="select-language" class="settings-select" style="width: 100%; height: 44px; padding: 0 12px; border-radius: 12px; border: 1px solid var(--border-color); background: var(--bg-hover); color: var(--text-main); font-weight: 600; font-size: 14.5px; outline: none; cursor: pointer;">
            ${langOptionsHtml}
          </select>
        </div>

        <!-- Theme Switcher Card -->
        <div class="settings-card">
          <div class="settings-card-title" style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; font-weight: 700; margin-bottom: 10px; color: var(--text-main);">
            <span>🎨</span>
            <span>Theme</span>
          </div>
          <div class="theme-options-row" style="display: flex; gap: 10px;">
            <button class="theme-option-btn ${currentTheme === 'light' ? 'active' : ''}" id="theme-light-btn" style="flex: 1;">
              Light
            </button>
            <button class="theme-option-btn ${currentTheme === 'dark' ? 'active' : ''}" id="theme-dark-btn" style="flex: 1;">
              Dark
            </button>
          </div>
        </div>

        <!-- Sound Mode Card -->
        <div class="settings-card">
          <div class="settings-card-title" style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; font-weight: 700; margin-bottom: 10px; color: var(--text-main);">
            <span>✨</span>
            <span>Sound Effects</span>
          </div>
          <div class="sound-options-row" style="display: flex; gap: 10px;">
            <button class="sound-option-btn active" id="sfx-on-btn" style="flex: 1;">
              🔔 Enabled
            </button>
            <button class="sound-option-btn" id="sfx-off-btn" style="flex: 1;">
              🔕 Disabled
            </button>
          </div>
        </div>

        <!-- Voice Accent Card -->
        <div class="settings-card">
          <div class="settings-card-title" style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; font-weight: 700; margin-bottom: 10px; color: var(--text-main);">
            <span>👤</span>
            <span>Voice Accent</span>
          </div>
          <div class="voice-options-row" style="display: flex; gap: 10px;">
            <button class="voice-option-btn flag-btn" id="voice-uk-btn" style="flex: 1;">
              <svg class="flag-svg-icon" viewBox="0 0 640 480" width="30" height="21">
                <path fill="#012169" d="M0 0h640v480H0z"/>
                <path fill="#FFF" d="m75 0 244 181L562 0h78v62L400 240l240 178v62h-80L320 301 81 480H0v-60l239-180L0 64V0h75z"/>
                <path fill="#C8102E" d="m424 288 216 159v33h-44L367 304l57-16zM640 22v10L432 201l-24-33 197-146h35zM0 458v-10l208-169 24 33L35 458H0zM216 192 0 33V0h44l229 176-57 16z"/>
              </svg>
            </button>
            <button class="voice-option-btn flag-btn active" id="voice-us-btn" style="flex: 1;">
              <svg class="flag-svg-icon" viewBox="0 0 640 480" width="30" height="21">
                <path fill="#bd3d44" d="M0 0h640v480H0z"/>
                <path stroke="#fff" stroke-width="37" d="M0 55.5h640M0 129.5h640M0 203.5h640M0 277.5h640M0 351.5h640M0 425.5h640"/>
                <path fill="#192f5d" d="M0 0h260v259H0z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 6px;">
          <button class="drawer-btn" id="btn-nav-levels" style="display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-radius: 12px; background: var(--bg-hover); border: 1px solid var(--border-color); color: var(--text-main); font-weight: 700; cursor: pointer;">
            <span>📚</span>
            <span>${t('levels_title')}</span>
          </button>
          <button class="drawer-btn" id="btn-nav-leaderboard" style="display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-radius: 12px; background: var(--bg-hover); border: 1px solid var(--border-color); color: var(--text-main); font-weight: 700; cursor: pointer;">
            <span>🏆</span>
            <span>${t('leaderboard_title')}</span>
          </button>
          <button class="drawer-btn" id="btn-reset-demo" style="display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-radius: 12px; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); color: #ef4444; font-weight: 700; cursor: pointer;">
            <span>🔄</span>
            <span>Сбросить демо-прогресс</span>
          </button>
        </div>

        <!-- Privacy Policy Footer -->
        <div style="text-align: center; margin-top: 14px; padding-bottom: 10px;">
          <a href="#" id="link-privacy-policy" style="font-size: 12.5px; color: var(--text-muted); text-decoration: underline; cursor: pointer;">Privacy Policy</a>
        </div>
      </div>
    </div>
  `;
}
