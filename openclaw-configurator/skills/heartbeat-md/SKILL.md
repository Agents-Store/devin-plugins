---
name: heartbeat-md
description: Guide for configuring HEARTBEAT.md — the periodic background task checklist that OpenClaw executes on a schedule. Use this skill whenever the user needs background monitoring, periodic checks, standing orders integration, quiet hours configuration, or wants to understand heartbeat mechanics and token costs. Even questions like "how do I make the agent check something periodically", "set up monitoring", or "reduce heartbeat token costs" need this skill.
---

# HEARTBEAT.md Configuration Guide

HEARTBEAT.md is a minimal checklist for heartbeat runs — periodic background tasks the agent executes automatically. Keep it SHORT to limit token burn (it's loaded on every heartbeat cycle).

## Default Template

```markdown
# Keep this file empty (or with only comments) to skip heartbeat API calls.
# Add tasks below when you want the agent to check something periodically.
```

An empty HEARTBEAT.md (or comments only) means NO heartbeat API calls — saves tokens.

## Heartbeat Mechanics

- Heartbeats run at intervals configured in `openclaw.json`:
  ```json
  {
    "agents": {
      "defaults": {
        "heartbeat": {
          "every": "5m",
          "model": "gpt-4o-mini",
          "lightContext": true,
          "isolatedSession": true
        }
      }
    }
  }
  ```
- Each heartbeat loads HEARTBEAT.md and executes listed tasks
- State tracking via `memory/heartbeat-state.json` prevents redundant checks
- Use `lightContext: true` and a cheaper model to minimize token costs

## Example HEARTBEAT.md

```markdown
# Periodic Checks

- [ ] Check email for new messages (inbox only)
- [ ] Check Telegram mentions in monitored groups
- [ ] Check calendar for upcoming events (next 2 hours)
- [ ] Review standing orders due for execution

# Quiet Hours
No checks between 22:00 and 08:00 (user's timezone)
```

## Standing Orders Integration

HEARTBEAT.md triggers standing order execution. Standing orders live in `docs/standing-orders/` and are referenced from AGENTS.md. The heartbeat checks which orders are due.

```markdown
# Standing Orders Check
- [ ] Read docs/standing-orders/ and execute any programs due
- [ ] Log execution results to memory/YYYY-MM-DD.md
```

See the **standing-orders** skill for detailed standing order design patterns.

## Token-Efficient Heartbeats

Every heartbeat costs tokens. Minimize cost:

1. **Use a cheap model** — set `heartbeat.model` to `gpt-4o-mini` or similar
2. **Keep checklist short** — 3-5 items max
3. **Use `lightContext: true`** — loads minimal context
4. **Set appropriate intervals** — don't check every minute unless needed
5. **Track state** — use `heartbeat-state.json` to skip already-processed items
6. **Define quiet hours** — no heartbeats during sleep/off hours

## What Data Is Needed

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Business hours | Client timezone + schedule | Quiet hours |
| Monitoring needs | Client requirements | What to check |
| News/legal sources | Domain-specific | Sites/feeds to monitor |
| Standing orders | docs/standing-orders/ | Scheduled tasks |
| Channel activity | openclaw.json channels | Which platforms to monitor |

## Signals That Improve HEARTBEAT.md

- **User asks "did anything happen?"** → add relevant monitoring
- **User wants periodic reports** → add to checklist
- **Agent burns tokens on useless checks** → remove from checklist
- **Missed important event** → add monitoring for that event type
- **Too many notifications** → refine filters, add quiet hours

## Common Patterns

### Minimal (personal assistant)
```markdown
- [ ] Check email for urgent messages
- [ ] Calendar: next 2 hours
```

### Moderate (team agent)
```markdown
- [ ] Check email for new messages
- [ ] Check Telegram mentions
- [ ] Review standing orders
- [ ] Calendar: upcoming meetings today
# Quiet: 22:00-07:00
```

### Comprehensive (monitoring agent)
```markdown
- [ ] Check email inbox
- [ ] Check all monitored channels for mentions
- [ ] Execute due standing orders from docs/standing-orders/
- [ ] Check system health dashboards
- [ ] Review pending approvals
# Quiet: 00:00-06:00
```

## Best Practices

1. Start with an empty file — add only what's needed
2. Keep to 3-5 checklist items
3. Always define quiet hours
4. Use the cheapest model that can handle the tasks
5. Track state to avoid redundant work
6. Review token costs weekly — remove low-value checks
