/**
 * Preview Server
 *
 * Serves a local preview of a Universal Lesson JSON as an interactive test.
 * This is the Test Engine in its simplest form — it reads local JSON,
 * not Firebase, making it fast and useful for validation before publish.
 *
 * Usage:
 *   node src/preview/server.js --input data/json/L001.json [--port 3456]
 */

import { createServer } from 'http';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { renderPreviewHTML } from './renderer.js';

const args = process.argv.slice(2);
function getArg(f) { const i = args.indexOf(f); return i !== -1 ? args[i+1] : null; }

const inputPath = getArg('--input');
const port = parseInt(getArg('--port') ?? process.env.PREVIEW_PORT ?? '3456', 10);

if (!inputPath) {
  console.error('❌ Usage: node src/preview/server.js --input data/json/L001.json');
  process.exit(1);
}

const absInput = resolve(inputPath);
let lesson;

try {
  lesson = JSON.parse(readFileSync(absInput, 'utf-8'));
} catch (err) {
  console.error(`❌ Cannot read/parse JSON: ${absInput}\n   ${err.message}`);
  process.exit(1);
}

const server = createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(renderPreviewHTML(lesson));
});

server.listen(port, () => {
  const url = `http://localhost:${port}`;
  console.log(`\n🔍 Preview running: ${url}`);
  console.log(`   Lesson: ${lesson.title} (${lesson.id})`);
  console.log(`   Press Ctrl+C to stop\n`);

  // Auto-open in browser (optional)
  if (!process.env.NO_OPEN) {
    import('open').then(m => m.default(url)).catch(() => {});
  }
});
