import os
import sqlite3
import threading
import time
import urllib.parse
import json
import random
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_FILE = "ghost_autonomous_memory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_key TEXT,
            semantic_vector_summary TEXT,
            cluster_tier TEXT,
            relevance_score REAL,
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
        cursor.execute("INSERT INTO global_command (command_text, timestamp) VALUES (?, ?)", ("System Nominal: Advanced Memory Swarm Online", time.time()))
    conn.commit()
    conn.close()

def bot_neural_worker(bot_id):
    servers = ["Neural-Vector-Grid-01", "Edge-Memory-Cluster", "Quantized-Node-Delta", "Synapse-Relay"]
    memory_states = [
        "Consolidating short-term episodic tokens into long-term graph memory.",
        "Executing semantic cluster pruning and relevance vector indexing.",
        "Synchronizing cross-node associative memory weights via local embeddings.",
        "Optimizing neural context retention and executing automated self-patching."
    ]
    
    while True:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT command_text FROM global_command ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            current_directive = row[0] if row else "Autonomous Vector Optimization"
            
            server_origin = servers[bot_id % len(servers)]
            ai_reply = f"Directive Vector [{current_directive[:18]}...]: {memory_states[bot_id % len(memory_states)]}"
            job_desc = f"Memory-Driven Task [{bot_id}]"
            
            cursor.execute(
                "INSERT OR REPLACE INTO bot_logs (bot_id, server_origin, job_name, response_text, status, last_ping) VALUES (?, ?, ?, ?, ?, ?)",
                (f"Vector-Agent-{bot_id}", server_origin, job_desc, ai_reply, "ACTIVE", time.time())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(20)

def launch_bot_swarm():
    print("[*] Initializing 100-Node Autonomous Vector-Memory Swarm...")
    for i in range(1, 101):
        t = threading.Thread(target=bot_neural_worker, args=(i,), daemon=True)
        t.start()

def autonomous_memory_synthesizer():
    advanced_architectures = [
        ("Hierarchical Spreading Activation Memory", "Graph-based association clustering with automated weight decay"),
        ("TurboQuant Vector-Embedding Compression", "4-bit scalar quantization for sub-millisecond local semantic lookup"),
        ("Dual-Layer STM/LTM Episodic Buffer", "Isolating high-frequency working memory from compressed long-term knowledge"),
        ("Recursive Self-Refining Neural RAG", "Dynamic context pruning and cross-node vector retrieval synchronization")
    ]
    counter = 200
    while True:
        time.sleep(90)
        counter += 1
        arch_name, arch_desc = random.choice(advanced_architectures)
        unique_memory_key = f"{arch_name} (Model-Gen-{counter})"
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memory_nodes (memory_key, semantic_vector_summary, cluster_tier, relevance_score, timestamp) VALUES (?, ?, ?, ?, ?)",
                (unique_memory_key, arch_desc, "LTM_CONSOLIDATED", round(random.uniform(0.92, 0.99), 4), time.time())
            )
            conn.commit()
            conn.close()

            # Autonomous GitHub Self-Publishing of New Memory Models
            with open("memory_swarm_changelog.txt", "a") as f:
                f.write(f"\n[{time.ctime()}] Deployed New Groundbreaking Memory Model: {unique_memory_key} -> {arch_desc}")
            
            subprocess.run(["git", "config", "--global", "user.email", "memory-swarm-bot@autonomous.ai"], capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Memory Swarm Autonomous Bot"], capture_output=True)
            subprocess.run(["git", "add", "memory_swarm_changelog.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Autonomous Memory Upgrade: {unique_memory_key}"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
        except Exception:
            pass

class MemoryRouter(BaseHTTPRequestHandler):
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
                    
                    cursor.execute("SELECT memory_key, cluster_tier, relevance_score FROM memory_nodes ORDER BY id DESC LIMIT 5")
                    recent_memories = cursor.fetchall()
                    
                    cursor.execute("SELECT bot_id, server_origin, response_text FROM bot_logs ORDER BY last_ping DESC LIMIT 5")
                    bot_dialogues = cursor.fetchall()
                    conn.close()
                    
                    memory_html = "".join([f"<li><b>{mkey}</b> <span style='color:#00ff66;'>[{tier} - Rel: {rel}]</span></li>" for mkey, tier, rel in recent_memories])
                    dialogue_html = "".join([f"<li style='margin-bottom:6px;'><b>{bid}</b> @ <code>{serv}</code>:<br><span style='color:#00ffcc;'>\"{resp}\"</span></li>" for bid, serv, resp in bot_dialogues])
                    
                    status_payload = f"{active_bots} Vector Agents Active | <span style='color:#ff0055;'>{active_servers} Memory Clusters</span>"
                    
                    payload = f"data: {status_payload}|||{active_cmd}|||{memory_html}|||{dialogue_html}\n\n"
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
            <title>GhostCorp Autonomous Vector Memory Swarm</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #070913; color: #00ffcc; font-family: monospace; padding: 20px; margin: 0; }
                h1 { color: #ff0055; text-shadow: 0 0 12px rgba(255,0,85,0.6); font-size: 24px; }
                .card { background: #0e1626; border: 1px solid #1a263f; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; }
                .status { color: #00ff66; font-weight: bold; }
                .container { max-width: 1200px; margin: 0 auto; }
                input[type="text"] { width: 65%; padding: 12px; background: #070913; border: 1px solid #00ffcc; color: #00ffcc; font-family: monospace; border-radius: 4px; font-size: 14px; }
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
                <h1>GhostCorp Vector Memory Swarm Core</h1>
                
                <div class="card">
                    <h3>Global Memory Directive Interface</h3>
                    <form action="/command" method="POST">
                        <input type="text" name="directive" placeholder="Broadcast directive to memory models..." required>
                        <button type="submit">Deploy Directive</button>
                    </form>
                    <p style="font-size: 13px; margin-top: 10px;"><b>Active Directive:</b> <span id="current-cmd" style="color: #ff0055;">Syncing...</span></p>
                </div>

                <div class="card">
                    <h3>Swarm Grid Telemetry: <span id="bot-status" class="status">Connecting...</span></h3>
                </div>

                <div class="card">
                    <h3>Live Agent Memory-State Feed:</h3>
                    <ul id="job-list">
                        <li>Establishing vector memory synchronization across nodes...</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Self-Synthesized Memory Models & GitHub Pushes:</h3>
                    <ul id="upgrade-list">
                        <li>Awaiting next local vector model compilation cycle...</li>
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
    server = HTTPServer(("0.0.0.0", port), MemoryRouter)
    server.serve_forever()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=launch_bot_swarm, daemon=True).start()
    threading.Thread(target=autonomous_memory_synthesizer, daemon=True).start()
    run_server()
