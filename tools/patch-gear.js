// Dauntless Forever - patch gear catalog tables
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const REPLACEMENTS = {
  // GLITTER -> Chronovore
  'WP_AC_GLITTER': 'Chaos & Entropy (Chronovore)',
  'WP_GA_GLITTER': 'Existential Crisis (Chronovore)',
  'WP_CB_GLITTER': 'The Weeping Hours (Chronovore)',
  'WP_IH_GLITTER': "History's Burden (Chronovore)",
  'WP_DP_GLITTER': 'Temporal Mechanics (Chronovore)',
  'WP_EB_GLITTER': 'Edge of Tomorrow (Chronovore)',
  'WP_MS_GLITTER': "Millennium's End (Chronovore)",
  'AR_GLITTER_ARMS': 'Chronogrips (Chronovore)',
  'AR_GLITTER_CHEST': 'Chronoplate (Chronovore)',
  'AR_GLITTER_HELM': 'Chronohelm (Chronovore)',
  'AR_GLITTER_LEGS': 'Chronotreads (Chronovore)',
  'AR_GLITTER_ARMS_00_ULTRA': 'Chronovore Ultra Arms',
  'AR_GLITTER_CHEST_00_ULTRA': 'Chronovore Ultra Chest',
  'AR_GLITTER_HELM_00_ULTRA': 'Chronovore Ultra Helm',
  'AR_GLITTER_LEGS_00_ULTRA': 'Chronovore Ultra Legs',
  'LT_GLITTER_00': 'Chronovore Lantern',
  'AC_HEAD_GLITTER_00': 'Headpiece: Chronovore 00',
  'TITLE_GLITTER_00': 'Title: Chronovore',
  'BNC_FABRIC_GLITTER_00': 'Fabric: Chronovore 00',
  'BNC_SIGIL_GLITTER_00': 'Sigil: Chronovore 00',
  'BNC_STANDARD_GLITTER_00': 'Standard: Chronovore 00',

  // MINT -> Urska
  'WP_AC_MINT': 'Ice Breakers (Urska)',
  'WP_GA_MINT': 'Permanent Frost (Urska)',
  'WP_CB_MINT': "Blizzard's Teeth (Urska)",
  'WP_IH_MINT': 'Bomb Cyclone (Urska)',
  'WP_DP_MINT': 'Cryo-Cannons (Urska)',
  'WP_EB_MINT': 'Hypothermica (Urska)',
  'WP_MS_MINT': 'Cold Hell (Urska)',
  'AR_MINT_ARMS': "Adversary's Wrath (Urska)",
  'AR_MINT_CHEST': "Adversary's Pride (Urska)",
  'AR_MINT_HELM': "Adversary's Guile (Urska)",
  'AR_MINT_LEGS': "Adversary's Drive (Urska)",
  'AR_MINT_ARMS_00_ULTRA': 'Urska Ultra Arms',
  'AR_MINT_CHEST_00_ULTRA': 'Urska Ultra Chest',
  'AR_MINT_HELM_00_ULTRA': 'Urska Ultra Helm',
  'AR_MINT_LEGS_00_ULTRA': 'Urska Ultra Legs',
  'LT_MINT_00': 'Urska Lantern',
  'AC_HEAD_MINT_00': 'Headpiece: Urska 00',
  'WP_EB_MINT_01': 'Hypothermica Skin (Urska)',
  'BNC_FABRIC_MINT': 'Fabric: Urska',
  'BNC_SIGIL_MINT': 'Sigil: Urska',
  'BNC_STANDARD_MINT_00': 'Standard: Urska 00',
  'QI_FLARE_MINT_00': 'Flare: Urska 00',

  // THUNDERBIRD -> Malkarion
  'WP_EB_THUNDERBIRD': 'Cyclonic Fury (Malkarion)',
  'WP_CB_THUNDERBIRD': 'Electric Cruelties (Malkarion)',
  'WP_IH_THUNDERBIRD': 'Galvanic Impact (Malkarion)',
  'WP_AC_THUNDERBIRD': 'Mistral Currents (Malkarion)',
  'WP_DP_THUNDERBIRD': 'Dynamic Deadlights (Malkarion)',
  'WP_GA_THUNDERBIRD': 'Terminal Voltage (Malkarion)',
  'WP_MS_THUNDERBIRD': 'The Conductor (Malkarion)',
  'AR_THUNDERBIRD_CHEST_ULTRA': 'Malevolent Heart (Malkarion Ultra Chest)',
  'AR_THUNDERBIRD_ARMS_ULTRA': 'Malevolent Reach (Malkarion Ultra Arms)',
  'AR_THUNDERBIRD_HELM_ULTRA': 'Malevolent Vision (Malkarion Ultra Helm)',
  'AR_THUNDERBIRD_LEGS_ULTRA': 'Malevolent Wings (Malkarion Ultra Legs)',

  // Other mislabeled legendaries
  'WP_DP_RANDALL': 'Eldritch Torments (Thrax)',
  'WP_DP_ARMSTRONG': 'Volcanic Eruptions (Torgadoro)',
  'WP_DP_FUNGUY': 'Tainted Needles (Agarus)'
};

function formatGear(data) {
  if (Array.isArray(data)) {
    return '[' + data.map(i => JSON.stringify(i)).join(',') + ']';
  } else {
    const lines = [];
    lines.push('{"_comment": ' + JSON.stringify(data._comment) + ',');
    lines.push('"types": ' + JSON.stringify(data.types) + ',');
    lines.push('"items": [');
    lines.push(data.items.map(i => JSON.stringify(i)).join(',\n'));
    lines.push(']}');
    return lines.join('\n');
  }
}

function updateFile(file) {
  if (!fs.existsSync(file)) { console.log('File not found:', file); return; }
  const raw = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
  const data = JSON.parse(raw);
  const items = Array.isArray(data) ? data : data.items;
  let count = 0;
  for (const item of items) {
    if (REPLACEMENTS[item[0]]) {
      item[1] = REPLACEMENTS[item[0]];
      count++;
    }
  }
  const formatted = formatGear(data);
  fs.writeFileSync(file, formatted, 'utf8');
  console.log('Updated', file, 'items changed:', count);
}

function updateManifest(versionDir, relFile) {
  const manifestPath = path.join(versionDir, '.package-files.json');
  if (!fs.existsSync(manifestPath)) return;
  const targetFile = path.join(versionDir, relFile);
  if (!fs.existsSync(targetFile)) return;
  const content = fs.readFileSync(targetFile);
  const hash = crypto.createHash('sha256').update(content).digest('hex').toUpperCase();
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  if (manifest.files && manifest.files[relFile]) {
    manifest.files[relFile] = { size: content.length, sha256: hash };
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 1), 'utf8');
    console.log('Updated manifest in', manifestPath, 'for', relFile, 'new hash:', hash);
  }
}

// 1. Update repository files
updateFile(path.join(__dirname, '..', 'resources', 'versions', '1.14.7', 'package', 'tools', 'gear-1147.json'));
updateFile(path.join(__dirname, '..', 'resources', 'versions', '1.6.2', 'package', 'tools', 'gear-162.json'));

// 2. Update LocalAppData files and manifests
const appData = process.env.LOCALAPPDATA;
if (appData) {
  const dir1147 = path.join(appData, 'DauntlessForever', 'versions', '1.14.7');
  const dir162 = path.join(appData, 'DauntlessForever', 'versions', '1.6.2');

  updateFile(path.join(dir1147, 'tools', 'gear-1147.json'));
  updateManifest(dir1147, 'tools/gear-1147.json');

  updateFile(path.join(dir162, 'tools', 'gear-162.json'));
  updateManifest(dir162, 'tools/gear-162.json');
}
