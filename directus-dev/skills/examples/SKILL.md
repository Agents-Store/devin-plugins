---
name: examples
description: End-to-end workflow examples, tool call patterns, and scenario walkthroughs for Directus MCP. This skill should be used when the user needs complete working examples, reference implementations, step-by-step walkthroughs, or tool call patterns for Directus.
---

# Examples & Scenarios

End-to-end walkthroughs and reference implementations for common Directus tasks.

## Quick Reference: Tools by Group

| Group | Tools | Use For |
|-------|-------|---------|
| Discovery | `system-prompt`, `schema` | Explore instance, understand data model |
| Data Model | `collections`, `fields`, `relations` | Build/modify schema |
| Content | `items` | CRUD data, queries, aggregation |
| Files | `files`, `assets`, `folders` | Manage uploads, organize media |
| Automation | `flows`, `operations`, `trigger-flow` | Event-driven workflows |

## Reference Files

| File | Description |
|------|-------------|
| [tool-patterns.md](references/mcp/tool-patterns.md) | Exact JSON for every tool and action |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step workflows end-to-end |
| [blog-cms.md](references/scenarios/blog-cms.md) | Complete blog CMS schema build |
| [ecommerce-catalog.md](references/scenarios/ecommerce-catalog.md) | E-commerce catalog with products, variants, orders |

## Quick Walkthrough: Explore → Build → Populate

**Every workflow starts with schema discovery.** Before creating collections, fields, or items, always call `schema {}` first to understand what already exists. This prevents duplicate collections, reveals existing field names, and ensures correct dependency ordering.

### 1. Explore the Instance (always do this first)

```json
Tool: schema
Input: {}
```

### 2. Inspect a Collection

```json
Tool: schema
Input: { "keys": ["posts"] }
```

### 3. Create a New Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "projects",
    "schema": {},
    "meta": { "icon": "work", "display_template": "{{name}}" }
  }]
}
```

### 4. Add Fields

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "projects",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "description", "type": "text", "meta": { "interface": "input-rich-text-md" } },
    { "field": "status", "type": "string", "meta": { "interface": "select-dropdown", "options": { "choices": [{"text": "Active", "value": "active"}, {"text": "Completed", "value": "completed"}] } }, "schema": { "default_value": "active" } }
  ]
}
```

### 5. Create Items

```json
Tool: items
Input: {
  "action": "create",
  "collection": "projects",
  "data": [
    { "name": "Website Redesign", "description": "Complete overhaul of company website", "status": "active" },
    { "name": "Mobile App", "description": "iOS and Android app development", "status": "active" }
  ]
}
```

### 6. Query Items

```json
Tool: items
Input: {
  "action": "read",
  "collection": "projects",
  "query": {
    "filter": { "status": { "_eq": "active" } },
    "sort": ["name"]
  }
}
```
