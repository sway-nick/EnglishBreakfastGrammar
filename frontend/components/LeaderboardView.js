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
  const avatarSrc = player.avatar || '';

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
        ${
          avatarSrc
            ? `<img src="${avatarSrc}" alt="${playerName}" class="podium-avatar-img" referrerpolicy="no-referrer" />`
            : `<div class="podium-avatar-placeholder" style="background: ${player.avatarBg || '#3b82f6'};">${initial}</div>`
        }
      </div>
      <div class="podium-info">
        <h4 class="podium-name" style="display: flex; align-items: center; justify-content: center; gap: 4px;">
          <span>${playerName}</span>
          ${isMe ? `<span class="sync-status-badge" style="position: relative; top: auto; right: auto; width: 7px; height: 7px;"></span>` : ''}
        </h4>
        <span class="podium-xp" style="color: #22c55e; font-weight: 800;">${player.xp} XP</span>
      </div>
    </div>
  `;
}

export function renderLeaderboardView() {
  const currentXP = StorageService.getXP() || 0;
  const weekTime = getTimeUntilSundayEnd();

  // Generic mock leaderboard participants
  const top4Players = [
    { id: '1', name: "Learner #1", xp: 1250, initial: "A", avatarBg: "#3b82f6" },
    { id: '2', name: "Learner #2", xp: 980, initial: "B", avatarBg: "#10b981" },
    { id: '3', name: "Learner #3", xp: 850, initial: "C", avatarBg: "#f59e0b" },
    { id: '4', name: "Learner #4", xp: 720, initial: "D", avatarBg: "#8b5cf6" }
  ];

  const restPlayers = [
    { rank: 5, name: "Learner #5", xp: 650, initial: "E", avatarBg: "#ec4899" },
    { rank: 6, name: "Learner #6", xp: 590, initial: "F", avatarBg: "#6366f1" },
    { rank: 7, name: "Learner #7", xp: 510, initial: "G", avatarBg: "#14b8a6" },
    { rank: 8, name: "Learner #8", xp: 470, initial: "H", avatarBg: "#f97316" },
    { rank: 9, name: "Learner #9", xp: 420, initial: "I", avatarBg: "#84cc16" },
    { rank: 10, name: "Learner #10", xp: 380, initial: "J", avatarBg: "#06b6d4" },
    { rank: 11, name: "Learner #11", xp: 340, initial: "K", avatarBg: "#a855f7" },
    { rank: 12, name: "Learner #12", xp: 300, initial: "L", avatarBg: "#64748b" }
  ];

  const podiumHtml = `
    <div class="podium-grid">
      ${top4Players.map((p, idx) => renderPodiumCard(p, idx + 1)).join('')}
    </div>
  `;

  const restHtml = restPlayers.map(p => {
    const avatarImg = p.avatar ? `<img src="${p.avatar}" alt="${p.name}" class="row-avatar-img" />` : `<div class="row-avatar-placeholder" style="background: ${p.avatarBg || '#64748b'};">${p.initial || '👤'}</div>`;
    return `
      <div class="leaderboard-row">
        <div class="row-rank">#${p.rank}</div>
        <div class="row-avatar-wrapper">
          ${avatarImg}
        </div>
        <div class="row-name">
          <span>${escapeHtml(p.name)}</span>
        </div>
        <div class="row-xp" style="color: #22c55e; font-weight: 800;">${p.xp} XP</div>
      </div>
    `;
  }).join('');

  const myStickyBar = `
    <div class="my-leaderboard-bar" style="position: sticky; bottom: 20px; display: flex; justify-content: space-between; align-items: center; background: #0f172a; border: 1.5px solid #22c55e; border-radius: 16px; padding: 12px 14px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); z-index: 50; margin-top: 10px;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="my-rank-badge" style="background: #22c55e; color: #0f172a; font-weight: 800; font-size: 14px; padding: 3px 8px; border-radius: 6px;">#108</span>
        <div class="my-bar-avatar-placeholder" style="width: 38px; height: 38px; border-radius: 50%; background: #3b82f6; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px;">Y</div>
        <div>
          <div class="my-bar-name" style="font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 6px; color: #f8fafc;">
            <span>You (Guest)</span>
            <span class="sync-status-badge" style="position: relative; top: auto; right: auto; width: 8px; height: 8px; background: #f97316; border-radius: 50%; display: inline-block;"></span>
          </div>
          <div class="my-bar-status" style="font-size: 11.5px; color: #ea580c; font-weight: 600; margin-top: 1px;">
            ⚠️ Прогресс на телефоне. Войдите для облака
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="text-align: right;">
          <div style="font-size: 14px; font-weight: 800; color: #22c55e; line-height: 1;">${currentXP}</div>
          <div style="font-size: 11px; font-weight: 800; color: #22c55e; line-height: 1; margin-top: 2px;">XP</div>
        </div>
        <button class="primary-button" id="leaderboard-login-action" style="background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; border: none; border-radius: 12px; padding: 8px 16px; font-weight: 700; font-size: 13.5px; cursor: pointer; box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35);">Log In</button>
      </div>
    </div>
  `;

  return `
    <div class="leaderboard-page" style="position: relative;">
      <!-- Single Sticky Header Group (Header + 2x2 Podium) Flush to Mobile Header -->
      <div class="leaderboard-sticky-group">
        <div class="leaderboard-top-row" style="display: grid; grid-template-columns: 3fr 1fr; gap: 8px; margin-bottom: 8px;">
          <div class="custom-dropdown" id="leaderboard-type-dropdown">
            <button type="button" class="leaderboard-header-chip" id="leaderboard-type-trigger" style="display: flex; justify-content: space-between; align-items: center; width: 100%; height: 38px; padding: 0 12px; border-radius: 12px; background: var(--bg-hover); border: 1.5px solid var(--border-color); color: var(--text-main); font-weight: 800; font-size: 14px; cursor: pointer;">
              <span>🏆 Weekly League</span>
              <span style="font-size: 9px; margin-left: 6px;">▼</span>
            </button>
          </div>
          <div class="leaderboard-header-chip leaderboard-timer-chip" id="leaderboard-timer-badge" style="display: flex; align-items: center; justify-content: center; gap: 4px; height: 38px; border-radius: 12px; background: var(--bg-hover); border: 1.5px solid var(--border-color); color: var(--text-main); font-weight: 700; font-size: 13.5px;">
            <span>⏳</span>
            <span>3d 2h</span>
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
