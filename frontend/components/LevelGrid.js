export function renderLevelGrid(catalog) {
  const cards = [
    { id: 'A1', title: 'A1 Elementary', bg: './assets/cards/card_a1.png' },
    { id: 'A2', title: 'A2 Pre-Intermediate', bg: './assets/cards/card_a2.png' },
    { id: 'B1', title: 'B1 Intermediate', bg: './assets/cards/card_b1.png' },
    { id: 'B1-B2', title: 'B1+ Upper-Intermediate', bg: './assets/cards/card_b1_b2.png' },
    { id: 'B2', title: 'B2 Pre-Advanced', bg: './assets/cards/card_b2.png' },
    { id: 'C1', title: 'C1 Advanced', bg: './assets/cards/card_c1.png' },
    { id: 'SHORTS', title: 'Shorts', bg: './assets/cards/card_shorts.png' },
    { id: 'favorites', title: 'Favorites', bg: './assets/cards/card_favorites.png' }
  ];

  const cardsHtml = cards.map(c => `
    <div class="level-card" data-level-id="${c.id}">
      <div class="level-card-image-wrap">
        <img src="${c.bg}" alt="${c.title}" class="level-card-img" />
      </div>
      <div class="level-card-placard">
        <span>${c.title}</span>
      </div>
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
