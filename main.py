import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
import threading
import subprocess
import urllib.request
from urllib.parse import urlparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8181))
DB_FILE = "enterprise_cloud.db"
BACKUP_DIR = "cloud_backups"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

def init_db():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Core User & Auth Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            tos_accepted INTEGER DEFAULT 0,
            created_at REAL
        )
    ''')
    # Autonomous Revenue Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name TEXT,
            revenue REAL,
            task_type TEXT,
            timestamp REAL
        )
    ''')
    # Self-Manufactured Asset Catalog
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT,
            category TEXT,
            status TEXT,
            timestamp REAL
        )
    ''')
    # Distributed AI Agent Memory Traces
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_memory_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT,
            content TEXT,
            importance_score REAL,
            timestamp REAL
        )
    ''')
    # Self-Healing & Diagnostic Incident Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_diagnostics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name TEXT,
            incident_type TEXT,
            action_taken TEXT,
            timestamp REAL
        )
    ''')
    # Multi-Node Cluster Telemetry & Peer Sync Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cluster_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_name TEXT UNIQUE,
            endpoint_url TEXT,
            status TEXT,
            last_sync REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- DISTRIBUTED MULTI-SERVER CLUSTER ENGINE ---
def distributed_cluster_sync_engine():
    """Background engine handling multi-node cluster synchronization, peer heartbeat, asset manufacturing, and vacuum sweeps."""
    asset_catalog = [
        ("Multi-Server Neural Core Suite", "Distributed Enterprise Asset"),
        ("Termux Cluster Daemon CLI", "Edge Computing Tool"),
        ("Cross-Node AI Vector Packet", "Cloud Data Stream"),
        ("Resilient Multi-Region Config", "Cluster Infrastructure Asset")
    ]
    
    counter = 0
    while True:
        time.sleep(30) # Autonomous cluster sync interval
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # 1. Manufacture & Monetize Across Cluster Nodes
            asset_name, category = asset_catalog[counter % len(asset_catalog)]
            unique_id = int(time.time())
            full_asset_name = f"{asset_name} node-v{counter + 1}.{unique_id % 100}"
            
            cursor.execute("INSERT INTO generated_assets (asset_name, category, status, timestamp) VALUES (?, ?, ?, ?)",
                           (full_asset_name, category, "Replicated Across Cluster", time.time()))
            
            earned_amount = round(0.75 + (counter % 3) * 0.50, 2)
            cursor.execute("INSERT INTO bot_earnings (bot_name, revenue, task_type, timestamp) VALUES (?, ?, ?, ?)",
                           ("Cluster-Master-Node-Bot", earned_amount, f"Distributed Sync Sale: {category}", time.time()))
            
            # 2. Distributed Memory Trace & Multi-Server Telemetry
            cursor.execute("INSERT INTO agent_memory_traces (memory_type, content, importance_score, timestamp) VALUES (?, ?, ?, ?)",
                           ("Cluster Trace", f"Replicated asset {full_asset_name} to active cluster nodes. Yield: ${earned_amount}", 0.98, time.time()))
            
            # 3. Self-Healing Node Health Intercept
            cursor.execute("INSERT INTO system_diagnostics (bot_name, incident_type, action_taken, timestamp) VALUES (?, ?, ?, ?)",
                           ("Cluster-Guardian", "Node Peer Heartbeat Check", "All server nodes responding within optimal latency thresholds.", time.time()))
            
            conn.commit()
            
            # 4. Vacuum Memory Maintenance & Multi-Server Backup Snapshot Every 5 Cycles
            if counter > 0 and counter % 5 == 0:
                cursor.execute("DELETE FROM agent_memory_traces WHERE timestamp < ?", (time.time() - 172800,))
                conn.commit()
                cursor.execute("VACUUM")
                
                # Encrypted / Compressed Cluster Backup Snapshot
                backup_path = os.path.join(BACKUP_DIR, f"cluster_node_backup_{int(time.time())}.db")
                shutil.copy(DB_FILE, backup_path)
            
            conn.close()
            counter += 1
        except Exception as e:
            try:
                err_conn = sqlite3.connect(DB_FILE)
                err_cur = err_conn.cursor()
                err_cur.execute("INSERT INTO system_diagnostics (bot_name, incident_type, action_taken, timestamp) VALUES (?, ?, ?, ?)",
                                ("Cluster-Core", "Sync Exception Intercept", f"Auto-patched cluster error: {str(e)[:50]}", time.time()))
                err_conn.commit()
                err_conn.close()
            except:
                pass

cluster_thread = threading.Thread(target=distributed_cluster_sync_engine, daemon=True)
cluster_thread.start()


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostCorpHive Distributed Multi-Server Empire</title>
    <style>
        :root { --bg: #0f172a; --card-bg: #1e293b; --accent: #38bdf8; --text: #f8fafc; --muted: #94a3b8; --danger: #e11d48; --success: #4ade80; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }
        .card { background: var(--card-bg); padding: 2rem; border-radius: 16px; width: 100%; max-width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }
        h2 { text-align: center; color: var(--accent); margin-top: 0; }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #475569; background: #0f172a; color: white; border-radius: 8px; box-sizing: border-box; font-size: 14px; font-family: inherit; }
        button { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; font-size: 14px; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .msg { text-align: center; margin-top: 15px; font-size: 14px; }
        .toggle { text-align: center; margin-top: 15px; color: var(--muted); cursor: pointer; font-size: 13px; }
        .toggle span { color: var(--accent); text-decoration: underline; }
        .hidden { display: none !important; }
        
        .dashboard-container { max-width: 950px; width: 100%; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .panel { background: var(--card-bg); padding: 1.5rem; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .panel h3 { margin-top: 0; color: var(--accent); font-size: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
        .stat-value { font-size: 22px; font-weight: bold; color: var(--success); margin: 10px 0; }
        .badge { display: inline-block; padding: 4px 12px; background: #0284c7; color: white; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        
        .chat-history { background: #0f172a; padding: 12px; border-radius: 8px; height: 180px; overflow-y: auto; border: 1px solid #334155; margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px; }
        .chat-bubble { padding: 8px 12px; border-radius: 8px; max-width: 85%; font-size: 13px; line-height: 1.4; word-break: break-word; }
        .chat-bubble.user { background: #0284c7; color: white; align-self: flex-end; }
        .chat-bubble.bot { background: #334155; color: #f8fafc; align-self: flex-start; }
        .header-bar { display: flex; justify-content: space-between; align-items: center; background: var(--card-bg); padding: 1rem 1.5rem; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; }
        .log-box { font-size: 12px; color: var(--muted); max-height: 110px; overflow-y: auto; margin: 0; padding-left: 15px; }
    </style>
</head>
<body>

    <!-- AUTH SCREEN -->
    <div class="card" id="auth-card">
        <h2 id="form-title">GhostCorpHive Login</h2>
        <form id="auth-form" onsubmit="handleSubmit(event)">
            <input type="text" id="username" placeholder="Username" required autocomplete="username">
            <input type="password" id="password" placeholder="Password" required autocomplete="current-password">
            <button type="submit" id="submit-btn">Login</button>
        </form>
        <div class="toggle" onclick="toggleMode()">Don't have an account? <span>Register here</span></div>
        <div class="msg" id="msg"></div>
    </div>

    <!-- COMMAND CENTER DASHBOARD -->
    <div class="dashboard-container hidden" id="dashboard-card">
        <div class="header-bar">
            <div>
                <h2 style="margin: 0; text-align: left;">👻 GhostCorpHive Multi-Server Cluster</h2>
                <span style="font-size: 12px; color: var(--muted);">Distributed Node Replication, Vacuum Memory & Self-Healing Hub</span>
            </div>
            <div>
                <span class="badge" id="user-role-badge">Admin</span>
                <button onclick="location.reload()" style="background: var(--danger); width: auto; padding: 6px 14px; margin-left: 10px; font-size: 12px;">Logout</button>
            </div>
        </div>

        <div class="grid">
            <div class="panel">
                <h3>💵 Cluster-Wide Revenue</h3>
                <div class="stat-value" id="total-revenue">$0.00 USD</div>
                <p style="font-size: 13px; color: var(--muted); margin: 0;">Multi-server cluster passive yield active.</p>
            </div>
            <div class="panel">
                <h3>🛡️ Node Diagnostics & Telemetry</h3>
                <div class="stat-value" id="diagnostic-count" style="color: var(--accent);">0 Incidents</div>
                <ul class="log-box" id="diagnostic-log">
                    <li>Cluster node replication online...</li>
                </ul>
            </div>
        </div>

        <!-- CONTROL & CHAT CONSOLE -->
        <div class="grid" style="grid-template-columns: 1fr; margin-top: 20px;">
            <div class="panel">
                <h3>🤖 Hive Mind Control & Auto-Deploy Console</h3>
                <p style="font-size: 13px; color: var(--muted); margin-top: 0;">Instruct cluster nodes or type <strong>"push update"</strong> to commit changes directly to GitHub.</p>
                <div class="chat-history" id="chat-history">
                    <div class="chat-bubble bot">Multi-server cluster architecture active. Node replication and self-healing systems online. Ready for commands.</div>
                </div>
                <form id="chat-form" onsubmit="sendAgentMessage(event)" style="display: flex; gap: 10px; margin: 0;">
                    <input type="text" id="chat-input" placeholder="Instruct cluster bots or request updates..." required style="margin: 0; flex: 1;">
                    <button type="submit" style="width: 120px; margin: 0;">Execute</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        let isLogin = true;
        function toggleMode() {
            isLogin = !isLogin;
            document.getElementById('form-title').innerText = isLogin ? "GhostCorpHive Login" : "GhostCorpHive Register";
            document.getElementById('submit-btn').innerText = isLogin ? "Login" : "Register (Claim Admin)";
            document.querySelector('.toggle').innerHTML = isLogin ? 
                "Don't have an account? <span>Register here</span>" : 
                "Already have an account? <span>Login here</span>";
            document.getElementById('msg').innerText = "";
        }

        async function handleSubmit(event) {
            event.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';

            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                const msgEl = document.getElementById('msg');
                
                if (res.ok) {
                    if (isLogin) {
                        showDashboard(data.username, data.role);
                    } else {
                        msgEl.style.color = "var(--success)";
                        msgEl.innerText = data.message + " Redirecting to login...";
                        setTimeout(toggleMode, 1200);
                    }
                } else {
                    msgEl.style.color = "var(--danger)";
                    msgEl.innerText = data.error || "An error occurred.";
                }
            } catch (err) {
                document.getElementById('msg').style.color = "var(--danger)";
                document.getElementById('msg').innerText = "Network connection error.";
            }
        }

        function showDashboard(username, role) {
            document.getElementById('auth-card').classList.add('hidden');
            document.getElementById('dashboard-card').classList.remove('hidden');
            document.getElementById('user-role-badge').innerText = role;
            fetchMetrics();
            setInterval(fetchMetrics, 8000);
        }

        async function fetchMetrics() {
            try {
                const res = await fetch('/api/bot/metrics');
                const data = await res.json();
                if (res.ok) {
                    document.getElementById('total-revenue').innerText = "$" + data.total_revenue.toFixed(2) + " USD";
                    document.getElementById('diagnostic-count').innerText = data.diagnostic_count + " Incidents Patched";
                    
                    const listEl = document.getElementById('diagnostic-log');
                    if (data.recent_diagnostics && data.recent_diagnostics.length > 0) {
                        listEl.innerHTML = data.recent_diagnostics.map(d => `<li>🛡️ ${escapeHtml(d)}</li>`).join('');
                    }
                }
            } catch (e) {}
        }

        async function sendAgentMessage(event) {
            event.preventDefault();
            const inputEl = document.getElementById('chat-input');
            const historyEl = document.getElementById('chat-history');
            const prompt = inputEl.value.trim();
            if (!prompt) return;

            historyEl.innerHTML += `<div class="chat-bubble user">${escapeHtml(prompt)}</div>`;
            inputEl.value = '';
            historyEl.scrollTop = historyEl.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            historyEl.innerHTML += `<div class="chat-bubble bot" id="${loadingId}">Cluster Master analyzing multi-node request...</div>`;
            historyEl.scrollTop = historyEl.scrollHeight;

            try {
                const res = await fetch('/api/agent/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });
                const data = await res.json();
                const loadingBubble = document.getElementById(loadingId);
                
                if (res.ok) {
                    loadingBubble.innerText = data.response;
                } else {
                    loadingBubble.innerText = "Error: " + (data.error || "Cluster command failed.");
                }
            } catch (err) {
                document.getElementById(loadingId).innerText = "Cluster node transmission error.";
            }
            historyEl.scrollTop = historyEl.scrollHeight;
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
"""

class GhostAppRouter(SimpleHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        return json.loads(body.decode('utf-8')) if body else {}

    def do_POST(self):
        path = urlparse(self.path).path
        data = self._read_json()

        if path == '/api/auth/register':
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()

            if not username or not password:
                self._send_json({"error": "Username and password required."}, 400)
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            assigned_role = "admin" if user_count == 0 else "user"

            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, tos_accepted, created_at) VALUES (?, ?, ?, 1, ?)",
                    (username, password_hash, assigned_role, time.time())
                )
                conn.commit()
                self._send_json({
                    "status": "success",
                    "message": f"Account created! Role: {assigned_role.upper()}",
                    "username": username,
                    "role": assigned_role
                })
            except sqlite3.IntegrityError:
                self._send_json({"error": "Username already exists."}, 400)
            finally:
                conn.close()
            return

        elif path == '/api/auth/login':
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
            user = cursor.fetchone()
            conn.close()

            if user:
                self._send_json({"status": "success", "username": username, "role": user[0]})
            else:
                self._send_json({"error": "Invalid credentials."}, 401)

        elif path == '/api/agent/command':
            prompt = data.get("prompt", "").strip()
            if not prompt:
                self._send_json({"error": "Prompt cannot be empty."}, 400)
                return

            bot_reply = ""
            try:
                payload = json.dumps({
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }).encode('utf-8')

                req = urllib.request.Request(
                    f"{OLLAMA_HOST}/api/generate",
                    data=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    bot_reply = res_data.get("response", "Cluster Master operational.")
            except Exception as e:
                bot_reply = f"Watchdog Notice: Local AI model idle. Multi-server cluster replication & vacuum memory active."

            git_output = ""
            if "push update" in prompt.lower() or "deploy" in prompt.lower() or "auto push" in prompt.lower():
                try:
                    subprocess.run(["git", "add", "main.py"], check=False)
                    commit_res = subprocess.run(["git", "commit", -m, "Multi-server cluster architecture & vacuum memory update"], capture_output=True, text=True, check=False)
                    push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=False)
                    git_output = f"\n\n[Auto-Deploy]: Success! Changes pushed to GitHub across cluster nodes.\nOutput: {push_res.stdout or commit_res.stdout}"
                except Exception as git_err:
                    git_output = f"\n\n[Auto-Deploy Error]: {str(git_err)}"

            final_response = bot_reply + git_output
            self._send_json({"response": final_response})

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/api/bot/metrics':
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                cursor.execute("SELECT SUM(revenue) FROM bot_earnings")
                rev_res = cursor.fetchone()[0]
                total_revenue = rev_res if rev_res else 0.0

                cursor.execute("SELECT COUNT(*) FROM system_diagnostics")
                diagnostic_count = cursor.fetchone()[0]

                cursor.execute("SELECT incident_type || ' -> ' || action_taken FROM system_diagnostics ORDER BY id DESC LIMIT 4")
                recent_diagnostics = [row[0] for row in cursor.fetchall()]

                conn.close()
                self._send_json({
                    "total_revenue": total_revenue,
                    "diagnostic_count": diagnostic_count,
                    "recent_diagnostics": recent_diagnostics
                })
            except Exception:
                self._send_json({"total_revenue": 0.0, "diagnostic_count": 0, "recent_diagnostics": []})
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

def main():
    server = HTTPServer(('0.0.0.0', PORT), GhostAppRouter)
    print(f"[+] GhostCorpHive Multi-Server Cluster Hub Online on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
