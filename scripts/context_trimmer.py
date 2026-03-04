#!/usr/bin/env python3
"""
Agenticana Context Trimmer — Token Optimization Engine
=======================================================
Trims large files to only the relevant sections before passing to an LLM.
Reduces token waste by up to 80% on large files.

Usage:
    python scripts/context_trimmer.py <file> [pattern] [window] [--all-matches]

Examples:
    python scripts/context_trimmer.py dashboard/index.html "runTask" 60
    python scripts/context_trimmer.py scripts/dashboard_api.py "def api_" 80 --all-matches
    python scripts/context_trimmer.py README.md --stats
"""
import sys
import os
import re
import json
from pathlib import Path


def trim_file_context(file_path: str, target_pattern: str = None,
                      window: int = 60, all_matches: bool = False) -> dict:
    """
    Trim a file to relevant sections only.
    Returns dict with: content, stats (lines_total, lines_returned, token_estimate, savings_pct)
    """
    try:
        text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=True)
        total = len(lines)
        chars_total = len(text)

        # Small file — return as-is
        if total <= window * 2:
            return {
                "content": text,
                "stats": {"lines_total": total, "lines_returned": total,
                          "token_estimate": chars_total // 4,
                          "savings_pct": 0, "matches": []}
            }

        # No pattern — return head + tail with gap marker
        if not target_pattern:
            head = lines[:window // 2]
            tail = lines[-(window // 2):]
            gap = f"\n// ... [{total - window} lines hidden — use pattern to focus] ...\n\n"
            content = "".join(head) + gap + "".join(tail)
            shown = len(head) + len(tail)
            return {
                "content": content,
                "stats": {"lines_total": total, "lines_returned": shown,
                          "token_estimate": len(content) // 4,
                          "savings_pct": round((1 - shown / total) * 100),
                          "matches": []}
            }

        # Find all matching line numbers
        matches = [i for i, line in enumerate(lines)
                   if re.search(target_pattern, line, re.IGNORECASE)]

        if not matches:
            # Pattern not found — return head only
            head = "".join(lines[:window])
            note = f"\n// [Pattern '{target_pattern}' not found — showing first {window} lines]\n"
            return {
                "content": head + note,
                "stats": {"lines_total": total, "lines_returned": window,
                          "token_estimate": len(head) // 4,
                          "savings_pct": round((1 - window / total) * 100),
                          "matches": []}
            }

        # Decide which matches to use
        use_matches = matches if all_matches else [matches[0]]

        # Build non-overlapping windows around each match
        ranges: list[tuple[int, int]] = []
        half = window // 2
        for m in use_matches:
            s = max(0, m - half)
            e = min(total, m + half)
            # Merge with previous if overlapping
            if ranges and s <= ranges[-1][1]:
                ranges[-1] = (ranges[-1][0], e)
            else:
                ranges.append((s, e))

        # Build output with gap markers
        parts = []
        prev_end = 0
        for s, e in ranges:
            if s > prev_end:
                parts.append(f"// ... [Lines {prev_end + 1}–{s} hidden] ...\n\n")
            parts.extend(lines[s:e])
            prev_end = e

        if prev_end < total:
            parts.append(f"\n// ... [Lines {prev_end + 1}–{total} hidden] ...\n")

        content = "".join(parts)
        shown = sum(e - s for s, e in ranges)

        return {
            "content": content,
            "stats": {
                "lines_total": total,
                "lines_returned": shown,
                "token_estimate": len(content) // 4,
                "savings_pct": round((1 - shown / total) * 100),
                "matches": [{"line": m + 1, "text": lines[m].rstrip()} for m in matches[:10]]
            }
        }

    except Exception as e:
        return {"content": f"// Error: {e}", "stats": {}}


def print_stats(stats: dict, file_path: str):
    """Print a human-readable token savings summary."""
    total    = stats.get("lines_total", "?")
    returned = stats.get("lines_returned", "?")
    tokens   = stats.get("token_estimate", "?")
    savings  = stats.get("savings_pct", 0)
    matches  = stats.get("matches", [])
    print(f"\n{'─'*55}", file=sys.stderr)
    print(f"  Context Trimmer Report: {file_path}", file=sys.stderr)
    print(f"{'─'*55}", file=sys.stderr)
    print(f"  Total lines  : {total}", file=sys.stderr)
    print(f"  Lines shown  : {returned}", file=sys.stderr)
    print(f"  Token est.   : ~{tokens} tokens", file=sys.stderr)
    print(f"  Token savings: {savings}%", file=sys.stderr)
    if matches:
        print(f"  Matches ({len(matches)}):", file=sys.stderr)
        for m in matches[:5]:
            print(f"    L{m['line']}: {m['text'][:70]}", file=sys.stderr)
    print(f"{'─'*55}\n", file=sys.stderr)


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if not args or "--help" in flags:
        print("Usage: python context_trimmer.py <file> [pattern] [window] [--all-matches] [--stats]")
        sys.exit(0)

    file_path  = args[0]
    pattern    = args[1] if len(args) > 1 else None
    window     = int(args[2]) if len(args) > 2 else 60
    all_matches = "--all-matches" in flags
    show_stats  = "--stats" in flags or True  # always show stats to stderr

    result = trim_file_context(file_path, pattern, window, all_matches)
    print(result["content"])
    if show_stats:
        print_stats(result["stats"], file_path)
