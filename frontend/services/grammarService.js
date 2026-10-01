export const GrammarService = {
  catalogCache: null,
  lessonsCache: {},

  async getCatalog() {
    if (this.catalogCache) return this.catalogCache;
    try {
      const res = await fetch('./assets/data/grammar_catalog.json');
      this.catalogCache = await res.json();
      return this.catalogCache;
    } catch (e) {
      console.error('Failed to load grammar catalog:', e);
      return { levels: [], lessons: [] };
    }
  },

  async getLesson(lessonId) {
    if (this.lessonsCache[lessonId]) return this.lessonsCache[lessonId];
    try {
      const res = await fetch(`./assets/data/lessons/${lessonId}.json`);
      const data = await res.json();
      this.lessonsCache[lessonId] = data;
      return data;
    } catch (e) {
      console.error(`Failed to load lesson ${lessonId}:`, e);
      return null;
    }
  },

  normalizeText(text) {
    if (!text) return '';
    return text
      .trim()
      .toLowerCase()
      .replace(/[\u2018\u2019\u0060\u00B4]/g, "'") // normalize curly apostrophes
      .replace(/\s+/g, ' ');
  },

  checkGapAnswer(userAnswer, gap) {
    const normUser = this.normalizeText(userAnswer);
    if (!normUser) return { isCorrect: false, correctAnswer: gap.correct_answer || (gap.accepted_answers && gap.accepted_answers[0]) || '' };

    const accepted = (gap.accepted_answers || []).map(a => this.normalizeText(a));
    if (gap.correct_answer) {
      accepted.push(this.normalizeText(gap.correct_answer));
    }

    const isCorrect = accepted.includes(normUser);
    return {
      isCorrect,
      correctAnswer: gap.correct_answer || gap.accepted_answers?.[0] || ''
    };
  },

  checkOptionAnswer(selectedOptionId, options) {
    const chosen = options.find(o => o.option_id === selectedOptionId);
    const correctOpt = options.find(o => o.is_correct);
    return {
      isCorrect: Boolean(chosen && chosen.is_correct),
      correctAnswer: correctOpt ? correctOpt.text : ''
    };
  }
};
