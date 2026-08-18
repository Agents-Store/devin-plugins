---
name: intake-triage
description: Plane intake inbox — triage incoming requests, bug reports, and ideas before they enter the backlog. Use when the user wants to review the intake queue, accept or reject incoming items, convert intake items into work items, or set up a triage process. Covers daily/weekly triage rituals and routing rules.
---

# Intake Triage

The intake inbox is where unvetted requests, bug reports, and ideas land before being turned into proper work items. A disciplined triage prevents the backlog from becoming a dumping ground.

## Tool Name Resolution

Resolve real tool names via the `connector-bootstrap` skill.

## Available Actions

| Action | Purpose |
|--------|---------|
| `list_intake_work_items` | List all items waiting for triage |
| `retrieve_intake_work_item` | Get a single intake item |
| `create_intake_work_item` | Create an intake item (usually by integration — see caveat below) |
| `update_intake_work_item` | Edit intake item (status, notes) |
| `delete_intake_work_item` | Reject and remove an intake item |

## Creating Intake Items — Schema Caveat

`create_intake_work_item` on most Plane deployments expects a **single `data` object wrapping all work item fields**, not flat top-level parameters:

```
create_intake_work_item({
  project_id,
  data: {
    name: "User reports: ...",
    description_html: "<p>…</p>",
    priority: "medium"
  }
})
```

Passing `name`, `description_html`, `priority` as top-level arguments will be rejected as "unexpected keyword arguments". Note that some MCP bridges also have trouble serializing the nested `data` dict — if the call fails with "Input should be a valid dictionary", check the bridge's list/dict parameter handling.

## Triage Workflow

### Step 1 — Review the Queue

```
1. connector-bootstrap → resolve tools
2. list_projects       → pick project_id
3. list_intake_work_items({ project_id })
4. Sort by age (oldest first) and source
```

### Step 2 — Classify Each Item

For each intake item, make one of four decisions:

| Decision | Action | Rationale |
|----------|--------|-----------|
| **Accept** | Convert to work item, add to backlog | Valid work aligned with product goals |
| **Accept + escalate** | Convert to work item, prioritize `urgent`/`high`, assign lead | Critical bug or time-sensitive request |
| **Defer** | Update intake status to "deferred" with rationale | Valid but not now; revisit in N weeks |
| **Reject** | Delete intake item with comment | Duplicate, out of scope, or invalid |

### Step 3 — Convert to Work Item

When accepting, resolve required IDs and create the item (see `work-items` skill):

```
create_work_item({
  project_id,
  name,
  description_html,     // include source link and original reporter
  priority,
  state_id,             // usually backlog state
  label_ids             // e.g. "bug", "feature-request"
})
```

Then remove or mark the intake item as processed per the tool schema.

### Step 4 — Communicate

Always tell the reporter what happened:
- Accepted → link to the new work item
- Deferred → explain when it will be reconsidered
- Rejected → explain why

## Routing Rules

Define routing rules up front so triage is fast:

| Signal | Route to |
|--------|----------|
| "Crashes", "data loss", "can't log in" | Bug → urgent, assign on-call |
| "Would be nice", "suggestion" | Feature request → label and defer until next grooming |
| Duplicate keywords match existing item | Reject → link to existing item |
| Missing reproduction steps (bug) | Request info via comment, keep in intake |
| Single customer with low impact | Defer with rationale |
| Multiple customers report same issue | Escalate |

## Triage Cadence

- **Daily** — check intake for urgent items (5 min)
- **Weekly** — full triage session (30–60 min, joint with PM)
- **Backlog grooming** — re-review deferred items

## Triage Session Output

A triage session should produce:

```
| # | Item | Decision | Target | Notes |
|---|------|----------|--------|-------|
| 1 | "Login 500" | Accept+escalate | PROJ-148 | Assigned to @alice |
| 2 | "Dark mode"  | Defer          | 2 sprints | Low signal |
| 3 | "Same bug"   | Reject         | —       | Duplicate of PROJ-142 |
```

## Best Practices

1. Triage every intake item within 48 hours, even if the decision is "defer".
2. Never let the intake queue grow past 20 items — increase cadence if it does.
3. Always link the original intake source (Slack, email, form) in the resulting work item description.
4. Reject duplicates fast but always link the existing work item so reporters feel heard.
5. Track triage decisions in a weekly report — it reveals product signal patterns.
