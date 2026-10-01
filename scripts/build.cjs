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

  // 2. Sync root-level web app files from frontend/ to root
  const rootFilesToSync = [
    'index.html',
    'app.js',
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

  // 3. Sync frontend components, services, assets to root for root-based hosting (e.g. GitHub Pages)
  copyRecursiveSync(path.join(__dirname, '../frontend/components'), path.join(__dirname, '../components'));
  copyRecursiveSync(path.join(__dirname, '../frontend/services'), path.join(__dirname, '../services'));
  copyRecursiveSync(path.join(__dirname, '../frontend/assets'), path.join(__dirname, '../assets'));

  console.log('✅ Build successful! Single source of truth (frontend/) synchronized to root and assets.');
}

build();
