const fs = require('fs');
const path = require('path');
const dir = 'frontend/assets/data/lessons';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));

let totalGaps = 0;
let replacedGaps = 0;
let appendedGaps = 0;
let unhandledExamples = [];

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function replaceGapInText(text, gap, gapIdx, qId, exId) {
  let matched = false;
  const gapNum = gap.order || (gapIdx + 1);
  
  const patterns = [];
  if (gap.placeholder && gap.placeholder.trim()) {
    patterns.push(new RegExp(escapeRegex(gap.placeholder), 'i'));
  }
  patterns.push(new RegExp('\\{\\{\\s*gap' + gapNum + '\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\[\\s*gap' + gapNum + '\\s*\\]', 'i'));
  patterns.push(new RegExp('\\[\\s*' + gapNum + '\\s*\\]', 'i'));
  patterns.push(new RegExp('\\{\\{\\s*' + gapNum + '\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\{\\{\\s*gap\\s*\\}\\}', 'i'));
  patterns.push(new RegExp('\\[\\s*gap\\s*\\]', 'i'));
  patterns.push(/_{2,}/);
  patterns.push(/\{\{[^}]+\}\}/);

  for (const pat of patterns) {
    if (pat.test(text)) {
      text = text.replace(pat, '[[INPUT]]');
      matched = true;
      break;
    }
  }

  if (!matched) {
    text += ' [[INPUT]]';
  }
  return { text, matched };
}

for (const file of files) {
  const content = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  for (const ex of (content.exercises || [])) {
    const exId = ex.id || ex.exercise_id;
    for (const q of (ex.questions || [])) {
      const qId = q.id || q.question_id;
      if (q.gaps && q.gaps.length > 0) {
        let currentText = q.text || q.prompt || '';
        q.gaps.forEach((g, gIdx) => {
          totalGaps++;
          const res = replaceGapInText(currentText, g, gIdx, qId, exId);
          currentText = res.text;
          if (res.matched) {
            replacedGaps++;
          } else {
            appendedGaps++;
            if (unhandledExamples.length < 10) {
              unhandledExamples.push({ file, qId, qText: q.text, gap: g });
            }
          }
        });
      }
    }
  }
}

console.log('Total gaps processed:', totalGaps);
console.log('Replaced inline:', replacedGaps);
console.log('Appended (no placeholder found in text):', appendedGaps);
if (unhandledExamples.length > 0) {
  console.log('Unhandled examples:', JSON.stringify(unhandledExamples, null, 2));
}
