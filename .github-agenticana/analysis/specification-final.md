# Specification v4 (Final): GitHub as AI Infrastructure for Agenticana — Consolidated

> **Version:** 4.0.0 | **Date:** 2026-03-03 | **Consolidates:** [v1](specification-v1.md), [v2](specification-v2.md), [v3](specification-v3.md)
> The definitive specification for running Agenticana as a repository-native, multi-agent AI system — fully self-contained inside `.github-agenticana/`, fork-safe, with multi-agent debates as a first-class primitive, and upstream artifacts removed.

---

## Executive Summary

GitHub Minimum Intelligence proved that a single folder, a workflow file, and an LLM API key can turn any repository into an interactive AI collaborator. Every GitHub primitive — Issues, Actions, Git commits, Secrets, Markdown files, branch protection — maps to a layer of intelligence: input, compute, memory, credentials, identity, and governance.

This specification defines how `github-agenticana`, which already contains 20 specialist agents, an MCP server, a model router, a reasoning bank, and a full governance framework, implements this pattern at scale — making the repository itself the runtime, the memory, and the interface for a multi-agent AI system.

The specification consolidates three prior versions:

- **v1** established the repository-as-runtime pattern: GitHub Issues as input, Actions as compute, git as memory, Markdown as identity.
- **v2** promoted multi-agent debates (the Simulacrum protocol) to a first-class primitive — any issue can trigger a structured debate between specialist agents.
- **v3** introduced fork-safe containment — all intelligence confined to `.github-agenticana/`, with a reconciler to bridge to GitHub-required file locations.
- **v4 (this document)** consolidates all three into a single self-contained specification and adds master fork cleanup — removing upstream workflows and templates that are irrelevant to execution.

The core thesis:

> **A repository is not just a place to store code. With the right loop — issues as input, Actions as runtime, an LLM as reasoning, git as memory — it becomes a place where intelligence can be born, shaped, audited, and trusted.**

---

## 1. Master Fork Cleanup: Removing Upstream Workflows and Templates

### 1.1 The Problem

When this repository is forked for use as an AI-powered execution environment, the upstream (master) fork's development-oriented files remain in the repository:

- `.github/workflows-disabled/` — CI and release workflows (`ci.yml`, `release.yml`)
- `.github/ISSUE_TEMPLATE-disabled/` — Development issue templates (`bug-report.md`, `new-agent.md`, `new-phase.md`)
- `.github/PR_TEMPLATE-disabled/` — Development PR template (`PULL_REQUEST_TEMPLATE.md`)

These files, even when disabled (via the `-disabled` suffix), interfere with the fork's own workflows, issue creation UX, and pull request experience. They create confusion about which templates and workflows are active and clutter the `.github/` directory.

### 1.2 The Decision

**All workflows and templates from the master fork are removed.** We are only **executing** the code in this repository, not **developing** it. The upstream's development infrastructure is irrelevant to our use case.

| Removed Directory | Contents | Reason for Removal |
|-------------------|----------|-------------------|
| `.github/workflows-disabled/` | `ci.yml`, `release.yml` | Development CI/CD — we don't run CI on the Agenticana codebase itself |
| `.github/ISSUE_TEMPLATE-disabled/` | `bug-report.md`, `new-agent.md`, `new-phase.md` | Development issue templates — interfere with our agent-interaction issue templates |
| `.github/PR_TEMPLATE-disabled/` | `PULL_REQUEST_TEMPLATE.md` | Development PR template — interferes with our PR UX |

### 1.3 What Replaces Them

Our own workflows, issue templates, and PR templates live inside `.github-agenticana/` per the v3 containment model:

- **Workflows:** `.github-agenticana/workflows/github-agenticana-agent.yml` → reconciled to `.github/workflows/`
- **Issue templates:** `.github-agenticana/templates/chat.md`, `debate.md`, `architecture.md`, `security-audit.md` → reconciled to `.github/ISSUE_TEMPLATE/`

The reconciler from v3 generates the actual `.github/` files we need. We do not need the upstream's disabled copies.

### 1.4 Impact on Upstream Pulls

Removing these directories means that if the upstream re-enables or modifies its workflows/templates, a future `git pull upstream main` may reintroduce them. The reconciler handles this by overwriting `.github/` files with our fork's versions. Any reintroduced upstream files outside the reconciler's manifest can be safely deleted after the pull.

---

## 1. The Fork-Safe Containment Model

### 1.1 The Problem

When a repository is forked and the fork adds AI infrastructure, the fork master faces a recurring problem:

```
Upstream pushes changes to:
  - .github/workflows/ci.yml
  - scripts/agent_cli.py
  - requirements.txt
  - .github/ISSUE_TEMPLATE/bug-report.md

Fork has modified the same files for AI integration.

Result: Merge conflicts on every upstream pull.
```

This is unsustainable. The fork master must either:
1. Manually resolve conflicts every time (error-prone, time-consuming)
2. Stop pulling upstream changes (fork diverges, misses fixes and features)
3. Accept that AI infrastructure will be overwritten (agent stops working)

### 1.2 The Solution: Directory Containment

All AI infrastructure lives inside a single directory that the upstream does not own:

```
.github-agenticana/           ← EVERYTHING lives here
├── analysis/                 ← Specifications (this document)
├── config/                   ← Agent configuration, routing rules
├── governance/               ← Identity, laws, DEFCON, security assessment
├── scripts/                  ← Fork-specific scripts (debate runner, reconciler)
├── state/                    ← Runtime state (sessions, debates, issue mappings)
├── templates/                ← Source templates for issues and workflows
├── workflows/                ← Workflow definitions (source of truth)
└── reconciler/               ← The automated change maker
```

### 1.3 The Two Rules

**Rule 1: No files outside `.github-agenticana/` may be created or edited.**

The AI infrastructure does not touch:
- `.github/workflows/` — workflow files
- `.github/ISSUE_TEMPLATE/` — issue templates
- `scripts/` — existing repository scripts
- `requirements.txt` — Python dependencies
- `mcp/` — MCP server code
- Any other file in the repository root or subdirectories

**Rule 2: Files inside `.github-agenticana/` may be created but not modified.**

This ensures:
- Fork-specific additions are append-only and never conflict with upstream
- State files (sessions, debates) are naturally append-only (new files per session)
- Configuration is versioned by creating new files (e.g., `config-v1.yaml`, `config-v2.yaml`)
- The reconciler generates fresh output each time rather than patching existing files

### 1.4 The Bridge: Automated Reconciler

Some GitHub features require files in specific locations:
- GitHub Actions workflows **must** be in `.github/workflows/`
- Issue templates **must** be in `.github/ISSUE_TEMPLATE/`

The reconciler is a script that lives inside `.github-agenticana/reconciler/` and generates these external files from source templates stored inside `.github-agenticana/`. It runs:
1. **After every upstream pull** — to reapply fork-specific changes
2. **On first installation** — to set up the external files initially
3. **On demand** — when the fork master wants to regenerate external files

```
.github-agenticana/workflows/github-agenticana-agent.yml   ← Source of truth
                          │
                    reconciler/apply.sh
                          │
                          ▼
.github/workflows/github-agenticana-agent.yml               ← Generated (gitignored or overwritten)
```

The reconciler is the **only mechanism** that creates or modifies files outside `.github-agenticana/`.

---


---

## 2. Architectural Foundation (Evolved from v1 §1, v2 §1)

### 2.1 The GitHub Primitives Stack

The primitives stack from v1 remains unchanged in function, but the **implementation column** changes to reflect containment:

| Primitive | Infrastructure Role | v3 Implementation (Contained) |
|-----------|-------------------|-------------------------------|
| **GitHub Issues** | Conversational UI (input/output) | Issue → Agent routing via labels; comments as dialogue (unchanged) |
| **GitHub Actions** | Compute runtime (execution) | Workflow **source** in `.github-agenticana/workflows/`; reconciler copies to `.github/workflows/` |
| **Git commits** | Persistent memory (state) | State committed to `.github-agenticana/state/` exclusively |
| **Repository Secrets** | Credential store (security) | LLM API keys stored in repo/org secrets (unchanged — secrets are not files) |
| **Markdown files** | Identity and governance (configuration) | Agent specs in `.github-agenticana/config/`; governance in `.github-agenticana/governance/` |
| **Branch protection** | Access control (authorization) | Collaborator-only invocation; PR-gated commits (unchanged — branch protection is a setting, not a file) |

### 2.2 The Closed Loop (Unchanged from v2)

The closed loop from v1/v2 remains unchanged. The containment model changes **where** files live, not **how** the loop operates.

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
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  .github-agenticana/ ← ALL intelligence contained here       │    │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │    │
│  │  │ config/ │ │ state/   │ │ govern/  │ │ reconciler/    │   │    │
│  │  │ scripts/│ │ workflows│ │ templates│ │ analysis/      │   │    │
│  │  └─────────┘ └──────────┘ └──────────┘ └────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 Event-Driven Cognition (Unchanged from v1)

The event-driven cognition model from v1 §1.3 is unchanged. Social events trigger computation, computation produces artifacts, artifacts trigger future events.

---


### 2.3 Event-Driven Cognition

The fundamental pattern is event-driven cognition:

1. A **social event** (issue opened, comment posted, label applied) occurs
2. **Infrastructure** transforms it into computation (Actions workflow triggers)
3. **Computation** produces artifacts (commits, comments, code changes)
4. **Artifacts** trigger future social events (user reads reply, collaborators review)

This creates a self-sustaining loop where the repository continuously accumulates intelligence through the interaction of human intent and machine execution.

---

## 3. Directory Structure

### 3.1 The Complete `.github-agenticana/` Tree

```
.github-agenticana/
│
├── README.md                              # Overview and getting started
├── github-agenticana.png                  # Logo
│
├── analysis/                              # Specifications and analysis
│   ├── specification-v1.md                # v1: Repository-as-runtime
│   ├── specification-v2.md                # v2: Multi-agent debates
│   └── specification-v3.md                # v3: Fork-safe containment (this document)
│
├── githubification/                       # Analysis of GitHub-as-AI-infrastructure pattern
│   ├── README.md
│   ├── architecture-analysis.md
│   ├── execution-model.md
│   ├── github-actions-cost-model.md
│   ├── identity-and-governance.md
│   ├── installation-model.md
│   ├── lifecycle-deep-dive.md
│   ├── memory-and-state.md
│   └── applicability-to-agenticana.md
│
├── config/                                # Agent and routing configuration
│   ├── agents.yaml                        # Label-to-agent mapping
│   ├── routing-rules.yaml                 # Auto-routing configuration
│   ├── debate-defaults.yaml               # Default debate parameters
│   └── cost-limits.yaml                   # Per-interaction cost caps
│
├── governance/                            # Identity, laws, and governance
│   ├── AGENTS.md                          # Master agent identity document
│   ├── FOUR-LAWS.md                       # Ethical foundation
│   ├── DEFCON.md                          # Readiness level definitions
│   ├── SECURITY-ASSESSMENT.md             # Self-audit of known risks
│   └── APPEND_SYSTEM.md                   # Behavioral constitution
│
├── scripts/                               # Fork-specific scripts (NOT modifying repo scripts/)
│   ├── debate_runner.py                   # Orchestrator entry point for debates
│   ├── agent_wrapper.sh                   # Wrapper that calls repo's agent_cli.py
│   └── state_manager.py                   # Session and state management
│
├── workflows/                             # Workflow source of truth
│   └── github-agenticana-agent.yml        # The primary workflow definition
│
├── templates/                             # Issue template sources
│   ├── chat.md                            # Chat with agents
│   ├── debate.md                          # Multi-agent debate
│   ├── architecture.md                    # Architecture review
│   └── security-audit.md                  # Security audit request
│
├── reconciler/                            # Automated change maker
│   ├── apply.sh                           # Main reconciler script
│   ├── README.md                          # How to use the reconciler
│   └── manifest.yaml                      # Declares what external files are generated
│
└── state/                                 # Runtime state (created by agents at runtime)
    ├── issues/                            # Issue → session mappings
    │   └── {N}.json                       # Per-issue mapping
    ├── sessions/                          # Agent execution transcripts
    │   └── {timestamp}.jsonl              # Per-session transcript
    ├── debates/                           # Debate transcripts and results
    │   ├── {issue}-{session}.json         # Full transcript (JSON)
    │   └── {issue}-latest.md              # Latest result (Markdown)
    └── attestations/                      # Proof-of-Work attestations
        └── ...
```

### 3.2 What Each Directory Owns

| Directory | Purpose | Created by | Modified? |
|-----------|---------|------------|-----------|
| `analysis/` | Specifications and design documents | Humans | Create-only (new versions, never edit existing) |
| `githubification/` | Analysis of the GitHub-as-AI-infrastructure pattern | Humans | Create-only |
| `config/` | Agent routing and cost configuration | Humans or reconciler | Create-only (version new configs) |
| `governance/` | Agent identity and ethical framework | Humans | Create-only |
| `scripts/` | Fork-specific scripts for agent execution | Humans or agents | Create-only |
| `workflows/` | Workflow definitions (source of truth) | Humans | Create-only |
| `templates/` | Issue template sources | Humans | Create-only |
| `reconciler/` | Automated change maker | Humans | Create-only |
| `state/` | Runtime state (sessions, debates, mappings) | Agents at runtime | Create-only (new files per interaction) |

---


---

## 4. The Reconciler

### 4.1 Why a Reconciler Is Needed

GitHub enforces specific file locations for certain features:

| Feature | Required Location | Cannot be changed |
|---------|------------------|-------------------|
| GitHub Actions workflows | `.github/workflows/*.yml` | GitHub only reads workflows from this path |
| Issue templates | `.github/ISSUE_TEMPLATE/*.md` | GitHub only reads templates from this path |
| PR templates | `.github/PULL_REQUEST_TEMPLATE.md` | GitHub only reads from this path |

Since Rule 1 prohibits creating or editing files outside `.github-agenticana/`, we need a bridge. The reconciler is that bridge.

### 4.2 Reconciler Design

The reconciler is a simple shell script (`.github-agenticana/reconciler/apply.sh`) that:

1. Reads source files from `.github-agenticana/workflows/` and `.github-agenticana/templates/`
2. Copies them to the required GitHub locations
3. Reports what it did

```bash
#!/usr/bin/env bash
# .github-agenticana/reconciler/apply.sh
#
# Automated change maker for github-agenticana.
# Copies workflow and template files from .github-agenticana/ to their
# required GitHub locations.
#
# Run after every upstream pull:
#   bash .github-agenticana/reconciler/apply.sh
#
# This is the ONLY mechanism that creates/modifies files outside .github-agenticana/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTICANA_DIR="$REPO_ROOT/.github-agenticana"

echo "🦅 github-agenticana reconciler"
echo "================================"

# --- Workflows ---
WORKFLOW_SRC="$AGENTICANA_DIR/workflows"
WORKFLOW_DST="$REPO_ROOT/.github/workflows"

if [ -d "$WORKFLOW_SRC" ]; then
  mkdir -p "$WORKFLOW_DST"
  for f in "$WORKFLOW_SRC"/*.yml "$WORKFLOW_SRC"/*.yaml; do
    [ -f "$f" ] || continue
    BASENAME=$(basename "$f")
    echo "  📋 Workflow: $BASENAME → .github/workflows/$BASENAME"
    cp "$f" "$WORKFLOW_DST/$BASENAME"
  done
fi

# --- Issue Templates ---
TEMPLATE_SRC="$AGENTICANA_DIR/templates"
TEMPLATE_DST="$REPO_ROOT/.github/ISSUE_TEMPLATE"

if [ -d "$TEMPLATE_SRC" ]; then
  mkdir -p "$TEMPLATE_DST"
  for f in "$TEMPLATE_SRC"/*.md; do
    [ -f "$f" ] || continue
    BASENAME=$(basename "$f")
    echo "  📋 Template: $BASENAME → .github/ISSUE_TEMPLATE/$BASENAME"
    cp "$f" "$TEMPLATE_DST/$BASENAME"
  done
fi

echo ""
echo "✅ Reconciliation complete."
echo ""
echo "Next steps:"
echo "  1. Review the generated files: git diff"
echo "  2. Commit: git add -A && git commit -m 'agenticana: reconcile after upstream pull'"
echo "  3. Push: git push"
```

### 4.3 Reconciler Manifest

The manifest (`.github-agenticana/reconciler/manifest.yaml`) declares every external file the reconciler generates, enabling audit and validation:

```yaml
# .github-agenticana/reconciler/manifest.yaml
#
# Declares all files that the reconciler generates outside .github-agenticana/.
# This is the complete list — no other external files should exist.

version: 1
generated_files:
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

reconciler_script: .github-agenticana/reconciler/apply.sh
```

### 4.4 When to Run the Reconciler

| Event | Action | Command |
|-------|--------|---------|
| **First installation** | Generate all external files | `bash .github-agenticana/reconciler/apply.sh` |
| **After upstream pull** | Reapply fork-specific changes | `bash .github-agenticana/reconciler/apply.sh` |
| **After editing workflow/template sources** | Regenerate external files | `bash .github-agenticana/reconciler/apply.sh` |
| **CI/CD pipeline** | Automated reconciliation | Can be added as a step in a CI workflow |

### 4.5 Post-Update Workflow

The recommended workflow for a fork master pulling upstream changes:

```bash
# 1. Pull upstream changes
git fetch upstream
git merge upstream/main

# 2. Resolve any conflicts (should be NONE in .github-agenticana/ if rules are followed)
# 3. Run the reconciler to reapply external file generation
bash .github-agenticana/reconciler/apply.sh

# 4. Review and commit
git diff
git add -A
git commit -m "agenticana: reconcile after upstream pull"
git push
```

If the upstream has modified files that the reconciler also generates (e.g., both upstream and the fork have `.github/workflows/github-agenticana-agent.yml`), the reconciler will overwrite the upstream version with the fork's version from `.github-agenticana/workflows/`. This is by design — the fork's AI infrastructure takes precedence.

> **⚠️ Warning:** Before running the reconciler after an upstream pull, review `git diff` to check whether the upstream has added workflows or templates with the same filenames declared in the reconciler manifest. If a collision is detected, review the upstream changes before allowing the reconciler to overwrite them. The reconciler logs every file it copies, making collisions visible in the output.

---


---

## 5. Execution Model (Evolved from v1 §2, v2 §2)

### 5.1 Primary Workflow: Source of Truth in `.github-agenticana/workflows/`

The workflow definition is stored in `.github-agenticana/workflows/github-agenticana-agent.yml`. The reconciler copies it to `.github/workflows/github-agenticana-agent.yml` where GitHub Actions can read it.

The workflow content includes all v2 features (debate mode detection, branching execution):

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

      # v2: Detect debate mode from labels and issue body
      - name: Detect execution mode
        id: detect_mode
        env:
          ISSUE_LABELS: ${{ toJSON(github.event.issue.labels.*.name) }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          COMMENT_BODY: ${{ github.event.comment.body }}
        run: |
          INPUT="${COMMENT_BODY:-$ISSUE_BODY}"
          if echo "$ISSUE_LABELS" | grep -q '"debate"'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          elif echo "$ISSUE_LABELS" | grep -q '"architecture"'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          elif echo "$INPUT" | head -1 | grep -qi '^@debate'; then
            echo "mode=debate" >> "$GITHUB_OUTPUT"
          else
            echo "mode=agent" >> "$GITHUB_OUTPUT"
          fi

      # v2: Run debate via orchestrator + Simulacrum
      # v3: debate_runner.py sourced from .github-agenticana/scripts/
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
          python .github-agenticana/scripts/debate_runner.py \
            --issue-number "$ISSUE_NUMBER" \
            --input "${COMMENT_BODY:-$ISSUE_BODY}" \
            --labels "$ISSUE_LABELS"

      # v1: Run single agent (calls existing repo scripts/ — no modification needed)
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

      # v3: Commit state — only .github-agenticana/state/ changes
      - name: Commit state
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .github-agenticana/state/
          if ! git diff --cached --quiet; then
            git commit -m "agenticana: work on issue #${{ github.event.issue.number }}"
            for i in $(seq 1 10); do
              git push origin HEAD:${{ github.event.repository.default_branch }} && break
              git pull --rebase -X theirs origin ${{ github.event.repository.default_branch }}
              sleep $((i * 2))
            done
          fi

      # v2: Post debate result as structured comment
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

### 5.2 Key v3 Workflow Differences

| Aspect | v1/v2 | v3 |
|--------|-------|----|
| **Workflow file location (source)** | `.github/workflows/` (direct) | `.github-agenticana/workflows/` (source) → reconciler → `.github/workflows/` |
| **Debate runner path** | `scripts/debate_runner.py` | `.github-agenticana/scripts/debate_runner.py` |
| **Agent CLI path** | `scripts/agent_cli.py` (modified) | `scripts/agent_cli.py` (unchanged — called as-is) |
| **git add scope** | `git add -A` (all changes) | `git add .github-agenticana/state/` (contained) |
| **State commit scope** | Entire repo state | Only `.github-agenticana/state/` |

### 5.3 Workflow Design Decisions (v3 Additions)

All v1 and v2 decisions remain. New v3 decisions:

| Decision | Rationale |
|----------|-----------|
| **Workflow source in `.github-agenticana/workflows/`** | Fork master edits here; reconciler copies to `.github/workflows/` |
| **`git add .github-agenticana/state/` instead of `git add -A`** | Prevents agent from committing changes outside the contained directory |
| **Debate runner at `.github-agenticana/scripts/debate_runner.py`** | New script, never existed in upstream — no conflict possible |
| **Agent CLI called as-is** | `scripts/agent_cli.py` is not modified — fork calls the upstream version directly |
| **Reconciler as post-update step** | Bridges the gap between containment and GitHub's required file locations |

---


---

## 6. Multi-Agent Routing via Issue Labels (Unchanged from v1 §3, v2 §7)

### 6.1 Label-to-Agent Mapping

The full label-to-agent mapping from v1 §3.1 and v2 §7.1 is unchanged. The mapping is documented here and also stored in `.github-agenticana/config/agents.yaml`:

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
| `debate` | orchestrator (debate mode) | COMPLEX | Triggers Simulacrum debate with auto-selected agents |

### 6.2 Auto-Routing and Debate Detection (Unchanged from v2)

The auto-routing logic and debate detection from v2 §7.2 is unchanged. The only difference is that the debate runner script path is `.github-agenticana/scripts/debate_runner.py`.

---


### 6.2 Auto-Routing Logic

When the `agenticana` label is applied without a specialist label, the agent CLI performs automatic routing:

```
Issue body + labels
    │
    ├─ Has 'debate' or 'architecture' label, or body starts with @debate?
    │   ├─ YES → Debate mode → .github-agenticana/scripts/debate_runner.py
    │   └─ NO  → Agent mode → scripts/agent_cli.py @auto (v1 behavior)
    │
    ├─ (Debate mode)
    │   ├─ Parse debate-config from issue body
    │   ├─ Select agents (cascade)
    │   └─ Run Simulacrum
    │
    └─ (Agent mode)
        ├─ Query Model Router (complexity-scorer.js)
        │     ├─ Extract keywords → match against agent routing_hints.trigger_keywords
        │     ├─ Score complexity (1-10)
        │     ├─ Select model tier (flash/pro/pro-extended)
        │     └─ Return { agent, model, strategy, skills }
        └─ Route to specialist agent
```

This leverages Agenticana's existing `router/router.js` and per-agent `routing_hints` in YAML specs.

---

## 7. Multi-Agent Debates: The Simulacrum Protocol

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


---

## 10. Debate State Persistence

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


---

## 8. Memory and State Persistence (Evolved from v1 §4, v2 §6)

### 8.1 Git as the Memory Layer (Unchanged in Concept)

The memory model from v1 §4 is unchanged: every agent interaction produces state committed to git. The difference in v3 is that the `git add` scope is restricted:

```
# v1/v2: git add -A (entire repo)
# v3:    git add .github-agenticana/state/ (contained)
```

### 8.2 State Directory Structure (Consolidated from v1 §4.1, v2 §6.1)

```
.github-agenticana/state/
├── issues/                    # Issue → session mappings
│   ├── 1.json                 # { issueNumber, agent, sessionPath, debates[], updatedAt }
│   ├── 2.json
│   └── ...
├── sessions/                  # Agent execution transcripts
│   ├── 1709510400.jsonl       # JSONL: each line is a conversation event
│   └── ...
├── debates/                   # Debate transcripts and results (v2)
│   ├── 42-a1b2c3d4.json      # Full transcript (JSON, machine-readable)
│   ├── 42-latest.md           # Latest debate result (Markdown, posted to issue)
│   └── ...
└── attestations/              # Proof-of-Work attestations
    └── ...
```

### 8.3 Session Continuity (Unchanged from v1 §4.2)

The issue-to-session mapping provides conversation continuity across multiple comments, exactly as described in v1 §4.2.

### 8.4 ReasoningBank Integration (Unchanged from v1 §4.3, v2 §6.4)

The ReasoningBank integration from v1 §4.3 and debate-specific integration from v2 §6.4 are unchanged. The existing `memory/reasoning-bank/decisions.json` in the repository root is read by the agent but not modified by the v3-contained workflow (the `git add` scope prevents it). If the agent needs to write to the ReasoningBank, it writes to `.github-agenticana/state/` and a separate process can merge it.

> **Note:** This is an area where the containment model introduces a trade-off. The ReasoningBank in `memory/reasoning-bank/` lives outside `.github-agenticana/`. The v3 approach is:
> 1. Read from `memory/reasoning-bank/` (read is always safe)
> 2. Write new decisions to `.github-agenticana/state/reasoning-bank/` (contained)
> 3. Merging contained decisions back into the main ReasoningBank is **not implemented by the reconciler** — it is left to the fork maintainer as a manual step or a future enhancement. The contained decisions remain readable and auditable in `.github-agenticana/state/reasoning-bank/` regardless.

### 8.5 Memory Properties (Unchanged from v1 §4.4)

All memory properties inherited from git (durability, auditability, diffability, recoverability, branchability, attribution, distribution) are unchanged.

### 8.6 Push Conflict Resolution (Unchanged from v1 §4.5)

The push retry with backoff strategy from v1 §4.5 is unchanged. The `-X theirs` strategy remains safe because state files are per-issue (no overlap).

---


### 8.3 Session Continuity

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

### 8.5 Memory Properties Inherited from Git

| Property | Meaning for Agent Memory |
|----------|-------------------------|
| **Durability** | Persists as long as the repository exists |
| **Auditability** | `git log` shows every memory change with timestamps |
| **Diffability** | `git diff` reveals exactly what changed between sessions |
| **Recoverability** | `git revert` can restore any prior state |
| **Branchability** | Fork a conversation by branching the repo |
| **Attribution** | Every memory write has an author (the agent's commit identity) |
| **Distribution** | Cloning the repo clones the entire memory |

### 8.6 Push Conflict Resolution

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

## 9. Identity and Governance (Evolved from v1 §5)

### 9.1 Governance Files Location

All governance files from v1 §5.1 are stored inside `.github-agenticana/governance/`:

```
.github-agenticana/governance/
├── AGENTS.md                 # Master agent identity document
├── FOUR-LAWS.md              # Ethical foundation (Asimov-adapted)
├── DEFCON.md                 # Readiness level definitions (1-5)
├── SECURITY-ASSESSMENT.md    # Self-audit of known risks
└── APPEND_SYSTEM.md          # Behavioral constitution (appended to all LLM prompts)
```

This is already consistent with v1's design. No change needed — governance was always inside `.github-agenticana/`.

### 9.2 The Four Laws, DEFCON Levels, Security Assessment

All governance content from v1 §5.2 (Four Laws), §5.3 (DEFCON Levels), and §5.4 (Security Assessment) is unchanged.

### 9.3 v3-Specific Security Considerations

The containment model introduces new security properties and one new finding:

| ID | Severity | Finding | Mitigation |
|----|----------|---------|------------|
| SEC-001–SEC-008 | Various | All v1 findings | All v1 mitigations (unchanged) |
| SEC-009–SEC-012 | Various | All v2 findings | All v2 mitigations (unchanged) |
| SEC-013 | 🟢 Low | Reconciler could be tricked into overwriting critical files | Manifest declares explicit target paths; reconciler only copies from declared sources |
| SEC-014 | 🟡 Medium | `git add .github-agenticana/state/` could still be large | Add `.github-agenticana/state/.gitkeep` for empty directories; size limits in state manager |
| SEC-015 | 🟢 Low | Upstream could add a `.github-agenticana/` directory, conflicting with the fork | Unlikely — directory name is fork-specific. If it happens, a migration is required: rename the directory (e.g., to `.github-agenticana-{fork-name}/`) and update all path references in workflows, scripts, and documentation. To mitigate proactively, fork maintainers may choose a namespaced directory from the start. |

### 9.4 DEFCON Level Interaction with Debates (Unchanged from v2 §12.2)

Debate behavior adapts to the active DEFCON level exactly as defined in v2 §12.2.

---


### 9.2 The Four Laws of AI

The ethical foundation, inherited from Minimum Intelligence and adapted for a multi-agent system:

| Law | Principle | Agenticana Application |
|-----|-----------|----------------------|
| **Zeroth** | Protect humanity as a whole | No monopolistic patterns; open source remains open; interoperability preserved |
| **First** | Do no harm to humans or communities | Never endanger safety, privacy, or civil rights; refuse malicious code generation |
| **Second** | Obey human operators (unless conflicts with First) | Faithfully execute instructions; be transparent about limitations |
| **Third** | Preserve own integrity (unless conflicts with First or Second) | Maintain security and audit trails; resist corruption |

### 9.3 DEFCON Readiness Levels

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

### 9.4 Security Self-Assessment

Radical transparency about known risks:

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
| SEC-009 | 🟡 Medium | Debate config in issue body could be manipulated by unauthorized users | Only collaborators can trigger debates (authorization step) |
| SEC-010 | 🟡 Medium | High agent count × high round count = expensive debates | Hard caps: max 7 agents, max 5 rounds, max 49 LLM calls per debate |
| SEC-011 | 🟢 Low | Debate transcripts may contain sensitive reasoning | Transcripts committed to repo (same access control as code); no external exposure |
| SEC-012 | 🟡 Medium | ReasoningBank fast-path could serve stale consensus | Include timestamp and staleness warning if prior debate is older than 30 days |
| SEC-013 | 🟢 Low | Reconciler could be tricked into overwriting critical files | Manifest declares explicit target paths; reconciler only copies from declared sources |
| SEC-014 | 🟡 Medium | `git add .github-agenticana/state/` could still be large | Add `.github-agenticana/state/.gitkeep` for empty directories; size limits in state manager |
| SEC-015 | 🟢 Low | Upstream could add a `.github-agenticana/` directory, conflicting with the fork | Unlikely — directory name is fork-specific. Migration available if needed. |

### 9.5 DEFCON Level Interaction with Debates

Debate behavior adapts to the active DEFCON level:

| DEFCON Level | Debate Behavior |
|-------------|----------------|
| **DEFCON 1** (Maximum) | Debates suspended. No LLM calls. |
| **DEFCON 2** (High) | Debates run in `logic` mode only (no LLM calls). Results are advisory. |
| **DEFCON 3** (Increased) | Debates run in `real` mode but consensus is not auto-applied. Human must approve. |
| **DEFCON 4** (Above Normal) | Normal debate operation with elevated logging. |
| **DEFCON 5** (Normal) | Normal debate operation. |

---

## 12. Cost Model

### 12.1 The Pay-Per-Think Economics

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

### 12.2 Per-Interaction Cost Estimates

| Scenario | Duration | Actions Cost | LLM Cost (est.) | Total |
|----------|----------|-------------|-----------------|-------|
| Simple question (flash model) | ~1 min | $0.008 | $0.01-0.05 | ~$0.02-0.06 |
| Code review (pro model) | ~2-3 min | $0.016-0.024 | $0.05-0.20 | ~$0.07-0.22 |
| Code generation (pro model) | ~3-5 min | $0.024-0.040 | $0.10-0.50 | ~$0.12-0.54 |
| Architecture debate (simulacrum) | ~5-10 min | $0.040-0.080 | $0.20-1.00 | ~$0.24-1.08 |

### 12.3 Debate Cost Estimates

| Debate Config | LLM Calls | Duration | Actions Cost | LLM Cost (est.) | Total |
|---------------|-----------|----------|-------------|-----------------|-------|
| 3 agents, 1 round (minimal) | 9 | ~2-3 min | $0.016-0.024 | $0.05-0.15 | ~$0.07-0.17 |
| 5 agents, 2 rounds (default) | 20 | ~3-5 min | $0.024-0.040 | $0.10-0.40 | ~$0.12-0.44 |
| 7 agents, 3 rounds (deep) | 35 | ~5-8 min | $0.040-0.064 | $0.20-0.70 | ~$0.24-0.76 |
| 7 agents, 5 rounds (max) | 49 | ~8-12 min | $0.064-0.096 | $0.30-1.00 | ~$0.36-1.10 |

**Formula:** `LLM calls = N_agents × (2 + N_rounds)` where the 2 accounts for opening + proposal/voting phases.

### 12.4 Cost Optimizations

| Optimization | Mechanism | Estimated Savings |
|-------------|-----------|------------------|
| **Model Router** | Route simple tasks to flash model instead of pro | ~40% on simple tasks |
| **ReasoningBank fast-path** | Skip full agent execution when similarity > 0.85 | ~60% on repeated patterns |
| **Dependency caching** | Cache pip and npm installs across runs | ~30-40 seconds per run |
| **Label-gating** | Only trigger on `agenticana`-labeled issues | 100% savings on non-agent issues |
| **Timeout caps** | Prevent runaway agents from burning minutes | Bounded worst-case cost |
| **Logic mode fallback** | Use persona heuristics when no API key or for cost-sensitive debates | ~95% (no LLM calls) |
| **Flash model for all debate calls** | Use `gemini-2.0-flash` with 200-token cap per agent response | ~70% vs pro model |
| **Agent count cap (7 max)** | Prevent runaway agent spawning | Bounded worst-case |
| **Round cap (5 max)** | Prevent excessive debate depth | Bounded worst-case |

### 12.5 Monthly Projections

| Usage Pattern | Single-Agent/Day | Debates/Day | Monthly Actions Cost |
|--------------|-----------------|-------------|---------------------|
| Light (1 developer) | 5 | 0-1 | Free tier (2,000 min) |
| Moderate (small team) | 15 | 2-3 | Free tier |
| Heavy (active team) | 30 | 5-10 | $0-20 overage |
| Intense (full reliance) | 50+ | 10-20 | $20-60 overage |

---

## 11. Issue Templates (Evolved from v1 §7, v2 §9)

### 11.1 Template Sources in `.github-agenticana/templates/`

All issue templates are stored as source files in `.github-agenticana/templates/`. The reconciler copies them to `.github/ISSUE_TEMPLATE/` with the `agenticana-` prefix.

**Chat Template** (`.github-agenticana/templates/chat.md`):

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

**Debate Template** (`.github-agenticana/templates/debate.md`):

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
```

**Architecture Review Template** (`.github-agenticana/templates/architecture.md`):

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

**Security Audit Template** (`.github-agenticana/templates/security-audit.md`):

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

### 11.2 Reconciler Output

After running `bash .github-agenticana/reconciler/apply.sh`, the templates appear at:

```
.github/ISSUE_TEMPLATE/
├── agenticana-chat.md
├── agenticana-debate.md
├── agenticana-architecture.md
└── agenticana-security-audit.md
```

The `agenticana-` prefix prevents collision with existing upstream issue templates.

---


---

## 12. Hybrid Execution Model (Evolved from v1 §8, v2 §10)

### 12.1 Architecture: Local + Cloud (Unchanged in Concept)

The hybrid model from v1 §8 and v2 §10 is unchanged. VS Code + MCP for local, GitHub Issues + Actions for cloud. Both interfaces share state.

### 12.2 Shared State Across Interfaces (v3 Adjustment)

| State Component | Local (VS Code/MCP) | Cloud (Actions) |
|----------------|---------------------|-----------------|
| ReasoningBank decisions | Read/write via MCP tools (repo root) | Read from repo root; write to `.github-agenticana/state/reasoning-bank/` |
| Agent YAML specs | Read via MCP tools | Read via filesystem |
| Session transcripts | Not applicable (ephemeral) | Read/write via `.github-agenticana/state/sessions/` |
| Issue mappings | Not applicable | Read/write via `.github-agenticana/state/issues/` |
| Debate transcripts | Not applicable | Read/write via `.github-agenticana/state/debates/` |

The v3 adjustment: cloud writes go to `.github-agenticana/state/` exclusively. The reconciler can optionally merge state back to repo-root locations if needed.

### 12.3 Local Debate via CLI (Unchanged from v2 §10.2)

Local CLI debates are unchanged. They write to `.Agentica/logs/simulacrum/` (not committed) and do not interact with the containment model.

---


### 12.2b Shared State Across Interfaces (Full)

| State Component | Local (VS Code/MCP) | Cloud (Actions) |
|----------------|---------------------|-----------------|
| ReasoningBank decisions | Read/write via MCP tools (repo root) | Read from repo root; write to `.github-agenticana/state/reasoning-bank/` |
| ReasoningBank patterns | Read via MCP tools | Read/write via CLI scripts |
| Agent YAML specs | Read via MCP tools | Read via filesystem |
| Session transcripts | Not applicable (ephemeral) | Read/write via `.github-agenticana/state/sessions/` |
| Issue mappings | Not applicable | Read/write via `.github-agenticana/state/issues/` |
| Debate transcripts | Not applicable | Read/write via `.github-agenticana/state/debates/` |
| Skill definitions | Read via MCP tools | Read via filesystem |

### 12.3b When to Use Each Interface

| Use Case | Interface | Why |
|----------|-----------|-----|
| Real-time coding assistance | VS Code (local) | Immediate feedback, IDE integration |
| Quick question to one agent | VS Code (local) | Immediate response |
| Asynchronous code review | GitHub Issue (cloud) | Collaborators see results without IDE |
| **Multi-agent debate** | **GitHub Issue (cloud)** | Debates take 3-12 minutes; async execution is natural |
| **Quick local debate** | **VS Code CLI** | `agentica simulacrum "topic" --agents ...` for local-only debates |
| Architecture review | GitHub Issue (cloud) | Team sees debate transcript as issue comment |
| Overnight batch processing | GitHub Issue (cloud) | Post issue, review results tomorrow |
| Shared knowledge building | Both | ReasoningBank updated from both interfaces |
| Audit trail required | GitHub Issue (cloud) | Every interaction is a visible issue comment |

### 12.4b Local Debate via CLI

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

## 13. What Cannot Be Fully Contained (and the Reconciler Solution)

### 13.1 Components That Require External Files

The following components cannot live inside `.github-agenticana/` because GitHub enforces specific file paths:

| Component | Required Path | Why |
|-----------|---------------|-----|
| **Actions workflow** | `.github/workflows/*.yml` | GitHub only triggers workflows from this directory |
| **Issue templates** | `.github/ISSUE_TEMPLATE/*.md` | GitHub only renders templates from this directory |
| **Copilot instructions** | `.github/copilot-instructions.md` | GitHub Copilot reads from this path |

### 13.2 Components That Are Already Contained

| Component | Path | Status |
|-----------|------|--------|
| Agent state | `.github-agenticana/state/` | ✅ Already contained |
| Governance | `.github-agenticana/governance/` | ✅ Already contained |
| Analysis | `.github-agenticana/analysis/` | ✅ Already contained |
| Debate transcripts | `.github-agenticana/state/debates/` | ✅ Already contained |

### 13.3 Components That Live in Repo Root (Read-Only Access)

These are upstream files that the agent **reads** but does not **write** to:

| Component | Path | v3 Approach |
|-----------|------|-------------|
| Agent YAML specs | `agents/*.yaml` | Read at runtime; not modified |
| Agent CLI | `scripts/agent_cli.py` | Called at runtime; not modified |
| Simulacrum engines | `scripts/simulacrum.py`, `scripts/real_simulacrum.py` | Called by debate runner; not modified |
| Model Router | `router/router.js` | Called at runtime; not modified |
| MCP Server | `mcp/` | Used by VS Code integration; not modified |
| ReasoningBank | `memory/reasoning-bank/` | Read at runtime; new writes go to `.github-agenticana/state/reasoning-bank/` |
| Skills | `skills/` | Read at runtime; not modified |
| Requirements | `requirements.txt` | Read by `pip install`; not modified |

### 13.4 The Reconciler Fills the Gap

For components in §13.1 (require external files), the reconciler generates the external files from sources inside `.github-agenticana/`. This is the **only** mechanism that creates files outside the contained directory.

The reconciler is **idempotent** — running it multiple times produces the same output. It is **safe** — it only copies files declared in the manifest. It is **auditable** — the manifest lists every external file.

---


---

## 14. Implementation Phases (Evolved from v1 §9, v2 §11)

### Phase 1: Containment Setup

**Goal:** Establish the `.github-agenticana/` directory structure and reconciler.

**Deliverables:**
- [ ] `.github-agenticana/config/agents.yaml` — Label-to-agent mapping
- [ ] `.github-agenticana/config/routing-rules.yaml` — Auto-routing configuration
- [ ] `.github-agenticana/config/debate-defaults.yaml` — Default debate parameters
- [ ] `.github-agenticana/reconciler/apply.sh` — Reconciler script
- [ ] `.github-agenticana/reconciler/manifest.yaml` — External file manifest
- [ ] `.github-agenticana/reconciler/README.md` — Usage instructions

**Verification:** Run `bash .github-agenticana/reconciler/apply.sh`. External files are generated. Run again — output is identical (idempotent).

### Phase 2: Workflow and Templates

**Goal:** Define workflow and issue templates inside `.github-agenticana/`, reconcile to GitHub-required locations.

**Deliverables:**
- [ ] `.github-agenticana/workflows/github-agenticana-agent.yml` — Workflow source of truth
- [ ] `.github-agenticana/templates/chat.md` — Chat template
- [ ] `.github-agenticana/templates/debate.md` — Debate template
- [ ] `.github-agenticana/templates/architecture.md` — Architecture template
- [ ] `.github-agenticana/templates/security-audit.md` — Security audit template
- [ ] Reconciler copies all to `.github/workflows/` and `.github/ISSUE_TEMPLATE/`

**Verification:** Run reconciler. Workflow appears in `.github/workflows/`. Templates appear in `.github/ISSUE_TEMPLATE/`.

### Phase 3: Fork-Specific Scripts

**Goal:** Implement debate runner and state manager inside `.github-agenticana/scripts/`.

**Deliverables:**
- [ ] `.github-agenticana/scripts/debate_runner.py` — Debate orchestrator (calls existing `scripts/simulacrum.py`)
- [ ] `.github-agenticana/scripts/state_manager.py` — Session and state management
- [ ] `.github-agenticana/scripts/agent_wrapper.sh` — Wrapper for calling `scripts/agent_cli.py` with containment

**Verification:** Debate runner correctly calls the existing Simulacrum engine. State is written to `.github-agenticana/state/`.

### Phase 4: Governance (From v1 Phase 4)

**Goal:** Establish governance framework inside `.github-agenticana/governance/`.

**Deliverables:**
- [ ] `.github-agenticana/governance/AGENTS.md`
- [ ] `.github-agenticana/governance/FOUR-LAWS.md`
- [ ] `.github-agenticana/governance/DEFCON.md`
- [ ] `.github-agenticana/governance/SECURITY-ASSESSMENT.md`
- [ ] `.github-agenticana/governance/APPEND_SYSTEM.md`

**Verification:** Agent responses reflect governance constraints.

### Phase 5: Integration and Optimization (From v1 Phase 5)

**Goal:** End-to-end integration with cost optimization.

**Deliverables:**
- [ ] End-to-end test: Open issue → agent responds → state committed to `.github-agenticana/state/`
- [ ] Dependency caching in workflow
- [ ] ReasoningBank read from repo root, write to `.github-agenticana/state/reasoning-bank/`
- [ ] Reconciler integrated into post-pull workflow

**Verification:** Full loop works. Upstream pull + reconciler produces no conflicts.

### Phase 6: Multi-Agent Debates (From v2 Phase 6)

**Goal:** Debates as first-class primitive with contained state.

**Deliverables:**
- [ ] Debate mode detection in workflow
- [ ] Debate runner integration with Simulacrum
- [ ] Debate state in `.github-agenticana/state/debates/`
- [ ] ReasoningBank fast-path for repeated topics

**Verification:** All v2 Phase 6 verifications, with state contained in `.github-agenticana/`.

### Phase 7: Future Enhancements (From v2 Phase 7)

As defined in v2 §11 Phase 7. Debate chains, branches, human-in-the-loop, analytics.

---


### Phase 8: Master Fork Cleanup (New — v4)

**Goal:** Remove upstream development artifacts that interfere with our execution-focused UX.

**Deliverables:**
- [x] Remove `.github/workflows-disabled/` (ci.yml, release.yml)
- [x] Remove `.github/ISSUE_TEMPLATE-disabled/` (bug-report.md, new-agent.md, new-phase.md)
- [x] Remove `.github/PR_TEMPLATE-disabled/` (PULL_REQUEST_TEMPLATE.md)
- [x] Document decision in this specification (§1)

**Verification:** `.github/` directory contains only `copilot-instructions.md` and reconciler-generated files. No disabled upstream artifacts remain.

---

## 17. What Makes v4 the Final Specification

| Dimension | v1 | v2 | v3 | v4 (Final) |
|-----------|----|----|-----|------------|
| **Foundation** | ✅ Established | Inherited | Inherited | ✅ Consolidated |
| **Multi-agent debates** | Implicit | ✅ First-class | Inherited | ✅ Consolidated |
| **Fork-safe containment** | Not addressed | Not addressed | ✅ Established | ✅ Consolidated |
| **Upstream cleanup** | Not addressed | Not addressed | Not addressed | ✅ Established |
| **Self-contained document** | Yes | References v1 | References v1, v2 | ✅ Fully self-contained |

---

## 16. Sovereignty Guarantees (Evolved from v1 §11)

All sovereignty guarantees from v1 §11 are preserved. The containment model adds:

| Concern | v1/v2 | v3 Addition |
|---------|-------|-------------|
| **Data sovereignty** | Code never leaves repo/runner | Same — containment doesn't change data flow |
| **Auditability** | Every action is a git commit | State commits scoped to `.github-agenticana/state/` — cleaner audit trail |
| **Vendor lock-in** | LLM provider configurable | Same |
| **Access control** | Collaborator permissions | Same |
| **Fork independence** | Not addressed | Fork can pull upstream without conflict; AI infrastructure is self-contained |
| **Reproducibility** | Deterministic pipeline | Reconciler is idempotent — same input, same output |
| **Identity governance** | Diffable, reviewable | Same — governance files already in `.github-agenticana/` |
| **Cost transparency** | Pay-per-think | Same |

---


| **Fork independence** | Not addressed | Not addressed | Fork can pull upstream without conflict | Same + upstream artifacts removed |
| **Clean UX** | N/A | N/A | N/A | No upstream templates/workflows interfering with agent UX |

---

## 19. Summary

This specification is the definitive, consolidated document for `github-agenticana` as a repository-native AI system. It combines:

1. **v1's foundation** — GitHub primitives as AI infrastructure (Issues=input, Actions=runtime, git=memory, Secrets=credentials, Markdown=identity)
2. **v2's debates** — Multi-agent Simulacrum protocol as a first-class primitive with structured output
3. **v3's containment** — All intelligence inside `.github-agenticana/` with automated reconciler
4. **v4's cleanup** — Removal of upstream development workflows and templates that interfere with execution UX

The result: **a fork-safe, conflict-free, self-contained, execution-focused AI infrastructure that can be maintained independently of the upstream repository — with 20 specialist agents triggerable via issues, multi-agent debates as a named primitive, and a clean UX free from upstream development artifacts.**
