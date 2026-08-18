---
name: standing-orders
description: Design patterns for standing orders — autonomous programs that give agents permanent operating authority for defined tasks. Use this skill whenever the user needs recurring tasks, scheduled agent operations, autonomous execution rules, or the execute-verify-report pattern. Also applies when discussing cron jobs with OpenClaw, periodic reports, automated monitoring, content scheduling, or any task the agent should do on its own without prompting each time.
---

# Standing Orders Design Guide

Standing orders grant agents "permanent operating authority" for defined programs. Instead of prompting for every task, you establish autonomous execution rules with clear boundaries.

## Core Concept

Without standing orders: you prompt for every task, becoming a bottleneck.
With standing orders: the agent executes autonomously within defined boundaries, and routine work happens on schedule without prompting.

## Anatomy of a Standing Order

Every standing order specifies four elements:

### 1. Scope — What the agent can do
```markdown
## Authority
- Draft weekly status reports from project data
- Pull metrics from configured dashboards
- Compile findings into standard template
```

### 2. Triggers — When it executes
```markdown
## Trigger
- Schedule: Every Friday at 15:00 (user's timezone)
- OR: On request from authorized user
- OR: When specific condition is met
```

### 3. Approval Gates — What needs human sign-off
```markdown
## Approval
- First 30 days: every execution requires approval before sending
- After 30 days: auto-send unless flagged for review
- Always require approval for: amounts > $1000, external communications
```

### 4. Escalation Rules — When to ask for help
```markdown
## Escalation
- If data source is unavailable: retry once, then notify owner
- If results look anomalous (>50% deviation): flag for review
- If task takes >30 minutes: notify and continue
- Never: proceed without data, fabricate numbers, skip verification
```

## Execute-Verify-Report Pattern

Every standing order task should follow this pattern (skipping it leads to a common failure where the agent acknowledges a task but doesn't actually complete it):

1. **Execute** — complete the work (not just acknowledge it)
2. **Verify** — confirm results (file exists, delivery confirmed, data parsed correctly)
3. **Report** — inform the owner of findings and status

This prevents a common failure: agent acknowledges a task but doesn't actually complete it.

## File Organization

Standing orders live in `docs/standing-orders/`:

```
workspace/
└── docs/
    └── standing-orders/
        ├── weekly-report.md
        ├── monitoring.md
        ├── content-drafting.md
        └── data-processing.md
```

Reference them from AGENTS.md:
```markdown
## Standing Orders
See docs/standing-orders/ for authorized autonomous programs.
Check heartbeat for due orders and execute per their instructions.
```

## Standing Orders + Cron Jobs

Standing orders define WHAT; cron jobs define WHEN.

```
Standing order (docs/standing-orders/weekly-report.md):
  - What to do, quality standards, approval rules

Cron job (managed via `openclaw cron add/edit/rm`, stored in ./cron/jobs.json):
  - When to trigger the agent
  - References the standing order
  - NOT configured in openclaw.json (only `cron.enabled` boolean lives there)
```

The cron job triggers the agent, which reads the standing order and executes it. Manage cron jobs via the CLI (`openclaw cron add`, `openclaw cron edit`, `openclaw cron rm`), not by editing openclaw.json directly.

## Real-World Patterns

### Content & Social Media
```markdown
# Content Drafting Program

## Authority
- Draft social media posts based on recent content
- Schedule posts using configured tools
- Monitor engagement metrics

## Trigger
- Daily at 09:00 (content drafting)
- Hourly (engagement monitoring)

## Approval
- First 30 days: every post requires approval
- After trust established: auto-post during business hours
- Always flag: controversial topics, competitor mentions

## Execution Steps
1. Review content calendar for today's topics
2. Draft posts matching brand voice (see SOUL.md)
3. Check against brand guidelines
4. Submit for approval OR auto-post (per approval rules)
5. Log results to memory

## What NOT to do
- Never post without checking brand guidelines
- Never engage with negative comments without approval
- Never share internal metrics publicly
```

### System Monitoring
```markdown
# System Monitoring Program

## Authority
- Check health endpoints for configured services
- Restart services that are down (max 2 restart attempts)
- Escalate persistent failures

## Trigger
- Every 5 minutes (via heartbeat)

## Approval
- Auto-restart: no approval needed (pre-authorized)
- Manual intervention: escalate to ops team

## Escalation
- Service down after 2 restarts → alert ops channel
- Multiple services down → alert + phone call to on-call
- Data loss indicators → immediate escalation, stop all operations
```

### Financial Processing
```markdown
# Transaction Processing Program

## Authority
- Process incoming invoices from configured sources
- Categorize transactions per chart of accounts
- Flag anomalies for review

## Trigger
- Event-driven: on new invoice received
- Daily at 18:00: reconciliation check

## Approval
- Transactions < $500: auto-categorize
- Transactions $500-$5000: flag for review
- Transactions > $5000: require explicit approval

## Escalation
- Duplicate invoice detected → flag immediately
- Vendor not in approved list → hold for approval
- Amount deviates >30% from average → flag for review
```

## Multi-Program Architecture

For complex agents, separate standing orders by domain:

1. Each program has distinct trigger cadence
2. Each program has its own approval requirements
3. Include universal escalation rules that apply across all programs
4. Review programs quarterly for relevance

## Best Practices

1. **Start narrow** — begin with limited authority, expand as trust builds
2. **Define explicit approval gates** — especially for external-facing actions
3. **Include "What NOT to do"** — prevents scope creep
4. **Pair with cron jobs** — for reliable schedule-based execution
5. **Review agent logs weekly** — verify standing orders execute correctly
6. **Update as needs evolve** — standing orders are living documents
7. **Never skip escalation rules** — they're the safety net
8. **Don't mix domains** — one program per area of responsibility
