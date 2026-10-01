import { t } from '../services/i18n.js';

export function renderTestResultModal(scorePercent, earnedXP, onContinue, onRetry) {
  const isPerfect = scorePercent >= 90;
  const isGood = scorePercent >= 70;
  const emoji = isPerfect ? '🏆' : (isGood ? '🎉' : '💪');

  return `
    <div class="modal-backdrop" id="test-result-modal">
      <div class="modal-box" onclick="event.stopPropagation()">
        <div style="font-size: 36px; line-height: 1;">${emoji}</div>
        <h2 style="font-size: 22px; font-weight: 800; color: var(--text-main);">${t('test_completed')}</h2>
        
        <div class="score-badge-circle">
          ${scorePercent}%
        </div>

        <div style="display: flex; justify-content: center; gap: 16px; margin: 8px 0;">
          <div class="header-stat-badge xp-badge" style="font-size: 16px; padding: 8px 16px;">
            <span>⚡</span>
            <span>+${earnedXP} XP</span>
          </div>
        </div>

        <p style="font-size: 14px; color: var(--text-muted); line-height: 1.4;">
          ${isGood ? 'Отличный результат! Урок усвоен на высокий балл.' : 'Хорошая попытка! Вы можете повторить тест или перейти к следующему уроку.'}
        </p>

        <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
          <button class="btn-primary" id="btn-result-continue">
            ${t('continue_btn')}
          </button>
          <button class="drawer-btn" id="btn-result-retry" style="justify-content: center;">
            ${t('retry_btn')}
          </button>
        </div>
      </div>
    </div>
  `;
}
