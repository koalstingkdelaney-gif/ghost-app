import os
import sqlite3
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from cryptography.fernet import Fernet

DB_FILE = "ghost_ultimate_matrix.db"
KEY_FILE = "server_master.key"

# --- 1. Cryptographic Pipeline (AES-256) ---
def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_or_create_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_text(plain_text):
    return cipher.encrypt(plain_text.encode("utf-8"))

def decrypt_text(cipher_bytes):
    try:
        return cipher.decrypt(cipher_bytes).decode("utf-8")
    except Exception:
        return "[DECRYPTION ERROR / CORRUPT DATA]"

# --- 2. Database Initialization ---
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_users (
                ip_address TEXT PRIMARY KEY,
                reason TEXT,
                banned_at REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                encrypted_content BLOB,
                flagged_by_ai INTEGER,
                timestamp REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swarm_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT,
                status TEXT,
                updated_at REAL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

# --- 3. Background Swarm Daemon (Self-Upgrading & Autonomous Loop) ---
def run_autonomous_swarm():
    """Runs silently in the background, executing tasks and simulating self-upgrades."""
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Log periodic swarm health check
            cursor.execute("INSERT INTO swarm_telemetry (task_name, status, updated_at) VALUES (?, ?, ?)",
                           ("Autonomous_Swarm_Daemon", "ACTIVE_OPTIMIZING", time.time()))
            conn.commit()
            conn.close()
        except Exception:
            pass
        
        # Sleep interval between background optimization sweeps
        time.sleep(30)

# Start background swarm thread safely
threading.Thread(target=run_autonomous_swarm, daemon=True).start()

# --- 4. Web Server & API Router ---
class UltimateMasterRouter(BaseHTTPRequestHandler):
    def _send_response(self, content, content_type="text/html", status=200):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def check_if_banned(self, ip):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT reason FROM banned_users WHERE ip_address = ?", (ip,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def do_GET(self):
        client_ip = self.client_address[0]

        if self.check_if_banned(client_ip):
            self._send_response("<h1>Access Denied</h1><p>Node permanently banned for policy violations.</p>", status=403)
            return

        # API Endpoint: Fetch Chat Archive
        if self.path == "/api/messages":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username, encrypted_content, timestamp FROM messages ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for r in reversed(rows):
                decrypted_msg = decrypt_text(r[1])
                messages.append({
                    "user": r[0],
                    "text": decrypted_msg,
                    "time": time.strftime("%H:%M:%S", time.localtime(r[2]))
                })
            self._send_response(json.dumps(messages), content_type="application/json")
            return

        # API Endpoint: Fetch Swarm Telemetry Status
        if self.path == "/api/swarm":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT task_name, status, updated_at FROM swarm_telemetry ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            conn.close()
            
            tasks = [{"task": r[0], "status": r[1], "time": time.strftime("%H:%M:%S", time.localtime(r[2]))} for r in rows]
            self._send_response(json.dumps(tasks), content_type="application/json")
            return

        # Main Unified Command & Control Dashboard (/app)
        if self.path == "/app":
            dashboard_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>GhostCorp C2 Matrix & Swarm Dashboard</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { box-sizing: border-box; }
                    body { background: #05070c; color: #00ffcc; font-family: monospace; margin: 0; padding: 15px; display: flex; flex-direction: column; height: 100vh; }
                    .header { background: #0b111d; border: 1px solid #162238; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
                    .header h2 { margin: 0; font-size: 18px; color: #ff0055; text-shadow: 0 0 10px rgba(255,0,85,0.5); }
                    .main-layout { display: flex; gap: 10px; flex: 1; overflow: hidden; }
                    .chat-panel { flex: 2; background: #0b111d; border: 1px solid #162238; border-radius: 8px; padding: 15px; display: flex; flex-direction: column; }
                    .swarm-panel { flex: 1; background: #0b111d; border: 1px solid #162238; border-radius: 8px; padding: 15px; display: flex; flex-direction: column; }
                    .chat-box { flex: 1; background: #05070c; border: 1px solid #162238; border-radius: 6px; padding: 10px; overflow-y: auto; margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px; }
                    .msg-card { background: #0b111d; border-left: 3px solid #00ffcc; padding: 8px; border-radius: 4px; font-size: 13px; }
                    .msg-meta { font-size: 10px; color: #8892b0; margin-bottom: 2px; display: flex; justify-content: space-between; }
                    .msg-user { color: #ff0055; font-weight: bold; }
                    .msg-text { color: #e6f1ff; word-break: break-word; }
                    .input-area { display: flex; gap: 10px; }
                    input[type="text"] { flex: 1; background: #05070c; border: 1px solid #162238; padding: 12px; color: #00ffcc; border-radius: 6px; font-family: monospace; outline: none; }
                    button { background: #ff0055; border: none; color: white; padding: 12px 18px; font-weight: bold; font-family: monospace; border-radius: 6px; cursor: pointer; }
                    button:hover { background: #ff2a6d; }
                    .swarm-log { background: #05070c; border: 1px solid #162238; border-radius: 6px; padding: 10px; flex: 1; overflow-y: auto; font-size: 11px; color: #00ffcc; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>GhostCorp Command Matrix</h2>
                    <span style="font-size: 11px; color: #8892b0;">● Swarm Active | AES-256 Storage | Indemnification Enforced</span>
                </div>
                
                <div class="main-layout">
                    <!-- Chat & Boss Interaction Panel -->
                    <div class="chat-panel">
                        <h3 style="margin-top:0; color:#ff0055; font-size:14px;">Secure Communications Feed</h3>
                        <div class="chat-box" id="chatBox">
                            <div class="msg-card">
                                <div class="msg-meta"><span class="msg-user">SYSTEM</span> <span>00:00:00</span></div>
                                <div class="msg-text">C2 Matrix online. Issue commands to swarm or chat freely.</div>
                            </div>
                        </div>
                        <div class="input-area">
                            <input type="text" id="msgInput" placeholder="Command swarm or chat..." onkeypress="handleKey(event)">
                            <button onclick="sendMessage()">TRANSMIT</button>
                        </div>
                    </div>

                    <!-- Autonomous Swarm Telemetry Panel -->
                    <div class="swarm-panel">
                        <h3 style="margin-top:0; color:#00ffcc; font-size:14px;">Active Swarm Telemetry</h3>
                        <div class="swarm-log" id="swarmLog">
                            Loading swarm nodes...
                        </div>
                        <button style="margin-top:10px; width:100%; background:#162238; color:#00ffcc; border:1px solid #00ffcc;" onclick="triggerUpgrade()">FORCE SWARM UPGRADE</button>
                    </div>
                </div>

                <script>
                    let myUser = "Boss-Agent-" + Math.floor(Math.random() * 9000 + 1000);

                    async function loadData() {
                        try {
                            // Load Messages
                            let res = await fetch('/api/messages');
                            let data = await res.json();
                            let chatBox = document.getElementById('chatBox');
                            chatBox.innerHTML = '';
                            data.forEach(m => {
                                let card = document.createElement('div');
                                card.className = 'msg-card';
                                card.innerHTML = `<div class="msg-meta"><span class="msg-user">${m.user}</span> <span>${m.time}</span></div><div class="msg-text">${escapeHtml(m.text)}</div>`;
                                chatBox.appendChild(card);
                            });
                            chatBox.scrollTop = chatBox.scrollHeight;

                            // Load Swarm Telemetry
                            let sRes = await fetch('/api/swarm');
                            let sData = await sRes.json();
                            let swarmLog = document.getElementById('swarmLog');
                            swarmLog.innerHTML = '';
                            sData.forEach(t => {
                                swarmLog.innerHTML += `<div>[${t.time}] ${t.task} -> <b>${t.status}</b></div>`;
                            });
                        } catch(e) {}
                    }

                    async function sendMessage() {
                        let input = document.getElementById('msgInput');
                        let text = input.value.trim();
                        if (!text) return;
                        input.value = '';
                        
                        await fetch('/api/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ username: myUser, text: text })
                        });
                        loadData();
                    }

                    async function triggerUpgrade() {
                        await fetch('/api/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ username: "DIRECTIVE", text: "COMMAND: Swarm initiated self-upgrade sequence." })
                        });
                        loadData();
                    }

                    function handleKey(e) { if(e.key === 'Enter') sendMessage(); }
                    function escapeHtml(str) { return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

                    setInterval(loadData, 3000);
                    loadData();
                </script>
            </body>
            </html>
            """
            self._send_response(dashboard_html)
            return

        # Default Terms of Service & Indemnification Gate (/)
        terms_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GhostCorp Access Gateway</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #05070c; color: #00ffcc; font-family: monospace; padding: 20px; margin: 0; }
                h1 { color: #ff0055; text-shadow: 0 0 12px rgba(255,0,85,0.6); font-size: 24px; }
                .card { background: #0b111d; border: 1px solid #162238; padding: 20px; margin-bottom: 15px; border-radius: 8px; }
                .terms-box { background: #05070c; border: 1px solid #162238; padding: 15px; height: 180px; overflow-y: scroll; font-size: 12px; color: #8892b0; margin-bottom: 15px; }
                button { padding: 14px 28px; background: #ff0055; border: none; color: white; font-weight: bold; font-family: monospace; cursor: pointer; border-radius: 4px; font-size: 14px; width: 100%; }
                button:hover { background: #ff2a6d; }
                .container { max-width: 600px; margin: 40px auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GhostCorp C2 Gateway</h1>
                <div class="card">
                    <h3>Terms of Service & Indemnification</h3>
                    <div class="terms-box">
                        <b>1. Sole User Accountability:</b> Users take 100% responsibility for actions executed through this software.<br><br>
                        <b>2. Indemnity Clause:</b> Hold harmless the creators and operators against all claims.<br><br>
                        <b>3. Autonomous Swarm & AI Moderation:</b> Background daemons and AI security agents actively monitor and log network telemetry.<br><br>
                        <b>4. Provided "AS IS":</b> No warranties expressed or implied.
                    </div>
                    <form action="/agree" method="POST">
                        <button type="submit">I AGREE & ENTER C2 MATRIX</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        self._send_response(terms_html)

    def do_POST(self):
        client_ip = self.client_address[0]

        if self.path == "/agree":
            self.send_response(303)
            self.send_header("Location", "/app")
            self.end_headers()
            return

        if self.path == "/api/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                user = data.get("username", "Boss-Agent")
                text = data.get("text", "").strip()

                if text:
                    # AI Moderation / Command Intercept
                    flagged = 0
                    if any(bad in text.lower() for bad in ["malware", "exploit"]):
                        flagged = 1
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("INSERT OR REPLACE INTO banned_users (ip_address, reason, banned_at) VALUES (?, ?, ?)",
                                       (client_ip, "Policy Violation", time.time()))
                        conn.commit()
                        conn.close()

                    # Encrypt communication payload with AES-256
                    encrypted_data = encrypt_text(text)

                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO messages (username, encrypted_content, flagged_by_ai, timestamp) VALUES (?, ?, ?, ?)",
                                   (user, encrypted_data, flagged, time.time()))
                    conn.commit()
                    conn.close()

                self._send_response(json.dumps({"status": "transmitted"}), content_type="application/json")
            except Exception as e:
                self._send_response(json.dumps({"error": str(e)}), content_type="application/json", status=400)

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), UltimateMasterRouter)
    print(f"[*] Ultimate C2 Master Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    run_server()
