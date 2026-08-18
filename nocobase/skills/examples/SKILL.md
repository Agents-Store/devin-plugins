---
name: examples
description: Application design scenarios and reference implementations. This skill should be used when the user needs complete application examples, tool call patterns, or end-to-end workflow references.
---

# Examples & References

This skill provides complete application design scenarios for NocoBase platform development.

## Reference Files

| File | Description |
|------|-------------|
| [crm-application.md](references/scenarios/crm-application.md) | Complete CRM application design with collections, relations, workflows, and UI |
| [project-management.md](references/scenarios/project-management.md) | Project management app with tasks, timelines, and kanban boards |
| [tool-patterns.md](references/mcp/tool-patterns.md) | Exact MCP tool call patterns with input/output examples for all 15 tools |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step MCP workflows — build pages, seed data, audit application |

## NocoBase Feature Overview

### Data Modeling
- Collections (tables) with 20+ field types
- Relations: hasOne, hasMany, belongsTo, belongsToMany
- Inheritance and tree structures
- Formula and sequence fields

### Workflows
- Collection event triggers (CRUD)
- Scheduled triggers (cron)
- Action triggers (button click)
- 10+ node types: condition, query, create, update, delete, request, manual, loop, parallel, delay

### UI Blocks
- Table, Form, Details, Kanban, Calendar, Gantt, Chart, List, Grid Card, Markdown, Iframe
- Configurable actions (CRUD, export, custom)
- Field components and layout

### Plugin System
- Server-side: collections, actions, resources, middleware, migrations
- Client-side: components, schema initializers, settings
- Full lifecycle management
