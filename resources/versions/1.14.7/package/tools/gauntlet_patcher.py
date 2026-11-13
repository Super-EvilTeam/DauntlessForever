# SPDX-License-Identifier: AGPL-3.0-only
# Dauntless Forever - Dynamic Gauntlet Encounter Patcher
import struct, json, sys, os, shutil, tempfile
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
    
    pos = b_data.find(struct.pack('<II', l_idx, int(level_num) + 1))
    if pos == -1:
        return {'ok': False, 'error': f'Level {level_num} not found in Season {s_idx}.'}
        
    o = pos + 8
    time_limit = 420.0
    rounds = []
    
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
                            if is_b and bn:
                                behemoths.append(bn)
                            if is_m and mn:
                                modifiers.append(mn)
                rounds.append({
                    'round': rnd + 1,
                    'arena': arena,
                    'behemoths': behemoths,
                    'modifiers': modifiers
                })
                
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
        'level': int(level_num),
        'timeLimit': time_limit,
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

def patch_spec_file(spec_name, cfg, out_dir):
    uasset_path = BASE_ASSETS_DIR / f'{spec_name}.uasset'
    uexp_path = BASE_ASSETS_DIR / f'{spec_name}.uexp'
    if not uasset_path.exists() or not uexp_path.exists():
        print(f"Missing base asset: {spec_name}")
        return False
        
    u = bytearray(uasset_path.read_bytes())
    b = bytearray(uexp_path.read_bytes())
    orig_u_len = len(u)
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
        
    rows = []
    for num in range(2, 35):
        pos = b.find(struct.pack('<II', l_idx, num))
        if pos != -1:
            rows.append((num - 1, pos))
            
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
                            
                            new_items = []
                            for s_idx, bn in enumerate(valid_b):
                                if s_idx < len(b_items):
                                    itm = bytearray(b_items[s_idx]['raw'])
                                    struct.pack_into('<I', itm, 66, names.index(bn))
                                    new_items.append(itm)
                                else:
                                    itm = bytearray(b_items[0]['raw'] if b_items else b_template)
                                    struct.pack_into('<I', itm, 33, b_ct_idx)
                                    struct.pack_into('<I', itm, 66, names.index(bn))
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
        
        total_delta += d
        
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
    print(f"[{spec_name}] Patched! added={total_delta} bytes (uasset intact at {len(u)} bytes)")
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

    custom_cfg = None
    if len(sys.argv) > 1:
        try:
            custom_cfg = json.loads(sys.argv[1])
        except Exception:
            pass
    generate_pak(custom_cfg)
