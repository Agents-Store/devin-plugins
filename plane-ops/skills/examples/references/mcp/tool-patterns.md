# Plane MCP Tool Call Patterns

Exact parameter formats for key Plane operations. Plane MCP (0.3.0 and later) exposes **one tool per resource** and an `action` parameter selects the operation. Tool names below are the **resource names**; the actual MCP tool name is `mcp__<server>__<resource>` - discover the server segment with the `connector-bootstrap` skill. Parameters are validated against the action's declared set: an unknown or misspelled parameter is an error, not a silent drop. Scope: pass `project_id` for a project's own set, omit it for the workspace.

## Projects

### List Projects
```
Tool: project
Input: { "action": "list", "per_page": 50 }
Output: Envelope { results: [{ id, name, identifier, ... }], next_cursor, ... }; pass next_cursor as "cursor" for the next page
```

### Retrieve Project
```
Tool: project
Input: { "action": "retrieve", "project_id": "uuid-of-project" }
Output: Full project details
```

### Get Project Members
```
Tool: member
Input: { "action": "list_project", "project_id": "uuid-of-project" }
Output: List of project members with their ids and display names
```

## Work Items

### Create Work Item
```
Tool: workitem
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "name": "User can sign up with email",
  "description_html": "<p>As a new user, I want to sign up...</p>",
  "priority": "high",
  "point": 5,
  "assignees": ["uuid-of-user"],
  "labels": ["uuid-of-label"],
  "state": "uuid-of-todo-state",
  "parent": "uuid-of-parent-item",
  "type_id": "uuid-of-work-item-type",
  "start_date": "2025-03-10",
  "target_date": "2025-03-14"
}
Output: Created work item with id, name, sequence_id
```

### Create an Epic
```
Tool: workitem_type
Input: { "action": "resolve", "project_id": "uuid-of-project", "name": "Epic" }
Output: The Epic type; its id is the type_id below (finds or creates, never duplicates)

Tool: workitem
Input: { "action": "create", "project_id": "uuid-of-project", "name": "Multi-tenant support", "type_id": "<id from resolve>" }
```
There are no epic tools; an epic is a work item of the type "Epic".

### Update Work Item (Set Story Points)
```
Tool: workitem
Input: {
  "action": "update",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-item",
  "point": 5
}
Output: Updated work item
```

### Update Work Item (Change Priority)
```
Tool: workitem
Input: {
  "action": "update",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-item",
  "priority": "urgent"
}
```

### Update Work Item (Change State)
```
Tool: workitem
Input: {
  "action": "update",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-item",
  "state": "uuid-of-done-state"
}
```

### Add an Assignee Without Replacing the List
```
Tool: workitem
Input: { "action": "manage_assignee", "project_id": "uuid-of-project", "workitem_id": "uuid-of-item", "add_user_id": "uuid-of-user" }
```

### Retrieve Work Item by Identifier
```
Tool: workitem
Input: { "action": "retrieve_by_identifier", "workitem_identifier": "MSA-42" }
Output: Full work item details for MSA-42
```

### Search Work Items
```
Tool: workitem
Input: { "action": "search", "query": "login authentication" }
Output: Work items matching the search text (workspace-wide)
```

### List Work Items (PQL filter)
```
Tool: workitem
Input: {
  "action": "list",
  "project_id": "uuid-of-project",
  "pql": "assignee = currentUser() AND stateGroup IN openStates()",
  "per_page": 50,
  "fields": "id,name,point,priority,state"
}
Output: Envelope { results: [...], total_count, next_cursor, ... }
```
`pql` is Plane Query Language, at most 5 conditions; call `get_pql_reference` for the syntax. More patterns: `stateGroup = "started"`, `priority IN ("urgent","high")`, `isOverdue()`, `hasNoAssignee()`, `title ~ "login"`, `cycle IN activeCycle()`, `childOf("MSA-42")`. Omit `project_id` to query the whole workspace.

### Count Work Items (aggregates)
```
Tool: workitem
Input: {
  "action": "count",
  "project_id": "uuid-of-project",
  "pql": "cycle = \"uuid-of-cycle\"",
  "group_by": "state__group"
}
Output: { total_count, grouped_counts: { "started": { count }, "completed": { count }, ... } }
```
`group_by` / `sub_group_by` keys: `state_id`, `state__group`, `priority`, `project_id`, `type_id`, `labels__id`, `assignees__id`, `issue_module__module_id`, `release_work_items__release_id`, `cycle_id`, `milestone_id`, `created_by`, `target_date`, `start_date`. They are grouping keys only, not PQL fields (filter with `stateGroup`). Counts are of items, not points.

## Cycles (Sprints)

### Create Cycle
```
Tool: cycle
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "name": "Sprint 12 — User Authentication",
  "owned_by": "uuid-of-current-user",
  "description": "By end of sprint, users can sign up and log in",
  "start_date": "2025-03-10",
  "end_date": "2025-03-14"
}
Output: Created cycle with id, name, dates
```

### List Cycles
```
Tool: cycle
Input: { "action": "list", "project_id": "uuid-of-project", "status": "current" }
Note: status is current | upcoming | completed | draft | incomplete; "archived": true lists archived cycles instead (status is then ignored)
```

### Add Work Items to Cycle (Bulk)
```
Tool: cycle
Input: {
  "action": "manage_workitems",
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-cycle",
  "add_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
Note: returns nothing; read back with list_workitems. "remove_ids" takes items out of the cycle.
```

### List Cycle Work Items
```
Tool: cycle
Input: {
  "action": "list_workitems",
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-cycle",
  "pql": "stateGroup = \"completed\""
}
Output: Envelope of the sprint's work items (pql is optional)
```

### Close a Sprint (complete, transfer, archive)
```
Tool: cycle
Input: { "action": "complete", "project_id": "uuid-of-project", "cycle_id": "uuid-of-current-cycle" }
Note: sets end_date to today; the server rejects a transfer from a cycle that has not ended

Tool: cycle
Input: {
  "action": "transfer_workitems",
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-current-cycle",
  "new_cycle_id": "uuid-of-next-cycle"
}
Note: moves ALL unfinished items to the new cycle (finished items stay)

Tool: cycle
Input: { "action": "archive", "project_id": "uuid-of-project", "cycle_id": "uuid-of-current-cycle" }
Note: ends a still-running cycle first, so complete and transfer come before it
```

## Relations

### Create Relation (Blocking)
```
Tool: workitem_relation
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-blocking-item",
  "relation_type": "blocking",
  "workitem_ids": ["uuid-of-blocked-item-1", "uuid-of-blocked-item-2"]
}
Relation types: blocking, blocked_by, start_before, start_after, finish_before, finish_after.
Duplicate, relates-to and custom relations: list_definitions, then relation_definition_id + relation_definition_label.
```

### List Relations
```
Tool: workitem_relation
Input: { "action": "list", "project_id": "uuid-of-project", "workitem_id": "uuid-of-item" }
Output: The item's relations grouped by type (blocking, blocked_by, ...)
```

## States

### Create State
```
Tool: state
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "name": "In Progress",
  "color": "#f59e0b",
  "group": "started",
  "sequence": 3
}
Groups: backlog, unstarted, started, completed, cancelled
```

## Labels

### Create Label
```
Tool: label
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "name": "bug",
  "color": "#ef4444",
  "description": "Bug or defect"
}
```

## Pages

### Create Project Page (Retro Notes)
```
Tool: page
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "name": "Retro — Sprint 12 (2025-03-14)",
  "description_html": "<h2>Sprint Metrics</h2><p>Completed: 34/40 points (85%)</p><h2>Start</h2><ul><li>Daily code reviews</li></ul><h2>Stop</h2><ul><li>Skipping standups</li></ul><h2>Continue</h2><ul><li>Pair programming</li></ul>"
}
```

### Update a Page
```
Tool: page
Input: { "action": "update", "project_id": "uuid-of-project", "page_id": "uuid-of-page", "description_html": "<full edited body>" }
Note: description_html replaces the WHOLE body - retrieve the page first and send the complete edited HTML
```

## Releases

### Write Release Notes into the Changelog
```
Tool: release
Input: { "action": "list_workitems", "release_id": "uuid-of-release" }
Output: The work items shipped in the release

Tool: release
Input: { "action": "get_changelog", "release_id": "uuid-of-release" }

Tool: release
Input: { "action": "update_changelog", "release_id": "uuid-of-release", "description_html": "<h2>New Features</h2><ul><li>…</li></ul>" }
```

## Intake

### Accept an Intake Item
```
Tool: intake
Input: { "action": "update", "project_id": "uuid-of-project", "workitem_id": "uuid-of-intake-item", "status": 1 }
Note: workitem_id is the "issue" field of the intake record. Status: -2 pending, -1 declined, 0 snoozed (needs snoozed_till), 1 accepted, 2 duplicate (needs duplicate_to). The tool description gives no format for snoozed_till / duplicate_to: confirm on your instance
```

## Work Logs

### Create Work Log
```
Tool: work_log
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-item",
  "duration": 120,
  "description": "Implemented API endpoints and wrote tests"
}
Note: duration is in minutes
```

## Comments

### Create Comment
```
Tool: workitem_comment
Input: {
  "action": "create",
  "project_id": "uuid-of-project",
  "workitem_id": "uuid-of-item",
  "comment_html": "<p>Updated the API schema based on review feedback.</p>"
}
```
