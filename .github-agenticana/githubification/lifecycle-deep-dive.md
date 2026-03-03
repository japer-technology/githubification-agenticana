# Lifecycle Deep Dive

> The three-phase agent lifecycle: indicator.ts (🚀), dependency install, agent.ts — with detailed analysis of the orchestration code.

---

## Overview: Three Phases of Execution

Every agent invocation follows a strict three-phase lifecycle:

```
Phase 1: Preinstall   → indicator.ts  → 🚀 reaction (immediate feedback)
Phase 2: Install      → bun install   → Dependencies ready
Phase 3: Run          → agent.ts      → LLM reasoning + tool execution + commit + reply
```

This ordering is intentional:
- **Phase 1 runs before dependencies** so users see immediate feedback even before npm packages are installed
- **Phase 2 is a standard install** using the frozen lockfile for reproducibility
- **Phase 3 is the core orchestrator** that does all the actual work

---

## Phase 1: indicator.ts — The Activity Indicator

### Purpose

Add a 🚀 rocket reaction to the triggering issue or comment the instant the workflow starts. This provides immediate visual feedback to the user: "I see your message, I'm working on it."

### How It Works

1. **Read the event payload** from `GITHUB_EVENT_PATH` (a JSON file injected by GitHub Actions)
2. **Determine the event type** from `GITHUB_EVENT_NAME`:
   - `issue_comment` → react to the specific comment
   - `issues` → react to the issue itself
3. **Add 🚀 reaction** via the GitHub API using `gh` CLI
4. **Persist reaction state** to `/tmp/reaction-state.json` for Phase 3

### Reaction State Handoff

The indicator writes a JSON file with metadata that `agent.ts` reads later:

```json
{
  "reactionId": "12345",
  "reactionTarget": "comment",
  "commentId": 67890,
  "issueNumber": 42,
  "repo": "owner/repo"
}
```

This enables the agent to add an outcome reaction (👍/👎) to the *same* target that received the 🚀.

### Fault Tolerance

Failures to add the reaction are caught and logged but do NOT abort the workflow. A missing emoji is not a critical error. The state file is always written (with `reactionId: null` on failure) so that `agent.ts` does not crash when reading it.

---

## Phase 2: bun install — Dependency Installation

```bash
cd .github-minimum-intelligence && bun install --frozen-lockfile
```

This installs `@mariozechner/pi-coding-agent` and its transitive dependencies. The `--frozen-lockfile` flag ensures exact version reproducibility from `bun.lock`.

### What Gets Installed

| Package | Role |
|---------|------|
| `@mariozechner/pi-coding-agent` | The core `pi` CLI agent with read, bash, edit, write tools |
| `@anthropic-ai/sdk` | Anthropic (Claude) API client (transitive) |
| `openai` | OpenAI API client (transitive) |
| `@google/generative-ai` | Google Gemini API client (transitive) |
| `@aws-sdk/client-bedrock-runtime` | AWS Bedrock client (transitive) |

---

## Phase 3: agent.ts — The Core Orchestrator

This is the heart of the system. At ~500 lines of TypeScript, `agent.ts` implements the complete agent execution pipeline.

### Execution Pipeline

#### Step 1: Read Environment Context

```typescript
const minimumIntelligenceDir = resolve(import.meta.dir, "..");
const stateDir = resolve(minimumIntelligenceDir, "state");
const issuesDir = resolve(stateDir, "issues");
const sessionsDir = resolve(stateDir, "sessions");
```

The agent resolves paths relative to its own location in the repository tree. It reads:
- `GITHUB_EVENT_PATH` — the webhook payload JSON
- `GITHUB_EVENT_NAME` — `issues` or `issue_comment`
- `GITHUB_REPOSITORY` — `owner/repo`

#### Step 2: Fetch Issue Context via GitHub CLI

```typescript
const issueData = JSON.parse(await gh("issue", "view", String(issueNumber), "--json", "title,body"));
```

The agent fetches the issue title and body using the `gh` CLI. For comments, it extracts the triggering comment body from the event payload.

#### Step 3: Resolve or Create Session

```typescript
// Check for existing session mapping
const mappingFile = resolve(issuesDir, `${issueNumber}.json`);
if (existsSync(mappingFile)) {
  // Load existing session for conversation continuity
  const mapping = JSON.parse(readFileSync(mappingFile, "utf-8"));
  sessionFile = mapping.sessionPath;
}
```

Session continuity logic:
- **New issue** → create a fresh session, no prior context
- **Existing issue with mapping** → load the existing session file, resume conversation
- **Existing issue without mapping** → treated as new (orphaned conversation)

#### Step 4: Build the Prompt

The agent constructs a prompt from:
- The issue title and body (for new issues)
- The comment body (for follow-up comments)
- The `AGENTS.md` file (agent identity and instructions)
- The `.pi/APPEND_SYSTEM.md` file (behavioral guidance)

#### Step 5: Execute the pi Agent

```typescript
const piArgs = [
  "pi",
  "--prompt", prompt,
  "--tools", "read,bash,edit,write,grep,find,ls",
  "--session-dir", sessionsDirRelative,
];

if (sessionFile) {
  piArgs.push("--session", sessionFile);
}
```

The `pi` binary runs with:
- The constructed prompt
- A set of allowed tools (read, bash, edit, write, grep, find, ls)
- An optional session file for conversation continuity
- Output streamed through `tee` to both Actions log and a JSONL file

#### Step 6: Extract the Reply

```typescript
// Extract the assistant's final text reply from JSONL output
const reply = await run(["bash", "-c",
  `tac /tmp/agent-raw.jsonl | jq -r 'select(.type == "message_end") | .content' | head -1`
]);
```

The agent output is JSONL (one JSON object per line). The final assistant reply is extracted by:
1. Reversing the file (`tac`)
2. Finding the last `message_end` event (`jq`)
3. Extracting its `content` field

#### Step 7: Persist Session Mapping

```typescript
writeFileSync(mappingFile, JSON.stringify({
  issueNumber,
  sessionPath: latestSession,
  updatedAt: new Date().toISOString(),
}, null, 2));
```

The issue→session mapping is written/updated so the next run can resume the conversation.

#### Step 8: Commit and Push

```typescript
await run(["git", "add", "-A"]);
const { exitCode } = await run(["git", "diff", "--cached", "--quiet"]);
if (exitCode !== 0) {
  await run(["git", "commit", "-m", `minimum-intelligence: work on issue #${issueNumber}`]);
}
```

All changes (session log, mapping JSON, any files the agent edited) are staged, committed, and pushed.

#### Step 9: Push with Conflict Resolution

```typescript
const pushBackoffs = [1000, 2000, 3000, 5000, 7000, 8000, 10000, 12000, 12000, 15000];
for (let i = 1; i <= 10; i++) {
  const push = await run(["git", "push", "origin", `HEAD:${defaultBranch}`]);
  if (push.exitCode === 0) { pushSucceeded = true; break; }
  await run(["git", "pull", "--rebase", "-X", "theirs", "origin", defaultBranch]);
  await new Promise(r => setTimeout(r, pushBackoffs[i - 1]));
}
```

Multiple agents may race to push to the same branch. The script retries up to 10 times with increasing backoff, rebasing with `--rebase -X theirs` to auto-resolve in favour of the remote.

#### Step 10: Post Reply as Issue Comment

```typescript
await gh("issue", "comment", String(issueNumber), "--body", commentBody);
```

The extracted reply is posted back to the issue as a new comment. GitHub enforces a ~65,535 character limit; the agent caps at 60,000 characters.

#### Step 11: Outcome Reaction (finally block)

```typescript
finally {
  const outcomeContent = succeeded ? "+1" : "-1";
  await gh("api", `repos/${repo}/issues/comments/${commentId}/reactions`,
    "-f", `content=${outcomeContent}`);
}
```

The `finally` block always executes. It adds 👍 on success or 👎 on error. The 🚀 from Phase 1 is left in place.

---

## Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| Authorization failure | 👎 reaction, workflow stops |
| Reaction API failure | Logged, not fatal |
| LLM API failure | Agent fails, 👎 reaction added |
| Empty response | Posts a fallback message with link to workflow logs |
| Git push conflict | Retries 10 times with backoff |
| All push attempts fail | Error thrown, 👎 reaction, warning appended to comment |
| Comment post failure | Logged in workflow run |

---

## Visual Feedback Timeline

```
User posts comment
    │
    ├─ T+0s    🚀 Rocket reaction appears (indicator.ts)
    │
    ├─ T+5-20s  (Dependencies installing)
    │
    ├─ T+20-300s (Agent thinking/executing)
    │
    ├─ T+end    💬 Reply posted as issue comment
    │
    └─ T+end    👍 Thumbs up (success) or 👎 Thumbs down (failure)
```

The three-reaction sequence (🚀 → 💬 → 👍/👎) provides a clear status indicator without requiring the user to check workflow logs.

---

## Key Observations

### 1. The Agent Is Ephemeral, the State Is Persistent

Each run starts fresh — no warm caches, no in-memory state. But the repository retains everything: session transcripts, issue mappings, code changes. Continuity is a property of the repository, not the process.

### 2. Tools Are the Real Capabilities

The `pi` binary with `--tools read,bash,edit,write,grep,find,ls` defines what the agent can actually *do*. Without these tools, the LLM can only generate text. With them, it can inspect code, run commands, make changes, and verify its work.

### 3. The Lifecycle Is Deliberately Minimal

Three TypeScript files (two in lifecycle/, one in install/) plus a workflow YAML. That's the entire runtime. No framework, no middleware, no plugin system. This minimalism is a feature: fewer moving parts means fewer failure modes.
