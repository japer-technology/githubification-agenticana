# Specification v2: Multi-Agent Debates via GitHub Infrastructure

> **Version:** 2.0.0 | **Date:** 2026-03-03 | **Evolves:** [specification-v1](specification-v1.md)
> Running the Simulacrum pattern via the orchestrator in a single GitHub Actions run — turning multi-agent debates into a first-class primitive of the repository-as-runtime.

---

## Executive Summary

Specification v1 established that `github-agenticana` can use GitHub Issues as input, Actions as runtime, git as memory, and Markdown as identity — making the repository a living multi-agent system. It mentioned Simulacrum debates only as a side-effect of the `architecture` label.

**This specification promotes multi-agent debates to a first-class primitive.** Any issue can trigger a structured debate between specialist agents, orchestrated within a single GitHub Actions run. The orchestrator agent coordinates the Simulacrum pattern — opening positions, debate rounds, proposals, voting, and consensus — all executing inside one workflow job, with the full transcript committed to git and the consensus posted as an issue comment.

The core evolution:

> **v1:** Debates are an implementation detail of the orchestrator agent, triggered only by the `architecture` label.
> **v2:** Debates are a named capability of the system, triggerable by any label combination, configurable per-issue, and producing auditable, structured output.

### What Changed from v1

| Area | v1 | v2 |
|------|----|----|
| **Debate trigger** | Only `architecture` label | Any label + `debate` label, or `architecture` label, or explicit `@debate` command in comment |
| **Debate scope** | Architecture questions only | Any multi-perspective question (security review, performance trade-offs, migration strategy, technology selection) |
| **Debate execution** | Implicit (orchestrator decides) | Explicit Simulacrum execution via orchestrator with structured 5-phase protocol |
| **Agent selection** | Hardcoded to 4 agents | Configurable via issue body, auto-detected from labels, or defaulted by topic |
| **Debate output** | Unstructured comment | Structured Markdown comment with opening positions, key arguments, proposals, vote tally, and consensus |
| **Debate persistence** | Not specified | Full transcript committed as JSON to `state/debates/`, linked from issue mapping |
| **Debate cost** | Not budgeted | Explicit cost model with configurable rounds and agent count caps |
| **Workflow changes** | Single execution path | Branching execution: detect debate mode → run Simulacrum → format output |

---

## 1. Architectural Foundation (Unchanged from v1)

The GitHub Primitives Stack, Closed Loop, and Event-Driven Cognition model from v1 §1 remain unchanged. Debates are a new **execution mode** within the existing architecture, not a new layer.

The updated closed loop adds a debate path:

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
│         │         │    ┌──────▼───────┐   │          │               │
│         │         │    │ DEBATE MODE? │   │          │               │
│         │         │    │  ┌─────────┐ │   │          │               │
│         │         │    │  │Simulacr.│ │   │          │               │
│         │         │    │  │Orchestr.│ │   │          │               │
│         │         │    │  └─────────┘ │   │          │               │
│         │         │    └──────┬───────┘   │          │               │
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

---

## 2. Execution Model

### 2.1 Primary Workflow: `github-agenticana-agent.yml` (Updated)

The workflow from v1 §2.1 is extended with debate detection and execution. Changes are marked with `# NEW v2`.

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

      # NEW v2: Detect debate mode from labels and issue body
      - name: Detect execution mode
        id: detect_mode
        env:
          ISSUE_LABELS: ${{ toJSON(github.event.issue.labels.*.name) }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          COMMENT_BODY: ${{ github.event.comment.body }}
        run: |
          INPUT="${COMMENT_BODY:-$ISSUE_BODY}"

          # Debate mode triggers:
          # 1. Has 'debate' label
          # 2. Has 'architecture' label (v1 compat)
          # 3. Comment starts with @debate
          if echo "$ISSUE_LABELS" | grep -q '"debate"'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          elif echo "$ISSUE_LABELS" | grep -q '"architecture"'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          elif echo "$INPUT" | head -1 | grep -qi '^@debate'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          else
            echo "mode=agent" >> "$GITHUB_OUTPUT"
          fi

      # NEW v2: Run debate via orchestrator + Simulacrum
      - name: Run debate (Simulacrum via orchestrator)
        if: steps.detect_mode.outputs.mode == 'debate'
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          COMMENT_BODY: ${{ github.event.comment.body }}
          ISSUE_LABELS: ${{ toJSON(github.event.issue.labels.*.name) }}
          EVENT_NAME: ${{ github.event_name }}
        run: |
          python scripts/debate_runner.py \
            --issue-number "$ISSUE_NUMBER" \
            --input "${COMMENT_BODY:-$ISSUE_BODY}" \
            --labels "$ISSUE_LABELS"

      # Original v1: Run single agent
      - name: Route and execute agent
        if: steps.detect_mode.outputs.mode == 'agent'
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

      # NEW v2: Post debate result as structured comment
      - name: Post debate result
        if: steps.detect_mode.outputs.mode == 'debate' && always()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
        run: |
          DEBATE_FILE=".github-agenticana/state/debates/${ISSUE_NUMBER}-latest.md"
          if [ -f "$DEBATE_FILE" ]; then
            gh issue comment "$ISSUE_NUMBER" \
              -R "${{ github.repository }}" \
              --body-file "$DEBATE_FILE"
          else
            gh issue comment "$ISSUE_NUMBER" \
              -R "${{ github.repository }}" \
              --body "⚠️ Debate completed but no structured output was produced. Check workflow logs."
          fi

      - name: Post reply
        if: steps.detect_mode.outputs.mode == 'agent' && always()
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

### 2.2 Workflow Design Decisions (Updated)

All v1 decisions from §2.2 remain. New decisions for v2:

| Decision | Rationale |
|----------|-----------|
| **Mode detection step** (`detect_mode`) | Single branch point: debate vs. agent. Clean separation of execution paths. |
| **Label-based debate trigger** (`debate` label) | Consistent with v1's label-routing pattern. User intent is explicit. |
| **`@debate` comment trigger** | Enables mid-conversation debate requests without re-labeling the issue. |
| **`architecture` label → debate mode** (v1 compat) | Preserves v1 behavior where `architecture` issues always trigger Simulacrum. |
| **Separate post steps** per mode | Debate produces structured Markdown; agent produces reactions. Different output formats. |
| **Debate output as Markdown file** | Enables git-committed debate results that are also postable as issue comments. |
| **Single workflow job** | Debate runs inside the same job as agent execution — no multi-job coordination overhead. |

### 2.3 The Debate Lifecycle (New)

The debate lifecycle is a specialization of v1's Three-Phase Lifecycle:

```
Phase 1: Indicate    → 🚀 reaction (immediate feedback)
Phase 2: Install     → pip install + npm install (cached)
Phase 3: Detect      → Is this a debate? (labels + body inspection)
Phase 4: Debate      → Orchestrator runs Simulacrum
Phase 5: Persist     → Commit transcript + post structured comment
```

**Phase 4 expands:**

```
4a. Parse debate configuration from issue body (agents, rounds, mode)
4b. Auto-select agents if not specified (from labels or topic keywords)
4c. Query ReasoningBank for prior debates on similar topics (fast-path if identical)
4d. Orchestrator invokes Simulacrum with selected agents
    4d-i.   Opening positions (each agent states perspective)
    4d-ii.  Debate rounds (agents respond to each other)
    4d-iii. Proposals (each agent makes a concrete recommendation)
    4d-iv.  Voting (agents vote for strongest proposal)
    4d-v.   Consensus (winning proposal + constraints from all agents)
4e. Format debate result as structured Markdown
4f. Record debate decision to ReasoningBank
```

---

## 3. Multi-Agent Debates: The Simulacrum Protocol

### 3.1 What Is a Debate?

A **debate** is a structured multi-agent reasoning session where 3+ specialist agents argue different perspectives on a question, produce concrete proposals, vote, and arrive at a consensus — all within a single GitHub Actions run.

The debate is not a chat. It is a **protocol** with defined phases, time-bounded execution, and a deterministic output structure.

### 3.2 Debate Triggers

Three ways to trigger a debate:

| Trigger | How | Example |
|---------|-----|---------|
| **`debate` label** | Add `agenticana` + `debate` labels to an issue | Issue labeled `agenticana, debate, security` |
| **`architecture` label** | Add `agenticana` + `architecture` labels (v1 compat) | Issue labeled `agenticana, architecture` |
| **`@debate` command** | Post a comment starting with `@debate` on any `agenticana` issue | `@debate Should we use REST or GraphQL for the new API?` |

All three triggers route to the same execution path: the orchestrator running the Simulacrum.

### 3.3 Agent Selection for Debates

Agents participating in a debate are selected through a priority cascade:

```
1. Explicit: Issue body contains <!-- agents: backend-specialist, security-auditor, ... -->
       ↓ (if not specified)
2. Label-derived: Issue labels map to agents (e.g., `security` → security-auditor)
       ↓ (if fewer than 3 agents)
3. Topic-inferred: NL keyword matching from nl_swarm.py's AGENT_TRIGGERS
       ↓ (if still fewer than 3 agents)
4. Default panel: backend-specialist, security-auditor, frontend-specialist
```

**Minimum 3 agents required.** The orchestrator enforces this (consistent with `workflows/orchestrate.md` §Minimum Agent Requirement). If the cascade produces fewer than 3, defaults are appended.

**Maximum 7 agents.** More than 7 agents produces diminishing returns and increases LLM cost linearly. The runner caps at 7.

### 3.4 Debate Configuration via Issue Body

Users can configure debate parameters using HTML comments in the issue body (invisible in rendered Markdown):

```markdown
**Should we migrate from REST to GraphQL?**

Our API has grown to 47 endpoints. Client teams are requesting
flexible queries. But we have existing consumers on REST.

<!-- debate-config
agents: backend-specialist, security-auditor, frontend-specialist, database-architect, performance-optimizer
rounds: 3
mode: real
-->
```

| Parameter | Default | Options | Effect |
|-----------|---------|---------|--------|
| `agents` | Auto-selected | Comma-separated agent names | Explicit agent panel |
| `rounds` | `2` | `1`-`5` | Number of debate rounds (more rounds = deeper analysis, higher cost) |
| `mode` | `real` | `real`, `logic` | `real` uses live LLM calls per agent (real_simulacrum.py); `logic` uses persona heuristics (simulacrum.py) |

### 3.5 The Five-Phase Simulacrum Protocol

The debate follows a strict 5-phase protocol, executed by the orchestrator agent calling either `real_simulacrum.py` (live LLM) or `simulacrum.py` (persona fallback):

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIMULACRUM PROTOCOL                           │
│                                                                  │
│  Phase 1: OPENING POSITIONS                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  backend     │ │  security   │ │  frontend   │  ...          │
│  │  specialist  │ │  auditor    │ │  specialist │               │
│  │  "I focus on │ │  "I focus on│ │  "I focus on│               │
│  │  scalability"│ │  threats"   │ │  DX"        │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         │               │               │                        │
│  Phase 2: DEBATE ROUNDS (N rounds)                               │
│         │←──────────────┼───────────────│                        │
│         │    Agents respond to each other's arguments            │
│         │    Each round deepens the analysis                     │
│         │───────────────┼──────────────▶│                        │
│         │               │               │                        │
│  Phase 3: PROPOSALS                                              │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ "Use event  │ │ "Implement  │ │ "Adopt BFF  │               │
│  │  sourcing"  │ │  zero-trust │ │  pattern"   │               │
│  │             │ │  gateway"   │ │             │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         │               │               │                        │
│  Phase 4: VOTING                                                 │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│         2 votes         1 vote          2 votes                  │
│         │               │               │                        │
│  Phase 5: CONSENSUS                                              │
│         └───────────────┼───────────────┘                        │
│                         ▼                                        │
│              ┌────────────────────┐                              │
│              │  WINNING PROPOSAL  │                              │
│              │  + all constraints │                              │
│              │  from every agent  │                              │
│              └────────────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 Execution: Orchestrator + Simulacrum in One Action

The key architectural decision: **the orchestrator does not spawn separate workflow jobs for each agent.** Instead, it runs the Simulacrum engine in-process within the same GitHub Actions job.

```
GitHub Actions Job
    │
    ├─ detect_mode → "debate"
    │
    ├─ debate_runner.py (orchestrator entry point)
    │   │
    │   ├─ Parse debate config from issue body
    │   ├─ Select agents (cascade: explicit → labels → topic → defaults)
    │   ├─ Check ReasoningBank for prior similar debates
    │   │
    │   ├─ if mode == "real":
    │   │   └─ real_simulacrum.py (each agent gets its own Gemini API call)
    │   │       ├─ Phase 1: Opening (N sequential LLM calls)
    │   │       ├─ Phase 2: Debate (N × rounds sequential LLM calls)
    │   │       ├─ Phase 3: Proposals (N sequential LLM calls)
    │   │       ├─ Phase 4: Voting (N sequential LLM calls)
    │   │       └─ Phase 5: Consensus (synthesized)
    │   │
    │   ├─ elif mode == "logic":
    │   │   └─ simulacrum.py (persona-based, no LLM calls)
    │   │
    │   ├─ Format result as Markdown (state/debates/{issue}-latest.md)
    │   ├─ Save full transcript as JSON (state/debates/{issue}-{session}.json)
    │   └─ Record to ReasoningBank
    │
    ├─ git add -A && git commit && git push (state committed)
    │
    └─ gh issue comment (structured Markdown posted to issue)
```

**Why a single job?**

| Alternative | Problem |
|-------------|---------|
| One job per agent | Requires `workflow_dispatch` chaining; complex; 6× startup overhead |
| Matrix strategy | Agents cannot see each other's responses; no debate possible |
| Reusable workflows | Same startup overhead; complex output passing |
| **Single job with Simulacrum engine** ✅ | All agents run sequentially in-process; each sees prior arguments; no orchestration overhead |

The Simulacrum engine runs agents sequentially within a single process. This is correct for a debate — agents must respond to each other. Parallelism is not beneficial because each agent's argument depends on the previous agent's statement.

### 3.7 LLM Usage in Debate Mode

In `real` mode, the Simulacrum makes sequential LLM API calls — one per agent per phase:

| Phase | LLM Calls | Context Per Call |
|-------|-----------|-----------------|
| Opening (Phase 1) | N agents × 1 | Topic + agent system prompt |
| Debate (Phase 2) | N agents × R rounds | Topic + prior argument + agent system prompt |
| Proposals (Phase 3) | N agents × 1 | Topic + agent system prompt |
| Voting (Phase 4) | N agents × 1 | All proposals + agent system prompt |
| **Total** | **N × (2 + R)** | |

For a typical 5-agent, 2-round debate: `5 × (2 + 2) = 20` LLM calls.

Each call uses `gemini-2.0-flash` with `maxOutputTokens: 200` — keeping responses concise and costs low.

---

## 4. The Debate Runner: `scripts/debate_runner.py`

### 4.1 Script Specification

A new script that serves as the orchestrator's entry point for debate mode:

```python
"""
debate_runner.py — Orchestrator entry point for multi-agent debates.

Parses issue input, selects agents, runs Simulacrum, formats output.
Called by the GitHub Actions workflow when debate mode is detected.

Usage:
  python scripts/debate_runner.py \
    --issue-number 42 \
    --input "Should we migrate from REST to GraphQL?" \
    --labels '["agenticana", "debate", "backend"]'
"""
```

### 4.2 Debate Runner Flow

```python
def run_debate(issue_number: int, input_text: str, labels: list[str]) -> dict:
    # 1. Parse debate config from input text
    config = parse_debate_config(input_text)
    
    # 2. Select agents (cascade)
    agents = select_agents(
        explicit=config.get("agents"),
        labels=labels,
        topic=input_text,
        min_agents=3,
        max_agents=7
    )
    
    # 3. Check ReasoningBank for prior debates
    prior = reasoning_bank_lookup(input_text, threshold=0.85)
    if prior:
        # Fast-path: return prior debate result with note
        return format_prior_debate(prior, issue_number)
    
    # 4. Run Simulacrum
    mode = config.get("mode", "real")
    rounds = config.get("rounds", 2)
    
    if mode == "real":
        from real_simulacrum import run_real_simulacrum
        result = run_real_simulacrum(input_text, agents, rounds)
    else:
        from simulacrum import run_simulacrum
        result = run_simulacrum(input_text, agents, rounds)
    
    # 5. Format as Markdown for issue comment
    markdown = format_debate_markdown(result)
    
    # 6. Persist state
    save_debate_state(issue_number, result, markdown)
    
    # 7. Record to ReasoningBank
    record_debate_decision(input_text, result)
    
    return result
```

### 4.3 Agent Selection Cascade

```python
def select_agents(explicit, labels, topic, min_agents=3, max_agents=7):
    """Select debate agents via priority cascade."""
    agents = []
    
    # Priority 1: Explicit from debate-config
    if explicit:
        agents = [a.strip() for a in explicit.split(",")]
    
    # Priority 2: Derive from issue labels
    if len(agents) < min_agents:
        label_map = {
            "security": "security-auditor",
            "frontend": "frontend-specialist",
            "backend": "backend-specialist",
            "database": "database-architect",
            "devops": "devops-engineer",
            "performance": "performance-optimizer",
            "testing": "test-engineer",
            # ... full mapping from v1 §3.1
        }
        for label in labels:
            if label in label_map and label_map[label] not in agents:
                agents.append(label_map[label])
    
    # Priority 3: NL keyword matching (reuse nl_swarm.py logic)
    if len(agents) < min_agents:
        from nl_swarm import detect_agents
        topic_agents = detect_agents(topic)
        for a in topic_agents:
            if a not in agents:
                agents.append(a)
    
    # Priority 4: Defaults
    defaults = ["backend-specialist", "security-auditor", "frontend-specialist"]
    while len(agents) < min_agents:
        for d in defaults:
            if d not in agents:
                agents.append(d)
                break
    
    return agents[:max_agents]
```

### 4.4 Debate Config Parser

```python
import re

def parse_debate_config(text: str) -> dict:
    """Extract debate configuration from HTML comments in issue body."""
    config = {}
    match = re.search(
        r'<!--\s*debate-config\s*\n(.*?)\n\s*-->',
        text, re.DOTALL
    )
    if match:
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                config[key.strip()] = value.strip()
    
    # Parse rounds as integer
    if "rounds" in config:
        config["rounds"] = max(1, min(5, int(config["rounds"])))
    
    return config
```

---

## 5. Debate Output Format

### 5.1 Structured Markdown Comment

The debate result is posted as a structured Markdown comment on the issue:

```markdown
## 🦅 Secretary Bird Debate — Session `a1b2c3d4`

**Topic:** Should we migrate from REST to GraphQL?
**Mode:** LIVE_LLM | **Rounds:** 2 | **Agents:** 5

---

### Phase 1: Opening Positions

**🔧 backend-specialist**
> From a scalability lens: GraphQL reduces over-fetching but introduces
> query complexity. We need to consider resolver performance and N+1 risks.

**🔒 security-auditor**
> GraphQL exposes a single endpoint which simplifies firewall rules but
> creates a larger attack surface via introspection and deep queries.

**🎨 frontend-specialist**
> GraphQL gives clients exactly the data they need. This eliminates
> waterfall requests and simplifies state management.

**🗄️ database-architect**
> GraphQL resolvers must be carefully designed to prevent N+1 queries.
> Without DataLoader or equivalent batching, database load will increase.

**⚡ performance-optimizer**
> GraphQL query parsing adds latency. For simple CRUD endpoints,
> REST is faster. But for complex aggregation queries, GraphQL wins.

---

### Phase 2: Key Arguments (2 rounds)

| Agent | Round 1 | Round 2 |
|-------|---------|---------|
| backend-specialist | Need to define resolver boundaries | Suggest BFF pattern as middle ground |
| security-auditor | Require query depth limiting | Add persisted queries for production |
| frontend-specialist | Client SDK generation is a major DX win | TypeScript codegen eliminates runtime errors |
| database-architect | DataLoader is mandatory for any resolver | Schema should mirror domain model |
| performance-optimizer | Benchmark REST vs GraphQL for top 10 queries | Cache at resolver level, not HTTP level |

---

### Phase 3: Proposals

| Agent | Proposal |
|-------|----------|
| backend-specialist | Adopt BFF pattern: GraphQL for new clients, REST maintained for existing consumers |
| security-auditor | Implement persisted queries with depth limiting; no open introspection in production |
| frontend-specialist | Ship GraphQL with auto-generated TypeScript SDK; deprecate REST over 6 months |
| database-architect | Use DataLoader everywhere; add resolver-level query logging from day one |
| performance-optimizer | A/B test top 20 endpoints: REST vs GraphQL; decide based on p95 latency data |

---

### Phase 4: Vote Tally

| Proposal (by agent) | Votes |
|---------------------|-------|
| backend-specialist | ⭐⭐ (2) |
| security-auditor | ⭐ (1) |
| frontend-specialist | ⭐⭐ (2) |

---

### ✅ Phase 5: Consensus

**Winning approach** (tie resolved by debate coherence):
> **backend-specialist:** Adopt BFF pattern: GraphQL for new clients, REST maintained for existing consumers

**Constraints agreed upon by all agents:**
- 🔧 [backend-specialist] API latency budget of 200ms p95
- 🔒 [security-auditor] No open introspection; persisted queries only
- 🎨 [frontend-specialist] TypeScript SDK auto-generation required
- 🗄️ [database-architect] DataLoader mandatory; N+1 detection in CI
- ⚡ [performance-optimizer] Benchmark before and after; rollback if p95 regresses

---

<details>
<summary>📋 Debate metadata</summary>

- **Session ID:** a1b2c3d4
- **Transcript:** `.github-agenticana/state/debates/42-a1b2c3d4.json`
- **Duration:** ~3 minutes
- **LLM calls:** 20 (5 agents × 4 phases)
- **Estimated cost:** $0.15-0.40

</details>
```

### 5.2 Agent Emoji Mapping

Each agent gets a consistent emoji for visual identification in debate output:

| Agent | Emoji | Domain |
|-------|-------|--------|
| backend-specialist | 🔧 | Backend/API |
| security-auditor | 🔒 | Security |
| frontend-specialist | 🎨 | Frontend/UX |
| database-architect | 🗄️ | Database |
| performance-optimizer | ⚡ | Performance |
| test-engineer | 🧪 | Testing |
| devops-engineer | 🚀 | DevOps |
| mobile-developer | 📱 | Mobile |
| documentation-writer | 📝 | Documentation |
| project-planner | 📋 | Planning |
| product-manager | 📊 | Product |
| game-developer | 🎮 | Games |
| seo-specialist | 🔍 | SEO |
| debugger | 🐛 | Debugging |
| explorer-agent | 🔭 | Exploration |
| code-archaeologist | 🏛️ | Legacy code |
| penetration-tester | 🗡️ | Offensive security |
| qa-automation-engineer | ✅ | QA |
| orchestrator | 🎼 | Coordination |

---

## 6. Debate State Persistence

### 6.1 State Directory Structure (Extended from v1 §4.1)

```
.github-agenticana/state/
├── issues/                    # Issue → session mappings (v1)
│   ├── 1.json
│   └── ...
├── sessions/                  # Agent execution transcripts (v1)
│   └── ...
├── debates/                   # NEW v2: Debate transcripts and results
│   ├── 42-a1b2c3d4.json      # Full transcript (JSON, machine-readable)
│   ├── 42-latest.md           # Latest debate result (Markdown, posted to issue)
│   └── ...
└── attestations/              # Proof-of-Work attestations (v1)
    └── ...
```

### 6.2 Debate JSON Schema

The full transcript JSON (`{issue}-{session}.json`) follows this schema:

```json
{
  "session_id": "a1b2c3d4",
  "issue_number": 42,
  "topic": "Should we migrate from REST to GraphQL?",
  "mode": "LIVE_LLM",
  "agents": ["backend-specialist", "security-auditor", "frontend-specialist", "database-architect", "performance-optimizer"],
  "config": {
    "rounds": 2,
    "mode": "real",
    "source": "issue_body"
  },
  "winning_agent": "backend-specialist",
  "winning_proposal": "Adopt BFF pattern: GraphQL for new clients, REST maintained for existing consumers",
  "vote_tally": {
    "backend-specialist": 2,
    "security-auditor": 1,
    "frontend-specialist": 2,
    "database-architect": 0,
    "performance-optimizer": 0
  },
  "all_proposals": {
    "backend-specialist": "...",
    "security-auditor": "...",
    "frontend-specialist": "...",
    "database-architect": "...",
    "performance-optimizer": "..."
  },
  "constraints": [
    "[backend-specialist] API latency budget of 200ms p95",
    "[security-auditor] No open introspection; persisted queries only",
    "[frontend-specialist] TypeScript SDK auto-generation required",
    "[database-architect] DataLoader mandatory; N+1 detection in CI",
    "[performance-optimizer] Benchmark before and after; rollback if p95 regresses"
  ],
  "timestamp": "2026-03-03T10:30:00.000Z",
  "duration_seconds": 180,
  "llm_calls": 20,
  "transcript": [
    {
      "timestamp": "...",
      "phase": "opening",
      "speaker": "backend-specialist",
      "content": "...",
      "mode": "LIVE_LLM"
    }
  ]
}
```

### 6.3 Issue Mapping Update

The issue-to-session mapping (`state/issues/{issue}.json`) is extended to include debate references:

```json
{
  "issueNumber": 42,
  "agent": "orchestrator",
  "sessionPath": "state/sessions/1709510400.jsonl",
  "debates": [
    {
      "sessionId": "a1b2c3d4",
      "path": "state/debates/42-a1b2c3d4.json",
      "topic": "Should we migrate from REST to GraphQL?",
      "winner": "backend-specialist",
      "timestamp": "2026-03-03T10:30:00.000Z"
    }
  ],
  "updatedAt": "2026-03-03T10:30:00.000Z"
}
```

### 6.4 ReasoningBank Integration for Debates

Debate decisions are recorded to the ReasoningBank, enabling fast-path on repeated topics:

```
Debate completes
    │
    ├─ Record: python scripts/reasoning_bank.py record \
    │     --task "debate: Should we migrate from REST to GraphQL?" \
    │     --decision "BFF pattern: GraphQL for new clients, REST for existing" \
    │     --outcome "consensus reached, 5 agents, 2 rounds" \
    │     --success true
    │
    └─ Next debate on similar topic:
       → ReasoningBank similarity > 0.85
       → Fast-path: return prior consensus with note
       → Save ~60% of LLM cost
```

---

## 7. Multi-Agent Routing via Issue Labels (Updated from v1 §3)

### 7.1 Label-to-Agent Mapping (Extended)

All v1 label mappings from §3.1 remain. New label added:

| Issue Label | Agent | Complexity Tier | Action |
|-------------|-------|----------------|--------|
| `debate` | orchestrator (debate mode) | COMPLEX | Triggers Simulacrum debate with auto-selected agents |

**Label combinations for debates:**

| Labels | Effect |
|--------|--------|
| `agenticana, debate` | Debate with auto-selected agents based on issue content |
| `agenticana, debate, security` | Debate with security-auditor guaranteed + auto-selected agents |
| `agenticana, debate, backend, frontend, database` | Debate with all three specified agents + auto-fill to minimum 3 |
| `agenticana, architecture` | Debate (v1 compat) with architecture-focused agent panel |

### 7.2 Auto-Routing Logic (Updated)

The auto-routing logic from v1 §3.2 is extended with a debate detection branch:

```
Issue body + labels
    │
    ├─ Has 'debate' or 'architecture' label, or body starts with @debate?
    │   ├─ YES → Debate mode → debate_runner.py
    │   └─ NO  → Agent mode → agent_cli.py @auto (v1 behavior)
    │
    ├─ (Debate mode)
    │   ├─ Parse debate-config from issue body
    │   ├─ Select agents (cascade)
    │   └─ Run Simulacrum
    │
    └─ (Agent mode)
        ├─ Query Model Router (complexity-scorer.js)
        └─ Route to specialist agent (v1 behavior)
```

---

## 8. Cost Model (Updated from v1 §6)

### 8.1 Debate Cost Estimates

Debates are more expensive than single-agent interactions because they invoke multiple LLM calls:

| Debate Config | LLM Calls | Duration | Actions Cost | LLM Cost (est.) | Total |
|---------------|-----------|----------|-------------|-----------------|-------|
| 3 agents, 1 round (minimal) | 9 | ~2-3 min | $0.016-0.024 | $0.05-0.15 | ~$0.07-0.17 |
| 5 agents, 2 rounds (default) | 20 | ~3-5 min | $0.024-0.040 | $0.10-0.40 | ~$0.12-0.44 |
| 7 agents, 3 rounds (deep) | 35 | ~5-8 min | $0.040-0.064 | $0.20-0.70 | ~$0.24-0.76 |
| 7 agents, 5 rounds (max) | 49 | ~8-12 min | $0.064-0.096 | $0.30-1.00 | ~$0.36-1.10 |

**Formula:** `LLM calls = N_agents × (2 + N_rounds)` where the 2 accounts for opening + proposal/voting phases.

### 8.2 Debate-Specific Cost Optimizations

| Optimization | Mechanism | Estimated Savings |
|-------------|-----------|------------------|
| **ReasoningBank fast-path** | Skip full debate when similarity > 0.85 | ~80% on repeated topics |
| **Logic mode fallback** | Use persona heuristics when no API key or for cost-sensitive debates | ~95% (no LLM calls) |
| **Flash model for all debate calls** | Use `gemini-2.0-flash` with 200-token cap per agent response | ~70% vs pro model |
| **Agent count cap (7 max)** | Prevent runaway agent spawning | Bounded worst-case |
| **Round cap (5 max)** | Prevent excessive debate depth | Bounded worst-case |
| **Concise system prompts** | "Max 3 sentences" constraint in agent prompts | ~40% fewer output tokens |

### 8.3 Updated Monthly Projections

| Usage Pattern | Single-Agent/Day | Debates/Day | Monthly Actions Cost |
|--------------|-----------------|-------------|---------------------|
| Light | 5 | 0-1 | Free tier |
| Moderate | 15 | 2-3 | Free tier |
| Heavy | 30 | 5-10 | $0-20 overage |
| Intense | 50+ | 10-20 | $20-60 overage |

---

## 9. Issue Templates (Updated from v1 §7)

### 9.1 Debate Template (New)

```markdown
---
name: "🦅 Agent Debate"
about: "Trigger a multi-agent Simulacrum debate on any question"
title: "[Debate] "
labels: ["agenticana", "debate"]
---

**Question to debate:**

<!-- What decision or trade-off should the agents argue about? -->

**Context:**

<!-- Relevant constraints, requirements, prior decisions, or code links. -->

<!-- debate-config
agents:
rounds: 2
mode: real
-->

<!-- Configuration help:
  agents: Comma-separated agent names (leave empty for auto-selection)
          Available: backend-specialist, security-auditor, frontend-specialist,
          database-architect, performance-optimizer, test-engineer, devops-engineer
  rounds: 1-5 (default: 2, more rounds = deeper analysis)
  mode: real (live LLM) or logic (persona heuristics, free)
-->
```

### 9.2 Architecture Review Template (Updated)

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

<!-- debate-config
agents: backend-specialist, security-auditor, frontend-specialist, database-architect, performance-optimizer
rounds: 3
mode: real
-->
```

### 9.3 Chat Template (Unchanged from v1)

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

### 9.4 Security Audit Template (Unchanged from v1)

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

## 10. Hybrid Execution Model (Updated from v1 §8)

### 10.1 Debates Across Interfaces

The local (VS Code/MCP) and cloud (Actions) interfaces from v1 §8 are extended with debate support:

| Use Case | Interface | Why |
|----------|-----------|-----|
| Quick question to one agent | VS Code (local) | Immediate response |
| **Multi-agent debate** | **GitHub Issue (cloud)** | **Debates take 3-12 minutes; async execution is natural** |
| **Quick local debate** | **VS Code CLI** | **`agentica simulacrum "topic" --agents ...` for local-only debates** |
| Architecture review | GitHub Issue (cloud) | Team sees debate transcript as issue comment |
| Code review | Either | VS Code for immediate, Issue for async |

### 10.2 Local Debate via CLI

Debates can also be run locally via the existing CLI for developer-only exploration:

```bash
# Logic mode (free, persona-based)
python scripts/agentica_cli.py simulacrum "Should we use REST or GraphQL?" \
  --agents backend-specialist security-auditor frontend-specialist

# Real LLM mode
python scripts/real_simulacrum.py "Should we use REST or GraphQL?" \
  --agents backend-specialist security-auditor frontend-specialist database-architect \
  --rounds 3
```

The local CLI writes transcripts to `.Agentica/logs/simulacrum/` (not committed). The GitHub Actions workflow writes to `.github-agenticana/state/debates/` (committed).

---

## 11. Implementation Phases

### Phase 1: Foundation (v1 — unchanged)

As defined in v1 §9 Phase 1. Actions workflow + Agent CLI integration.

### Phase 2: Multi-Agent Routing (v1 — unchanged)

As defined in v1 §9 Phase 2. Labels + Router.

### Phase 3: Persistent Memory (v1 — unchanged)

As defined in v1 §9 Phase 3. Git-backed state.

### Phase 4: Governance Layer (v1 — unchanged)

As defined in v1 §9 Phase 4. Identity + DEFCON + Four Laws.

### Phase 5: Optimization (v1 — unchanged)

As defined in v1 §9 Phase 5. Caching, cost control, monitoring.

### Phase 6: Multi-Agent Debates (New — this specification)

**Goal:** Make multi-agent debates a first-class feature, triggerable via issues, with structured output.

**Deliverables:**
- [ ] `scripts/debate_runner.py` — Orchestrator entry point for debate mode
- [ ] Debate config parser — Extract `<!-- debate-config -->` from issue body
- [ ] Agent selection cascade — Explicit → labels → topic → defaults
- [ ] Markdown formatter — Structured debate output as issue comment
- [ ] State persistence — `state/debates/` directory with JSON transcripts and Markdown results
- [ ] Issue mapping extension — `debates[]` array in issue JSON
- [ ] ReasoningBank integration — Record debate decisions; fast-path on repeated topics
- [ ] Workflow update — `detect_mode` step + conditional debate/agent execution
- [ ] `debate` label documentation — Add to label-to-agent mapping
- [ ] Debate issue template — `.github/ISSUE_TEMPLATE/debate.md`
- [ ] Updated architecture issue template — Add `debate-config` section

**Verification:** 
1. Open issue with `agenticana, debate` labels → Simulacrum runs → structured comment posted → transcript committed
2. Open issue with `agenticana, architecture` label → same debate flow (v1 compat)
3. Post `@debate Should we...?` comment on existing `agenticana` issue → debate runs
4. Include `<!-- debate-config agents: ... rounds: 3 -->` → agents and rounds honored
5. Run same debate topic twice → second time hits ReasoningBank fast-path

### Phase 7: Debate Enhancements (Future)

**Goal:** Advanced debate features for power users.

**Potential deliverables:**
- [ ] **Debate chains** — One debate's consensus feeds into the next debate as context
- [ ] **Debate branches** — Fork a debate to explore an alternative with different agents
- [ ] **Human-in-the-loop** — Pause debate after Phase 2, let human add a comment, then resume with Phase 3
- [ ] **Debate analytics** — Track which agents win most often, which topics generate most rounds
- [ ] **Cross-repo debates** — Reference code/issues from other repos as debate context
- [ ] **Debate scheduling** — `schedule` event trigger for periodic architectural reviews

---

## 12. Security Considerations (Updated from v1 §5)

### 12.1 Debate-Specific Security

All security mitigations from v1 §5.4 apply. Additional considerations for debates:

| ID | Severity | Finding | Mitigation |
|----|----------|---------|------------|
| SEC-009 | 🟡 Medium | Debate config in issue body could be manipulated by unauthorized users | Only collaborators can trigger debates (authorization step unchanged from v1) |
| SEC-010 | 🟡 Medium | High agent count × high round count = expensive debates | Hard caps: max 7 agents, max 5 rounds, max 49 LLM calls per debate |
| SEC-011 | 🟢 Low | Debate transcripts may contain sensitive reasoning | Transcripts committed to repo (same access control as code); no external exposure |
| SEC-012 | 🟡 Medium | ReasoningBank fast-path could serve stale consensus | Include timestamp and staleness warning if prior debate is older than 30 days |

### 12.2 DEFCON Level Interaction

Debate behavior adapts to the active DEFCON level:

| DEFCON Level | Debate Behavior |
|-------------|----------------|
| **DEFCON 1** (Maximum) | Debates suspended. No LLM calls. |
| **DEFCON 2** (High) | Debates run in `logic` mode only (no LLM calls). Results are advisory. |
| **DEFCON 3** (Increased) | Debates run in `real` mode but consensus is not auto-applied. Human must approve. |
| **DEFCON 4** (Above Normal) | Normal debate operation with elevated logging. |
| **DEFCON 5** (Normal) | Normal debate operation. |

---

## 13. What v2 Adds to v1

| Dimension | v1 | v2 |
|-----------|----|----|
| **Debate trigger** | `architecture` label only | `debate` label, `architecture` label, `@debate` command |
| **Debate configuration** | None | `<!-- debate-config -->` in issue body (agents, rounds, mode) |
| **Debate execution** | Implicit orchestrator behavior | Explicit `debate_runner.py` with structured Simulacrum protocol |
| **Debate output** | Unstructured comment | Structured 5-section Markdown with phases, proposals, votes, consensus |
| **Debate persistence** | Not specified | `state/debates/` with JSON transcripts + Markdown results + issue mapping |
| **Debate cost model** | ~$0.24-1.08 (estimated in v1) | Detailed per-config estimates with optimization strategies |
| **Debate fast-path** | Not specified | ReasoningBank similarity > 0.85 skips full debate |
| **Debate limits** | Not specified | Max 7 agents, max 5 rounds, max 49 LLM calls |
| **Debate DEFCON** | Not specified | Behavior adapts to active DEFCON level |
| **Workflow** | Single execution path | Branching: detect mode → debate OR agent |
| **Issue templates** | Chat, Architecture, Security | + Debate template with config section |

---

## 14. Summary

This specification evolves `github-agenticana` from a system where multi-agent debates are an implicit behavior of the orchestrator into one where **debates are a named, configurable, auditable primitive** of the repository-as-runtime.

The key design decision:

> **Run the Simulacrum pattern via the orchestrator in a single GitHub Actions job.** No multi-job coordination. No matrix strategies. One job, one process, sequential LLM calls — because a debate requires each agent to hear and respond to the others.

For users, this means:

1. **Add the `debate` label** (or use `@debate`) to trigger a structured multi-agent debate
2. **Configure agents and rounds** via `<!-- debate-config -->` in the issue body
3. **Receive a structured Markdown comment** with opening positions, arguments, proposals, votes, and consensus
4. **Review the full transcript** committed to git at `state/debates/`
5. **Benefit from ReasoningBank fast-path** — repeated topics are answered from prior consensus

For the system, this means:

1. A new `detect_mode` step in the workflow that branches between debate and agent execution
2. A new `debate_runner.py` script that orchestrates the Simulacrum within a single process
3. A new `state/debates/` directory for persistent, auditable debate transcripts
4. An extended cost model that accounts for multi-LLM-call debate sessions
5. DEFCON-aware debate behavior that adapts to the active readiness level

The result: **any question worth multiple perspectives can be debated by specialist agents, within a single GitHub Actions run, with the consensus posted as an issue comment and the full transcript committed to git.**
