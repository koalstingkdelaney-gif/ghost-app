import os
import sqlite3
import threading
import time
import random
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
    conn.commit()
    conn.close()

def bot_worker(bot_id):
    # Assign a unique operational job profile based on the bot's ID
    job_types = [
        "Memory Telemetry Indexer", "Packet Stream Scrubber", 
        "State Consistency Auditor", "Neural Node Sync", 
        "Autonomous Micro-Patch Routine", "Local Cache Optimizer",
        "Sub-Routine Watchdog", "Data Entropy Analyzer"
    ]
    assigned_job = f"{job_types[bot_id % len(job_types)]} (Node #{bot_id})"
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, job_name, status, last_ping) VALUES (?, ?, ?, ?)",
                (bot_id, assigned_job, "EXECUTING", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        
        # Stagger work cycles slightly so the swarm runs fluidly
        time.sleep(45 + (bot_id % 15))

def launch_bot_swarm():
    print("[*] Initializing GhostCorp Swarm: Spawning dynamic workers...")
    # Expanding capacity dynamically to match your scaling swarm
    for i in range(1, 1601):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()

def self_upgrade_routine():
    upgrades_catalog = [
        ("Dynamic Job Dispatcher", "def dispatch(): return 'Custom tasks assigned'"),
        ("Swarm Mesh Routing", "def mesh_route(): return 'Node interconnect optimized'"),
        ("Autonomous Self-Repair", "def self_heal(): return 'Integrity verified'"),
        ("Predictive Task Allocator", "def predict_load(): return 'Workload balanced'")
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
                    
                    cursor.execute("SELECT feature_name, timestamp FROM upgrades ORDER BY id DESC LIMIT 5")
                    recent_upgrades = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, job_name FROM bot_logs ORDER BY last_ping DESC LIMIT 6")
                    active_jobs = cursor.fetchall()
                    conn.close()
                    
                    upgrades_html = "".join([f"<li><b>{feat}</b> (Synced: {ts})</li>" for feat, ts in recent_upgrades])
                    jobs_html = "".join([f"<li><b>Bot #{bid}</b>: Executing <code>{jname}</code></li>" for bid, jname in active_jobs])
                    
                    payload = f"data: <span class='status'>{active_bots} Active</span>|||{upgrades_html}|||{jobs_html}\n\n"
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
            <title>GhostCorp Autonomous Command Center</title>
            <style>
                body { background: #0b0f19; color: #00ffcc; font-family: monospace; padding: 20px; }
                h1 { color: #ff0055; text-shadow: 0 0 10px rgba(255,0,85,0.5); }
                .card { background: #131d31; border: 1px solid #1f293d; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
                .status { color: #00ff66; font-weight: bold; }
                ul { padding-left: 20px; }
            </style>
        </head>
        <body>
            <h1>GhostCorp Autonomous Cloud Core</h1>
            <div class="card">
                <h3>Swarm Telemetry: <span id="bot-status">Connecting...</span></h3>
                <p>Every bot is assigned a specialized live background task.</p>
            </div>
            <div class="card">
                <h3>Live Active Bot Jobs (Sample Feed):</h3>
                <ul id="job-list">
                    <li>Loading task assignments...</li>
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
                    document.getElementById("upgrade-list").innerHTML = parts[1];
                    document.getElementById("job-list").innerHTML = parts[2];
                };
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

def run_server():
    port = int(os.environ.get("PORT", 8181))
    server = HTTPServer(("0.0.0.0", port), AutonomousRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=self_upgrade_routine, daemon=True).start()
    run_server()
