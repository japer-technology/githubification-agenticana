import subprocess
import json
import os
import time
from pathlib import Path

# Agentica P8: The Self-Healing Sentinel
# Automatically detects failures and dispatches fixing swarms.

class Sentinel:
    def __init__(self, project_root="."):
        self.root = Path(project_root)
        self.logs_dir = self.root / ".Agentica" / "logs" / "sentinel"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def run_audit(self):
        """Runs a suite of core checks to detect 'unhealthy' states."""
        results = []

        # 1. Lint Check
        print("[*] Sentinel Audit: Running Lint Check...")
        lint = subprocess.run(["python", "scripts/verify_all.py", ".", "--url", "http://localhost:8080", "--no-e2e"], capture_output=True, text=True)
        results.append({
            "check": "Audit/Lint/Verify",
            "success": lint.returncode == 0,
            "output": lint.stdout + lint.stderr
        })

        return results

    def analyze_failures(self, audit_results):
        failures = [r for r in audit_results if not r["success"]]
        if not failures:
            print("[+] Sentinel: System is HEALTHY.")
            return None

        print(f"[!] Sentinel: Detected {len(failures)} failures. Generating healing manifest...")

        manifest = {
            "tasks": []
        }

        for fail in failures:
            # Simple heuristic: If verify_all fails, spawn debugger
            manifest["tasks"].append({
                "id": f"heal-{int(time.time())}",
                "agent": "debugger",
                "command": f"python scripts/agent_cli.py @debugger 'Fix failures in audit: {fail['check']}'",
                "description": "Autonomous repair of audit failure."
            })

        return manifest

    def heal(self):
        audit = self.run_audit()
        manifest = self.analyze_failures(audit)

        if manifest:
            manifest_path = self.root / ".Agentica" / "heal_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"[*] Sentinel: Dispatching Healing Swarm...")
            subprocess.run(["python", "scripts/swarm_dispatcher.py", str(manifest_path)])
            print("[+] Sentinel: Healing process initiated.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    s = Sentinel(project_root=args.root)
    s.heal()
