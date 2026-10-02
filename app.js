import { GrammarService } from './services/grammarService.js?v=3.1';
import { StorageService } from './services/storageService.js?v=3.1';
import { t, setLanguage } from './services/i18n.js?v=3.1';

import { renderHeader } from './components/Header.js?v=3.1';
import { renderBurgerDrawer } from './components/BurgerDrawer.js?v=3.1';
import { renderLevelGrid } from './components/LevelGrid.js?v=3.1';
import { renderLessonList } from './components/LessonList.js?v=3.1';
import { renderGrammarRuleView } from './components/GrammarRuleView.js?v=3.1';
import { renderTestEngine } from './components/TestEngine.js?v=3.1';
import { renderTestResultModal } from './components/TestResultModal.js?v=3.1';
import { renderLeaderboardView, initLeaderboardEvents } from './components/LeaderboardView.js?v=3.1';

class App {
  constructor() {
    this.state = {
      screen: 'levels', // 'levels' | 'lessons' | 'theory' | 'test' | 'leaderboard'
      selectedLevelId: null,
      currentLesson: null,
      catalog: null,
      isDrawerOpen: false,
      testUserAnswers: {}
    };

    this.init();
  }

  async init() {
    try {
      this.applyTheme(StorageService.getTheme());
      this.state.catalog = await GrammarService.getCatalog();
      this.bindGlobalEvents();
      this.render();
    } catch (e) {
      console.error('App init error:', e);
    } finally {
      if (window.hideAppSplashScreen) {
        window.hideAppSplashScreen();
      }
    }
  }

  applyTheme(theme) {
    StorageService.setTheme(theme);
    const isDark = theme === 'dark';
    if (isDark) {
      document.body.classList.add('dark-theme');
      document.documentElement.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
      document.documentElement.classList.remove('dark-theme');
    }
  }

  setAppTheme(theme) {
    this.applyTheme(theme);
    this.render();
  }

  navigate(screen, payload = {}) {
    this.state.screen = screen;
    if (payload.levelId !== undefined) this.state.selectedLevelId = payload.levelId;
    if (payload.lesson !== undefined) this.state.currentLesson = payload.lesson;
    this.state.isDrawerOpen = false;
    this.state.testUserAnswers = {};
    this.render();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  bindGlobalEvents() {
    document.addEventListener('click', async (e) => {
      // 1. Header logo / brand home
      if (e.target.closest('#brand-logo')) {
        this.navigate('levels');
        return;
      }

      // 2. Header XP button -> Leaderboard
      if (e.target.closest('#header-xp-btn')) {
        this.navigate('leaderboard');
        return;
      }

      // 3. Header Burger button -> Toggle Drawer
      if (e.target.closest('#header-burger-btn')) {
        this.state.isDrawerOpen = !this.state.isDrawerOpen;
        this.render();
        return;
      }

      // 4. Close Drawer
      if (e.target.closest('#drawer-close-btn') || e.target.id === 'drawer-overlay') {
        this.state.isDrawerOpen = false;
        this.render();
        return;
      }

      // 5. Drawer Theme Buttons
      if (e.target.closest('#theme-light-btn')) {
        this.setAppTheme('light');
        return;
      }

      if (e.target.closest('#theme-dark-btn')) {
        this.setAppTheme('dark');
        return;
      }

      // 6. Drawer Sound & Voice Toggles
      if (e.target.closest('#sfx-on-btn')) {
        document.getElementById('sfx-on-btn')?.classList.add('active');
        document.getElementById('sfx-off-btn')?.classList.remove('active');
        return;
      }

      if (e.target.closest('#sfx-off-btn')) {
        document.getElementById('sfx-off-btn')?.classList.add('active');
        document.getElementById('sfx-on-btn')?.classList.remove('active');
        return;
      }

      if (e.target.closest('#voice-uk-btn')) {
        document.getElementById('voice-uk-btn')?.classList.add('active');
        document.getElementById('voice-us-btn')?.classList.remove('active');
        return;
      }

      if (e.target.closest('#voice-us-btn')) {
        document.getElementById('voice-us-btn')?.classList.add('active');
        document.getElementById('voice-uk-btn')?.classList.remove('active');
        return;
      }

      // 7. Drawer Nav Links
      if (e.target.closest('#btn-nav-levels')) {
        this.navigate('levels');
        return;
      }

      if (e.target.closest('#btn-nav-leaderboard')) {
        this.navigate('leaderboard');
        return;
      }

      if (e.target.closest('#btn-reset-demo')) {
        if (confirm('Сбросить весь демо-прогресс и очки?')) {
          localStorage.removeItem('eb_grammar_xp');
          localStorage.removeItem('eb_grammar_completed');
          this.navigate('levels');
        }
        return;
      }

      if (e.target.closest('#link-privacy-policy')) {
        alert('English Breakfast Grammar • Privacy Policy\nДанные сохраняются локально на вашем устройстве для обеспечения конфиденциальности.');
        return;
      }

      // 8. Level card click
      const levelCard = e.target.closest('.level-card');
      if (levelCard) {
        const levelId = levelCard.getAttribute('data-level-id');
        this.navigate('lessons', { levelId });
        return;
      }

      // 9. Back to levels
      if (e.target.closest('#btn-back-to-levels') || e.target.closest('#btn-back-to-levels-from-lb')) {
        this.navigate('levels');
        return;
      }

      // 10. Lesson card click
      const lessonCard = e.target.closest('.lesson-card');
      if (lessonCard) {
        try {
          const lessonId = lessonCard.getAttribute('data-lesson-id');
          const lesson = await GrammarService.getLesson(lessonId);
          if (lesson) {
            const lang = getLanguage();
            try {
              lesson._localizedRule = await GrammarService.getRuleForLesson(lesson, lang);
            } catch (ruleErr) {
              console.warn('Could not load localized rule:', ruleErr);
            }
            this.navigate('theory', { lesson });
          }
        } catch (err) {
          console.error('Error loading lesson:', err);
        }
        return;
      }

      // 11. Back to lesson list
      if (e.target.closest('#btn-back-to-lesson-list')) {
        this.navigate('lessons', { levelId: this.state.selectedLevelId || this.state.currentLesson?.level || 'A1' });
        return;
      }

      // 11b. Toggle favorite in grammar rule
      const favBtn = e.target.closest('#btn-toggle-favorite');
      if (favBtn) {
        const lessonId = favBtn.getAttribute('data-lesson-id');
        if (lessonId) {
          StorageService.toggleFavorite(lessonId);
          const isFav = StorageService.isFavorite(lessonId);
          favBtn.textContent = isFav ? '⭐' : '☆';
          favBtn.style.color = isFav ? '#f59e0b' : 'var(--text-muted)';
        }
        return;
      }

      // 12. Start Test action button
      if (e.target.closest('#btn-start-test-action')) {
        this.navigate('test', { lesson: this.state.currentLesson });
        return;
      }

      // 13. Back to theory
      if (e.target.closest('#btn-back-to-theory')) {
        this.navigate('theory', { lesson: this.state.currentLesson });
        return;
      }

      // 14. Check Test Answers button
      if (e.target.closest('#btn-check-test-answers')) {
        this.evaluateTest();
        return;
      }

      // 15. Test result modal Continue
      if (e.target.closest('#btn-result-continue')) {
        const modal = document.getElementById('test-result-modal');
        if (modal) modal.remove();
        this.navigate('lessons', { levelId: this.state.currentLesson?.level || 'A1' });
        return;
      }

      // 16. Test result modal Retry
      if (e.target.closest('#btn-result-retry')) {
        const modal = document.getElementById('test-result-modal');
        if (modal) modal.remove();
        this.navigate('test', { lesson: this.state.currentLesson });
        return;
      }

      // 17. Choice label click selection
      const choiceLabel = e.target.closest('.choice-label');
      if (choiceLabel) {
        const radio = choiceLabel.querySelector('input[type="radio"]');
        if (radio) {
          const name = radio.name;
          document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
            inp.closest('.choice-label')?.classList.remove('selected');
          });
          radio.checked = true;
          choiceLabel.classList.add('selected');
        }
      }

      // 18. Leaderboard tab switch
      const lbTab = e.target.closest('.leaderboard-tab');
      if (lbTab) {
        document.querySelectorAll('.leaderboard-tab').forEach(t => t.classList.remove('active'));
        lbTab.classList.add('active');
      }
    });

    // Language selection change
    document.addEventListener('change', async (e) => {
      if (e.target.id === 'select-language') {
        const newLang = e.target.value;
        setLanguage(newLang);
        if (this.state.screen === 'theory' && this.state.currentLesson) {
          this.state.currentLesson._localizedRule = await GrammarService.getRuleForLesson(this.state.currentLesson, newLang);
        }
        this.render();
      }
    });
  }

  evaluateTest() {
    const lesson = this.state.currentLesson;
    if (!lesson || !lesson.exercises) return;

    let totalPoints = 0;
    let earnedPoints = 0;

    lesson.exercises.forEach(ex => {
      (ex.questions || []).forEach(q => {
        totalPoints++;
        let questionCorrect = true;
        let correctHint = '';

        // Evaluate Gaps
        if (q.gaps && q.gaps.length > 0) {
          q.gaps.forEach(gap => {
            const gapInput = document.querySelector(`[data-gap-id="${gap.gap_id}"]`);
            const userVal = gapInput ? gapInput.value : '';
            const res = GrammarService.checkGapAnswer(userVal, gap);

            if (gapInput) {
              gapInput.classList.remove('is-correct', 'is-wrong');
              gapInput.classList.add(res.isCorrect ? 'is-correct' : 'is-wrong');
            }

            if (!res.isCorrect) {
              questionCorrect = false;
              correctHint += (correctHint ? ', ' : '') + `Правильно: «${res.correctAnswer}»`;
            }
          });
        }
        // Evaluate Choice Options
        else if (q.options && q.options.length > 0) {
          const isMulti = q.response_model === 'multiple_choice';
          if (!isMulti) {
            const selectedRadio = document.querySelector(`input[name="q_${q.question_id}"]:checked`);
            const selectedOptId = selectedRadio ? selectedRadio.value : null;
            const res = GrammarService.checkOptionAnswer(selectedOptId, q.options);

            const allLabels = document.querySelectorAll(`[data-question-id="${q.question_id}"].choice-label, .question-item[data-question-id="${q.question_id}"] .choice-label`);
            allLabels.forEach(lbl => {
              const optId = lbl.getAttribute('data-option-id');
              const opt = q.options.find(o => o.option_id === optId);
              if (opt && opt.is_correct) {
                lbl.classList.add('is-correct');
              } else if (optId === selectedOptId && !res.isCorrect) {
                lbl.classList.add('is-wrong');
              }
            });

            if (!res.isCorrect) {
              questionCorrect = false;
              correctHint = `Правильный ответ: «${res.correctAnswer}»`;
            }
          }
        }

        if (questionCorrect) {
          earnedPoints++;
        }

        // Show feedback block
        const feedbackEl = document.getElementById(`feedback-${q.question_id}`);
        if (feedbackEl) {
          feedbackEl.style.display = 'block';
          feedbackEl.className = `answer-feedback ${questionCorrect ? 'correct' : 'wrong'}`;
          let explanationText = q.explanation || '';
          if (questionCorrect) {
            feedbackEl.innerHTML = `✓ Отлично! ${explanationText}`;
          } else {
            feedbackEl.innerHTML = `✗ ${correctHint}. ${explanationText}`;
          }
        }
      });
    });

    const percent = Math.round((earnedPoints / (totalPoints || 1)) * 100);
    const xpReward = percent >= 80 ? 50 : (percent >= 50 ? 25 : 10);

    // Save Progress
    StorageService.addXP(xpReward);
    StorageService.setLessonCompleted(lesson.lesson_id, percent);

    // Update Header counters instantly
    const xpVal = document.getElementById('header-xp-val');
    if (xpVal) xpVal.textContent = StorageService.getXP();

    // Show Result Modal
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = renderTestResultModal(percent, xpReward);
    document.body.appendChild(modalContainer.firstElementChild);
  }

  render() {
    const appEl = document.getElementById('app');
    if (!appEl) return;

    let screenHtml = '';
    try {
      switch (this.state.screen) {
        case 'lessons':
          screenHtml = renderLessonList(this.state.selectedLevelId || 'A1', this.state.catalog);
          break;
        case 'theory':
          screenHtml = renderGrammarRuleView(this.state.currentLesson);
          break;
        case 'test':
          screenHtml = renderTestEngine(this.state.currentLesson);
          break;
        case 'leaderboard':
          screenHtml = renderLeaderboardView();
          break;
        case 'levels':
        default:
          screenHtml = renderLevelGrid(this.state.catalog);
          break;
      }
    } catch (renderErr) {
      console.error('Render error on screen ' + this.state.screen + ':', renderErr);
      screenHtml = `
        <div style="padding: 24px; text-align: center;">
          <p style="color: #ef4444; font-weight: 700;">Ошибка отображения экрана: ${renderErr.message}</p>
          <button class="back-btn" id="btn-back-to-levels" style="margin-top: 12px;">← На главную</button>
        </div>
      `;
    }

    const drawerHtml = this.state.isDrawerOpen ? renderBurgerDrawer() : '';
    const currentTheme = StorageService.getTheme();

    appEl.innerHTML = `
      <div class="mobile-app ${currentTheme === 'dark' ? 'dark-theme' : ''}">
        ${renderHeader()}
        <main class="app-main-content">
          <div id="app-content">
            ${screenHtml}
          </div>
        </main>
        <footer class="app-footer">
          <a href="#" id="link-privacy-policy">Privacy Policy</a>
        </footer>
        ${drawerHtml}
      </div>
    `;

    if (this.state.screen === 'leaderboard') {
      initLeaderboardEvents();
    }
  }
}

// Start application safely
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', () => new App());
} else {
  new App();
}
