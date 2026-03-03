# Applicability to Agenticana

> How the Minimum Intelligence pattern maps to and contrasts with Agenticana's architecture — and a concrete path for githubification.

---

## Two Approaches to Repository-Native Intelligence

| Dimension | GitHub Minimum Intelligence | Agenticana v6.0 |
|-----------|---------------------------|-----------------|
| **Agent count** | 1 (unified agent) | 20 (specialist agents) |
| **Runtime** | GitHub Actions (serverless) | Local (VS Code, CLI, MCP) |
| **LLM interaction** | Per-issue via `pi` agent | Per-task via Copilot Chat / CLI |
| **Memory** | Git commits (session JSONL) | File-based (decisions.json, patterns.json) |
| **UI** | GitHub Issues | VS Code, terminal, MCP |
| **Identity** | AGENTS.md (single persona) | 20 YAML specs + markdown instructions |
| **Governance** | Four Laws + DEFCON levels | Guardian Mode + Sentinel |
| **Install model** | Single folder, one-command setup | Clone + setup script |
| **Execution trigger** | Issue event → Actions workflow | User command → local execution |

---

## What Agenticana Can Learn

### 1. The Issue-as-Conversation Pattern

**Minimum Intelligence:** Every GitHub Issue becomes a persistent, auditable conversation thread with the AI agent. The agent replies as comments. History is durable.

**Agenticana opportunity:** Currently, Agenticana operates through VS Code Copilot Chat or CLI commands. These are ephemeral — conversations vanish when VS Code closes. Adding issue-triggered execution would give Agenticana:
- Persistent conversation history (visible to all collaborators)
- Asynchronous collaboration (post an issue, go to bed, see the reply tomorrow)
- Auditable decision-making (every AI interaction is a comment on a public issue)

### 2. The Git-as-Memory Pattern

**Minimum Intelligence:** Every session transcript, every code change, every state update is committed to git. Memory is a property of the repository.

**Agenticana opportunity:** Agenticana's ReasoningBank stores decisions in JSON files, but these are typically committed manually. Automating the commit cycle (after every agent interaction) would make Agenticana's memory truly persistent and auditable.

### 3. The Folder-as-Product Pattern

**Minimum Intelligence:** The entire system is one folder (`.github-minimum-intelligence/`) that can be dropped into any repo. Nothing else is needed.

**Agenticana opportunity:** Agenticana could be packaged as a `.github-agenticana/` folder that self-installs its workflow triggers, issue templates, and MCP configuration. The current structure is close to this — the main gap is the GitHub Actions workflow that triggers execution.

### 4. The Event-Driven Cognition Pattern

**Minimum Intelligence:** A social event (issue comment) triggers computation (Actions workflow), which produces artifacts (commits, comments), which trigger future social events (user reads reply).

**Agenticana opportunity:** Agenticana's 20 agents could each be triggerable by different issue labels or event types. For example:
- Label `security-audit` → runs security-auditor agent
- Label `performance` → runs performance-optimizer agent
- Label `architecture` → triggers Logic Simulacrum debate

---

## What Minimum Intelligence Can Learn from Agenticana

### 1. Multi-Agent Specialization

Minimum Intelligence uses a single agent. Agenticana demonstrates that specialized agents produce better results in their domains. A combined system could route issue requests to the most appropriate specialist.

### 2. Agent Debates (Simulacrum)

Minimum Intelligence conversations are one-agent dialogues. Agenticana's Logic Simulacrum enables multi-agent debates where specialists argue different perspectives before producing a recommendation. This could be adapted for issue-triggered architectural decisions.

### 3. Quality Gates (Guardian Mode)

Minimum Intelligence commits directly to the default branch. Agenticana's Guardian Mode provides pre-commit validation. A combined system could have the Actions agent create a PR instead of pushing directly, then run Guardian Mode checks.

### 4. Cost-Aware Routing

Agenticana's Model Router selects the optimal model based on task complexity (flash for simple, pro for complex). Minimum Intelligence uses a single configured model. Integrating routing into the Actions workflow could significantly reduce LLM costs.

---

## A Concrete Path: Githubifying Agenticana

### Phase 1: Actions Workflow for Agent Execution

Create a GitHub Actions workflow that triggers Agenticana agents on issue events:

```yaml
name: agenticana-agent
on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: write

jobs:
  run-agent:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'agenticana')
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd mcp && npm install
      - name: Route and execute
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/agent_cli.py @auto "$ISSUE_BODY"
```

### Phase 2: Issue→Agent Routing

Map issue labels to Agenticana agents:

| Label | Agent | Action |
|-------|-------|--------|
| `agenticana` | Auto-routed | Run Model Router to select agent |
| `security` | security-auditor | Security review |
| `performance` | performance-optimizer | Performance audit |
| `architecture` | orchestrator | Architecture planning + Simulacrum |
| `debug` | debugger | Bug investigation |
| `frontend` | frontend-specialist | UI/component work |
| `backend` | backend-specialist | API/server work |

### Phase 3: State Persistence via Git

Adapt Agenticana's memory system for git-committed persistence:

```
.github-agenticana/state/
├── issues/           # Issue → agent session mappings
├── sessions/         # Agent execution transcripts
├── decisions/        # ReasoningBank decisions (auto-committed)
└── attestations/     # Proof-of-Work attestations
```

### Phase 4: Identity and Governance

Create an Agenticana-specific governance framework:

```
.github-agenticana/governance/
├── AGENTS.md         # Master agent identity document
├── FOUR-LAWS.md      # Ethical foundation
├── DEFCON.md         # Readiness level definitions
└── SECURITY.md       # Self-assessment
```

---

## Architecture Comparison: Current vs. Githubified

### Current Agenticana (Local-First)

```
Developer → VS Code → Copilot Chat → MCP Server → Agenticana Agents
                                                        │
                                                   Local files
```

### Githubified Agenticana (Actions-First)

```
Collaborator → GitHub Issue → Actions Workflow → Agent Router
                                                      │
                                              ┌───────┼───────┐
                                              ▼       ▼       ▼
                                          Agent 1  Agent 2  Agent N
                                              │       │       │
                                              └───────┼───────┘
                                                      │
                                               Git Commit + Push
                                                      │
                                               Issue Comment Reply
```

### Hybrid Agenticana (Both)

```
                    ┌─── VS Code (local dev) ───────────┐
Developer ──────────┤                                    ├──▶ Agenticana Agents
                    └─── GitHub Issue (async collab) ────┘         │
                                                              Git Memory
```

The hybrid model is the most powerful: developers use VS Code for real-time local work, and GitHub Issues for asynchronous collaboration and long-running tasks.

---

## Summary

The core lesson from GitHub Minimum Intelligence is that **a repository can serve as the complete operating environment for an AI agent** — input, compute, memory, identity, and governance all expressed through existing GitHub primitives.

For Agenticana, this means:
1. **Add an Actions workflow** to make the 20 agents triggerable via issues
2. **Auto-commit agent state** after every interaction for git-backed memory
3. **Route issues to specialists** using label-based agent selection
4. **Create a governance layer** with Four Laws, DEFCON levels, and self-assessment
5. **Maintain the local experience** as a complementary (not replaced) interface

The result would be a system that works both as a local VS Code companion AND as an autonomous repository-native agent — truly executing the repo as a mind.
