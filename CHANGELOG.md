# Changelog

All notable changes to Agenticana are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [P29+] 2026-03-06 — GitHub Actions CI Agent (Enhanced)

### Added

- **GitHub Actions CI Agent (Enhanced)**: A GitHub Actions workflow that runs the full Agenticana audit chain (Guardian → Sentinel → tests → Lighthouse) on every PR automatically.
- Plan document: `plans/p29_github_actions_agent.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P29+ as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P28+] 2026-03-06 — Local-First Vector Storage (Enhanced)

### Added

- **Local-First Vector Storage (Enhanced)**: Replace in-memory vector store with a persistent local Qdrant/ChromaDB instance. Enables persistent agent memory across restarts without cloud dependency.
- Plan document: `plans/p28_local_vector_store.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P28+ as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P27+] 2026-03-06 — Cross-LLM Debate Voting (Enhanced)

### Added

- **Cross-LLM Debate Voting (Enhanced)**: Extended Simulacrum that uses multiple LLM providers (Gemini, OpenAI, Anthropic) as different agent 'brains' to produce genuinely diverse opinions.
- Plan document: `plans/p27_cross_llm_debate.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P27+ as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P26+] 2026-03-06 — Voice-to-Code Bridge (Enhanced)

### Added

- **Voice-to-Code Bridge (Enhanced)**: Allow users to describe code changes in spoken/written natural language. The system transcribes and pipes input directly to NL Swarm for agent dispatch.
- Plan document: `plans/p26_voice_to_code.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P26+ as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P30] 2026-03-06 — Agent Performance Leaderboard

### Added

- **Agent Performance Leaderboard**: Track which agents win the most Simulacrum debates, which proposals get accepted, and surface a ranked leaderboard on the dashboard.
- Plan document: `plans/p30_leaderboard.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P30 as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P29] 2026-03-06 — GitHub Actions CI Agent

### Added

- **GitHub Actions CI Agent**: A GitHub Actions workflow that runs the full Agenticana audit chain (Guardian → Sentinel → tests → Lighthouse) on every PR automatically.
- Plan document: `plans/p29_github_actions_agent.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P29 as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P28] 2026-03-06 — Local-First Vector Storage

### Added

- **Local-First Vector Storage**: Replace in-memory vector store with a persistent local Qdrant/ChromaDB instance. Enables persistent agent memory across restarts without cloud dependency.
- Plan document: `plans/p28_local_vector_store.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P28 as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P27] 2026-03-04 — Cross-LLM Debate Voting

### Added

- **Cross-LLM Debate Voting**: Extended Simulacrum that uses multiple LLM providers (Gemini, OpenAI, Anthropic) as different agent 'brains' to produce genuinely diverse opinions.
- Plan document: `plans/p27_cross_llm_debate.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P27 as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [P26] 2026-03-04 — Voice-to-Code Bridge

### Added

- **Voice-to-Code Bridge**: Allow users to describe code changes in spoken/written natural language. The system transcribes and pipes input directly to NL Swarm for agent dispatch.
- Plan document: `plans/p26_voice_to_code.md`
- Triggered by market gap analysis: _"Voice-to-code integration"_

### Evolution Chain

- Intel swarm identified gap across 11 competitor repos
- Evolution engine selected P26 as next logical phase
- All artifacts auto-committed by Secretary Bird 🦅

---

## [6.0.0] — 2026-03-03 🦅 Secretary Bird Edition

### The Differentiators — Phases P15–P19

> _"We don't react. We stomp, record, and move forward with proof."_
> Agenticana becomes the first AI developer system to prove its work.

#### Added — P15: Real LLM Simulacrum

- `scripts/real_simulacrum.py` — Each agent (backend-specialist, security-auditor, etc.) calls a real Gemini API instance with a domain-specific system prompt
- Agents genuinely debate architecture with opposing LLM opinions — not hardcoded responses
- Graceful fallback to persona mode when no API key is set
- `--set-key` flag to save Gemini key to `.Agentica/gemini.key`

#### Added — P16: Guardian Mode

- `scripts/guardian_mode.py` — Git pre-commit hook that intercepts every commit
- **Check 1:** Sentinel audit (advisory — warns but does not block)
- **Check 2:** Python syntax lint (blocking on error)
- **Check 3:** Smart secret scan — detects real hardcoded secret values (len >20, not placeholder), not variable names
- `guardian_mode.py install / remove / audit / status`
- Logs every audit to `.Agentica/logs/guardian/`

#### Added — P17: Natural Language Swarm

- `scripts/nl_swarm.py` — Type plain English, get a swarm manifest
- Keyword-based agent selection (22 trigger groups across 8 agents)
- Intent detection: build / audit / test / deploy / optimise / document / debug / review
- `--run` flag to immediately dispatch the generated swarm
- `--shadow` flag for sandboxed execution

#### Added — P18: ADR Generator

- `scripts/adr_generator.py` — Converts Simulacrum session JSON into professional Architecture Decision Records
- Saved to `docs/decisions/ADR-XXX-topic-slug.md`
- Auto-numbered, includes vote tally, winning proposal, all constraints
- `--latest` / `--list` / `--all` flags

#### Added — P19: Proof-of-Work Commits

- `scripts/pow_commit.py` — Signs every commit with a cryptographic attestation
- Attestation proves: debate completed, performance benchmarked, guardian passed
- Trust Score: 0–100 — CERTIFIED (≥70) / PARTIAL (≥40) / UNVERIFIED (<40)
- Stored in `.Agentica/attestations/attest_<hash>_<ts>.json`
- `pow_commit.py sign / verify / log`

#### Changed

- **Mascot:** Secretary Bird 🦅 replaces all lobster references (8 files purged)
- `README.md` fully rewritten for v6.0 with P1–P19 phase table
- Competitor table updated to include OpenClaw comparison
- `scripts/rebrand_secretary_bird.py` — migration utility (can be run again if needed)
- Zero lobster emoji or text remain in codebase (verified via grep)

---

## [5.0.0] — 2026-03-03

### Phases P12–P14 + MCP Fix

#### Added — P12: Logic Simulacrum

- `scripts/simulacrum.py` — 5-phase debate engine (opening → debate → proposal → vote → consensus)
- 7 built-in agent personas with distinct domain biases
- `quick_debate()` function for auto-agent selection based on topic keywords
- Session logs saved to `.Agentica/logs/simulacrum/session_<id>.json`

#### Added — P13: Performance Pulse

- `scripts/performance_pulse.py` — Benchmarks 4 core Agenticana scripts × 3 runs each
- Reports avg_time_ms, peak_memory_mb, status (OPTIMAL / WARN / ERROR)
- Configurable thresholds. Results saved to `.Agentica/logs/performance/pulse_<ts>.json`

#### Added — P14: Agentica CLI v2

- `scripts/agentica_cli.py` — Unified command interface for all Agenticana tools
- Commands: `swarm`, `sentinel`, `dashboard`, `bridge`, `simulacrum`, `pulse`, `sandbox`, `heartbeat`, `exchange`
- ASCII Secretary Bird header art, no third-party deps, Windows UTF-8 safe

#### Fixed

- MCP Server `MODULE_NOT_FOUND`: resolved by running `npm install` in `mcp/`
- Windows `UnicodeEncodeError` in simulacrum.py: UTF-8 stdout wrapper added
- Recursive sandbox clone: removed `sandbox_manager.py init` from performance benchmarks

---

## [4.0.0] — 2026-03-02

### Phases P9–P11 + Shadow Sandbox

#### Added — P11: Shadow Sandbox

- `scripts/sandbox_manager.py` — Git-based project clone for isolated execution
- Runs Sentinel audit on shadow clone before merging to production
- Full rollback support if audit fails
- `--shadow` flag added to `swarm_dispatcher.py`

#### Added — P9: Soul Bridge

- `scripts/soul_bridge.py` — Cross-project memory sync
- Reads from `.Agentica/bridge.json` to monitor linked external projects

#### Added — P10: Heartbeat Daemon

- `scripts/heartbeat_daemon.py` — Background health monitoring
- Alerts on agent failures, memory anomalies, sentinel warnings

---

## [3.0.0] — 2026-03-01

### Phases P6–P8 + Control Center

#### Added — P8: Sentinel (Self-Healing)

- `scripts/sentinel.py` — Autonomous code audit: security, lint, dead code
- Accepts `--root` argument for auditing sandbox clones

#### Added — P6: Vector Soul Memory

- `scripts/vector_memory.py` — Semantic storage for agent soul data

#### Added — P7: Soul Injection API + Dashboard

- `scripts/soul_inject.py` — REST API for memory injection
- `scripts/dashboard_api.py` — Control Center HTTP server (port 8080)
- `dashboard/index.html` — Live monitoring dashboard with real-time refresh

---

## [2.0.0] — 2026-03-01

### Major Release — ReasoningBank + Model Router + MCP

#### Added

- **ReasoningBank** — Vector-based decision memory with cosine similarity search
- **Model Router** — Intelligent complexity scoring, ~40% token savings
- **MCP Server** — 11 tools via Model Context Protocol
- **20 Agent YAML Specs** — Machine-readable agent specifications
- **Swarm Dispatcher (P5)** — Parallel agent execution with `--shadow`, `--dry-run`, `--timeout`
- **3-Tier Skill System** — Core / Domain / Utility with strategy-aware loading
- **`install-to-project.ps1`** — Windows project installer
- **GitHub Actions CI** — Full validation pipeline

---

## [1.0.0] — 2025-12-01

### Initial Release

#### Added

- 20 specialist agent `.md` files with rules and personas
- 36 skills organized into 3-tier hierarchy
- `GEMINI.md` — AI behavior protocol
- Basic `scripts/` directory
- `.vscode/` configuration files

---

[6.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v6.0.0
[5.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v5.0.0
[4.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v4.0.0
[3.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v3.0.0
[2.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v2.0.0
[1.0.0]: https://github.com/ashrafmusa/AGENTICANA/releases/tag/v1.0.0
