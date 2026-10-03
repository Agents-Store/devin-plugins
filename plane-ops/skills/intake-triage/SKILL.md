---
name: intake-triage
description: Plane intake inbox — triage incoming requests, bug reports, and ideas before they enter the backlog. Use when the user wants to review the intake queue, accept or reject incoming items, convert intake items into work items, or set up a triage process. Covers daily/weekly triage rituals and routing rules.
---

# Intake Triage

The intake inbox is where unvetted requests, bug reports, and ideas land before being turned into proper work items. A disciplined triage prevents the backlog from becoming a dumping ground.

## Tool Name Resolution

Plane MCP exposes one `intake` tool and the operation goes into the `action` parameter: `intake(action=list, ...)`. This skill writes calls in that form. Resolve the real tool name (`mcp__<server>__intake`) through the `connector-bootstrap` skill - never assume a server prefix.

## Available Calls

| Call | Purpose |
|------|---------|
| `intake(action=list, project_id)` | List all items waiting for triage (paginated: `next_cursor`) |
| `intake(action=retrieve, project_id, workitem_id)` | Get a single intake item |
| `intake(action=create, project_id, name, ...)` | Create an intake item (usually done by an integration) |
| `intake(action=update, project_id, workitem_id, status=...)` | Make the triage decision (accept, decline, snooze, mark duplicate) |
| `intake(action=delete, project_id, workitem_id)` | Remove an intake item permanently (spam only; confirmation required) |

`workitem_id` is the **`issue` field** of an intake record - the id of the work item behind it - not the record's own id. The project needs the `intakes` feature: check `project(action=get_features, project_id)` and, with the user's consent, enable it with `project(action=update_features, project_id, intakes=true)`.

## Creating Intake Items

`intake(action=create)` takes flat fields; the server nests them as the API requires:

```
intake(action=create,
  project_id=<id>,
  name="User reports: ...",
  description_html="<p>…</p>",
  priority="medium")      // urgent | high | medium | low | none
```

## Triage Statuses

`intake(action=update, status=...)` is the decision itself. The status codes:

| `status` | Meaning | Extra parameter |
|----------|---------|-----------------|
| `-2` | Pending (untriaged) | - |
| `-1` | Declined | - |
| `0` | Snoozed | `snoozed_till` (required; the tool description gives no format, use an ISO 8601 timestamp) |
| `1` | Accepted | - |
| `2` | Duplicate | `duplicate_to` (required; the tool description names no format, use the id of the original work item) |

`intake(action=update)` without a status only edits `source` / `source_email`.

> **Confirm on your instance:** the tool description defines the status codes and the two required parameters, but not their formats or what each decision does to the item. The behaviour described below (an accepted item leaves the queue as a regular backlog work item; a snoozed item comes back on its date) is Plane's triage behaviour as commonly documented, not something the tool states. Check the first accept and the first snooze on your instance.

## Triage Workflow

### Step 1 — Review the Queue

```
1. connector-bootstrap → resolve tools
2. project(action=list) → pick project_id
3. intake(action=list, project_id=<id>)       → items waiting (follow next_cursor)
4. Sort by age (oldest first) and source
```

The items are work items, so PQL can also find them: `workitem(action=list, project_id=<id>, pql='isIntake()')`, or count them with `workitem(action=count, project_id=<id>, pql='isIntake()')`.

### Step 2 — Classify Each Item

For each intake item, make one of four decisions:

| Decision | Call | Rationale |
|----------|------|-----------|
| **Accept** | `intake(action=update, status=1)`, then groom the item with `workitem(action=update)` | Valid work aligned with product goals |
| **Accept + escalate** | `status=1`, then `workitem(action=update, priority="urgent"\|"high", assignees=[<lead>])` | Critical bug or time-sensitive request |
| **Defer** | `intake(action=update, status=0, snoozed_till=<date>)` with a rationale comment | Valid but not now; it returns to the queue on that date (confirm on your instance) |
| **Reject** | `intake(action=update, status=-1)` with a comment explaining why; duplicates use `status=2, duplicate_to=<id>` | Out of scope, invalid or duplicate; declining keeps the trace, `delete` does not |

### Step 3 — Finish the Accepted Item

Accepting should turn the intake record into a regular work item in the project (per Plane's triage model, not stated by the tool description - confirm on your instance), so there is no second "create" step. Complete it with the fields the intake form did not carry (see the `work-items` skill):

```
workitem(action=update,
  project_id=<id>,
  workitem_id=<intake item's issue id>,
  description_html="...",   // add the source link and the original reporter
  priority="high",
  state=<backlog state uuid>,
  labels=[<label uuid>])    // e.g. "bug", "feature-request"
```

### Step 4 — Communicate

Always tell the reporter what happened, with a comment on the item (`workitem_comment(action=create, comment_html="<p>…</p>")`):
- Accepted → link to the work item
- Deferred → explain when it will be reconsidered
- Rejected or duplicate → explain why, link the existing item

## Routing Rules

Define routing rules up front so triage is fast:

| Signal | Route to |
|--------|----------|
| "Crashes", "data loss", "can't log in" | Bug → urgent, assign on-call |
| "Would be nice", "suggestion" | Feature request → label and defer until next grooming |
| Duplicate keywords match existing item | Mark duplicate (`status=2`, `duplicate_to`) → link to existing item |
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
