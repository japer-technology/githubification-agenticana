# Agenticana v2 — Complete Usage Guide

> Everything you need to know to use Agenticana v2 on **Windows + VS Code + GitHub Copilot**.

---

## 1. First-Time Setup (Windows)

### Prerequisites
- [Node.js v20+](https://nodejs.org)
- [Python 3.11+](https://python.org)
- [VS Code](https://code.visualstudio.com)
- [GitHub Copilot](https://github.com/features/copilot) subscription

### Run Setup (One Time)
```powershell
# Open PowerShell in the Agenticana folder
cd d:\_Projects\Agenticana

# Run the setup script
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This automatically:
- Installs MCP server dependencies (`mcp/node_modules`)
- Installs `sentence-transformers` for ML embeddings
- Writes `.vscode/mcp.json` for Copilot integration

---

## 2. Enabling in VS Code + GitHub Copilot

### Step 1: Open Agenticana as a Workspace
```
File → Open Folder → d:\_Projects\Agenticana
```
VS Code will detect `.vscode/settings.json` automatically.

### Step 2: Install Recommended Extensions
When prompted by VS Code, click **"Install All"** to install:
- GitHub Copilot + GitHub Copilot Chat *(required)*
- Red Hat YAML *(for agent YAML validation)*
- Prettier, ESLint, Pylance

### Step 3: Enable the Agenticana MCP Tools in Copilot Chat

1. Open **Copilot Chat** (`Ctrl+Alt+I`)
2. Click the **Tools icon (🔧 hammer)** in the chat input bar
3. Find **"Agenticana"** in the list → toggle it **ON**
4. You'll see 11 tools available:
   - `reasoningbank_retrieve`, `reasoningbank_record`, `reasoningbank_distill`
   - `router_route`, `router_stats`
   - `agent_list`, `agent_get`, `skill_list`
   - `memory_store`, `memory_search`, `memory_consolidate`

### Step 4: Verify Copilot Instructions are Active
Copilot will automatically load `.github/copilot-instructions.md`.
You can verify by asking Copilot: *"Which agents do you have access to?"*

---

## 3. Daily Workflow

### Before Starting a Task

**Always do Phase -1 and Step 0:**

```powershell
# 1. Check if similar work was done before (ReasoningBank)
python scripts/reasoning_bank.py retrieve "your task description" --k 3

# 2. Get model/strategy recommendation (Router)
python scripts/router_cli.py "your task description"
```

Or **in Copilot Chat** (with tools enabled):
> "Before we start, check the ReasoningBank for 'build a user dashboard' and route the task."

### During the Task

Ask Copilot Chat using the agent system:
```markdown
@frontend-specialist Build a user profile card component with dark mode support.

@backend-specialist Design the REST API for user settings with rate limiting.

@debugger The /api/users endpoint returns 401 even with a valid token. Debug it.

@orchestrator I need to build a SaaS billing system. Plan it out.
```

### After Completing a Task

Always record to the ReasoningBank for future reuse:
```powershell
python scripts/reasoning_bank.py record `
  --task "Build dark mode toggle in Next.js" `
  --decision "next-themes + CSS variables on :root[data-theme=dark] + localStorage" `
  --outcome "Flicker-free, SSR-safe dark mode with system preference" `
  --success true `
  --agent "frontend-specialist" `
  --tags "dark-mode" "css" "next.js"
```

Or in Copilot Chat:
> "Record this solution to the ReasoningBank."

---

## 4. Using Copilot Chat with Agenticana Tools

### Example: Starting a New Feature
```
You: @orchestrator I need to add payment processing with Stripe to our Next.js app.

Copilot will:
1. Call reasoningbank_retrieve → check past payment patterns
2. Call router_route → recommend model/strategy
3. Ask Socratic questions (Stripe is test or live? Subscriptions or one-time?)
4. Create a payments-stripe.md plan
5. Assign tasks to backend-specialist, frontend-specialist, test-engineer
```

### Example: Debugging
```
You: The checkout page crashes with "Cannot read properties of undefined (reading 'price')"

Copilot will:
1. Call reasoningbank_retrieve → find similar null-ref patterns
2. Apply @debugger 5-layer analysis
3. Find the root cause in the data fetching layer
4. Fix with null coalescing / optional chaining
5. Record the fix to ReasoningBank
```

### Example: Quick Code Gen (Router auto-selects flash)
```
You: Add a loading spinner to the submit button when the form is submitting.

Copilot will:
1. Detect: SIMPLE task → flash model, MINIMAL strategy
2. Apply frontend-specialist rules (no purple, AAA testing)
3. Generate the component directly (no planning needed)
```

---

## 5. CLI Reference (PowerShell)

### ReasoningBank
```powershell
# Search for similar past decisions
python scripts/reasoning_bank.py retrieve "build auth with google oauth" --k 5

# Record a new decision
python scripts/reasoning_bank.py record --task "T" --decision "D" --outcome "O" --success true

# Distill patterns from decisions
python scripts/reasoning_bank.py distill

# View stats
python scripts/reasoning_bank.py stats

# Merge redundant patterns
python scripts/reasoning_bank.py consolidate
```

### Model Router
```powershell
# Get routing recommendation
python scripts/router_cli.py "implement a real-time chat feature"

# Compact one-liner output (for scripts)
python scripts/router_cli.py "fix typo" --compact
# → MODEL=lite STRATEGY=FULL TOKENS~4226 SCORE=1.0

# Show config/savings breakdown
python scripts/router_cli.py --stats
```

### Agentica Exchange (📦 New)
The Exchange allows you to pull new agents, skills, and patterns from a remote registry.

![Agentica Exchange in Action](.Agentica/logs/visuals/cli_exchange_demo.png)

```powershell
# Sync registry with remote manifest
python scripts/exchange.py sync

# List installed components
python scripts/exchange.py list

# Install a new component (agent or skill)
python scripts/exchange.py install react-expert

# Get details on an installed component
python scripts/exchange.py info react-expert
```

### Heartbeat Daemon (⚡ Autonomous)
The background daemon ensures project health (Linting, Security, Soul Distillation).

```powershell
# Start the daemon
python scripts/heartbeat_daemon.py

# Run tasks once and exit
python scripts/heartbeat_daemon.py --once
```

# Dispatch parallel tasks from a manifest
python scripts/swarm_dispatcher.py .Agentica/swarm_manifest.json

# Dispatch in SHADOW MODE (Sandbox execution + Auto-merge)
python scripts/swarm_dispatcher.py .Agentica/swarm_manifest.json --shadow
```

- **Shadow Mode**: Clones the repo to `.Agentica/shadow_sandbox/`, runs agents there, performs a Sentinel audit, and only merges back to production if no errors are found.

### Control Center Dashboard (🔐 Secure)
Monitor your workforce via a beautiful web interface.

```powershell
# Start the secure Control Center API
python scripts/dashboard_api.py
```

- **URL**: `http://127.0.0.1:8080/dashboard/index.html`
- **Security**: The dashboard is restricted to **localhost only**.
- **Auth Key**: You will be prompted for an API key. Find yours in `.Agentica/auth.key`.

### Self-Healing Sentinel (🛡️ Auto-Repair)
The autonomous system that monitors and repairs your codebase.

```powershell
# Manually trigger a healing sweep
python scripts/sentinel.py
```

- **Function**: Runs audits (lint, tests, security).
- **Action**: If a failure is detected, it automatically dispatches a **Debugger Swarm** to fix the issue.
- **Automation**: Integrated into the Heartbeat Daemon for periodic background maintenance.

### Visual Brain (🎨 Phase P9)
Automated UI verification and design auditing.

```powershell
# Run a design audit on a local or remote site
python scripts/visual_audit.py http://localhost:8080/dashboard/index.html
```

- **Output**: A "Premium Score" and detailed design feedback (contrast, alignment, aesthetics).

### Soul Bridge (🌐 Phase P10)
Cross-project intelligence synchronization.

```powershell
# Add a sibling project to the knowledge network
python scripts/soul_bridge.py add d:/_Projects/accreditex

# Sync intelligence across all connected projects
python scripts/soul_bridge.py sync
```

---

## 6. Automation & CI/CD
**Agentica v4.0 (A.I.R Edition)** is fully automated.
- **Sentinel**: Repairs code errors.
- **Bridge**: Syncs intelligence across projects.
- **Heartbeat**: Manages the schedule.

Agenticana includes a pre-configured **GitHub Actions CI** pipeline.

- **Path**: `.github/workflows/ci.yml`
- **Features**:
  - Automated `verify_all.py` on every push/PR.
  - Automatic Registry Sync check.
  - Windows-native runner environment.

---

### MCP Server (manual start)
```powershell
cd mcp
npm install   # first time only
node server.js
# → [Agenticana MCP] Server started on stdio. Tools: reasoningbank_retrieve, ...
```

---

## 6. Agent Quick Reference

Use these in Copilot Chat with `@agent-name` or just describe your task:

| Agent | When to Use | Model |
|-------|------------|-------|
| `@orchestrator` | Complex multi-domain planning | pro |
| `@frontend-specialist` | React, Next.js, UI, CSS | pro |
| `@backend-specialist` | APIs, Node.js, databases | pro |
| `@mobile-developer` | React Native, Expo | pro |
| `@database-architect` | Prisma, SQL, schemas | flash |
| `@debugger` | Any bug, error, crash | pro |
| `@security-auditor` | Auth, JWT, OWASP review | pro |
| `@devops-engineer` | Docker, CI/CD, deploy | flash |
| `@test-engineer` | Unit/E2E tests | flash |
| `@performance-optimizer` | Slow pages, bundle analysis | pro |
| `@explorer-agent` | Find files, map dependencies | flash |
| `@game-developer` | Phaser, game loops | pro |

---

## 7. VS Code Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Copilot Chat | `Ctrl+Alt+I` |
| Open Copilot inline | `Ctrl+I` |
| Open terminal | `` Ctrl+` `` |
| Run last debug config | `F5` |
| Open launch.json configs | `Ctrl+Shift+D` |

### Debug Configs (F5 → select):
- **Python: ReasoningBank CLI** → Runs `reasoning_bank.py stats`
- **Python: Router CLI** → Runs `router_cli.py "build a login system"`
- **Node: MCP Server (stdio)** → Starts MCP server for manual testing
- **Node: Router JS** → Tests the Node.js router directly

---

## 8. Token Savings — What You Get

Every request through the v2 system saves tokens:

| Scenario | Without v2 | With v2 | Savings |
|---------|-----------|---------|---------|
| Fix a typo | pro model | lite model | ~80% |
| Similar to past task (≥0.85) | Full plan | Fast path | ~60% |
| Multi-skill load | All 36 skills | 1-2 skills | ~30% |
| Average task | - | - | **~40%** |

---

## 9. How Self-Learning Works

```
Task completed
    ↓
reasoning_bank.py record --success true
    ↓
(after 5+ decisions)
distill_patterns.py
    ↓
New pattern stored in decisions.json
    ↓
Next similar task: similarity ≥ 0.85 → 🚀 Fast Path
    ↓
60% fewer tokens, skip re-planning
```

The system gets smarter every time you record a decision.

---

## 10. File Structure Reference

```
d:\_Projects\Agenticana\
├── .github/
│   └── copilot-instructions.md   ← Copilot reads this automatically
├── .vscode/
│   ├── mcp.json                  ← MCP server config for Copilot
│   ├── settings.json             ← Workspace settings + Copilot instructions
│   ├── extensions.json           ← Recommended extensions
│   └── launch.json               ← Debug configs
├── agents/                       ← 20 agents (.md rules + .yaml specs)
├── skills/                       ← 36 skills (3-tier hierarchy)
├── router/                       ← Model Router (JS)
│   ├── router.js
│   ├── complexity-scorer.js
│   ├── token-estimator.js
│   └── config.json
├── memory/
│   └── reasoning-bank/
│       ├── decisions.json        ← Past decisions (grows over time)
│       └── patterns.json        ← Distilled patterns
├── mcp/                          ← MCP Server for Copilot Tools
│   ├── server.js
│   └── tools/
├── schemas/                      ← JSON validation schemas
├── scripts/                      ← Python CLI tools
│   ├── reasoning_bank.py
│   ├── router_cli.py
│   └── distill_patterns.py
├── ARCHITECTURE.md               ← Full system map
├── GEMINI.md                     ← AI behavior rules (in rules/)
├── setup.ps1                     ← One-time Windows setup
└── requirements.txt              ← Python deps
```

---

*Agenticana v2 — Built for Windows + VS Code + GitHub Copilot*
