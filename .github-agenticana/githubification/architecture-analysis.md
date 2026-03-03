# Architecture Analysis

> How `github-minimum-intelligence` functions as a "mind" — the closed-loop system of Issues → Actions → LLM → Git.

---

## The Thesis: The Repo Is the Mind

GitHub Minimum Intelligence proves that a full AI agent can live as a single folder in any GitHub repository, powered by a production-grade runtime, with zero external infrastructure. The architectural thesis is:

> Intelligence should not orbit the repository as an external service. It should inhabit the repository as a first-class, auditable participant.

This is not metaphorical. It is an implementation reflected in file layout and workflow behavior.

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     GITHUB REPOSITORY                            │
│                                                                  │
│  ┌──────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │ GitHub Issues │───▶│ GitHub Actions   │───▶│ Git Commits    │  │
│  │ (UI Layer)   │    │ (Compute Layer)  │    │ (Memory Layer) │  │
│  └──────┬───────┘    └────────┬────────┘    └───────┬────────┘  │
│         │                     │                      │           │
│         │              ┌──────▼───────┐              │           │
│         │              │ LLM Provider  │              │           │
│         │              │ (Reasoning)   │              │           │
│         │              └──────┬───────┘              │           │
│         │                     │                      │           │
│         ◀─────────────────────┴──────────────────────┘           │
│                    (Reply posted to Issue)                        │
└──────────────────────────────────────────────────────────────────┘
```

### The Four Pillars

| Pillar | GitHub Primitive | Role in the System |
|--------|-----------------|-------------------|
| **Input** | GitHub Issues & Comments | Conversational interface — every issue becomes a conversation thread |
| **Compute** | GitHub Actions | Execution runtime — workflow triggers on issue events, runs agent code |
| **Reasoning** | LLM Provider (OpenAI, Anthropic, etc.) | Cognitive engine — plans, reasons, generates code via `pi` agent loop |
| **Memory** | Git commits | Persistent state — conversations, session transcripts, code edits all committed |

---

## The Closed Loop

The entire system runs as a closed loop inside the repository:

```
1. User opens issue (or comments)
       │
2. GitHub Actions workflow triggers
       │
3. Authorization check (collaborator permissions)
       │
4. 🚀 Reaction added (visual indicator)
       │
5. Dependencies installed (bun install)
       │
6. Agent receives issue body + conversation context
       │
7. pi agent runs ReAct loop:
   │   a. LLM receives prompt + repo context
   │   b. LLM emits tool call (read, bash, edit, write)
   │   c. pi executes the call, returns result
   │   d. LLM reasons over result, emits next action
   │   e. Loop until task resolves
       │
8. Session state committed to git
       │
9. Reply posted as issue comment
       │
10. Outcome reaction added (👍 or 👎)
```

Every step produces auditable artifacts. Every change is a commit with a hash, author, and diff.

---

## Key Architectural Decisions

### 1. devDependency, Not a Platform

`@mariozechner/pi-coding-agent` is an npm package installed in the repo's own tree. There is no hosted backend, no OAuth handshake, no tenant isolation. Standard supply-chain practices apply: version pinning, lockfile auditing, vendoring, forking.

### 2. Colocation With the Worktree

The agent runs inside a GitHub Actions runner with a full checkout of the repository. It has direct filesystem access — no API abstraction layer, no context-window packing heuristics. It reads `tsconfig.json`, runs `find`, greps source code. The full project graph is available.

### 3. Separation of Cognition and Action

The architecture cleanly separates:
- **LLM** → planning, reasoning, code generation (probabilistic reconstruction)
- **pi tool harness** → filesystem operations, shell access, search, git commands (deterministic execution)

This is a standard ReAct-style agent loop, but the tool surface is the actual development environment, not a sandboxed approximation.

### 4. Stateless Execution, Stateful History

Each agent invocation is a fresh process. No warm session, no in-memory conversation cache. State is reconstructed from durable artifacts: the issue thread, the commit log, the repo contents at HEAD.

### 5. Configuration as Code for Agent Personality

The agent's persona, behavioral boundaries, and operational practices are stored as editable Markdown files in the repository. Identity is diffable, reviewable, and subject to normal PR processes.

---

## File Layout

```
.github-minimum-intelligence/
├── .pi/
│   ├── APPEND_SYSTEM.md      # Agent behavioral instructions (the "soul")
│   ├── BOOTSTRAP.md          # First-run identity co-creation script
│   ├── settings.json         # LLM provider/model configuration
│   ├── skills/               # Modular capability definitions
│   │   ├── memory/
│   │   └── skill-creator/
│   └── README.md
├── lifecycle/
│   ├── agent.ts              # Core agent orchestrator (main entry point)
│   ├── indicator.ts          # Pre-install 🚀 reaction indicator
│   └── README.md
├── install/
│   ├── MINIMUM-INTELLIGENCE-INSTALLER.ts  # Setup script
│   ├── github-minimum-intelligence-agent.yml  # Workflow template
│   ├── github-minimum-intelligence-chat.md    # Issue template (chat)
│   ├── github-minimum-intelligence-hatch.md   # Issue template (hatch)
│   ├── MINIMUM-INTELLIGENCE-AGENTS.md         # Default identity
│   ├── settings.json                          # Default provider config
│   └── package.json
├── state/
│   ├── issues/               # Issue → session mappings (JSON)
│   ├── sessions/             # Session transcripts (JSONL)
│   └── user.md               # User profile
├── docs/                     # Comprehensive documentation
│   ├── index.md
│   ├── the-repo-is-the-mind.md
│   ├── the-four-laws-of-ai.md
│   ├── security-assessment.md
│   ├── question-{what,who,when,where,how,how-much}.md
│   └── ...
├── AGENTS.md                 # Agent identity and instructions
├── PACKAGES.md               # Dependency documentation
├── package.json              # Runtime dependency (pi-coding-agent)
├── bun.lock                  # Lockfile
└── logo.png
```

---

## What Makes This Architecture Novel

### 1. No New Trust Boundary

The agent's capabilities are scoped to what the workflow file grants. The same `GITHUB_TOKEN` permissions model applies. No new trust boundary is introduced beyond what is explicitly configured in Actions YAML.

### 2. Memory as Repository Primitive

"Long-term context" is not promised by marketing copy — it is guaranteed by commit history. Session transcripts are committed, diffable, and recoverable.

### 3. Identity Through Textual Constitutionalism

The agent is shaped by editable rules in the repo, not opaque server-side settings. You can `git log` the persona file to trace behavioral evolution. You can `git blame` to see who changed what and when.

### 4. Sovereignty by Default

| Concern | How Addressed |
|---------|--------------|
| Data sovereignty | Code never leaves repo/runner infrastructure |
| Auditability | Every agent action is a git commit with full diff |
| Vendor lock-in | npm dependency — pin, fork, or replace at will |
| Access control | Standard GitHub permissions, branch protection, CODEOWNERS |
| Reproducibility | Deterministic given same model + config + repo state |
| Offline capability | Runs anywhere you can host a runner and reach an LLM endpoint |

---

## The Cognitive Stack

Intelligence in this system is not a single model — it is distributed:

| Layer | Contributor |
|-------|------------|
| **Reasoning** | The LLM (plans, generates, synthesizes) |
| **Action** | The pi tool harness (executes filesystem ops, shell, git) |
| **Continuity** | Git history (preserves everything across sessions) |
| **Repeatability** | GitHub Actions workflows (deterministic pipeline) |
| **Correction** | Human collaborators (govern, review, course-correct) |

This is a cognitive stack, not a cognitive monolith. Intelligence scales with the quality of each layer, not just model capability alone.
