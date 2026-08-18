# Plane MCP Tool Call Patterns

Exact parameter formats for key Plane operations. All tool names are **generic action names** — discover the actual MCP prefix by listing available tools.

## Projects

### List Projects
```
Tool: list_projects
Input: {}
Output: List of projects with id, name, identifier, description
```

### Retrieve Project
```
Tool: retrieve_project
Input: { "project_id": "uuid-of-project" }
Output: Full project details
```

### Get Project Members
```
Tool: get_project_members
Input: { "project_id": "uuid-of-project" }
Output: List of { id, display_name, email } for each member
```

## Work Items

### Create Work Item
```
Tool: create_work_item
Input: {
  "project_id": "uuid-of-project",
  "name": "User can sign up with email",
  "description_html": "<p>As a new user, I want to sign up...</p>",
  "priority": "high",
  "point": 5,
  "assignees": ["uuid-of-user"],
  "labels": ["uuid-of-label"],
  "state": "uuid-of-todo-state",
  "parent": "uuid-of-parent-item",
  "start_date": "2025-03-10",
  "target_date": "2025-03-14"
}
Output: Created work item with id, name, sequence_id
```

### Update Work Item (Set Story Points)
```
Tool: update_work_item
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item",
  "point": 5
}
Output: Updated work item
```

### Update Work Item (Change Priority)
```
Tool: update_work_item
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item",
  "priority": "urgent"
}
```

### Update Work Item (Change State)
```
Tool: update_work_item
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item",
  "state": "uuid-of-done-state"
}
```

### Retrieve Work Item by Identifier
```
Tool: retrieve_work_item_by_identifier
Input: {
  "project_identifier": "MSA",
  "issue_identifier": 42
}
Output: Full work item details for MSA-42
```

### Search Work Items
```
Tool: search_work_items
Input: { "query": "login authentication" }
Output: Work items matching the search text
```

### List Work Items (with filtering)
```
Tool: list_work_items
Input: {
  "project_id": "uuid-of-project",
  "per_page": 50,
  "expand": "assignees,labels,state",
  "order_by": "-priority"
}
Output: Paginated list with expanded relations
```

## Cycles (Sprints)

### Create Cycle
```
Tool: create_cycle
Input: {
  "project_id": "uuid-of-project",
  "name": "Sprint 12 — User Authentication",
  "owned_by": "uuid-of-current-user",
  "description": "By end of sprint, users can sign up and log in",
  "start_date": "2025-03-10",
  "end_date": "2025-03-14"
}
Output: Created cycle with id, name, dates
```

### Add Work Items to Cycle (Bulk)
```
Tool: add_work_items_to_cycle
Input: {
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-cycle",
  "issue_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### List Cycle Work Items
```
Tool: list_cycle_work_items
Input: {
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-cycle"
}
Output: All work items in the sprint with states and points
```

### Transfer Cycle Work Items
```
Tool: transfer_cycle_work_items
Input: {
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-current-cycle",
  "new_cycle_id": "uuid-of-next-cycle"
}
Note: Transfers ALL incomplete items to the new cycle
```

### Archive Cycle
```
Tool: archive_cycle
Input: {
  "project_id": "uuid-of-project",
  "cycle_id": "uuid-of-cycle"
}
```

## Relations

### Create Relation (Blocking)
```
Tool: create_work_item_relation
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-blocking-item",
  "relation_type": "blocking",
  "issues": ["uuid-of-blocked-item-1", "uuid-of-blocked-item-2"]
}
Relation types: blocking, blocked_by, duplicate, relates_to,
                start_before, start_after, finish_before, finish_after
```

### List Relations
```
Tool: list_work_item_relations
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item"
}
Output: { blocking: [...], blocked_by: [...], duplicate: [...], relates_to: [...] }
```

## States

### Create State
```
Tool: create_state
Input: {
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
Tool: create_label
Input: {
  "project_id": "uuid-of-project",
  "name": "bug",
  "color": "#ef4444",
  "description": "Bug or defect"
}
```

## Pages

### Create Project Page (Retro Notes)
```
Tool: create_project_page
Input: {
  "project_id": "uuid-of-project",
  "name": "Retro — Sprint 12 (2025-03-14)",
  "description_html": "<h2>Sprint Metrics</h2><p>Completed: 34/40 points (85%)</p><h2>Start</h2><ul><li>Daily code reviews</li></ul><h2>Stop</h2><ul><li>Skipping standups</li></ul><h2>Continue</h2><ul><li>Pair programming</li></ul>"
}
```

## Work Logs

### Create Work Log
```
Tool: create_work_log
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item",
  "duration": 120,
  "description": "Implemented API endpoints and wrote tests"
}
Note: duration is in minutes
```

## Comments

### Create Comment
```
Tool: create_work_item_comment
Input: {
  "project_id": "uuid-of-project",
  "work_item_id": "uuid-of-item",
  "comment_html": "<p>Updated the API schema based on review feedback.</p>"
}
```
