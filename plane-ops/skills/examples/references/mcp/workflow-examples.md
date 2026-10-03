# Multi-Step Workflow Examples

Complete multi-tool workflows for common Agile operations in Plane. Calls are written `resource(action=..., ...)`; resolve the real tool names (`mcp__<server>__<resource>`) with the `connector-bootstrap` skill. Filters use PQL (`pql=`); counts use `workitem(action=count, ...)`.

## 1. Complete Sprint Planning Ceremony

```
Step 1: Gather context
  project(action=list) → find project_id
  member(action=me) → current user_id for owned_by
  member(action=list_project, project_id) → team roster (count for capacity)
  state(action=list, project_id) → map state names to UUIDs

Step 2: Calculate velocity
  cycle(action=list, project_id, status=completed) → last 5 sprints
  For each cycle:
    cycle(action=list_workitems, project_id, cycle_id,
          pql='stateGroup = "completed"', fields="id,point,estimate_point")
    → sum `point` of the results
  avg_velocity = total_completed / num_sprints

Step 3: Get backlog candidates
  workitem(action=list, project_id,
           pql='stateGroup IN ("backlog","unstarted")',
           fields="id,name,point,estimate_point,priority,assignees")
  → keep items where point is set (PQL has no estimate field)
  → sort by priority

Step 4: Select items up to capacity
  capacity = avg_velocity × 0.85 (15% buffer)
  selected = []
  For each candidate (by priority):
    if sum(selected.points) + item.point <= capacity:
      selected.push(item)

Step 5: Create sprint
  cycle(action=create, project_id, name="Sprint N", owned_by=user_id,
        start_date="YYYY-MM-DD", end_date="YYYY-MM-DD",
        description="Sprint goal here") → cycle_id

Step 6: Add items to sprint
  cycle(action=manage_workitems, project_id, cycle_id,
        add_ids=selected.map(i => i.id))

Step 7: Verify
  cycle(action=list_workitems, project_id, cycle_id)
  → confirm all items are in the sprint

Step 8: Present summary
  Sprint: [name]
  Goal: [description]
  Capacity: [velocity] pts | Committed: [sum] pts ([%] utilization)
  Items: [count]
  | # | Item | Priority | Points | Assignee |
```

## 2. Backlog Grooming Session

```
Step 1: Get current backlog
  workitem(action=count, project_id, pql='stateGroup IN ("backlog","unstarted")')
  → total_count first, then page through the items:
  workitem(action=list, project_id, pql='stateGroup IN ("backlog","unstarted")', per_page=100)

Step 2: Health check
  Counts by PQL: total, no_priority (priority = "none"), unassigned (hasNoAssignee())
  From the listed items: unestimated, no_description, oversized (>8 pts)
  Health score = ready_items / total × 100

Step 3: Review top items (by priority)
  For each item:
    a. Check description quality
    b. Check if estimated
    c. Check if size ≤ 8
    d. Check dependencies

Step 4: Fix issues
  Unestimated → workitem(action=update, project_id, workitem_id, point=N)
  Oversized → decompose using task-decomposition skill
  No priority → workitem(action=update, ..., priority="medium")
  No description → workitem(action=update, ..., description_html="...")

Step 5: Label groomed items
  workitem(action=manage_label, project_id, workitem_id, add_label_id="ready-label-id")

Step 6: Re-check health score
  Report improvement: "Health improved from 45% to 78%"
```

## 3. Sprint Close and Retrospective

```
Step 1: Get sprint data
  cycle(action=list, project_id, status=current) → find active cycle
  cycle(action=list_workitems, project_id, cycle_id)
  workitem(action=count, project_id, pql='cycle = "<cycle_id>"', group_by=state__group)

Step 2: Categorize items
  completed = items where state group = "completed"
  incomplete = items where state group != "completed"
  Calculate completion_rate = completed_points / total_points

Step 3: Present review
  Show completed items, incomplete items, metrics

Step 4: Handle incomplete items
  Option B first — Return to backlog (before the transfer):
    cycle(action=manage_workitems, project_id, cycle_id, remove_ids=[<ids that go back>])

  Option A — Transfer the rest to the next sprint:
    cycle(action=create, ... next sprint ...) → next_cycle_id
    cycle(action=complete, project_id, cycle_id)
    cycle(action=transfer_workitems, project_id, cycle_id, new_cycle_id=next_cycle_id)

Step 5: Run retrospective
  Present retro template (Start-Stop-Continue)
  Collect team input

Step 6: Create action items
  For each action:
    workitem(action=create,
             project_id, name="[RETRO] action description",
             priority="high", labels=["retro-action-label-id"])

Step 7: Save retro notes
  page(action=create,
       project_id, name="Retro — Sprint N",
       description_html="<retro notes in HTML>")

Step 8: Archive sprint
  cycle(action=archive, project_id, cycle_id)
```

## 4. Daily Standup Generation

```
Step 1: Find active sprint
  cycle(action=list, project_id, status=current)
  → cycle where today between start_date and end_date

Step 2: Get sprint items
  cycle(action=list_workitems, project_id, cycle_id)
  workitem(action=count, project_id, pql='cycle = "<cycle_id>"', group_by=state__group)

Step 3: Get team
  member(action=list_project, project_id)

Step 4: Generate per-person summary
  Group items by assignee
  For each person:
    completed = items in "completed" state
    in_progress = items in "started" state
    not_started = items in "unstarted" state

Step 5: Detect blockers
  Stalled: cycle(action=list_workitems, ..., pql='stateGroup = "started" AND updatedAt < daysAgo(2)')
  For in-progress items:
    workitem_relation(action=list, project_id, workitem_id)
    → flag items with "blocked_by" relations

Step 6: Calculate sprint progress
  total_points, completed_points, remaining_points
  elapsed_days, remaining_days
  pace = completed_points / elapsed_days
  needed_pace = remaining_points / remaining_days
```

## 5. Batch Estimation Session

```
Step 1: Get candidate items
  workitem(action=list, project_id, pql='stateGroup IN ("backlog","unstarted")',
           fields="id,name,point,estimate_point,priority")
  → keep items where point is null or 0

Step 2: Find reference stories
  workitem(action=search, query="well-known completed item")
  → pick 2-3 as calibration points

Step 3: Estimate each item
  For each unestimated item:
    a. Read name and description
    b. Compare to reference stories
    c. Assess: components touched, unknowns, dependencies
    d. Suggest estimate with reasoning
    e. On confirmation:
       workitem(action=update, project_id, workitem_id, point=N)

Step 4: Flag oversized items
  Items estimated > 8 points → recommend decomposition

Step 5: Summary
  Total estimated: N items, M points
  Flagged for splitting: K items
```

## 6. Release Notes from a Plane Release

```
Step 1: Find the release
  release(action=list) → pick release_id (status: unreleased | released | cancelled)

Step 2: Collect what shipped
  release(action=list_workitems, release_id) → follow next_cursor
  release(action=get_changelog, release_id) → keep any hand-written notes

Step 3: Render
  Group items into New Features / Improvements / Bug Fixes, fill the release-notes template

Step 4: Publish
  page(action=create, project_id, name="Release vX.Y — YYYY-MM-DD", description_html="<…>")
  release(action=update_changelog, release_id, description_html="<…>")
```
