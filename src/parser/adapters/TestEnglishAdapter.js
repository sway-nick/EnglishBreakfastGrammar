/**
 * TestEnglishAdapter
 *
 * Parses HTML pages from test-english.com (WatuPRO-based quiz format).
 *
 * ─── Rule 12A ────────────────────────────────────────────────────────────────
 * The parser NEVER sets correct_answer or is_correct.
 * All answer fields are null / [] after import.
 * Correct answers are filled exclusively by the AI Answer Processing step.
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * Strategy — structural, not ID-based:
 *   - Finds the lesson/page title from <h1>/<h2>
 *   - Finds exercises via quiz containers (generic class patterns)
 *   - Extracts questions by looking for select/input elements
 *   - Infers type (gap_select | gap_text | single_choice | multiple_choice)
 *   - Extracts Explanation tab content
 *   - NEVER rewrites or "corrects" source content
 *   - Emits WARNINGs for ambiguous structures instead of guessing
 *
 * Source IDs (quiz-258, question-2242, etc.) are stored in SourceMeta only.
 */

import { parse as parseHTML } from 'node-html-parser';
import {
  createLesson,
  createExercise,
  createQuestion,
  createGap,
  createOption,
  IdCounter,
  QuestionType,
  ContentStatus,
} from '../../models/index.js';
import { BaseSourceAdapter } from '../BaseSourceAdapter.js';

// ---------------------------------------------------------------------------
// CONSTANTS — patterns we recognise from WatuPRO / test-english.com
// These are heuristics, NOT the backbone of our data model.
// ---------------------------------------------------------------------------

const QUIZ_CONTAINER_SELECTORS = [
  'form[id*="quiz"]',
  '[id*="quiz"]',
  '.watu-quiz',
  '.quiz-content',
  '.wp-block-group',
];

const QUESTION_CONTAINER_SELECTORS = [
  '.watu-question',
  '[id*="question"]',
  '[class*="question"]',
  'li.question',
];

// Selectors for the Explanation / Grammar tab on test-english.com
const EXPLANATION_SELECTORS = [
  '#tab-explanation',
  '[id*="explanation"]',
  '[class*="explanation"]',
  '.grammar-explanation',
  '.tab-content-explanation',
  '[data-tab="explanation"]',
  // WatuPRO uses tabli2 for Explanation
  '#tabli2',
  '.tabli2',
  '[id*="tabli2"]',
];

// ---------------------------------------------------------------------------
// HELPERS
// ---------------------------------------------------------------------------

/** Try to detect the level from common patterns in the page. */
function detectLevel(root) {
  const text = root.text;
  const match = text.match(/\b(A1|A2|B1|B2|C1|C2)\b/);
  return match ? match[1] : '';
}

/** Clean up whitespace from text content. */
function clean(str) {
  return (str ?? '').replace(/\s+/g, ' ').trim();
}

/**
 * Extract source ID from an element's id attribute.
 * e.g. 'question-2242' → '2242'
 */
function extractSourceId(el) {
  const id = el?.id ?? '';
  const match = id.match(/\d+$/);
  return match ? match[0] : id;
}

// ---------------------------------------------------------------------------
// CORE PARSER
// ---------------------------------------------------------------------------

export class TestEnglishAdapter extends BaseSourceAdapter {
  constructor() {
    super('test-english');
  }

  /**
   * @param {string} html
   * @param {{ url?: string, lessonId?: string, idSeed?: Object }} [options]
   */
  parse(html, options = {}) {
    const ids = new IdCounter();
    const warnings = [];
    const errors = [];

    // ── Seed IDs if a prefix is given (for multi-page / multi-lesson imports) ──
    if (options.idSeed) {
      Object.entries(options.idSeed).forEach(([prefix, val]) => ids.seed(prefix, val));
    }

    const root = parseHTML(html, {
      lowerCaseTagName: false,
      comment: false,
      blockTextElements: { style: false, script: false },
    });

    // ── Lesson title ──────────────────────────────────────────────────────────
    const h1 = root.querySelector('h1');
    const h2 = root.querySelector('h2');
    const lessonTitle = clean(h1?.text ?? h2?.text ?? 'Untitled Lesson');
    const level = detectLevel(root);

    if (!h1 && !h2) {
      warnings.push('No <h1> or <h2> found — lesson title may be inaccurate');
    }

    // ── Extract Explanation tab ───────────────────────────────────────────────
    const { explanationText, explanationHtml } = this.#extractExplanation(root, warnings);

    // ── Find quiz/exercise containers ─────────────────────────────────────────
    const exerciseContainers = this.#findExerciseContainers(root, warnings);

    // ── Build Lesson ──────────────────────────────────────────────────────────
    const lessonId = options.lessonId ?? ids.next('L');
    const exercises = [];
    let totalGaps = 0;
    let totalOptions = 0;
    const questionTypeCounts = {};

    exerciseContainers.forEach((container, exIdx) => {
      const exerciseId = ids.next('E');

      const instruction = this.#extractInstruction(container, warnings);
      const exTitle     = this.#extractExerciseTitle(container, exIdx + 1);

      const { questions, gapCount, optionCount, typeCounts, exWarnings } =
        this.#extractQuestions(container, exerciseId, ids, explanationText);

      exWarnings.forEach(w => warnings.push(w));
      totalGaps    += gapCount;
      totalOptions += optionCount;
      Object.entries(typeCounts).forEach(([t, n]) => {
        questionTypeCounts[t] = (questionTypeCounts[t] ?? 0) + n;
      });

      exercises.push(createExercise({
        id:          exerciseId,
        lessonId,
        order:       exIdx + 1,
        title:       exTitle,
        instruction,
        status:      ContentStatus.DRAFT,
        questions,
        source: {
          provider:   this.provider,
          url:        options.url ?? '',
          sourceId:   extractSourceId(container),
          importedAt: new Date().toISOString(),
        },
      }));
    });

    if (exercises.length === 0) {
      errors.push('No exercise containers found — is this a test-english.com page?');
    }

    const lesson = createLesson({
      id:          lessonId,
      title:       lessonTitle,
      level,
      description: '',
      status:      ContentStatus.DRAFT,
      order:       1,
      version:     1,
      exercises,
      source: {
        provider:       this.provider,
        url:            options.url ?? '',
        importedAt:     new Date().toISOString(),
        explanationHtml: explanationHtml || null,
      },
    });

    const report = {
      provider:           this.provider,
      url:                options.url ?? '',
      lessonTitle,
      lessonLevel:        level,
      exerciseCount:      exercises.length,
      questionCount:      exercises.reduce((s, e) => s + e.questions.length, 0),
      questionTypes:      questionTypeCounts,
      gapCount:           totalGaps,
      optionCount:        totalOptions,
      hasExplanation:     !!explanationText,
      explanationPreview: explanationText ? explanationText.slice(0, 120) + '…' : null,
      warnings,
      errors,
    };

    return { lesson, report };
  }

  // ── Private: extract Explanation tab content ─────────────────────────────

  #extractExplanation(root, warnings) {
    let explanationEl = null;

    for (const sel of EXPLANATION_SELECTORS) {
      explanationEl = root.querySelector(sel);
      if (explanationEl) break;
    }

    if (!explanationEl) {
      warnings.push('No Explanation tab found — explanationText will be empty');
      return { explanationText: '', explanationHtml: '' };
    }

    // Preserve the full HTML for later rendering but also extract clean text
    const explanationHtml = explanationEl.innerHTML ?? '';
    const explanationText = clean(explanationEl.text);

    return { explanationText, explanationHtml };
  }

  // ── Private: find exercise containers ─────────────────────────────────────

  #findExerciseContainers(root, warnings) {
    let containers = [];

    for (const selector of QUIZ_CONTAINER_SELECTORS) {
      const found = root.querySelectorAll(selector);
      if (found.length > 0) {
        containers = found;
        break;
      }
    }

    // If no named containers, treat the whole body as one exercise
    if (containers.length === 0) {
      const body = root.querySelector('body') ?? root;
      const hasInteractives = body.querySelector(
        'select, input[type=radio], input[type=checkbox], input[type=text]'
      );
      if (hasInteractives) {
        warnings.push('No explicit quiz container found — treating entire page as one exercise');
        containers = [body];
      }
    }

    // Filter out containers that have no interactive elements
    containers = containers.filter(c =>
      c.querySelector('select, input[type=radio], input[type=checkbox], input[type=text]')
    );

    return containers;
  }

  // ── Private: extract exercise instruction ──────────────────────────────────

  #extractInstruction(container, _warnings) {
    const instrEl = container.querySelector(
      '[class*="instruction"], [class*="description"], p.intro, .exercise-intro'
    );
    if (instrEl) return clean(instrEl.text);

    // Fallback: first <p> that doesn't contain an <input>/<select>
    const paras = container.querySelectorAll('p');
    for (const p of paras) {
      if (!p.querySelector('select, input')) {
        const text = clean(p.text);
        if (text.length > 5) return text;
      }
    }

    return '';
  }

  // ── Private: extract exercise title ───────────────────────────────────────

  #extractExerciseTitle(container, fallbackIndex) {
    const h = container.querySelector('h2, h3, h4, .exercise-title');
    if (h) return clean(h.text);
    return `Exercise ${fallbackIndex}`;
  }

  // ── Private: extract questions from an exercise container ──────────────────

  #extractQuestions(container, exerciseId, ids, explanationText) {
    const exWarnings = [];
    const questions  = [];
    let gapCount    = 0;
    let optionCount = 0;
    const typeCounts = {};

    // Try structural question detection
    let questionEls = [];
    for (const sel of QUESTION_CONTAINER_SELECTORS) {
      questionEls = container.querySelectorAll(sel);
      if (questionEls.length > 0) break;
    }

    if (questionEls.length === 0) {
      questionEls = this.#buildSyntheticQuestions(container, exWarnings);
    }

    questionEls.forEach((qEl, qIdx) => {
      const qId     = ids.next('Q');
      const sourceId = extractSourceId(qEl);

      // Detect question type
      const selects   = qEl.querySelectorAll('select');
      const textInputs = qEl.querySelectorAll('input[type=text]');
      const radios    = qEl.querySelectorAll('input[type=radio]');
      const checkboxes = qEl.querySelectorAll('input[type=checkbox]');

      let type;
      if (selects.length > 0) {
        type = QuestionType.GAP_SELECT;
      } else if (textInputs.length > 0) {
        type = QuestionType.GAP_TEXT;
      } else if (radios.length > 0) {
        type = QuestionType.SINGLE_CHOICE;
      } else if (checkboxes.length > 0) {
        type = QuestionType.MULTIPLE_CHOICE;
      } else {
        type = QuestionType.GAP_SELECT;
        exWarnings.push(`Q${qIdx + 1}: Could not determine question type — defaulting to gap_select`);
      }

      typeCounts[type] = (typeCounts[type] ?? 0) + 1;

      // Build question text with {{gapN}} placeholders; extract gaps + options
      const { text, gaps: rawGaps } = this.#buildQuestionText(qEl, type, ids, exWarnings);
      gapCount += rawGaps.length;

      // Build choice options (for single/multiple choice questions)
      let options = [];
      if (type === QuestionType.SINGLE_CHOICE || type === QuestionType.MULTIPLE_CHOICE) {
        options = this.#extractChoiceOptions(qEl, type, ids);
        optionCount += options.length;
      }
      rawGaps.forEach(g => { optionCount += g.options.length; });

      const feedback = this.#extractFeedback(qEl);

      questions.push(createQuestion({
        id:          qId,
        order:       qIdx + 1,
        type,
        text,
        gaps:        rawGaps,
        options,
        hint:        '',
        feedback,
        explanation: explanationText,   // shared Explanation tab text for this exercise page
        source: {
          provider:   this.provider,
          sourceId,
          importedAt: new Date().toISOString(),
        },
      }));
    });

    return { questions, gapCount, optionCount, typeCounts, exWarnings };
  }

  // ── Private: build question text + gap objects ─────────────────────────────

  #buildQuestionText(qEl, type, ids, warnings) {
    const gaps = [];

    if (type !== QuestionType.GAP_SELECT && type !== QuestionType.GAP_TEXT) {
      const text = clean(this.#getQuestionTextOnly(qEl));
      return { text, gaps };
    }

    // Clone the element so we can manipulate it
    const clone    = parseHTML(qEl.toString());
    const selects  = clone.querySelectorAll('select');
    const inputs   = clone.querySelectorAll('input[type=text]');
    const interactives = type === QuestionType.GAP_SELECT ? selects : inputs;

    let gapIndex = 0;

    interactives.forEach(el => {
      gapIndex++;
      const placeholder = `{{gap${gapIndex}}}`;
      const gapId = ids.next('G');

      // ── Rule 12A: extract options WITHOUT marking any as correct ───────────
      let gapOptions = [];
      if (type === QuestionType.GAP_SELECT) {
        const optEls = el.querySelectorAll('option');
        let optIndex = 0;
        optEls.forEach(optEl => {
          const val = clean(optEl.text);
          if (!val || val === '---' || val === '--' || val === '—') return; // skip placeholders

          optIndex++;
          const optId = ids.next('O');

          gapOptions.push(createOption({
            id:         optId,
            order:      optIndex,
            value:      val,
            is_correct: null,   // Rule 12A: never set by parser
          }));
        });
      }

      gaps.push(createGap({
        id:               gapId,
        order:            gapIndex,
        placeholder,
        options:          gapOptions,
        correct_answer:   null,   // Rule 12A: set by AI Answer Processing
        accepted_answers: [],     // Rule 12A: set by AI Answer Processing
        review_required:  false,
      }));

      // Replace the interactive element with the placeholder text in the clone
      el.replaceWith(placeholder);
    });

    // Extract clean text from the modified clone
    let text = clean(
      clone.querySelector('[id*="question"], .question, li, div')?.text ?? clone.text
    );
    text = text.replace(/\s{2,}/g, ' ').trim();

    return { text, gaps };
  }

  // ── Private: extract text excluding interactive elements ───────────────────

  #getQuestionTextOnly(qEl) {
    const clone = parseHTML(qEl.toString());
    clone.querySelectorAll(
      'ul.options, ol.options, .answers, input, select, button'
    ).forEach(el => el.remove());
    return clean(clone.text);
  }

  // ── Private: extract choice options ───────────────────────────────────────
  // Rule 12A: is_correct is always null; never set by parser.

  #extractChoiceOptions(qEl, type, ids) {
    const inputs = qEl.querySelectorAll(
      type === QuestionType.SINGLE_CHOICE ? 'input[type=radio]' : 'input[type=checkbox]'
    );
    const options = [];
    let optIndex = 0;

    inputs.forEach(input => {
      optIndex++;
      const optId = ids.next('O');

      // Find associated label
      const inputId = input.id;
      let label;
      if (inputId) {
        label = qEl.querySelector(`label[for="${inputId}"]`);
      }
      if (!label) {
        label = input.parentNode?.querySelector('label') ?? input.nextElementSibling;
      }

      const value = clean(label?.text ?? input.getAttribute('value') ?? '');

      options.push(createOption({
        id:         optId,
        order:      optIndex,
        value,
        is_correct: null,   // Rule 12A: set by AI Answer Processing
      }));
    });

    return options;
  }

  // ── Private: extract feedback ─────────────────────────────────────────────

  #extractFeedback(qEl) {
    const fbEl = qEl.querySelector(
      '[class*="feedback"], [class*="rationale"], .note'
    );
    return fbEl ? clean(fbEl.text) : '';
  }

  // ── Private: build synthetic questions when no explicit containers exist ───

  #buildSyntheticQuestions(container, warnings) {
    const candidates = container.querySelectorAll('li, p, div');
    const questionEls = candidates.filter(el =>
      el.querySelector('select, input[type=radio], input[type=checkbox], input[type=text]') &&
      !el.querySelector(QUESTION_CONTAINER_SELECTORS.join(','))
    );

    if (questionEls.length > 0) {
      warnings.push(`Using synthetic question detection (${questionEls.length} found)`);
    }

    return questionEls;
  }
}
