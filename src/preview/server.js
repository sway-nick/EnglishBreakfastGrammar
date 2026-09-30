/**
 * Preview Server
 *
 * Serves a local preview of a Universal Lesson JSON as an interactive test.
 * This is the Test Engine in its simplest form — it reads local JSON,
 * not Firebase, making it fast and useful for validation before publish.
 *
 * Usage:
 *   node src/preview/server.js --input data/json/L001.json [--port 3456] [--allow-unresolved] [--force]
 *
 * Note on --force:
 *   --force is strictly a local developer/debugging escape hatch.
 *   It allows rendering malformed content for debugging purposes only.
 *   It is NOT an acceptable mechanism for publish, test engine runtime, or automated pipelines.
 */

import { createServer } from 'http';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import { renderPreviewHTML } from './renderer.js';
import { validate, formatResult } from '../validation/index.js';

/**
 * Validates lesson against the preview validation gate.
 *
 * @param {Object} lesson
 * @param {Object} [options]
 * @param {boolean} [options.allowUnresolved=false] - Permit Rule 12A drafts awaiting AI resolution
 * @param {boolean} [options.force=false] - Local dev-only bypass; never permitted in production/runtime
 * @returns {{ valid: boolean, shouldBlock: boolean, isBypassed: boolean, validationResult: import('../validation/index.js').ValidationResult }}
 */
export function checkPreviewGate(lesson, { allowUnresolved = false, force = false } = {}) {
  const validationResult = validate(lesson, { allowUnresolved });
  const shouldBlock = !validationResult.valid && !force;
  const isBypassed = !validationResult.valid && Boolean(force);

  return {
    valid: validationResult.valid,
    shouldBlock,
    isBypassed,
    validationResult,
  };
}

// ── CLI Execution ───────────────────────────────────────────────────────────

export function startPreviewServer(args = process.argv.slice(2)) {
  function getArg(f) { const i = args.indexOf(f); return i !== -1 ? args[i+1] : null; }
  function hasFlag(f) { return args.includes(f); }

  const inputPath = getArg('--input');
  const port = parseInt(getArg('--port') ?? process.env.PREVIEW_PORT ?? '3456', 10);
  const allowUnresolved = hasFlag('--allow-unresolved');
  const force = hasFlag('--force');

  if (!inputPath) {
    console.error('❌ Usage: node src/preview/server.js --input data/json/L001.json [--allow-unresolved] [--force]');
    return process.exit(1);
  }

  const absInput = resolve(inputPath);
  let lesson;

  try {
    lesson = JSON.parse(readFileSync(absInput, 'utf-8'));
  } catch (err) {
    console.error(`❌ Cannot read/parse JSON: ${absInput}\n   ${err.message}`);
    return process.exit(1);
  }

  // ── Explicit Validation Gate (ADR-002) ────────────────────────────────────
  const gate = checkPreviewGate(lesson, { allowUnresolved, force });
  console.log('\n--- Lesson Validation ---');
  console.log(formatResult(gate.validationResult));

  if (gate.shouldBlock) {
    console.error('❌ Preview startup blocked: lesson failed validation.');
    console.error('   Fix validation errors above, or use --allow-unresolved for drafts, or --force (DEBUG ONLY) to bypass.\n');
    return process.exit(1);
  }

  if (gate.isBypassed) {
    console.warn('\n⚠️ [SECURITY/INTEGRITY WARNING]: Preview started with --force.');
    console.warn('   --force is strictly a developer-only debug escape hatch for local preview.');
    console.warn('   This content FAILS validation and MUST NEVER be used in publish or runtime workflows.\n');
  }

  const server = createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(renderPreviewHTML(lesson));
  });

  server.listen(port, () => {
    const url = `http://localhost:${port}`;
    console.log(`🔍 Preview running: ${url}`);
    console.log(`   Lesson: ${lesson.title} (${lesson.id})`);
    console.log(`   Press Ctrl+C to stop\n`);

    if (!process.env.NO_OPEN) {
      import('open').then(m => m.default(url)).catch(() => {});
    }
  });

  return server;
}

// Auto-run if executed directly as CLI script
const isMain = process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url));
if (isMain) {
  startPreviewServer();
}
