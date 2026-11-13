// Dauntless Forever - Dauntless 1.14.7 offline package
// Copyright (C) 2026 Addison2k. https://github.com/addison2k/DauntlessForever
// Licence: AGPL-3.0-only. Keep this notice: the licence requires it.
'use strict';
// Modded mode for 1.14.7: UE4SS (RE-UE4SS, MIT licence, https://github.com/UE4SS-RE/RE-UE4SS) for Lua/Blueprint mods, plus
// the Boss Health Bar that is built into this package's loader (bin\dxgi.dll).
// UE4SS lives in <game>\Archon\Binaries\Win64\ue4ss and is NOT loaded through its dwmapi.dll proxy (that would load it into
// your game AND every hidden server copy). The loader (dxgi.dll) loads it instead: in your game only when it was started
// with -dfmods, and in the servers only when the host turned on server mods (D1147_SERVER_MODS=1). The start scripts read
// data\mods.txt for that. The Boss Health Bar (D1147_CLIENT_BOSSBAR=1) works with or without UE4SS.
//   node ue4ss.cjs status                     -> JSON: installed, on, servers, mods [{name, on, builtin}]
//   node ue4ss.cjs install                    download UE4SS once (checked by SHA256) and put it in place
//   node ue4ss.cjs set <on|off|servers-on|servers-off>
//   node ue4ss.cjs mod <name> <on|off>        tick a mod in ue4ss\Mods\mods.txt ("Boss Health Bar": data\mods.txt)
//   node ue4ss.cjs prepare                    before a start: consoles hidden (Ctrl+O shows UE4SS's window), and an old
//                                             dwmapi.dll proxy moved aside
// Everything answers one line of JSON. Mods are never deleted by this script.
const fs = require('fs'), path = require('path'), crypto = require('crypto'), https = require('https'), os = require('os');
const { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const DATA = path.join(ROOT, 'data');
const MODE_FILE = path.join(DATA, 'mods.txt');
const RELEASE = {
  version: 'v3.0.1',
  url: 'https://github.com/UE4SS-RE/RE-UE4SS/releases/download/v3.0.1/UE4SS_v3.0.1.zip',
  sha256: '4b47d4bceddd2f561a4e395bfa00924ccfc945af576a2d0c613e6537846c57ec',
};
// Mods that come with UE4SS itself (tools for modders, not gameplay)
const BUILTIN = new Set(['ActorDumperMod', 'BPML_GenericFunctions', 'BPModLoaderMod', 'CheatManagerEnablerMod', 'ConsoleCommandsMod',
  'ConsoleEnablerMod', 'Keybinds', 'LineTraceMod', 'SplitScreenMod', 'jsbLuaProfilerMod']);

const out = (o) => { process.stdout.write(JSON.stringify(o)); };
const fail = (error) => { out({ ok: false, error }); process.exit(0); };
const sha = (f) => { try { return crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'); } catch { return null; } };

function gameDir() {
  try { return JSON.parse(fs.readFileSync(path.join(ROOT, 'config.json'), 'utf8').replace(/^\uFEFF/, '')).GameDir || null; } catch {
    try {
      const local = process.env.LOCALAPPDATA;
      if (local) {
        const c = JSON.parse(fs.readFileSync(path.join(local, 'DauntlessForever', 'versions', '1.14.7', 'config.json'), 'utf8'));
        if (c && c.GameDir) return c.GameDir;
      }
    } catch {}
    return null;
  }
}
function places() {
  const g = gameDir(); if (!g) fail('The game folder is not known yet. Run Set up first.');
  const win64 = path.join(g, 'Archon', 'Binaries', 'Win64');
  if (!fs.existsSync(path.join(win64, 'Dauntless-Win64-Shipping.exe'))) fail('The game was not found in ' + g + '. Run Set up again.');
  const dir = path.join(win64, 'ue4ss');
  return { win64, dir, dll: path.join(dir, 'UE4SS.dll'), ini: path.join(dir, 'UE4SS-settings.ini'), mods: path.join(dir, 'Mods'), list: path.join(dir, 'Mods', 'mods.txt') };
}
function mode() {
  const m = { on: false, servers: false, bossbar: true, trialsretry: false };
  try {
    for (const l of fs.readFileSync(MODE_FILE, 'utf8').split(/\r?\n/)) {
      const t = l.trim().toLowerCase();
      if (t === 'mods=on') m.on = true;
      if (t === 'servers=on') m.servers = true;
      if (t === 'bossbar=off') m.bossbar = false;
      if (t === 'trialsretry=on') m.trialsretry = true;   // DF-WARM-1147: spare trial server (tools\server-1147.ps1)
    }
  } catch {}
  return m;
}
function writeMode(m) {
  fs.mkdirSync(DATA, { recursive: true });
  fs.writeFileSync(MODE_FILE, '# Modded mode (launcher, 1.14.7 page). mods=on loads UE4SS in your game; servers=on also in your servers;\r\n' +
    '# bossbar=on shows the Boss Health Bar (part of Modded mode).\r\n' +
    '# trialsretry=on keeps a spare trial server warm so Retry is instant (works without UE4SS; needs 4 GB of free RAM).\r\n' +
    `mods=${m.on ? 'on' : 'off'}\r\nservers=${m.servers ? 'on' : 'off'}\r\nbossbar=${m.bossbar ? 'on' : 'off'}\r\ntrialsretry=${m.trialsretry ? 'on' : 'off'}\r\n`);
}
// ue4ss\Mods\mods.txt: "Name : 1" lines. Keybinds must stay last (UE4SS's own rule), so new lines go above it.
function readList(p) {
  const lines = fs.existsSync(p.list) ? fs.readFileSync(p.list, 'utf8').split(/\r?\n/) : [];
  const on = new Map();
  for (const l of lines) { const m = /^\s*([^:;#]+?)\s*:\s*([01])\s*$/.exec(l); if (m) on.set(m[1], m[2] === '1'); }
  return { lines, on };
}
function setListEntry(p, name, value) {
  const { lines } = readList(p);
  const re = new RegExp('^\\s*' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*:\\s*[01]\\s*$');
  const i = lines.findIndex((l) => re.test(l));
  if (i >= 0) lines[i] = `${name} : ${value ? 1 : 0}`;
  else {
    const k = lines.findIndex((l) => /^\s*Keybinds\s*:/.test(l));
    const at = k >= 0 ? (k > 0 && /^\s*;/.test(lines[k - 1]) ? k - 1 : k) : lines.length;
    lines.splice(at, 0, `${name} : ${value ? 1 : 0}`);
  }
  while (lines.length && lines[lines.length - 1] === '') lines.pop();
  fs.writeFileSync(p.list, lines.join('\r\n') + '\r\n');
}
const BOSSBAR = 'Boss Health Bar';   // built into this package's loader, not a UE4SS mod
const TRIALS = 'Trials Quick Retry';   // DF-WARM-1147: a spare trial server, in tools\server-1147.ps1; no UE4SS needed
const GAUNTLET3 = 'GauntletThreeBehemoths';
const GAUNTLET_PAK = 'zzzzzzzzzzzzzzzz_GauntletThreeBehemoths_P.pak';
const GAUNTLET_CFG_FILE = path.join(DATA, 'gauntlet.json');
const GAUNTLET_MODIFIERS = [
  { id: 'HM_PUSHANDPULL', name: 'Push and Pull', desc: 'Gravitational shockwaves pulse across the arena floor', seasons: [3] },
  { id: 'HM_FAST_ATTACKS', name: 'Fast Attacks', desc: 'Accelerated Behemoth attack and recovery speed', seasons: [2] },
  { id: 'HM_ELECTRIFY', name: 'Electrify', desc: 'Lightning orbs and shock auras periodically pulse', seasons: [1, 2, 3] },
  { id: 'HM_COMBUSTION', name: 'Combustion', desc: 'Fiery explosions erupt under Slayers or on impacts', seasons: [1, 2, 3] },
  { id: 'HM_ENVIRONMENT_DEEPFREEZE', name: 'Deep Freeze', desc: 'Severe Frostbite cold slows stamina recovery', seasons: [2] },
  { id: 'HM_FURY', name: 'Fury', desc: 'Behemoths enrage faster, stay enraged longer, hit harder', seasons: [2] },
  { id: 'HM_AFTERSHOCK', name: 'Aftershock', desc: 'Fissures erupt from the ground after slams', seasons: [2] },
  { id: 'HM_STONEHIDE', name: 'Stonehide', desc: 'Heavily reduced damage until armor plates break', seasons: [1, 2] },
  { id: 'HM_THICK_SKULL', name: 'Thick Skull', desc: 'Massive stagger and interrupt resistance', seasons: [2] },
  { id: 'HM_POISON_BLOOD', name: 'Poison Blood', desc: 'Corruption and poison hazard damage', seasons: [2] },
  { id: 'HM_LESS_NORMAL_MORE_EXPOSE', name: 'Weak Spot Surge', desc: 'Only wounded or broken parts take high damage', seasons: [1, 2] },
  { id: 'HM_MOMENTUM', name: 'Momentum', desc: 'Behemoths gain increased movement and charge speed', seasons: [1] },
  { id: 'HM_FRIGID_TOUCH', name: 'Frigid Touch', desc: 'Frost hazards build up on hits', seasons: [1, 2, 3] },
  { id: 'HM_ENTROPY', name: 'Entropy', desc: 'Aetheric anomalies drain Slayer stamina or health', seasons: [1, 2, 3] },
  { id: 'HM_ANEMIC', name: 'Anemic', desc: 'Healing effectiveness and potion power significantly reduced', seasons: [3] }
];

function getActiveSeasonNum() {
  try {
    const seasonFile = path.join(DATA, 'gauntlet_season.txt');
    if (fs.existsSync(seasonFile)) {
      const raw = fs.readFileSync(seasonFile, 'utf8').trim();
      const m = /([1-5])/.exec(raw);
      if (m) return Number(m[1]);
    }
  } catch {}
  return 5;
}

function unlockGauntletLevels(targetSeason) {
  try {
    const stateFile = path.join(DATA, 'state.json');
    if (!fs.existsSync(stateFile)) return false;
    const raw = fs.readFileSync(stateFile, 'utf8');
    const state = JSON.parse(raw.replace(/^\uFEFF/, ''));
    const players = state.players || {};
    let p = null;
    let epic = 'd211000000000000000000000000e91c';
    try {
      const m = /^\s*EpicAccountId\s*=\s*([0-9a-f]{32})\s*$/im.exec(fs.readFileSync(path.join(ROOT, 'eos', 'eos_offline.ini'), 'utf8'));
      if (m) epic = m[1];
    } catch {}
    const myKey = crypto.createHash('sha256').update('epic:' + epic).digest('hex').slice(0, 32);
    p = players[myKey] || players[state.lastPlayer];
    if (!p) {
      const keys = Object.keys(players);
      if (keys.length) p = players[keys[0]];
    }
    if (!p) return false;
    if (!p.mega1147) p.mega1147 = {};
    if (!p.mega1147.gauntlet1147) p.mega1147.gauntlet1147 = {};

    const targets = [];
    if (!targetSeason || targetSeason === 'all' || targetSeason === 0) {
      targets.push(1, 2, 3, 4, 5);
    } else {
      targets.push(Number(targetSeason));
    }

    const comp = [];
    for (let k = 1; k <= 100; k++) comp.push(k);

    for (const n of targets) {
      p.mega1147.gauntlet1147['gauntlet-season' + n] = { completed: comp.slice(), highest: 100 };
    }

    const tmp = stateFile + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(state, null, 2), 'utf8');
    JSON.parse(fs.readFileSync(tmp, 'utf8'));
    fs.renameSync(tmp, stateFile);
    return true;
  } catch {
    return false;
  }
}

function gauntletGet() {
  const def = {
    season: 3,
    allDualBehemothLevels: true,
    targetLevels: [5],
    behemothCount: 3,
    timeLimitSeconds: 0,
    modifiers: ['HM_PUSHANDPULL', 'HM_ELECTRIFY'],
    replaceExistingModifiers: true,
    unlockAllLevels: true
  };
  let cfg = def;
  try {
    if (fs.existsSync(GAUNTLET_CFG_FILE)) {
      cfg = Object.assign({}, def, JSON.parse(fs.readFileSync(GAUNTLET_CFG_FILE, 'utf8')));
    }
  } catch {}
  const activeSeason = getActiveSeasonNum();
  return { ok: true, config: cfg, activeSeason, seasons: [1, 2, 3, 4, 5], availableModifiers: GAUNTLET_MODIFIERS };
}

function gauntletLevelGet(season, level) {
  const patcher = path.join(ROOT, 'tools', 'gauntlet_patcher.py');
  try {
    const s = String(season || '3'), l = String(level || '1');
    const outStr = execFileSync('python', [patcher, 'inspect', s, l], { encoding: 'utf8', windowsHide: true });
    return JSON.parse(outStr.trim());
  } catch (e) {
    return { ok: false, error: 'Could not inspect level: ' + (e.message || String(e)) };
  }
}

function gauntletSet(raw) {
  let cfg;
  try {
    let s = String(raw || '').trim();
    if (s.startsWith('b64:')) s = Buffer.from(s.slice(4), 'base64').toString('utf8');
    cfg = JSON.parse(s);
  } catch (e) {
    try {
      const s = String(raw).replace(/([{,]\s*)([a-zA-Z0-9_]+)\s*:/g, '$1"$2":');
      cfg = JSON.parse(s);
    } catch {
      fail('Invalid JSON configuration.');
    }
  }
  fs.mkdirSync(DATA, { recursive: true });
  fs.writeFileSync(GAUNTLET_CFG_FILE, JSON.stringify(cfg, null, 2) + '\r\n');
  const sNum = Number(cfg.season);
  if (Number.isInteger(sNum) && sNum >= 1 && sNum <= 5) {
    try {
      const seasonFile = path.join(DATA, 'gauntlet_season.txt');
      fs.writeFileSync(seasonFile, String(sNum) + '\n', 'utf8');
    } catch {}
  }
  if (cfg.unlockAllLevels) {
    unlockGauntletLevels(cfg.season);
  }
  const patcher = path.join(ROOT, 'tools', 'gauntlet_patcher.py');
  try {
    execFileSync('python', [patcher, JSON.stringify(cfg)], { windowsHide: true });
  } catch (e) {
    fail('Could not generate custom pak: ' + (e.message || String(e)));
  }
  try {
    const p = places();
    const { on: modsOn } = readList(p);
    const gOn = modsOn.has(GAUNTLET3) ? modsOn.get(GAUNTLET3) : fs.existsSync(path.join(p.mods, GAUNTLET3, 'enabled.txt'));
    syncGauntletPak(gOn);
  } catch {}
  return { ok: true, message: 'Custom Gauntlet applied!', activeSeason: getActiveSeasonNum() };
}

function syncGauntletPak(isOn) {
  const g = gameDir(); if (!g) return;
  const paksDir = path.join(g, 'Archon', 'Content', 'Paks');
  const pak = path.join(paksDir, GAUNTLET_PAK);
  const pakOff = pak + '.off';
  const srcPak = path.join(ROOT, 'bin', GAUNTLET_PAK);
  try {
    if (isOn) {
      if (fs.existsSync(pakOff)) fs.renameSync(pakOff, pak);
      if (!fs.existsSync(srcPak)) {
        const patcher = path.join(ROOT, 'tools', 'gauntlet_patcher.py');
        if (fs.existsSync(patcher)) {
          try { execFileSync('python', [patcher], { windowsHide: true }); } catch {}
        }
      }
      if (fs.existsSync(srcPak)) fs.copyFileSync(srcPak, pak);
    } else {
      if (fs.existsSync(pak)) fs.renameSync(pak, pakOff);
    }
  } catch {}
}
function mods(p) {
  const m = mode();
  const boss = { name: BOSSBAR, on: m.bossbar, builtin: false, scripts: true, df: true,
    about: 'The behemoth\'s name and health at the top of the screen, with a bar for each of its parts below it. Play in borderless or windowed mode.',
    keys: [['Ctrl+Alt+Arrow keys', 'move the bar (while it shows)'], ['Ctrl+Alt+Home', 'put it back in the middle']] };   // the loader saves the position
  const trials = { name: TRIALS, on: m.trialsretry, builtin: false, scripts: true, df: true, noUe4ss: true, about: 'Retry in a trial is instant: a spare copy of the trial warms up while you play (host PC, about 4 GB of free RAM).' };
  return [boss, trials, ...ue4ssMods(p)];
}
function ue4ssMods(p) {
  if (!fs.existsSync(p.mods)) return [];
  const { on } = readList(p);
  return fs.readdirSync(p.mods, { withFileTypes: true })
    .filter((d) => d.isDirectory() && d.name !== 'shared')
    .map((d) => {
      // UE4SS also switches a mod on with an enabled.txt in its folder
      const flag = fs.existsSync(path.join(p.mods, d.name, 'enabled.txt'));
      const isG3 = d.name === GAUNTLET3;
      return { name: d.name, title: isG3 ? 'Gauntlet Customizer' : d.name, on: on.has(d.name) ? on.get(d.name) || flag : flag, builtin: BUILTIN.has(d.name),
        scripts: fs.existsSync(path.join(p.mods, d.name, 'Scripts')) || fs.existsSync(path.join(p.mods, d.name, 'dlls')),
        about: isG3 ? 'Customize Gauntlet Mode: spawn 1-4 Behemoths, select Seasons 1-5, adjust match timers, configure individual level rounds, and stack hunt modifiers.' : undefined,
        keys: isG3 ? [['F6', 'log active behemoths in UE4SS.log']] : undefined };
    })
    .sort((a, b) => (a.builtin - b.builtin) || a.name.localeCompare(b.name));
}
// [Debug] keys in UE4SS-settings.ini: no console windows; the GUI console stays available on its key (Ctrl+O by default).
function hideConsoles(p) {
  if (!fs.existsSync(p.ini)) return;
  const want = { ConsoleEnabled: '0', GuiConsoleEnabled: '1', GuiConsoleVisible: '0' };
  let text = fs.readFileSync(p.ini, 'utf8'), changed = false;
  for (const [k, v] of Object.entries(want)) {
    const re = new RegExp('^(\\s*' + k + '\\s*=\\s*)(\\S*)\\s*$', 'm');
    const m = re.exec(text);
    if (m) { if (m[2] !== v) { text = text.replace(re, `$1${v}`); changed = true; } }
    else if (/^\[Debug\]\s*$/m.test(text)) { text = text.replace(/^\[Debug\]\s*$/m, `[Debug]\r\n${k} = ${v}`); changed = true; }
  }
  if (changed) fs.writeFileSync(p.ini, text);
}
// An old manual install loads UE4SS through dwmapi.dll next to the exe, in every copy of the game. Moved aside (renamed,
// never deleted) the first time modded mode is used, and left there: Off means no UE4SS at all.
function proxyAside(p) {
  const d = path.join(p.win64, 'dwmapi.dll'), off = d + '.df-off';
  if (fs.existsSync(d)) { if (fs.existsSync(off)) fs.renameSync(off, off + '.' + Date.now()); fs.renameSync(d, off); return true; }
  return false;
}
function proxyBack(p) {
  const d = path.join(p.win64, 'dwmapi.dll'), off = d + '.df-off';
  if (fs.existsSync(off) && !fs.existsSync(d)) { fs.renameSync(off, d); return true; }
  return false;
}

// Mods that come with this package (package\mods\<name>, e.g. DamageMeter). Put into ue4ss\Mods when missing and
// switched on the first time; kept up to date while their df-bundled.txt is there (delete it to keep your own edits).
// Never removes anything.
function bundledMods(p) {
  const src = path.join(ROOT, 'mods'); if (!fs.existsSync(src) || !fs.existsSync(p.dir)) return [];
  const done = [];
  for (const d of fs.readdirSync(src, { withFileTypes: true })) {
    if (!d.isDirectory()) continue;
    const from = path.join(src, d.name), to = path.join(p.mods, d.name), isNew = !fs.existsSync(to);
    if (!isNew && !fs.existsSync(path.join(to, 'df-bundled.txt'))) continue;   // the player's own copy: left alone
    const copy = (a, b) => { fs.mkdirSync(b, { recursive: true }); for (const e of fs.readdirSync(a, { withFileTypes: true })) {
      const x = path.join(a, e.name), y = path.join(b, e.name);
      if (e.isDirectory()) copy(x, y); else if (sha(x) !== sha(y)) fs.copyFileSync(x, y); } };
    try { copy(from, to); if (isNew) { fs.mkdirSync(p.mods, { recursive: true }); if (!fs.existsSync(p.list)) fs.writeFileSync(p.list, ''); setListEntry(p, d.name, true); } done.push(d.name); } catch {}
  }
  return done;
}

function download(url, file, redirects = 5) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'DauntlessForever' }, timeout: 60000 }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && redirects > 0) { res.resume(); return resolve(download(new URL(res.headers.location, url).toString(), file, redirects - 1)); }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error('HTTP ' + res.statusCode)); }
      const part = file + '.part', w = fs.createWriteStream(part);
      res.pipe(w); w.on('finish', () => w.close(() => { fs.renameSync(part, file); resolve(file); })); w.on('error', reject);
    }).on('error', reject).on('timeout', function () { this.destroy(new Error('timed out')); });
  });
}
function copyMissing(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const e of fs.readdirSync(from, { withFileTypes: true })) {
    const a = path.join(from, e.name), b = path.join(to, e.name);
    if (e.isDirectory()) copyMissing(a, b);
    else if (!fs.existsSync(b)) fs.copyFileSync(a, b);
  }
}
async function install() {
  const p = places();
  if (fs.existsSync(p.dll)) { hideConsoles(p); bundledMods(p); return { ok: true, installed: true, already: true }; }
  const dl = path.join(DATA, 'downloads'); fs.mkdirSync(dl, { recursive: true });
  const zip = path.join(dl, 'UE4SS_' + RELEASE.version + '.zip');
  if (sha(zip) !== RELEASE.sha256) {
    try { await download(RELEASE.url, zip); } catch (e) { fail('Could not download UE4SS (' + e.message + '). Check your internet and try again.'); }
    if (sha(zip) !== RELEASE.sha256) { try { fs.rmSync(zip, { force: true }); } catch {} fail('The UE4SS download was damaged. Try again.'); }
  }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'df-ue4ss-'));
  try {
    execFileSync(process.platform === 'win32' ? 'tar.exe' : 'tar', ['-xf', zip, '-C', tmp], { windowsHide: true });
    fs.rmSync(path.join(tmp, 'dwmapi.dll'), { force: true });   // the proxy is never used (see the top of this file)
    copyMissing(tmp, p.dir);                                      // existing files (your mods, your mods.txt) stay as they are
  } catch (e) { fail('Could not unpack UE4SS: ' + e.message); }
  finally { try { fs.rmSync(tmp, { recursive: true, force: true }); } catch {} }
  hideConsoles(p);
  bundledMods(p);
  return { ok: true, installed: fs.existsSync(p.dll), version: RELEASE.version };
}

(async () => {
  const [cmd, a, b] = process.argv.slice(2);
  if (cmd === 'status') {
    const p = places(), m = mode();
    return out({ ok: true, installed: fs.existsSync(p.dll), on: m.on, servers: m.servers, folder: p.mods, mods: mods(p) });
  }
  if (cmd === 'gauntlet-get') return out(gauntletGet());
  if (cmd === 'gauntlet-level-get') return out(gauntletLevelGet(a, b));
  if (cmd === 'gauntlet-set') return out(gauntletSet(process.argv.slice(3).join(' ')));
  if (cmd === 'gauntlet-unlock-all') return out({ ok: unlockGauntletLevels('all'), message: 'All 5 seasons unlocked to Level 100!' });
  if (cmd === 'install') return out(await install());
  if (cmd === 'set') {
    const m = mode();
    if (a === 'on') m.on = true; else if (a === 'off') m.on = false;
    else if (a === 'servers-on') m.servers = true; else if (a === 'servers-off') m.servers = false;
    else fail('Use set on|off|servers-on|servers-off');
    writeMode(m);
    // Off does NOT put an old dwmapi.dll proxy back: that would load UE4SS into the game and every server copy again
    return out({ ok: true, on: m.on, servers: m.servers });
  }
  if (cmd === 'mod' && a === TRIALS) {
    if (b !== 'on' && b !== 'off') fail('Use mod <name> on|off');
    const m = mode(); m.trialsretry = b === 'on'; writeMode(m);
    return out({ ok: true, mods: mods(places()) });
  }
  if (cmd === 'mod' && a === BOSSBAR) {
    if (b !== 'on' && b !== 'off') fail('Use mod <name> on|off');
    const m = mode(); m.bossbar = b === 'on'; writeMode(m);
    return out({ ok: true, mods: mods(places()) });
  }
  if (cmd === 'mod') {
    const p = places();
    if (!a || !/^[\w .-]{1,80}$/.test(a) || a === 'shared' || !fs.existsSync(path.join(p.mods, a))) fail('Unknown mod.');
    if (b !== 'on' && b !== 'off') fail('Use mod <name> on|off');
    setListEntry(p, a, b === 'on');
    const flag = path.join(p.mods, a, 'enabled.txt');   // enabled.txt would keep it on regardless of mods.txt
    if (b === 'off' && fs.existsSync(flag)) fs.renameSync(flag, flag + '.off');
    if (a === GAUNTLET3) syncGauntletPak(b === 'on');
    return out({ ok: true, mods: mods(p) });
  }
  if (cmd === 'prepare') {
    const m = mode(); if (!m.on) return out({ ok: true, on: false });
    const p = places();
    const moved = proxyAside(p);
    if (!fs.existsSync(p.dll)) return out({ ok: false, on: true, bossbar: m.bossbar, ue4ss: false, error: 'UE4SS is not installed (launcher: Mods > Get UE4SS).' });
    hideConsoles(p);
    bundledMods(p);
    const { on: modsOn } = readList(p);
    const gOn = modsOn.has(GAUNTLET3) ? modsOn.get(GAUNTLET3) : fs.existsSync(path.join(p.mods, GAUNTLET3, 'enabled.txt'));
    syncGauntletPak(gOn);
    return out({ ok: true, on: true, servers: m.servers, bossbar: m.bossbar, ue4ss: true, movedProxy: moved });
  }
  fail('Use status | install | set | mod | prepare');
})().catch((e) => fail(String(e && e.message || e)));
