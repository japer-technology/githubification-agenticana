# Specification v3: Fork-Safe Containment — All Intelligence Inside `.github-agenticana`

> **Version:** 3.0.0 | **Date:** 2026-03-03 | **Evolves:** [specification-v1](specification-v1.md), [specification-v2](specification-v2.md)
> Confining the entire AI infrastructure to the `.github-agenticana` directory — enabling fork maintainers to pull upstream changes without conflict.

---

## Executive Summary

Specification v1 established the repository-as-runtime pattern: GitHub Issues as input, Actions as compute, git as memory, Markdown as identity. Specification v2 promoted multi-agent debates to a first-class primitive via the Simulacrum protocol. Both specifications assumed the freedom to create and modify files anywhere in the repository — workflows in `.github/workflows/`, scripts in `scripts/`, templates in `.github/ISSUE_TEMPLATE/`.

**This specification introduces a hard constraint: no files may be created or edited outside the `.github-agenticana/` directory.** Files inside `.github-agenticana/` may be **created** but not **modified**. This is the **fork-safe containment model**.

The motivation is practical: when a fork of this repository pulls updates from the upstream master, any files that the fork has modified outside `.github-agenticana/` will produce merge conflicts. By confining all fork-specific intelligence to a single directory that the upstream does not own, the fork master can `git pull upstream main` without concern.

The core evolution:

> **v1:** The repository is the runtime. Files are created and edited wherever needed.
> **v2:** Multi-agent debates are a first-class primitive. Workflow files, scripts, and templates are modified to support them.
> **v3:** All intelligence is contained inside `.github-agenticana/`. No files outside this directory are touched. An automated reconciler handles the bridge.

### What Changed from v2

| Area | v2 | v3 |
|------|----|----|
| **File scope** | Creates/edits files anywhere in the repo | All files confined to `.github-agenticana/` only |
| **Modification model** | Files freely created and modified | Files inside `.github-agenticana/` may be created, never modified |
| **Workflow definition** | `.github/workflows/github-agenticana-agent.yml` created directly | Workflow template stored in `.github-agenticana/workflows/`; reconciler generates the external file |
| **Issue templates** | `.github/ISSUE_TEMPLATE/*.md` created directly | Template sources in `.github-agenticana/templates/`; reconciler generates external files |
| **Script changes** | `scripts/debate_runner.py` created, `scripts/agent_cli.py` modified | All new scripts in `.github-agenticana/scripts/`; existing scripts untouched |
| **Fork safety** | Not addressed | Primary design goal — upstream pull produces zero conflicts in `.github-agenticana/` |
| **Post-update process** | Not needed | Automated reconciler reapplies external changes after upstream pull |
| **State persistence** | `state/` inside `.github-agenticana/` | Unchanged — already contained |
| **Governance** | `governance/` inside `.github-agenticana/` | Unchanged — already contained |

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

## 7. Multi-Agent Debates: The Simulacrum Protocol (Unchanged from v2 §3)

The entire Simulacrum protocol from v2 §3 is unchanged:
- Debate triggers (§3.2): `debate` label, `architecture` label, `@debate` command
- Agent selection cascade (§3.3): Explicit → labels → topic → defaults
- Debate configuration via issue body (§3.4): `<!-- debate-config -->` HTML comments
- Five-phase protocol (§3.5): Opening → Debate → Proposals → Voting → Consensus
- Single-job execution (§3.6): All agents run sequentially in-process
- LLM usage model (§3.7): N × (2 + R) calls per debate

The debate runner script (v2 §4) is implemented at `.github-agenticana/scripts/debate_runner.py` instead of `scripts/debate_runner.py`.

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

## 10. Cost Model (Unchanged from v1 §6, v2 §8)

The cost model from v1 §6 and debate-specific cost model from v2 §8 are unchanged. The containment model does not affect cost — the same LLM calls, the same Actions minutes, the same optimizations.

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

## 15. What Makes v3 Different

| Dimension | v1 | v2 | v3 |
|-----------|----|----|-----|
| **File scope** | Anywhere in repo | Anywhere in repo | `.github-agenticana/` only |
| **Modification model** | Free edit | Free edit | Create-only (never modify) |
| **Fork safety** | Not addressed | Not addressed | Primary design goal |
| **External files** | Created directly | Created directly | Generated by reconciler |
| **Upstream pull** | May conflict | May conflict | Conflict-free |
| **Post-update process** | None | None | `bash .github-agenticana/reconciler/apply.sh` |
| **State commit scope** | `git add -A` | `git add -A` | `git add .github-agenticana/state/` |
| **Script location** | `scripts/` (modified) | `scripts/` (new + modified) | `.github-agenticana/scripts/` (new only) |
| **Agent CLI** | Modified | Modified | Called as-is (no modification) |
| **Debate runner** | N/A | `scripts/debate_runner.py` | `.github-agenticana/scripts/debate_runner.py` |
| **ReasoningBank writes** | `memory/reasoning-bank/` | `memory/reasoning-bank/` | `.github-agenticana/state/reasoning-bank/` |

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

## 17. Summary

This specification evolves `github-agenticana` from a system that freely modifies files across the repository into one where **all intelligence is contained inside `.github-agenticana/`** — enabling fork maintainers to pull upstream changes without merge conflicts.

The key design decisions:

> **1. No files outside `.github-agenticana/` may be created or edited.**
> This ensures upstream pulls are conflict-free for the fork's AI infrastructure.

> **2. Files inside `.github-agenticana/` may be created but not modified.**
> This ensures a clean append-only model where history is preserved and conflicts are impossible.

> **3. An automated reconciler bridges the gap.**
> For GitHub features that require files in specific locations (workflows, templates), the reconciler generates external files from sources inside `.github-agenticana/`.

For fork maintainers, this means:

1. **Pull upstream freely** — no conflicts in `.github-agenticana/`
2. **Run the reconciler** — `bash .github-agenticana/reconciler/apply.sh` after every pull
3. **All AI configuration is in one place** — `.github-agenticana/` is the single source of truth
4. **State is contained** — agent writes go to `.github-agenticana/state/` only
5. **Existing scripts are untouched** — the workflow calls `scripts/agent_cli.py` as-is

For the system, this means:

1. A **reconciler** that generates external files from contained sources
2. A **scoped `git add`** that only commits state inside `.github-agenticana/`
3. **New scripts** in `.github-agenticana/scripts/` that wrap existing repo scripts
4. **Workflow source of truth** in `.github-agenticana/workflows/`
5. **Template sources** in `.github-agenticana/templates/`

The result: **a fork-safe, conflict-free, self-contained AI infrastructure that can be maintained independently of the upstream repository — with an automated reconciler to bridge the gap between containment and GitHub's required file locations.**
