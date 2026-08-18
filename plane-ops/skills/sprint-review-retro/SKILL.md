---
name: sprint-review-retro
description: Sprint review and retrospective — completion metrics, previous retro action review, Start-Stop-Continue retro, DAKI format, 4Ls format, action item tracking, sprint close. Use when running sprint review, retrospective, closing a sprint, or reviewing previous retro action item status.
---

# Sprint Review & Retrospective

This skill covers sprint review (what was built), retrospective (how to improve), and sprint close (cleanup and transfer).

> **Page formatting:** when saving retro notes via `create_project_page`, follow the HTML rules in [`examples/references/page-formatting.md`](../examples/references/page-formatting.md). Plane pages use `description_html` — wrap every text block in `<p>`, use `<h2>`/`<h3>` for sections, and prefer `<details>` for long raw notes.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `list_cycle_work_items`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_cycles` | Find active/current cycle |
| `retrieve_cycle` | Get cycle details (dates, owner) |
| `list_cycle_work_items` | Get all work items in sprint |
| `list_archived_cycles` | Find recently completed sprints |
| `archive_cycle` | Archive completed sprint |
| `transfer_cycle_work_items` | Move incomplete items to next cycle |
| `create_cycle` | Create next sprint cycle |
| `create_work_item` | Create action items from retro |
| `create_work_item_comment` | Add retro notes to items |
| `create_project_page` | Save retro notes as a page |
| `list_labels` | Get labels for "retro-action" tag |
| `create_label` | Create "retro-action" label if needed |

## Sprint Review

### Purpose
Demo completed work, gather feedback, measure what was accomplished vs planned.

### Sprint Review Workflow

```
1. Get sprint data:
   list_cycles({ project_id })
   → Find active or most recent cycle

   retrieve_cycle({ project_id, cycle_id })
   → Get sprint name, dates, description (goal)

2. Get sprint items:
   list_cycle_work_items({ project_id, cycle_id })
   → Categorize by state group:
     completed  → items in "completed" state group
     in_progress → items in "started" state group
     not_started → items in "unstarted" or "backlog" state group

3. Calculate metrics:
   total_items      = count of all sprint items
   completed_items  = count in completed state
   total_points     = sum of all points
   completed_points = sum of completed items' points
   completion_rate  = completed_points / total_points × 100
   item_completion  = completed_items / total_items × 100

4. Generate review report:
   ┌─────────────────────────────────────────┐
   │ SPRINT REVIEW: Sprint 12                │
   │ Goal: "Users can manage their profile"  │
   │ Period: Mar 10 - Mar 14                 │
   ├─────────────────────────────────────────┤
   │ Completion: 34/40 points (85%)          │
   │ Items: 8/10 completed                   │
   ├─────────────────────────────────────────┤
   │ COMPLETED:                              │
   │  [DONE] MP-42 Edit profile name (5 pts)  │
   │  [DONE] MP-43 Upload avatar (3 pts)     │
   │  [DONE] MP-44 Change email (5 pts)      │
   │  ...                                    │
   ├─────────────────────────────────────────┤
   │ NOT COMPLETED:                          │
   │  [INCOMPLETE] MP-48 Delete account (5 pts) — In Progress │
   │  [INCOMPLETE] MP-49 Export data (3 pts) — Not Started   │
   └─────────────────────────────────────────┘
```

## Retrospective Formats

### Format 1: Start-Stop-Continue

```
START — What should we start doing?
  (New practices, tools, habits)

STOP — What should we stop doing?
  (Wasteful practices, blockers, bad habits)

CONTINUE — What should we continue doing?
  (What's working well, keep it up)
```

### Format 2: DAKI

```
DROP — What's not working and should be dropped?
ADD — What new practices should we adopt?
KEEP — What's working well?
IMPROVE — What can we make better?
```

### Format 3: 4Ls

```
LIKED — What did the team enjoy?
LEARNED — What did the team learn?
LACKED — What was missing?
LONGED FOR — What do we wish we had?
```

### Running a Retrospective

```
1. Review previous retro actions:
   list_labels({ project_id })
   → Find label with name "retro-action" → get label_id

   list_work_items({ project_id })
   → Filter items with "retro-action" label_id
   → Check which are completed vs still open
   → Present status:
     "[DONE] Every PR reviewed within 4 hours — completed"
     "[OPEN] Set up staging deploy pipeline — still in progress"
   → Discuss: what helped? what blocked completion?
   → This creates accountability and shows the team that retro actions matter

2. Present sprint metrics (from review above)

3. Choose a format (Start-Stop-Continue is default for startups)

4. Collect input from team:
   "What should we START doing?"
   "What should we STOP doing?"
   "What should we CONTINUE doing?"

5. Identify top 2-3 action items (not more!)
   - Each must be specific, measurable, and assignable
   - SMART: Specific, Measurable, Achievable, Relevant, Time-boxed

6. Create action items in Plane:
   For each action:
   create_work_item({
     project_id: "<id>",
     name: "[RETRO] <action item description>",
     description_html: "<p>From Sprint N retrospective. <details></p>",
     priority: "high",
     labels: ["<retro-action-label-id>"],
     assignees: ["<owner_id>"],
     target_date: "<next_sprint_end_date>"
   })

7. Save retro notes:
   create_project_page({
     project_id: "<id>",
     name: "Retro — Sprint N (YYYY-MM-DD)",
     description_html: "<h2>Sprint Metrics</h2>...<h2>Start</h2>...<h2>Stop</h2>...<h2>Continue</h2>...<h2>Action Items</h2>..."
   })
```

## Sprint Close Workflow

### Step-by-step

```
1. Complete the sprint review (above)

2. Handle incomplete items:
   Option A: Transfer to next sprint
     - Create next cycle first (if not exists):
       create_cycle({
         project_id, name, owned_by, start_date, end_date
       })
     - Transfer:
       transfer_cycle_work_items({
         project_id,
         cycle_id: "<current_cycle_id>",
         new_cycle_id: "<next_cycle_id>"
       })

   Option B: Move back to backlog
     - Remove from cycle (items return to backlog)
     - Don't carry over items that weren't started — reprioritize

3. Archive the sprint:
   archive_cycle({
     project_id: "<id>",
     cycle_id: "<current_cycle_id>"
   })

4. Record velocity:
   Note completed_points for velocity tracking
   (Use velocity-metrics skill for historical analysis)
```

### Decision: Transfer vs Return to Backlog

| Situation | Action |
|-----------|--------|
| Item was in-progress, nearly done | Transfer to next sprint |
| Item was not started | Return to backlog, reprioritize |
| Item was blocked all sprint | Return to backlog, resolve blocker first |
| Item scope changed significantly | Return to backlog, re-estimate |

## Action Items Best Practices

1. **Limit to 2-3 actions per retro** — more won't get done
2. **Assign each to a specific person** — "the team" is nobody
3. **Set a deadline** — by end of next sprint
4. **Track completion** — review at start of next retro
5. **Make them specific** — "Improve code reviews" → "Every PR must have review within 4 hours"
6. **Label them** — use "retro-action" label for easy filtering

## Retro Health Metrics

Track these across sprints:

| Metric | Healthy | Warning |
|--------|---------|---------|
| Sprint completion rate | ≥ 80% | < 70% |
| Action items completed | ≥ 80% | < 50% |
| Velocity trend | Stable or improving | Declining 3+ sprints |
| Scope changes mid-sprint | ≤ 10% | > 20% |

## Best Practices

1. **Review before retro** — discuss what was built, then how to improve
2. **Time-box the retro** — 45 min for 1-week sprint, 60 min for 2-week
3. **Everyone speaks** — go around the room, no silent members
4. **Focus on process, not people** — "the deploy process failed" not "John broke the deploy"
5. **Celebrate wins** — acknowledge completed items and improvements
6. **Follow through** — action items without follow-up erode trust in the process
