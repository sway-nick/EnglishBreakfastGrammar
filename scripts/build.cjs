const fs = require('fs');
const path = require('path');

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach((childItemName) => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    if (fs.existsSync(dest)) {
      const destStats = fs.statSync(dest);
      if (destStats.size === stats.size && Math.abs(destStats.mtimeMs - stats.mtimeMs) < 1000) {
        return;
      }
    }
    fs.copyFileSync(src, dest);
  }
}

function build() {
  console.log('📦 Building English Breakfast Grammar from frontend/ ...');

  // 1. Check data integrity in grammar_catalog.json
  const catalogPath = path.join(__dirname, '../frontend/assets/data/grammar_catalog.json');
  if (fs.existsSync(catalogPath)) {
    const rawCatalog = fs.readFileSync(catalogPath, 'utf8');
    const catalog = JSON.parse(rawCatalog);
    console.log(`🔍 Verified catalog: ${catalog.levels.length} levels, ${catalog.lessons.length} lessons.`);
  }

  // 2. Sync root-level web app files if needed
  const rootFilesToSync = [
    'index.html',
    'favicon.ico',
    'favicon.svg',
    'manifest.json',
    'sw.js'
  ];

  rootFilesToSync.forEach((filename) => {
    const srcFile = path.join(__dirname, '../frontend', filename);
    if (fs.existsSync(srcFile)) {
      fs.copyFileSync(srcFile, path.join(__dirname, '../', filename));
    }
  });

  console.log('✅ Build successful! Frontend assets ready.');
}

build();
