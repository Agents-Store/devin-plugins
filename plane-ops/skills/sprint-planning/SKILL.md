---
name: sprint-planning
description: Sprint planning — capacity calculation, sprint goal setting, work item selection, cycle creation. Use when planning a new sprint, calculating capacity, or selecting items for a sprint.
---

# Sprint Planning

This skill covers the complete sprint planning ceremony — from capacity calculation to sprint creation in Plane.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `create_cycle`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_projects` | List all projects in workspace |
| `get_project_members` | Get team members for capacity calculation |
| `list_cycles` | List current/active cycles (sprints) |
| `list_archived_cycles` | List completed sprints for velocity data |
| `list_cycle_work_items` | Get work items in a specific cycle |
| `create_cycle` | Create a new sprint cycle |
| `update_cycle` | Update sprint details |
| `add_work_items_to_cycle` | Add items to sprint (bulk) |
| `list_work_items` | List backlog items for selection |
| `list_states` | Get project states for filtering |
| `get_me` | Get current user info (for owned_by field) |

## Sprint Planning Ceremony (Step-by-Step)

### Step 1: Resolve Project Context

```
1. list_projects()
   → Find project by name, get project_id

2. get_project_members({ project_id })
   → Get team roster, count team_size

3. list_states({ project_id })
   → Map state names to UUIDs (needed for filtering)

4. get_me()
   → Get current user UUID (for cycle owned_by)
```

### Step 2: Calculate Historical Velocity

```
1. list_archived_cycles({ project_id })
   → Get last 3-5 completed sprints

2. For each archived cycle:
   list_cycle_work_items({ project_id, cycle_id })
   → Sum story points of items in "completed" state group
   → Record: cycle_name, completed_points, total_planned_points

3. Calculate:
   average_velocity = sum(completed_points) / number_of_sprints
   completion_rate = sum(completed_points) / sum(total_planned_points)
```

### Step 3: Calculate Capacity

**With velocity history (preferred):**
```
capacity = average_velocity × 0.85  (15% buffer)
```

**Without history (first sprint):**
```
available_days = team_size × sprint_days
effective_days = available_days × 0.7  (focus factor for startups)
capacity = effective_days × 0.85       (15% buffer)
≈ 1 story point per effective person-day
```

**Adjustments:**
- Subtract PTO: reduce capacity by (pto_days / total_person_days)
- First sprint: use 60% of calculated capacity (learning curve)
- Holiday weeks: reduce proportionally

### Step 4: Select Work Items

```
1. list_work_items({ project_id })
   → Filter: items where state group is "backlog" or "unstarted"
   → Filter: items where point is not null (estimated items only)

2. Sort by priority:
   urgent (1st) → high (2nd) → medium (3rd) → low (4th)

3. For each candidate item, validate Definition of Ready:
   [OK] Has story points assigned (point field is set)
   [OK] Has description with acceptance criteria
   [OK] No "blocked_by" relations (check list_work_item_relations if needed)
   [OK] Points ≤ 8 (if > 8, flag for decomposition)
   [OK] Has assignee or can be assigned

4. Add items to sprint until:
   sum(selected_points) ≤ capacity
   Leave at least 15% capacity unplanned

5. Present selection to user:
   | # | Item | Priority | Points | Assignee |
   |---|------|----------|--------|----------|
   | 1 | ... | high | 5 | @name |
   Total: X/Y points (Z% of capacity)
```

### Caveats

- `archive_cycle` typically rejects active cycles (HTTP 400). Archive is only allowed after the cycle is completed or its `end_date` is in the past. To remove an active cycle, use `delete_cycle` directly.
- `add_work_items_to_cycle` uses `issue_ids` (plural, array). Some MCP bridges have issues serializing list parameters — see the Known Limitations section in the `work-items` skill for workarounds.

### Step 5: Create the Sprint

```
1. create_cycle({
     project_id: "<project_id>",
     name: "Sprint N — <sprint goal summary>",
     owned_by: "<current_user_id>",
     description: "<sprint goal>",
     start_date: "YYYY-MM-DD",
     end_date: "YYYY-MM-DD"
   })
   → Get cycle_id

2. add_work_items_to_cycle({
     project_id: "<project_id>",
     cycle_id: "<cycle_id>",
     issue_ids: ["<item1_id>", "<item2_id>", ...]
   })

3. Confirm sprint is created:
   list_cycle_work_items({ project_id, cycle_id })
   → Verify all items are in the sprint
```

## Sprint Goal Template

A good sprint goal follows this format:

> "By end of this sprint, **[users/customers]** can **[capability/feature]** so that **[business value]**"

**Examples:**
- "By end of this sprint, users can sign up and log in so that we can start onboarding beta testers"
- "By end of this sprint, admins can export reports so that stakeholders get weekly updates"
- "By end of this sprint, the API handles 1000 req/s so that we're ready for launch"

## Definition of Ready (DoR) Checklist

Before a work item enters a sprint:

| Criterion | Plane Validation |
|-----------|-----------------|
| Clear title and description | `name` is descriptive, `description_html` has acceptance criteria |
| Estimated | `point` field is set (1-8 range) |
| Dependencies identified | `list_work_item_relations` shows no unresolved `blocked_by` |
| No unresolved blockers | No items in blocking state |
| Small enough | `point` ≤ 8 (flag > 8 for decomposition) |
| Assignee identified | `assignees` field is set or can be set |

## Sprint Duration Guide

| Team Size | Duration | Planning Time | Daily Standup |
|-----------|----------|--------------|---------------|
| 1-3 devs | 1 week | 1 hour | 10 min |
| 4-7 devs | 1-2 weeks | 2 hours | 15 min |
| 8+ devs | 2 weeks | 3 hours | 15 min |

## Common Issues

- **Overcommitment:** If completion rate < 70% for 2+ sprints, reduce capacity by 20%
- **Undercommitment:** If team finishes early consistently, increase capacity by 10%
- **Unestimated items:** Never add unestimated items to sprint — estimate first
- **Large items (> 8 points):** Use task-decomposition skill to split before adding
- **No sprint goal:** Always set a goal — it guides daily decisions on scope

## Best Practices

1. **Commit to a sprint goal, not just items** — the goal guides trade-offs when scope changes
2. **Leave 15% buffer** — unplanned work always appears, especially in startups
3. **Don't add unestimated items** — estimate first using the estimation skill
4. **Plan as a team** — everyone should understand and agree to the sprint commitment
