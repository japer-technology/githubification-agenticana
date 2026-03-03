# Execution Model

> How GitHub Actions minutes serve as the compute layer — the workflow YAML, trigger events, authorization, concurrency, and the full execution pipeline.

---

## GitHub Actions as the Mind's Body

The central execution insight of GitHub Minimum Intelligence is that **GitHub Actions is not just CI/CD — it is a general-purpose compute platform** that can serve as the "body" for an AI agent. The workflow runner provides:

- A fresh Linux VM (`ubuntu-latest`) for every invocation
- Full filesystem access to a checked-out repository
- Network access to LLM API endpoints
- Authenticated access to the GitHub API via `GITHUB_TOKEN`
- Environment variables for secrets management

This transforms a social event (an issue comment) into a deterministic build-and-run pipeline. The prompt is treated like source input to a CI job.

---

## The Workflow: `github-minimum-intelligence-agent.yml`

### Trigger Events

```yaml
on:
  issues:
    types: [opened]
  issue_comment:
    types: [created]
```

The workflow fires on two events:
1. **New issue opened** — triggers a fresh conversation
2. **Comment on existing issue** — continues an existing conversation

This means every GitHub Issue is a bidirectional communication channel: the user writes, the agent responds, the user responds back, and so on.

### Permissions

```yaml
permissions:
  contents: write    # Read/write repo files, commit and push
  issues: write      # Post comments, add reactions
  actions: write     # Cancel or re-run workflows
```

These permissions define the constitutional limits of the agent. It can read and modify repository contents, interact with issues, and manage workflow state — but nothing beyond what these scopes allow.

### Concurrency Control

```yaml
concurrency:
  group: github-minimum-intelligence-${{ github.repository }}-issue-${{ github.event.issue.number }}
  cancel-in-progress: false
```

Each issue gets its own concurrency group. This ensures:
- **Serialization per issue** — only one agent run per issue at a time
- **No cancellation** — if a second comment arrives while the agent is processing, it queues rather than cancelling the running job
- **Cross-issue parallelism** — different issues can be processed simultaneously

### Bot Comment Filtering

```yaml
if: >-
  (github.event_name == 'issues')
  || (github.event_name == 'issue_comment' && !endsWith(github.event.comment.user.login, '[bot]'))
```

This prevents infinite loops: the agent's own comments (posted by `github-actions[bot]`) do not retrigger the workflow.

---

## Execution Pipeline: Step by Step

### Step 1: Authorize

```yaml
- name: Authorize
  run: |
    PERM=$(gh api "repos/${{ github.repository }}/collaborators/${{ github.actor }}/permission" \
      --jq '.permission' 2>/dev/null || echo "none")
    if [[ "$PERM" != "admin" && "$PERM" != "maintain" && "$PERM" != "write" ]]; then
      exit 1
    fi
```

**Purpose:** Gate access to the agent. Only repository collaborators with `write`, `maintain`, or `admin` permissions can trigger the agent. This prevents random users on public repos from consuming Actions minutes or interacting with the agent.

**Security implication:** The same mechanism that controls who can push code controls who can instruct the agent. No parallel ACL surface.

### Step 2: Reject (on auth failure)

```yaml
- name: Reject
  if: ${{ failure() && steps.authorize.outcome == 'failure' }}
  run: |
    gh api "repos/.../reactions" -f content=-1
```

**Purpose:** If authorization fails, add a 👎 reaction to the triggering comment/issue as visual feedback.

### Step 3: Checkout

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    ref: ${{ github.event.repository.default_branch }}
    fetch-depth: 0
```

**Purpose:** Full checkout of the repository with complete history (`fetch-depth: 0`). The agent operates on the actual repository contents, not a shallow copy.

### Step 4: Setup Bun

```yaml
- name: Setup Bun
  uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest
```

**Purpose:** Install the Bun JavaScript/TypeScript runtime. Bun is used because it can directly execute TypeScript without a compilation step.

### Step 5: Preinstall (indicator.ts)

```yaml
- name: Preinstall
  run: bun .github-minimum-intelligence/lifecycle/indicator.ts
```

**Purpose:** Add a 🚀 reaction to signal the agent is working. Runs *before* dependency installation to provide immediate visual feedback. Persists reaction metadata to `/tmp/reaction-state.json` for the agent's outcome reaction.

### Step 6: Install Dependencies

```yaml
- name: Install dependencies
  run: cd .github-minimum-intelligence && bun install --frozen-lockfile
```

**Purpose:** Install `@mariozechner/pi-coding-agent` and its transitive dependencies using the locked versions.

### Step 7: Run Agent (agent.ts)

```yaml
- name: Run
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    # ... (all supported provider keys)
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: bun .github-minimum-intelligence/lifecycle/agent.ts
```

**Purpose:** Execute the core agent orchestrator with all LLM API keys and GitHub token available as environment variables.

---

## The Agent as a CI Job

This execution model reinterprets AI interaction as CI/CD:

| CI/CD Concept | AI Agent Analog |
|---------------|----------------|
| Source code | Repository contents + issue body |
| Build step | Dependency installation |
| Test/run step | Agent execution (LLM reasoning + tool use) |
| Artifacts | Committed session state + code changes |
| Build log | Actions workflow log |
| Build status | Reaction (👍 success / 👎 failure) |

### Why This Matters

1. **Reproducibility** — Each run is a fresh VM. No state leaks between runs.
2. **Auditability** — Every run has logs, timestamps, and artifacts.
3. **Scalability** — GitHub provides the compute; you don't manage servers.
4. **Isolation** — Each run is sandboxed; one issue's processing can't corrupt another.

---

## Runtime Environment Characteristics

The `ubuntu-latest` runner provides:

| Resource | Specification |
|----------|--------------|
| CPU | 2-core |
| RAM | 7 GB |
| Storage | 14 GB SSD |
| OS | Ubuntu (latest LTS) |
| Network | Full internet access (outbound) |
| Privileges | `sudo` available (NOPASSWD) |
| Docker | Available |
| Tools | git, curl, jq, tac, tee, gh CLI |

The agent has access to all of this — it can install packages, run builds, execute tests, and interact with external services. The only boundaries are GitHub Actions' own resource limits and timeout policies.

---

## Timeout and Resource Limits

| Limit | Value |
|-------|-------|
| Job timeout | 6 hours (default), configurable |
| Workflow timeout | 35 days max queued |
| Storage | 14 GB per runner |
| Concurrent jobs | Varies by plan (20 for Free, 40 for Pro, etc.) |
| Monthly minutes | 2,000 (Free), 3,000 (Pro), 50,000 (Enterprise) |

Each agent invocation consumes minutes based on actual wall-clock runtime. A typical interaction (LLM call + file operations + git push) takes 1-5 minutes, making the per-interaction cost roughly **1-5 minutes** of GitHub Actions time.

---

## The Execution Loop as "Thinking"

When the agent runs, the `pi` tool harness creates a ReAct-style execution loop:

```
LLM receives prompt + context
    │
    ├─▶ LLM emits tool call (read file)
    │   pi executes → returns file contents
    │   LLM reasons over contents
    │
    ├─▶ LLM emits tool call (bash command)
    │   pi executes → returns output
    │   LLM reasons over output
    │
    ├─▶ LLM emits tool call (edit file)
    │   pi executes → returns confirmation
    │   LLM reasons, decides next step
    │
    └─▶ LLM produces final response
        Agent extracts text, posts to issue
```

This loop is the "thinking" of the mind. Each iteration is a thought → action → observation cycle, running inside the GitHub Actions runner.

---

## Key Design Pattern: Event-Driven Cognition

The fundamental pattern is **event-driven cognition**:

1. A social event (issue/comment) occurs
2. Infrastructure transforms it into computation
3. Computation produces artifacts (commits, comments)
4. Artifacts trigger future social events (user reads reply, responds)

This creates a self-sustaining loop where the repository continuously accumulates intelligence through the interaction of human intent and machine execution — all powered by GitHub Actions minutes.
