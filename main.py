import os
import sys
import json
import time
import sqlite3
import hashlib
from urllib.parse import urlparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))
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
        CREATE TABLE IF NOT EXISTS banned_ips (
            ip_address TEXT PRIMARY KEY,
            reason TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class CloudApplicationRouter(SimpleHTTPRequestHandler):
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

    def get_client_ip(self):
        x_forwarded = self.headers.get('X-Forwarded-For')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return self.client_address[0]

    def do_POST(self):
        client_ip = self.get_client_ip()
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
                    "message": f"Account created. Assigned role: {assigned_role}",
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
        self.wfile.write(b"<h1>Ghost Enterprise Cloud Application Online</h1><p>Public Node Active.</p>")

def main():
    server = HTTPServer(('0.0.0.0', PORT), CloudApplicationRouter)
    print(f"[+] Ghost Cloud Server listening on 0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
