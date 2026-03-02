import http.server
import socketserver
import json
import os
from pathlib import Path

# Agentica Control Center API (Hardened)
PORT = 8080
AUTH_KEY_PATH = Path(".Agentica/auth.key")

def get_auth_key():
    if AUTH_KEY_PATH.exists():
        return AUTH_KEY_PATH.read_text().strip()
    return None

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Security Gate: Check for API Key
        auth_header = self.headers.get('X-Agentica-Auth')
        expected_key = get_auth_key()

        if self.path.startswith('/api/') and auth_header != expected_key:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'X-Agentica-Auth')
            self.end_headers()
            # ... rest of status logic ...

            # Aggregate status
            status = {
                "project": "Agent Americana",
                "version": "3.0.0 (Evolution)",
                "heartbeat": self.get_latest_heartbeat(),
                "swarm": self.get_latest_swarm(),
                "registry": self.get_registry_count(),
                "vector_memory": self.get_vector_count()
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            super().do_GET()

    def get_latest_heartbeat(self):
        path = Path(".Agentica/logs/heartbeat.log")
        return "Active" if path.exists() else "Inactive"

    def get_latest_swarm(self):
        path = Path(".Agentica/logs/swarm/report.json")
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def get_registry_count(self):
        path = Path(".Agentica/registry.json")
        if path.exists():
            with open(path, 'r') as f:
                return len(json.load(f).get("installed", {}))
        return 0

    def get_vector_count(self):
        path = Path(".Agentica/vector_store.json")
        if path.exists():
            with open(path, 'r') as f:
                return len(json.load(f).get("documents", []))
        return 0

if __name__ == "__main__":
    print(f"[*] Starting Agentica Control Center API on http://127.0.0.1:{PORT}...")
    # Bind to localhost only for security
    with socketserver.TCPServer(("127.0.0.1", PORT), DashboardHandler) as httpd:
        httpd.serve_forever()
