"""
Agenticana Dashboard API — v7.1 (Live Log Streaming)
Flask API with unbuffered subprocess output and incremental log endpoint.
"""
import os
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, redirect, Response

# ── Config ────────────────────────────────────────────────────────────────────
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent.parent   # d:\_Projects\Agentica
DASHBOARD_DIR = BASE_DIR / "dashboard"
AUTH_KEY_PATH = BASE_DIR / ".Agentica" / "auth.key"
LOG_PATH = BASE_DIR / ".Agentica" / "logs" / "dashboard_action.log"

app = Flask(__name__, static_folder=str(DASHBOARD_DIR))

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_auth_key() -> str | None:
    if AUTH_KEY_PATH.exists():
        return AUTH_KEY_PATH.read_text(encoding="utf-8").strip()
    return None


def check_auth() -> bool:
    key = request.headers.get("X-Agentica-Auth", "")
    expected = get_auth_key()
    ok = key == expected
    if not ok:
        print(f"[AUTH] Blocked — received='{key}' expected='{expected}'")
    return ok


def read_json(path: Path, default=None):
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}")
    return default


def get_recent_logs(n: int = 50):
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            return f.readlines()[-n:]
    return []


def get_latest_simulacrum():
    log_dir = BASE_DIR / ".Agentica" / "logs" / "simulacrum"
    if not log_dir.exists():
        return None
    logs = sorted(log_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
    return read_json(logs[0]) if logs else None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def root():
    return redirect("/dashboard/index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/dashboard/")
@app.route("/dashboard/<path:filename>")
def serve_dashboard(filename="index.html"):
    return send_from_directory(DASHBOARD_DIR, filename)


@app.route("/api/status")
def api_status():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    registry_path = BASE_DIR / ".Agentica" / "registry.json"
    vector_path   = BASE_DIR / ".Agentica" / "vector_store.json"
    swarm_path    = BASE_DIR / ".Agentica" / "logs" / "swarm" / "report.json"
    intel_path    = BASE_DIR / ".Agentica" / "competitor_intel.json"
    heartbeat_path= BASE_DIR / ".Agentica" / "logs" / "heartbeat.log"

    registry_data = read_json(registry_path, {})
    vector_data   = read_json(vector_path, {})

    status = {
        "project": "Agenticana",
        "version": "v7.0.0 (Flask Edition)",
        "timestamp": datetime.now().isoformat(),
        "heartbeat": "Active" if heartbeat_path.exists() else "Inactive",
        "swarm": read_json(swarm_path),
        "registry": len(registry_data.get("installed", {})),
        "vector_memory": len(vector_data.get("documents", [])),
        "intel": read_json(intel_path, []),
        "simulacrum": get_latest_simulacrum(),
        "logs": get_recent_logs(),
    }
    return jsonify(status)


@app.route("/api/run")
def api_run():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    task = request.args.get("task", "").strip()
    print(f"[TASK] Received run request for: '{task}'")

    SCRIPT_MAP = {
        "intel":  ["python", str(BASE_DIR / "scripts" / "sovereign_intel.py")],
        "evolve": ["python", str(BASE_DIR / "scripts" / "nl_swarm.py"), "Autonomous Evolution", "--intel", "--run"],
        "audit":  ["python", str(BASE_DIR / "scripts" / "verify_all.py"), "--url", "local"],
    }

    cmd = SCRIPT_MAP.get(task)
    if not cmd:
        print(f"[ERROR] Unknown task: '{task}' — valid: {list(SCRIPT_MAP.keys())}")
        return jsonify({"error": "Task not found", "task": task, "valid": list(SCRIPT_MAP.keys())}), 404

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_file_handle = open(LOG_PATH, "a", encoding="utf-8")
    log_file_handle.write(f"\n--- Starting '{task}' at {datetime.now()} ---\n")
    log_file_handle.flush()

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(cmd, stdout=log_file_handle, stderr=log_file_handle, cwd=str(BASE_DIR), env=env)
    print(f"[EXEC] Launched: {' '.join(cmd)}")

    # ── Background watcher: fires post-commit hook when task finishes ──────────
    def watch_and_commit(process, lf, t):
        process.wait()  # block until task subprocess exits
        lf.write(f"\n--- Task '{t}' completed. Running auto-commit hook... ---\n")
        lf.flush()
        hook_cmd = ["python", str(BASE_DIR / "scripts" / "post_task_commit.py"), t]
        hook = subprocess.Popen(hook_cmd, stdout=lf, stderr=lf, cwd=str(BASE_DIR), env=env)
        hook.wait()
        lf.write(f"--- Auto-commit hook done for '{t}' ---\n")
        lf.flush()
        lf.close()
        print(f"[HOOK] Post-commit done for task: {t}")

    watcher = threading.Thread(target=watch_and_commit, args=(proc, log_file_handle, task), daemon=True)
    watcher.start()

    offset = LOG_PATH.stat().st_size if LOG_PATH.exists() else 0
    return jsonify({"status": "started", "task": task, "log_offset": offset})


# ── Boot ──────────────────────────────────────────────────────────────────────

@app.route("/api/logs")
def api_logs():
    """Return log lines from a byte offset (for incremental polling)."""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    offset = int(request.args.get("offset", 0))

    if not LOG_PATH.exists():
        return jsonify({"lines": [], "offset": 0})

    size = LOG_PATH.stat().st_size
    if offset >= size:
        return jsonify({"lines": [], "offset": size})

    with open(LOG_PATH, "rb") as f:
        f.seek(max(0, offset))
        raw = f.read()

    lines = raw.decode("utf-8", errors="replace").splitlines()
    return jsonify({"lines": lines, "offset": size})


@app.route("/api/logs/clear", methods=["POST"])
def api_logs_clear():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    if LOG_PATH.exists():
        LOG_PATH.write_text("", encoding="utf-8")
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    print(f"[*] Agenticana Dashboard API v7.0 — http://127.0.0.1:{PORT}")
    print(f"[*] Serving dashboard from: {DASHBOARD_DIR}")
    print(f"[*] Base dir: {BASE_DIR}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
