---
name: daily-standup
description: Daily standup support — progress summary, blocker identification, team status updates, sprint progress tracking, async standup. Use when running daily standups, checking team progress, identifying blockers, or generating async standup reports.
---

# Daily Standup

This skill covers generating daily standup summaries — per-person progress, blockers, and sprint-level status from Plane data.

> **Page formatting:** when publishing the standup as a project page, follow the HTML rules in [`examples/references/page-formatting.md`](../examples/references/page-formatting.md). Use one new dated page per standup (`Standup — YYYY-MM-DD`) so history stays browsable.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `cycle(action=list, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix.

## Available Tools

| Call | Description |
|------|-------------|
| `cycle(action=list)` | Find the active sprint: `status=current` |
| `cycle(action=list_workitems)` | Get all sprint items with states and assignees; takes a `pql` filter |
| `workitem(action=count)` | Sprint totals per state group without listing items |
| `workitem(action=list)` | Targeted queries: stalled, unassigned, overdue (`pql`) |
| `workitem_activity(action=list)` | Track recent state changes |
| `workitem_relation(action=list)` | Identify blocked items |
| `member(action=list_project)` | Team roster |
| `member(action=me)` | The current user, for `assignee = currentUser()` |
| `get_pql_reference` | Syntax of the `pql` filter |

## Standup Queries with PQL

Let the server do the filtering. These queries answer the standup questions directly (`<cycle_id>` from `cycle(action=list, status=current)`; at most 5 conditions per query; call `get_pql_reference` for the full syntax):

| Question | Call |
|----------|------|
| Sprint totals per state group | `workitem(action=count, project_id, pql='cycle = "<cycle_id>"', group_by=state__group)` |
| Done since the last standup | `cycle(action=list_workitems, project_id, cycle_id, pql='stateGroup = "completed" AND updatedAt >= daysAgo(1)')` |
| In progress | `cycle(action=list_workitems, project_id, cycle_id, pql='stateGroup = "started"')` |
| Stalled (no change for 2+ days) | `cycle(action=list_workitems, project_id, cycle_id, pql='stateGroup = "started" AND updatedAt < daysAgo(2)')` |
| In progress with no owner | `cycle(action=list_workitems, project_id, cycle_id, pql='stateGroup = "started" AND hasNoAssignee()')` |
| Past due and still open | `cycle(action=list_workitems, project_id, cycle_id, pql='isOverdue()')` |
| One person's items (my standup) | `workitem(action=list, project_id, pql='assignee = currentUser() AND stateGroup IN openStates()')` |

`updatedAt` is the time of the last change to the item itself; it does not move for every comment. Treat the stalled query as a candidate list and confirm with `workitem_activity(action=list)` before calling an item stalled in front of the team.

## Standup Summary Generation

### Full Workflow

```
1. Find active sprint:
   cycle(action=list, project_id=<id>, status=current)
   → The cycle where today is between start_date and end_date
   → Get cycle_id, start_date, end_date

2. Get sprint items:
   cycle(action=list_workitems, project_id=<id>, cycle_id=<cycle_id>)
   → Get all items with: name, state, assignees, point (follow next_cursor)
   workitem(action=count, project_id=<id>, pql='cycle = "<cycle_id>"', group_by=state__group)
   → The state-group totals for the dashboard in one call

3. Get team members:
   member(action=list_project, project_id=<id>)
   → Map user IDs to names

4. Group items by assignee and state:
   For each team member:
     completed_recently  = items in "completed" state (check activities for recent moves)
     in_progress         = items in "started" state assigned to them
     blocked             = items with "blocked_by" relations
     not_started         = items in "unstarted" state assigned to them

5. Detect blockers:
   For each "started" item, optionally:
   workitem_relation(action=list, project_id=<id>, workitem_id=<item_id>)
   → Check for "blocked_by" relations

   Also flag: items in "started" state for > 2 days without activity
   → cycle(action=list_workitems, ..., pql='stateGroup = "started" AND updatedAt < daysAgo(2)')

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
   workitem_relation(action=list, project_id=<id>, workitem_id=<item_id>)
   → Items with "blocked_by" relations
   (PQL shortcut for one item: blocks("MP-45") lists the items that block MP-45 — direction per the PQL reference wording, confirm on your instance)

2. Stalled items:
   Items in "started" state for > 2 business days
   → pql='stateGroup = "started" AND updatedAt < daysAgo(2)', then confirm the last
     state change with workitem_activity(action=list, project_id, workitem_id)

3. Unassigned in-progress:
   Items in "started" state with no assignees
   → pql='stateGroup = "started" AND hasNoAssignee()'
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

page(action=create,
     project_id=<id>,
     name="Standup — YYYY-MM-DD",
     description_html="<h2>Sprint Progress</h2>...<h2>Per Person</h2>...<h2>Blockers</h2>...")
```

## Best Practices

1. **Focus on blockers** — the standup's #1 purpose is surfacing and resolving blockers
2. **Keep it brief** — per person: 30 seconds max, whole team: 15 minutes max
3. **Update before standup** — move items to correct states in Plane before the meeting
4. **Flag at-risk items** — items not started past mid-sprint should be called out
5. **Don't solve problems in standup** — note the issue, schedule a separate discussion
6. **Track WIP** — if WIP is over limit, discuss what to finish before starting new work
