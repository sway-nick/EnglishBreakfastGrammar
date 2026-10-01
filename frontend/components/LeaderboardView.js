import { t } from '../services/i18n.js';
import { StorageService } from '../services/storageService.js';

export function renderLeaderboardView() {
  const currentXP = StorageService.getXP();
  
  // Realistic leaderboard mock data seamlessly integrated with user's current XP
  const mockPlayers = [
    { rank: 1, name: "Alexander K.", xp: 3450, avatar: "🦁", league: "diamond" },
    { rank: 2, name: "Elena Smith", xp: 2980, avatar: "🦊", league: "gold" },
    { rank: 3, name: "Dmitry R.", xp: 2710, avatar: "🦉", league: "silver" },
    { rank: 4, name: "Anna Grammar", xp: 2340, avatar: "🐼", league: "bronze" },
    { rank: 5, name: "Вы (Игрок)", xp: currentXP > 0 ? currentXP : 120, avatar: "☕", isUser: true },
    { rank: 6, name: "Maria V.", xp: 1890, avatar: "🐱" },
    { rank: 7, name: "Sergey T.", xp: 1650, avatar: "🐨" },
    { rank: 8, name: "Olga P.", xp: 1420, avatar: "🐯" }
  ];

  // Sort by XP
  mockPlayers.sort((a, b) => b.xp - a.xp);
  mockPlayers.forEach((p, idx) => p.rank = idx + 1);

  const top3 = mockPlayers.slice(0, 3);
  const remaining = mockPlayers.slice(3);

  const podiumHtml = `
    <div class="podium-wrap">
      <div class="podium-item rank-2">
        <div class="podium-avatar">🥈</div>
        <div class="podium-name">${top3[1]?.name || 'Player 2'}</div>
        <div class="podium-xp">${top3[1]?.xp || 0} XP</div>
      </div>
      <div class="podium-item rank-1">
        <div class="podium-avatar">💎</div>
        <div class="podium-name">${top3[0]?.name || 'Player 1'}</div>
        <div class="podium-xp">${top3[0]?.xp || 0} XP</div>
      </div>
      <div class="podium-item rank-3">
        <div class="podium-avatar">🥉</div>
        <div class="podium-name">${top3[2]?.name || 'Player 3'}</div>
        <div class="podium-xp">${top3[2]?.xp || 0} XP</div>
      </div>
    </div>
  `;

  const listHtml = remaining.map(p => `
    <div class="player-card ${p.isUser ? 'is-current-user' : ''}">
      <div class="player-rank">#${p.rank}</div>
      <div class="player-main-info">
        <div class="player-avatar-sm">${p.avatar}</div>
        <div class="player-name">${p.name} ${p.isUser ? '(Вы)' : ''}</div>
      </div>
      <div class="player-xp">${p.xp} XP</div>
    </div>
  `).join('');

  return `
    <div class="screen-view">
      <div class="screen-header-nav">
        <button class="back-btn" id="btn-back-to-levels-from-lb">
          ← ${t('back_to_levels')}
        </button>
      </div>

      <div style="margin-bottom: 16px;">
        <h1 class="screen-title">${t('leaderboard_title')}</h1>
        <p class="screen-subtitle">Соревнуйтесь с другими учениками каждую неделю</p>
      </div>

      <div class="leaderboard-tabs">
        <div class="leaderboard-tab active" data-tab="weekly">${t('leaderboard_weekly')}</div>
        <div class="leaderboard-tab" data-tab="alltime">${t('leaderboard_alltime')}</div>
      </div>

      ${podiumHtml}

      <div class="leaderboard-list">
        ${listHtml}
      </div>
    </div>
  `;
}
