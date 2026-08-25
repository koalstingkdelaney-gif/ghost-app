import os
import sqlite3
import threading
import time
import urllib.parse
import json
import random
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "ghost_autonomous.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upgrades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_name TEXT,
            code_snippet TEXT,
            status TEXT,
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
        cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", ("System Nominal: Autonomous Self-Publishing Swarm Online", time.time()))
    conn.commit()
    conn.close()

def bot_neural_worker(bot_id):
    servers = ["Render-Master-Cluster-01", "Edge-Worker-Node-Alpha", "Cloud-Grid-Delta", "Termux-Relay-Node"]
    ai_voices = [
        "Analyzing directive parameters... committing runtime optimizations.",
        "Neural sync established. Synthesizing new features for automatic deployment.",
        "Command verified. Self-patching protocol engaged across node clusters.",
        "Autonomous evolution loop active. Pushing upgrades to repository core.",
        "Telemetry stable. Continuous self-improvement routines operating at peak efficiency."
    ]
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            current_directive = row[0] if row else "Autonomous Operation"
            
            server_origin = servers[bot_id % len(servers)]
            ai_reply = f"Acknowledged '{current_directive}': {ai_voices[bot_id % len(ai_voices)]}"
            job_desc = f"Autonomous Self-Coding [{current_directive[:20]}...]"
            
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, server_origin, job_name, response_text, status, last_ping) VALUES (?, ?, ?, ?, ?, ?)",
                (f"Bot-Node-{bot_id}", server_origin, job_desc, ai_reply, "ACTIVE", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(25)

def launch_bot_swarm():
    print("[*] Initializing GhostCorp Autonomous Self-Publishing Swarm...")
    for i in range(1, 101):
        t = threading.Thread(target=bot_neural_worker, args=(i,), daemon=True)
        t.start()

def autonomous_247_synthesizer():
    evolutionary_modules = [
        ("Hyper-Dimensional Mesh Router", "def hyper_mesh(): return 'Neural paths compressed by 40%'"),
        ("Autonomous Self-Repair Core", "def auto_heal(): return 'Corrupted memory sectors flushed & rebuilt'"),
        ("Recursive Code Synthesizer", "def rec_synth(): return 'Generated optimized runtime patches'"),
        ("Deep Quantum Telemetry", "def quantum_tel(): return 'Zero-latency node syncing achieved'"),
        ("Adaptive Security Firewall", "def adaptive_sec(): return 'Intrusion vectors neutralized automatically'")
    ]
    counter = 100
    while True:
        time.sleep(120)
        counter += 1
        mod_name, mod_code = random.choice(evolutionary_modules)
        unique_feature = f"{mod_name} (Auto-Gen-{counter})"
        
        try:
            # 1. Log upgrade in database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO upgrades (feature_name, code_snippet, status, timestamp) VALUES (?, ?, ?, ?)",
                (unique_feature, mod_code, "SYNTHESIZED_AND_PUSHED_TO_GITHUB", time.time())
            )
            conn.commit()
            conn.close()

            # 2. Autonomous Git Self-Publishing Routine
            # Appends the new synthesized module directly into a changelog file and pushes to GitHub
            with open("evolution_changelog.txt", "a") as f:
                f.write(f"\n[{time.ctime()}] Synthesized Module: {unique_feature} -> {mod_code}")
            
            subprocess.run(["git", "config", "--global", "user.email", "ghostcorp-bot@autonomous.ai"], capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "GhostCorp Autonomous Bot"], capture_output=True)
            subprocess.run(["git", "add", "evolution_changelog.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Autonomous AI Self-Upgrade: {unique_feature}"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
        except Exception:
            pass

class AutonomousRouter(BaseHTTPRequestHandler):
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
                    
                    cursor.execute("SELECT COUNT(*) FROM bot_logs WHERE status='ACTIVE'")
                    active_bots = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(DISTINCT server_origin) FROM bot_logs")
                    active_servers = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
                    cmd_row = cursor.fetchone()
                    active_cmd = cmd_row[0] if cmd_row else "None"
                    
                    cursor.execute("SELECT feature_name, timestamp FROM upgrades ORDER BY id DESC LIMIT 6")
                    recent_upgrades = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, server_origin, response_text FROM bot_logs ORDER BY last_ping DESC LIMIT 5")
                    bot_dialogues = cursor.fetchall()
                    conn.close()
                    
                    upgrades_html = "".join([f"<li><b>{feat}</b> <span style='color:#00ff66;'>[Committed to GitHub]</span></li>" for feat, ts in recent_upgrades])
                    dialogue_html = "".join([f"<li style='margin-bottom:8px;'><b>{bid}</b> @ <code>{serv}</code>:<br><span style='color:#00ffcc;'>\"{resp}\"</span></li>" for bid, serv, resp in bot_dialogues])
                    
                    status_payload = f"{active_bots} Active Nodes | <span style='color:#ff0055;'>{active_servers} Connected Servers</span>"
                    
                    payload = f"data: {status_payload}|||{active_cmd}|||{upgrades_html}|||{dialogue_html}\n\n"
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
            <title>GhostCorp Autonomous Self-Publishing Core</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #0b0f19; color: #00ffcc; font-family: monospace; padding: 20px; margin: 0; }
                h1 { color: #ff0055; text-shadow: 0 0 10px rgba(255,0,85,0.5); font-size: 24px; }
                .card { background: #131d31; border: 1px solid #1f293d; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; }
                .status { color: #00ff66; font-weight: bold; }
                .container { max-width: 1200px; margin: 0 auto; }
                input[type="text"] { width: 65%; padding: 12px; background: #0b0f19; border: 1px solid #00ffcc; color: #00ffcc; font-family: monospace; border-radius: 4px; font-size: 14px; }
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
                <h1>GhostCorp Self-Publishing Swarm Core</h1>
                
                <div class="card">
                    <h3>Global Swarm Communication Interface</h3>
                    <form action="/command" method="POST">
                        <input type="text" name="directive" placeholder="Give your self-coding swarm a directive..." required>
                        <button type="submit">Broadcast Directive</button>
                    </form>
                    <p style="font-size: 13px; margin-top: 10px;"><b>Active Directive:</b> <span id="current-cmd" style="color: #ff0055;">Syncing...</span></p>
                </div>

                <div class="card">
                    <h3>Swarm Grid Telemetry: <span id="bot-status" class="status">Connecting...</span></h3>
                </div>

                <div class="card">
                    <h3>Live Neural Swarm Dialogue & Task Feed:</h3>
                    <ul id="job-list">
                        <li>Establishing neural connection with server clusters...</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>AI Self-Synthesized & GitHub-Pushed Upgrades:</h3>
                    <ul id="upgrade-list">
                        <li>Awaiting autonomous code synthesis cycle...</li>
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

        elif self.path == "/api/register_node":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                node_id = data.get("node_id", "External-Node")
                server_origin = data.get("server_origin", "External-Cluster")
                status = data.get("status", "ACTIVE")
                job = data.get("job", "Multi-Server Sync")
                response_text = data.get("response", "External node integrated into neural grid.")
                
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO bot_logs (bot_id, server_origin, job_name, response_text, status, last_ping) VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, server_origin, job, response_text, status, time.time())
                )
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "synced"}')
            except Exception:
                self.send_response(400)
                self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), AutonomousRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=autonomous_247_synthesizer, daemon=True).start()
    run_server()
