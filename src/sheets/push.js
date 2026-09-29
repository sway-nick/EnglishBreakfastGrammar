#!/usr/bin/env node
/**
 * Sheets Push CLI
 * Usage: node src/sheets/push.js --input data/json/L001.json
 */

import { readFileSync } from 'fs';
import { resolve } from 'path';
import 'dotenv/config';
import { pushLesson } from './index.js';

const args = process.argv.slice(2);
function getArg(f) { const i = args.indexOf(f); return i !== -1 ? args[i+1] : null; }

const inputPath     = getArg('--input');
const spreadsheetId = getArg('--spreadsheet') ?? process.env.GOOGLE_SHEETS_SPREADSHEET_ID;
const keyPath       = getArg('--key') ?? process.env.GOOGLE_SERVICE_ACCOUNT_KEY_PATH ?? './credentials/service-account.json';

if (!inputPath) {
  console.error('❌ Usage: node src/sheets/push.js --input data/json/L001.json');
  process.exit(1);
}
if (!spreadsheetId) {
  console.error('❌ GOOGLE_SHEETS_SPREADSHEET_ID is not set. Add it to .env or pass --spreadsheet <id>');
  process.exit(1);
}

const lesson = JSON.parse(readFileSync(resolve(inputPath), 'utf-8'));
console.log(`\n📤 Pushing "${lesson.title}" (${lesson.id}) to Google Sheets...`);

try {
  await pushLesson({ lesson, spreadsheetId, keyPath });
  console.log('\n✅ Done! Open your spreadsheet:');
  console.log(`   https://docs.google.com/spreadsheets/d/${spreadsheetId}`);
} catch (err) {
  console.error('\n❌ Sheets push failed:', err.message);
  if (process.env.DEBUG) console.error(err.stack);
  process.exit(1);
}
