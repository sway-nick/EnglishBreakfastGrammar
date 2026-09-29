/**
 * Base Source Adapter
 *
 * All concrete parsers (TestEnglishAdapter, ManualAdapter, etc.) extend this.
 * The contract: parse(html) → Lesson (Universal Model).
 */

export class BaseSourceAdapter {
  /**
   * @param {string} providerName - e.g. 'test-english'
   */
  constructor(providerName) {
    this.provider = providerName;
  }

  /**
   * Parse raw HTML and return a Universal Lesson object.
   *
   * @param {string} html       - Raw HTML string
   * @param {Object} [options]  - Adapter-specific options
   * @returns {{ lesson: import('../../models/index.js').Lesson, report: ParseReport }}
   */
  // eslint-disable-next-line no-unused-vars
  parse(html, options = {}) {
    throw new Error(`${this.constructor.name}.parse() is not implemented`);
  }
}

/**
 * @typedef {Object} ParseReport
 * A structured summary of what the parser found.
 * Shown to the user BEFORE confirming the import.
 *
 * @property {string}   provider
 * @property {string}   [url]
 * @property {string}   lessonTitle
 * @property {string}   [lessonLevel]
 * @property {number}   exerciseCount
 * @property {number}   questionCount
 * @property {Object}   questionTypes   - { gap_select: N, single_choice: M, ... }
 * @property {number}   gapCount
 * @property {number}   optionCount
 * @property {string[]} warnings        - Non-fatal issues found during parsing
 * @property {string[]} errors          - Fatal issues that stopped the parse
 */

/**
 * Format a ParseReport for display in the console.
 * @param {ParseReport} report
 * @returns {string}
 */
export function formatReport(report) {
  const lines = [
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '  IMPORT REPORT',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    `  Provider:   ${report.provider}`,
    report.url ? `  URL:        ${report.url}` : null,
    `  Lesson:     ${report.lessonTitle}`,
    report.lessonLevel ? `  Level:      ${report.lessonLevel}` : null,
    `  Exercises:  ${report.exerciseCount}`,
    `  Questions:  ${report.questionCount}`,
  ];

  const types = Object.entries(report.questionTypes ?? {});
  if (types.length > 0) {
    lines.push('  Question types:');
    types.forEach(([type, count]) => {
      lines.push(`    ${type}: ${count}`);
    });
  }

  lines.push(`  Gaps:       ${report.gapCount}`);
  lines.push(`  Options:    ${report.optionCount}`);

  if (report.warnings?.length > 0) {
    lines.push('');
    lines.push(`  ⚠  Warnings (${report.warnings.length}):`);
    report.warnings.forEach(w => lines.push(`     - ${w}`));
  }

  if (report.errors?.length > 0) {
    lines.push('');
    lines.push(`  ✗  Errors (${report.errors.length}):`);
    report.errors.forEach(e => lines.push(`     - ${e}`));
  }

  lines.push('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  return lines.filter(l => l !== null).join('\n');
}
