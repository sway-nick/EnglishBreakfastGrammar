// Fallback catalog in case of network or path issues
const DEFAULT_CATALOG = {
  levels: [
    { id: 'A1', title: 'A1 Elementary', description: 'Основы грамматики: времена, местоимения, базовые конструкции', color: '#22c55e', icon: '🌱' },
    { id: 'A2', title: 'A2 Pre-Intermediate', description: 'Прошедшие времена, модальные глаголы, сравнения', color: '#3b82f6', icon: '📘' },
    { id: 'B1', title: 'B1 Intermediate', description: 'Совершенные времена, пассивный залог, условные предложения', color: '#f59e0b', icon: '⚡' },
    { id: 'B1-B2', title: 'B1+ Upper-Intermediate', description: 'Сложные грамматические структуры, герундий и инфинитив', color: '#8b5cf6', icon: '🎯' },
    { id: 'B2', title: 'B2 Pre-Advanced', description: 'Инверсия, смешанные условные, идиоматическая грамматика', color: '#ec4899', icon: '🔥' },
    { id: 'C1', title: 'C1 Advanced', description: 'Продвинутый уровень: нюансы стилистики, акцентные конструкции', color: '#06b6d4', icon: '👑' },
    { id: 'SHORTS', title: 'Grammar Shorts', description: 'Короткие тесты и правила на частые ошибки', color: '#10b981', icon: '💡' }
  ],
  lessons: []
};

export const GrammarService = {
  catalogCache: null,
  lessonsCache: {},

  async getCatalog() {
    if (this.catalogCache) return this.catalogCache;
    try {
      const catalogUrl = new URL('../assets/data/grammar_catalog.json', import.meta.url).href;
      const res = await fetch(catalogUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.catalogCache = await res.json();
      return this.catalogCache;
    } catch (e) {
      console.warn('Could not fetch grammar_catalog.json, using fallback catalog:', e);
      this.catalogCache = DEFAULT_CATALOG;
      return this.catalogCache;
    }
  },

  async getLesson(lessonId) {
    if (this.lessonsCache[lessonId]) return this.lessonsCache[lessonId];
    try {
      const lessonUrl = new URL(`../assets/data/lessons/${lessonId}.json`, import.meta.url).href;
      const res = await fetch(lessonUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.lessonsCache[lessonId] = data;
      return data;
    } catch (e) {
      console.error(`Failed to load lesson ${lessonId}:`, e);
      return {
        lesson_id: lessonId,
        level: 'A1',
        title: 'Урок грамматики',
        description: 'Практический тест и правила',
        theory: {
          title: 'Правила урока',
          level: 'A1',
          overview: 'Разбор ключевых грамматических правил.',
          rules: [
            {
              heading: 'Основное правило',
              content: 'Обратите внимание на порядок слов в предложении и форму глагола.'
            }
          ]
        },
        exercises: []
      };
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
