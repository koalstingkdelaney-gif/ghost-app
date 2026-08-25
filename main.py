import os
import sqlite3
import threading
import time
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
            status TEXT,
            last_ping REAL
        )
    ''')
    conn.commit()
    conn.close()

def bot_worker(bot_id):
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, status, last_ping) VALUES (?, ?, ?)",
                (bot_id, "ACTIVE", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(60)

def launch_bot_swarm():
    print("[*] Initializing GhostCorp Swarm: Spawning 565 autonomous bots...")
    for i in range(1, 566):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()

def self_upgrade_routine():
    upgrades_catalog = [
        ("Auto-Optimizer", "def optimized_path(): return 'Speed increased'"),
        ("Predictive Caching", "def cache_handler(): return 'Memory optimized'"),
        ("Neural Telemetry", "def telemetry_pulse(): return 'Swarm nominal'"),
        ("Dynamic Route Injector", "def dynamic_route(): return 'Endpoint online'")
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
        # Endpoint for real-time data stream
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
                    cursor.execute("SELECT COUNT(*) FROM bot_logs WHERE status='ACTIVE'")
                    active_bots = cursor.fetchone()[0]
                    cursor.execute("SELECT feature_name, timestamp FROM upgrades ORDER BY id DESC LIMIT 5")
                    recent_upgrades = cursor.fetchall()
                    conn.close()
                    
                    upgrades_html = "".join([f"<li><b>{feat}</b> (Synced: {ts})</li>" for feat, ts in recent_upgrades])
                    
                    payload = f"data: <span class='status'>{active_bots} / 565 Bots Active</span>|||{upgrades_html}\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(3) # Pushes updates every 3 seconds seamlessly
            except Exception:
                return

        # Main HTML Dashboard UI
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
            </style>
        </head>
        <body>
            <h1>GhostCorp Autonomous Cloud Core</h1>
            <div class="card">
                <h3>Swarm Status: <span id="bot-status">Connecting to swarm...</span></h3>
                <p>Cloud architecture is self-sustaining, tracking, and upgrading in real time.</p>
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
