---
name: velocity-metrics
description: Velocity and metrics — historical velocity calculation, sprint burndown analysis, WIP limits, throughput tracking, time effort analysis. Use when calculating velocity, analyzing sprint progress, reviewing team metrics, comparing estimated vs actual effort, or checking time logged per story point.
---

# Velocity & Metrics

This skill covers velocity tracking, sprint burndown analysis, WIP limit management, and team throughput metrics.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `cycle(action=list, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix.

## Available Tools

| Call | Description |
|------|-------------|
| `cycle(action=list)` | Sprints: `status=current\|upcoming\|completed\|draft\|incomplete`, or `archived=true` |
| `cycle(action=retrieve)` | Cycle dates and details |
| `cycle(action=list_workitems)` | Items in a cycle, filterable with `pql` |
| `workitem(action=count)` | Aggregates without listing: `pql` filter plus `group_by` / `sub_group_by` |
| `workitem(action=list)` | Project items for WIP analysis, filterable with `pql` |
| `state(action=list)` | State definitions for grouping |
| `member(action=list_project)` | Team size for WIP limit calculation |
| `project(action=worklog_summary)` | Aggregated time data |
| `work_log(action=list)` | Time entries of one work item (`workitem_id` is required) |
| `workitem_activity(action=list)` | Audit trail: when an item moved to started / completed |
| `get_pql_reference` | Syntax of the `pql` filter |

## Counting with PQL and `workitem(action=count)`

`workitem(action=count)` answers "how many" in one call instead of listing every item: it takes the same `pql` filter as `list`, an optional `project_id` (omit it to count the whole workspace), and `group_by` / `sub_group_by`. The result carries `total_count` and `grouped_counts` (key to `{count}`; the key `"None"` means "no value"). Valid `group_by` keys: `state_id`, `state__group`, `priority`, `project_id`, `type_id`, `labels__id`, `assignees__id`, `issue_module__module_id`, `release_work_items__release_id`, `cycle_id`, `milestone_id`, `created_by`, `target_date`, `start_date`.

- It counts **items, not points**. Story points are summed from listed items (`point` and `estimate_point` are fetched together); use `count` for throughput, WIP, distribution and workload. Estimate-system fallback: if `point` is empty on the items and the project has an estimate system (`project_estimate(action=retrieve, project_id)`), sum the `value` of each item's `estimate_point` instead (ids and values from `project_estimate(action=list_points, project_id, estimate_id)`). Every points formula below (velocity, burndown, effort ratios) reads the same way.
- `state__group` is a grouping key only. To filter by state group in PQL write `stateGroup = "started"` or `stateGroup IN openStates()`.
- PQL allows at most 5 conditions; call `get_pql_reference` before composing anything beyond the examples in this skill. With `project_id`, `count` adds the condition `project = "<id>"` to your `pql`, so that one counts against the 5.

## Velocity Calculation

### Workflow

```
1. Get completed sprints:
   cycle(action=list, project_id=<id>, status=completed)
   → Get last 5 completed cycles (or as many as available)
   → Sprints that are already archived: cycle(action=list, project_id=<id>, archived=true)
     (status is ignored when archived=true)
   → Sort by end_date descending

2. For each cycle, calculate completed points:
   cycle(action=list_workitems, project_id=<id>, cycle_id=<cycle_id>,
         pql='stateGroup = "completed"', fields="id,point,estimate_point")
   → Sum their `point` values (follow next_cursor)
   cycle(action=list_workitems, project_id=<id>, cycle_id=<cycle_id>, fields="id,point,estimate_point")
   → Sum total planned points (all items)

   Cheap cross-check of item counts for ALL completed sprints in one call:
   workitem(action=count, project_id=<id>,
            pql='cycle IN completedCycles() AND stateGroup = "completed"',
            group_by=cycle_id)
   → grouped_counts maps each cycle_id to the number of items finished in it

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
   cycle(action=list, project_id=<id>, status=current)
   → The cycle where today is between start_date and end_date

2. Count the sprint's items per state group (one call):
   workitem(action=count, project_id=<id>,
            pql='cycle = "<cycle_id>"', group_by=state__group)
   → grouped_counts: backlog / unstarted / started / completed / cancelled

3. Get the sprint's points (counts have no points):
   cycle(action=list_workitems, project_id=<id>, cycle_id=<cycle_id>,
         fields="id,name,point,estimate_point,state")
   → Sum `point` per state group (map `state` ids with state(action=list));
     or pass pql='stateGroup = "completed"' to sum only the finished items

   State groups:
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
   member(action=list_project, project_id=<id>)
   → count members

2. Calculate WIP limit:
   wip_limit = floor(team_size × 1.5)

3. Count current WIP:
   workitem(action=count, project_id=<id>, pql='stateGroup = "started"')
   → total_count is current_wip
   → Per person: add group_by=assignees__id
   → The items themselves (for the table below):
     workitem(action=list, project_id=<id>, pql='stateGroup = "started"')

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
Items completed per sprint, one call for all completed cycles:
  workitem(action=count, project_id=<id>,
           pql='cycle IN completedCycles() AND stateGroup = "completed"',
           group_by=cycle_id)
  → grouped_counts[<cycle_id>].count is the throughput of that sprint
    (map cycle ids to names with cycle(action=list, status=completed))

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
  (dates come from workitem_activity(action=list, project_id, workitem_id) -
   the state-change entries; PQL cannot query history such as wasEver or changedTo)

Average cycle time tells you how long items typically take.
High cycle time (> sprint_length/2) suggests items are too large.
```

## Time Effort Analysis

Compare estimated effort (story points) with actual time spent (work logs) to improve estimation accuracy over time.

### Workflow

```
1. Get project-level time summary:
   project(action=worklog_summary, project_id=<id>)
   → Total logged hours, hours per member, hours per label

2. Get individual time entries for the sprint's completed items:
   work_log(action=list, project_id=<id>, workitem_id=<item_id>)
   → One call per work item (workitem_id is required); take the item ids from
     cycle(action=list_workitems, ..., pql='stateGroup = "completed"')
   → Filter entries by date range matching the sprint period
   → Group by work item (duration is in minutes)

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
