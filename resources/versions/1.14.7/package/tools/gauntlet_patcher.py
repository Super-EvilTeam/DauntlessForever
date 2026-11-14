# SPDX-License-Identifier: AGPL-3.0-only
# Dauntless Forever - Dynamic Gauntlet Encounter Patcher
import struct, json, sys, os, shutil, tempfile, random
from pathlib import Path
import repak

ROOT = Path(__file__).resolve().parent.parent
BASE_ASSETS_DIR = ROOT / 'tools' / 'gauntlet_base_assets'
DATA_DIR = ROOT / 'data'
CONFIG_FILE = DATA_DIR / 'gauntlet.json'
OUT_PAK_FILE = ROOT / 'bin' / 'zzzzzzzzzzzzzzzz_GauntletThreeBehemoths_P.pak'

CANDIDATES = [
    'crowbear_alpha', 'rock_alpha', 'shadowcat_normal', 'fulgar_normal',
    'mcrollin_alpha', 'electroquill_alpha', 'beaver_frost', 'bullseye_alpha',
    'mantis_normal', 'terramane_alpha', 'lavaroller_alpha'
]

BEHEMOTH_NAMES = {
    'amber_normal': 'Alyra',
    'amber_heroic': 'Heroic Alyra',
    'armstrong_normal': 'Torgadoro',
    'armstrong_heroic': 'Heroic Torgadoro',
    'beaver_normal': 'Gnasher',
    'beaver_alpha': 'Ragetail Gnasher',
    'beaver_blaze': 'Flameborn Gnasher',
    'beaver_frost': 'Frostwisp Gnasher',
    'beaver_heroic': 'Heroic Gnasher',
    'bugbear_normal': 'Rezakiri',
    'bugbear_blaze': 'Flameborn Rezakiri',
    'bullseye_normal': 'Quillshot',
    'bullseye_alpha': 'Deadeye Quillshot',
    'bullseye_blaze': 'Flameborn Quillshot',
    'bullseye_heroic': 'Heroic Quillshot',
    'crowbear_normal': 'Shrowd',
    'crowbear_alpha': 'Bloodshot Shrowd',
    'crowbear_heroic': 'Heroic Shrowd',
    'electroquill_normal': 'Nayzaga',
    'electroquill_alpha': 'Shockjaw Nayzaga',
    'electroquill_umbral': 'Shadowtouched Nayzaga',
    'electroquill_heroic': 'Heroic Nayzaga',
    'fulgar_normal': 'Drask',
    'fulgar_alpha': 'Thunderdeep Drask',
    'fulgar_umbral': 'Shadowtouched Drask',
    'fulgar_heroic': 'Heroic Drask',
    'funguy_normal': 'Agarus',
    'funguy_heroic': 'Heroic Agarus',
    'glitter_normal': 'Chronovore',
    'glitter_heroic': 'Heroic Chronovore',
    'habanero_normal': 'Phaelanx',
    'habanero_heroic': 'Heroic Phaelanx',
    'host_normal': 'Boreus',
    'host_alpha': 'Dreadfrost Boreus',
    'host_radiant': 'Lightbound Boreus',
    'host_heroic': 'Heroic Boreus',
    'lavaroller_normal': 'Hellion',
    'lavaroller_alpha': 'Scorchstone Hellion',
    'lavaroller_heroic': 'Heroic Hellion',
    'lerawr_normal': 'Embermane',
    'lerawr_alpha': 'Bloodfire Embermane',
    'lerawr_heroic': 'Heroic Embermane',
    'mantis_normal': 'Sahvyt',
    'mantis_heroic': 'Heroic Sahvyt',
    'mcrollin_normal': 'Pangar',
    'mcrollin_alpha': 'Frostback Pangar',
    'mcrollin_heroic': 'Heroic Pangar',
    'mint_normal': 'Urska',
    'mint_heroic': 'Heroic Urska',
    'moonface_normal': 'Shrike',
    'moonface_alpha': 'Moonreaver Shrike',
    'moonface_heroic': 'Heroic Shrike',
    'paper_normal': 'Koshai',
    'paper_radiant': 'Lightbound Koshai',
    'paper_umbral': 'Shadowtouched Koshai',
    'paper_heroic': 'Heroic Koshai',
    'randall_normal': 'Thrax',
    'randall_heroic': 'Heroic Thrax',
    'rock_normal': 'Skarn',
    'rock_alpha': 'Rockfall Skarn',
    'rock_frost': 'Deepfrost Skarn',
    'rock_heroic': 'Heroic Skarn',
    'sally_normal': 'Charrogg',
    'sally_alpha': 'Firebrand Charrogg',
    'sally_heroic': 'Heroic Charrogg',
    'salt_normal': 'Valomyr',
    'salt_heroic': 'Heroic Valomyr',
    'scissors_normal': 'Kharabak',
    'scissors_alpha': 'Razorwing Kharabak',
    'scissors_heroic': 'Heroic Kharabak',
    'shadowcat_normal': 'Riftstalker',
    'shadowcat_heroic': 'Heroic Riftstalker',
    'shockmane_normal': 'Stormclaw',
    'shockmane_alpha': 'Tempestborne Stormclaw',
    'shockmane_heroic': 'Heroic Stormclaw',
    'snowflake_normal': 'Skraev',
    'snowflake_alpha': 'Winterhorn Skraev',
    'snowflake_heroic': 'Heroic Winterhorn Skraev',
    'terramane_normal': 'Fenroar',
    'terramane_alpha': 'Sporestruck Fenroar',
    'terramane_heroic': 'Heroic Fenroar',
    'thunderbird_normal': 'Malkarion',
    'thunderbird_heroic': 'Heroic Malkarion',
    'wolf_normal': 'Frostwulf',
    'wolf_heroic': 'Heroic Frostwulf',
}

KEYSTONE_BEHEMOTHS = [
    'armstrong_normal', 'armstrong_heroic',
    'thunderbird_normal', 'thunderbird_heroic',
    'randall_normal', 'randall_heroic',
    'funguy_normal', 'funguy_heroic',
    'mint_normal', 'mint_heroic',
    'glitter_normal', 'glitter_heroic',
    'crowbear_alpha', 'habanero_normal'
]

THEME_BEHEMOTHS = {
    'frost': [
        'host_normal', 'host_alpha', 'host_heroic', 'mcrollin_normal', 'mcrollin_alpha',
        'mcrollin_heroic', 'snowflake_normal', 'snowflake_alpha', 'snowflake_heroic',
        'wolf_normal', 'wolf_heroic', 'mint_normal', 'mint_heroic', 'beaver_frost', 'rock_frost'
    ],
    'blaze': [
        'sally_normal', 'sally_alpha', 'sally_heroic', 'lerawr_normal', 'lerawr_alpha',
        'lerawr_heroic', 'lavaroller_normal', 'lavaroller_alpha', 'lavaroller_heroic',
        'armstrong_normal', 'armstrong_heroic', 'beaver_blaze', 'bugbear_blaze', 'bullseye_blaze',
        'habanero_normal', 'habanero_heroic'
    ],
    'shock': [
        'fulgar_normal', 'fulgar_alpha', 'fulgar_heroic', 'electroquill_normal', 'electroquill_alpha',
        'electroquill_heroic', 'shockmane_normal', 'shockmane_alpha', 'shockmane_heroic',
        'mantis_normal', 'mantis_heroic', 'thunderbird_normal', 'thunderbird_heroic'
    ],
    'terra': [
        'beaver_normal', 'beaver_alpha', 'beaver_heroic', 'rock_normal', 'rock_alpha',
        'rock_heroic', 'scissors_normal', 'scissors_alpha', 'scissors_heroic',
        'paper_normal', 'paper_heroic', 'terramane_normal', 'terramane_alpha', 'terramane_heroic',
        'funguy_normal', 'funguy_heroic', 'bullseye_normal', 'bullseye_alpha'
    ],
    'umbral': [
        'crowbear_normal', 'crowbear_alpha', 'crowbear_heroic', 'shadowcat_normal', 'shadowcat_heroic',
        'paper_umbral', 'electroquill_umbral', 'fulgar_umbral', 'randall_normal', 'randall_heroic'
    ],
    'radiant': [
        'salt_normal', 'salt_heroic', 'bugbear_normal', 'glitter_normal', 'glitter_heroic',
        'amber_normal', 'amber_heroic', 'paper_radiant', 'host_radiant'
    ],
    'keystones': KEYSTONE_BEHEMOTHS
}

THEME_MODIFIERS = {
    'frost': ['HM_ENVIRONMENT_DEEPFREEZE', 'HM_DRAIN_REVIVE', 'HM_STAMINA_DRAIN', 'HM_SLAYER_SPEED_REDUCED'],
    'blaze': ['HM_COMBUSTION', 'HM_SPEED_UP', 'HM_EXPLOSIVE_EXPLOSIONS'],
    'shock': ['HM_ELECTRIFY', 'HM_SPEED_UP'],
    'terra': ['HM_ARMOR_PLATES', 'HM_CRIT_WOUNDED', 'HM_REFLECT_DAMAGE'],
    'umbral': ['HM_PUSHANDPULL', 'HM_STAMINA_DRAIN', 'HM_DRAIN_REVIVE'],
    'radiant': ['HM_ELECTRIFY', 'HM_FAST_ATTACKS', 'HM_SPEED_UP'],
    'keystones': ['HM_PUSHANDPULL', 'HM_ELECTRIFY', 'HM_COMBUSTION', 'HM_ARMOR_PLATES', 'HM_SPEED_UP']
}

DEFAULT_CONFIG = {
    "enabled": True,
    "season": 3,
    "allDualBehemothLevels": True,
    "targetLevels": [5],
    "behemothCount": 3,
    "timeLimitSeconds": 0,
    "modifiers": ["HM_PUSHANDPULL", "HM_ELECTRIFY"],
    "replaceExistingModifiers": True
}

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except Exception as e:
            print(f"Error reading config: {e}")
    return DEFAULT_CONFIG.copy()

def r_name(buf, off, names):
    i, n = struct.unpack_from('<II', buf, off)
    return (names[i] + ('_' + str(n-1) if n else '')), off + 8

def parse_tag(buf, off, names):
    name, off = r_name(buf, off, names)
    if name == 'None': return {'name': 'None', 'tag_start': off-8}, off
    typ, off = r_name(buf, off, names)
    sz, idx = struct.unpack_from('<II', buf, off); off += 8
    info = {'name': name, 'type': typ, 'sz': sz, 'idx': idx, 'tag_start': off-24}
    if typ == 'StructProperty':
        sname, off = r_name(buf, off, names); info['struct'] = sname; off += 16
    elif typ == 'ByteProperty':
        btyp, off = r_name(buf, off, names); info['enum'] = btyp
    elif typ == 'EnumProperty':
        etyp, off = r_name(buf, off, names); info['enum_type'] = etyp
    elif typ == 'ArrayProperty':
        ityp, off = r_name(buf, off, names); info['item'] = ityp
    elif typ == 'MapProperty':
        ktyp, off = r_name(buf, off, names); vtyp, off = r_name(buf, off, names); info['map'] = (ktyp, vtyp)
    elif typ == 'BoolProperty':
        val = buf[off]; off += 2; info['val'] = val; return info, off
    off += 1
    info['raw_start'] = off
    info['raw'] = buf[off:off+sz]; off += sz
    return info, off

def get_uasset_names(u):
    name_count, name_offset = struct.unpack_from('<II', u, 41)
    pos = name_offset
    names = []
    for _ in range(name_count):
        length = struct.unpack_from('<i', u, pos)[0]
        pos += 4
        if length > 0:
            s = u[pos:pos+length-1].decode('utf-8', 'ignore')
            pos += length
        else:
            s = u[pos:pos+(-length)*2-2].decode('utf-16-le', 'ignore')
            pos += (-length) * 2
        pos += 4
        names.append(s)
    return names

def inspect_level(season_num, level_num):
    spec_map = {
        1: 'gauntlet_mode_encounter_specs',
        2: 'gauntlet_mode_encounter_specs_s2',
        3: 'gauntlet_mode_encounter_specs_s3',
        4: 'gauntlet_mode_encounter_specs_s4',
        5: 'gauntlet_mode_encounter_specs_s5'
    }
    s_idx = int(season_num) if str(season_num).isdigit() else 3
    spec_name = spec_map.get(s_idx, 'gauntlet_mode_encounter_specs_s3')
    uasset_path = BASE_ASSETS_DIR / f'{spec_name}.uasset'
    uexp_path = BASE_ASSETS_DIR / f'{spec_name}.uexp'
    if not uasset_path.exists() or not uexp_path.exists():
        return {'ok': False, 'error': f'Base asset {spec_name} not found.'}
        
    u_data = uasset_path.read_bytes()
    b_data = uexp_path.read_bytes()
    names = get_uasset_names(u_data)
    
    if 'GAUNTLET_S1_LEVEL' not in names:
        return {'ok': False, 'error': 'GAUNTLET_S1_LEVEL not found in asset names.'}
    l_idx = names.index('GAUNTLET_S1_LEVEL')
    
    lvl_num = int(level_num) if str(level_num).isdigit() else 1
    base_rows = struct.unpack_from('<I', b_data, 67)[0]
    target_lvl = lvl_num if (1 <= lvl_num <= base_rows) else (((lvl_num - 1) % base_rows) + 1)
    pos = -1
    o_cur = 71
    for r_idx in range(base_rows):
        cur_lvl = r_idx + 1
        if cur_lvl == target_lvl:
            pos = o_cur
            break
        rname, o_cur = r_name(b_data, o_cur, names)
        while o_cur < len(b_data):
            tag, o_cur = parse_tag(b_data, o_cur, names)
            if tag['name'] == 'None':
                break
    if pos == -1:
        return {'ok': False, 'error': f'Level {level_num} not found in Season {s_idx}.'}
        
    o = pos + 8
    time_limit = 420.0
    rounds = []
    behemoth_levels = []
    
    while o < len(b_data):
        tag, o = parse_tag(b_data, o, names)
        if tag['name'] == 'None': break
        if tag['name'] == 'TimeLimit':
            time_limit = struct.unpack_from('<f', tag['raw'], 0)[0]
        elif tag['name'] == 'RoundStructures':
            raw = tag['raw']
            num_rounds = struct.unpack_from('<I', raw, 0)[0]
            ro = 4
            _, ro = r_name(raw, ro, names); _, ro = r_name(raw, ro, names); ro += 8; _, ro = r_name(raw, ro, names); ro += 17
            for rnd in range(num_rounds):
                arena = 'EGauntletArena::Plaza'
                behemoths = []
                modifiers = []
                while ro < len(raw):
                    rtag, ro = parse_tag(raw, ro, names)
                    if rtag['name'] == 'None': break
                    if rtag['name'] == 'Arena':
                        a_idx, _ = struct.unpack_from('<II', rtag['raw'], 0)
                        if a_idx < len(names): arena = names[a_idx]
                    elif rtag['name'] == 'Content':
                        craw = rtag['raw']
                        cnum = struct.unpack_from('<I', craw, 0)[0]
                        co = 4
                        _, co = r_name(craw, co, names); _, co = r_name(craw, co, names); co += 8; _, co = r_name(craw, co, names); co += 17
                        for ci in range(cnum):
                            is_b = False
                            is_m = False
                            bn = None
                            mn = None
                            blvl = None
                            while co < len(craw):
                                ctag, co = parse_tag(craw, co, names)
                                if ctag['name'] == 'None': break
                                if ctag['name'] == 'ContentType':
                                    i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                    if i < len(names):
                                        if names[i] == 'EGauntletContentType::Behemoth': is_b = True
                                        elif names[i] == 'EGauntletContentType::Modifier': is_m = True
                                elif ctag['name'] == 'BehemothName':
                                    i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                    if i < len(names): bn = names[i]
                                elif ctag['name'] == 'BehemothLevel':
                                    blvl = struct.unpack_from('<i', ctag['raw'], 0)[0]
                                elif ctag['name'] == 'Modifier':
                                    mraw = ctag['raw']
                                    mo = 0
                                    while mo < len(mraw):
                                        mtag, mo = parse_tag(mraw, mo, names)
                                        if mtag['name'] == 'RowName':
                                            ri, _ = struct.unpack_from('<II', mtag['raw'], 0)
                                            if ri < len(names) and names[ri] != 'None':
                                                mn = names[ri]
                                        if mtag['name'] == 'None': break
                            if is_b and bn:
                                behemoths.append(bn)
                                if blvl is not None:
                                    behemoth_levels.append(blvl)
                            if is_m and mn:
                                modifiers.append(mn)
                rounds.append({
                    'round': rnd + 1,
                    'arena': arena,
                    'behemoths': behemoths,
                    'modifiers': modifiers
                })
                
    avg_b_lvl = int(round(sum(behemoth_levels) / len(behemoth_levels))) if behemoth_levels else 10
    try:
        cfg = load_config()
        lvl_cfg = cfg.get('levelConfig', {}).get(str(lvl_num))
        if lvl_cfg:
            if 'timeLimit' in lvl_cfg and float(lvl_cfg['timeLimit']) > 0:
                time_limit = float(lvl_cfg['timeLimit'])
            if 'behemothLevel' in lvl_cfg and int(lvl_cfg['behemothLevel']) > 0:
                avg_b_lvl = int(lvl_cfg['behemothLevel'])
    except Exception:
        pass
        
    avail_behemoths = []
    for bn, display in BEHEMOTH_NAMES.items():
        if bn in names:
            avail_behemoths.append({'id': bn, 'name': f"{display} ({bn})"})
    for n in names:
        if ('_normal' in n or '_alpha' in n or '_heroic' in n) and n not in BEHEMOTH_NAMES:
            clean = n.replace('_', ' ').title()
            avail_behemoths.append({'id': n, 'name': f"{clean} ({n})"})
    avail_behemoths.sort(key=lambda x: x['name'])
    
    return {
        'ok': True,
        'season': s_idx,
        'level': lvl_num,
        'timeLimit': time_limit,
        'behemothLevel': avg_b_lvl,
        'rounds': rounds,
        'catalog': {
            'arenas': [
                {'id': 'EGauntletArena::Plaza', 'name': 'Plaza'},
                {'id': 'EGauntletArena::Forge', 'name': 'Forge'},
                {'id': 'EGauntletArena::Hangar', 'name': 'Hangar'}
            ],
            'behemoths': avail_behemoths
        }
    }

def generate_random_season(season_num=3, options=None):
    if options is None:
        options = {}
    elif isinstance(options, str):
        s = options.strip()
        if s.startswith('b64:'):
            import base64
            try:
                s = base64.b64decode(s[4:]).decode('utf-8', 'ignore')
            except Exception:
                pass
        try:
            options = json.loads(s)
        except Exception:
            options = {}
            
    spec_map = {
        1: 'gauntlet_mode_encounter_specs',
        2: 'gauntlet_mode_encounter_specs_s2',
        3: 'gauntlet_mode_encounter_specs_s3',
        4: 'gauntlet_mode_encounter_specs_s4',
        5: 'gauntlet_mode_encounter_specs_s5'
    }
    s_idx = int(season_num) if str(season_num).isdigit() else 3
    if s_idx < 1 or s_idx > 5:
        s_idx = 3
        
    req_lvls = options.get('levelCount', 20)
    try:
        level_count = max(1, min(int(req_lvls), 1000))
    except Exception:
        level_count = 20
        
    theme = str(options.get('theme', 'all')).lower()
    density = str(options.get('density', 'progressive')).lower()
    modifier_intensity = str(options.get('modifierIntensity', 'progressive')).lower()
    boss_milestones = str(options.get('bossMilestones', 'every5')).lower()
    timer_mode = str(options.get('timerMode', 'default')).lower()
    b_lvl_mode = str(options.get('behemothLevelProgression', 'progressive')).lower()
    custom_b_lvl = 10
    try:
        custom_b_lvl = max(1, min(100, int(options.get('customBehemothLevel', 10))))
    except Exception:
        custom_b_lvl = 10
    
    spec_name = spec_map[s_idx]
    uasset_path = BASE_ASSETS_DIR / f'{spec_name}.uasset'
    if not uasset_path.exists():
        return {'ok': False, 'error': f'Base asset {spec_name} not found.'}
        
    names = get_uasset_names(uasset_path.read_bytes())
    avail_behemoths = [bn for bn in BEHEMOTH_NAMES if bn in names]
    if not avail_behemoths:
        avail_behemoths = [n for n in names if ('_normal' in n or '_alpha' in n or '_heroic' in n) and n != 'None']
    avail_modifiers = [n for n in names if n.startswith('HM_') and n != 'HM_TEST_SELF_REVIVE']
    
    theme_behemoths = []
    if theme in THEME_BEHEMOTHS:
        theme_behemoths = [bn for bn in THEME_BEHEMOTHS[theme] if bn in names]
        
    theme_modifiers = []
    if theme in THEME_MODIFIERS:
        theme_modifiers = [mn for mn in THEME_MODIFIERS[theme] if mn in names]
        
    keystone_pool = [bn for bn in KEYSTONE_BEHEMOTHS if bn in names]
    
    arenas = ['EGauntletArena::Plaza', 'EGauntletArena::Forge', 'EGauntletArena::Hangar']
    
    timer_seconds = 420.0
    if timer_mode == 'speedrun':
        timer_seconds = 180.0
    elif timer_mode == 'fast':
        timer_seconds = 300.0
    elif timer_mode == 'endurance':
        timer_seconds = 600.0
    elif timer_mode == 'marathon':
        timer_seconds = 900.0
    else:
        try:
            val = float(options.get('timerSeconds', timer_mode))
            if val > 0:
                timer_seconds = val
        except Exception:
            timer_seconds = 420.0
            
    level_cfg = {}
    for lvl in range(1, level_count + 1):
        rounds = []
        is_boss_level = False
        if boss_milestones == 'every5' and (lvl % 5 == 0):
            is_boss_level = True
        elif boss_milestones == 'every10' and (lvl % 10 == 0):
            is_boss_level = True
            
        for rnd in range(1, 6):
            arena = random.choice(arenas)
            
            # Determine behemoth count
            if density == 'solo':
                b_count = 1
            elif density == 'duo':
                b_count = 2
            elif density == 'trio':
                b_count = 3
            elif density == 'chaos':
                b_count = random.choices([2, 3, 4], weights=[0.1, 0.45, 0.45])[0]
            elif density == 'varied':
                b_count = random.choice([1, 2, 3, 4])
            else: # progressive across 100 levels
                if lvl <= 4:
                    weights = [0.65, 0.35, 0.0, 0.0]
                elif lvl <= 10:
                    weights = [0.25, 0.60, 0.15, 0.0]
                elif lvl <= 20:
                    weights = [0.05, 0.45, 0.40, 0.10]
                elif lvl <= 35:
                    weights = [0.0, 0.25, 0.50, 0.25]
                elif lvl <= 60:
                    weights = [0.0, 0.10, 0.50, 0.40]
                else:
                    weights = [0.0, 0.05, 0.45, 0.50]
                b_count = random.choices([1, 2, 3, 4], weights=weights)[0]
                
            if is_boss_level:
                if rnd == 5:
                    b_count = max(b_count, 3)
                else:
                    b_count = max(b_count, 2)
                    
            # Pick behemoths for this round
            picked_b = []
            if is_boss_level and rnd == 5 and keystone_pool:
                keystone_pick = random.choice(keystone_pool)
                picked_b.append(keystone_pick)
                
            pool = theme_behemoths if (theme_behemoths and random.random() < 0.85) else avail_behemoths
            needed = b_count - len(picked_b)
            if needed > 0:
                remaining_candidates = [b for b in pool if b not in picked_b]
                if len(remaining_candidates) < needed:
                    remaining_candidates = [b for b in avail_behemoths if b not in picked_b]
                if len(remaining_candidates) < needed:
                    remaining_candidates = avail_behemoths[:]
                picked_b.extend(random.sample(remaining_candidates, min(needed, len(remaining_candidates))))
                
            # Determine modifiers
            picked_m = []
            if avail_modifiers and modifier_intensity != 'vanilla':
                if modifier_intensity == 'chaos':
                    m_count = random.choices([1, 2, 3], weights=[0.35, 0.45, 0.20])[0]
                elif modifier_intensity == 'mild':
                    m_count = random.choices([0, 1], weights=[0.5, 0.5])[0]
                else: # progressive
                    if lvl <= 4:
                        m_count = random.choices([0, 1], weights=[0.65, 0.35])[0]
                    elif lvl <= 10:
                        m_count = random.choices([0, 1, 2], weights=[0.25, 0.55, 0.20])[0]
                    elif lvl <= 20:
                        m_count = random.choices([1, 2, 3], weights=[0.30, 0.50, 0.20])[0]
                    elif lvl <= 50:
                        m_count = random.choices([1, 2, 3], weights=[0.20, 0.50, 0.30])[0]
                    else:
                        m_count = random.choices([2, 3], weights=[0.55, 0.45])[0]
                        
                if is_boss_level and rnd == 5:
                    m_count = max(m_count, 2)
                    
                if m_count > 0:
                    m_pool = theme_modifiers if (theme_modifiers and random.random() < 0.75) else avail_modifiers
                    if len(m_pool) < m_count:
                        m_pool = avail_modifiers
                    picked_m = random.sample(m_pool, min(m_count, len(m_pool)))
                    
            rounds.append({
                'round': rnd,
                'arena': arena,
                'behemoths': picked_b,
                'modifiers': picked_m
            })
            
        # Determine Behemoth Level for this level (engine supported up to 100 via expanded table)
        if b_lvl_mode == 'escalating':
            b_lvl = min(100, 10 + (lvl - 1) // 5)
        elif b_lvl_mode == 'fixed10':
            b_lvl = 10
        elif b_lvl_mode == 'fixed15':
            b_lvl = 15
        elif b_lvl_mode == 'fixed20':
            b_lvl = 20
        elif b_lvl_mode == 'fixed25':
            b_lvl = 25
        elif b_lvl_mode == 'fixed30':
            b_lvl = 30
        elif b_lvl_mode == 'fixed40':
            b_lvl = 40
        elif b_lvl_mode == 'fixed50':
            b_lvl = 50
        elif b_lvl_mode == 'custom':
            b_lvl = custom_b_lvl
        else: # progressive
            max_p = 25 if level_count <= 20 else (30 if level_count <= 100 else 50)
            b_lvl = min(100, int(10 + round(float(max_p - 10) * (lvl - 1) / max(1, level_count - 1))))

        level_cfg[str(lvl)] = {
            'timeLimit': timer_seconds,
            'behemothLevel': b_lvl,
            'rounds': rounds
        }
        
    return {
        'ok': True,
        'season': s_idx,
        'levelCount': level_count,
        'theme': theme,
        'density': density,
        'modifierIntensity': modifier_intensity,
        'bossMilestones': boss_milestones,
        'behemothLevelProgression': b_lvl_mode,
        'levelConfig': level_cfg
    }

def patch_spec_file(spec_name, cfg, out_dir):
    uasset_path = BASE_ASSETS_DIR / f'{spec_name}.uasset'
    uexp_path = BASE_ASSETS_DIR / f'{spec_name}.uexp'
    if not uasset_path.exists() or not uexp_path.exists():
        print(f"Missing base asset: {spec_name}")
        return False
        
    u = bytearray(uasset_path.read_bytes())
    b = bytearray(uexp_path.read_bytes())
    orig_u_len = len(u)
    orig_b_len = len(b)
    names = get_uasset_names(u)
    
    if 'GAUNTLET_S1_LEVEL' not in names:
        return False
    l_idx = names.index('GAUNTLET_S1_LEVEL')
    
    mod_ct_idx = names.index('EGauntletContentType::Modifier') if 'EGauntletContentType::Modifier' in names else None
    b_ct_idx = names.index('EGauntletContentType::Behemoth') if 'EGauntletContentType::Behemoth' in names else None
    none_idx = names.index('None') if 'None' in names else 0
    
    b_template = None
    m_template = None
    if b_ct_idx is not None:
        b_pos = b.find(struct.pack('<II', b_ct_idx, 0))
        if b_pos != -1:
            b_template = bytearray(b[b_pos - 33 : b_pos - 33 + 230])
    if mod_ct_idx is not None:
        m_pos = b.find(struct.pack('<II', mod_ct_idx, 0))
        if m_pos != -1:
            m_template = bytearray(b[m_pos - 33 : m_pos - 33 + 230])
    if m_template is None and b_template is not None and mod_ct_idx is not None:
        m_template = bytearray(b_template)
        struct.pack_into('<I', m_template, 33, mod_ct_idx)
        struct.pack_into('<I', m_template, 66, none_idx)
        struct.pack_into('<i', m_template, 99, 0)
        struct.pack_into('<I', m_template, 206, none_idx)
        
    target_levels = set(cfg.get('targetLevels', []))
    all_levels = cfg.get('allDualBehemothLevels', True)
    level_config = cfg.get('levelConfig', {})
    desired_behemoth_count = int(cfg.get('behemothCount', 3))
    time_limit = float(cfg.get('timeLimitSeconds', 0))
    global_modifiers = cfg.get('modifiers', [])
    
    base_row_count = struct.unpack_from('<I', b, 67)[0]
    
    # Calculate maximum required level across targetLevels and levelConfig
    max_req_lvl = 0
    if target_levels:
        max_req_lvl = max(max_req_lvl, max(int(x) for x in target_levels if str(x).isdigit()))
    if level_config:
        max_req_lvl = max(max_req_lvl, max(int(x) for x in level_config.keys() if str(x).isdigit()))
        
    # Dynamically expand table if more levels than base rows are requested
    if max_req_lvl > base_row_count:
        pos_last = -1
        o_scan = 71
        for r_idx in range(base_row_count):
            if r_idx == base_row_count - 1:
                pos_last = o_scan
                break
            _, o_scan = r_name(b, o_scan, names)
            while o_scan < len(b):
                tag, o_scan = parse_tag(b, o_scan, names)
                if tag['name'] == 'None':
                    break
        if pos_last != -1:
            row_template = bytearray(b[pos_last : len(b) - 4])
            new_rows_bytes = bytearray()
            for extra_lvl in range(base_row_count + 1, max_req_lvl + 1):
                new_row = bytearray(row_template)
                struct.pack_into('<II', new_row, 0, l_idx, extra_lvl + 1)
                new_rows_bytes.extend(new_row)
            b = bytearray(b[:len(b) - 4] + new_rows_bytes + b[-4:])
            struct.pack_into('<I', b, 67, max_req_lvl)
            
    effective_total_rows = max(base_row_count, max_req_lvl)
    rows = []
    o = 71
    for r_idx in range(effective_total_rows):
        start_o = o
        rows.append((r_idx + 1, start_o))
        rname, o = r_name(b, o, names)
        while o < len(b):
            tag, o = parse_tag(b, o, names)
            if tag['name'] == 'None':
                break
            
    target_levels = set(cfg.get('targetLevels', []))
    all_levels = cfg.get('allDualBehemothLevels', True)
    level_config = cfg.get('levelConfig', {})
    desired_behemoth_count = int(cfg.get('behemothCount', 3))
    time_limit = float(cfg.get('timeLimitSeconds', 0))
    global_modifiers = cfg.get('modifiers', [])
    
    round_ops = []
    for lvl, p in rows:
        lvl_str = str(lvl)
        is_custom_lvl = (not all_levels) and (lvl in target_levels or lvl_str in level_config)
        if not all_levels and not is_custom_lvl:
            continue
            
        lvl_cfg = level_config.get(lvl_str) or level_config.get(lvl) if is_custom_lvl else None
        
        o = p
        rname, o = r_name(b, o, names)
        
        while o < len(b):
            tag, o = parse_tag(b, o, names)
            if tag['name'] == 'None': break
            
            # TimeLimit
            if tag['name'] == 'TimeLimit':
                if lvl_cfg and 'timeLimit' in lvl_cfg and float(lvl_cfg['timeLimit']) > 0:
                    struct.pack_into('<f', b, tag['raw_start'], float(lvl_cfg['timeLimit']))
                elif time_limit > 0:
                    struct.pack_into('<f', b, tag['raw_start'], time_limit)
                    
            if tag['name'] == 'RoundStructures':
                r_tag_sz_off = tag['tag_start'] + 16
                r_inner_sz_off = tag['raw_start'] + 20
                raw = tag['raw']
                num_rounds = struct.unpack_from('<I', raw, 0)[0]
                ro = 4
                _, ro = r_name(raw, ro, names); _, ro = r_name(raw, ro, names); ro += 8; _, ro = r_name(raw, ro, names); ro += 17
                
                custom_rounds = {r['round'] - 1: r for r in lvl_cfg.get('rounds', [])} if (lvl_cfg and 'rounds' in lvl_cfg) else None
                
                for rnd in range(num_rounds):
                    rnd_cfg = custom_rounds.get(rnd) if custom_rounds else None
                    while ro < len(raw):
                        rtag, ro = parse_tag(raw, ro, names)
                        if rtag['name'] == 'None': break
                        
                        # Arena override
                        if rtag['name'] == 'Arena' and rnd_cfg and 'arena' in rnd_cfg:
                            a_name = rnd_cfg['arena']
                            if a_name in names:
                                arena_abs = tag['raw_start'] + rtag['raw_start']
                                struct.pack_into('<I', b, arena_abs, names.index(a_name))
                                
                        if rtag['name'] == 'Content':
                            c_tag_sz_off = tag['raw_start'] + rtag['tag_start'] + 16
                            c_num_items_off = tag['raw_start'] + rtag['raw_start']
                            c_inner_sz_off = tag['raw_start'] + rtag['raw_start'] + 20
                            craw = rtag['raw']
                            cnum = struct.unpack_from('<I', craw, 0)[0]
                            co = 4
                            _, co = r_name(craw, co, names); _, co = r_name(craw, co, names); co += 8; _, co = r_name(craw, co, names); co += 17
                            
                            b_items = []
                            m_items = []
                            for ci in range(cnum):
                                item_start = co
                                is_b = False
                                is_m = False
                                bn = None
                                mn = None
                                while co < len(craw):
                                    ctag, co = parse_tag(craw, co, names)
                                    if ctag['name'] == 'None': break
                                    if ctag['name'] == 'ContentType':
                                        i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                        if i < len(names):
                                            if names[i] == 'EGauntletContentType::Behemoth': is_b = True
                                            elif names[i] == 'EGauntletContentType::Modifier': is_m = True
                                    elif ctag['name'] == 'BehemothName':
                                        i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                        if i < len(names): bn = names[i]
                                    elif ctag['name'] == 'Modifier':
                                        mraw = ctag['raw']
                                        mo = 0
                                        while mo < len(mraw):
                                            mtag, mo = parse_tag(mraw, mo, names)
                                            if mtag['name'] == 'RowName':
                                                ri, _ = struct.unpack_from('<II', mtag['raw'], 0)
                                                if ri < len(names) and names[ri] != 'None':
                                                    mn = names[ri]
                                            if mtag['name'] == 'None': break
                                item_end = co
                                if is_b and bn:
                                    b_items.append({'ci': ci, 'raw': craw[item_start:item_end], 'name': bn})
                                elif is_m:
                                    m_items.append({'ci': ci, 'raw': craw[item_start:item_end], 'name': mn})
                                    
                            if rnd_cfg:
                                want_b = rnd_cfg.get('behemoths', [bi['name'] for bi in b_items])
                                want_m = rnd_cfg.get('modifiers', [mi['name'] for mi in m_items if mi['name']])
                            else:
                                if all_levels and len(b_items) == 2:
                                    existing_behemoths = [bi['name'] for bi in b_items]
                                    want_b = list(existing_behemoths)
                                    if desired_behemoth_count >= 3:
                                        pick = None
                                        for cand in CANDIDATES:
                                            if cand in names and cand not in want_b:
                                                pick = cand; break
                                        if not pick:
                                            for cand in CANDIDATES:
                                                if cand in names: pick = cand; break
                                        if not pick: pick = CANDIDATES[0]
                                        want_b.append(pick)
                                    if desired_behemoth_count >= 4:
                                        pick2 = None
                                        for cand in CANDIDATES:
                                            if cand in names and cand not in want_b:
                                                pick2 = cand; break
                                        if not pick2: pick2 = CANDIDATES[1]
                                        want_b.append(pick2)
                                    elif desired_behemoth_count == 1:
                                        want_b = want_b[:1]
                                    want_m = global_modifiers
                                else:
                                    want_b = [bi['name'] for bi in b_items]
                                    want_m = [mi['name'] for mi in m_items if mi['name']]
                                    
                            valid_b = [x for x in want_b if x in names]
                            valid_m = [x for x in want_m if x in names] if mod_ct_idx is not None else []
                            
                            target_b_lvl = None
                            if lvl_cfg and 'behemothLevel' in lvl_cfg:
                                try:
                                    target_b_lvl = max(1, min(100, int(lvl_cfg['behemothLevel'])))
                                except Exception:
                                    pass
                            elif 'behemothLevel' in cfg:
                                try:
                                    target_b_lvl = max(1, min(100, int(cfg['behemothLevel'])))
                                except Exception:
                                    pass
                            
                            new_items = []
                            for s_idx, bn in enumerate(valid_b):
                                if s_idx < len(b_items):
                                    itm = bytearray(b_items[s_idx]['raw'])
                                    struct.pack_into('<I', itm, 66, names.index(bn))
                                    if target_b_lvl is not None and target_b_lvl > 0:
                                        struct.pack_into('<i', itm, 99, target_b_lvl)
                                    new_items.append(itm)
                                else:
                                    itm = bytearray(b_items[0]['raw'] if b_items else b_template)
                                    struct.pack_into('<I', itm, 33, b_ct_idx)
                                    struct.pack_into('<I', itm, 66, names.index(bn))
                                    if target_b_lvl is not None and target_b_lvl > 0:
                                        struct.pack_into('<i', itm, 99, target_b_lvl)
                                    struct.pack_into('<I', itm, 206, none_idx)
                                    new_items.append(itm)
                                    
                            for mn in valid_m:
                                itm = bytearray(m_template)
                                struct.pack_into('<I', itm, 33, mod_ct_idx)
                                struct.pack_into('<I', itm, 66, none_idx)
                                struct.pack_into('<i', itm, 99, 0)
                                struct.pack_into('<I', itm, 206, names.index(mn))
                                new_items.append(itm)
                                
                            old_bytes = craw[53:]
                            new_bytes = b''.join(new_items)
                            if new_bytes != old_bytes:
                                abs_start = tag['raw_start'] + rtag['raw_start'] + 53
                                abs_end = tag['raw_start'] + rtag['raw_start'] + len(craw)
                                round_ops.append({
                                    'pos': abs_start,
                                    'end': abs_end,
                                    'new_bytes': new_bytes,
                                    'count': len(new_items),
                                    'delta': len(new_bytes) - len(old_bytes),
                                    'c_num_items_off': c_num_items_off,
                                    'c_tag_sz_off': c_tag_sz_off,
                                    'c_inner_sz_off': c_inner_sz_off,
                                    'r_tag_sz_off': r_tag_sz_off,
                                    'r_inner_sz_off': r_inner_sz_off
                                })
                                
    round_ops.sort(key=lambda x: x['pos'], reverse=True)
    total_delta = 0
    for op in round_ops:
        d = op['delta']
        b[op['pos']:op['end']] = op['new_bytes']
        struct.pack_into('<I', b, op['c_num_items_off'], op['count'])
        
        c_sz = struct.unpack_from('<I', b, op['c_tag_sz_off'])[0]
        struct.pack_into('<I', b, op['c_tag_sz_off'], c_sz + d)
        c_inner = struct.unpack_from('<Q', b, op['c_inner_sz_off'])[0]
        struct.pack_into('<Q', b, op['c_inner_sz_off'], c_inner + d)
        
        r_sz = struct.unpack_from('<I', b, op['r_tag_sz_off'])[0]
        struct.pack_into('<I', b, op['r_tag_sz_off'], r_sz + d)
        r_inner = struct.unpack_from('<Q', b, op['r_inner_sz_off'])[0]
        struct.pack_into('<Q', b, op['r_inner_sz_off'], r_inner + d)
        
    total_delta = len(b) - orig_b_len
    export_count, export_at = struct.unpack_from('<II', u, 57)
    size, offset = struct.unpack_from('<qq', u, export_at + 28)
    struct.pack_into('<q', u, export_at + 28, size + total_delta)
    bulk = struct.unpack_from('<q', u, 169)[0]
    struct.pack_into('<q', u, 169, bulk + total_delta)
    
    assert len(u) == orig_u_len, f"uasset size changed from {orig_u_len} to {len(u)}!"
    
    out_dir.mkdir(parents=True, exist_ok=True)
    out_u = out_dir / f'{spec_name}.uasset'
    out_b = out_dir / f'{spec_name}.uexp'
    out_u.write_bytes(u)
    out_b.write_bytes(b)
    print(f"[{spec_name}] Patched! added={total_delta} bytes (uasset intact at {len(u)} bytes, rows={effective_total_rows})")
    return True

def build_expanded_enemy_level_table(max_level=100, out_dir=None):
    base_u = BASE_ASSETS_DIR / 'exploration_enemy_level_table.uasset'
    base_b = BASE_ASSETS_DIR / 'exploration_enemy_level_table.uexp'
    hashes_file = ROOT / 'tools' / 'digit_name_hashes.json'
    if not hashes_file.exists():
        hashes_file = ROOT / 'package' / 'tools' / 'digit_name_hashes.json'
    
    if not base_u.exists() or not base_b.exists() or not hashes_file.exists():
        print("[exploration_enemy_level_table] Base assets or digit hashes missing, skipping table expansion.")
        return False
        
    uasset_bytes = bytearray(base_u.read_bytes())
    uexp_bytes = bytearray(base_b.read_bytes())
    with open(hashes_file, 'r', encoding='utf-8') as f:
        hashes = json.load(f)
        
    # Read existing names
    curr = 193
    name_to_idx = {}
    names_list = []
    base_name_count = struct.unpack_from('<i', uasset_bytes, 41)[0]
    for i in range(base_name_count):
        slen, = struct.unpack_from('<i', uasset_bytes, curr)
        curr += 4
        s = uasset_bytes[curr:curr+slen-1].decode('latin-1') if slen > 0 else ''
        curr += slen + 4
        name_to_idx[s] = i
        names_list.append(s)
        
    import_off = struct.unpack_from('<i', uasset_bytes, 69)[0]
    
    new_name_entries = bytearray()
    for lvl in range(26, max_level + 1):
        s = str(lvl)
        if s not in name_to_idx:
            s_bytes = s.encode('latin-1') + b'\x00'
            slen = len(s_bytes)
            h1, h2 = hashes.get(s, [0, 0])
            name_to_idx[s] = len(names_list)
            names_list.append(s)
            new_name_entries.extend(struct.pack('<i', slen) + s_bytes + struct.pack('<HH', h1, h2))
            
    name_delta = len(new_name_entries)
    new_uasset = bytearray(uasset_bytes[:import_off] + new_name_entries + uasset_bytes[import_off:])
    
    total_new_uasset_size = len(new_uasset)
    struct.pack_into('<i', new_uasset, 24, total_new_uasset_size)
    struct.pack_into('<i', new_uasset, 41, len(names_list))
    struct.pack_into('<i', new_uasset, 69, import_off + name_delta)
    
    exp_off = struct.unpack_from('<i', uasset_bytes, 61)[0]
    new_exp_off = exp_off + name_delta
    struct.pack_into('<i', new_uasset, 61, new_exp_off)
    dep_off = struct.unpack_from('<i', uasset_bytes, 73)[0]
    struct.pack_into('<i', new_uasset, 73, dep_off + name_delta)
    struct.pack_into('<i', new_uasset, 117, len(names_list))

    # Shift AssetRegistryDataOffset (offset 165)
    asset_reg_off = struct.unpack_from('<i', uasset_bytes, 165)[0]
    struct.pack_into('<i', new_uasset, 165, asset_reg_off + name_delta)

    # Shift PreloadDependencyOffset (offset 189)
    preload_off = struct.unpack_from('<i', uasset_bytes, 189)[0]
    struct.pack_into('<i', new_uasset, 189, preload_off + name_delta)
    
    body = bytearray(uexp_bytes[:-4])
    footer = uexp_bytes[-4:]
    struct.pack_into('<i', body, 41, max_level + 1)
    
    r25 = bytearray(uexp_bytes[20794:20794+847])
    for lvl in range(26, max_level + 1):
        row = bytearray(r25)
        s_idx = name_to_idx[str(lvl)]
        struct.pack_into('<ii', row, 0, s_idx, 0)
        # Scaled Rams reward
        struct.pack_into('<i', row, 414, min(2000, 500 + (lvl - 25) * 10))
        # Mastery XP reward
        struct.pack_into('<i', row, 777, 100 + (lvl - 1) * 10)
        # Recommended Power (+25 per level)
        rec_pow = 65 + (lvl - 1) * 25
        struct.pack_into('<i', row, 806, rec_pow)
        struct.pack_into('<i', row, 835, rec_pow)
        body.extend(row)
        
    new_uexp = bytearray(body + footer)

    # BulkDataStartOffset (offset 169, int64): uasset size + uexp size - 4
    struct.pack_into('<q', new_uasset, 169, total_new_uasset_size + len(new_uexp) - 4)

    struct.pack_into('<q', new_uasset, new_exp_off + 28, len(new_uexp) - 4)
    struct.pack_into('<q', new_uasset, new_exp_off + 36, total_new_uasset_size)
    
    if out_dir is not None:
        out_p = Path(out_dir)
        (out_p / 'exploration_enemy_level_table.uasset').write_bytes(new_uasset)
        (out_p / 'exploration_enemy_level_table.uexp').write_bytes(new_uexp)
        
    print(f"[exploration_enemy_level_table] Expanded successfully up to level {max_level} ({len(names_list)} names, {max_level+1} rows, {len(new_uexp)} uexp bytes)")
    return True

def generate_pak(custom_config=None):
    cfg = custom_config or load_config()
    target_season = cfg.get('season', 3)
    
    with tempfile.TemporaryDirectory() as td:
        tmp_out = Path(td)
        
        specs = [
            ('gauntlet_mode_encounter_specs', 1),
            ('gauntlet_mode_encounter_specs_s2', 2),
            ('gauntlet_mode_encounter_specs_s3', 3),
            ('gauntlet_mode_encounter_specs_s4', 4),
            ('gauntlet_mode_encounter_specs_s5', 5),
        ]
        
        for s_name, s_num in specs:
            if str(target_season).lower() == 'all' or target_season == 0 or target_season == s_num:
                patch_spec_file(s_name, cfg, tmp_out)
            else:
                shutil.copy2(BASE_ASSETS_DIR / f'{s_name}.uasset', tmp_out / f'{s_name}.uasset')
                shutil.copy2(BASE_ASSETS_DIR / f'{s_name}.uexp', tmp_out / f'{s_name}.uexp')
                
        # Build expanded exploration_enemy_level_table (supports behemoth levels 0 to 100)
        try:
            build_expanded_enemy_level_table(max_level=100, out_dir=tmp_out)
        except Exception as e:
            print(f"[exploration_enemy_level_table] Build error: {e}")

        builder = repak.PakBuilder()
        OUT_PAK_FILE.parent.mkdir(parents=True, exist_ok=True)
        writer = builder.writer(OUT_PAK_FILE, version=repak.Version.V3, mount_point='../../../')
        
        target_base = 'Archon/Content/gamemodes/escalation/base_blueprints'
        for s_name, _ in specs:
            for ext in ['.uasset', '.uexp']:
                fpath = tmp_out / f'{s_name}{ext}'
                if fpath.exists():
                    rel_path = f'{target_base}/{s_name}{ext}'
                    writer.write_file(rel_path, fpath.read_bytes())

        # Also write expanded exploration_enemy_level_table into pak
        table_base = 'Archon/Content/Monsters/_shared/data_tables'
        for ext in ['.uasset', '.uexp']:
            fpath = tmp_out / f'exploration_enemy_level_table{ext}'
            if fpath.exists():
                rel_path = f'{table_base}/exploration_enemy_level_table{ext}'
                writer.write_file(rel_path, fpath.read_bytes())
                    
        writer.write_index()
        print(f"Pak successfully compiled: {OUT_PAK_FILE} ({OUT_PAK_FILE.stat().st_size} bytes)")
    
    gdir = None
    try:
        conf_file = ROOT / 'config.json'
        if conf_file.exists():
            with open(conf_file, 'r', encoding='utf-8') as f:
                gdir = json.load(f).get('GameDir')
        if not gdir and os.environ.get('LOCALAPPDATA'):
            lad_conf = Path(os.environ['LOCALAPPDATA']) / 'DauntlessForever' / 'versions' / '1.14.7' / 'config.json'
            if lad_conf.exists():
                with open(lad_conf, 'r', encoding='utf-8') as f:
                    gdir = json.load(f).get('GameDir')
        if gdir:
            paks_dir = Path(gdir) / 'Archon' / 'Content' / 'Paks'
            if paks_dir.exists():
                dest = paks_dir / OUT_PAK_FILE.name
                shutil.copy2(OUT_PAK_FILE, dest)
                print(f"Synced pak directly to active game: {dest}")
    except Exception as e:
        print(f"Active game sync note: {e}")
        
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'inspect':
        s = sys.argv[2] if len(sys.argv) > 2 else 3
        l = sys.argv[3] if len(sys.argv) > 3 else 1
        res = inspect_level(s, l)
        print(json.dumps(res))
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == 'random-season':
        s = sys.argv[2] if len(sys.argv) > 2 else 3
        opts = sys.argv[3] if len(sys.argv) > 3 else '{}'
        res = generate_random_season(s, opts)
        print(json.dumps(res))
        sys.exit(0)

    custom_cfg = None
    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].strip()
        if raw_arg.startswith('@'):
            try:
                with open(raw_arg[1:], 'r', encoding='utf-8') as f:
                    custom_cfg = json.load(f)
            except Exception:
                pass
        else:
            try:
                custom_cfg = json.loads(raw_arg)
            except Exception:
                pass
    generate_pak(custom_cfg)
