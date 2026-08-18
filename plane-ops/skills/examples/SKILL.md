---
name: examples
description: Tool call patterns, end-to-end workflow examples, and scenario references for Plane Agile workflows. Use when needing reference implementations, complete examples, or tool call patterns.
---

# Examples & References

This skill provides reference implementations, tool call patterns, and complete workflow scenarios for Plane Agile workflows.

## Related Skills

For day-to-day operations, route through the dedicated skills rather than this reference:

| Domain | Skill |
|--------|-------|
| Tool discovery across any MCP/connector/instance | **connector-bootstrap** |
| Formulas, DoR/DoD, MoSCoW, WSJF, Fibonacci | **agile-fundamentals** |
| Sprint planning ceremony | **sprint-planning** |
| Work item CRUD, relations, comments, logs | **work-items** |
| Feature/workstream grouping | **modules** |
| Long-horizon planning (epic, initiative, milestone) | **epics-initiatives-milestones** |
| Triage incoming requests | **intake-triage** |
| Publish reports and pages (sprint, retro, ADR, runbook, spec) | **pages-publishing** |
| Labels, states, work item types, custom properties | **labels-states-properties** |
| Backlog grooming, WSJF | **backlog-management** |
| Estimation | **estimation** |
| Task decomposition | **task-decomposition** |
| Velocity and burndown | **velocity-metrics** |
| Daily standup | **daily-standup** |
| Sprint review and retro | **sprint-review-retro** |
| New project setup | **project-setup** |

## Reference Files

| File | Description |
|------|-------------|
| [tool-patterns.md](references/mcp/tool-patterns.md) | Tool call patterns with exact parameter formats |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step workflow examples combining multiple tools |
| [page-formatting.md](references/page-formatting.md) | HTML formatting rules and templates for Plane pages (`description_html`) |
| [sprint-lifecycle.md](references/scenarios/sprint-lifecycle.md) | End-to-end sprint lifecycle scenario |
| [backlog-grooming.md](references/scenarios/backlog-grooming.md) | Backlog grooming session scenario |
| [everyday-commands.md](references/scenarios/everyday-commands.md) | Common day-to-day flows: page creation, time logging, PR linking, bulk edits, label/state setup |

## Quick Reference: All Tools by Group

### Workspace (4)
`get_me`, `get_workspace_members`, `get_workspace_features`, `update_workspace_features`

### Projects (9)
`list_projects`, `create_project`, `retrieve_project`, `update_project`, `delete_project`, `get_project_members`, `get_project_features`, `update_project_features`, `get_project_worklog_summary`

### Work Items (7)
`list_work_items`, `create_work_item`, `retrieve_work_item`, `retrieve_work_item_by_identifier`, `update_work_item`, `delete_work_item`, `search_work_items`

### Cycles / Sprints (12)
`list_cycles`, `create_cycle`, `retrieve_cycle`, `update_cycle`, `delete_cycle`, `list_archived_cycles`, `add_work_items_to_cycle`, `remove_work_item_from_cycle`, `list_cycle_work_items`, `transfer_cycle_work_items`, `archive_cycle`, `unarchive_cycle`

### Modules (11)
`list_modules`, `create_module`, `retrieve_module`, `update_module`, `delete_module`, `list_archived_modules`, `add_work_items_to_module`, `remove_work_item_from_module`, `list_module_work_items`, `archive_module`, `unarchive_module`

### Epics (5)
`list_epics`, `create_epic`, `retrieve_epic`, `update_epic`, `delete_epic`

### Milestones (8)
`list_milestones`, `create_milestone`, `retrieve_milestone`, `update_milestone`, `delete_milestone`, `add_work_items_to_milestone`, `remove_work_items_from_milestone`, `list_milestone_work_items`

### Initiatives (5)
`list_initiatives`, `create_initiative`, `retrieve_initiative`, `update_initiative`, `delete_initiative`

### Labels (5)
`list_labels`, `create_label`, `retrieve_label`, `update_label`, `delete_label`

### States (5)
`list_states`, `create_state`, `retrieve_state`, `update_state`, `delete_state`

### Work Item Comments (5)
`list_work_item_comments`, `create_work_item_comment`, `retrieve_work_item_comment`, `update_work_item_comment`, `delete_work_item_comment`

### Work Item Links (5)
`list_work_item_links`, `create_work_item_link`, `retrieve_work_item_link`, `update_work_item_link`, `delete_work_item_link`

### Work Item Relations (3)
`list_work_item_relations`, `create_work_item_relation`, `remove_work_item_relation`

### Work Item Activities (2)
`list_work_item_activities`, `retrieve_work_item_activity`

### Work Logs (4)
`list_work_logs`, `create_work_log`, `update_work_log`, `delete_work_log`

### Work Item Types (5)
`list_work_item_types`, `create_work_item_type`, `retrieve_work_item_type`, `update_work_item_type`, `delete_work_item_type`

### Work Item Properties (5)
`list_work_item_properties`, `create_work_item_property`, `retrieve_work_item_property`, `update_work_item_property`, `delete_work_item_property`

### Intake (5)
`list_intake_work_items`, `create_intake_work_item`, `retrieve_intake_work_item`, `update_intake_work_item`, `delete_intake_work_item`

### Pages (4)
`create_workspace_page`, `retrieve_workspace_page`, `create_project_page`, `retrieve_project_page`

**Total: 98 tools**

## Tool Name Resolution

All tool names above are **generic action names**. The actual MCP tool name depends on how Plane is connected — the prefix and structure vary across MCP servers, connectors, self-hosted instances, and cloud deployments. Never assume a specific prefix in this plugin.

To discover the real tool names for the current environment, follow the `connector-bootstrap` skill. In short: use `ToolSearch` with multiple queries (`plane`, `work_item`, `create_cycle`, domain keywords), match tools by the action suffix, and handle multiple instances when present.
