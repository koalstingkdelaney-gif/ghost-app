import os
import sqlite3
import threading
import time
import urllib.parse
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
            bot_id INTEGER,
            job_name TEXT,
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
    # Set default command if table is empty
    cursor.execute("SELECT COUNT(*) FROM global_command")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", ("System Nominal: Awaiting User Directive", time.time()))
    conn.commit()
    conn.close()

def bot_worker(bot_id):
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            
            # Fetch the latest global user command
            cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            current_directive = row[0] if row else "Autonomous Operation"
            
            job_desc = f"Executing Directive: [{current_directive}]"
            
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, job_name, status, last_ping) VALUES (?, ?, ?, ?)",
                (bot_id, job_desc, "EXECUTING", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        
        time.sleep(40 + (bot_id % 20))

def launch_bot_swarm():
    print("[*] Initializing GhostCorp Swarm: Spawning command-responsive workers...")
    for i in range(1, 1601):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()

def self_upgrade_routine():
    upgrades_catalog = [
        ("Interactive C2 Link", "def c2_handler(): return 'Command channel open'"),
        ("Global Swarm Mesh", "def swarm_mesh(): return 'Directive broadcast active'"),
        ("Autonomous Task Injector", "def task_inject(): return 'Dynamic payload ready'"),
        ("Neural Telemetry Matrix", "def matrix_sync(): return 'All nodes synchronized'")
    ]
    counter = 0
    while True:
        time.sleep(300)
        counter += 1
        feature_name, snippet = upgrades_catalog[counter % len(upgrades_catalog)]
        unique_feature = f"{feature_name}_v{counter}"
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO upgrades (feature_name, code_snippet, status, timestamp) VALUES (?, ?, ?, ?)",
            (unique_feature, snippet, "DEPLOYED_AUTONOMOUSLY", time.time())
        )
        conn.commit()
        conn.close()

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
                    cursor.execute("SELECT COUNT(*) FROM bot_logs WHERE status='EXECUTING'")
                    active_bots = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
                    cmd_row = cursor.fetchone()
                    active_cmd = cmd_row[0] if cmd_row else "None"
                    
                    cursor.execute("SELECT feature_name, timestamp FROM upgrades ORDER BY id DESC LIMIT 5")
                    recent_upgrades = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, job_name FROM bot_logs ORDER BY last_ping DESC LIMIT 6")
                    active_jobs = cursor.fetchall()
                    conn.close()
                    
                    upgrades_html = "".join([f"<li><b>{feat}</b> (Synced: {ts})</li>" for feat, ts in recent_upgrades])
                    jobs_html = "".join([f"<li><b>Bot #{bid}</b>: <code>{jname}</code></li>" for bid, jname in active_jobs])
                    
                    payload = f"data: <span class='status'>{active_bots} Active</span>|||{active_cmd}|||{upgrades_html}|||{jobs_html}\n\n"
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
            <title>GhostCorp Command & Control Center</title>
            <style>
                body { background: #0b0f19; color: #00ffcc; font-family: monospace; padding: 20px; }
                h1 { color: #ff0055; text-shadow: 0 0 10px rgba(255,0,85,0.5); }
                .card { background: #131d31; border: 1px solid #1f293d; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
                .status { color: #00ff66; font-weight: bold; }
                input[type="text"] { width: 70%; padding: 10px; background: #0b0f19; border: 1px solid #00ffcc; color: #00ffcc; font-family: monospace; border-radius: 4px; }
                button { padding: 10px 20px; background: #ff0055; border: none; color: white; font-weight: bold; font-family: monospace; cursor: pointer; border-radius: 4px; }
                button:hover { background: #ff2a6d; }
                ul { padding-left: 20px; }
            </style>
        </head>
        <body>
            <h1>GhostCorp Autonomous Command Core</h1>
            
            <div class="card">
                <h3>Global Swarm Command Interface</h3>
                <form action="/command" method="POST">
                    <input type="text" name="directive" placeholder="Type a task/command for all bots (e.g., Scan Subnets, Deep Cache Clean)..." required>
                    <button type="submit">Broadcast Directive</button>
                </form>
                <p><b>Active Global Directive:</b> <span id="current-cmd" style="color: #ff0055;">Syncing...</span></p>
            </div>

            <div class="card">
                <h3>Swarm Telemetry: <span id="bot-status">Connecting...</span></h3>
            </div>

            <div class="card">
                <h3>Live Swarm Task Execution Feed:</h3>
                <ul id="job-list">
                    <li>Awaiting execution stream...</li>
                </ul>
            </div>

            <div class="card">
                <h3>Self-Generated Upgrades & Synthesized Modules:</h3>
                <ul id="upgrade-list">
                    <li>Awaiting next system evolution cycle...</li>
                </ul>
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
            
            # Redirect back to dashboard UI
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8181))
    server = HTTPServer(("0.0.0.0", port), AutonomousRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=self_upgrade_routine, daemon=True).start()
    run_server()
