import os
import sqlite3
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "ghost_indemnity.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_users (
                user_identifier TEXT PRIMARY KEY,
                ip_address TEXT,
                client_platform TEXT,
                indemnity_agreed INTEGER,
                access_count INTEGER,
                last_active REAL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

class IndemnityRouter(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GhostCorp User Accountability & Terms</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #05070c; color: #00ffcc; font-family: monospace; padding: 20px; margin: 0; }
                h1 { color: #ff0055; text-shadow: 0 0 12px rgba(255,0,85,0.6); font-size: 24px; }
                .card { background: #0b111d; border: 1px solid #162238; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; }
                .terms-box { background: #05070c; border: 1px solid #162238; padding: 15px; height: 180px; overflow-y: scroll; font-size: 12px; color: #8892b0; margin-bottom: 15px; }
                button { padding: 12px 25px; background: #ff0055; border: none; color: white; font-weight: bold; font-family: monospace; cursor: pointer; border-radius: 4px; font-size: 14px; }
                button:hover { background: #ff2a6d; }
                .container { max-width: 800px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GhostCorp User Agreement & Indemnification</h1>
                <div class="card">
                    <h3>User Accountability & Liability Waiver</h3>
                    <div class="terms-box">
                        <b>1. Sole User Responsibility:</b> You explicitly acknowledge and agree that you are 100% accountable for all actions, communications, and data transmissions you execute while using this application.<br><br>
                        <b>2. Indemnification & Hold Harmless:</b> You agree to defend, indemnify, and hold harmless the creators, developers, operators, and hosts of GhostCorp from and against any and all claims, liabilities, damages, losses, or legal expenses (including attorney fees) arising out of your use or misuse of this software.<br><br>
                        <b>3. Illegal Activity Prohibition:</b> Any violation of local, national, or international law using this platform is strictly prohibited. Automated moderation systems will instantly flag, block, and permanently ban accounts engaging in unauthorized or malicious conduct, logging telemetry data into secure system archives.<br><br>
                        <b>4. "AS IS" Provision:</b> The software is provided without warranties of any kind, explicit or implied.
                    </div>
                    <form action="/agree" method="POST">
                        <button type="submit">I Agree & Accept Full Accountability</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        if self.path == "/agree":
            try:
                ip = self.client_address[0]
                user_agent = self.headers.get('User-Agent', 'Unknown-Client')
                user_id = f"User-{abs(hash(ip + user_agent)) % 100000}"
                
                conn = sqlite3.connect(DB_FILE, timeout=5)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO active_users (user_identifier, ip_address, client_platform, indemnity_agreed, access_count, last_active) VALUES (?, ?, ?, 1, 1, ?)",
                               (user_id, ip, user_agent[:40], time.time()))
                conn.commit()
                conn.close()
            except Exception:
                pass

            self.send_response(303)
            self.send_header("Location", "/app")
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), IndemnityRouter)
    print(f"[*] Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    run_server()
