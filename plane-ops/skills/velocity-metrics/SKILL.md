---
name: velocity-metrics
description: Velocity and metrics — historical velocity calculation, sprint burndown analysis, WIP limits, throughput tracking, time effort analysis. Use when calculating velocity, analyzing sprint progress, reviewing team metrics, comparing estimated vs actual effort, or checking time logged per story point.
---

# Velocity & Metrics

This skill covers velocity tracking, sprint burndown analysis, WIP limit management, and team throughput metrics.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `list_archived_cycles`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_cycles` | List active cycles |
| `list_archived_cycles` | List completed sprints for velocity history |
| `retrieve_cycle` | Get cycle dates and details |
| `list_cycle_work_items` | Get items in a cycle with states |
| `list_work_items` | Get all project items for WIP analysis |
| `list_states` | Get state definitions for grouping |
| `get_project_members` | Team size for WIP limit calculation |
| `get_project_worklog_summary` | Aggregated time data |
| `list_work_logs` | Individual time entries per work item |

## Velocity Calculation

### Workflow

```
1. Get completed sprints:
   list_archived_cycles({ project_id })
   → Get last 5 archived cycles (or as many as available)
   → Sort by end_date descending

2. For each cycle, calculate completed points:
   list_cycle_work_items({ project_id, cycle_id })
   → Filter items where state group = "completed"
   → Sum their `point` values
   → Also sum total planned points (all items)

3. Build velocity table:
   | Sprint | Planned | Completed | Rate |
   |--------|---------|-----------|------|
   | Sprint 10 | 40 | 34 | 85% |
   | Sprint 9 | 38 | 35 | 92% |
   | Sprint 8 | 42 | 30 | 71% |
   | Sprint 7 | 35 | 33 | 94% |
   | Sprint 6 | 36 | 32 | 89% |

4. Check data reliability:
   If fewer than 3 completed sprints:
     → Warn: "Velocity based on <N> sprint(s) — treat as rough estimate.
       Need at least 3 sprints for a reliable baseline, 5+ for trend analysis."
     → Still calculate and show, but flag as LOW CONFIDENCE
   If 3-4 sprints: MODERATE CONFIDENCE
   If 5+ sprints: HIGH CONFIDENCE

5. Calculate metrics:
   average_velocity = mean(completed_points) = 32.8
   velocity_range = min..max = 30..35
   avg_completion_rate = mean(rates) = 86%
   trend = compare last 3 vs previous 3 (only if 6+ sprints)

6. Recommendation:
   "Plan next sprint for ~33 points (average velocity)"
   "With 15% buffer: commit to ~28 points"
```

### Velocity Trend Analysis

```
Improving: last 3 sprints avg > previous 3 sprints avg
  → Team is maturing, can slightly increase commitment

Stable: last 3 ≈ previous 3 (within 10%)
  → Predictable, use average for planning

Declining: last 3 < previous 3
  → Investigate: burnout? scope creep? technical debt?
  → Reduce commitment by 15-20%
```

## Sprint Burndown Analysis

### Workflow

```
1. Find active cycle:
   list_cycles({ project_id })
   → Find cycle where today is between start_date and end_date

2. Get sprint items:
   list_cycle_work_items({ project_id, cycle_id })

3. Categorize by state group:
   backlog    = items in "backlog" group (not started, not planned)
   unstarted  = items in "unstarted" group (planned but not started)
   started    = items in "started" group (in progress)
   completed  = items in "completed" group (done)
   cancelled  = items in "cancelled" group

4. Calculate burndown data:
   total_points     = sum of all items' points
   completed_points = sum of completed items' points
   remaining_points = total_points - completed_points

   sprint_days      = end_date - start_date (business days)
   elapsed_days     = today - start_date (business days)
   remaining_days   = end_date - today (business days)

   ideal_remaining  = total_points × (remaining_days / sprint_days)
   actual_remaining = remaining_points

5. Assess status:
   actual_remaining ≤ ideal_remaining → [ON TRACK]
   actual_remaining > ideal_remaining × 1.2 → [AT RISK]
   actual_remaining > ideal_remaining × 1.5 → [BEHIND]

6. Present dashboard:
   ┌──────────────────────────────────────┐
   │ SPRINT BURNDOWN: Sprint 12          │
   │ Day 3 of 5 (60% elapsed)           │
   ├──────────────────────────────────────┤
   │ Total:     40 points                │
   │ Completed: 22 points (55%)          │
   │ Remaining: 18 points                │
   │ Ideal:     16 points                │
   │ Status:    [AT RISK]               │
   ├──────────────────────────────────────┤
   │ Distribution:                       │
   │ ████████████░░░░░░░░ Completed (55%)│
   │ ████░░░░░░░░░░░░░░░░ In Progress(15%)│
   │ ██████░░░░░░░░░░░░░░ Not Started(30%)│
   ├──────────────────────────────────────┤
   │ Need to complete ~9 pts/day         │
   │ (vs ~6 pts/day pace so far)         │
   └──────────────────────────────────────┘
```

## WIP (Work in Progress) Limits

### Setting WIP Limits

```
Recommended WIP = floor(team_size × 1.5)

Examples:
  3-person team → WIP limit: 4
  5-person team → WIP limit: 7
  8-person team → WIP limit: 12
```

### WIP Monitoring Workflow

```
1. Get team size:
   get_project_members({ project_id })
   → count members

2. Calculate WIP limit:
   wip_limit = floor(team_size × 1.5)

3. Count current WIP:
   list_work_items({ project_id })
   → Count items in "started" state group
   → This is current_wip

4. Assess:
   current_wip ≤ wip_limit → HEALTHY
   current_wip > wip_limit → [OVER LIMIT]

5. Report:
   "WIP: 8/7 — [OVER LIMIT]"
   "1 item should be completed before starting new work"

   Items in progress:
   | Item | Assignee | Days in Progress |
   |------|----------|-----------------|
   | MP-42 Edit profile | @alice | 2 days |
   | MP-43 Upload avatar | @bob | 1 day |
   ...
```

### Why WIP Limits Matter

- **Reduces context switching** — team focuses on fewer things
- **Improves flow** — items move through faster
- **Exposes bottlenecks** — when limit hit, find what's stuck
- **Increases quality** — less multitasking, fewer mistakes

## Throughput Metrics

### Items Completed Per Sprint

```
For each archived cycle:
  count items in "completed" state group

Track trend:
  Sprint 10: 8 items
  Sprint 9:  10 items
  Sprint 8:  7 items
  Average:   8.3 items/sprint
```

### Cycle Time (Days per Item)

```
For completed items:
  cycle_time = date_moved_to_completed - date_moved_to_started

Average cycle time tells you how long items typically take.
High cycle time (> sprint_length/2) suggests items are too large.
```

## Time Effort Analysis

Compare estimated effort (story points) with actual time spent (work logs) to improve estimation accuracy over time.

### Workflow

```
1. Get project-level time summary:
   get_project_worklog_summary({ project_id })
   → Total logged hours, hours per member, hours per label

2. Get individual time entries for the sprint:
   list_work_logs({ project_id })
   → Filter by date range matching the sprint period
   → Group by work item

3. Build effort comparison table:
   For each completed item:
     estimated_effort = story points
     actual_hours     = sum of work logs for that item
     ratio            = actual_hours / estimated_effort

   | Item | Points | Hours Logged | Ratio (hrs/pt) |
   |------|--------|-------------|----------------|
   | MP-42 Edit profile | 3 | 4.5h | 1.5 |
   | MP-43 Upload avatar | 2 | 6.0h | 3.0 |
   | MP-44 Change email | 5 | 5.0h | 1.0 |

4. Calculate averages:
   avg_ratio = mean(actual_hours / points) across all items
   → This is the team's "hours per point" baseline

5. Identify estimation gaps:
   Items where ratio > avg_ratio × 1.5 → UNDERESTIMATED
   Items where ratio < avg_ratio × 0.5 → OVERESTIMATED

   Flag patterns:
   - Specific types (bugs, frontend, backend) consistently off?
   - Specific team members estimating differently?

6. Present analysis:
   ┌──────────────────────────────────────────┐
   │ TIME EFFORT ANALYSIS: Sprint 12          │
   ├──────────────────────────────────────────┤
   │ Team baseline: 1.8 hrs/point             │
   │ Total logged: 42h across 8 items         │
   ├──────────────────────────────────────────┤
   │ UNDERESTIMATED (ratio > 2.7):            │
   │   MP-43 Upload avatar: 3.0 hrs/pt        │
   │   → Consider: file handling tasks need    │
   │     higher estimates                      │
   ├──────────────────────────────────────────┤
   │ OVERESTIMATED (ratio < 0.9):             │
   │   MP-44 Change email: 1.0 hrs/pt         │
   │   → Team improving on CRUD tasks          │
   ├──────────────────────────────────────────┤
   │ Recommendation: Adjust estimates for      │
   │ file/media tasks upward by ~50%           │
   └──────────────────────────────────────────┘
```

### When to Use

- After sprint close — compare planned vs actual effort
- During estimation — reference historical hrs/point ratio
- In retrospectives — discuss estimation accuracy trends

## Sprint Health Dashboard

Combine all metrics into a single view:

```
┌─────────────────────────────────────────────┐
│ SPRINT HEALTH: Sprint 12                    │
├─────────────────────────────────────────────┤
│ Burndown:  55% done, 60% elapsed — [AT RISK] │
│ Velocity:  Trending stable (~33 pts/sprint)  │
│ WIP:       6/7 — Healthy                     │
│ Blockers:  1 item blocked                    │
│ Completion forecast: ~35 pts (vs 40 planned) │
├─────────────────────────────────────────────┤
│ Recommendations:                             │
│ 1. Focus on completing in-progress items     │
│ 2. Consider descoping MP-49 (not started)    │
│ 3. Resolve blocker on MP-48                  │
└─────────────────────────────────────────────┘
```

## Best Practices

1. **Velocity is for planning, not performance** — don't use it as a KPI
2. **Track trends, not individual sprints** — one bad sprint doesn't mean failure
3. **WIP limits are guidelines first** — start with recommended, adjust based on team feedback
4. **Burndown daily** — check mid-sprint to catch issues early
5. **Don't game metrics** — inflating points or splitting trivially defeats the purpose
6. **Use velocity for forecasting** — "at current velocity, this epic will take ~3 sprints"
