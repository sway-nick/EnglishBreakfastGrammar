import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

let currentPeriod = 'week'; // 'week' or 'all'

function getTimeUntilSundayEnd() {
  const now = new Date();
  const day = now.getUTCDay();
  const daysUntilSunday = (7 - day) % 7;
  const targetEndMs = Date.UTC(
    now.getUTCFullYear(),
    now.getUTCMonth(),
    now.getUTCDate() + daysUntilSunday,
    23, 59, 59, 999
  );
  const diffMs = Math.max(0, targetEndMs - now.getTime());
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  return { days, hours };
}

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderPodiumCard(player, rank) {
  if (!player) return '';
  let badgeIcon = '💎';
  let rankClass = 'rank-diamond';

  if (rank === 2) {
    badgeIcon = '🥇';
    rankClass = 'rank-gold';
  } else if (rank === 3) {
    badgeIcon = '🥈';
    rankClass = 'rank-silver';
  } else if (rank === 4) {
    badgeIcon = '🥉';
    rankClass = 'rank-bronze';
  }

  const rawPlayerName = player.name || 'Student';
  const playerName = escapeHtml(rawPlayerName);
  const initial = escapeHtml(rawPlayerName.trim().charAt(0).toUpperCase() || '👤');
  const isMe = !!player.isCurrentUser;

  return `
    <div class="podium-card ${rankClass} ${isMe ? 'is-me' : ''}">
      <div class="podium-badge">${badgeIcon}</div>
      <div class="podium-avatar-wrapper ${rank === 1 ? 'has-wreath' : ''}">
        ${
          rank === 1
            ? `
          <svg class="diamond-laurel-wreath" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="laurelGoldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffffff" />
                <stop offset="25%" stop-color="#fef08a" />
                <stop offset="55%" stop-color="#f59e0b" />
                <stop offset="85%" stop-color="#d97706" />
                <stop offset="100%" stop-color="#78350f" />
              </linearGradient>
              <filter id="wreathGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0.8" stdDeviation="1.2" flood-color="#451a03" flood-opacity="0.55"/>
              </filter>
              <g id="laurel-pair">
                <path d="M 50 91.5 C 55 93.5 60 91.5 62 86.5 C 60 83 54 84.5 50 89" fill="url(#laurelGoldGrad)" stroke="#92400e" stroke-width="0.5"/>
                <path d="M 50 91.5 C 53.5 89.5 56 85 54 80.5 C 51.5 81 49 84.5 50 90" fill="url(#laurelGoldGrad)" stroke="#92400e" stroke-width="0.5"/>
                <circle cx="50" cy="91.5" r="0.8" fill="#fef08a"/>
              </g>
              <g id="laurel-tip">
                <path d="M 50 91.5 C 53 93 57 88 56 83 C 53 84 51 88 50 91.5" fill="url(#laurelGoldGrad)" stroke="#92400e" stroke-width="0.5"/>
              </g>
            </defs>
            <g filter="url(#wreathGlow)">
              <path d="M 50 91.5 A 41.5 41.5 0 0 1 39.5 10" stroke="url(#laurelGoldGrad)" stroke-width="1.6" stroke-linecap="round"/>
              <path d="M 50 91.5 A 41.5 41.5 0 0 0 60.5 10" stroke="url(#laurelGoldGrad)" stroke-width="1.6" stroke-linecap="round"/>
              <use href="#laurel-pair" transform="rotate(-20 50 50)"/>
              <use href="#laurel-pair" transform="rotate(-44 50 50)"/>
              <use href="#laurel-pair" transform="rotate(-68 50 50)"/>
              <use href="#laurel-pair" transform="rotate(-92 50 50)"/>
              <use href="#laurel-pair" transform="rotate(-116 50 50)"/>
              <use href="#laurel-pair" transform="rotate(-140 50 50)"/>
              <use href="#laurel-tip" transform="rotate(-162 50 50)"/>
              <g transform="translate(100, 0) scale(-1, 1)">
                <use href="#laurel-pair" transform="rotate(-20 50 50)"/>
                <use href="#laurel-pair" transform="rotate(-44 50 50)"/>
                <use href="#laurel-pair" transform="rotate(-68 50 50)"/>
                <use href="#laurel-pair" transform="rotate(-92 50 50)"/>
                <use href="#laurel-pair" transform="rotate(-116 50 50)"/>
                <use href="#laurel-pair" transform="rotate(-140 50 50)"/>
                <use href="#laurel-tip" transform="rotate(-162 50 50)"/>
              </g>
              <path d="M 46.5 91.5 C 48 89.5 52 89.5 53.5 91.5 C 52 93.5 48 93.5 46.5 91.5 Z" fill="url(#laurelGoldGrad)" stroke="#92400e" stroke-width="0.5"/>
              <path d="M 48 92.5 L 45 96.5 L 47.5 95.5 L 49.5 92.5" fill="url(#laurelGoldGrad)"/>
              <path d="M 52 92.5 L 55 96.5 L 52.5 95.5 L 50.5 92.5" fill="url(#laurelGoldGrad)"/>
              <circle cx="50" cy="91.5" r="1.6" fill="#fffbeb" stroke="#b45309" stroke-width="0.4"/>
            </g>
          </svg>
        `
            : ''
        }
        <div class="podium-avatar-placeholder" style="background: ${player.avatarBg || '#3b82f6'};">${initial}</div>
      </div>
      <div class="podium-info">
        <h4 class="podium-name" style="display: flex; align-items: center; justify-content: center; gap: 4px;">
          <span>${playerName}</span>
          ${isMe ? `<span class="sync-status-badge" style="position: relative; top: auto; right: auto; width: 7px; height: 7px;"></span>` : ''}
        </h4>
        <span class="podium-xp">${player.xp} XP</span>
      </div>
    </div>
  `;
}

export function renderLeaderboardView() {
  const currentXP = StorageService.getXP() || 0;
  const weekTime = getTimeUntilSundayEnd();

  const players = [
    { id: '1', name: "Alexander K.", xp: 3450, avatarBg: "#f59e0b" },
    { id: '2', name: "Elena Smith", xp: 2980, avatarBg: "#8b5cf6" },
    { id: '3', name: "Dmitry R.", xp: 2710, avatarBg: "#06b6d4" },
    { id: '4', name: "Anna Grammar", xp: 2340, avatarBg: "#ec4899" },
    { id: '5', name: "Maxim V.", xp: 1920, avatarBg: "#10b981" },
    { id: '6', name: "Olga P.", xp: 1650, avatarBg: "#3b82f6" },
    { id: '7', name: "Sergey T.", xp: 1420, avatarBg: "#f97316" },
    { id: '8', name: "Tatiana M.", xp: 1180, avatarBg: "#6366f1" },
    { id: 'me', name: "Гость (Демо)", xp: currentXP > 0 ? currentXP : 0, avatarBg: "#334155", isCurrentUser: true }
  ];

  // Sort players by XP
  players.sort((a, b) => b.xp - a.xp);
  const myRankIndex = players.findIndex(p => p.isCurrentUser);
  const myRank = myRankIndex >= 0 ? myRankIndex + 1 : 9;
  const myPlayer = players[myRankIndex];

  const top4 = players.slice(0, 4);
  const rest = players.slice(4);

  const podiumHtml = `
    <div class="podium-grid">
      ${top4.map((p, idx) => renderPodiumCard(p, idx + 1)).join('')}
    </div>
  `;

  const restHtml = rest.map((p, idx) => {
    const rank = idx + 5;
    const isMe = p.isCurrentUser;
    const initial = escapeHtml(p.name.trim().charAt(0).toUpperCase() || '👤');

    return `
      <div class="leaderboard-row ${isMe ? 'is-me' : ''}">
        <div class="row-rank">#${rank}</div>
        <div class="row-avatar-wrapper">
          <div class="row-avatar-placeholder" style="background: ${p.avatarBg || '#64748b'};">${initial}</div>
        </div>
        <div class="row-name" style="display: flex; align-items: center; gap: 6px;">
          <span>${escapeHtml(p.name)}</span>
          ${isMe ? `<span class="me-tag">(Вы)</span>` : ''}
          ${isMe ? `<span class="sync-status-badge" style="position: relative; top: auto; right: auto; width: 7px; height: 7px;"></span>` : ''}
        </div>
        <div class="row-xp">${p.xp} XP</div>
      </div>
    `;
  }).join('');

  const myStickyBar = myRank > 4 ? `
    <div class="my-leaderboard-bar">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="my-rank-badge">#${myRank}</span>
        <div class="my-bar-avatar-placeholder" style="background: #334155;">G</div>
        <div>
          <div class="my-bar-name" style="font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 6px; color: var(--text-main);">
            <span>Гость (Демо)</span>
            <span class="sync-status-badge" style="position: relative; top: auto; right: auto; width: 7px; height: 7px;"></span>
          </div>
          <div class="my-bar-status" style="font-size: 12px; color: #ea580c; font-weight: 500;">
            ⚠️ Прогресс на телефоне. Войдите для облака
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="my-bar-xp">${currentXP} XP</span>
        <button class="primary-button" id="leaderboard-register-btn" style="background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; border: none; border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 13px; cursor: pointer;">Войти</button>
      </div>
    </div>
  ` : '';

  return `
    <div class="leaderboard-page" style="position: relative;">
      <!-- Single Sticky Header Group (Header + Podium) -->
      <div class="leaderboard-sticky-group">
        <div class="leaderboard-top-row">
          <div class="custom-dropdown" id="leaderboard-type-dropdown">
            <button type="button" class="leaderboard-header-chip leaderboard-dropdown-chip" id="leaderboard-type-trigger">
              <span id="leaderboard-type-label">Лига недели</span>
              <span class="dropdown-arrow" style="font-size: 9px; margin-left: 6px;">▼</span>
            </button>
          </div>
          <div class="leaderboard-header-chip leaderboard-timer-chip" id="leaderboard-timer-badge">
            <span style="font-size: 13.5px; line-height: 1;">⏳</span>
            <span>${weekTime.days > 0 ? `${weekTime.days}д ` : ''}${weekTime.hours}ч</span>
          </div>
        </div>

        <div id="leaderboard-podium-container">
          ${podiumHtml}
        </div>
      </div>

      <!-- Scrollable Table -->
      <div id="leaderboard-content" style="min-height: 280px; margin-top: 10px;">
        <div class="leaderboard-table">
          ${restHtml}
        </div>
        ${myStickyBar}
      </div>
    </div>
  `;
}
