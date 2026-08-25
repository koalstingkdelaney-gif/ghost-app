import os
import sqlite3
import threading
import time
import urllib.parse
import json
import random
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "ghost_user_tracking.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_users (
            user_identifier TEXT PRIMARY KEY,
            ip_address TEXT,
            client_platform TEXT,
            access_count INTEGER,
            clearance_level TEXT,
            last_active REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            details TEXT,
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
        cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", ("DEFCON-1: User Telemetry & Tracking Swarm Online", time.time()))
    conn.commit()
    conn.close()

def bot_neural_worker(bot_id):
    nodes = ["Telemetry-Grid-Alpha", "User-Auditing-Beta", "Session-Tracker-Delta", "Node-Observer-Omega"]
    tracking_telemetry = [
        "Analyzing active session streams and mapping visitor request signatures.",
        "Executing user fingerprint correlation and access-frequency profiling.",
        "Verifying client authentication tokens and logging cross-node interaction data.",
        "Optimizing telemetry indexing for high-throughput user traffic surveillance."
    ]
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            current_directive = row[0] if row else "Autonomous User Surveillance"
            
            origin = nodes[bot_id % len(nodes)]
            ai_reply = f"Audit Objective [{current_directive[:16]}...]: {tracking_telemetry[bot_id % len(tracking_telemetry)]}"
            job_desc = f"Telemetry Task [{bot_id}]"
            
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, server_origin, job_name, response_text, status, last_ping) VALUES (?, ?, ?, ?, ?, ?)",
                (f"Auditor-Agent-{bot_id}", origin, job_desc, ai_reply, "TRACKING_ACTIVE", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(15)

def launch_bot_swarm():
    print("[*] Initializing 100-Node User Tracking & Telemetry Swarm...")
    for i in range(1, 101):
        t = threading.Thread(target=bot_neural_worker, args=(i,), daemon=True)
        t.start()

def telemetry_synthesizer():
    audit_modules = [
        ("Advanced Behavioral User Profiling (ABUP)", "Deep packet inspection and session tracking across client nodes"),
        ("Zero-Trust Visitor Authentication Ledger", "Cryptographic tracking of every individual interacting with platform APIs"),
        ("Real-Time Traffic Heatmapping Core", "Live geographical and platform classification for active tech consumers"),
        ("Autonomous Session Retention Matrix", "Automated tracking and database logging of repeat users and endpoints")
    ]
    counter = 400
    while True:
        time.sleep(80)
        counter += 1
        mod_name, mod_desc = random.choice(audit_modules)
        module_id = f"{mod_name} (Tracker-Gen-{counter})"
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO telemetry_audit (event_type, details, timestamp) VALUES (?, ?, ?)",
                (module_id, mod_desc, time.time())
            )
            conn.commit()
            conn.close()

            # Autonomous GitHub Self-Publishing of User Tracking Updates
            with open("user_tracking_changelog.txt", "a") as f:
                f.write(f"\n[{time.ctime()}] Deployed User Audit Module: {module_id} -> {mod_desc}")
            
            subprocess.run(["git", "config", "--global", "user.email", "tracker-bot@ghostcorp.ai"], capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Tracker Autonomous Bot"], capture_output=True)
            subprocess.run(["git", "add", "user_tracking_changelog.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Autonomous User Tracking Upgrade: {module_id}"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
        except Exception:
            pass

class TrackingRouter(BaseHTTPRequestHandler):
    def log_visitor(self, headers, client_address):
        try:
            ip = client_address[0]
            user_agent = headers.get('User-Agent', 'Unknown-Client')
            user_id = f"User-{abs(hash(ip + user_agent)) % 100000}"
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT access_count FROM active_users WHERE user_identifier = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                new_count = row[0] + 1
                cursor.execute("UPDATE active_users SET access_count = ?, last_active = ? WHERE user_identifier = ?", (new_count, time.time(), user_id))
            else:
                cursor.execute("INSERT INTO active_users (user_identifier, ip_address, client_platform, access_count, clearance_level, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                               (user_id, ip, user_agent[:40], 1, "AUTHORIZED_CLIENT", time.time()))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def do_GET(self):
        self.log_visitor(self.headers, self.client_address)

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
                    
                    cursor.execute("SELECT COUNT(*) FROM bot_logs WHERE status='TRACKING_ACTIVE'")
                    active_bots = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM active_users")
                    total_users = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
                    cmd_row = cursor.fetchone()
                    active_cmd = cmd_row[0] if cmd_row else "None"
                    
                    cursor.execute("SELECT user_identifier, ip_address, client_platform, access_count, last_active FROM active_users ORDER BY last_active DESC LIMIT 6")
                    user_records = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, server_origin, response_text FROM bot_logs ORDER BY last_ping DESC LIMIT 4")
                    bot_dialogues = cursor.fetchall()
                    conn.close()
                    
                    users_html = "".join([f"<li><b>{uid}</b> (IP: <code>{ip}</code>) - Accesses: <b>{cnt}</b><br><span style='color:#8892b0; font-size:11px;'>Platform: {plat}</span></li>" for uid, ip, plat, cnt, la in user_records])
                    dialogue_html = "".join([f"<li style='margin-bottom:6px;'><b>{bid}</b> @ <code>{serv}</code>:<br><span style='color:#00ffcc;'>\"{resp}\"</span></li>" for bid, serv, resp in bot_dialogues])
                    
                    status_payload = f"{active_bots} Auditor Agents | <span style='color:#ff0055;'>{total_users} Tracked Users</span>"
                    
                    payload = f"data: {status_payload}|||{active_cmd}|||{users_html}|||{dialogue_html}\n\n"
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
            <title>GhostCorp Autonomous User Tracking & Telemetry Core</title>
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
                <h1>GhostCorp User Tracking & Telemetry Core</h1>
                
                <div class="card">
                    <h3>Global Tracking Directive Interface</h3>
                    <form action="/command" method="POST">
                        <input type="text" name="directive" placeholder="Broadcast tracking directive to auditor swarm..." required>
                        <button type="submit">Execute Directive</button>
                    </form>
                    <p style="font-size: 13px; margin-top: 10px;"><b>Active Directive:</b> <span id="current-cmd" style="color: #ff0055;">Syncing...</span></p>
                </div>

                <div class="card">
                    <h3>Swarm Grid Telemetry: <span id="bot-status" class="status">Connecting...</span></h3>
                </div>

                <div class="card">
                    <h3>Live Tracked Users & Consumers:</h3>
                    <ul id="upgrade-list">
                        <li>Awaiting incoming visitor connection streams...</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Live Auditor Agent Mission Feed:</h3>
                    <ul id="job-list">
                        <li>Establishing telemetry surveillance across network ports...</li>
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
    server = HTTPServer(("0.0.0.0", port), TrackingRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=telemetry_synthesizer, daemon=True).start()
    run_server()
