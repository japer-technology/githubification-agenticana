import os
import shutil
import subprocess
import json
from pathlib import Path

# Agentica P11: The Shadow Sandbox
# Provides a safe, isolated environment for agent execution and auditing.

class SandboxManager:
    def __init__(self, project_root=".", sandbox_name="shadow_sandbox"):
        self.root = Path(project_root).resolve()
        self.sandbox_path = self.root / ".Agentica" / sandbox_name
        self.ignore_patterns = [
            ".git", "node_modules", ".Agentica", "__pycache__",
            ".venv", "venv", ".next", "dist", "build"
        ]

    def initialize_sandbox(self):
        """Creates a fresh clone of the project in the sandbox directory."""
        if self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path)

        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        print(f"[*] Sandbox: Initializing clone at {self.sandbox_path}...")

        # Use a more efficient copy that respects ignore patterns
        for item in self.root.iterdir():
            if item.name in self.ignore_patterns:
                continue

            dest = self.sandbox_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*self.ignore_patterns))
            else:
                shutil.copy2(item, dest)

        print("[+] Sandbox: Clone complete.")

    def run_in_sandbox(self, command):
        """Executes a command within the sandbox context."""
        print(f"[*] Sandbox: Executing '{command}'...")
        # Note: We need to handle Cwd correctly for subcommands
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.sandbox_path),
                capture_output=True,
                text=True
            )
            return result
        except Exception as e:
            print(f"[-] Sandbox Execution Error: {str(e)}")
            return None

    def audit_sandbox(self):
        """Runs the Sentinel audit on the sandbox directory."""
        print("[*] Sandbox: Running Sentinel Audit on Shadow Clone...")
        # Modify sentinel to accept a custom root
        cmd = f"python {self.root}/scripts/sentinel.py --root {self.sandbox_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        is_healthy = "System is HEALTHY" in result.stdout
        print(f"[?] Sandbox Health: {'OPTIMAL' if is_healthy else 'FAILED'}")
        return is_healthy, result.stdout

    def merge_sandbox(self):
        """Syncs verified changes from the sandbox back to the production root."""
        print("[*] Sandbox: Merging verified changes to production...")
        # Simple overwrite merge (excluding the sandbox itself and core Agentica configs)
        for item in self.sandbox_path.iterdir():
            if item.name == ".Agentica":
                continue

            dest = self.root / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        print("[+] Sandbox: Production successfully merged and updated.")

if __name__ == "__main__":
    import sys
    sm = SandboxManager()
    if len(sys.argv) < 2:
        print("Usage: python sandbox_manager.py <command>")
        print("Commands: init, audit, merge")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        sm.initialize_sandbox()
    elif cmd == "audit":
        sm.audit_sandbox()
    elif cmd == "merge":
        sm.merge_sandbox()
