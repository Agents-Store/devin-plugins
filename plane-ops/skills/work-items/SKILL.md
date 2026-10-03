---
name: work-items
description: Work item operations in Plane — create, read, update, delete, search, filter with PQL, assign, label, link, comment, relate, and log time on work items (issues/tasks/tickets). Use when the user wants to create a task, update an issue, add a comment, attach a label, link a PR, set a blocker, log work time, or inspect a specific item. Covers work item types, custom properties, and multi-item batch edits.
---

# Work Items

This skill covers the full life of a work item in Plane: creation, inspection, updates, relations, comments, links, labels, work logs, and custom properties.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `workitem(action=create, ...)`, `workitem_relation(action=create, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix. Every tool's own description lists its actions with the required and optional parameters; read it before the first call on a resource.

## Field Names

The `workitem` tool has **fixed** parameter names and validates every call against the declared set: an unknown or misspelled parameter is an error, not a silent drop.

| Concept | Parameter |
|---------|-----------|
| Work item id | `workitem_id` |
| Human identifier | `workitem_identifier` (`PROJ-42`, for `retrieve_by_identifier`) |
| State UUID | `state` |
| Label UUIDs | `labels` |
| Assignees | `assignees` |
| Points | `point` or `estimate_point` |
| Parent | `parent` |
| Work item type | `type_id` |
| Priority | `priority` (`urgent`, `high`, `medium`, `low`, `none`) |
| Description | `description_html` (or `description_stripped` for plain text; `description_html` wins if both are given) |

To clear a field on update pass `assignees=[]` or `labels=[]`, or `start_date=null` / `target_date=null`; a field you leave out is not changed. If a call is rejected, re-read the tool description rather than guessing another spelling.

## Available Calls

| Call | Purpose |
|------|---------|
| `workitem(action=list)` | List items in a project, or the whole workspace without `project_id`; `pql` filter, `order_by`, `cursor`, `per_page`, `expand`, `fields` |
| `workitem(action=list_archived)` | Archived items of a project |
| `workitem(action=search)` | Text search (`query`), workspace-wide |
| `workitem(action=count)` | Count items, optionally grouped (`group_by`, `sub_group_by`) |
| `workitem(action=create)` | Create a new work item |
| `workitem(action=retrieve)` | Get an item by UUID |
| `workitem(action=retrieve_by_identifier)` | Get an item by human identifier (`workitem_identifier="PROJ-42"`) |
| `workitem(action=update)` | Update any field (state, points, priority, assignees, description) |
| `workitem(action=manage_assignee)` / `workitem(action=manage_label)` | Add or remove assignees or labels without replacing the list |
| `workitem(action=archive)` | Archive (`archive=false` restores); only completed or cancelled items |
| `workitem(action=delete)` | Delete an item permanently |
| `workitem_comment(action=list\|retrieve\|create\|update\|delete)` | Comments |
| `workitem_link(action=list\|retrieve\|create\|update\|delete)` | External links (PRs, docs, designs) |
| `workitem_relation(action=list\|create\|delete)` | Blocked-by / blocks / start-finish dependencies, plus custom relation definitions |
| `workitem_activity(action=list\|retrieve)` | Audit trail |
| `work_log(action=list\|create\|update\|delete)` | Time tracking |
| `workitem_type(action=list\|resolve\|create\|...)` | Custom types (bug, story, task, spike, epic) |
| `workitem_property(action=list\|create\|set_value\|...)` | Custom fields and their values |
| `workitem_attachment(action=list\|upload_from_url\|download_url\|read\|delete)` | Files on a work item |
| `label(action=list\|create)` | Labels |
| `state(action=list)` | Resolve state UUIDs for filtering and updating |

## Creating a Work Item

```
1. connector-bootstrap                       → resolve tool names and instance
2. project(action=list)                      → pick project_id
3. state(action=list, project_id=<id>)       → map target state to UUID
4. label(action=list, project_id=<id>)       → map labels to UUIDs (optional)
5. member(action=list_project, project_id=<id>) → resolve assignee UUIDs
6. workitem(action=create,
     project_id=<id>,
     name="...",
     description_html="...",     // with acceptance criteria
     priority="high",            // urgent | high | medium | low | none
     point=3,                    // Fibonacci 1..8 (see agile-fundamentals)
     state=<state_uuid>,
     assignees=[<user_uuid>],
     labels=[<label_uuid>],
     type_id=<type_uuid>)        // optional custom type, from workitem_type(action=resolve)
```

### Description Template

```html
<h3>Context</h3>
<p>Why this matters, links to related work.</p>

<h3>Acceptance Criteria</h3>
<ul>
  <li>Given … when … then …</li>
  <li>Given … when … then …</li>
</ul>

<h3>Out of Scope</h3>
<ul>
  <li>Explicit exclusions</li>
</ul>

<h3>Notes</h3>
<p>Implementation hints, open questions.</p>
```

## Updating a Work Item

Always resolve IDs first. Typical updates:

```
workitem(action=update, project_id=<id>, workitem_id=<id>, state=<state_uuid>)      # move state
workitem(action=update, project_id=<id>, workitem_id=<id>, point=5)                 # estimate
workitem(action=update, project_id=<id>, workitem_id=<id>, priority="high")         # re-prioritize
workitem(action=update, project_id=<id>, workitem_id=<id>, assignees=[<user_uuid>]) # replace assignees
workitem(action=update, project_id=<id>, workitem_id=<id>, labels=[<label_uuid>])   # replace labels
```

`update` replaces the whole `assignees` or `labels` list. To add or drop one entry without reading the current list first, use the merge actions (removals apply first, each takes one id or several):

```
workitem(action=manage_assignee, project_id=<id>, workitem_id=<id>, add_user_id=<uuid>)
workitem(action=manage_label, project_id=<id>, workitem_id=<id>, remove_label_id=<uuid>)
```

Batch updates: loop over items; do not call in parallel if the tool is not idempotent by default — check the tool description.

## Relations (Blockers, Duplicates, Relates-to)

```
workitem_relation(action=create,
  project_id=<id>,
  workitem_id=<id>,
  workitem_ids=["<other_uuid>"],               // related work item UUIDs (array)
  relation_type="blocking" | "blocked_by" | "start_before" | "start_after" | "finish_before" | "finish_after"
)
```

The related items go in `workitem_ids` (array of UUID strings), and the relation is one of six built-in dependency types. Other relationships — duplicate, relates-to and any workspace-defined custom relation — are *definitions*: call `workitem_relation(action=list_definitions)`, match the user's wording to an entry, and pass `relation_definition_id` plus `relation_definition_label` (the matched outward or inward label, which sets the direction) instead of `relation_type`. To remove a relation use `workitem_relation(action=delete, project_id, workitem_id, related_workitem_id, is_dependency)`; `is_dependency` must match the kind that was created (default false).

Before adding an item to a sprint, always check that it has no unresolved `blocked_by` relations — see `agile-fundamentals` Definition of Ready. PQL can also answer it in one query: `blocks("PROJ-12")` lists the items that block PROJ-12 (direction per the `get_pql_reference` wording — confirm on your instance; `workitem_relation(action=list)` is the authoritative answer).

## Comments and Links

- **Comments** use `comment_html` (not `description_html`): `workitem_comment(action=create, project_id, workitem_id, comment_html="<p>…</p>")`. `access` is `INTERNAL` or `EXTERNAL`. To mention someone, write `@[<user uuid>]` inline (`comment_html="<p>@[<user uuid>] can you review?</p>"`) and the chip and the notification are generated - a bare `@name` is ordinary text and notifies nobody; the id must belong to a member of the work item's project (`member(action=list_project)` resolves a name to one).
- **Links** are external URLs (`http://` or `https://`). `workitem_link(action=create)` and `update` accept both **`url` and `title`**; the title is the text Plane shows in place of the URL (without one, the URL itself is shown).

```
workitem_link(action=create,
  project_id=<id>,
  workitem_id=<id>,
  url="https://github.com/org/repo/pull/420",
  title="PR #420: fix login redirect"          // optional
)
```

## Attachments

```
workitem_attachment(action=upload_from_url, project_id=<id>, workitem_id=<id>, url="https://example.com/mockup.png", name="Mockup v3")
workitem_attachment(action=list, project_id=<id>, workitem_id=<id>)                     → attachment ids
workitem_attachment(action=read, project_id=<id>, workitem_id=<id>, attachment_id=<id>) → images and text inline
workitem_attachment(action=download_url, project_id=<id>, workitem_id=<id>, attachment_id=<id>) → a link for anything else
```

`upload_from_url` makes the server fetch the file, so the URL must be reachable without authentication and must not resolve to a private address; there is no way to upload a local file through the tool. `workitem_attachment(action=delete)` is permanent and asks for confirmation.

## Work Logs (Time Tracking)

```
work_log(action=create,
  project_id=<id>,
  workitem_id=<id>,
  description="Debug + fix",
  duration=150      // integer MINUTES (2h 30m = 150)
)
```

**`duration` is an integer number of minutes**, not an ISO 8601 string like `"PT2H30M"` and not seconds. Convert user input accordingly: "2h 30m" → 150; "PT2H30M" → parse, then convert to minutes.

The project must have time tracking enabled, otherwise the call fails. Check with `project(action=retrieve, project_id)` (`is_time_tracking_enabled`) and, with the user's consent, enable it with `project(action=update, project_id, is_time_tracking_enabled=true)`. `work_log(action=list)` needs a `workitem_id`; for project totals use `project(action=worklog_summary, project_id)`.

Use to compare estimated story points vs actual time (see `velocity-metrics`).

## Searching and Filtering

### Human identifier lookup

```
workitem(action=retrieve_by_identifier, workitem_identifier="PROJ-42")
```

Pass the full `PROJECT-N` identifier as one string; the server splits it. A malformed identifier is rejected with a message naming the expected form.

### Full-text search

```
workitem(action=search, query="login bug")
```

`search` is **workspace-scoped**: it has no `project_id`, and the result contains matching work items across the whole workspace — filter by project client-side if needed. The parameter is `query`.

### Filtered list with PQL

Filtering is done by the server with the `pql` parameter (Plane Query Language) of `workitem(action=list)`, `list_archived` and `count`. Call `get_pql_reference` before composing anything beyond these examples. At most 5 conditions per query; UUID fields (`assignee`, `state`, `label`, `cycle`, `module`, `type`, `milestone`, `project`, `createdBy`) need UUIDs, resolve names first.

```
workitem(action=list, project_id=<id>, pql='assignee = currentUser() AND stateGroup = "started"')
workitem(action=list, project_id=<id>, pql='priority IN ("urgent","high") AND stateGroup IN openStates()')
workitem(action=list, project_id=<id>, pql='isOverdue()')
workitem(action=list, project_id=<id>, pql='title ~ "webhook"')
workitem(action=list, project_id=<id>, pql='cycle IN activeCycle() AND stateGroup IN closedStates()')
workitem(action=list, pql='id = "PROJ-42"')                          # no project_id = whole workspace
workitem(action=count, project_id=<id>, pql='stateGroup = "started"', group_by=assignees__id)
```

`state__group` is a `group_by` key for `count`, not a PQL field: filter with `stateGroup`. `count` with a `project_id` adds the condition `project = "<id>"` to your `pql`, so that one counts against the 5-condition limit. Pagination: results come back as an envelope with `next_cursor`; pass it as `cursor` for the next page (`per_page` sets the page size). Use `order_by`, `expand` and the sparse fieldset `fields` (for example `fields="id,name,point,estimate_point,state"`; use `project`, not `project_id`) to shrink the payload.

## Custom Types and Properties

If the project uses custom work item types (Bug, Story, Spike, Task, Epic):

```
workitem_type(action=resolve, project_id=<id>, name="Bug")  → id is the type_id (finds or creates, never duplicates)
workitem(action=create, ..., type_id=<type_id>)
workitem_type(action=list, project_id=<id>)                  → all types of the project
```

Custom properties (e.g. "Customer impact", "RICE score") live with a work item type and are written per item, not through `workitem(action=update)`:

```
workitem_property(action=list, project_id=<id>, workitem_type_id=<type_id>) → property_id and its options
workitem_property(action=set_value, project_id=<id>, workitem_id=<id>, property_id=<id>, value=<value>)
workitem_property(action=get_value, project_id=<id>, workitem_id=<id>, property_id=<id>)
```

Pass `value` in the type the property expects (TEXT/URL as a string, DECIMAL as a number, BOOLEAN as true/false, OPTION as an option id, an array of them for a multi-value property); `set_value` replaces every existing value of a multi-value property. A property id also filters in PQL: `cf["<property-uuid>"] = "<value>"`.

## Best Practices

1. Always fill acceptance criteria before estimating.
2. Never assign points > 8 — decompose instead.
3. Link the PR as soon as it opens; link the deploy as soon as it ships.
4. Log actual time on items with estimates > 3 points to calibrate future estimation.
5. When closing a blocker, also verify the downstream items it was blocking.
6. Use labels sparingly — they should reflect meaningful categories, not tags for everything.
7. Count before you list: `workitem(action=count, pql=...)` answers "how many" without pulling items into the conversation.

## Known Limitations

- **List parameters.** `cycle`, `module`, `milestone`, `initiative` and `release` `manage_workitems` take `add_ids` / `remove_ids` arrays and `workitem_relation` takes `workitem_ids`. The official server repairs a JSON-encoded string such as `'["uuid"]'` before validation, but some MCP bridges still reject list-typed parameters with `Input should be a valid list`. That is a bridge bug, not a content bug: try the native list, then the JSON-encoded string, and if both fail do the operation in the Plane UI and tell the user.
- **Archive.** `cycle(action=archive)` ends a still-running cycle first, so it succeeds but cuts the sprint short: run `complete` and `transfer_workitems` first (see `/close-sprint`). For modules, check the behavior on your instance. To remove a cycle or module entirely use the `delete` action, after confirmation.
- **Write-then-read.** `manage_workitems` and the project/initiative link actions return nothing; read the result back with `list_workitems` or `list_projects` of the same resource.
- **Plan-gated features.** Time tracking (`work_log`), work item types, work item properties and project feature toggles depend on the workspace plan; the refusal names the missing feature.
