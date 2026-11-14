#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Gauntlet Customizer Local Web UI Server
import http.server, socketserver, json, sys, os, subprocess, urllib.parse, webbrowser, socket
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent
MOD_DIR = UI_DIR.parent
TOOLS_DIR = MOD_DIR / 'Tools'
PATCHER_SCRIPT = TOOLS_DIR / 'gauntlet_patcher.py'
CONFIG_FILE = MOD_DIR / 'config.json'
PORT = 8799

GAUNTLET_MODIFIERS = [
    {"id": "HM_PUSHANDPULL", "name": "Push and Pull", "desc": "Gravitational shockwaves pulse across the arena floor", "seasons": [3]},
    {"id": "HM_FAST_ATTACKS", "name": "Fast Attacks", "desc": "Accelerated Behemoth attack and recovery speed", "seasons": [2]},
    {"id": "HM_ELECTRIFY", "name": "Electrify", "desc": "Lightning orbs and shock auras periodically pulse", "seasons": [1, 2, 3]},
    {"id": "HM_COMBUSTION", "name": "Combustion", "desc": "Fiery explosions erupt under Slayers or on impacts", "seasons": [1, 2, 3]},
    {"id": "HM_ENVIRONMENT_DEEPFREEZE", "name": "Deep Freeze", "desc": "Severe Frostbite cold slows stamina recovery", "seasons": [2]},
    {"id": "HM_FURY", "name": "Fury", "desc": "Behemoths enrage faster, stay enraged longer, hit harder", "seasons": [2]},
    {"id": "HM_AFTERSHOCK", "name": "Aftershock", "desc": "Fissures erupt from the ground after slams", "seasons": [2]},
    {"id": "HM_STONEHIDE", "name": "Stonehide", "desc": "Heavily reduced damage until armor plates break", "seasons": [1, 2]},
    {"id": "HM_THICK_SKULL", "name": "Thick Skull", "desc": "Massive stagger and interrupt resistance", "seasons": [2]},
    {"id": "HM_POISON_BLOOD", "name": "Poison Blood", "desc": "Corruption and poison hazard damage", "seasons": [2]},
    {"id": "HM_LESS_NORMAL_MORE_EXPOSE", "name": "Weak Spot Surge", "desc": "Only wounded or broken parts take high damage", "seasons": [1, 2]},
    {"id": "HM_MOMENTUM", "name": "Momentum", "desc": "Behemoths gain increased movement and charge speed", "seasons": [1]},
    {"id": "HM_FRIGID_TOUCH", "name": "Frigid Touch", "desc": "Frost hazards build up on hits", "seasons": [1, 2, 3]},
    {"id": "HM_ENTROPY", "name": "Entropy", "desc": "Aetheric anomalies drain Slayer stamina or health", "seasons": [1, 2, 3]},
    {"id": "HM_ANEMIC", "name": "Anemic", "desc": "Healing effectiveness and potion power significantly reduced", "seasons": [3]}
]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

class CustomizerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            cfg = {}
            if CONFIG_FILE.exists():
                try:
                    cfg = json.loads(CONFIG_FILE.read_text('utf-8'))
                except Exception:
                    pass
            resp = {
                "ok": True,
                "config": cfg,
                "seasons": [1, 2, 3, 4, 5],
                "availableModifiers": GAUNTLET_MODIFIERS
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        if url.path == '/api/inspect':
            params = urllib.parse.parse_qs(url.query)
            season = params.get('season', ['3'])[0]
            level = params.get('level', ['1'])[0]
            try:
                out = subprocess.check_output(
                    [sys.executable, str(PATCHER_SCRIPT), 'inspect', str(season), str(level)],
                    text=True, encoding='utf-8'
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(out.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')

        if url.path == '/api/random-season':
            try:
                data = json.loads(body) if body else {}
                season = str(data.get('season', 3))
                opts_json = json.dumps(data.get('options', {}))
                out = subprocess.check_output(
                    [sys.executable, str(PATCHER_SCRIPT), 'random-season', season, opts_json],
                    text=True, encoding='utf-8'
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(out.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if url.path == '/api/save':
            try:
                cfg = json.loads(body)
                CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
                out = subprocess.check_output(
                    [sys.executable, str(PATCHER_SCRIPT), f'@{CONFIG_FILE}'],
                    text=True, encoding='utf-8'
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": "Custom Gauntlet compiled & mounted successfully!", "log": out}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def main():
    if is_port_in_use(PORT):
        print(f"Gauntlet Customizer server is already running on http://127.0.0.1:{PORT}. Opening browser...")
        webbrowser.open(f'http://127.0.0.1:{PORT}')
        return

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORT), CustomizerHandler) as httpd:
        print(f"================================================================")
        print(f" Gauntlet Customizer Web UI running at http://127.0.0.1:{PORT}")
        print(f" Press Ctrl+C in this terminal to stop the server.")
        print(f"================================================================")
        webbrowser.open(f'http://127.0.0.1:{PORT}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == '__main__':
    main()
