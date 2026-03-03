# Installation Model

> How `github-minimum-intelligence` installs into target repos: the folder-as-agent pattern, setup.sh, the installer script, and what gets placed where.

---

## The Core Insight: A Folder Is the Entire Product

The most radical design decision in GitHub Minimum Intelligence is that the entire AI agent system is a single folder — `.github-minimum-intelligence/` — that can be dropped into any Git repository. There is no hosted backend, no cloud dashboard, no SaaS subscription. The product is a directory.

This is not minimalism for its own sake. It is a deliberate architectural constraint that keeps the agent:
- **Inspectable** — every file is readable by any developer
- **Portable** — copy the folder, and the agent comes with it
- **Governable** — changes go through normal PR/review processes
- **Versionable** — git tracks everything, including behavioral changes

---

## Installation Methods

### Method 1: One-Command Setup Script

```bash
curl -fsSL https://raw.githubusercontent.com/japer-technology/github-minimum-intelligence/main/setup.sh | bash
```

The `setup.sh` script performs:

1. **Preflight checks**
   - Verifies `git` is installed
   - Confirms we're inside a Git repository
   - Verifies `bun` runtime is available
   - Checks that `.github-minimum-intelligence/` doesn't already exist

2. **Download**
   - Downloads the latest main branch as a zip archive
   - Extracts to a temp directory
   - Copies the `.github-minimum-intelligence/` folder to the target repo

3. **Clean state**
   - Removes the `state/` folder (contains runtime state from the source repo)
   - Resets `AGENTS.md` to default template (no inherited identity)
   - Resets `.pi/settings.json` to default provider config

4. **Install**
   - Runs the TypeScript installer: `bun .github-minimum-intelligence/install/MINIMUM-INTELLIGENCE-INSTALLER.ts`

### Method 2: Manual Copy

Copy the `.github-minimum-intelligence/` folder manually and run the installer.

### Method 3: GitHub App (automated installation across repos)

Uses `app-manifest.json` to define a GitHub App with permissions for issues (write), contents (write), actions (write), and metadata (read).

---

## The Installer Script

`MINIMUM-INTELLIGENCE-INSTALLER.ts` is a Bun/TypeScript script that sets up the GitHub integration points:

### What It Creates

| Target | Source | Purpose |
|--------|--------|---------|
| `.github/workflows/github-minimum-intelligence-agent.yml` | `install/github-minimum-intelligence-agent.yml` | The GitHub Actions workflow that powers the agent |
| `.github/ISSUE_TEMPLATE/github-minimum-intelligence-hatch.md` | `install/github-minimum-intelligence-hatch.md` | Issue template for "hatching" the agent's identity |
| `.github/ISSUE_TEMPLATE/github-minimum-intelligence-chat.md` | `install/github-minimum-intelligence-chat.md` | Issue template for chatting with the agent |
| `.github-minimum-intelligence/AGENTS.md` | `install/MINIMUM-INTELLIGENCE-AGENTS.md` | Default agent identity (if not already configured) |
| `.github-minimum-intelligence/.pi/settings.json` | `install/settings.json` | Default LLM provider settings |

### What It Does NOT Overwrite

The installer respects existing configuration:
- If `AGENTS.md` already contains an `## Identity` section, it is preserved
- If `.pi/settings.json` already exists, it is not overwritten
- Existing workflow files are skipped with a log message

### Post-Install Steps

After the installer runs:

1. **Add API key** — Set an LLM provider API key as a GitHub repository secret (e.g., `OPENAI_API_KEY`)
2. **Commit and push** — `git add -A && git commit -m "Add minimum-intelligence" && git push`
3. **Open an issue** — The agent replies automatically

---

## What Gets Committed to the Target Repo

After installation, the target repo gains:

```
target-repo/
├── .github/
│   ├── workflows/
│   │   └── github-minimum-intelligence-agent.yml   # Agent workflow
│   └── ISSUE_TEMPLATE/
│       ├── github-minimum-intelligence-chat.md      # Chat template
│       └── github-minimum-intelligence-hatch.md     # Hatch template
├── .github-minimum-intelligence/
│   ├── .pi/
│   │   ├── APPEND_SYSTEM.md      # Behavioral instructions
│   │   ├── BOOTSTRAP.md          # First-run co-creation
│   │   ├── settings.json         # LLM provider config
│   │   └── skills/               # Agent capabilities
│   ├── lifecycle/
│   │   ├── agent.ts              # Core orchestrator
│   │   └── indicator.ts          # Activity indicator
│   ├── install/                  # Installer templates (reference)
│   ├── docs/                     # Documentation
│   ├── AGENTS.md                 # Agent identity
│   ├── PACKAGES.md               # Dependency docs
│   ├── package.json              # pi-coding-agent dependency
│   └── bun.lock                  # Lockfile
└── (existing repo files unchanged)
```

---

## Design Principles of the Installation Model

### 1. Zero Configuration Required

The only external dependency is an LLM API key. Everything else is self-contained in the folder.

### 2. No Build Step

The agent code is TypeScript executed directly by Bun. There's no compilation, no bundling, no build pipeline to maintain.

### 3. Self-Documenting

Every component includes inline documentation:
- `agent.ts` has a ~80-line header documenting purpose, lifecycle position, execution pipeline, session continuity, push conflict resolution, and dependencies
- `indicator.ts` similarly documents its purpose and fault tolerance model
- The `docs/` folder contains comprehensive architectural documentation

### 4. Clean Separation of Concerns

| Directory | Concern |
|-----------|---------|
| `.pi/` | Agent configuration and behavioral rules |
| `lifecycle/` | Runtime orchestration code |
| `install/` | One-time setup templates |
| `state/` | Per-session runtime state |
| `docs/` | Documentation and analysis |

### 5. Dependency Minimalism

The entire runtime dependency tree is one package: `@mariozechner/pi-coding-agent`. This pulls in LLM SDK clients transitively, but the direct dependency surface is intentionally minimal.

---

## Implications for Agenticana

The installation model demonstrates that a complex AI agent system can be:

1. **Distributed as files** — no package registry, no installer binary, no cloud account
2. **Activated by a workflow** — the `.github/workflows/` file is the activation mechanism
3. **Configured by text** — Markdown and JSON files replace dashboards and settings panels
4. **Scoped by folder** — the entire agent lives inside one directory prefix, keeping it isolated from the host repo

This pattern could be directly adapted for Agenticana, where the 20-agent system, MCP server, and orchestration framework could similarly be encapsulated in a `.github-agenticana/` folder that self-installs its workflow triggers and issue templates.
