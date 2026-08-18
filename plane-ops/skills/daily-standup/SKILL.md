---
name: daily-standup
description: Daily standup support — progress summary, blocker identification, team status updates, sprint progress tracking, async standup. Use when running daily standups, checking team progress, identifying blockers, or generating async standup reports.
---

# Daily Standup

This skill covers generating daily standup summaries — per-person progress, blockers, and sprint-level status from Plane data.

> **Page formatting:** when publishing the standup as a project page, follow the HTML rules in [`examples/references/page-formatting.md`](../examples/references/page-formatting.md). Use one new dated page per standup (`Standup — YYYY-MM-DD`) so history stays browsable.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `list_cycle_work_items`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_cycles` | Find active sprint |
| `list_cycle_work_items` | Get all sprint items with states and assignees |
| `list_work_item_activities` | Track recent state changes |
| `list_work_item_relations` | Identify blocked items |
| `get_project_members` | Team roster |
| `retrieve_cycle` | Sprint dates for progress calculation |

## Standup Summary Generation

### Full Workflow

```
1. Find active sprint:
   list_cycles({ project_id })
   → Find cycle where today is between start_date and end_date
   → Get cycle_id, start_date, end_date

2. Get sprint items:
   list_cycle_work_items({ project_id, cycle_id })
   → Get all items with: name, state, assignees, point

3. Get team members:
   get_project_members({ project_id })
   → Map user IDs to names

4. Group items by assignee and state:
   For each team member:
     completed_recently  = items in "completed" state (check activities for recent moves)
     in_progress         = items in "started" state assigned to them
     blocked             = items with "blocked_by" relations
     not_started         = items in "unstarted" state assigned to them

5. Detect blockers:
   For each "started" item, optionally:
   list_work_item_relations({ project_id, work_item_id })
   → Check for "blocked_by" relations

   Also flag: items in "started" state for > 2 days without activity

6. Generate report (see format below)
```

### Per-Person Standup Format

```
**Alice** (assigned: 4 items, 15 pts)
  [DONE] MP-42 Edit profile name (5 pts)
  [DOING] MP-43 Upload avatar (3 pts)
  [NEXT] MP-44 Change email (5 pts)

**Bob** (assigned: 3 items, 11 pts)
  [DOING] MP-45 Password reset (5 pts) — Day 2
  [NEXT] MP-46 Session management (3 pts)
  [BLOCKED] MP-47 OAuth setup — blocked by MP-45

**Carol** (assigned: 3 items, 14 pts)
  [DONE] MP-50 Fix login bug (2 pts)
  [DOING] MP-51 Rate limiting (5 pts)
  [NEXT] MP-52 API docs (3 pts)
```

### Team-Level Summary

```
┌──────────────────────────────────────┐
│ DAILY STANDUP — Sprint 12            │
│ Day 3 of 5 (Wed, Mar 12)            │
├──────────────────────────────────────┤
│ Sprint Progress:                     │
│ Points: 22/40 completed (55%)        │
│ Items:  5/10 done                    │
│                                      │
│ Status:                              │
│ [DONE] Completed today: 2 items (7 pts)    │
│ [DOING] In Progress: 4 items (18 pts)      │
│ [NEXT] Not Started: 1 item (5 pts)         │
│ [BLOCKED] Blocked: 1 item (5 pts)          │
│                                      │
│ WIP: 4/7 — Healthy                   │
│ Pace: 7.3 pts/day (need 6 pts/day)  │
├──────────────────────────────────────┤
│ [!] Attention:                       │
│ • MP-47 blocked by MP-45 (2 days)   │
│ • MP-49 not started (at risk)       │
└──────────────────────────────────────┘
```

## Blocker Detection

### Automatic Blocker Identification

Check for these signals:

```
1. Explicit blockers:
   list_work_item_relations({ project_id, work_item_id })
   → Items with "blocked_by" relations

2. Stalled items:
   Items in "started" state for > 2 business days
   (Check activities for last state change date)

3. Unassigned in-progress:
   Items in "started" state with no assignees
   → Risk: nobody owns it

4. Dependencies at risk:
   Items that block other sprint items and are not yet completed
```

### Blocker Report Format

```
[BLOCKED] BLOCKERS:
1. MP-47 "OAuth setup" — blocked by MP-45 "Password reset"
   Owner: @bob | Blocked for: 2 days
   Impact: Blocks MP-48 "Social login" too

2. MP-51 "Rate limiting" — stalled (no activity for 3 days)
   Owner: @carol | In progress since: Mar 9
   Suggestion: Check if help is needed
```

## Standup Cadence

| Sprint Length | Standup Frequency | Duration |
|--------------|-------------------|----------|
| 1 week | Daily (Mon-Fri) | 10 min |
| 2 weeks | Daily (Mon-Fri) | 15 min |
| Async team | 3x/week (Mon, Wed, Fri) | Async post |

## Async Standup (Remote Teams)

For async teams, generate a standup post that team members can review:

```
Generate and post as a comment or page:

create_project_page({
  project_id: "<id>",
  name: "Standup — YYYY-MM-DD",
  description_html: "<h2>Sprint Progress</h2>...<h2>Per Person</h2>...<h2>Blockers</h2>..."
})
```

## Best Practices

1. **Focus on blockers** — the standup's #1 purpose is surfacing and resolving blockers
2. **Keep it brief** — per person: 30 seconds max, whole team: 15 minutes max
3. **Update before standup** — move items to correct states in Plane before the meeting
4. **Flag at-risk items** — items not started past mid-sprint should be called out
5. **Don't solve problems in standup** — note the issue, schedule a separate discussion
6. **Track WIP** — if WIP is over limit, discuss what to finish before starting new work
