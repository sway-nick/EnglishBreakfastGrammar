import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';
import { AuthService } from '../services/authService.js';

let currentPeriod = typeof localStorage !== 'undefined' ? (localStorage.getItem('eb_leaderboard_period') || 'week') : 'week'; // 'week' or 'all'

function shouldShowSyncBadge() {
  try {
    const u = AuthService.getCurrentUser();
    const isGuest = !u || !u.id || u.id === 'guest' || String(u.id).startsWith('guest_') || !u.email;
    if (isGuest) return true;
    return Boolean(window.__eb_sync_issue || (typeof sessionStorage !== 'undefined' && sessionStorage.getItem('eb_sync_issue') === '1'));
  } catch (e) {
    return true;
  }
}

function getTimeUntilSundayEnd() {
  const now = new Date();
  const day = now.getUTCDay(); // 0 is Sunday, 1 is Monday... 6 is Saturday
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
  const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

  return { days, hours, mins };
}

function formatLeaderboardXp(xp, period = 'week') {
  return String(Math.round(Number(xp || 0)));
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

function sanitizeAvatarUrl(url) {
  if (!url || typeof url !== 'string') return '';
  const trimmed = url.trim();
  if (/^(https?:\/\/|\.\/|\/|assets\/|data:image\/)/i.test(trimmed)) {
    return escapeHtml(trimmed);
  }
  return '';
}

function renderPodiumCard(player, rank, period = 'week') {
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

  const rawAvatar = player.avatar || '';
  const avatarSrc = sanitizeAvatarUrl(rawAvatar);
  const rawPlayerName = (player && player.name != null) ? String(player.name) : (t('lead_student_default') || 'Student');
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
        ${
          avatarSrc
            ? `<img src="${avatarSrc}" alt="${playerName}" class="podium-avatar-img" referrerpolicy="no-referrer" />`
            : `<div class="podium-avatar-placeholder">${initial}</div>`
        }
      </div>
      <div class="podium-info">
        <h4 class="podium-name" style="display: flex; align-items: center; justify-content: center; gap: 5px;">
          <span>${playerName}</span>
          ${player.isCurrentUser && shouldShowSyncBadge() ? `<span class="sync-status-badge" style="position: relative; top: auto; right: auto;" title="Прогресс учтён локально. Войдите для обновления рейтинга"></span>` : ''}
        </h4>
        <span class="podium-xp">${formatLeaderboardXp(player.xp, period)} XP</span>
      </div>
    </div>
  `;
}

function buildLeaderboardBodyHtml(players, currentUser, period = 'week') {
  const safePlayers = Array.isArray(players) ? players.filter(p => p && typeof p === 'object') : [];
  
  const top100 = safePlayers.slice(0, 100);
  const top4 = top100.slice(0, 4);
  const rest = top100.slice(4);

  const myRankIndex = safePlayers.findIndex((p) => p && p.isCurrentUser);
  const myRank = myRankIndex >= 0 ? myRankIndex + 1 : 108;
  const myPlayer = myRankIndex >= 0 ? safePlayers[myRankIndex] : { xp: StorageService.getXP() || 0, isCurrentUser: true };

  const podiumHtml = `
    <div class="podium-grid">
      ${top4.map((p, idx) => renderPodiumCard(p, idx + 1, period)).join('')}
    </div>
  `;

  let restListHtml = '';
  if (rest.length > 0) {
    restListHtml = `
      <div class="leaderboard-table">
        ${rest
          .map((p, idx) => {
            const rank = idx + 5;
            const isMe = p.isCurrentUser;
            const avatarSrc = sanitizeAvatarUrl(p.avatar || '');
            const rawPName = (p && p.name != null) ? String(p.name) : (t('lead_student_default') || 'Student');
            const pName = escapeHtml(rawPName);
            const initial = escapeHtml(rawPName.trim().charAt(0).toUpperCase() || '👤');

            return `
            <div class="leaderboard-row ${isMe ? 'is-me' : ''}">
              <div class="row-rank">#${rank}</div>
              <div class="row-avatar-wrapper">
                ${
                  avatarSrc
                    ? `<img src="${avatarSrc}" alt="${pName}" class="row-avatar-img" referrerpolicy="no-referrer" />`
                    : `<div class="row-avatar-placeholder">${initial}</div>`
                }
              </div>
              <div class="row-name" style="display: flex; align-items: center; gap: 6px;">
                <span>${pName}</span>
                ${isMe && shouldShowSyncBadge() ? `<span class="sync-status-badge" style="position: relative; top: auto; right: auto;" title="Прогресс учтён локально. Войдите для обновления рейтинга"></span>` : ''}
              </div>
              <div class="row-xp">${formatLeaderboardXp(p.xp, period)} XP</div>
            </div>
          `;
          })
          .join('')}
      </div>
    `;
  }

  let myStickyBarHtml = '';
  if (myPlayer) {
    const myAvatar = sanitizeAvatarUrl(AuthService.getUserAvatar ? AuthService.getUserAvatar() : '');
    const isIssue = shouldShowSyncBadge();
    const statusText = isIssue
      ? '⚠️ Прогресс на телефоне. Войдите для облака'
      : (period === 'all'
          ? (t('lead_score_all_time') || 'All time XP')
          : (currentUser
              ? (t('lead_score_current') || 'Weekly XP')
              : (t('lead_login_to_save') || 'Log in to save progress')
            ));
    const rawMyName = (currentUser && currentUser.name != null) ? String(currentUser.name) : (t('lead_guest_name') || 'You (Guest)');
    const myName = escapeHtml(rawMyName);
    const myInitial = escapeHtml(rawMyName.trim().charAt(0).toUpperCase() || 'Y');
    myStickyBarHtml = `
      <div class="my-leaderboard-bar">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span class="my-rank-badge">#${myRank || '-'}</span>
          ${
            myAvatar
              ? `<img src="${myAvatar}" class="my-bar-avatar" alt="Вы" referrerpolicy="no-referrer" />`
              : `<div class="my-bar-avatar-placeholder">${myInitial}</div>`
          }
          <div>
            <div class="my-bar-name" style="font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 6px;">
              <span>${myName}</span>
              ${isIssue ? `<span class="sync-status-badge" id="leaderboard-player-sync-badge" style="position: relative; top: auto; right: auto;" title="Прогресс учтён локально. Войдите для обновления рейтинга"></span>` : ''}
            </div>
            <div class="my-bar-status" style="font-size: 12px; color: ${isIssue ? '#ea580c' : 'var(--text-muted)'}; font-weight: ${isIssue ? '500' : 'normal'};">
              ${statusText}
            </div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span class="my-bar-xp">${formatLeaderboardXp(myPlayer.xp, period)} XP</span>
          ${
            !currentUser || isIssue
              ? `<button class="primary-button" id="leaderboard-login-btn" style="padding: 6px 14px; min-height: 34px; height: 34px; font-size: 13px;">${t('settings_login') || 'Log In'}</button>`
              : ''
          }
        </div>
      </div>
    `;
  }

  return {
    podiumHtml,
    restHtml: `${restListHtml}${myStickyBarHtml}`
  };
}

export function renderLeaderboardView(containerSelector = '#app-content', options = {}) {
  const currentUser = AuthService.getCurrentUser ? AuthService.getCurrentUser() : null;
  const weekTime = getTimeUntilSundayEnd();

  // Demo participant list (purely for structure / styling preview)
  const defaultPlayers = [
    { id: '1', name: "Learner #1", xp: 1250 },
    { id: '2', name: "Learner #2", xp: 980 },
    { id: '3', name: "Learner #3", xp: 850 },
    { id: '4', name: "Learner #4", xp: 720 },
    { id: '5', name: "Learner #5", xp: 650 },
    { id: '6', name: "Learner #6", xp: 590 },
    { id: '7', name: "Learner #7", xp: 510 },
    { id: '8', name: "Learner #8", xp: 470 },
    { id: '9', name: "Learner #9", xp: 420 },
    { id: '10', name: "Learner #10", xp: 380 },
    { id: '11', name: "Learner #11", xp: 340 },
    { id: '12', name: "Learner #12", xp: 300 }
  ];

  const bodyData = buildLeaderboardBodyHtml(defaultPlayers, currentUser, currentPeriod);

  const dText = t('lead_days_short') || 'd';
  const hText = t('lead_hours_short') || 'h';

  const html = `
    <div class="leaderboard-page" style="position: relative;">
      <!-- Single Sticky Header Group (Header + Podium) Flush to Mobile Header -->
      <div class="leaderboard-sticky-group">
        <div class="leaderboard-top-row ${currentPeriod === 'all' ? 'no-timer' : ''}">
          <div class="custom-dropdown" id="leaderboard-type-dropdown">
            <button type="button" class="leaderboard-header-chip leaderboard-dropdown-chip" id="leaderboard-type-trigger" aria-haspopup="listbox" aria-expanded="false">
              <span id="leaderboard-type-label" style="white-space: nowrap; text-align: left; overflow: hidden; text-overflow: ellipsis;">${currentPeriod === 'all' ? '🌎 ' + (t('lead_all_time') || 'All Time') : (t('lead_title') || '🏆 Weekly League')}</span>
              <span class="dropdown-arrow" style="font-size: 9px; flex-shrink: 0; margin-left: 6px; transition: transform 0.2s ease;">▼</span>
            </button>
            <div class="custom-dropdown-menu" id="leaderboard-type-menu" role="listbox" style="z-index: 130; width: 100%; min-width: 190px;">
              <div class="dropdown-item ${currentPeriod === 'week' ? 'selected' : ''}" data-value="week" style="white-space: nowrap;">${t('lead_title') || '🏆 Weekly League'}</div>
              <div class="dropdown-item ${currentPeriod === 'all' ? 'selected' : ''}" data-value="all" style="white-space: nowrap;">🌎 ${t('lead_all_time') || 'All Time'}</div>
            </div>
          </div>
          ${currentPeriod === 'all' ? '' : `
          <div class="leaderboard-header-chip leaderboard-timer-chip" id="leaderboard-timer-badge">
            <span style="font-size: 13.5px; line-height: 1;">⏳</span>
            <span>${weekTime.days > 0 ? `${weekTime.days}${dText} ` : ''}${weekTime.hours}${hText}</span>
          </div>
          `}
        </div>

        <div id="leaderboard-podium-container">
          ${bodyData.podiumHtml}
        </div>
      </div>

      <!-- Scrollable Content -->
      <div id="leaderboard-content" style="min-height: 280px;">
        ${bodyData.restHtml}
      </div>
    </div>
  `;

  return html;
}

export function initLeaderboardEvents() {
  const typeDropdown = document.querySelector('#leaderboard-type-dropdown');
  const typeTrigger = document.querySelector('#leaderboard-type-trigger');
  const typeItems = document.querySelectorAll('#leaderboard-type-menu .dropdown-item');

  if (typeTrigger && typeDropdown) {
    typeTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      typeDropdown.classList.toggle('open');
    });

    typeItems.forEach((item) => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        currentPeriod = item.getAttribute('data-value');
        localStorage.setItem('eb_leaderboard_period', currentPeriod);
        typeDropdown.classList.remove('open');
        const container = document.querySelector('#app-content');
        if (container) {
          container.innerHTML = renderLeaderboardView();
          initLeaderboardEvents();
        }
      });
    });

    document.addEventListener('click', () => {
      typeDropdown.classList.remove('open');
    });
  }
}
