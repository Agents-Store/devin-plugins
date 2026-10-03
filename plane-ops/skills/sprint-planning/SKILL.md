---
name: sprint-planning
description: Sprint planning — capacity calculation, sprint goal setting, work item selection, cycle creation. Use when planning a new sprint, calculating capacity, or selecting items for a sprint.
---

# Sprint Planning

This skill covers the complete sprint planning ceremony — from capacity calculation to sprint creation in Plane.

## Tool Name Resolution

Plane MCP exposes one tool per resource (`project`, `member`, `cycle`, `workitem`, ...) and the operation goes into the `action` parameter: `cycle(action=create, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix.

## Available Tools

| Call | Description |
|------|-------------|
| `project(action=list)` | List projects in the workspace (paginated: follow `next_cursor`) |
| `member(action=list_project)` | Team members for the capacity calculation |
| `member(action=me)` | Current user (for the `owned_by` field) |
| `cycle(action=list)` | List sprints: `status=current\|upcoming\|completed\|draft\|incomplete`, or `archived=true` |
| `cycle(action=list_workitems)` | Work items of one sprint, filterable with `pql` |
| `cycle(action=create)` / `cycle(action=update)` | Create or change a sprint (`owned_by` is required on create) |
| `cycle(action=manage_workitems)` | Add or remove work items in bulk: `add_ids`, `remove_ids` |
| `workitem(action=list)` | Backlog items for selection, filterable with `pql` |
| `workitem(action=count)` | Aggregates without listing: `group_by`, `pql` |
| `state(action=list)` | Project states (names to UUIDs, state groups) |
| `get_pql_reference` | Syntax of the `pql` filter (call it before composing a complex query) |

## Sprint Planning Ceremony (Step-by-Step)

### Step 1: Resolve Project Context

```
1. project(action=list)
   → Find project by name, get project_id (follow next_cursor if the workspace has many projects)

2. member(action=list_project, project_id=<project_id>)
   → Get team roster, count team_size

3. state(action=list, project_id=<project_id>)
   → Map state names to UUIDs. State GROUPS need no UUIDs in PQL
     (stateGroup = "started"); a single state does (state = "<uuid>")

4. member(action=me)
   → Get current user UUID (for cycle owned_by)
```

### Step 2: Calculate Historical Velocity

```
1. cycle(action=list, project_id=<project_id>, status=completed)
   → Last 3-5 completed sprints, newest end_date first
   → Sprints already archived: cycle(action=list, project_id=<project_id>, archived=true)
     (status is ignored when archived=true)

2. For each completed cycle:
   cycle(action=list_workitems, project_id=<project_id>, cycle_id=<cycle_id>,
         pql='stateGroup = "completed"', fields="id,name,point,estimate_point")
   → Sum `point` of the results → completed_points
   cycle(action=list_workitems, project_id=<project_id>, cycle_id=<cycle_id>,
         fields="id,point,estimate_point")
   → Sum `point` → total_planned_points (follow next_cursor on both)
   → Estimate-system fallback: if `point` is empty on the items and the project has an estimate system (`project_estimate(action=retrieve, project_id)`), sum the `value` of each item's `estimate_point` instead (ids and values from `project_estimate(action=list_points, project_id, estimate_id)`).
   Record: cycle_name, completed_points, total_planned_points

3. Calculate:
   average_velocity = sum(completed_points) / number_of_sprints
   completion_rate = sum(completed_points) / sum(total_planned_points)
```

Points are summed from the listed items: `workitem(action=count)` counts items, not points, so use it for throughput (items finished per sprint) and the `point` sum for velocity.

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
1. workitem(action=list, project_id=<project_id>,
            pql='stateGroup IN ("backlog","unstarted")',
            fields="id,name,point,estimate_point,priority,assignees,sequence_id", per_page=100)
   → Backlog candidates (follow next_cursor). PQL has no estimate field, so
     keep only items where `point` is not null on the client side.
   → Quick sizing before listing: workitem(action=count, project_id=<project_id>,
     pql='stateGroup IN ("backlog","unstarted")', group_by=priority)

2. Sort by priority:
   urgent (1st) → high (2nd) → medium (3rd) → low (4th)

3. For each candidate item, validate Definition of Ready:
   [OK] Has story points assigned (point field is set)
   [OK] Has description with acceptance criteria
   [OK] No "blocked_by" relations: workitem_relation(action=list, project_id, workitem_id)
   [OK] Points ≤ 8 (if > 8, flag for decomposition)
   [OK] Has assignee or can be assigned (PQL: hasNoAssignee() finds the gaps)

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

- `cycle(action=archive)` ends a still-running cycle first instead of failing, which cuts the sprint short: complete the sprint and move unfinished items before archiving (see `/close-sprint`). To remove an active cycle entirely, use `cycle(action=delete)` directly, after confirmation.
- `cycle(action=manage_workitems)` takes `add_ids` (an array of work item UUIDs), returns nothing, and is read back with `cycle(action=list_workitems)`. If an MCP bridge rejects the array, see the Known Limitations section of the `work-items` skill.

### Step 5: Create the Sprint

```
1. cycle(action=create,
         project_id=<project_id>,
         name="Sprint N — <sprint goal summary>",
         owned_by=<current_user_id>,
         description="<sprint goal>",
         start_date="YYYY-MM-DD",
         end_date="YYYY-MM-DD")
   → Get cycle_id

2. cycle(action=manage_workitems,
         project_id=<project_id>,
         cycle_id=<cycle_id>,
         add_ids=["<item1_id>", "<item2_id>", ...])

3. Confirm sprint is created:
   cycle(action=list_workitems, project_id=<project_id>, cycle_id=<cycle_id>)
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
| Dependencies identified | `workitem_relation(action=list)` shows no unresolved `blocked_by` |
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
