---
name: backlog-management
description: Backlog management — MoSCoW prioritization, WSJF scoring, value-effort analysis, backlog health monitoring, grooming workflows. Use when prioritizing backlog, grooming items, or assessing backlog health.
---

# Backlog Management

This skill covers backlog prioritization, grooming, and health monitoring using established Agile frameworks — MoSCoW, WSJF, Value vs Effort analysis.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `list_work_items`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_work_items` | List all backlog items with pagination |
| `update_work_item` | Update priority, labels, estimates |
| `search_work_items` | Search items by text |
| `list_labels` | Get existing labels |
| `create_label` | Create prioritization labels |
| `list_states` | Get state definitions |
| `list_work_item_relations` | Check blocking dependencies |
| `list_work_item_activities` | Check item freshness |

## MoSCoW Prioritization

Map MoSCoW categories directly to Plane priority values:

| MoSCoW | Plane Priority | Description |
|--------|---------------|-------------|
| **Must Have** | `urgent` or `high` | Critical for current release, non-negotiable |
| **Should Have** | `medium` | Important but can be deferred if needed |
| **Could Have** | `low` | Nice-to-have, adds value if time permits |
| **Won't Have** | `none` | Explicitly out of scope for now |

### MoSCoW Workflow

```
1. list_work_items({ project_id })
   → Get all backlog items

2. For each item, classify:
   - Does the product fail without this? → Must Have (urgent/high)
   - Is it important but not critical? → Should Have (medium)
   - Would users appreciate it but won't miss it? → Could Have (low)
   - Is it out of scope for now? → Won't Have (none)

3. Update priorities:
   update_work_item({
     project_id: "<id>",
     work_item_id: "<item_id>",
     priority: "high"
   })

4. Target distribution for a healthy backlog:
   Must Have:   ~60% of sprint capacity
   Should Have: ~20% of sprint capacity
   Could Have:  ~20% of sprint capacity (buffer items)
```

## WSJF (Weighted Shortest Job First)

**Formula:** `WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size`

Higher WSJF = Higher priority (do first).

### WSJF Scoring Guide

| Factor | 1 (Low) | 5 (Medium) | 10 (High) |
|--------|---------|-----------|------------|
| **Business Value** | Minor improvement | Important feature | Revenue/growth critical |
| **Time Criticality** | No deadline | Needed soon | Urgent deadline |
| **Risk Reduction** | No risk addressed | Moderate risk | Critical risk mitigated |
| **Job Size** | XL (13+ pts) | M (3-5 pts) | S (1-2 pts) |

### WSJF Workflow

```
1. list_work_items({ project_id })
   → Get backlog items with estimates

2. For each item, score (with user input):
   Business Value:    [1-10]
   Time Criticality:  [1-10]
   Risk Reduction:    [1-10]
   Job Size (points): use existing story points

3. Calculate WSJF:
   WSJF = (BV + TC + RR) / points

4. Sort by WSJF descending

5. Update priorities:
   Top 25%  → priority: "urgent"
   25-50%   → priority: "high"
   50-75%   → priority: "medium"
   Bottom 25% → priority: "low"

6. Present ranked list:
   | Rank | Item | BV | TC | RR | Size | WSJF | Priority |
   |------|------|----|----|-----|------|------|----------|
   | 1 | Quick win feature | 8 | 7 | 5 | 2 | 10.0 | urgent |
   | 2 | Critical fix | 9 | 9 | 8 | 5 | 5.2 | high |
```

## Value vs Effort Matrix

Plot items on a 2x2 grid:

```
                    HIGH VALUE
                        │
    ┌───────────────────┼───────────────────┐
    │   Quick Wins      │   Big Bets        │
    │   (Do First)      │   (Plan Carefully) │
    │   priority: urgent│   priority: high   │
LOW ├───────────────────┼───────────────────┤ HIGH
EFF │   Fill-ins        │   Money Pit       │  EFFORT
    │   (Do If Time)    │   (Avoid/Defer)   │
    │   priority: low   │   priority: none   │
    └───────────────────┼───────────────────┘
                    LOW VALUE
```

### Value-Effort Workflow

```
1. For each backlog item:
   Value:  rate 1-10 (user impact, revenue, strategic)
   Effort: use story points

2. Classify:
   High Value (≥6) + Low Effort (≤5 pts)  → Quick Win (urgent)
   High Value (≥6) + High Effort (>5 pts)  → Big Bet (high)
   Low Value (<6) + Low Effort (≤5 pts)    → Fill-in (low)
   Low Value (<6) + High Effort (>5 pts)   → Money Pit (none)
```

## Backlog Health Metrics

### Health Check Workflow

```
1. list_work_items({ project_id, per_page: 100 })
   → Get all backlog items

2. Calculate metrics:
   total_items         = count of all items in backlog/unstarted states
   unestimated         = count where point is null
   unassigned          = count where assignees is empty
   no_priority         = count where priority is "none" or null
   no_description      = count where description_html is empty/minimal
   large_items         = count where point > 8

3. Health score:
   ready_items = items with: point set + priority set + description exists
   health_score = (ready_items / total_items) × 100

4. Present report:
   ┌─────────────────────────────────────┐
   │ BACKLOG HEALTH REPORT               │
   ├─────────────────────────────────────┤
   │ Total items:      45                │
   │ Ready for sprint: 28 (62%)          │
   │ Unestimated:      12 (27%) [!]       │
   │ No priority:       8 (18%) [!]       │
   │ No assignee:      15 (33%)          │
   │ Oversized (>8pt):  3 (7%) [!]        │
   │ No description:    5 (11%) [!]       │
   ├─────────────────────────────────────┤
   │ Health Score: 62% — Needs Grooming  │
   └─────────────────────────────────────┘

   Recommendations:
   1. Estimate 12 unestimated items (use /estimate)
   2. Split 3 oversized items (use /decompose)
   3. Set priorities for 8 items (use /wsjf-prioritize)
```

### Health Score Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 90-100% | Healthy | Ready for sprint planning |
| 70-89% | Good | Light grooming needed |
| 50-69% | Needs Work | Dedicate a grooming session |
| < 50% | Unhealthy | Urgent grooming required |

## Backlog Grooming Workflow

### Full Grooming Session

```
1. Review from top of backlog (highest priority first)

2. For each item:
   a. Is this still relevant? → If not, move to cancelled state or delete
   b. Is it clear enough? → If not, add description/acceptance criteria
   c. Is it estimated? → If not, estimate (see estimation skill)
   d. Is it the right size? → If > 8 points, decompose
   e. Is priority correct? → Adjust if business context changed
   f. Are dependencies identified? → Check/create relations

3. After grooming, re-check health metrics
```

## Recommended Labels for Backlog Management

Use the labels defined in the **project-setup** skill. Key labels for backlog triage:

- `ready` — item meets Definition of Ready, can enter sprint
- `needs-refinement` — item needs more detail before sprint
- `blocked` — item has unresolved dependency
- `quick-win` — low effort, high value (see Value vs Effort matrix)

To create these labels, refer to the project-setup skill for full label definitions with colors.

## Best Practices

1. **Groom regularly** — mid-sprint for 30-60 minutes, not before sprint planning
2. **Top-down review** — start with highest priority items
3. **Keep backlog lean** — if an item hasn't moved in 3+ sprints, archive or delete it
4. **One prioritization method** — pick MoSCoW or WSJF, don't mix
5. **Involve the team** — grooming is a team activity, not just PM
6. **Limit backlog size** — aim for 2-3 sprints worth of refined items
7. **Use labels for triage** — "ready", "needs-refinement", "blocked" for at-a-glance status
