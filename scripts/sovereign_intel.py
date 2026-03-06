#!/usr/bin/env python3
"""
P25: Sovereign Intel Swarm 🦅
============================
The 'Spy' of Agenticana. Monitors competitor repositories to identify
trending feature requests and market gaps.

Usage:
    python scripts/sovereign_intel.py --repos "openclaw/openclaw,cursor/app"
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Default competitors to monitor (expanded baseline).
DEFAULT_COMPETITORS = [
    "openclaw/openclaw",
    "cursor-labs/app",
    "continuedev/continue",
    "cline/cline",
    "Significant-Gravitas/AutoGPT",
    "reworkd/AgentGPT",
    "Pythagora-io/gpt-pilot",
    "abi/screenshot-to-code",
    "e2b-dev/code-interpreter",
    "supermaven-inc/supermaven",
    "TabbyML/tabby",
    "OpenInterpreter/open-interpreter",
    "microsoft/autogen",
    "crewAIInc/crewAI",
    "langchain-ai/langchain",
    "langgenius/dify",
    "run-llama/llama_index",
    "microsoft/semantic-kernel",
    "stanford-oval/storm",
    "microsoft/promptflow",
    "AnythingLLM/AnythingLLM",
    "nomic-ai/gpt4all",
]

COMPETITORS_PATH = Path(".Agentica/competitors.json")


def load_competitors() -> list[str]:
    """Load competitor list from project config, with expanded defaults fallback."""
    if COMPETITORS_PATH.exists():
        try:
            data = json.loads(COMPETITORS_PATH.read_text(encoding="utf-8"))
            repos = data.get("repos", []) if isinstance(data, dict) else []
            cleaned = [str(r).strip() for r in repos if str(r).strip()]
            if cleaned:
                return cleaned
        except Exception as exc:
            print(f"[!] Could not parse {COMPETITORS_PATH}: {exc}")

    COMPETITORS_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPETITORS_PATH.write_text(
        json.dumps(
            {
                "updated_at": datetime.now().isoformat(),
                "repos": DEFAULT_COMPETITORS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return DEFAULT_COMPETITORS

def monitor_competitor(repo: str):
    """
    Simulated monitoring logic (will use GitHub API in full implementation).
    Identifies trending issues and feature requests.
    """
    print(f"[*] Monitoring {repo}...")
    # In full P25, this would call GitHub API /search/issues
    # For now, we return a mock of what the research agent found
    return {
        "repo": repo,
        "scanned_at": datetime.now().isoformat(),
        "trending_requests": [
            "Voice-to-code integration",
            "Multi-model simulation/debate",
            "Local-first vector storage"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="Agenticana Sovereign Intel Swarm")
    parser.add_argument("--repos", help="Comma-separated list of repos to monitor")
    args = parser.parse_args()

    repos = args.repos.split(",") if args.repos else load_competitors()

    findings = []
    for repo in repos:
        findings.append(monitor_competitor(repo.strip()))

    output_path = Path(".Agentica/competitor_intel.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(findings, f, indent=2)

    print(f"\n[+] Intel Swarm complete. Found {len(findings)} competitor snapshots.")
    print(f"[+] Intelligence saved to: {output_path}")
    print("[!] Run 'python scripts/nl_swarm.py --intel' to process these gaps (P25 bridge).")

if __name__ == "__main__":
    main()
