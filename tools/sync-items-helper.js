// Dauntless Forever - sync items.js and modes1147.js to LocalAppData and update manifest hashes
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function updateManifest(versionDir, relFile) {
  const manifestPath = path.join(versionDir, '.package-files.json');
  if (!fs.existsSync(manifestPath)) return;
  const targetFile = path.join(versionDir, relFile);
  if (!fs.existsSync(targetFile)) return;
  const content = fs.readFileSync(targetFile);
  const hash = crypto.createHash('sha256').update(content).digest('hex').toUpperCase();
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const normKey = relFile.replace(/\\/g, '/');
  if (manifest.files && manifest.files[normKey]) {
    manifest.files[normKey] = { size: content.length, sha256: hash };
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 1), 'utf8');
    console.log('Updated manifest in', manifestPath, 'for', normKey, 'new hash:', hash);
  }
}

const appData = process.env.LOCALAPPDATA;
if (appData) {
  for (const ver of ['1.14.7', '1.6.2']) {
    const dstDir = path.join(appData, 'DauntlessForever', 'versions', ver);
    if (!fs.existsSync(dstDir)) continue;

    const files = ['tools/items.js'];
    if (ver === '1.14.7') files.push('backend/modes1147.js');

    for (const rel of files) {
      const src = path.join(__dirname, '..', 'resources', 'versions', ver, 'package', rel);
      const dst = path.join(dstDir, rel);
      if (fs.existsSync(src)) {
        fs.mkdirSync(path.dirname(dst), { recursive: true });
        fs.copyFileSync(src, dst);
        console.log('Copied', src, '->', dst);
        updateManifest(dstDir, rel);
      }
    }
  }
}
