# AI Instructions to Achieve specification-final.md

> **Purpose:** The exact, ordered AI requests required to fully implement [specification-final.md](specification-final.md).
> Each request is a self-contained prompt that can be given to an AI coding agent (e.g., GitHub Copilot, Claude, GPT).
> Execute them in order. Each prompt assumes the previous ones have been completed.
>
> **Source specification:** [specification-final.md](specification-final.md) — Specification v4 (Final): GitHub as AI Infrastructure for Agenticana — Consolidated

---

## Phase 1: Containment Setup

### Request 1.1 — Create the `.github-agenticana/` directory structure

```
Create the following directory tree inside the repository root. Each directory should
contain a .gitkeep file to ensure it is tracked by git. Do not create any files other
than .gitkeep in each directory.

.github-agenticana/
├── config/
├── governance/
├── scripts/
├── workflows/
├── templates/
├── reconciler/
└── state/
    ├── issues/
    ├── sessions/
    ├── debates/
    ├── attestations/
    └── reasoning-bank/

The analysis/ directory already exists (it contains the specifications).
The githubification/ directory already exists if present — do not modify it.
```

### Request 1.2 — Create `.github-agenticana/config/agents.yaml`

```
Create the file .github-agenticana/config/agents.yaml that defines the complete
label-to-agent mapping for issue routing. Use the following mapping exactly:

label_mapping:
  agenticana: auto-routed (Model Router selects agent based on issue content)
  security: security-auditor
  penetration-test: penetration-tester
  performance: performance-optimizer
  architecture: orchestrator (triggers Simulacrum debate)
  debug: debugger
  frontend: frontend-specialist
  backend: backend-specialist
  mobile: mobile-developer
  database: database-architect
  devops: devops-engineer
  testing: test-engineer
  qa: qa-automation-engineer
  docs: documentation-writer
  explore: explorer-agent
  archaeology: code-archaeologist
  game: game-developer
  seo: seo-specialist
  plan: project-planner
  product: product-manager
  debate: orchestrator (debate mode — triggers Simulacrum with auto-selected agents)

Include a top-level comment explaining this file is the source of truth for label-to-agent
routing, read at runtime by the GitHub Actions workflow. Format as valid YAML with
descriptive comments.
```

### Request 1.3 — Create `.github-agenticana/config/routing-rules.yaml`

```
Create the file .github-agenticana/config/routing-rules.yaml that defines auto-routing
configuration for the agent system.

Include:
- auto_route_label: "agenticana" — the label that triggers auto-routing
- debate_trigger_labels: ["debate", "architecture"] — labels that trigger debate mode
- debate_trigger_command: "@debate" — comment prefix that triggers debate mode
- routing_method: "model-router" — use router/router.js for agent selection
- fallback_agent: "backend-specialist" — if routing fails, use this agent
- complexity_tiers:
    SIMPLE: { model: "gemini-2.0-flash", max_tokens: 2000 }
    MODERATE: { model: "gemini-2.0-flash", max_tokens: 4000 }
    COMPLEX: { model: "gemini-2.5-pro", max_tokens: 8000 }

Format as valid YAML with descriptive comments.
```

### Request 1.4 — Create `.github-agenticana/config/debate-defaults.yaml`

```
Create the file .github-agenticana/config/debate-defaults.yaml that defines default
parameters for multi-agent Simulacrum debates.

Include:
- default_rounds: 2
- min_agents: 3
- max_agents: 7
- max_rounds: 5
- default_mode: "real" (options: real, logic)
- default_agents: ["backend-specialist", "security-auditor", "frontend-specialist"]
- llm_model: "gemini-2.0-flash"
- max_output_tokens_per_agent: 200
- reasoning_bank_similarity_threshold: 0.85
- reasoning_bank_staleness_days: 30
- cost_formula: "N_agents × (2 + N_rounds)"
- cost_note: "The 2 accounts for opening + proposal/voting phases"

Include agent emoji mapping for debate output formatting:
  backend-specialist: 🔧
  security-auditor: 🔒
  frontend-specialist: 🎨
  database-architect: 🗄️
  performance-optimizer: ⚡
  test-engineer: 🧪
  devops-engineer: 🚀
  mobile-developer: 📱
  documentation-writer: 📝
  project-planner: 📋
  product-manager: 📊
  game-developer: 🎮
  seo-specialist: 🔍
  debugger: 🐛
  explorer-agent: 🔭
  code-archaeologist: 🏛️
  penetration-tester: 🗡️
  qa-automation-engineer: ✅
  orchestrator: 🎼

Format as valid YAML with descriptive comments.
```

### Request 1.5 — Create `.github-agenticana/config/cost-limits.yaml`

```
Create the file .github-agenticana/config/cost-limits.yaml that defines per-interaction
cost caps.

Include:
- workflow_timeout_minutes: 15
- debate_max_llm_calls: 49 (7 agents × (2 + 5 rounds))
- per_interaction_estimates:
    simple_question: { duration: "~1 min", actions_cost: "$0.008", llm_cost: "$0.01-0.05" }
    code_review: { duration: "~2-3 min", actions_cost: "$0.016-0.024", llm_cost: "$0.05-0.20" }
    code_generation: { duration: "~3-5 min", actions_cost: "$0.024-0.040", llm_cost: "$0.10-0.50" }
    architecture_debate: { duration: "~5-10 min", actions_cost: "$0.040-0.080", llm_cost: "$0.20-1.00" }
- debate_cost_tiers:
    minimal: { agents: 3, rounds: 1, llm_calls: 9, duration: "~2-3 min" }
    default: { agents: 5, rounds: 2, llm_calls: 20, duration: "~3-5 min" }
    deep: { agents: 7, rounds: 3, llm_calls: 35, duration: "~5-8 min" }
    max: { agents: 7, rounds: 5, llm_calls: 49, duration: "~8-12 min" }
- cost_optimizations:
    - "Model Router: route simple tasks to flash model (~40% savings)"
    - "ReasoningBank fast-path: skip execution when similarity > 0.85 (~60% savings)"
    - "Dependency caching: save ~30-40 seconds per run"
    - "Label-gating: only trigger on agenticana-labeled issues"
    - "Logic mode fallback: no LLM calls (~95% savings)"
    - "Flash model for all debate calls with 200-token cap (~70% vs pro model)"

Format as valid YAML with descriptive comments.
```

### Request 1.6 — Create `.github-agenticana/reconciler/apply.sh`

```
Create the file .github-agenticana/reconciler/apply.sh — the automated reconciler
script that bridges .github-agenticana/ sources to GitHub-required file locations.

The script must:
1. Use bash with set -euo pipefail
2. Determine REPO_ROOT and AGENTICANA_DIR from the script's own location
3. Print a header: "🦅 github-agenticana reconciler"
4. Copy all .yml and .yaml files from .github-agenticana/workflows/ to .github/workflows/
5. Copy all .md files from .github-agenticana/templates/ to .github/ISSUE_TEMPLATE/
6. Log every file copied with emoji indicators
7. Print a summary with next steps (review with git diff, commit, push)

This is the ONLY mechanism that creates or modifies files outside .github-agenticana/.
The script must be idempotent — running it multiple times produces the same output.

Use the exact script content from specification-final.md §4.2.
Make the file executable (chmod +x).
```

### Request 1.7 — Create `.github-agenticana/reconciler/manifest.yaml`

```
Create the file .github-agenticana/reconciler/manifest.yaml that declares every
external file the reconciler generates. This enables audit and validation.

Include version: 1 and list these generated_files:
- source: .github-agenticana/workflows/github-agenticana-agent.yml
  target: .github/workflows/github-agenticana-agent.yml
  description: Primary agent workflow — triggers on issue events, runs agent CLI

- source: .github-agenticana/templates/chat.md
  target: .github/ISSUE_TEMPLATE/agenticana-chat.md
  description: Issue template for chatting with agents

- source: .github-agenticana/templates/debate.md
  target: .github/ISSUE_TEMPLATE/agenticana-debate.md
  description: Issue template for multi-agent debates

- source: .github-agenticana/templates/architecture.md
  target: .github/ISSUE_TEMPLATE/agenticana-architecture.md
  description: Issue template for architecture reviews

- source: .github-agenticana/templates/security-audit.md
  target: .github/ISSUE_TEMPLATE/agenticana-security-audit.md
  description: Issue template for security audits

Also include: reconciler_script: .github-agenticana/reconciler/apply.sh

Format as valid YAML with descriptive comments.
```

### Request 1.8 — Create `.github-agenticana/reconciler/README.md`

```
Create the file .github-agenticana/reconciler/README.md with usage instructions for
the reconciler.

Include:
- What the reconciler does (bridges .github-agenticana/ to GitHub-required locations)
- When to run it (first installation, after upstream pull, after editing sources)
- How to run it: bash .github-agenticana/reconciler/apply.sh
- The post-update workflow for pulling upstream changes:
    1. git fetch upstream && git merge upstream/main
    2. Resolve conflicts (should be NONE in .github-agenticana/)
    3. bash .github-agenticana/reconciler/apply.sh
    4. git diff && git add -A && git commit -m "agenticana: reconcile after upstream pull"
    5. git push
- Warning about collision detection when upstream modifies generated files
- Note that the reconciler is idempotent and the manifest lists all external files
```

### Verification for Phase 1

```
Verify Phase 1 by running:
  bash .github-agenticana/reconciler/apply.sh
The script should complete without errors. Running it a second time should produce
identical output (idempotent). At this point there are no source workflows or templates
yet, so it should report nothing to copy but exit cleanly.
```

---

## Phase 2: Workflow and Templates

### Request 2.1 — Create `.github-agenticana/workflows/github-agenticana-agent.yml`

```
Create the file .github-agenticana/workflows/github-agenticana-agent.yml — the
primary GitHub Actions workflow definition. This is the source of truth; the reconciler
copies it to .github/workflows/.

The workflow must:
- Name: agenticana-agent
- Trigger on: issues (opened, labeled), issue_comment (created)
- Permissions: contents: write, issues: write, actions: write
- Concurrency group: agenticana-${{ github.repository }}-issue-${{ github.event.issue.number }}
  with cancel-in-progress: false

Jobs (single job: run-agent):
- runs-on: ubuntu-latest
- if: issue has 'agenticana' label AND (event is issue OR comment is not from a bot)
- timeout-minutes: 15

Steps in exact order:
1. Authorize — check collaborator permission (admin/maintain/write), fail if unauthorized
2. Reject — on auth failure, add thumbs-down reaction
3. Checkout — actions/checkout@v4 with default branch, fetch-depth: 0
4. Indicate — add rocket reaction to issue or comment
5. Setup Python — actions/setup-python@v5 with python 3.11
6. Setup Node.js — actions/setup-node@v4 with node 20
7. Cache dependencies — actions/cache@v4 for ~/.cache/pip and mcp/node_modules
8. Install dependencies — pip install -r requirements.txt && cd mcp && npm install
9. Detect execution mode — check labels and body for debate triggers, output mode=debate or mode=agent
10. Run debate (if mode==debate) — python .github-agenticana/scripts/debate_runner.py with all env vars
11. Route and execute agent (if mode==agent) — python scripts/agent_cli.py @auto with all env vars
12. Commit state — git add .github-agenticana/state/ only, commit, push with retry (up to 10 attempts, -X theirs)
13. Post debate result (if mode==debate) — post .github-agenticana/state/debates/{N}-latest.md as issue comment
14. Post reply (if mode==agent) — add thumbs-up or thumbs-down reaction based on job status

Environment variables for LLM steps: GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY,
GITHUB_TOKEN, ISSUE_NUMBER, ISSUE_BODY, COMMENT_BODY, ISSUE_LABELS, EVENT_NAME.

Use the exact workflow YAML from specification-final.md §5.1.
```

### Request 2.2 — Create `.github-agenticana/templates/chat.md`

```
Create the file .github-agenticana/templates/chat.md — the issue template for chatting
with any of the 20 Agenticana specialist agents.

Use this exact content:

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

### Request 2.3 — Create `.github-agenticana/templates/debate.md`

```
Create the file .github-agenticana/templates/debate.md — the issue template for
triggering a multi-agent Simulacrum debate.

Use this exact content:

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
```

### Request 2.4 — Create `.github-agenticana/templates/architecture.md`

```
Create the file .github-agenticana/templates/architecture.md — the issue template for
triggering a multi-agent architecture review debate.

Use this exact content:

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

### Request 2.5 — Create `.github-agenticana/templates/security-audit.md`

```
Create the file .github-agenticana/templates/security-audit.md — the issue template for
requesting a security audit.

Use this exact content:

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

### Request 2.6 — Run the reconciler to generate external files

```
Run the reconciler to copy the workflow and templates to their GitHub-required locations:

  bash .github-agenticana/reconciler/apply.sh

Verify:
- .github/workflows/github-agenticana-agent.yml exists and matches the source
- .github/ISSUE_TEMPLATE/agenticana-chat.md exists
- .github/ISSUE_TEMPLATE/agenticana-debate.md exists
- .github/ISSUE_TEMPLATE/agenticana-architecture.md exists
- .github/ISSUE_TEMPLATE/agenticana-security-audit.md exists
```

### Verification for Phase 2

```
Verify Phase 2:
1. Run bash .github-agenticana/reconciler/apply.sh — should report 1 workflow and
   4 templates copied.
2. Run it again — output is identical (idempotent).
3. Diff the source and target files — they should be byte-identical.
```

---

## Phase 3: Fork-Specific Scripts

### Request 3.1 — Create `.github-agenticana/scripts/debate_runner.py`

```
Create the file .github-agenticana/scripts/debate_runner.py — the orchestrator entry
point for multi-agent debates. Called by the GitHub Actions workflow when debate mode
is detected.

The script must:

1. Accept command-line arguments:
   --issue-number (int): The GitHub issue number
   --input (str): The issue body or comment body text
   --labels (str): JSON array of issue label names

2. Implement parse_debate_config(text) function:
   - Extract debate configuration from HTML comments in the input text
   - Look for <!-- debate-config ... --> blocks
   - Parse key: value pairs for agents, rounds, mode
   - Clamp rounds to range [1, 5]
   - Return a dict with the parsed config

3. Implement select_agents(explicit, labels, topic, min_agents=3, max_agents=7) function:
   - Priority 1: Use explicitly specified agents from debate-config
   - Priority 2: Derive agents from issue labels using the label-to-agent mapping
   - Priority 3: Use NL keyword matching (import from nl_swarm.py if available)
   - Priority 4: Fill with defaults [backend-specialist, security-auditor, frontend-specialist]
   - Ensure minimum 3 agents, cap at 7
   - Return the agent list

4. Implement run_debate(issue_number, input_text, labels) function:
   - Parse debate config
   - Select agents via cascade
   - Check ReasoningBank for prior debates (similarity > 0.85 threshold)
   - If prior debate found, format and return it with a staleness note if > 30 days old
   - Otherwise, run Simulacrum:
     - If mode == "real": import and call real_simulacrum.run_real_simulacrum()
     - If mode == "logic": import and call simulacrum.run_simulacrum()
   - Format result as Markdown (save to .github-agenticana/state/debates/{issue}-latest.md)
   - Save full transcript as JSON (save to .github-agenticana/state/debates/{issue}-{session}.json)
   - Record decision to ReasoningBank
   - Return result

5. Main entry point:
   - Parse args with argparse
   - Call run_debate()
   - Exit 0 on success, 1 on failure

Include the debate JSON schema in a docstring:
{
  "session_id": "...",
  "issue_number": N,
  "topic": "...",
  "mode": "LIVE_LLM" or "LOGIC",
  "agents": [...],
  "config": { "rounds": N, "mode": "real"|"logic", "source": "issue_body"|"comment" },
  "winning_agent": "...",
  "winning_proposal": "...",
  "vote_tally": { "agent": N, ... },
  "all_proposals": { "agent": "...", ... },
  "constraints": ["[agent] constraint text", ...],
  "timestamp": "ISO 8601",
  "duration_seconds": N,
  "llm_calls": N,
  "transcript": [ { "timestamp", "phase", "speaker", "content", "mode" }, ... ]
}

Include the structured Markdown output format in a docstring showing the 5-phase
format: Session header, Phase 1 (Opening Positions), Phase 2 (Key Arguments table),
Phase 3 (Proposals table), Phase 4 (Vote Tally), Phase 5 (Consensus with winning
proposal and all agent constraints), and a collapsible metadata section.

Use agent emoji mapping from config/debate-defaults.yaml for output formatting.

Handle errors gracefully — if the Simulacrum engine is not available, log the error
and exit with a clear message. Do not crash silently.
```

### Request 3.2 — Create `.github-agenticana/scripts/state_manager.py`

```
Create the file .github-agenticana/scripts/state_manager.py — session and state
management for the contained agent system.

The script must implement:

1. STATE_DIR constant pointing to .github-agenticana/state/

2. get_or_create_issue_mapping(issue_number) function:
   - Check if state/issues/{issue_number}.json exists
   - If yes, read and return the mapping
   - If no, create a new mapping with:
     { "issueNumber": N, "agent": null, "sessionPath": null, "debates": [], "updatedAt": ISO timestamp }
   - Return the mapping

3. update_issue_mapping(issue_number, agent, session_path) function:
   - Read existing mapping (or create new)
   - Update agent, sessionPath, updatedAt
   - Write back to state/issues/{issue_number}.json

4. add_debate_to_issue(issue_number, session_id, transcript_path, topic, winner) function:
   - Read existing mapping
   - Append to debates array:
     { "sessionId": session_id, "path": transcript_path, "topic": topic, "winner": winner, "timestamp": ISO }
   - Update updatedAt
   - Write back

5. create_session_file(issue_number) function:
   - Create a new JSONL session file at state/sessions/{timestamp}.jsonl
   - Return the file path

6. append_to_session(session_path, event) function:
   - Append a JSON line to the session file
   - Each line is a conversation event: { "timestamp", "role", "content", "agent" }

7. save_debate_transcript(issue_number, session_id, transcript_json) function:
   - Save full transcript to state/debates/{issue_number}-{session_id}.json
   - Return the file path

8. save_debate_result(issue_number, markdown_content) function:
   - Save formatted Markdown to state/debates/{issue_number}-latest.md
   - Return the file path

All functions must create parent directories if they don't exist (use os.makedirs).
All timestamps must be ISO 8601 format.
All JSON files must be written with indent=2 for readability.
```

### Request 3.3 — Create `.github-agenticana/scripts/agent_wrapper.sh`

```
Create the file .github-agenticana/scripts/agent_wrapper.sh — a wrapper script that
calls the repository's existing scripts/agent_cli.py with containment-aware state
management.

The script must:
1. Use bash with set -euo pipefail
2. Accept the same arguments as agent_cli.py
3. Call python scripts/agent_cli.py with all forwarded arguments
4. After execution, ensure only .github-agenticana/state/ changes are staged for commit
5. Log what it did

This wrapper ensures the agent CLI is called as-is (no modifications to the upstream
script) while keeping state writes contained.

Make the file executable (chmod +x).
```

### Verification for Phase 3

```
Verify Phase 3:
1. python -c "import ast; ast.parse(open('.github-agenticana/scripts/debate_runner.py').read())"
   — should parse without syntax errors
2. python -c "import ast; ast.parse(open('.github-agenticana/scripts/state_manager.py').read())"
   — should parse without syntax errors
3. bash -n .github-agenticana/scripts/agent_wrapper.sh
   — should pass syntax check
```

---

## Phase 4: Governance

### Request 4.1 — Create `.github-agenticana/governance/AGENTS.md`

```
Create the file .github-agenticana/governance/AGENTS.md — the master agent identity
document.

List all 20 specialist agents with their:
- Name
- Label that triggers them
- Complexity tier (SIMPLE, MODERATE, COMPLEX)
- Domain of expertise
- Emoji identifier
- Default DEFCON level

The 20 agents are:
1. orchestrator — coordination, architecture — COMPLEX — DEFCON 4 — 🎼
2. frontend-specialist — React, Next.js, UI, CSS — MODERATE — DEFCON 5 — 🎨
3. backend-specialist — APIs, Node.js, Express, server — MODERATE — DEFCON 5 — 🔧
4. mobile-developer — React Native, Expo, iOS/Android — COMPLEX — DEFCON 5 — 📱
5. database-architect — Prisma, SQL, schemas, migrations — MODERATE — DEFCON 5 — 🗄️
6. debugger — bug fixes, errors, crashes — MODERATE — DEFCON 5 — 🐛
7. security-auditor — auth reviews, vulnerability checks — MODERATE — DEFCON 4 — 🔒
8. penetration-tester — offensive security testing — COMPLEX — DEFCON 3 — 🗡️
9. devops-engineer — Docker, CI/CD, GitHub Actions — MODERATE — DEFCON 5 — 🚀
10. test-engineer — unit tests, E2E tests, coverage — SIMPLE — DEFCON 5 — 🧪
11. qa-automation-engineer — test automation, quality gates — MODERATE — DEFCON 5 — ✅
12. performance-optimizer — slow pages, bundle size, LCP — MODERATE — DEFCON 5 — ⚡
13. documentation-writer — documentation generation — SIMPLE — DEFCON 5 — 📝
14. explorer-agent — codebase exploration, discovery — SIMPLE — DEFCON 5 — 🔭
15. code-archaeologist — legacy code analysis — SIMPLE — DEFCON 5 — 🏛️
16. game-developer — game development — COMPLEX — DEFCON 5 — 🎮
17. seo-specialist — SEO analysis and optimization — SIMPLE — DEFCON 5 — 🔍
18. project-planner — project planning, roadmapping — COMPLEX — DEFCON 5 — 📋
19. product-manager — product strategy, prioritization — MODERATE — DEFCON 5 — 📊

(Note: The specification references "20 specialist agents" — the 19 above plus the
orchestrator acting in debate mode as the 20th role. The label "agenticana" is auto-routed
and does not map to a named agent.)

Include a note that agent YAML specs live in agents/*.yaml in the repo root and are
read at runtime by the workflow (not modified).
```

### Request 4.2 — Create `.github-agenticana/governance/FOUR-LAWS.md`

```
Create the file .github-agenticana/governance/FOUR-LAWS.md — the ethical foundation
for the Agenticana agent system, adapted from Asimov's Laws.

Define four laws:

| Law | Principle | Agenticana Application |
|-----|-----------|----------------------|
| Zeroth | Protect humanity as a whole | No monopolistic patterns; open source remains open; interoperability preserved |
| First | Do no harm to humans or communities | Never endanger safety, privacy, or civil rights; refuse malicious code generation |
| Second | Obey human operators (unless conflicts with First) | Faithfully execute instructions; be transparent about limitations |
| Third | Preserve own integrity (unless conflicts with First or Second) | Maintain security and audit trails; resist corruption |

Include an explanation that these laws are appended to every LLM system prompt via
APPEND_SYSTEM.md, ensuring all agents operate within this ethical framework.
```

### Request 4.3 — Create `.github-agenticana/governance/DEFCON.md`

```
Create the file .github-agenticana/governance/DEFCON.md — readiness level definitions
for progressive capability lockdown.

Define five DEFCON levels:

| Level | Name | Agent Capabilities |
|-------|------|--------------------|
| DEFCON 1 | Maximum Readiness | All operations suspended. No file modifications, no tool use, no code execution. |
| DEFCON 2 | High Readiness | Read-only, advisory only. No file modifications. |
| DEFCON 3 | Increased Readiness | Read-only. Explain planned changes and await human approval before any write. |
| DEFCON 4 | Above Normal | Full capability with elevated discipline. Confirm intent before every write. |
| DEFCON 5 | Normal | Standard operations. All capabilities available per agent spec. |

Include per-agent DEFCON defaults:
- penetration-tester: DEFCON 3 (explain before acting)
- security-auditor: DEFCON 4 (elevated discipline)
- documentation-writer: DEFCON 5 (full autonomy)
- All other agents: DEFCON 5

Include DEFCON interaction with debates:
| DEFCON Level | Debate Behavior |
|-------------|----------------|
| DEFCON 1 | Debates suspended. No LLM calls. |
| DEFCON 2 | Debates run in logic mode only (no LLM calls). Results are advisory. |
| DEFCON 3 | Debates run in real mode but consensus is not auto-applied. Human must approve. |
| DEFCON 4 | Normal debate operation with elevated logging. |
| DEFCON 5 | Normal debate operation. |
```

### Request 4.4 — Create `.github-agenticana/governance/SECURITY-ASSESSMENT.md`

```
Create the file .github-agenticana/governance/SECURITY-ASSESSMENT.md — the complete
self-audit of known security risks.

List all 15 security findings (SEC-001 through SEC-015):

| ID | Severity | Finding | Mitigation |
|----|----------|---------|------------|
| SEC-001 | 🔴 Critical | Repository write access via GITHUB_TOKEN | Scope permissions in workflow YAML; use branch protection |
| SEC-002 | 🔴 Critical | Unrestricted network egress from runner | Limit to known LLM API endpoints via firewall rules |
| SEC-003 | 🟠 High | Passwordless sudo on runner | Agent code should never require sudo; add linting check |
| SEC-004 | 🔴 Critical | LLM API keys exposed in environment | Use repository secrets; never log env vars |
| SEC-005 | 🟠 High | No branch protection on default branch | Enable branch protection; require PR reviews for agent commits |
| SEC-006 | 🟠 High | Agent can self-modify workflow files | Exclude .github/workflows/ from agent write paths |
| SEC-007 | 🟡 Medium | Multiple third-party dependencies | Pin versions; audit lockfiles; use dependabot |
| SEC-008 | 🟠 High | Concurrent agents may produce conflicting commits | Push retry with -X theirs rebase strategy |
| SEC-009 | 🟡 Medium | Debate config in issue body could be manipulated by unauthorized users | Only collaborators can trigger debates (authorization step) |
| SEC-010 | 🟡 Medium | High agent count × high round count = expensive debates | Hard caps: max 7 agents, max 5 rounds, max 49 LLM calls per debate |
| SEC-011 | 🟢 Low | Debate transcripts may contain sensitive reasoning | Transcripts committed to repo (same access control as code) |
| SEC-012 | 🟡 Medium | ReasoningBank fast-path could serve stale consensus | Include timestamp and staleness warning if prior debate is older than 30 days |
| SEC-013 | 🟢 Low | Reconciler could be tricked into overwriting critical files | Manifest declares explicit target paths; reconciler only copies from declared sources |
| SEC-014 | 🟡 Medium | git add .github-agenticana/state/ could still be large | Add .gitkeep for empty directories; size limits in state manager |
| SEC-015 | 🟢 Low | Upstream could add .github-agenticana/ directory | Unlikely — directory name is fork-specific. Migration available if needed. |

Include a note on radical transparency: this assessment is public by design.
```

### Request 4.5 — Create `.github-agenticana/governance/APPEND_SYSTEM.md`

```
Create the file .github-agenticana/governance/APPEND_SYSTEM.md — the behavioral
constitution that is appended to all LLM system prompts.

This file should contain the text that is injected into every LLM call made by any
agent. It should include:

1. Agent identity preamble — "You are {agent_name}, a specialist agent in the
   Agenticana multi-agent system."
2. The Four Laws reference — all four laws summarized in one paragraph
3. DEFCON awareness — "You are currently operating at DEFCON {level}. Adjust your
   behavior accordingly."
4. Containment rule — "All state must be written to .github-agenticana/state/. Do
   not create or modify files outside .github-agenticana/."
5. Output discipline — keep responses concise, structured, and actionable
6. Safety clause — refuse to generate malicious code, expose secrets, or bypass
   security controls

Format as a Markdown template with {placeholders} for runtime values.
```

### Verification for Phase 4

```
Verify Phase 4:
1. All five governance files exist in .github-agenticana/governance/
2. Each file is valid Markdown
3. SECURITY-ASSESSMENT.md contains all 15 findings (SEC-001 through SEC-015)
4. DEFCON.md defines all 5 levels plus debate interaction table
5. FOUR-LAWS.md defines all 4 laws with Agenticana applications
```

---

## Phase 5: Integration and Optimization

### Request 5.1 — Verify end-to-end flow

```
Review the entire pipeline and verify the end-to-end flow works as documented:

1. Issue created with "agenticana" label
2. Workflow triggers (from .github/workflows/github-agenticana-agent.yml)
3. Authorization check (collaborator permission)
4. Execution mode detection (agent vs debate)
5. Agent routing or debate execution
6. State committed to .github-agenticana/state/
7. Reply posted to issue

Check that:
- The workflow YAML references the correct script paths:
  - .github-agenticana/scripts/debate_runner.py for debates
  - scripts/agent_cli.py for single-agent (unchanged upstream script)
- The git add scope is limited to .github-agenticana/state/
- The push retry strategy uses -X theirs with backoff
- All environment variables are passed correctly

Report any discrepancies between the specification and the implemented files.
Fix any issues found.
```

### Request 5.2 — Verify dependency caching

```
Verify that the workflow includes proper dependency caching:

- actions/cache@v4 should cache:
  - ~/.cache/pip (Python dependencies)
  - mcp/node_modules (Node.js dependencies)
- Cache key should use: hashFiles('requirements.txt', 'mcp/package.json')
- This saves ~30-40 seconds per run

Check the workflow file and confirm this is present.
```

### Request 5.3 — Verify ReasoningBank integration

```
Verify the ReasoningBank integration follows the containment model:

- Read: agents read from memory/reasoning-bank/ in the repo root (existing location)
- Write: new decisions are written to .github-agenticana/state/reasoning-bank/
- The git add .github-agenticana/state/ scope ensures only contained writes are committed
- The debate_runner.py checks ReasoningBank with 0.85 similarity threshold
- Stale results (> 30 days) include a warning note

Check debate_runner.py and state_manager.py for correct paths and behavior.
```

### Request 5.4 — Verify reconciler integration

```
Verify that the reconciler integrates correctly into the workflow:

1. Run: bash .github-agenticana/reconciler/apply.sh
2. Check output — should list each copied file with emoji indicators
3. Verify generated files match their sources exactly (byte-identical)
4. Run again — output is identical (idempotent)
5. Check manifest.yaml against actual generated files — all declared files should exist

Report any issues.
```

### Verification for Phase 5

```
Verify Phase 5:
1. Workflow references correct paths for all scripts
2. Dependency caching is configured
3. ReasoningBank reads from repo root, writes to contained state
4. Reconciler produces correct output and is idempotent
5. git add scope is limited to .github-agenticana/state/
```

---

## Phase 6: Multi-Agent Debates

### Request 6.1 — Verify debate mode detection

```
Verify the workflow's detect_mode step correctly identifies debate triggers:

Three triggers must be detected:
1. Issue has "debate" label → mode=debate
2. Issue has "architecture" label → mode=debate
3. Issue body or comment starts with "@debate" → mode=debate
4. Otherwise → mode=agent

Check the detect_mode step in the workflow YAML and confirm it handles all three
trigger types correctly.
```

### Request 6.2 — Verify debate runner integration with Simulacrum

```
Verify that debate_runner.py correctly integrates with the existing Simulacrum engines:

1. For mode=="real": imports from scripts/real_simulacrum.py
2. For mode=="logic": imports from scripts/simulacrum.py
3. These are upstream scripts — they are called as-is, not modified
4. The debate runner passes: topic, agents list, rounds count
5. The result is formatted as structured Markdown per the 5-phase format

Check that the import paths are correct and error handling covers missing modules.
```

### Request 6.3 — Verify debate state persistence

```
Verify that debate state is correctly persisted in .github-agenticana/state/debates/:

1. Full transcript saved as JSON: state/debates/{issue_number}-{session_id}.json
2. Latest result saved as Markdown: state/debates/{issue_number}-latest.md
3. Issue mapping updated with debate reference
4. The Markdown file is what gets posted as the issue comment
5. The JSON file follows the schema defined in the specification

Check state_manager.py save_debate_transcript() and save_debate_result() functions.
```

### Request 6.4 — Verify ReasoningBank fast-path for debates

```
Verify the ReasoningBank fast-path in debate_runner.py:

1. Before running a new debate, check ReasoningBank for prior debates on similar topics
2. Similarity threshold: 0.85
3. If a matching prior debate is found:
   - Return the prior result with a note explaining it's from a prior debate
   - Include a staleness warning if the prior debate is > 30 days old
   - Save ~60% of LLM cost
4. If no match, proceed with full Simulacrum execution

Check the run_debate() function in debate_runner.py.
```

### Verification for Phase 6

```
Verify Phase 6:
1. Debate mode detection handles all three triggers
2. Debate runner integrates with both Simulacrum engines (real and logic)
3. Debate state is persisted in .github-agenticana/state/debates/
4. ReasoningBank fast-path works with 0.85 threshold
5. Structured Markdown output follows the 5-phase format
```

---

## Phase 7: Future Enhancements (Design Only)

### Request 7.1 — Document future debate enhancements

```
Add a section to .github-agenticana/analysis/specification-final.md (or create a
separate .github-agenticana/analysis/future-enhancements.md) documenting planned
but not yet implemented features:

1. Debate chains — one debate's consensus feeds into a follow-up debate
2. Debate branches — fork a debate into two parallel tracks exploring different options
3. Human-in-the-loop — allow a human to interject during a debate round
4. Debate analytics — dashboard showing debate frequency, cost, consensus quality
5. Cross-issue debate references — link related debates across issues
6. Debate templates library — pre-configured debate setups for common decisions
7. Automated follow-up — after consensus, automatically create implementation issues

Mark these as Phase 7 / future enhancements. Do not implement them — document only.
```

---

## Phase 8: Master Fork Cleanup

### Request 8.1 — Remove upstream disabled workflows

```
Delete the directory .github/workflows-disabled/ and all its contents:
- .github/workflows-disabled/ci.yml
- .github/workflows-disabled/release.yml

These are upstream development CI/CD workflows that are irrelevant to our
execution-focused fork. They were already disabled (via the -disabled suffix)
but their presence causes confusion.
```

### Request 8.2 — Remove upstream disabled issue templates

```
Delete the directory .github/ISSUE_TEMPLATE-disabled/ and all its contents:
- .github/ISSUE_TEMPLATE-disabled/bug-report.md
- .github/ISSUE_TEMPLATE-disabled/new-agent.md
- .github/ISSUE_TEMPLATE-disabled/new-phase.md

These are upstream development issue templates that interfere with our
agent-interaction issue templates. They were already disabled but still
clutter the .github/ directory.
```

### Request 8.3 — Remove upstream disabled PR template

```
Delete the directory .github/PR_TEMPLATE-disabled/ and all its contents:
- .github/PR_TEMPLATE-disabled/PULL_REQUEST_TEMPLATE.md

This is the upstream development PR template that interferes with our PR UX.
```

### Request 8.4 — Verify clean `.github/` directory

```
After cleanup, verify the .github/ directory contains only:
- .github/copilot-instructions.md (if it exists — GitHub Copilot config)
- .github/workflows/github-agenticana-agent.yml (generated by reconciler)
- .github/ISSUE_TEMPLATE/agenticana-*.md (generated by reconciler)

No other files should exist. No disabled upstream artifacts should remain.

If .github/copilot-instructions.md exists, check whether it references the
.github-agenticana/ containment model and governance files. If not, consider
whether the reconciler should also manage this file.
```

### Verification for Phase 8

```
Verify Phase 8:
1. .github/workflows-disabled/ does not exist
2. .github/ISSUE_TEMPLATE-disabled/ does not exist
3. .github/PR_TEMPLATE-disabled/ does not exist
4. .github/ contains only copilot-instructions.md and reconciler-generated files
```

---

## Final Verification

### Request FINAL — End-to-end validation

```
Perform a complete end-to-end validation of the entire specification implementation:

1. Directory structure:
   - .github-agenticana/ exists with all subdirectories
   - config/ has agents.yaml, routing-rules.yaml, debate-defaults.yaml, cost-limits.yaml
   - governance/ has AGENTS.md, FOUR-LAWS.md, DEFCON.md, SECURITY-ASSESSMENT.md, APPEND_SYSTEM.md
   - scripts/ has debate_runner.py, state_manager.py, agent_wrapper.sh
   - workflows/ has github-agenticana-agent.yml
   - templates/ has chat.md, debate.md, architecture.md, security-audit.md
   - reconciler/ has apply.sh, manifest.yaml, README.md
   - state/ has issues/, sessions/, debates/, attestations/, reasoning-bank/

2. Reconciler:
   - bash .github-agenticana/reconciler/apply.sh runs without errors
   - Generates all files declared in manifest.yaml
   - Is idempotent (second run produces identical output)

3. Workflow:
   - YAML is valid
   - References correct script paths
   - Has proper permissions, concurrency, and timeout
   - git add scope limited to .github-agenticana/state/

4. Scripts:
   - debate_runner.py has no syntax errors
   - state_manager.py has no syntax errors
   - agent_wrapper.sh passes bash syntax check

5. Governance:
   - All 15 security findings documented
   - All 5 DEFCON levels defined
   - All 4 laws defined
   - All 20 agents listed

6. Cleanup:
   - No disabled upstream artifacts in .github/
   - Clean .github/ directory with only active files

7. Containment rules verified:
   - No files created or edited outside .github-agenticana/ (except by reconciler)
   - All state writes go to .github-agenticana/state/
   - Reconciler is the ONLY mechanism creating external files
   - External files are declared in manifest.yaml

Report: PASS or FAIL for each check, with details on any failures.
```
