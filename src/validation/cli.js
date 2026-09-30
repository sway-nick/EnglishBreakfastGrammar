#!/usr/bin/env node
/**
 * CLI Validation Runner
 *
 * Runs strict (or draft) validation on a Universal Lesson JSON file.
 * Usage:
 *   node src/validation/cli.js [--input path/to/universal_lessons.json] [--allow-unresolved]
 */

import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import { validate, formatResult, Severity } from './index.js';

function parseArgs(args) {
  let inputPath = 'data/cms/universal_lessons_final_enriched.json';
  let allowUnresolved = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' || args[i] === '-i') {
      inputPath = args[++i];
    } else if (args[i] === '--allow-unresolved') {
      allowUnresolved = true;
    }
  }

  return { inputPath, allowUnresolved };
}

function main() {
  const { inputPath, allowUnresolved } = parseArgs(process.argv.slice(2));
  const fullPath = resolve(inputPath);

  if (!existsSync(fullPath)) {
    console.error(`❌ Input file not found: ${fullPath}`);
    process.exit(1);
  }

  console.log(`[INFO] Validating JSON: ${fullPath}`);
  console.log(`[INFO] Mode: ${allowUnresolved ? 'ALLOW UNRESOLVED (Draft)' : 'STRICT (Production)'}`);

  const raw = readFileSync(fullPath, 'utf-8');
  let data;
  try {
    data = JSON.parse(raw);
  } catch (err) {
    console.error(`❌ JSON parse error: ${err.message}`);
    process.exit(1);
  }

  let lessons = [];
  if (Array.isArray(data)) {
    lessons = data;
  } else if (Array.isArray(data.lessons)) {
    lessons = data.lessons;
  } else if (data.id && (data.exercises || data.title)) {
    lessons = [data];
  } else {
    console.error(`❌ Unrecognized JSON structure (no lessons array or lesson object found)`);
    process.exit(1);
  }

  console.log(`[INFO] Loaded ${lessons.length} lessons to validate.`);

  let totalErrors = 0;
  let totalWarnings = 0;
  let totalInfos = 0;
  let invalidLessons = 0;

  lessons.forEach((lesson, idx) => {
    const res = validate(lesson, { allowUnresolved });
    totalErrors += res.errors.length;
    totalWarnings += res.warnings.length;
    totalInfos += res.infos.length;

    if (!res.valid) {
      invalidLessons++;
      console.log(`\n❌ Lesson [${lesson.id || idx}] (${lesson.title || 'Untitled'}):`);
      console.log(formatResult(res));
    }
  });

  console.log('\n' + '='.repeat(60));
  console.log('UNIVERSAL LESSONS VALIDATION SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Lessons Validated: ${lessons.length}`);
  console.log(`Valid Lessons:           ${lessons.length - invalidLessons}`);
  console.log(`Invalid Lessons:         ${invalidLessons}`);
  console.log(`Total Errors:            ${totalErrors}`);
  console.log(`Total Warnings:          ${totalWarnings}`);
  console.log(`Total Infos:             ${totalInfos}`);
  console.log('='.repeat(60));

  if (totalErrors > 0) {
    console.log('\n❌ STRICT VALIDATION FAILED');
    process.exit(1);
  } else {
    console.log('\n✅ STRICT VALIDATION PASSED (0 ERRORS)');
    process.exit(0);
  }
}

main();
