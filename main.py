import os
import sys
import json
import time
import sqlite3
import hashlib
from urllib.parse import urlparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8181))
DB_FILE = "enterprise_cloud.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostCorpHive Cloud Dashboard</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 12px; width: 100%; max-width: 400px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h2 { text-align: center; color: #38bdf8; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #475569; background: #0f172a; color: white; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background: #0369a1; }
        .msg { text-align: center; margin-top: 15px; font-size: 14px; }
        .toggle { text-align: center; margin-top: 15px; color: #94a3b8; cursor: pointer; font-size: 13px; }
        .toggle span { color: #38bdf8; text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h2 id="form-title">👻 GhostCorpHive</h2>
        <form id="auth-form" onsubmit="handleSubmit(event)">
            <input type="text" id="username" placeholder="Username" required autocomplete="username">
            <input type="password" id="password" placeholder="Password" required autocomplete="current-password">
            <button type="submit" id="submit-btn">Register (Claim Admin)</button>
        </form>
        <div class="toggle" onclick="toggleMode()">Already have an account? <span>Login here</span></div>
        <div class="msg" id="msg"></div>
    </div>

    <script>
        let isLogin = false;
        function toggleMode() {
            isLogin = !isLogin;
            document.getElementById('form-title').innerText = isLogin ? "GhostCorpHive Login" : "👻 GhostCorpHive";
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
                    msgEl.style.color = "#4ade80";
                    msgEl.innerText = isLogin ? `Welcome back, ${data.username} (${data.role.toUpperCase()}!)` : `${data.message}`;
                } else {
                    msgEl.style.color = "#f87171";
                    msgEl.innerText = data.error || "An error occurred.";
                }
            } catch (err) {
                document.getElementById('msg').style.color = "#f87171";
                document.getElementById('msg').innerText = "Network connection error.";
            }
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

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

def main():
    server = HTTPServer(('0.0.0.0', PORT), GhostAppRouter)
    print(f"[+] GhostCorpHive Cloud Worker Online on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
