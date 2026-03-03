# GitHub Actions Cost Model

> GitHub Actions minutes analysis, cost considerations, optimization strategies, and the economics of running a repo-native AI agent.

---

## The Economics: Running a Mind on GitHub's Clock

GitHub Actions is the sole compute layer for GitHub Minimum Intelligence. Every issue opened, every comment posted, every agent thought consumes GitHub Actions minutes. Understanding the cost model is essential for evaluating the viability of "executing a repo as a mind."

---

## GitHub Actions Pricing

### Included Minutes (Monthly)

| Plan | Minutes/Month | Concurrent Jobs |
|------|---------------|-----------------|
| Free | 2,000 | 20 |
| Pro | 3,000 | 40 |
| Team | 3,000 | 60 |
| Enterprise | 50,000 | 180 |

### Overage Pricing

| Runner Type | Per-Minute Cost |
|-------------|----------------|
| Linux (ubuntu-latest) | $0.008 |
| Windows | $0.016 |
| macOS | $0.08 |

Since Minimum Intelligence runs on `ubuntu-latest`, the per-minute cost is **$0.008**.

---

## Per-Interaction Cost Analysis

### Typical Agent Invocation Timeline

| Phase | Duration | What Happens |
|-------|----------|-------------|
| Checkout + Setup | 10-20s | Clone repo, setup Bun |
| Preinstall (indicator.ts) | 2-5s | Add 🚀 reaction |
| Dependency install | 15-45s | `bun install --frozen-lockfile` |
| Agent execution | 30s-5min | LLM reasoning + tool use loop |
| Commit + push | 5-15s | Stage, commit, push, post reply |
| **Total** | **~1-6 min** | |

### Cost Per Interaction

| Scenario | Duration | Actions Cost | LLM Cost (est.) | Total Cost |
|----------|----------|-------------|-----------------|------------|
| Simple question | ~1 min | $0.008 | $0.01-0.05 | ~$0.02-0.06 |
| Code review | ~2-3 min | $0.016-0.024 | $0.05-0.20 | ~$0.07-0.22 |
| Code generation | ~3-5 min | $0.024-0.040 | $0.10-0.50 | ~$0.12-0.54 |
| Complex refactor | ~5-6 min | $0.040-0.048 | $0.20-1.00 | ~$0.24-1.05 |

### Monthly Usage Scenarios

| Usage Pattern | Interactions/Day | Minutes/Day | Monthly Minutes | Monthly Actions Cost |
|--------------|-----------------|-------------|-----------------|---------------------|
| Light (1 developer) | 5 | 10-15 | 300-450 | Free tier covers |
| Moderate (small team) | 20 | 40-60 | 1,200-1,800 | Free tier covers |
| Heavy (active team) | 50 | 100-150 | 3,000-4,500 | $0-12 overage |
| Intense (full reliance) | 100+ | 200-300 | 6,000-9,000 | $24-48 overage |

---

## Cost Optimization Strategies

### 1. Choose the Right LLM Provider

The LLM API call is typically the most expensive part — not the Actions minutes:

| Provider | Model | Input Cost | Output Cost | Speed |
|----------|-------|-----------|-------------|-------|
| OpenAI | gpt-5.3-codex | Varies | Varies | Fast |
| Anthropic | claude-sonnet-4 | $3/MTok | $15/MTok | Moderate |
| Google | gemini-2.5-flash | Low | Low | Fast |
| Groq | deepseek-r1 distill | Very low | Very low | Very fast |
| OpenRouter | Various | Varies | Varies | Varies |

Cheaper/faster models reduce both LLM cost and Actions minutes (shorter agent runtime).

### 2. Optimize the Workflow

```yaml
# Cache Bun dependencies to speed up install
- name: Cache Bun
  uses: actions/cache@v4
  with:
    path: ~/.bun/install/cache
    key: bun-${{ hashFiles('.github-minimum-intelligence/bun.lock') }}

# Use sparse checkout if the repo is large
- name: Checkout
  uses: actions/checkout@v4
  with:
    sparse-checkout: |
      .github-minimum-intelligence
      src/
```

### 3. Filter by Label

Only trigger the agent on issues with a specific label:

```yaml
on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]

jobs:
  run-agent:
    if: contains(github.event.issue.labels.*.name, 'ai')
```

This prevents every issue from consuming Actions minutes.

### 4. Set Timeouts

```yaml
jobs:
  run-agent:
    timeout-minutes: 10  # Cap runaway agent
```

### 5. Use Self-Hosted Runners

For teams with heavy usage, self-hosted runners eliminate per-minute charges:

```yaml
runs-on: self-hosted  # Instead of ubuntu-latest
```

---

## Cost Comparison: AI Agent Hosting Models

| Model | Monthly Cost (Moderate Use) | Infrastructure | Control |
|-------|-----------------------------|---------------|---------|
| **GitHub Actions** (Minimum Intelligence) | $0-15 (Actions) + $10-50 (LLM) | Zero | Full |
| **SaaS AI Platform** (Cursor, etc.) | $20-40/seat | Managed | Limited |
| **Self-Hosted Server** | $50-200 (cloud VM) + LLM | DIY | Full |
| **GitHub Copilot** | $10-19/seat | Managed | Limited |

GitHub Actions is the most cost-effective for low-to-moderate usage because:
- Free tier covers ~150-600 interactions/month
- No server to maintain
- Pay only for what you use

---

## The Economics of "Executing a Repo as a Mind"

### The Fundamental Equation

```
Cost of Intelligence = GitHub Actions Minutes + LLM API Calls
```

Both scale linearly with usage. There is no base cost, no minimum commitment, no idle infrastructure charge. The "mind" is dormant when not thinking and costs nothing.

### What You Get for Free

- **2,000 minutes/month** of compute (Free plan)
- Unlimited storage for session state (within Git limits)
- Unlimited issues for conversations
- Unlimited conversation history (committed to git)
- CI/CD infrastructure, security scanning, and collaboration features
- Full audit trail at no extra cost

### The Real Cost Driver

In practice, the **LLM API cost dominates** over Actions minutes:

| Component | ~% of Total Cost |
|-----------|-----------------|
| LLM API calls | 60-80% |
| GitHub Actions minutes | 20-40% |

This means the most impactful optimization is model selection, not workflow optimization.

---

## Scaling Considerations

### For Individual Developers

The Free tier (2,000 minutes) supports ~300-600 interactions/month — more than sufficient for an individual developer's daily workflow.

### For Small Teams (2-5 people)

The Pro/Team tier (3,000 minutes) supports ~500-1,000 interactions/month. With label-based filtering and judicious use, this covers most team needs.

### For Organizations

Enterprise tier (50,000 minutes) supports ~8,000-16,000 interactions/month — enough for multiple teams running agents across many repositories.

### Beyond GitHub's Limits

For very high usage:
- Self-hosted runners (unlimited minutes, you pay for hardware)
- Scheduled batch processing (run during off-peak hours)
- Hybrid model (self-hosted for heavy repos, GitHub-hosted for others)

---

## Key Insight: The Mind Is Pay-Per-Think

Unlike a traditional server that runs 24/7, this "mind" only exists when it's thinking. Each thought is a discrete GitHub Actions job that:
- Starts from nothing (fresh VM)
- Loads its memory (git checkout)
- Thinks (LLM + tool loop)
- Saves its memory (git commit + push)
- Disappears (VM destroyed)

This is **serverless cognition**: intelligence that exists only during the moments of interaction, but whose memory persists indefinitely in git. The cost model is pay-per-think, not pay-per-month.
