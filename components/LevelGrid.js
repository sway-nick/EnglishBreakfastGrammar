export function renderLevelGrid(catalog) {
  const cards = [
    { id: 'A1', title: 'A1 Elementary', bg: './assets/cards/card_a1.webp' },
    { id: 'A2', title: 'A2 Pre-Intermediate', bg: './assets/cards/card_a2.webp' },
    { id: 'B1', title: 'B1 Intermediate', bg: './assets/cards/card_b1.webp' },
    { id: 'B1-B2', title: 'B1+ Upper-Intermediate', bg: './assets/cards/card_b1_b2.webp' },
    { id: 'B2', title: 'B2 Pre-Advanced', bg: './assets/cards/card_b2.webp' },
    { id: 'C1', title: 'C1 Advanced', bg: './assets/cards/card_c1.webp' },
    { id: 'SHORTS', title: 'Shorts', bg: './assets/cards/card_shorts.webp' },
    { id: 'favorites', title: 'Favorites', bg: './assets/cards/card_favorites.webp' }
  ];

  const cardsHtml = cards.map(c => `
    <div class="level-card" data-level-id="${c.id}">
      <img 
        src="${c.bg}" 
        alt="${c.title}" 
        class="level-card-img" 
        width="650" 
        height="500" 
        loading="eager" 
        decoding="async" 
        fetchpriority="high"
      />
    </div>
  `).join('');

  return `
    <div class="screen-view">
      <div class="level-grid">
        ${cardsHtml}
      </div>
    </div>
  `;
}
