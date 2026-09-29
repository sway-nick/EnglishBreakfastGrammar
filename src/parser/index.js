/**
 * Parser Registry
 *
 * Maps provider names to their Source Adapters.
 * Add new adapters here as new sources are supported.
 */

import { TestEnglishAdapter } from './adapters/TestEnglishAdapter.js';

const ADAPTERS = {
  'test-english': () => new TestEnglishAdapter(),
  // 'source-b':    () => new SourceBAdapter(),
  // 'manual':      () => new ManualContentAdapter(),
};

/**
 * Get an adapter by provider name.
 * @param {string} provider
 * @returns {import('./BaseSourceAdapter.js').BaseSourceAdapter}
 */
export function getAdapter(provider) {
  const factory = ADAPTERS[provider];
  if (!factory) {
    throw new Error(
      `Unknown provider: "${provider}". Available: ${Object.keys(ADAPTERS).join(', ')}`
    );
  }
  return factory();
}

/**
 * Auto-detect the provider from HTML content.
 * Falls back to 'test-english' if no match.
 *
 * @param {string} html
 * @returns {string} provider name
 */
export function detectProvider(html) {
  if (html.includes('test-english.com') || html.includes('watu') || html.includes('WatuPRO')) {
    return 'test-english';
  }
  // Add more detection patterns as new sources are added
  return 'test-english'; // default
}

export { TestEnglishAdapter };
