import { GrammarService } from './services/grammarService.js';
import { StorageService } from './services/storageService.js';
import { t, setLanguage } from './services/i18n.js';

import { renderHeader } from './components/Header.js';
import { renderBurgerDrawer } from './components/BurgerDrawer.js';
import { renderLevelGrid } from './components/LevelGrid.js';
import { renderLessonList } from './components/LessonList.js';
import { renderGrammarRuleView } from './components/GrammarRuleView.js';
import { renderTestEngine } from './components/TestEngine.js';
import { renderTestResultModal } from './components/TestResultModal.js';
import { renderLeaderboardView } from './components/LeaderboardView.js';

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
      // Always hide splash screen
      if (window.hideAppSplashScreen) {
        window.hideAppSplashScreen();
      }
    }
  }

  applyTheme(theme) {
    StorageService.setTheme(theme);
    if (theme === 'dark') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }

  toggleTheme() {
    const current = StorageService.getTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    this.applyTheme(next);
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
      // 1. Header logo / home
      if (e.target.closest('#btn-header-home')) {
        this.navigate('levels');
        return;
      }

      // 2. Theme toggle
      if (e.target.closest('#btn-theme-toggle')) {
        this.toggleTheme();
        return;
      }

      // 3. Burger menu
      if (e.target.closest('#btn-burger-menu')) {
        this.state.isDrawerOpen = true;
        this.render();
        return;
      }

      // 4. Close drawer
      if (e.target.closest('#btn-close-drawer') || e.target.id === 'drawer-backdrop') {
        this.state.isDrawerOpen = false;
        this.render();
        return;
      }

      // 5. Drawer Nav Links
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

      // 6. Level card click
      const levelCard = e.target.closest('.level-card');
      if (levelCard) {
        const levelId = levelCard.getAttribute('data-level-id');
        this.navigate('lessons', { levelId });
        return;
      }

      // 7. Back to levels
      if (e.target.closest('#btn-back-to-levels') || e.target.closest('#btn-back-to-levels-from-lb')) {
        this.navigate('levels');
        return;
      }

      // 8. Lesson card click
      const lessonCard = e.target.closest('.lesson-card');
      if (lessonCard) {
        const lessonId = lessonCard.getAttribute('data-lesson-id');
        const lesson = await GrammarService.getLesson(lessonId);
        if (lesson) {
          this.navigate('theory', { lesson });
        }
        return;
      }

      // 9. Back to lesson list
      if (e.target.closest('#btn-back-to-lesson-list')) {
        this.navigate('lessons', { levelId: this.state.selectedLevelId || this.state.currentLesson?.level || 'A1' });
        return;
      }

      // 10. Start Test action button
      if (e.target.closest('#btn-start-test-action')) {
        this.navigate('test', { lesson: this.state.currentLesson });
        return;
      }

      // 11. Back to theory
      if (e.target.closest('#btn-back-to-theory')) {
        this.navigate('theory', { lesson: this.state.currentLesson });
        return;
      }

      // 12. Check Test Answers button
      if (e.target.closest('#btn-check-test-answers')) {
        this.evaluateTest();
        return;
      }

      // 13. Test result modal Continue
      if (e.target.closest('#btn-result-continue')) {
        const modal = document.getElementById('test-result-modal');
        if (modal) modal.remove();
        this.navigate('lessons', { levelId: this.state.currentLesson?.level || 'A1' });
        return;
      }

      // 14. Test result modal Retry
      if (e.target.closest('#btn-result-retry')) {
        const modal = document.getElementById('test-result-modal');
        if (modal) modal.remove();
        this.navigate('test', { lesson: this.state.currentLesson });
        return;
      }

      // 15. Choice label click selection
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

      // 16. Leaderboard tab switch
      const lbTab = e.target.closest('.leaderboard-tab');
      if (lbTab) {
        document.querySelectorAll('.leaderboard-tab').forEach(t => t.classList.remove('active'));
        lbTab.classList.add('active');
      }
    });

    // Language selection change
    document.addEventListener('change', (e) => {
      if (e.target.id === 'select-language') {
        setLanguage(e.target.value);
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

    const drawerHtml = this.state.isDrawerOpen ? renderBurgerDrawer() : '';

    appEl.innerHTML = `
      <div class="mobile-app">
        ${renderHeader()}
        <main id="screen-container">
          ${screenHtml}
        </main>
        ${drawerHtml}
      </div>
    `;
  }
}

// Start application safely whether DOM is ready or already loaded
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', () => new App());
} else {
  new App();
}
