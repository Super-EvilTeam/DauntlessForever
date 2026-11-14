// ==========================================================================
// Gauntlet Customizer Client Application
// ==========================================================================

let activeConfig = null;
let currentSeason = 3;
let currentLevel = 5;
let currentRound = 0;
let availableModifiers = [];
let availableSpecies = [];
let levelCache = {}; // levelNum -> inspected/edited level data

// DOM Elements
const selSeason = document.getElementById('sel-season');
const modeGlobalBtn = document.getElementById('mode-global-btn');
const modeSpecBtn = document.getElementById('mode-spec-btn');
const panelGlobal = document.getElementById('panel-global');
const panelSpecific = document.getElementById('panel-specific');
const chkUnlockAll = document.getElementById('chk-unlock-all');
const selGlobalTimer = document.getElementById('sel-global-timer');
const globalModifiersGrid = document.getElementById('global-modifiers-grid');
const globalBehemothPills = document.getElementById('global-behemoth-pills');

const btnPrevLvl = document.getElementById('btn-prev-lvl');
const btnNextLvl = document.getElementById('btn-next-lvl');
const inpLevelNum = document.getElementById('inp-level-num');
const selSpecTimer = document.getElementById('sel-spec-timer');
const inpBehemothLvl = document.getElementById('inp-behemoth-lvl');
const roundTabs = document.getElementById('round-tabs');
const selRoundArena = document.getElementById('sel-round-arena');
const roundBehemothPills = document.getElementById('round-behemoth-pills');
const behemothSlotsGrid = document.getElementById('behemoth-slots-grid');
const roundModifiersGrid = document.getElementById('round-modifiers-grid');

const btnSaveApply = document.getElementById('btn-save-apply');
const btnRandomSeason = document.getElementById('btn-random-season');
const modalRandom = document.getElementById('modal-random');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const btnGenerateModal = document.getElementById('btn-generate-modal');
const toastEl = document.getElementById('toast');

// --------------------------------------------------------------------------
// Initialization
// --------------------------------------------------------------------------
async function init() {
  try {
    const res = await fetch('/api/config');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Failed to load config');

    activeConfig = data.config || {};
    availableModifiers = data.availableModifiers || [];
    currentSeason = Number(activeConfig.season) || 3;
    selSeason.value = String(currentSeason);
    chkUnlockAll.checked = activeConfig.unlockAllLevels !== false;

    // Set Global values
    if (activeConfig.allDualBehemothLevels === false) {
      setMode('specific');
    } else {
      setMode('global');
    }

    const bCount = activeConfig.behemothCount || 3;
    setGlobalPillCount(bCount);
    selGlobalTimer.value = String(activeConfig.timeLimitSeconds || 0);

    renderGlobalModifiers();
    setupEventListeners();

    if (activeConfig.allDualBehemothLevels === false) {
      await loadSpecificLevel(currentLevel);
    }
  } catch (err) {
    showToast('Error loading configuration: ' + err.message, true);
  }
}

// --------------------------------------------------------------------------
// Event Listeners
// --------------------------------------------------------------------------
function setupEventListeners() {
  // Season switch
  selSeason.addEventListener('change', async () => {
    currentSeason = Number(selSeason.value);
    levelCache = {};
    if (modeSpecBtn.classList.contains('active')) {
      await loadSpecificLevel(currentLevel);
    }
  });

  // Mode toggles
  modeGlobalBtn.addEventListener('click', () => setMode('global'));
  modeSpecBtn.addEventListener('click', () => setMode('specific'));

  // Global Behemoth count pills
  globalBehemothPills.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
      globalBehemothPills.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    });
  });

  // Level Navigation
  btnPrevLvl.addEventListener('click', () => navigateLevel(-1));
  btnNextLvl.addEventListener('click', () => navigateLevel(1));
  inpLevelNum.addEventListener('change', () => {
    let lvl = parseInt(inpLevelNum.value, 10);
    if (isNaN(lvl)) lvl = 1;
    lvl = Math.max(1, Math.min(1000, lvl));
    inpLevelNum.value = lvl;
    currentLevel = lvl;
    loadSpecificLevel(currentLevel);
  });

  // Round Tabs
  roundTabs.querySelectorAll('.round-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      roundTabs.querySelectorAll('.round-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentRound = parseInt(tab.dataset.round, 10);
      renderRoundEditor();
    });
  });

  // Round Behemoth count pills
  roundBehemothPills.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
      roundBehemothPills.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const count = parseInt(pill.dataset.count, 10);
      updateRoundBehemothCount(count);
    });
  });

  // Arena change
  selRoundArena.addEventListener('change', () => {
    const lvlData = levelCache[currentLevel];
    if (lvlData && lvlData.rounds && lvlData.rounds[currentRound]) {
      lvlData.rounds[currentRound].arena = selRoundArena.value;
    }
  });

  // Timer change
  selSpecTimer.addEventListener('change', () => {
    const lvlData = levelCache[currentLevel];
    if (lvlData) {
      lvlData.timeLimit = parseFloat(selSpecTimer.value);
    }
  });

  // Behemoth level change
  inpBehemothLvl.addEventListener('change', () => {
    const lvlData = levelCache[currentLevel];
    if (lvlData) {
      let val = parseInt(inpBehemothLvl.value, 10);
      if (isNaN(val)) val = 1;
      val = Math.max(1, Math.min(100, val));
      inpBehemothLvl.value = val;
      lvlData.behemothLevel = val;
    }
  });

  // Random season modal
  btnRandomSeason.addEventListener('click', () => modalRandom.style.display = 'flex');
  btnCloseModal.addEventListener('click', () => modalRandom.style.display = 'none');
  btnCancelModal.addEventListener('click', () => modalRandom.style.display = 'none');
  btnGenerateModal.addEventListener('click', generateRandomSeason);

  // Save & Apply
  btnSaveApply.addEventListener('click', saveAndApply);
}

// --------------------------------------------------------------------------
// Mode Switching
// --------------------------------------------------------------------------
function setMode(mode) {
  if (mode === 'global') {
    modeGlobalBtn.classList.add('active');
    modeSpecBtn.classList.remove('active');
    panelGlobal.style.display = 'block';
    panelSpecific.style.display = 'none';
  } else {
    modeSpecBtn.classList.add('active');
    modeGlobalBtn.classList.remove('active');
    panelGlobal.style.display = 'none';
    panelSpecific.style.display = 'block';
    if (!levelCache[currentLevel]) {
      loadSpecificLevel(currentLevel);
    }
  }
}

function setGlobalPillCount(count) {
  globalBehemothPills.querySelectorAll('.pill').forEach(p => {
    p.classList.toggle('active', parseInt(p.dataset.count, 10) === count);
  });
}

// --------------------------------------------------------------------------
// Global Modifiers
// --------------------------------------------------------------------------
function renderGlobalModifiers() {
  globalModifiersGrid.innerHTML = '';
  const activeMods = activeConfig.modifiers || [];

  availableModifiers.forEach(mod => {
    const card = document.createElement('label');
    card.className = 'modifier-card' + (activeMods.includes(mod.id) ? ' active' : '');
    
    const chk = document.createElement('input');
    chk.type = 'checkbox';
    chk.value = mod.id;
    chk.checked = activeMods.includes(mod.id);
    chk.addEventListener('change', () => card.classList.toggle('active', chk.checked));

    const info = document.createElement('div');
    info.className = 'modifier-info';
    info.innerHTML = `<span class="modifier-name">${mod.name}</span><span class="modifier-desc">${mod.desc}</span>`;

    card.appendChild(chk);
    card.appendChild(info);
    globalModifiersGrid.appendChild(card);
  });
}

// --------------------------------------------------------------------------
// Specific Level Loading & Navigation
// --------------------------------------------------------------------------
async function navigateLevel(delta) {
  let next = currentLevel + delta;
  next = Math.max(1, Math.min(1000, next));
  if (next === currentLevel) return;
  currentLevel = next;
  inpLevelNum.value = currentLevel;
  await loadSpecificLevel(currentLevel);
}

async function loadSpecificLevel(levelNum) {
  if (levelCache[levelNum]) {
    renderLevelData(levelCache[levelNum]);
    return;
  }

  try {
    const res = await fetch(`/api/inspect?season=${currentSeason}&level=${levelNum}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Inspection failed');

    availableSpecies = data.species || [];
    levelCache[levelNum] = data;
    renderLevelData(data);
  } catch (err) {
    showToast('Failed to inspect level ' + levelNum + ': ' + err.message, true);
  }
}

function renderLevelData(data) {
  selSpecTimer.value = String(Math.round(data.timeLimit || 420));
  inpBehemothLvl.value = data.behemothLevel || 18;
  renderRoundEditor();
}

// --------------------------------------------------------------------------
// Round Editor
// --------------------------------------------------------------------------
function renderRoundEditor() {
  const lvlData = levelCache[currentLevel];
  if (!lvlData || !lvlData.rounds || !lvlData.rounds[currentRound]) return;

  const round = lvlData.rounds[currentRound];
  selRoundArena.value = round.arena || 'Plaza';

  // Density pills
  const count = (round.behemoths || []).length || 2;
  roundBehemothPills.querySelectorAll('.pill').forEach(p => {
    p.classList.toggle('active', parseInt(p.dataset.count, 10) === count);
  });

  renderBehemothSlots(round);
  renderRoundModifiers(round);
}

function renderBehemothSlots(round) {
  behemothSlotsGrid.innerHTML = '';
  const behemoths = round.behemoths || [];

  behemoths.forEach((bCode, idx) => {
    const slot = document.createElement('div');
    slot.className = 'behemoth-slot';

    const lbl = document.createElement('span');
    lbl.className = 'slot-label';
    lbl.textContent = `Behemoth Slot ${idx + 1}`;

    const sel = document.createElement('select');
    sel.className = 'form-control';
    availableSpecies.forEach(sp => {
      const opt = document.createElement('option');
      opt.value = sp.codename;
      opt.textContent = `${sp.name} (${sp.codename})`;
      if (sp.codename === bCode) opt.selected = true;
      sel.appendChild(opt);
    });

    sel.addEventListener('change', () => {
      round.behemoths[idx] = sel.value;
    });

    slot.appendChild(lbl);
    slot.appendChild(sel);
    behemothSlotsGrid.appendChild(slot);
  });
}

function updateRoundBehemothCount(count) {
  const lvlData = levelCache[currentLevel];
  if (!lvlData || !lvlData.rounds || !lvlData.rounds[currentRound]) return;

  const round = lvlData.rounds[currentRound];
  round.behemoths = round.behemoths || [];

  while (round.behemoths.length < count) {
    const fallback = availableSpecies.length ? availableSpecies[0].codename : 'crowbear_alpha';
    round.behemoths.push(fallback);
  }
  while (round.behemoths.length > count) {
    round.behemoths.pop();
  }

  renderBehemothSlots(round);
}

function renderRoundModifiers(round) {
  roundModifiersGrid.innerHTML = '';
  const activeMods = round.modifiers || [];

  availableModifiers.forEach(mod => {
    const card = document.createElement('label');
    card.className = 'modifier-card' + (activeMods.includes(mod.id) ? ' active' : '');

    const chk = document.createElement('input');
    chk.type = 'checkbox';
    chk.value = mod.id;
    chk.checked = activeMods.includes(mod.id);
    chk.addEventListener('change', () => {
      card.classList.toggle('active', chk.checked);
      if (chk.checked) {
        if (!round.modifiers.includes(mod.id)) round.modifiers.push(mod.id);
      } else {
        round.modifiers = round.modifiers.filter(m => m !== mod.id);
      }
    });

    const info = document.createElement('div');
    info.className = 'modifier-info';
    info.innerHTML = `<span class="modifier-name">${mod.name}</span><span class="modifier-desc">${mod.desc}</span>`;

    card.appendChild(chk);
    card.appendChild(info);
    roundModifiersGrid.appendChild(card);
  });
}

// --------------------------------------------------------------------------
// Procedural Season Randomizer
// --------------------------------------------------------------------------
async function generateRandomSeason() {
  btnGenerateModal.disabled = true;
  btnGenerateModal.textContent = 'Generating...';

  const theme = document.getElementById('rnd-theme').value;
  const levels = parseInt(document.getElementById('rnd-levels').value, 10);
  const bosses = document.getElementById('rnd-bosses').value;
  const density = document.getElementById('rnd-density').value;
  const scaling = document.getElementById('rnd-scaling').value;

  try {
    const res = await fetch('/api/random-season', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        season: currentSeason,
        options: { theme, levels, bosses, density, scaling }
      })
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Generation failed');

    // Populate cache with generated season levels
    levelCache = {};
    if (data.config && data.config.levelConfig) {
      Object.entries(data.config.levelConfig).forEach(([lvlNum, lvl]) => {
        levelCache[lvlNum] = {
          level: parseInt(lvlNum, 10),
          timeLimit: lvl.timeLimitSeconds,
          behemothLevel: lvl.behemothLevel,
          rounds: lvl.rounds
        };
      });
    }

    activeConfig = data.config;
    setMode('specific');
    modalRandom.style.display = 'none';
    currentLevel = 1;
    inpLevelNum.value = 1;
    loadSpecificLevel(1);

    showToast(`Successfully generated ${levels}-level custom season! Click Save & Apply to compile.`);
  } catch (err) {
    showToast('Failed to generate season: ' + err.message, true);
  } finally {
    btnGenerateModal.disabled = false;
    btnGenerateModal.textContent = '✨ Generate & Apply';
  }
}

// --------------------------------------------------------------------------
// Save & Apply
// --------------------------------------------------------------------------
async function saveAndApply() {
  btnSaveApply.disabled = true;
  btnSaveApply.textContent = 'Compiling...';

  const isGlobal = modeGlobalBtn.classList.contains('active');
  const payload = {
    season: currentSeason,
    allDualBehemothLevels: isGlobal,
    unlockAllLevels: chkUnlockAll.checked
  };

  if (isGlobal) {
    const activePill = globalBehemothPills.querySelector('.pill.active');
    payload.behemothCount = activePill ? parseInt(activePill.dataset.count, 10) : 3;
    payload.timeLimitSeconds = parseFloat(selGlobalTimer.value);
    payload.modifiers = Array.from(globalModifiersGrid.querySelectorAll('input:checked')).map(i => i.value);
    payload.replaceExistingModifiers = true;
  } else {
    payload.levelConfig = {};
    Object.entries(levelCache).forEach(([lvlNum, data]) => {
      payload.levelConfig[lvlNum] = {
        timeLimitSeconds: data.timeLimit,
        behemothLevel: data.behemothLevel,
        rounds: data.rounds
      };
    });
    payload.targetLevels = Object.keys(levelCache).map(Number);
  }

  try {
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (!result.ok) throw new Error(result.error || 'Compilation failed');

    showToast('Custom Gauntlet compiled & mounted! Ready for next hunt.');
  } catch (err) {
    showToast('Failed to save & compile: ' + err.message, true);
  } finally {
    btnSaveApply.disabled = false;
    btnSaveApply.textContent = '💾 Save & Apply';
  }
}

// --------------------------------------------------------------------------
// Toast Feedback
// --------------------------------------------------------------------------
function showToast(message, isError = false) {
  toastEl.textContent = message;
  toastEl.className = 'toast' + (isError ? ' error' : '');
  toastEl.style.display = 'block';
  setTimeout(() => {
    toastEl.style.display = 'none';
  }, 4000);
}

// Start
document.addEventListener('DOMContentLoaded', init);
