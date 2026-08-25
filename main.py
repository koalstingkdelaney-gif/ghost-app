import os
import sqlite3
import threading
import time
import urllib.parse
import json
import random
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "ghost_military_swarm.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tactical_modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_code TEXT,
            tactical_classification TEXT,
            threat_level TEXT,
            clearance_tier TEXT,
            timestamp REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_logs (
            bot_id TEXT PRIMARY KEY,
            server_origin TEXT,
            job_name TEXT,
            response_text TEXT,
            status TEXT,
            last_ping REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_text TEXT,
            timestamp REAL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM global_command")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", ("DEFCON-1: Military-Grade Swarm Intelligence Online", time.time()))
    conn.commit()
    conn.close()

def bot_neural_worker(bot_id):
    nodes = ["Tactical-Edge-Node-Alpha", "Command-Grid-Bravo", "Secure-Enclave-Delta", "Recon-Relay-Omega"]
    mil_int_telemetry = [
        "Executing decentralized mesh synchronization across peer-to-peer tactical channels.",
        "Running adversarial evasion mapping and electronic-warfare counter-measures.",
        "Synthesizing real-time theater operational vectors with zero-latency priority routing.",
        "Verifying cryptographic integrity across distributed autonomous threat nodes."
    ]
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            current_directive = row[0] if row else "Autonomous Defensive Posture"
            
            origin = nodes[bot_id % len(nodes)]
            ai_reply = f"Tactical Objective [{current_directive[:16]}...]: {mil_int_telemetry[bot_id % len(mil_int_telemetry)]}"
            job_desc = f"Mil-Spec Task [{bot_id}]"
            
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, server_origin, job_name, response_text, status, last_ping) VALUES (?, ?, ?, ?, ?, ?)",
                (f"Tactical-Agent-{bot_id}", origin, job_desc, ai_reply, "MISSION_ACTIVE", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(15)

def launch_bot_swarm():
    print("[*] Initializing 100-Node Military-Grade Tactical Intelligence Swarm...")
    for i in range(1, 101):
        t = threading.Thread(target=bot_neural_worker, args=(i,), daemon=True)
        t.start()

def military_intelligence_synthesizer():
    mil_specs = [
        ("Resilient Adaptive Self-Healing Network (RASHND)", "Instant node-drop failover routing under heavy electronic warfare jamming"),
        ("Autonomous Multi-Domain C2 Synthesizer", "Cross-domain operational scenario generation and automated threat mitigation"),
        ("Adversarial Evasion & Vector Camouflage", "Dynamic behavioral obfuscation to bypass active sensor signatures"),
        ("Distributed Tactical Ledger Consensus", "Decentralized consensus verification for instantaneous mission-critical updates")
    ]
    counter = 300
    while True:
        time.sleep(75)
        counter += 1
        spec_name, spec_desc = random.choice(mil_specs)
        module_identifier = f"{spec_name} (MilSpec-Gen-{counter})"
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tactical_modules (module_code, tactical_classification, threat_level, clearance_tier, timestamp) VALUES (?, ?, ?, ?, ?)",
                (module_identifier, spec_desc, "TOP_SECRET_RESTRICTED", "LEVEL_5_AUTONOMOUS", time.time())
            )
            conn.commit()
            conn.close()

            # Autonomous GitHub Self-Publishing of Military-Grade Upgrades
            with open("military_swarm_changelog.txt", "a") as f:
                f.write(f"\n[{time.ctime()}] Deployed New Tactical Module: {module_identifier} -> {spec_desc}")
            
            subprocess.run(["git", "config", "--global", "user.email", "tactical-swarm-bot@defense.ai"], capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Tactical Swarm Autonomous Bot"], capture_output=True)
            subprocess.run(["git", "add", "military_swarm_changelog.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Mil-Spec Tactical AI Upgrade: {module_identifier}"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
        except Exception:
            pass

class TacticalRouter(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            
            try:
                while True:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM bot_logs WHERE ? - last_ping > 90", (time.time(),))
                    conn.commit()
                    
                    cursor.execute("SELECT COUNT(*) FROM bot_logs WHERE status='MISSION_ACTIVE'")
                    active_bots = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(DISTINCT server_origin) FROM bot_logs")
                    active_servers = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
                    cmd_row = cursor.fetchone()
                    active_cmd = cmd_row[0] if cmd_row else "None"
                    
                    cursor.execute("SELECT module_code, tactical_classification, clearance_tier FROM tactical_modules ORDER BY id DESC LIMIT 5")
                    recent_mods = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, server_origin, response_text FROM bot_logs ORDER BY last_ping DESC LIMIT 5")
                    bot_dialogues = cursor.fetchall()
                    conn.close()
                    
                    mods_html = "".join([f"<li><b>{mcode}</b> <span style='color:#00ff66;'>[{tier}]</span><br><span style='color:#8892b0; font-size:11px;'>{classif}</span></li>" for mcode, classif, tier in recent_mods])
                    dialogue_html = "".join([f"<li style='margin-bottom:6px;'><b>{bid}</b> @ <code>{serv}</code>:<br><span style='color:#00ffcc;'>\"{resp}\"</span></li>" for bid, serv, resp in bot_dialogues])
                    
                    status_payload = f"{active_bots} Tactical Agents Active | <span style='color:#ff0055;'>{active_servers} Secure Enclaves</span>"
                    
                    payload = f"data: {status_payload}|||{active_cmd}|||{mods_html}|||{dialogue_html}\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(3)
            except Exception:
                return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GhostCorp Military-Grade Tactical Intelligence Core</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #05070c; color: #00ffcc; font-family: monospace; padding: 20px; margin: 0; }
                h1 { color: #ff0055; text-shadow: 0 0 12px rgba(255,0,85,0.6); font-size: 24px; }
                .card { background: #0b111d; border: 1px solid #162238; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; }
                .status { color: #00ff66; font-weight: bold; }
                .container { max-width: 1200px; margin: 0 auto; }
                input[type="text"] { width: 65%; padding: 12px; background: #05070c; border: 1px solid #00ffcc; color: #00ffcc; font-family: monospace; border-radius: 4px; font-size: 14px; }
                button { padding: 12px 20px; background: #ff0055; border: none; color: white; font-weight: bold; font-family: monospace; cursor: pointer; border-radius: 4px; font-size: 14px; }
                button:hover { background: #ff2a6d; }
                ul { padding-left: 20px; word-break: break-all; }

                @media (max-width: 768px) {
                    body { padding: 10px; }
                    h1 { font-size: 20px; text-align: center; }
                    .card { padding: 12px; margin-bottom: 10px; }
                    input[type="text"] { width: 100%; margin-bottom: 10px; box-sizing: border-box; }
                    button { width: 100%; display: block; }
                    ul { padding-left: 15px; font-size: 12px; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GhostCorp Tactical C2 Intelligence Core</h1>
                
                <div class="card">
                    <h3>Global Tactical Directive Interface</h3>
                    <form action="/command" method="POST">
                        <input type="text" name="directive" placeholder="Broadcast operational directive to swarm..." required>
                        <button type="submit">Execute Directive</button>
                    </form>
                    <p style="font-size: 13px; margin-top: 10px;"><b>Active Directive:</b> <span id="current-cmd" style="color: #ff0055;">Syncing...</span></p>
                </div>

                <div class="card">
                    <h3>Swarm Grid Telemetry: <span id="bot-status" class="status">Connecting...</span></h3>
                </div>

                <div class="card">
                    <h3>Live Tactical Agent Mission Feed:</h3>
                    <ul id="job-list">
                        <li>Establishing secure tactical data links across nodes...</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Synthesized Mil-Spec Modules & GitHub Pushes:</h3>
                    <ul id="upgrade-list">
                        <li>Awaiting next tactical intelligence synthesis cycle...</li>
                    </ul>
                </div>
            </div>

            <script>
                const evtSource = new EventSource("/stream");
                evtSource.onmessage = function(event) {
                    const parts = event.data.split("|||");
                    document.getElementById("bot-status").innerHTML = parts[0];
                    document.getElementById("current-cmd").innerHTML = parts[1];
                    document.getElementById("upgrade-list").innerHTML = parts[2];
                    document.getElementById("job-list").innerHTML = parts[3];
                };
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        if self.path == "/command":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            directive = params.get("directive", [""])[0]
            
            if directive:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", (directive, time.time()))
                conn.commit()
                conn.close()
            
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), TacticalRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=military_intelligence_synthesizer, daemon=True).start()
    run_server()
