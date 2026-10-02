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

  rulesCache: {},

  async getRulesForLanguage(lang = 'ru') {
    if (this.rulesCache[lang]) return this.rulesCache[lang];
    try {
      const rulesUrl = new URL(`../assets/data/rules/rules_${lang}.json`, import.meta.url).href;
      const res = await fetch(rulesUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.rulesCache[lang] = data;
      return data;
    } catch (e) {
      console.warn(`Could not load rules for ${lang}, falling back to ru:`, e);
      if (lang !== 'ru') return this.getRulesForLanguage('ru');
      return [];
    }
  },

  async getRuleForLesson(lesson, lang = 'ru') {
    if (!lesson) return null;
    try {
      const rules = await this.getRulesForLanguage(lang);
      if (!rules || !rules.length) return null;

      const lessonNum = lesson.theory?.lesson_num;
      const lessonLevel = (lesson.theory?.level || lesson.level || '').toUpperCase().trim();
      const lessonTitle = (lesson.title || '').toLowerCase().trim();
      const normLevel = (lvl) => {
        const u = String(lvl || '').toUpperCase().trim();
        if (u === 'B1-B2' || u === 'B1+') return 'B1+';
        if (u === 'SHORTS' || u === 'GRAMMAR SHORTS') return 'GRAMMAR SHORTS';
        return u;
      };

      // 1. Exact match by lesson_num and level
      if (lessonNum !== undefined && lessonNum !== null) {
        const matched = rules.find(r => 
          normLevel(r['Level']) === normLevel(lessonLevel) &&
          parseInt(r['Lesson #'], 10) === parseInt(lessonNum, 10)
        );
        if (matched) return matched;
      }

      // 2. Match by Rule ID if available
      if (lesson.theory?.rule_id) {
        const baseRuleId = lesson.theory.rule_id.replace(/-[A-Z]{2}$/i, '');
        const matched = rules.find(r => (r['Rule ID'] || '').startsWith(baseRuleId));
        if (matched) return matched;
      }

      // 3. Fallback: match by Topic / title
      const matched = rules.find(r => {
        const topic = (r['Lesson / Topic'] || '').toLowerCase().trim();
        return topic && (lessonTitle.includes(topic) || topic.includes(lessonTitle));
      });

      return matched || null;
    } catch (e) {
      console.warn('Error matching rule for lesson:', e);
      return null;
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
