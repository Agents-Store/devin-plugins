# Multi-Step Workflow Examples

Complete multi-tool workflows for common Agile operations in Plane.

## 1. Complete Sprint Planning Ceremony

```
Step 1: Gather context
  list_projects() → find project_id
  get_me() → get current user_id for owned_by
  get_project_members({ project_id }) → team roster (count for capacity)
  list_states({ project_id }) → map state names to UUIDs

Step 2: Calculate velocity
  list_archived_cycles({ project_id }) → get last 5 sprints
  For each cycle:
    list_cycle_work_items({ project_id, cycle_id })
    → sum points of items in "completed" state group
  avg_velocity = total_completed / num_sprints

Step 3: Get backlog candidates
  list_work_items({ project_id, order_by: "-priority" })
  → filter: state group = "backlog" or "unstarted"
  → filter: point is set (estimated items only)
  → sort by priority

Step 4: Select items up to capacity
  capacity = avg_velocity × 0.85 (15% buffer)
  selected = []
  For each candidate (by priority):
    if sum(selected.points) + item.point <= capacity:
      selected.push(item)

Step 5: Create sprint
  create_cycle({
    project_id, name: "Sprint N", owned_by: user_id,
    start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD",
    description: "Sprint goal here"
  }) → cycle_id

Step 6: Add items to sprint
  add_work_items_to_cycle({
    project_id, cycle_id,
    issue_ids: selected.map(i => i.id)
  })

Step 7: Verify
  list_cycle_work_items({ project_id, cycle_id })
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
  list_work_items({ project_id, per_page: 100 })
  → filter state group = "backlog" or "unstarted"

Step 2: Health check
  Count: total, unestimated, no_priority, no_description, oversized (>8 pts)
  Health score = ready_items / total × 100

Step 3: Review top items (by priority)
  For each item:
    a. Check description quality
    b. Check if estimated
    c. Check if size ≤ 8
    d. Check dependencies

Step 4: Fix issues
  Unestimated → update_work_item({ point: N })
  Oversized → decompose using task-decomposition skill
  No priority → update_work_item({ priority: "medium" })
  No description → update_work_item({ description_html: "..." })

Step 5: Label groomed items
  update_work_item({ labels: ["ready-label-id"] })

Step 6: Re-check health score
  Report improvement: "Health improved from 45% to 78%"
```

## 3. Sprint Close and Retrospective

```
Step 1: Get sprint data
  list_cycles({ project_id }) → find active cycle
  list_cycle_work_items({ project_id, cycle_id })

Step 2: Categorize items
  completed = items where state group = "completed"
  incomplete = items where state group != "completed"
  Calculate completion_rate = completed_points / total_points

Step 3: Present review
  Show completed items, incomplete items, metrics

Step 4: Handle incomplete items
  Option A — Transfer to next sprint:
    create_cycle({ ... next sprint ... }) → next_cycle_id
    transfer_cycle_work_items({ project_id, cycle_id, new_cycle_id: next_cycle_id })

  Option B — Return to backlog:
    For each incomplete item:
      remove_work_item_from_cycle({ project_id, cycle_id, work_item_id })

Step 5: Run retrospective
  Present retro template (Start-Stop-Continue)
  Collect team input

Step 6: Create action items
  For each action:
    create_work_item({
      project_id, name: "[RETRO] action description",
      priority: "high", labels: ["retro-action-label-id"]
    })

Step 7: Save retro notes
  create_project_page({
    project_id, name: "Retro — Sprint N",
    description_html: "<retro notes in HTML>"
  })

Step 8: Archive sprint
  archive_cycle({ project_id, cycle_id })
```

## 4. Daily Standup Generation

```
Step 1: Find active sprint
  list_cycles({ project_id })
  → cycle where today between start_date and end_date

Step 2: Get sprint items
  list_cycle_work_items({ project_id, cycle_id })

Step 3: Get team
  get_project_members({ project_id })

Step 4: Generate per-person summary
  Group items by assignee
  For each person:
    completed = items in "completed" state
    in_progress = items in "started" state
    not_started = items in "unstarted" state

Step 5: Detect blockers
  For in-progress items:
    list_work_item_relations({ project_id, work_item_id })
    → flag items with "blocked_by" relations

Step 6: Calculate sprint progress
  total_points, completed_points, remaining_points
  elapsed_days, remaining_days
  pace = completed_points / elapsed_days
  needed_pace = remaining_points / remaining_days
```

## 5. Batch Estimation Session

```
Step 1: Get unestimated items
  list_work_items({ project_id })
  → filter: point is null or 0

Step 2: Find reference stories
  search_work_items({ query: "well-known completed item" })
  → pick 2-3 as calibration points

Step 3: Estimate each item
  For each unestimated item:
    a. Read name and description
    b. Compare to reference stories
    c. Assess: components touched, unknowns, dependencies
    d. Suggest estimate with reasoning
    e. On confirmation:
       update_work_item({ project_id, work_item_id, point: N })

Step 4: Flag oversized items
  Items estimated > 8 points → recommend decomposition

Step 5: Summary
  Total estimated: N items, M points
  Flagged for splitting: K items
```
