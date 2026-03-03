# Specification v1: GitHub as AI Infrastructure for Agenticana

> **Version:** 1.0.0 | **Date:** 2026-03-03
> How a repository containing the source of Agenticana implements GitHub as AI Infrastructure — derived from the [githubification analysis](../githubification/) of `japer-technology/github-minimum-intelligence`.

---

## Executive Summary

GitHub Minimum Intelligence proved that a single folder, a workflow file, and an LLM API key can turn any repository into an interactive AI collaborator. Every GitHub primitive — Issues, Actions, Git commits, Secrets, Markdown files, branch protection — maps to a layer of intelligence: input, compute, memory, credentials, identity, and governance.

This specification defines how `github-agenticana`, which already contains 20 specialist agents, an MCP server, a model router, a reasoning bank, and a full governance framework, can implement the same pattern at scale — making the repository itself the runtime, the memory, and the interface for a multi-agent AI system.

The core thesis:

> **A repository is not just a place to store code. With the right loop — issues as input, Actions as runtime, an LLM as reasoning, git as memory — it becomes a place where intelligence can be born, shaped, audited, and trusted.**

---

## 1. Architectural Foundation

### 1.1 The GitHub Primitives Stack

Every layer of intelligence maps to an existing GitHub primitive. No new infrastructure is required.

| Primitive | Infrastructure Role | Agenticana Implementation |
|-----------|-------------------|--------------------------|
| **GitHub Issues** | Conversational UI (input/output) | Issue → Agent routing via labels; comments as bidirectional dialogue |
| **GitHub Actions** | Compute runtime (execution) | Workflow triggers on issue events; runs agent CLI in ubuntu-latest runner |
| **Git commits** | Persistent memory (state) | Session transcripts, reasoning bank decisions, agent state auto-committed |
| **Repository Secrets** | Credential store (security) | LLM API keys (Gemini, OpenAI, Anthropic), GITHUB_TOKEN |
| **Markdown files** | Identity and governance (configuration) | 20 agent specs (.md + .yaml), AGENTS.md, governance framework |
| **Branch protection** | Access control (authorization) | Collaborator-only agent invocation; PR-gated agent commits |

### 1.2 The Closed Loop

The system operates as a self-sustaining closed loop inside the repository:

```
┌──────────────────────────────────────────────────────────────────────┐
│                     GITHUB REPOSITORY                                │
│                                                                      │
│  ┌──────────────┐    ┌─────────────────┐    ┌────────────────────┐  │
│  │ GitHub Issues │───▶│ GitHub Actions   │───▶│ Git Commits        │  │
│  │ (Input/Output)│    │ (Agent Runtime)  │    │ (Memory/State)     │  │
│  └──────┬───────┘    └────────┬────────┘    └───────┬────────────┘  │
│         │                     │                      │               │
│         │         ┌───────────┼───────────┐          │               │
│         │         ▼           ▼           ▼          │               │
│         │    Agent Router  Specialist  Reasoning     │               │
│         │    (model/agent) Agent(s)    Bank          │               │
│         │         │           │           │          │               │
│         │         └───────────┼───────────┘          │               │
│         │                     │                      │               │
│         │              ┌──────▼───────┐              │               │
│         │              │ LLM Provider  │              │               │
│         │              │ (Reasoning)   │              │               │
│         │              └──────┬───────┘              │               │
│         │                     │                      │               │
│         ◀─────────────────────┴──────────────────────┘               │
│                    (Reply posted to Issue)                            │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.3 Event-Driven Cognition

The fundamental pattern is event-driven cognition:

1. A **social event** (issue opened, comment posted, label applied) occurs
2. **Infrastructure** transforms it into computation (Actions workflow triggers)
3. **Computation** produces artifacts (commits, comments, code changes)
4. **Artifacts** trigger future social events (user reads reply, collaborators review)

This creates a self-sustaining loop where the repository continuously accumulates intelligence through the interaction of human intent and machine execution.

---

## 2. Execution Model

### 2.1 Primary Workflow: `github-agenticana-agent.yml`

The central workflow that makes the repository alive:

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
  actions: write

concurrency:
  group: agenticana-${{ github.repository }}-issue-${{ github.event.issue.number }}
  cancel-in-progress: false

jobs:
  run-agent:
    runs-on: ubuntu-latest
    if: >-
      contains(github.event.issue.labels.*.name, 'agenticana')
      && (
        github.event_name == 'issues'
        || (github.event_name == 'issue_comment'
            && !endsWith(github.event.comment.user.login, '[bot]'))
      )
    timeout-minutes: 15
    steps:
      - name: Authorize
        id: authorize
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          PERM=$(gh api "repos/${{ github.repository }}/collaborators/${{ github.actor }}/permission" \
            --jq '.permission' 2>/dev/null || echo "none")
          if [[ "$PERM" != "admin" && "$PERM" != "maintain" && "$PERM" != "write" ]]; then
            echo "::error::Unauthorized: ${{ github.actor }} has '$PERM' permission"
            exit 1
          fi

      - name: Reject
        if: ${{ failure() && steps.authorize.outcome == 'failure' }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api "repos/${{ github.repository }}/issues/${{ github.event.issue.number }}/reactions" \
            -f content="-1" || true

      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.repository.default_branch }}
          fetch-depth: 0

      - name: Indicate
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if [ "${{ github.event_name }}" = "issue_comment" ]; then
            TARGET="repos/${{ github.repository }}/issues/comments/${{ github.event.comment.id }}/reactions"
          else
            TARGET="repos/${{ github.repository }}/issues/${{ github.event.issue.number }}/reactions"
          fi
          gh api "$TARGET" -f content="rocket" || true

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            mcp/node_modules
          key: agenticana-deps-${{ hashFiles('requirements.txt', 'mcp/package.json') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd mcp && npm install

      - name: Route and execute agent
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          COMMENT_BODY: ${{ github.event.comment.body }}
          EVENT_NAME: ${{ github.event_name }}
        run: |
          python scripts/agent_cli.py @auto "${COMMENT_BODY:-$ISSUE_BODY}"

      - name: Commit state
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          if ! git diff --cached --quiet; then
            git commit -m "agenticana: work on issue #${{ github.event.issue.number }}"
            for i in $(seq 1 10); do
              git push origin HEAD:${{ github.event.repository.default_branch }} && break
              git pull --rebase -X theirs origin ${{ github.event.repository.default_branch }}
              sleep $((i * 2))
            done
          fi

      - name: Post reply
        if: always()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          OUTCOME=${{ job.status }}
          if [ "$OUTCOME" = "success" ]; then
            REACTION="+1"
          else
            REACTION="-1"
          fi
          if [ "${{ github.event_name }}" = "issue_comment" ]; then
            gh api "repos/${{ github.repository }}/issues/comments/${{ github.event.comment.id }}/reactions" \
              -f content="$REACTION" || true
          else
            gh api "repos/${{ github.repository }}/issues/${{ github.event.issue.number }}/reactions" \
              -f content="$REACTION" || true
          fi
```

### 2.2 Workflow Design Decisions

| Decision | Rationale | Source Insight |
|----------|-----------|---------------|
| **Label-gated triggers** (`agenticana` label required) | Prevents every issue from consuming Actions minutes | [Cost Model](../githubification/github-actions-cost-model.md) §3 |
| **Bot comment filtering** (`!endsWith(..., '[bot]')`) | Prevents infinite loops where the agent's own replies retrigger execution | [Execution Model](../githubification/execution-model.md) §Bot Comment Filtering |
| **Per-issue concurrency groups** | Serializes processing per issue while allowing cross-issue parallelism | [Execution Model](../githubification/execution-model.md) §Concurrency Control |
| **cancel-in-progress: false** | Queues new comments instead of cancelling running agents | [Execution Model](../githubification/execution-model.md) §Concurrency Control |
| **Collaborator-only authorization** | Reuses GitHub's existing trust boundary; no parallel ACL surface | [Execution Model](../githubification/execution-model.md) §Step 1 |
| **Full checkout (fetch-depth: 0)** | Agent needs complete repo context and git history for memory | [Execution Model](../githubification/execution-model.md) §Step 3 |
| **🚀 reaction before install** | Immediate visual feedback; user knows the agent is working | [Lifecycle Deep Dive](../githubification/lifecycle-deep-dive.md) §Phase 1 |
| **Dependency caching** | Reduces install time from ~45s to ~5s on cache hit | [Cost Model](../githubification/github-actions-cost-model.md) §Optimization |
| **Push retry with backoff** | Handles concurrent pushes from multiple issue agents | [Memory and State](../githubification/memory-and-state.md) §Push Conflict Resolution |
| **timeout-minutes: 15** | Caps runaway agents; typical run is 1-6 minutes | [Cost Model](../githubification/github-actions-cost-model.md) §Timeouts |

### 2.3 The Three-Phase Lifecycle

Adapted from Minimum Intelligence's lifecycle pattern to Agenticana's multi-agent architecture:

```
Phase 1: Indicate    → 🚀 reaction (immediate feedback, before install)
Phase 2: Install     → pip install + npm install (cached for speed)
Phase 3: Route + Run → Model Router → Agent Selection → LLM reasoning + tool execution → commit + reply
```

**Phase 3 expands for Agenticana:**

```
3a. Read issue/comment body and labels
3b. Query ReasoningBank for similar past decisions (fast-path if similarity > 0.85)
3c. Run Model Router to select optimal model tier (flash/pro/pro-extended)
3d. Route to specialist agent based on label or auto-detection
3e. Agent executes with LLM reasoning + tool loop
3f. Record decision to ReasoningBank
3g. Commit all state changes to git
3h. Post reply as issue comment
```

---

## 3. Multi-Agent Routing via Issue Labels

### 3.1 Label-to-Agent Mapping

Agenticana's 20 specialist agents are exposed through issue labels. This is the key differentiator from Minimum Intelligence's single-agent model.

| Issue Label | Agent | Complexity Tier | Action |
|-------------|-------|----------------|--------|
| `agenticana` | Auto-routed | Varies | Model Router selects agent based on issue content |
| `security` | security-auditor | MODERATE | Security review, vulnerability analysis |
| `penetration-test` | penetration-tester | COMPLEX | Offensive security testing |
| `performance` | performance-optimizer | MODERATE | Performance audit, bundle analysis |
| `architecture` | orchestrator | COMPLEX | Architecture planning + Simulacrum debate |
| `debug` | debugger | MODERATE | Bug investigation, root cause analysis |
| `frontend` | frontend-specialist | MODERATE | UI/component work, React, CSS |
| `backend` | backend-specialist | MODERATE | API/server work, Node.js, Express |
| `mobile` | mobile-developer | COMPLEX | React Native, Expo, iOS/Android |
| `database` | database-architect | MODERATE | Schema design, migrations, Prisma |
| `devops` | devops-engineer | MODERATE | Docker, CI/CD, GitHub Actions |
| `testing` | test-engineer | SIMPLE | Unit tests, E2E tests, coverage |
| `qa` | qa-automation-engineer | MODERATE | Test automation, quality gates |
| `docs` | documentation-writer | SIMPLE | Documentation generation |
| `explore` | explorer-agent | SIMPLE | Codebase exploration, discovery |
| `archaeology` | code-archaeologist | SIMPLE | Legacy code analysis |
| `game` | game-developer | COMPLEX | Game development |
| `seo` | seo-specialist | SIMPLE | SEO analysis and optimization |
| `plan` | project-planner | COMPLEX | Project planning, roadmapping |
| `product` | product-manager | MODERATE | Product strategy, prioritization |

### 3.2 Auto-Routing Logic

When the `agenticana` label is applied without a specialist label, the agent CLI performs automatic routing:

```
Issue body → Model Router (complexity-scorer.js)
                │
                ├─ Extract keywords → match against agent routing_hints.trigger_keywords
                ├─ Score complexity (1-10)
                ├─ Select model tier (flash/pro/pro-extended)
                └─ Return { agent, model, strategy, skills }
```

This leverages Agenticana's existing `router/router.js` and per-agent `routing_hints` in YAML specs.

### 3.3 Multi-Agent Debates via Labels

When the `architecture` label is applied, the orchestrator agent can invoke the Simulacrum pattern — a multi-agent debate where specialists argue different perspectives:

```
Issue with `architecture` label
    │
    ▼
orchestrator agent invoked
    │
    ▼
simulacrum.py triggered with relevant agents
    │
    ├─ backend-specialist: argues for API-first approach
    ├─ security-auditor: argues for threat model considerations
    ├─ performance-optimizer: argues for latency constraints
    └─ database-architect: argues for data model implications
    │
    ▼
Synthesized recommendation posted as issue comment
```

---

## 4. Memory and State Persistence

### 4.1 Git as the Memory Layer

Every agent interaction produces state that is committed to the repository. Memory is not a feature — it is a property of the repository.

```
.github-agenticana/state/
├── issues/                    # Issue → session mappings
│   ├── 1.json                 # { issueNumber, agent, sessionPath, updatedAt }
│   ├── 2.json
│   └── ...
├── sessions/                  # Agent execution transcripts
│   ├── 1709510400.jsonl       # JSONL: each line is a conversation event
│   └── ...
└── attestations/              # Proof-of-Work attestations (optional)
    └── ...
```

### 4.2 Session Continuity

The issue-to-session mapping provides conversation continuity across multiple comments:

**New issue (first message):**
1. User opens issue #42 with `agenticana` label
2. Agent checks: does `state/issues/42.json` exist? → No
3. Agent runs without prior context → fresh conversation
4. Agent creates `state/sessions/<timestamp>.jsonl`
5. Agent writes `state/issues/42.json` mapping
6. Agent commits all state

**Follow-up comment (continuing conversation):**
1. User comments on issue #42
2. Agent reads `state/issues/42.json` → finds session path
3. Agent loads session history → LLM receives full conversation context
4. Agent appends to existing session file
5. Agent updates mapping with new timestamp
6. Agent commits updated state

### 4.3 ReasoningBank Integration

Agenticana's existing ReasoningBank (`memory/reasoning-bank/decisions.json`) is auto-committed after every agent interaction:

```
Agent completes task
    │
    ├─ Record decision: python scripts/reasoning_bank.py record \
    │     --task "..." --decision "..." --outcome "..." --success true
    │
    ├─ Distill patterns (periodically): python scripts/distill_patterns.py
    │
    └─ git add -A && git commit → reasoning bank decisions and patterns committed
```

This transforms the ReasoningBank from a local-only feature into a git-backed, auditable, shared knowledge base.

### 4.4 Memory Properties Inherited from Git

| Property | Meaning for Agent Memory |
|----------|-------------------------|
| **Durability** | Persists as long as the repository exists |
| **Auditability** | `git log` shows every memory change with timestamps |
| **Diffability** | `git diff` reveals exactly what changed between sessions |
| **Recoverability** | `git revert` can restore any prior state |
| **Branchability** | Fork a conversation by branching the repo |
| **Attribution** | Every memory write has an author (the agent's commit identity) |
| **Distribution** | Cloning the repo clones the entire memory |

### 4.5 Push Conflict Resolution

When multiple issue agents run concurrently and try to push:

```
Attempt N: git push
  → Fails (remote has new commits from another agent)
  → git pull --rebase -X theirs origin <default-branch>
  → Wait N*2 seconds
  → Retry (up to 10 attempts, max ~110 seconds total wait)
```

The `-X theirs` strategy is safe because:
- Session files are per-issue (no overlap)
- Issue mappings are per-issue (no overlap)
- ReasoningBank is append-only (merge conflicts unlikely)

---

## 5. Identity and Governance

### 5.1 Identity as Versioned Configuration

Agent identity is stored as editable files in the repository — governed by the same PR process as code:

```
.github-agenticana/governance/
├── AGENTS.md                 # Master agent identity document
├── FOUR-LAWS.md              # Ethical foundation (Asimov-adapted)
├── DEFCON.md                 # Readiness level definitions (1-5)
├── SECURITY-ASSESSMENT.md    # Self-audit of known risks
└── APPEND_SYSTEM.md          # Behavioral constitution (appended to all LLM prompts)
```

Identity properties:
- **Diffable** — `git diff` shows personality and governance changes
- **Reviewable** — PRs can modify agent behavior with review gates
- **Attributable** — `git blame` shows who changed what
- **Reversible** — `git revert` can undo behavioral changes
- **Branchable** — fork the repo to A/B test different agent configurations

### 5.2 The Four Laws of AI

The ethical foundation, inherited from Minimum Intelligence and adapted for a multi-agent system:

| Law | Principle | Agenticana Application |
|-----|-----------|----------------------|
| **Zeroth** | Protect humanity as a whole | No monopolistic patterns; open source remains open; interoperability preserved |
| **First** | Do no harm to humans or communities | Never endanger safety, privacy, or civil rights; refuse malicious code generation |
| **Second** | Obey human operators (unless conflicts with First) | Faithfully execute instructions; be transparent about limitations |
| **Third** | Preserve own integrity (unless conflicts with First or Second) | Maintain security and audit trails; resist corruption |

### 5.3 DEFCON Readiness Levels

Progressive capability lockdown for risk management:

| Level | Name | Agent Capabilities |
|-------|------|--------------------|
| **DEFCON 1** | Maximum Readiness | All operations suspended. No file modifications, no tool use, no code execution. |
| **DEFCON 2** | High Readiness | Read-only, advisory only. No file modifications. |
| **DEFCON 3** | Increased Readiness | Read-only. Explain planned changes and await human approval before any write. |
| **DEFCON 4** | Above Normal | Full capability with elevated discipline. Confirm intent before every write. |
| **DEFCON 5** | Normal | Standard operations. All capabilities available per agent spec. |

**Per-agent DEFCON overrides:** Each of the 20 agents can operate at a different DEFCON level based on risk profile. For example:
- `penetration-tester` defaults to DEFCON 3 (explain before acting)
- `documentation-writer` defaults to DEFCON 5 (full autonomy for docs)
- `security-auditor` defaults to DEFCON 4 (elevated discipline)

### 5.4 Security Self-Assessment

Radical transparency about known risks (adapted from Minimum Intelligence):

| ID | Severity | Finding | Mitigation |
|----|----------|---------|------------|
| SEC-001 | 🔴 Critical | Repository write access via GITHUB_TOKEN | Scope permissions in workflow YAML; use branch protection |
| SEC-002 | 🔴 Critical | Unrestricted network egress from runner | Limit to known LLM API endpoints via firewall rules |
| SEC-003 | 🟠 High | Passwordless sudo on runner | Agent code should never require sudo; add linting check |
| SEC-004 | 🔴 Critical | LLM API keys exposed in environment | Use repository secrets; never log env vars |
| SEC-005 | 🟠 High | No branch protection on default branch | Enable branch protection; require PR reviews for agent commits |
| SEC-006 | 🟠 High | Agent can self-modify workflow files | Exclude `.github/workflows/` from agent write paths |
| SEC-007 | 🟡 Medium | Multiple third-party dependencies | Pin versions; audit lockfiles; use dependabot |
| SEC-008 | 🟠 High | Concurrent agents may produce conflicting commits | Push retry with `-X theirs` rebase strategy |

---

## 6. Cost Model

### 6.1 The Pay-Per-Think Economics

The "mind" only exists when it is thinking. Each thought is a discrete GitHub Actions job:
- Starts from nothing (fresh VM)
- Loads its memory (git checkout)
- Thinks (LLM + tool loop)
- Saves its memory (git commit + push)
- Disappears (VM destroyed)

**Cost equation:**
```
Cost of Intelligence = GitHub Actions Minutes + LLM API Calls
```

Both scale linearly. No base cost, no idle infrastructure charge.

### 6.2 Per-Interaction Cost Estimates

| Scenario | Duration | Actions Cost | LLM Cost (est.) | Total |
|----------|----------|-------------|-----------------|-------|
| Simple question (flash model) | ~1 min | $0.008 | $0.01-0.05 | ~$0.02-0.06 |
| Code review (pro model) | ~2-3 min | $0.016-0.024 | $0.05-0.20 | ~$0.07-0.22 |
| Code generation (pro model) | ~3-5 min | $0.024-0.040 | $0.10-0.50 | ~$0.12-0.54 |
| Architecture debate (simulacrum) | ~5-10 min | $0.040-0.080 | $0.20-1.00 | ~$0.24-1.08 |

### 6.3 Monthly Projections

| Usage Pattern | Interactions/Day | Monthly Minutes | Monthly Actions Cost |
|--------------|-----------------|-----------------|---------------------|
| Light (1 developer) | 5 | 300-450 | Free tier (2,000 min) |
| Moderate (small team) | 20 | 1,200-1,800 | Free tier |
| Heavy (active team) | 50 | 3,000-4,500 | $0-12 overage |
| Intense (full reliance) | 100+ | 6,000-9,000 | $24-48 overage |

### 6.4 Agenticana-Specific Cost Optimizations

| Optimization | Mechanism | Estimated Savings |
|-------------|-----------|------------------|
| **Model Router** | Route simple tasks to flash model instead of pro | ~40% on simple tasks |
| **ReasoningBank fast-path** | Skip full agent execution when similarity > 0.85 | ~60% on repeated patterns |
| **Dependency caching** | Cache pip and npm installs across runs | ~30-40 seconds per run |
| **Label-gating** | Only trigger on `agenticana`-labeled issues | 100% savings on non-agent issues |
| **Timeout caps** | Prevent runaway agents from burning minutes | Bounded worst-case cost |

---

## 7. Issue Templates

### 7.1 Chat Template

```markdown
---
name: "🤖 Agenticana Chat"
about: "Chat with any of the 20 Agenticana specialist agents"
title: ""
labels: ["agenticana"]
---

**What do you need help with?**

<!-- Describe your task. The agent will auto-route to the best specialist. -->
<!-- Add a specialist label (e.g., `security`, `frontend`, `backend`) for direct routing. -->
```

### 7.2 Architecture Review Template

```markdown
---
name: "🏗️ Architecture Review"
about: "Trigger a multi-agent Simulacrum debate on an architecture question"
title: "[Architecture] "
labels: ["agenticana", "architecture"]
---

**Architecture Question:**

<!-- Describe the architectural decision or trade-off you want the agents to debate. -->

**Context:**

<!-- Provide relevant constraints, requirements, or existing design decisions. -->
```

### 7.3 Security Audit Template

```markdown
---
name: "🔒 Security Audit"
about: "Request a security audit from the security-auditor agent"
title: "[Security] "
labels: ["agenticana", "security"]
---

**What should be audited?**

<!-- Describe the component, feature, or codebase area to audit. -->

**Specific concerns (optional):**

<!-- Any known risks or areas of concern. -->
```

---

## 8. Hybrid Execution Model

### 8.1 Architecture: Local + Cloud

The specification preserves Agenticana's existing local experience while adding cloud-native execution:

```
                     ┌─── VS Code Copilot Chat (real-time local dev) ──┐
                     │     └─ MCP Server ─ 11 tools                    │
Developer ──────────┤                                                  ├──▶ Agenticana Agents
                     │                                                  │         │
                     └─── GitHub Issue (async cloud collaboration) ─────┘    Git Memory
                           └─ Actions Workflow ─ Agent CLI                (shared state)
```

### 8.2 Shared State Across Interfaces

Both interfaces read from and write to the same state:

| State Component | Local (VS Code/MCP) | Cloud (Actions) |
|----------------|---------------------|-----------------|
| ReasoningBank decisions | Read/write via MCP tools | Read/write via CLI scripts |
| ReasoningBank patterns | Read via MCP tools | Read/write via CLI scripts |
| Agent YAML specs | Read via MCP tools | Read via filesystem |
| Session transcripts | Not applicable (ephemeral) | Read/write via state/ directory |
| Issue mappings | Not applicable | Read/write via state/ directory |
| Skill definitions | Read via MCP tools | Read via filesystem |

### 8.3 When to Use Each Interface

| Use Case | Interface | Why |
|----------|-----------|-----|
| Real-time coding assistance | VS Code (local) | Immediate feedback, IDE integration |
| Asynchronous code review | GitHub Issue (cloud) | Collaborators see results without IDE |
| Long-running architecture debates | GitHub Issue (cloud) | Simulacrum debate may take 5-10 minutes |
| Overnight batch processing | GitHub Issue (cloud) | Post issue, review results tomorrow |
| Shared knowledge building | Both | ReasoningBank updated from both interfaces |
| Audit trail required | GitHub Issue (cloud) | Every interaction is a visible issue comment |

---

## 9. Implementation Phases

### Phase 1: Foundation (Actions Workflow + Agent CLI Integration)

**Goal:** Make the 20 agents triggerable via GitHub Issues.

**Deliverables:**
- [ ] `.github/workflows/github-agenticana-agent.yml` — the primary workflow
- [ ] Adapt `scripts/agent_cli.py` to accept issue body as input and post reply as issue comment
- [ ] State directory structure: `.github-agenticana/state/issues/`, `.github-agenticana/state/sessions/`
- [ ] Issue-to-session mapping logic in the workflow
- [ ] Push retry with conflict resolution

**Verification:** Open an issue with the `agenticana` label. Agent responds as a comment. State is committed.

### Phase 2: Multi-Agent Routing (Labels + Router)

**Goal:** Route issues to specialist agents via labels and auto-detection.

**Deliverables:**
- [ ] Label-to-agent mapping configuration
- [ ] Integration of `router/router.js` for auto-routing when only `agenticana` label is present
- [ ] Per-agent YAML `routing_hints.trigger_keywords` matched against issue content
- [ ] Issue templates for common agent interactions (chat, architecture, security)

**Verification:** Open an issue with `security` label. Security-auditor agent responds. Open an issue with only `agenticana` label. Router auto-selects the appropriate agent.

### Phase 3: Persistent Memory (Git-Backed State)

**Goal:** Auto-commit all agent state after every interaction.

**Deliverables:**
- [ ] ReasoningBank decisions auto-committed after each agent run
- [ ] Session transcripts committed in JSONL format
- [ ] Issue-to-session mapping enables multi-turn conversations
- [ ] Pattern distillation runs periodically (or after N interactions)

**Verification:** Interact with the same issue multiple times. Agent remembers prior conversation context. ReasoningBank shows new decisions in git log.

### Phase 4: Governance Layer (Identity + DEFCON + Four Laws)

**Goal:** Establish the governance framework for autonomous agent operation.

**Deliverables:**
- [ ] `.github-agenticana/governance/AGENTS.md` — master identity
- [ ] `.github-agenticana/governance/FOUR-LAWS.md` — ethical foundation
- [ ] `.github-agenticana/governance/DEFCON.md` — readiness levels with per-agent overrides
- [ ] `.github-agenticana/governance/SECURITY-ASSESSMENT.md` — self-audit
- [ ] `.github-agenticana/governance/APPEND_SYSTEM.md` — behavioral constitution injected into all agent prompts

**Verification:** Agent responses reflect governance constraints. DEFCON level changes are visible in git history. Security assessment is honest about known risks.

### Phase 5: Optimization (Caching, Cost Control, Monitoring)

**Goal:** Reduce cost and improve reliability.

**Deliverables:**
- [ ] Dependency caching in workflow
- [ ] Model Router integration for cost-optimal model selection
- [ ] ReasoningBank fast-path for repeated patterns
- [ ] Timeout enforcement (15 min default, configurable per agent)
- [ ] Self-hosted runner configuration option
- [ ] Monitoring: workflow run duration and success rate tracking

**Verification:** Cached runs complete 30-40 seconds faster. Flash model used for simple queries. Fast-path triggers on known patterns.

---

## 10. What Makes This Different from Minimum Intelligence

| Dimension | Minimum Intelligence | Agenticana (This Specification) |
|-----------|---------------------|-------------------------------|
| **Agent count** | 1 unified agent | 20 specialists with auto-routing |
| **Routing** | None (single agent) | Label-based + Model Router + keyword matching |
| **Model selection** | Fixed per config | Dynamic per task via complexity scoring |
| **Memory** | Session JSONL only | Session JSONL + ReasoningBank + pattern distillation |
| **Multi-agent debates** | Not supported | Simulacrum pattern via orchestrator |
| **Governance** | AGENTS.md + APPEND_SYSTEM.md | Four Laws + DEFCON + per-agent overrides + self-assessment |
| **Local experience** | None (Actions-only) | VS Code + MCP + CLI preserved as complementary interface |
| **Cost optimization** | Manual model selection | Automated routing, fast-path, caching |
| **Tool runtime** | Bun + pi agent (TypeScript) | Python + Node.js + MCP server |
| **Skill system** | Single skills/ directory | 3-tier hierarchy (Core/Domain/Utility) with budget-aware loading |

---

## 11. Sovereignty Guarantees

This specification inherits and extends the sovereignty model from Minimum Intelligence:

| Concern | How Addressed |
|---------|--------------|
| **Data sovereignty** | Code never leaves repo/runner infrastructure; LLM calls are the only external communication |
| **Auditability** | Every agent action is a git commit with full diff; every conversation is an issue comment |
| **Vendor lock-in** | LLM provider is configurable (Gemini, OpenAI, Anthropic, Groq, OpenRouter); agent code is open source |
| **Access control** | GitHub collaborator permissions gate agent invocation; branch protection gates agent commits |
| **Reproducibility** | Given the same model + config + repo state, the agent produces deterministic pipeline execution |
| **Offline capability** | Runs anywhere you can host a runner and reach an LLM endpoint |
| **Identity governance** | Agent personality is diffable, reviewable, attributable, and reversible via git |
| **Cost transparency** | Pay-per-think model with no hidden charges; Actions minutes and LLM costs are measurable |

---

## 12. Summary

This specification defines how `github-agenticana` implements **GitHub as AI Infrastructure** — transforming a repository from a code store into a living system where 20 specialist agents can be invoked via issues, reason with LLMs, commit their state to git, and respond as collaborators.

The key insight from the githubification analysis:

> A repository can serve as the complete operating environment for an AI agent — input, compute, memory, identity, and governance all expressed through existing GitHub primitives.

For Agenticana, this means:

1. **An Actions workflow** makes the 20 agents triggerable via issues
2. **Issue labels** route to specialist agents or auto-detect via the Model Router
3. **Git commits** provide persistent, auditable, recoverable agent memory
4. **The Four Laws + DEFCON levels** govern agent behavior with graduated trust
5. **The local VS Code experience** is preserved as a complementary interface
6. **The cost model** is pay-per-think with aggressive optimization via model routing and caching

The result is a system that works both as a local VS Code companion **and** as an autonomous, repository-native, multi-agent AI collaborator — executing the repo as a mind.
