#!/usr/bin/env node
/**
 * Parser CLI
 *
 * Usage:
 *   node src/parser/cli.js --input data/imports/lesson.html [--output data/json/] [--provider test-english] [--lessonId L001] [--url https://...]
 *
 * Workflow:
 *   1. Reads HTML from --input
 *   2. Detects or uses specified --provider
 *   3. Parses HTML → Universal Lesson JSON
 *   4. Shows Import Report
 *   5. Asks for confirmation
 *   6. Saves JSON to --output directory
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, join, basename, extname } from 'path';
import { createInterface } from 'readline';
import { getAdapter, detectProvider } from './index.js';
import { formatReport } from './BaseSourceAdapter.js';
import { validate, formatResult } from '../validation/index.js';

// ── Parse CLI args ────────────────────────────────────────────────────────

const args = process.argv.slice(2);

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
}

function hasFlag(flag) {
  return args.includes(flag);
}

const inputPath  = getArg('--input');
const outputDir  = getArg('--output') ?? 'data/json';
const provider   = getArg('--provider');
const lessonId   = getArg('--lessonId');
const url        = getArg('--url') ?? '';
const autoYes    = hasFlag('--yes') || hasFlag('-y');

if (!inputPath) {
  console.error('❌ Usage: node src/parser/cli.js --input <path/to/file.html> [--output data/json/]');
  process.exit(1);
}

// ── Main ─────────────────────────────────────────────────────────────────

async function main() {
  const absInput = resolve(inputPath);
  let html;

  try {
    html = readFileSync(absInput, 'utf-8');
  } catch (err) {
    console.error(`❌ Cannot read file: ${absInput}\n   ${err.message}`);
    process.exit(1);
  }

  // Detect provider
  const detectedProvider = provider ?? detectProvider(html);
  console.log(`\n📡 Provider: ${detectedProvider}`);

  // Get adapter and parse
  let adapter;
  try {
    adapter = getAdapter(detectedProvider);
  } catch (err) {
    console.error(`❌ ${err.message}`);
    process.exit(1);
  }

  const options = {
    url:      url || `file://${absInput}`,
    lessonId: lessonId ?? undefined,
  };

  let lesson, report;
  try {
    ({ lesson, report } = adapter.parse(html, options));
  } catch (err) {
    console.error(`❌ Parse error: ${err.message}`);
    if (process.env.DEBUG) console.error(err.stack);
    process.exit(1);
  }

  // ── Show Import Report ────────────────────────────────────────────────
  console.log('\n' + formatReport(report));

  if (report.errors.length > 0) {
    console.error('\n❌ Fatal errors during parsing — aborting.');
    process.exit(1);
  }

  // ── Validate ──────────────────────────────────────────────────────────
  const validation = validate(lesson);
  console.log('\n' + formatResult(validation));

  if (!validation.valid) {
    console.error('\n❌ Validation errors found — fix source or review warnings before proceeding.');
    if (!autoYes) process.exit(1);
  }

  // ── Confirm ───────────────────────────────────────────────────────────
  if (!autoYes) {
    const confirmed = await confirm(
      `\n❓ Proceed with import? (${lesson.exercises.length} exercises, ` +
      `${lesson.exercises.reduce((s, e) => s + e.questions.length, 0)} questions) [y/N]: `
    );
    if (!confirmed) {
      console.log('⏹  Import cancelled.');
      process.exit(0);
    }
  }

  // ── Save JSON ─────────────────────────────────────────────────────────
  const absOutputDir = resolve(outputDir);
  mkdirSync(absOutputDir, { recursive: true });

  const outputFilename = `${lesson.id}.json`;
  const outputPath = join(absOutputDir, outputFilename);

  writeFileSync(outputPath, JSON.stringify(lesson, null, 2), 'utf-8');

  console.log(`\n✅ Saved: ${outputPath}`);
  console.log(`   Lesson ID: ${lesson.id}`);
  console.log(`   Title:     ${lesson.title}`);
  console.log(`   Exercises: ${lesson.exercises.length}`);
  console.log(`   Questions: ${lesson.exercises.reduce((s, e) => s + e.questions.length, 0)}`);
}

function confirm(prompt) {
  return new Promise(resolve => {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    rl.question(prompt, answer => {
      rl.close();
      resolve(['y', 'yes'].includes(answer.trim().toLowerCase()));
    });
  });
}

main().catch(err => {
  console.error('❌ Unexpected error:', err.message);
  if (process.env.DEBUG) console.error(err.stack);
  process.exit(1);
});
