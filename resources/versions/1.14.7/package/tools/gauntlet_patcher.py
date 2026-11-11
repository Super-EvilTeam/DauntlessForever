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
    'armstrong_normal': 'Torgadoro',
    'armstrong_heroic': 'Winterhorn Skraev',
    'beaver_normal': 'Gnasher',
    'beaver_alpha': 'Ragetail Gnasher',
    'beaver_blaze': 'Flameborn Gnasher',
    'beaver_frost': 'Frostwisp Gnasher',
    'bugbear_normal': 'Charrogg',
    'bullseye_normal': 'Quillshot',
    'bullseye_alpha': 'Deadeye Quillshot',
    'bullseye_heroic': 'Heroic Quillshot',
    'crowbear_normal': 'Shrowd',
    'crowbear_alpha': 'Bloodshot Shrowd',
    'electroquill_normal': 'Nayzaga',
    'electroquill_alpha': 'Shockjaw Nayzaga',
    'fulgar_normal': 'Drask',
    'fulgar_alpha': 'Thunderdeep Drask',
    'glitter_normal': 'Valomyr',
    'glitter_heroic': 'Heroic Valomyr',
    'habanero_normal': 'Hellion',
    'host_normal': 'Boreus',
    'host_alpha': 'Dreadfrost Boreus',
    'host_radiant': 'Lightbound Boreus',
    'lavaroller_normal': 'Charrogg',
    'lavaroller_alpha': 'Firebrand Charrogg',
    'lavaroller_heroic': 'Heroic Charrogg',
    'lerawr_normal': 'Embermane',
    'lerawr_alpha': 'Bloodfire Embermane',
    'lerawr_heroic': 'Flameborn Embermane',
    'mantis_normal': 'Sahvyt',
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
    'paper_heroic': 'Flameborn Rezakiri',
    'paper_umbral': 'Shadowtouched Koshai',
    'randall_normal': 'Thrax',
    'randall_heroic': 'Heroic Thrax',
    'rock_normal': 'Skarn',
    'rock_alpha': 'Rockfall Skarn',
    'rock_frost': 'Deepfrost Skarn',
    'rock_heroic': 'Heroic Skarn',
    'sally_normal': 'Charrogg',
    'sally_alpha': 'Firebrand Charrogg',
    'salt_normal': 'Valomyr',
    'salt_heroic': 'Heroic Valomyr',
    'scissors_normal': 'Kharabak',
    'scissors_alpha': 'Razorwing Kharabak',
    'shadowcat_normal': 'Riftstalker',
    'shadowcat_heroic': 'Heroic Riftstalker',
    'shockmane_normal': 'Stormclaw',
    'shockmane_alpha': 'Tempestborne Stormclaw',
    'shockmane_heroic': 'Heroic Stormclaw',
    'snowflake_normal': 'Pangar',
    'snowflake_alpha': 'Frostback Pangar',
    'snowflake_heroic': 'Heroic Pangar',
    'terramane_normal': 'Fenroar',
    'terramane_alpha': 'Sporestruck Fenroar',
    'thunderbird_normal': 'Malkarion',
    'thunderbird_heroic': 'Heroic Malkarion',
    'wolf_normal': 'Frostwulf'
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
                            bn = None
                            while co < len(craw):
                                ctag, co = parse_tag(craw, co, names)
                                if ctag['name'] == 'None': break
                                if ctag['name'] == 'ContentType':
                                    i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                    if i < len(names) and names[i] == 'EGauntletContentType::Behemoth': is_b = True
                                elif ctag['name'] == 'BehemothName':
                                    i, _ = struct.unpack_from('<II', ctag['raw'], 0)
                                    if i < len(names): bn = names[i]
                            if is_b and bn:
                                behemoths.append(bn)
                rounds.append({
                    'round': rnd + 1,
                    'arena': arena,
                    'behemoths': behemoths
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
    
    mod_name_indices = []
    for m in cfg.get('modifiers', []):
        if m in names:
            mod_name_indices.append(names.index(m))
            
    if 'GAUNTLET_S1_LEVEL' not in names:
        return False
    l_idx = names.index('GAUNTLET_S1_LEVEL')
    
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
    
    levels_to_patch = []
    for lvl, p in rows:
        lvl_str = str(lvl)
        is_custom_lvl = (not all_levels) and (lvl in target_levels or lvl_str in level_config)
        if not all_levels and not is_custom_lvl:
            continue
            
        lvl_cfg = level_config.get(lvl_str) or level_config.get(lvl) if is_custom_lvl else None
        
        o = p
        rname, o = r_name(b, o, names)
        
        round_ops = []
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
                                item_end = co
                                if is_b: b_items.append((ci, item_start, item_end, bn))
                                if is_m: m_items.append((ci, item_start, item_end))
                                
                            new_items_to_insert = []
                            
                            # Specific level custom config branch
                            if rnd_cfg and 'behemoths' in rnd_cfg:
                                want_b = rnd_cfg['behemoths']
                                # Replace existing slots in place
                                for slot in range(min(len(want_b), len(b_items))):
                                    b_choice = want_b[slot]
                                    if b_choice in names:
                                        sco = b_items[slot][1]
                                        while sco < b_items[slot][2]:
                                            ctag, sco = parse_tag(craw, sco, names)
                                            if ctag['name'] == 'BehemothName':
                                                bn_abs = tag['raw_start'] + rtag['raw_start'] + ctag['raw_start']
                                                struct.pack_into('<I', b, bn_abs, names.index(b_choice))
                                                break
                                                
                                # Insert extra slots if user wants more than existing
                                if len(want_b) > len(b_items) and b_items:
                                    template_item = craw[b_items[0][1] : b_items[0][2]]
                                    for extra_b in want_b[len(b_items):]:
                                        if extra_b in names:
                                            item_new = bytearray(template_item)
                                            t_co = 0
                                            while t_co < len(item_new):
                                                ctag, t_co = parse_tag(item_new, t_co, names)
                                                if ctag['name'] == 'BehemothName':
                                                    struct.pack_into('<I', item_new, ctag['raw_start'], names.index(extra_b))
                                                    new_items_to_insert.append(item_new)
                                                    break
                                                    
                                if new_items_to_insert:
                                    insert_pos = tag['raw_start'] + rtag['raw_start'] + b_items[-1][2]
                                    round_ops.append({
                                        'type': 'insert',
                                        'pos': insert_pos,
                                        'items': new_items_to_insert,
                                        'c_tag_sz_off': c_tag_sz_off,
                                        'c_num_items_off': c_num_items_off,
                                        'c_inner_sz_off': c_inner_sz_off,
                                        'r_tag_sz_off': r_tag_sz_off,
                                        'r_inner_sz_off': r_inner_sz_off
                                    })
                                    
                                # Delete slots if user wants fewer than existing
                                if len(want_b) < len(b_items):
                                    for del_slot in range(len(want_b), len(b_items)):
                                        del_start = tag['raw_start'] + rtag['raw_start'] + b_items[del_slot][1]
                                        del_end = tag['raw_start'] + rtag['raw_start'] + b_items[del_slot][2]
                                        round_ops.append({
                                            'type': 'delete',
                                            'pos': del_start,
                                            'end': del_end,
                                            'sz': del_end - del_start,
                                            'c_tag_sz_off': c_tag_sz_off,
                                            'c_num_items_off': c_num_items_off,
                                            'c_inner_sz_off': c_inner_sz_off,
                                            'r_tag_sz_off': r_tag_sz_off,
                                            'r_inner_sz_off': r_inner_sz_off
                                        })
                                        
                                # Modifiers for this specific round
                                rnd_mods = rnd_cfg.get('modifiers')
                                active_mod_indices = [names.index(m) for m in rnd_mods if m in names] if rnd_mods is not None else mod_name_indices
                                if active_mod_indices and m_items:
                                    first_m_abs = tag['raw_start'] + rtag['raw_start'] + m_items[0][1]
                                    struct.pack_into('<I', b, first_m_abs + 206, active_mod_indices[0])
                                    if len(active_mod_indices) > 1:
                                        template_m = craw[m_items[0][1] : m_items[0][2]]
                                        for extra_m_idx in active_mod_indices[1:]:
                                            mod_new = bytearray(template_m)
                                            struct.pack_into('<I', mod_new, 206, extra_m_idx)
                                            round_ops.append({
                                                'type': 'insert',
                                                'pos': tag['raw_start'] + rtag['raw_start'] + b_items[-1][2],
                                                'items': [mod_new],
                                                'c_tag_sz_off': c_tag_sz_off,
                                                'c_num_items_off': c_num_items_off,
                                                'c_inner_sz_off': c_inner_sz_off,
                                                'r_tag_sz_off': r_tag_sz_off,
                                                'r_inner_sz_off': r_inner_sz_off
                                            })
                            else:
                                # Global dual-behemoth modification branch
                                should_add_behemoth = (len(b_items) == 2 and desired_behemoth_count >= 3)
                                existing_behemoths = [bi[3] for bi in b_items]
                                
                                if mod_name_indices and m_items:
                                    first_m_abs = tag['raw_start'] + rtag['raw_start'] + m_items[0][1]
                                    struct.pack_into('<I', b, first_m_abs + 206, mod_name_indices[0])
                                    
                                if should_add_behemoth and b_items:
                                    template_item = craw[b_items[0][1] : b_items[0][2]]
                                    pick = None
                                    for cand in CANDIDATES:
                                        if cand in names and cand not in existing_behemoths:
                                            pick = cand
                                            break
                                    if not pick:
                                        for cand in CANDIDATES:
                                            if cand in names: pick = cand; break
                                    if not pick: pick = CANDIDATES[0]
                                    pick_idx = names.index(pick)
                                    
                                    item_new = bytearray(template_item)
                                    struct.pack_into('<I', item_new, 66, pick_idx)
                                    new_items_to_insert.append(item_new)
                                    
                                    if desired_behemoth_count >= 4:
                                        pick2 = None
                                        for cand in CANDIDATES:
                                            if cand in names and cand not in existing_behemoths and cand != pick:
                                                pick2 = cand; break
                                        if not pick2: pick2 = CANDIDATES[1]
                                        if pick2 in names:
                                            pick2_idx = names.index(pick2)
                                            item_new2 = bytearray(template_item)
                                            struct.pack_into('<I', item_new2, 66, pick2_idx)
                                            new_items_to_insert.append(item_new2)
                                            
                                if len(mod_name_indices) > 1 and m_items:
                                    template_m = craw[m_items[0][1] : m_items[0][2]]
                                    for extra_mod_idx in mod_name_indices[1:]:
                                        mod_new = bytearray(template_m)
                                        struct.pack_into('<I', mod_new, 206, extra_mod_idx)
                                        new_items_to_insert.append(mod_new)
                                        
                                if new_items_to_insert:
                                    insert_pos = tag['raw_start'] + rtag['raw_start'] + (b_items[-1][2] if b_items else 0)
                                    round_ops.append({
                                        'type': 'insert',
                                        'pos': insert_pos,
                                        'items': new_items_to_insert,
                                        'c_tag_sz_off': c_tag_sz_off,
                                        'c_num_items_off': c_num_items_off,
                                        'c_inner_sz_off': c_inner_sz_off,
                                        'r_tag_sz_off': r_tag_sz_off,
                                        'r_inner_sz_off': r_inner_sz_off
                                    })
                                    
        if round_ops:
            levels_to_patch.append(round_ops)
            
    # Flatten all ops and execute in reverse order of position
    all_ops = []
    for ops in levels_to_patch:
        for op in ops:
            if op['type'] == 'insert':
                for itm in op['items']:
                    all_ops.append({
                        'type': 'insert',
                        'pos': op['pos'],
                        'item': itm,
                        'delta': len(itm),
                        'c_tag_sz_off': op['c_tag_sz_off'],
                        'c_num_items_off': op['c_num_items_off'],
                        'c_inner_sz_off': op['c_inner_sz_off'],
                        'r_tag_sz_off': op['r_tag_sz_off'],
                        'r_inner_sz_off': op['r_inner_sz_off']
                    })
            elif op['type'] == 'delete':
                all_ops.append({
                    'type': 'delete',
                    'pos': op['pos'],
                    'end': op['end'],
                    'delta': -op['sz'],
                    'c_tag_sz_off': op['c_tag_sz_off'],
                    'c_num_items_off': op['c_num_items_off'],
                    'c_inner_sz_off': op['c_inner_sz_off'],
                    'r_tag_sz_off': op['r_tag_sz_off'],
                    'r_inner_sz_off': op['r_inner_sz_off']
                })
                
    all_ops.sort(key=lambda x: x['pos'], reverse=True)
    total_delta = 0
    for op in all_ops:
        d = op['delta']
        if op['type'] == 'insert':
            itm = op['item']
            b[op['pos']:op['pos']] = itm
            c_num = struct.unpack_from('<I', b, op['c_num_items_off'])[0]
            struct.pack_into('<I', b, op['c_num_items_off'], c_num + 1)
        elif op['type'] == 'delete':
            del b[op['pos']:op['end']]
            c_num = struct.unpack_from('<I', b, op['c_num_items_off'])[0]
            struct.pack_into('<I', b, op['c_num_items_off'], c_num - 1)
            
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
