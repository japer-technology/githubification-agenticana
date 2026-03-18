# .ANALYSIS-Githubification.md — How This Repo Becomes a GitHub Action

> **Version:** 1.0.0 | **Date:** 2026-03-18
> **Scope:** Deep analysis of three repositories and a concrete blueprint for converting `githubification-agenticana` into a GitHub Action–based mechanism.

---

## Executive Summary

This document analyzes three repositories — the current repo (`japer-technology/githubification-agenticana`), the reference implementation (`japer-technology/github-minimum-intelligence`), and the framework (`japer-technology/githubification`) — and outlines how this repository can become a GitHub Action–based mechanism.

**The core insight:** Agenticana is a 20-agent, multi-skill AI Developer OS designed for local VS Code execution. Converting it to a GitHub Action–based mechanism requires a **Transformation strategy** — a new dispatch layer that maps GitHub events to specialist agents, running on GitHub Actions runners with Git as persistent memory and Issues as the conversational interface. The `.PLAN-v0.md` and `.PLAN-v1.md` documents in this repo have already charted the architectural direction. This analysis consolidates the lessons from all three repos into a concrete, actionable blueprint.

---

## Part 1: The Three Repositories

### 1.1 This Repo — `githubification-agenticana`

**What it is:** A Sovereign AI Developer OS (Agenticana v6.0) with 20 specialist agents, a ReasoningBank for decision memory, a Model Router for cost-aware LLM selection, a Swarm Dispatcher for parallel agent execution, a Logic Simulacrum for multi-agent debate, Guardian Mode for pre-commit validation, and Proof-of-Work commit attestations.

**Current runtime:** Local — VS Code + GitHub Copilot Chat, CLI scripts (Python), MCP server (Node.js).

**Current state of Githubification:** Analysis phase. The `.github-agenticana/` folder contains 8 deep analysis documents and 5 specification drafts studying the reference architecture. Two plan documents (`.PLAN-v0.md` and `.PLAN-v1.md`) define the architectural direction. No runtime implementation (workflow YAML, lifecycle scripts, state management) has been built yet.

**Key assets for Githubification:**

| Asset | Location | Role in Githubified System |
|-------|----------|---------------------------|
| 20 agent specs | `agents/*.yaml` + `agents/*.md` | Agent personas for dispatch routing |
| 36 skills | `skills/*/SKILL.md` | Context injection per agent invocation |
| Model Router | `router/router.js` + `router/config.json` | Cost-aware model selection (lite/flash/pro/pro-extended) |
| ReasoningBank | `memory/reasoning-bank/decisions.json` | Git-committed decision memory with semantic similarity |
| MCP Server | `mcp/server.js` (11 tools) | Could expose tools to the Actions-hosted agent |
| Python scripts | `scripts/*.py` (18+ scripts) | CLI tools that could run on Actions runners |
| Copilot instructions | `.github/copilot-instructions.md` | Dual-use: local Copilot + GitHub-hosted Copilot agent |

### 1.2 Reference Implementation — `github-minimum-intelligence`

**What it is:** A minimal, production-ready AI agent that runs entirely on GitHub. One folder (`.github-minimum-intelligence/`), one workflow, one dependency (`@mariozechner/pi-coding-agent`), and one entry point (`lifecycle/agent.ts`).

**How it works:**

```
User opens issue or comments
    → GitHub Actions workflow triggers
    → Authorization check (write+ collaborator)
    → 🚀 reaction added
    → Bun runtime installed
    → agent.ts orchestrator runs:
        1. Reads issue/comment via GitHub API
        2. Resolves session mapping (issue # → session .jsonl file)
        3. Builds prompt from event context
        4. Spawns pi agent with --session for continuity
        5. Extracts reply from JSONL output
        6. Persists session mapping + transcript to git
        7. Posts reply as issue comment (60,000 char limit)
    → 👍 on success, 👎 on error
```

**The four primitives that make it work:**

| GitHub Primitive | Role |
|---|---|
| **GitHub Actions** | Compute — ephemeral 2-core/7GB runners |
| **Git** | Memory — session transcripts committed after every interaction |
| **GitHub Issues** | UI — each issue is a persistent AI conversation thread |
| **GitHub Secrets** | Credentials — LLM API keys (8+ providers supported) |

**Key patterns proven:**

1. **Session continuity via git** — Issue #N maps to `state/issues/N.json` which points to `state/sessions/<timestamp>.jsonl`. Comments weeks later resume with full context.
2. **Push conflict resolution** — Up to 10 retries with `git pull --rebase -X theirs` and increasing backoff delays.
3. **Reaction-based status** — 🚀 (running), 👍 (success), 👎 (error).
4. **Authorization at workflow level** — Only admin/maintain/write collaborators trigger the agent.
5. **Concurrency control** — One agent runs per issue at a time; subsequent runs queue.
6. **Agent identity as versioned config** — `AGENTS.md` defines persona; `BOOTSTRAP.md` enables personality hatching.

### 1.3 The Framework — `githubification`

**What it is:** A conceptual framework and case study repository documenting how any software repository can be converted to run on GitHub itself — "GitHub as infrastructure."

**The core definition:**

> *"Githubification is the act of converting a repository into GitHub-as-infrastructure. Instead of cloning the repo and running the software elsewhere, the repo becomes something that runs on GitHub itself via GitHub Actions. There's no separate local runtime to install — GitHub is the runtime."*

**Five Githubification strategies** (derived from 6 case studies across 20 analyzed projects):

| # | Strategy | When to Use | Example |
|---|----------|-------------|---------|
| 1 | **Native** | Building a new agent from scratch for GitHub | GMI, GitClaw |
| 2 | **Wrapping** | Agent exists, wrap without modifying source | OpenClaw |
| 3 | **Substitution** | Agent's runtime conflicts with Actions | Agent Zero |
| 4 | **Transformation** | Multi-agent system needs a routing layer | **Agenticana** |
| 5 | **Channel Addition** | Agent has multi-channel architecture | MicroClaw |

**Agenticana is classified as Strategy 4 — Transformation.** This is the most complex strategy because it requires building new dispatch infrastructure that doesn't exist in the current system.

**The universal invariant** (holds across all 6 fully analyzed case studies):

```
┌─ GitHub Actions ────→ Compute (the runner)
├─ Git ────────────────→ Storage & Memory
├─ GitHub Issues ──────→ User Interface
└─ GitHub Secrets ─────→ Credentials
```

**The universal lifecycle pipeline:**

```
Guard → Validate → Indicate → Execute → Commit → Post → React
```

---

## Part 2: Why Transformation (Not Wrapping or Native)

Agenticana cannot use the simpler strategies:

| Strategy | Why Not |
|----------|---------|
| **Native** | Agenticana already exists with 20 agents, 36 skills, and a full architecture. It wasn't built for GitHub from scratch. |
| **Wrapping** | There is no single entry point to wrap. Agenticana is 20 agents + a router + a memory system + a swarm dispatcher. A thin wrapper cannot capture this complexity. |
| **Substitution** | Agenticana CAN run on GitHub Actions (Python + Node.js are natively supported). There's no fundamental runtime conflict. |
| **Channel Addition** | Agenticana has no multi-channel adapter architecture. It was built for one channel (VS Code). |
| **Transformation** ✅ | Agenticana's interaction model (synchronous, interactive, local) must be transformed to GitHub's model (asynchronous, event-driven, remote). A new dispatch layer must route GitHub events to the correct specialist agent(s). |

**What makes Transformation unique:**

| Dimension | Single-Agent Githubification | Agenticana Transformation |
|-----------|------------------------------|---------------------------|
| Routing | Not needed — one agent handles everything | Label-based or prefix-based dispatch to 20 specialists |
| Concurrency | One agent per issue | Multiple agents per issue (swarm execution) |
| Memory | Unified session history | Per-agent decisions + shared ReasoningBank |
| Identity | One persona (AGENTS.md) | 20 personas (YAML specs + MD instructions) |
| Model selection | One configured model | Router selects per-task (lite/flash/pro/pro-extended) |
| Cost management | Simple (one model, one invocation) | Critical (20 agents × variable model tiers × Actions minutes) |

---

## Part 3: The Blueprint — How This Repo Becomes a GitHub Action

### 3.1 Unified Folder Structure

Following `.PLAN-v1.md`'s dual-engine architecture, the Githubified system lives in a single folder:

```
.github-agenticana-intelligence/
├── lifecycle/
│   ├── agent.ts                    # Unified orchestrator (prefix → engine dispatch)
│   ├── agenticana-engine.ts        # Agenticana 20-agent path (? prefix)
│   ├── gmi-engine.ts               # GMI single-agent path (! prefix)
│   └── indicator.ts                # Pre-execution 🚀 reaction
├── .agenticana/
│   ├── settings.json               # LLM provider/model config per engine
│   ├── agents/                     # 20 agent YAML specs (copied from agents/)
│   ├── skills/                     # 36 skill SKILL.md files (copied from skills/)
│   ├── router/                     # Model Router (from router/)
│   │   ├── router.js
│   │   ├── complexity-scorer.js
│   │   ├── token-estimator.js
│   │   └── config.json
│   └── memory/
│       └── reasoning-bank/
│           ├── decisions.json      # Git-committed decision memory
│           └── patterns.json       # Distilled patterns
├── .pi/                            # GMI engine config (pi-mono)
│   ├── settings.json
│   ├── APPEND_SYSTEM.md
│   ├── BOOTSTRAP.md
│   └── skills/
├── state/                          # Git-tracked session state
│   ├── issues/                     # Issue # → session file mapping
│   │   └── {number}.json
│   └── sessions/                   # Full conversation transcripts
│       └── {timestamp}_{hash}.jsonl
├── AGENTS.md                       # Unified agent identity file
├── VERSION                         # Installed version
├── package.json                    # Runtime dependencies
└── bun.lock                        # Lockfile
```

### 3.2 Single Workflow File

One workflow powers both engines:

**`.github/workflows/github-agenticana-intelligence-agent.yml`**

```yaml
name: github-agenticana-intelligence-agent

on:
  issues:
    types: [opened]
  issue_comment:
    types: [created]
  workflow_dispatch:               # Manual install/upgrade

permissions:
  contents: write                  # Commit state & responses
  issues: write                    # Post comments & reactions
  actions: write                   # Allow commits to trigger workflows

jobs:
  run-agent:
    runs-on: ubuntu-latest
    timeout-minutes: 240           # 4-hour default
    concurrency:
      group: agenticana-${{ github.repository }}-issue-${{ github.event.issue.number }}
      cancel-in-progress: false    # Queue, don't cancel

    steps:
      # 1. Guard — Authorization check
      - name: Authorize
        run: |
          PERMISSION=$(gh api repos/${{ github.repository }}/collaborators/${{ github.actor }}/permission --jq '.permission')
          if [[ ! "$PERMISSION" =~ ^(admin|maintain|write)$ ]]; then
            echo "Unauthorized: $PERMISSION"
            exit 1
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # 2. Checkout — Full history for session continuity
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # 3. Setup — Runtime installation
      - uses: oven-sh/setup-bun@v2
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      # 4. Indicate — Add 🚀 reaction
      - name: Indicate
        run: bun .github-agenticana-intelligence/lifecycle/indicator.ts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # 5. Install — Dependencies
      - name: Install
        run: |
          cd .github-agenticana-intelligence && bun install --frozen-lockfile
          pip install -r requirements.txt 2>/dev/null || true

      # 6. Execute — Unified orchestrator dispatches to correct engine
      - name: Execute
        run: bun .github-agenticana-intelligence/lifecycle/agent.ts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          MISTRAL_API_KEY: ${{ secrets.MISTRAL_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

### 3.3 Prefix-Based Dual-Engine Dispatch

The unified `agent.ts` orchestrator reads the issue title or comment body and dispatches based on the first character:

| Prefix | Engine | Behavior |
|--------|--------|----------|
| `?` | **Agenticana** | Content analyzed by Model Router → routed to best of 20 specialist agents. Multi-agent swarm for complex tasks. ReasoningBank queried for past decisions. |
| `!` | **GMI** | Content passed directly to `pi` generalist agent. Single-agent, single-session, direct execution. |
| *(no prefix)* | **Ignored** | No AI response — prevents accidental triggers on regular issue discussions. |

**Dispatch flow:**

```
Event received (issue opened / comment created)
  ↓
agent.ts reads event payload
  ↓
Extract first character of title/body
  ├─ '?' → agenticana-engine.ts
  │         ├─ Parse natural language intent
  │         ├─ Query ReasoningBank for similar past decisions
  │         ├─ Run Model Router (complexity → model tier → skill selection)
  │         ├─ Select specialist agent(s)
  │         ├─ Execute agent(s) via Python scripts or direct LLM call
  │         ├─ Record decision to ReasoningBank
  │         └─ Return response
  ├─ '!' → gmi-engine.ts
  │         ├─ Resolve/create session
  │         ├─ Spawn pi agent with --session
  │         ├─ Extract reply from JSONL
  │         └─ Return response
  └─ other → exit 0 (silent, no response)
  ↓
Persist state to git (with push-retry loop)
  ↓
Post reply as issue comment
  ↓
Add 👍 (success) or 👎 (error) reaction
```

### 3.4 Agenticana Engine — Multi-Agent Routing

When the `?` prefix triggers the Agenticana engine, the routing layer must decide which of 20 specialist agents handles the request. Three routing mechanisms, used in combination:

#### Mechanism 1: Issue Labels → Agent Routing

| Issue Label | Agent | What It Does |
|-------------|-------|--------------|
| `security` | security-auditor | Security review, vulnerability scanning |
| `performance` | performance-optimizer | Performance audit, Lighthouse, bundle analysis |
| `architecture` | orchestrator | Architecture planning, triggers Logic Simulacrum |
| `debug` | debugger | Bug investigation, root cause analysis |
| `frontend` | frontend-specialist | React/Next.js UI work |
| `backend` | backend-specialist | API/server/database work |
| `mobile` | mobile-developer | React Native/Expo work |
| `database` | database-architect | Schema design, migrations, indexing |
| `devops` | devops-engineer | CI/CD, Docker, deployment |
| `test` | test-engineer | Test writing, coverage improvement |
| `docs` | documentation-writer | Documentation, READMEs |
| `gamedev` | game-developer | Game development |
| `seo` | seo-specialist | SEO optimization |
| `explore` | explorer-agent | Codebase discovery |

#### Mechanism 2: Natural Language Classification

When no label is present, the Model Router's complexity scorer analyzes the issue text and selects the best agent based on keyword matching and domain inference from the agent YAML specs' `routing_hints.keywords` fields.

#### Mechanism 3: Swarm Dispatch

For complex tasks that span multiple domains (e.g., "Build a user dashboard with auth, write tests, and do a security review"), the Swarm Dispatcher runs multiple agents:

```
? Build a user dashboard with auth, write tests, and security review
  → NL Swarm parser extracts:
    1. frontend-specialist (dashboard UI)
    2. backend-specialist (auth API)
    3. test-engineer (test suite)
    4. security-auditor (security review)
  → Agents execute sequentially or in parallel (via matrix strategy)
  → Results aggregated into single issue comment
```

### 3.5 Session Continuity & Git-as-Memory

Following the proven GMI pattern:

```
Issue #42 created with "? Build a REST API for user management"
  → Session created: state/sessions/2026-03-18T10-30_a1b2c3.jsonl
  → Mapping created: state/issues/42.json → { session: "a1b2c3", engine: "agenticana", agent: "backend-specialist" }
  → Agent responds, session committed to git

Two days later, comment: "? Add pagination to the list endpoint"
  → Mapping loaded: state/issues/42.json
  → Session resumed: state/sessions/2026-03-18T10-30_a1b2c3.jsonl
  → Agent has FULL CONTEXT of prior conversation
  → Updated session committed to git
```

**ReasoningBank as Git-Committed Memory:**

Every successful agent decision gets recorded to `memory/reasoning-bank/decisions.json` and committed:

```json
{
  "id": "rb-019",
  "timestamp": "2026-03-18T10:30:00Z",
  "task": "Build REST API for user management",
  "agent": "backend-specialist",
  "decision": "Express + Prisma + JWT auth, RESTful routes, input validation with Zod",
  "outcome": "API deployed, all tests pass",
  "success": true,
  "tokens_used": 5200,
  "model_used": "pro",
  "tags": ["api", "rest", "backend", "prisma"]
}
```

This creates a **git-auditable decision log** — every AI decision is a committed artifact, diffable, recoverable, and visible to all collaborators.

### 3.6 Push Conflict Resolution

Identical to the proven GMI pattern — up to 10 retries with increasing backoff:

```
Attempt 1: git push origin main
  → Conflict? → git pull --rebase -X theirs
Attempt 2: wait 1s → retry
Attempt 3: wait 2s → retry
...
Attempt 10: wait 15s → retry
  → All failed? → Post comment anyway + warning about state loss
```

### 3.7 Cost Management

On GitHub Actions, every invocation consumes minutes and LLM tokens. Agenticana's existing cost-optimization infrastructure becomes critical:

| Mechanism | How It Saves |
|-----------|-------------|
| **Model Router** | Routes simple tasks to `lite`/`flash` models instead of `pro` (40% token savings) |
| **Skill Tier System** | Loads only Tier 1 (core) for simple tasks; adds Tier 2/3 only when domain matches (25% savings) |
| **ReasoningBank Fast-Path** | If a past decision has similarity ≥ 0.85, reuse it instead of full LLM invocation (60% savings) |
| **Prefix Gating** | Unprefixed content is ignored — zero Actions minutes consumed on regular issue discussions |
| **Concurrency Queuing** | One agent per issue at a time — prevents duplicate processing |

**Estimated cost per interaction:**

| Scenario | Model Tier | Actions Minutes | LLM Tokens | Est. Cost |
|----------|-----------|-----------------|------------|-----------|
| Simple question (!) | GMI (pi) | 2-5 min | ~4,000 | ~$0.02 |
| Simple routed task (?) | flash | 3-8 min | ~12,000 | ~$0.05 |
| Complex multi-agent (?) | pro | 10-30 min | ~60,000 | ~$0.30 |
| Swarm (3 agents) (?) | mixed | 15-45 min | ~120,000 | ~$0.60 |
| Simulacrum debate (?) | pro | 20-60 min | ~200,000 | ~$1.00 |

### 3.8 Security Model

**Authorization:** Workflow-level permission check (same as GMI). Only admin/maintain/write collaborators trigger the agent.

**Kill Switch:** Repository owner can disable the workflow via GitHub Actions settings (one click).

**Secrets:** All LLM API keys stored as GitHub Secrets — never committed.

**Fail-Closed:** If authorization fails, prefix is missing, or any error occurs, the agent does nothing (or adds 👎 reaction).

**Guardian Mode as PR Check:** When the Agenticana engine creates code changes on a branch, Guardian Mode runs as a separate workflow on the PR — validating with Sentinel audit, Python lint, and secret scan before merge.

---

## Part 4: Implementation Phases

### Phase 0 — Foundation (Estimated: 1-2 days)

**Goal:** Scaffold the minimal GitHub Actions runtime.

- [ ] Create `.github-agenticana-intelligence/` folder structure
- [ ] Write `lifecycle/agent.ts` — minimal orchestrator that reads events and dispatches based on prefix
- [ ] Write `lifecycle/indicator.ts` — adds 🚀 reaction on execution start
- [ ] Write workflow YAML (`.github/workflows/github-agenticana-intelligence-agent.yml`)
- [ ] Wire up `!` prefix → GMI engine (pi agent) as the first working path
- [ ] Implement session state management (`state/issues/`, `state/sessions/`)
- [ ] Implement git push retry loop (10 attempts with backoff)
- [ ] Test: Open issue with `! Hello` → agent responds

### Phase 1 — Agenticana Engine Basics (Estimated: 2-3 days)

**Goal:** Wire the `?` prefix to a single Agenticana agent.

- [ ] Write `lifecycle/agenticana-engine.ts` — reads intent, selects one agent
- [ ] Port Model Router (`router/router.js`) into `.github-agenticana-intelligence/.agenticana/router/`
- [ ] Port agent YAML specs into `.github-agenticana-intelligence/.agenticana/agents/`
- [ ] Implement label-based routing (issue label → agent selection)
- [ ] Implement NL classification fallback (keyword matching from `routing_hints`)
- [ ] Execute selected agent via LLM call with agent persona as system prompt + relevant skills as context
- [ ] Record decision to ReasoningBank and commit to git
- [ ] Test: Open issue with `? What is the architecture of this repo?` → explorer-agent responds

### Phase 2 — Multi-Agent & Swarm (Estimated: 3-5 days)

**Goal:** Enable multi-agent dispatch and swarm execution.

- [ ] Implement NL Swarm parser (extract multiple agent intents from one request)
- [ ] Implement sequential multi-agent execution (one-by-one in the same job)
- [ ] Implement parallel multi-agent execution (matrix strategy or parallel jobs)
- [ ] Aggregate multi-agent responses into a single structured issue comment
- [ ] Handle concurrent git pushes from multiple agents (enhanced retry loop)
- [ ] Test: Open issue with `? Build auth API, write tests, do security review` → 3 agents respond

### Phase 3 — Advanced Features (Estimated: 3-5 days)

**Goal:** Port Agenticana's flagship features.

- [ ] Port Logic Simulacrum — `architecture` label triggers multi-agent debate, posts consensus + ADR
- [ ] Port Guardian Mode — runs as PR check workflow, validates agent-created changes before merge
- [ ] Port Proof-of-Work — commit attestations with Trust Score in git history
- [ ] Implement ReasoningBank fast-path — skip full LLM invocation when similarity ≥ 0.85
- [ ] Implement skill tier loading — load only relevant skills per agent to minimize token usage
- [ ] Test: Open issue with `? Should we use microservices or monolith?` + label `architecture` → Simulacrum debate

### Phase 4 — Installation & Distribution (Estimated: 1-2 days)

**Goal:** Make it installable in any repository.

- [ ] Write installer script (workflow_dispatch job that downloads and installs the folder)
- [ ] Write upgrade script (semver comparison, preserves state directory)
- [ ] Create GitHub Pages deployment for documentation (`run-gitpages` job)
- [ ] Write one-line installation instructions
- [ ] Test: Run installer on a fresh repo → working dual-engine AI agent

---

## Part 5: What Changes, What Stays the Same

### What Changes (Local → Githubified)

| Dimension | Local (Current) | Githubified (Target) |
|-----------|----------------|---------------------|
| **Trigger** | User types in VS Code / CLI | User opens issue or comments with prefix |
| **Runtime** | Developer's machine | GitHub Actions runner (ubuntu-latest) |
| **Context** | VS Code workspace, open files | Full repository checkout (fetch-depth: 0) |
| **LLM interaction** | Copilot Chat / CLI scripts | agent.ts → LLM API via agent scripts |
| **Memory** | Local files (`decisions.json`, `memory.json`) | Git-committed state (diffable, auditable) |
| **Output** | VS Code editor changes, terminal output | Issue comment + git commit |
| **Session** | Ephemeral (Copilot Chat session) | Persistent (git-backed JSONL) |
| **Collaboration** | Single developer | All repo collaborators see AI interactions |
| **Auditability** | Local logs (gitignored) | Every interaction committed to git |

### What Stays the Same

| Component | Why It Transfers Directly |
|-----------|--------------------------|
| 20 agent YAML specs | Agent personas are LLM-agnostic — they define system prompts, not runtime dependencies |
| 36 skill SKILL.md files | Skills are markdown instructions — they work as LLM context in any execution environment |
| Model Router | Complexity scoring and model tier selection are pure functions — no runtime dependency |
| ReasoningBank schema | JSON with structured fields — naturally git-committable |
| Agent identities | YAML + markdown definitions are the same whether loaded in VS Code or on an Actions runner |
| MCP tool interfaces | The 11 tool schemas could be exposed to an Actions-hosted agent via function calling |

---

## Part 6: The Dual-Engine Advantage

The `.PLAN-v1.md` dual-engine architecture provides a unique advantage: users get **two AI systems in one installation**.

| Need | Engine | Why |
|------|--------|-----|
| Quick question, simple fix | GMI (`!`) | Single generalist agent, fast, low cost |
| Complex task, domain expertise needed | Agenticana (`?`) | 20 specialists, routing, memory, cost-optimized |
| Architecture decision | Agenticana (`?`) + `architecture` label | Logic Simulacrum debate → ADR committed |
| Code review | Agenticana (`?`) + `security` label | Security auditor + test engineer |
| Exploration | Agenticana (`?`) + `explore` label | Explorer agent + code archaeologist |

The `!` prefix gives GMI's proven simplicity for everyday tasks. The `?` prefix unlocks Agenticana's full power for complex, multi-domain work. Both share the same folder, the same state management, the same authorization model, and the same workflow file.

---

## Part 7: Comparison to Existing Githubified Repos

| Dimension | GMI (Native) | OpenClaw (Wrapping) | Agent Zero (Substitution) | **Agenticana (Transformation)** |
|-----------|-------------|--------------------|--------------------------|---------------------------------|
| Agents | 1 | 1 (30+ tools) | 1 (substitute) | **20 specialists** |
| Routing | None | None | None | **Label + NL + Swarm** |
| Memory | JSONL sessions | JSONL sessions | JSONL sessions | **JSONL + ReasoningBank + Patterns** |
| Model selection | Fixed | Fixed | Fixed | **Router (4 tiers)** |
| Cost optimization | None | None | None | **Router + Skill tiers + ReasoningBank fast-path** |
| Multi-agent | No | No | No | **Swarm Dispatcher** |
| AI debate | No | No | No | **Logic Simulacrum** |
| Pre-merge gate | No | No | No | **Guardian Mode** |
| Commit provenance | No | No | No | **Proof-of-Work attestations** |
| Dual engine | No | No | No | **GMI + Agenticana** |

Agenticana's Githubification would be the **most sophisticated GitHub Action–based AI mechanism** in the Githubification ecosystem — the first with multi-agent routing, cost-aware model selection, persistent decision memory, AI-driven architecture debates, and pre-merge validation.

---

## Part 8: Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Actions timeout** | Complex swarm tasks may exceed 4-hour limit | Emergency override label extends to 5 hours; break large tasks into subtasks |
| **LLM cost spiraling** | 20 agents × pro model × frequent invocations | Model Router selects cheapest adequate tier; ReasoningBank fast-path skips LLM for known decisions; prefix gating prevents accidental triggers |
| **Git push conflicts** | Multiple swarm agents push simultaneously | Proven 10-retry loop with `--rebase -X theirs`; sequential execution as fallback |
| **Agent hallucination** | Specialist agent produces incorrect output | Guardian Mode validates before merge; ReasoningBank captures past failures; human review via issue comments |
| **Complexity creep** | Full 20-agent system is hard to maintain on Actions | Phase 0-1 deliver value with single-agent routing; multi-agent is additive, not required |
| **Runner resource limits** | 2-core/7GB may be insufficient for swarm | Sequential execution uses one agent at a time; matrix strategy fans out to separate runners |

---

## Part 9: Key Architectural Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Single folder (`.github-agenticana-intelligence/`) | One installation, dual engine, clean separation from repo source |
| D2 | Prefix routing (`?` / `!`) | Natural syntax, prevents accidental triggers, easy to teach |
| D3 | Git-committed ReasoningBank | Makes every AI decision auditable, diffable, recoverable |
| D4 | Label-based agent routing | Explicit, discoverable, works with GitHub's existing label UI |
| D5 | NL classification fallback | When no label is set, the router infers intent from text |
| D6 | Sequential-first swarm | Start with sequential multi-agent execution; add parallel later |
| D7 | Bun + Python dual runtime | Bun for lifecycle scripts (TypeScript), Python for Agenticana scripts |
| D8 | Workflow-level authorization | Follows GMI's proven pattern; no sentinel file needed |
| D9 | 4-hour timeout with 5-hour override | Balances cost control with complex task completion |
| D10 | Phased implementation | Each phase delivers standalone value; no big-bang launch |

---

## Conclusion

This repository can become a GitHub Action–based mechanism by following the **Transformation strategy** documented in the `japer-technology/githubification` framework. The proven patterns from `github-minimum-intelligence` — session continuity via git, issue-driven conversation, reaction-based status, push conflict resolution, workflow-level authorization — provide the foundation. Agenticana's unique assets — 20 specialist agents, Model Router, ReasoningBank, Swarm Dispatcher, Logic Simulacrum, Guardian Mode, Proof-of-Work — provide the differentiation.

The dual-engine architecture from `.PLAN-v1.md` (GMI on `!`, Agenticana on `?`) delivers immediate value through GMI's proven simplicity while enabling Agenticana's full power for complex tasks. The four-phase implementation plan ensures each phase delivers standalone value without requiring the entire system to be built at once.

**The four GitHub primitives are sufficient:**

| Primitive | Agenticana Role |
|-----------|----------------|
| **GitHub Actions** | Runs 20 specialist agents, swarm orchestration, Logic Simulacrum debates, Guardian Mode checks |
| **Git** | Persists ReasoningBank decisions, session transcripts, Proof-of-Work attestations, agent-created code changes |
| **GitHub Issues** | Routes user requests to specialist agents via prefix + labels; displays multi-agent responses and debate outcomes |
| **GitHub Secrets** | Stores LLM API keys for 8+ providers (OpenAI, Anthropic, Gemini, xAI, OpenRouter, Mistral, Groq) |

The repository doesn't need to be rebuilt. It needs to be **transformed** — the existing agents, skills, router, memory, and scripts become the payload that a new dispatch layer delivers to GitHub Actions runners when issues are opened and comments are created.

> *"A repository is not just a place to store code. With the right loop — issues as input, actions as runtime, an LLM as reasoning, git as memory — it becomes a place where intelligence can be born, shaped, audited, and trusted."*
> — `.github-agenticana/githubification/README.md`
