#!/ env python3
import os
import json
import time
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup Path
ROOT_DIR = Path(__file__).parent.parent.resolve()
CONFIG_PATH = ROOT_DIR / ".Agentica" / "heartbeat.json"
LOG_DIR = ROOT_DIR / ".Agentica" / "logs"
LOG_FILE = LOG_DIR / "heartbeat.log"

# ANSI Colors for Windows
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def log_info(msg):
    logging.info(f"{Colors.BLUE}[*] {msg}{Colors.ENDC}")

def log_success(msg):
    logging.info(f"{Colors.GREEN}[+] {msg}{Colors.ENDC}")

def log_error(msg):
    logging.error(f"{Colors.RED}[-] {msg}{Colors.ENDC}")

def is_git_clean() -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0 and not result.stdout.strip()
    except Exception:
        return False

def safe_stash_local_changes() -> str | None:
    """Stash local changes and return stash ref when successful, else None."""
    try:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"agenticana-heartbeat-safe-evolve-{stamp}"
        result = subprocess.run(
            ["git", "stash", "push", "-u", "-m", name],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        # git returns "No local changes to save" when tree is already clean.
        if "No local changes to save" in (result.stdout + result.stderr):
            return None
        return "stash@{0}"
    except Exception:
        return None

def restore_stash(stash_ref: str):
    try:
        subprocess.run(
            ["git", "stash", "pop", stash_ref],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        pass

class HeartbeatDaemon:
    def __init__(self, config_path):
        self.config_path = config_path
        self.last_runs = {}
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)['heartbeat']
        log_info(f"Loaded heartbeat config from {self.config_path}")

    def run_task(self, task):
        log_info(f"Executing task: {task['id']} - {task['description']}")
        start_time = time.time()

        stash_ref = None
        if "evolve" in task.get("id", "").lower() and not is_git_clean():
            log_info("Working tree dirty before evolve. Applying safe auto-stash...")
            stash_ref = safe_stash_local_changes()
            if stash_ref:
                log_success("Local changes stashed for isolated evolve cycle.")
            else:
                log_error("Could not stash local changes safely. Skipping evolve task.")
                return

        try:
            # Execute command in shells
            process = subprocess.run(
                task['command'],
                shell=True,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            duration = time.time() - start_time
            if process.returncode == 0:
                log_success(f"Task {task['id']} completed successfully in {duration:.1f}s")
            else:
                log_error(f"Task {task['id']} failed with code {process.returncode}")
                # 🦅 NEW: Audio/Visual Alert
                subprocess.run(["powershell", "-File", str(ROOT_DIR / "scripts" / "notify.ps1"),
                                "-Message", f"Heartbeat Task Failed: {task['id']}",
                                "-Sound", "Hand"],
                               capture_output=True)
                if process.stderr:
                    logging.error(f"Error: {process.stderr[:200]}...")

        except Exception as e:
            log_error(f"Failed to execute {task['id']}: {str(e)}")
        finally:
            if stash_ref:
                restore_stash(stash_ref)
                log_info("Restored local changes after evolve task.")

    def start(self, once=False):
        log_info("Agentica Heartbeat Daemon starting...")

        while True:
            self.load_config() # Reload for any dynamic changes
            if not self.config.get('enabled', False):
                log_info("Heartbeat disabled in config. Sleeping 10 min...")
                time.sleep(600)
                continue

            now = datetime.now()
            for task in self.config['tasks']:
                last_run = self.last_runs.get(task['id'])
                interval = timedelta(hours=task.get('interval_hours', 4))

                if last_run is None or (now - last_run) >= interval:
                    self.run_task(task)
                    self.last_runs[task['id']] = now

            if once:
                log_info("One-time run complete. Exiting.")
                break

            log_info(f"Next pulse in {self.config['interval_minutes']} minutes...")
            time.sleep(self.config['interval_minutes'] * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agentica Heartbeat Daemon")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    setup_logging()
    daemon = HeartbeatDaemon(CONFIG_PATH)
    daemon.start(once=args.once)
