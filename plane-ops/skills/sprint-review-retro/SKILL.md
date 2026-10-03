---
name: sprint-review-retro
description: Sprint review and retrospective — completion metrics, previous retro action review, Start-Stop-Continue retro, DAKI format, 4Ls format, action item tracking, sprint close. Use when running sprint review, retrospective, closing a sprint, or reviewing previous retro action item status.
---

# Sprint Review & Retrospective

This skill covers sprint review (what was built), retrospective (how to improve), and sprint close (cleanup and transfer).

> **Page formatting:** when saving retro notes via `page(action=create)`, follow the HTML rules in [`examples/references/page-formatting.md`](../examples/references/page-formatting.md). Plane pages use `description_html` — wrap every text block in `<p>`, use `<h2>`/`<h3>` for sections, and prefer `<details>` for long raw notes.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `cycle(action=list, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix.

## Available Tools

| Call | Description |
|------|-------------|
| `cycle(action=list)` | Find the active (`status=current`) or recently completed (`status=completed`) cycle; `archived=true` lists archived ones |
| `cycle(action=retrieve)` | Get cycle details (dates, owner) |
| `cycle(action=list_workitems)` | Get all work items in sprint (`pql` filter) |
| `cycle(action=complete)` | End the sprint: sets `end_date` to today |
| `cycle(action=transfer_workitems)` | Move the unfinished items of a finished cycle to the next cycle (`new_cycle_id`) |
| `cycle(action=manage_workitems)` | Take items out of the cycle (`remove_ids`) so they return to the backlog |
| `cycle(action=archive)` | Archive the sprint |
| `cycle(action=create)` | Create next sprint cycle |
| `workitem(action=count)` | Sprint totals per state group in one call |
| `workitem(action=create)` | Create action items from retro |
| `workitem_comment(action=create)` | Add retro notes to items |
| `page(action=create)` | Save retro notes as a page |
| `label(action=list)` | Get labels for "retro-action" tag |
| `label(action=create)` | Create "retro-action" label if needed |

## Sprint Review

### Purpose
Demo completed work, gather feedback, measure what was accomplished vs planned.

### Sprint Review Workflow

```
1. Get sprint data:
   cycle(action=list, project_id=<id>, status=current)
   → Find the active cycle; for a sprint that just ended use status=completed

   cycle(action=retrieve, project_id=<id>, cycle_id=<cycle_id>)
   → Get sprint name, dates, description (goal)

2. Get sprint items:
   cycle(action=list_workitems, project_id=<id>, cycle_id=<cycle_id>)
   workitem(action=count, project_id=<id>, pql='cycle = "<cycle_id>"', group_by=state__group)
   → The count gives the item totals per state group in one call; the list gives
     the points and the item table. Categorize by state group:
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
   label(action=list, project_id=<id>)
   → Find label with name "retro-action" → get label_id

   workitem(action=list, project_id=<id>, pql='label = "<retro-action-label-id>"')
   → Items carrying the "retro-action" label, server-side
   → Check which are completed vs still open
     (workitem(action=count, ..., group_by=state__group) gives the split in one call)
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
   workitem(action=create,
            project_id=<id>,
            name="[RETRO] <action item description>",
            description_html="<p>From Sprint N retrospective. <details></p>",
            priority="high",
            labels=["<retro-action-label-id>"],
            assignees=["<owner_id>"],
            target_date="<next_sprint_end_date>")

7. Save retro notes:
   page(action=create,
        project_id=<id>,
        name="Retro — Sprint N (YYYY-MM-DD)",
        description_html="<h2>Sprint Metrics</h2>...<h2>Start</h2>...<h2>Stop</h2>...<h2>Continue</h2>...<h2>Action Items</h2>...")
```

## Sprint Close Workflow

### Step-by-step

```
1. Complete the sprint review (above)

2. Handle incomplete items. Decide per item first (see the table below):
   Option B: Move back to backlog (do this BEFORE the transfer)
     - cycle(action=manage_workitems, project_id=<id>, cycle_id=<current_cycle_id>,
             remove_ids=[<item ids>])
       Items leave the cycle and return to the backlog (a removal: the permission
       dialog asks first)
     - Don't carry over items that weren't started — reprioritize

   Option A: Transfer the rest to the next sprint
     - Create next cycle first (if not exists):
       cycle(action=create, project_id=<id>, name=..., owned_by=<member_id>,
             start_date=..., end_date=...)
     - End the sprint (the server rejects a transfer from a cycle that has not ended):
       cycle(action=complete, project_id=<id>, cycle_id=<current_cycle_id>)
     - Transfer (moves only the UNFINISHED items):
       cycle(action=transfer_workitems, project_id=<id>,
             cycle_id=<current_cycle_id>, new_cycle_id=<next_cycle_id>)

3. Archive the sprint:
   cycle(action=archive, project_id=<id>, cycle_id=<current_cycle_id>)
   (archive ends a still-running cycle first, which is why complete and transfer
    come before it)

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
