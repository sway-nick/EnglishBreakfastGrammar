export const StorageService = {
  getXP() {
    return parseInt(localStorage.getItem('eb_grammar_xp') || '0', 10);
  },

  addXP(amount) {
    const newXP = this.getXP() + amount;
    localStorage.setItem('eb_grammar_xp', newXP.toString());
    return newXP;
  },

  getStreak() {
    return parseInt(localStorage.getItem('eb_grammar_streak') || '1', 10);
  },

  getCompletedLessons() {
    try {
      return JSON.parse(localStorage.getItem('eb_grammar_completed') || '{}');
    } catch (e) {
      return {};
    }
  },

  setLessonCompleted(lessonId, scorePercent) {
    const completed = this.getCompletedLessons();
    completed[lessonId] = {
      score: scorePercent,
      completedAt: new Date().toISOString()
    };
    localStorage.setItem('eb_grammar_completed', JSON.stringify(completed));
  },

  getTheme() {
    return localStorage.getItem('eb_grammar_theme') || 'light';
  },

  setTheme(theme) {
    localStorage.setItem('eb_grammar_theme', theme);
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem('eb_grammar_user') || 'null');
    } catch (e) {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem('eb_grammar_user', JSON.stringify(user));
  },

  getFavorites() {
    try {
      return JSON.parse(localStorage.getItem('eb_grammar_favorites') || '[]');
    } catch (e) {
      return [];
    }
  },

  toggleFavorite(lessonId) {
    let favs = this.getFavorites();
    if (favs.includes(lessonId)) {
      favs = favs.filter(id => id !== lessonId);
    } else {
      favs.push(lessonId);
    }
    localStorage.setItem('eb_grammar_favorites', JSON.stringify(favs));
    return favs;
  },

  isFavorite(lessonId) {
    return this.getFavorites().includes(lessonId);
  },

  getSoundEnabled() {
    const val = localStorage.getItem('eb_grammar_sound');
    return val === null ? true : val === 'true';
  },

  setSoundEnabled(enabled) {
    localStorage.setItem('eb_grammar_sound', enabled ? 'true' : 'false');
  }
};
