# Memory and State

> Session continuity via git-as-memory, state directory structure, issue→session mapping, push conflict resolution, and conversation persistence.

---

## The Central Claim: Git Is the Memory Layer

In conventional AI tooling, memory is a vendor feature — session transcripts stored on someone else's servers, context windows managed by platform logic, conversation history trapped in proprietary databases.

GitHub Minimum Intelligence replaces all of this with a single insight:

> **Git is already a versioned, distributed, append-only, auditable memory system.** Use it.

Every conversation transcript, every session mapping, every code change the agent makes is committed to the repository. Memory is not a feature bolted onto the system — it *is* the system.

---

## State Directory Structure

All agent state lives under `.github-minimum-intelligence/state/`:

```
.github-minimum-intelligence/state/
├── issues/
│   ├── 1.json          # Issue #1 → session mapping
│   ├── 2.json          # Issue #2 → session mapping
│   └── ...
├── sessions/
│   ├── 1708441200.jsonl   # Session transcript (JSONL)
│   ├── 1708527600.jsonl   # Another session
│   └── ...
└── user.md             # User profile information
```

### Issue Mapping Files (`issues/*.json`)

Each file maps an issue number to its associated session:

```json
{
  "issueNumber": 42,
  "sessionPath": ".github-minimum-intelligence/state/sessions/1708441200.jsonl",
  "updatedAt": "2026-02-20T10:00:00.000Z"
}
```

This is the continuity mechanism. When a new comment arrives on issue #42, the agent:
1. Reads `issues/42.json`
2. Finds the session path
3. Passes `--session <path>` to the `pi` agent
4. The LLM receives full conversation history from that session

### Session Transcripts (`sessions/*.jsonl`)

Session files are JSONL (JSON Lines) — one JSON object per line, where each line represents an event in the conversation:

```jsonl
{"type":"message_start","role":"user","content":"Add authentication to the API"}
{"type":"tool_use","name":"read","input":{"path":"src/api/server.ts"}}
{"type":"tool_result","content":"import express from 'express'..."}
{"type":"message_end","role":"assistant","content":"I've added JWT authentication..."}
```

These transcripts contain:
- User prompts
- Tool calls and their results
- Assistant responses
- Timestamps and metadata

### User Profile (`user.md`)

A Markdown file storing information about the human user:

```markdown
# User Profile
- Name: The Admiral
- Preferred address: Admiral
- Notes: Prefers concise responses
```

This is updated by the agent during the "hatch" process and ongoing conversations.

---

## Session Continuity Flow

### New Issue (First Message)

```
1. User opens issue #42
2. Agent checks: does issues/42.json exist?
   → No
3. Agent runs pi WITHOUT --session flag
   → Fresh conversation, no prior context
4. pi creates new session file: sessions/<timestamp>.jsonl
5. Agent writes issues/42.json mapping to the new session
6. Agent commits everything
```

### Follow-up Comment (Continuing Conversation)

```
1. User comments on issue #42
2. Agent checks: does issues/42.json exist?
   → Yes, sessionPath = sessions/1708441200.jsonl
3. Agent runs pi WITH --session sessions/1708441200.jsonl
   → LLM receives full conversation history
4. pi appends to the session file
5. Agent updates issues/42.json with new timestamp
6. Agent commits everything
```

### Orphaned Issue (Missing Session File)

If the mapping file points to a session file that no longer exists (deleted, moved, etc.):
- The agent treats it as a new conversation
- A new session is created
- The mapping is updated
- Previous context is lost for this issue

---

## Memory Properties Inherited from Git

Because all state is committed, memory inherits every property of Git:

| Property | What It Means for Memory |
|----------|------------------------|
| **Durability** | Persists as long as the repository exists |
| **Auditability** | `git log` shows every memory change with timestamps |
| **Diffability** | `git diff` reveals exactly what changed between sessions |
| **Recoverability** | `git revert` or `git checkout` can restore any prior state |
| **Branchability** | Fork a conversation by branching the repo |
| **Searchability** | `git log --grep` or `grep` across session files |
| **Attribution** | Every memory write has an author (the agent's commit) |
| **Distribution** | Cloning the repo clones the entire memory |

### Practical Implications

- **Resume after months** — Open an issue, get a response, disappear for a month. Reply with new requirements. The agent reads the full thread and current repo state.
- **Onboard new maintainers** — Show a factual trail, not a narrative summary. The entire conversation history is in git.
- **Roll back bad changes** — If the agent did something wrong, `git revert` the commit. Memory is reversible.
- **Audit what happened** — `git blame` on any session file shows exactly when each exchange occurred.

---

## Push Conflict Resolution

When multiple agents (or other processes) try to push simultaneously:

```
Attempt 1: git push
  → Fails (remote has new commits)
  → git pull --rebase -X theirs
  → Wait 1 second

Attempt 2: git push
  → Fails
  → git pull --rebase -X theirs
  → Wait 2 seconds

...

Attempt 10: git push
  → Fails
  → ERROR: "All 10 push attempts failed"
```

The backoff schedule is: 1s, 2s, 3s, 5s, 7s, 8s, 10s, 12s, 12s, 15s (total max wait: ~75 seconds).

The `-X theirs` strategy auto-resolves merge conflicts by accepting the remote's version. This is appropriate because:
- Session files are append-only (different issues write to different files)
- Mapping files are per-issue (no overlap)
- The most likely conflict is with another agent run that committed between our commit and push

---

## Memory Capacity and Scaling

### How Much Memory Can Accumulate?

Memory grows linearly with usage:
- Each conversation turn adds ~1-50 KB to the session JSONL
- Each issue mapping is ~100-200 bytes
- Over time, the `state/` directory grows

### Scaling Concerns

| Factor | Impact | Mitigation |
|--------|--------|------------|
| Repository size | Session files add to repo size | Periodic cleanup of old sessions |
| Checkout time | More files = longer checkout | Use sparse checkout for large repos |
| Context window | Full session history may exceed LLM context | `pi` handles context window management |
| Git performance | Large repos slow git operations | Prune old sessions, use shallow clones for CI |

### Memory Hygiene

The README notes: "The repo is overwhelmingly dominated by node_modules (~99%). The actual project files are only about ~1 MB." This suggests that session state accumulation is a long-term concern but not an immediate one.

Good practices:
- Periodically archive old sessions
- Use `.gitattributes` to mark session files as binary (prevent diff noise)
- Consider git LFS for very large session transcripts

---

## Comparison: Memory Models

| Model | Where Memory Lives | Who Controls It | Durability | Auditability |
|-------|--------------------|----------------|------------|-------------|
| ChatGPT | OpenAI servers | OpenAI | Platform-dependent | Not auditable |
| Claude Projects | Anthropic servers | Anthropic | Platform-dependent | Not auditable |
| VS Code Copilot | No persistent memory | N/A | Ephemeral | N/A |
| GitHub Minimum Intelligence | Git repository | Repository owner | Git-backed | Fully auditable |

The key difference: in every other model, memory is a vendor feature. In Minimum Intelligence, memory is a repository artifact — owned, inspectable, and under the maintainer's control.

---

## Implications for Agenticana

Agenticana's current memory system (`memory/reasoning-bank/`, `memory/trajectories/`) is already file-based but not git-committed as part of an automated workflow. The Minimum Intelligence pattern suggests:

1. **Commit agent state after every interaction** — not just on manual commits
2. **Use issue→session mapping** for conversation continuity
3. **Leverage git properties** (audit, rollback, diff) as first-class memory features
4. **Build conflict resolution** into the push logic for concurrent agent runs
