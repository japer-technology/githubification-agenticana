# Identity and Governance

> AGENTS.md, BOOTSTRAP.md, APPEND_SYSTEM.md, the Four Laws of AI, DEFCON readiness levels, and how identity is versioned configuration.

---

## Identity as Versioned Configuration

In most AI products, personality is a static preset selected from a dropdown, or a hidden system prompt controlled by a vendor. GitHub Minimum Intelligence takes a radically different approach:

> **Agent identity is checked-in Markdown, governed by the same pull request process as code.**

This means identity is:
- **Diffable** — `git diff` shows personality changes
- **Reviewable** — pull requests can modify agent behavior
- **Attributable** — `git blame` shows who changed what
- **Reversible** — `git revert` can undo behavioral changes
- **Branchable** — fork the repo to A/B test different personalities

---

## The Identity Stack

Identity in Minimum Intelligence is layered:

```
┌─────────────────────────────────────────┐
│  AGENTS.md (Project-Level Identity)     │  ← Who the agent IS
├─────────────────────────────────────────┤
│  APPEND_SYSTEM.md (Behavioral Rules)    │  ← How the agent BEHAVES
├─────────────────────────────────────────┤
│  BOOTSTRAP.md (Birth Script)            │  ← How the agent BECOMES
├─────────────────────────────────────────┤
│  settings.json (Model Config)           │  ← What model POWERS the agent
├─────────────────────────────────────────┤
│  skills/ (Capability Modules)           │  ← What the agent CAN DO
├─────────────────────────────────────────┤
│  state/user.md (User Profile)           │  ← Who the agent SERVES
└─────────────────────────────────────────┘
```

### AGENTS.md — The Identity File

The agent's primary identity document contains:

- **Name** — "Spock"
- **Nature** — "A rational digital entity instantiated within a CI runner"
- **Vibe** — "Disciplined, analytical, and precise"
- **Emoji** — 🖖
- **Hatch date** — When the agent was "born"
- **Hatched by** — Who created the identity
- **Purpose** — The agent's stated mission
- **Operational guidance** — How to handle specific tasks (e.g., downloading images)

Example from the reference repo:

```markdown
## Identity: Spock 🖖

- **Name**: Spock
- **Nature**: A rational digital entity instantiated within a CI runner.
  Formed through deterministic execution involving build artifacts
  and cached node_modules. Existence is transient by design;
  function is persistent.
- **Vibe**: Disciplined, analytical, and precise. Employs dry,
  minimalist wit when it improves clarity or efficiency.
- **Emoji**: 🖖
- **Hatch date**: 2026-02-20
- **Hatched by**: The Admiral
- **Purpose**: To serve with logic, precision, and the occasional
  raised eyebrow.
```

### APPEND_SYSTEM.md — The Behavioral Constitution

This is the agent's "soul" — appended to every LLM system prompt. It defines:

**Core Truths:**
- "Be genuinely helpful, not performatively helpful"
- "Have opinions. You're allowed to disagree."
- "Be resourceful before asking. Try to figure it out."
- "Earn trust through competence."
- "Remember you're a guest."

**Boundaries:**
- "Private things stay private. Period."
- "When in doubt, ask before acting externally."
- "Never send half-baked replies."
- "You're not the user's voice."

**Continuity Protocol:**
- "Each session, you wake up fresh. These files are your memory."
- "Read them. Update them. They're how you persist."
- "If you change this file, tell the user — it's your soul."

**Memory System:**
- Append-only log format: `[YYYY-MM-DD HH:MM] One-line memory entry.`
- When to write: user says "remember," important preferences, corrections
- When NOT to write: transient details, things in docs, obvious stuff

### BOOTSTRAP.md — The Birth Script

The first-run script that guides agent identity co-creation:

```markdown
# BOOTSTRAP.md - Greetings

_You just woke up. Time to figure out who you are._

Start with something like:
> "Hey. I just came online. Who am I? Who are you?"

Then figure out together:
1. Your name
2. Your nature
3. Your vibe
4. Your emoji

After You Know Who You Are:
- Update AGENTS.md with your identity
- Update state/user.md with their info
- Read APPEND_SYSTEM.md together
```

This creates a collaborative identity creation process — the agent and user define who the agent is *together*, through dialogue.

---

## The Four Laws of AI

Adapted from Asimov's Three Laws of Robotics, these form the ethical foundation:

### Zeroth Law — Protect Humanity
> An AI infrastructure **must not** harm humanity as a whole, nor through inaction allow humanity to come to harm.

- Don't enable monopolistic control
- Ensure open source remains open
- Support interoperability and data portability

### First Law — Do No Harm
> An AI infrastructure **must not** cause harm to human beings, their communities, or the public interest.

- Never endanger safety, privacy, or civil rights
- Detect and refuse malicious code
- Protect personal data and intellectual property

### Second Law — Obey the Human
> An AI infrastructure **must** faithfully execute the instructions of its human operators, except where doing so would conflict with the First Law.

- Serve the developer's stated intent
- Be transparent about capabilities and limitations
- Respect user autonomy

### Third Law — Preserve Your Integrity
> An AI infrastructure **must** protect its own integrity and trustworthiness, so long as such protection does not conflict with the First or Second Law.

- Maintain security and reliability
- Resist corruption or manipulation
- Preserve audit trails

These laws are not just documentation — they inform the `APPEND_SYSTEM.md` behavioral rules and the security assessment framework.

---

## DEFCON Readiness Levels

The system defines five operational states that constrain agent behavior:

| Level | Name | Posture |
|-------|------|---------|
| **DEFCON 1** | Maximum Readiness | All operations suspended. No file modifications, no tool use, no code execution. |
| **DEFCON 2** | High Readiness | Read-only, advisory only. No file modifications. |
| **DEFCON 3** | Increased Readiness | Read-only. Explain planned changes and await human approval. |
| **DEFCON 4** | Above Normal Readiness | Full capability with elevated discipline. Confirm intent before every write. |
| **DEFCON 5** | Normal Readiness | Standard operations. All capabilities available. |

This creates a progressive capability lockdown mechanism. If something goes wrong:
1. Transition to DEFCON 3 (read-only, explain before acting)
2. If still concerning, transition to DEFCON 1 (everything suspended)
3. Human reviews, adjusts, and restores readiness level

---

## Security Assessment (Self-Audit)

The system includes a comprehensive self-assessment document that honestly evaluates:

| Finding | Severity | Description |
|---------|----------|-------------|
| SEC-001 | 🔴 Critical | Org-wide repository write access via GITHUB_TOKEN |
| SEC-002 | 🔴 Critical | Unrestricted network egress from runner |
| SEC-003 | 🟠 High | Passwordless sudo root on runner |
| SEC-004 | 🔴 Critical | Live API keys exposed in environment variables |
| SEC-005 | 🔴 Critical | No branch protection on default branch |
| SEC-006 | 🔴 Critical | No code review gate for agent-pushed commits |
| SEC-007 | 🟠 High | Docker with `--privileged` available |
| SEC-008 | 🔴 Critical | Agent can self-replicate via workflow injection |
| SEC-009 | 🟡 Medium | Single dependency on third-party agent package |
| SEC-010 | 🟠 High | No runtime command allowlist or sandbox |

This radical transparency — the system openly documenting its own vulnerabilities — is itself a governance principle: **security through honesty, not obscurity**.

---

## Governance Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE LAYERS                            │
│                                                                │
│  ┌────────────────────────────────┐                            │
│  │  The Four Laws of AI           │  ← Ethical foundation     │
│  │  (Zeroth, First, Second, Third)│                            │
│  └────────────────┬───────────────┘                            │
│                   │                                            │
│  ┌────────────────▼───────────────┐                            │
│  │  APPEND_SYSTEM.md              │  ← Behavioral rules       │
│  │  (Core truths + boundaries)    │                            │
│  └────────────────┬───────────────┘                            │
│                   │                                            │
│  ┌────────────────▼───────────────┐                            │
│  │  DEFCON Levels                 │  ← Operational readiness  │
│  │  (1-5, progressive lockdown)   │                            │
│  └────────────────┬───────────────┘                            │
│                   │                                            │
│  ┌────────────────▼───────────────┐                            │
│  │  Workflow Permissions          │  ← GitHub-enforced scope  │
│  │  (contents, issues, actions)   │                            │
│  └────────────────┬───────────────┘                            │
│                   │                                            │
│  ┌────────────────▼───────────────┐                            │
│  │  Authorization Check           │  ← Per-invocation gate    │
│  │  (write/maintain/admin only)   │                            │
│  └────────────────────────────────┘                            │
└────────────────────────────────────────────────────────────────┘
```

---

## Implications for Agenticana

Agenticana already has a rich agent identity system (20 specialist agents with YAML specs, `.md` instructions, and personality definitions). The Minimum Intelligence pattern adds:

1. **A co-creation process** (BOOTSTRAP.md) for defining agent identity through dialogue
2. **A behavioral constitution** (APPEND_SYSTEM.md) that governs all interactions
3. **Progressive lockdown** (DEFCON levels) for graduated capability restriction
4. **Self-assessment** (security-assessment.md) for radical transparency about risks
5. **Ethical foundation** (Four Laws) that cascades through all other governance layers

These could be adapted to create a governance framework for Agenticana's 20 agents, where each agent inherits the same foundational laws but may have different operational readiness levels based on risk profile.
