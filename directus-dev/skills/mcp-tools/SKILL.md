---
name: mcp-tools
description: All Directus MCP tools reference — action patterns, parameters, query system. This skill should be used when the user asks about "Directus MCP tools", "which Directus tools are available", "how to use Directus MCP", "Directus tool parameters", or needs to know which MCP operations are available for Directus and how to use them correctly.
---

# Directus MCP Tool Patterns

Reference for all 12 available MCP tools, their parameters, and usage patterns. The Directus MCP server is built in and needs Directus v11.12 or later (tested up to v12.4.1). It is disabled until an administrator enables it in Settings → AI → Model Context Protocol, and every call runs with the permissions of the connected user.

## Connection Modes

Directus offers two tool modes on the same endpoint:

| URL | The client sees | Use it when |
|-----|-----------------|-------------|
| `${DIRECTUS_URL}/mcp` (default) | The 12 tools below, each with its own description and approval setting | The client searches or loads tools on demand (Claude Code enables MCP tool search by default), or you want per-tool approval rules |
| `${DIRECTUS_URL}/mcp?tool_mode=registry` | Three root tools: `search`, `execute`, `schema` | The client sends every tool definition to the model up front, has no tool search, or hits a tool-count limit |

Prefer the default mode when the client already does tool search. Registry mode would duplicate that step.

Registry mode works in three steps:

1. `search` with a query to find the relevant tools
2. `search` with the chosen tool names to load their instructions and input types
3. `execute` with the tool name and its input (take the parameter names from step 2, not from memory)

`schema` stays a direct tool, because the data model is needed before almost any other call. Trade-offs: extra `search` calls add latency, and the client shows nearly everything as `execute`, so approval rules and allow lists cannot tell `items` from `files` or `collections`. Do not auto-approve `execute`: it runs reads and writes. Authentication, Directus permissions and the **Allow Deletes** setting behave the same in both modes.

Connect with OAuth where the client supports it (Claude Code, Claude Desktop, claude.ai, VS Code, Cursor, Raycast and ChatGPT do): no token in the URL or headers, and the user approves access in the browser. The server side needs `MCP_OAUTH_ENABLED=true`, a registration method (`MCP_OAUTH_CIMD_ENABLED=true`, preferred, or `MCP_OAUTH_DCR_ENABLED=true`) and `PUBLIC_URL`, then the matching toggles in the MCP settings. When the client cannot do OAuth, use a static token of a dedicated user, sent as `Authorization: Bearer <token>`. A client that only accepts a URL can pass it as `?access_token=<token>`, combined with the mode as `/mcp?tool_mode=registry&access_token=<token>`. A token in a URL ends up in logs, so prefer the header.

## Critical: The Action Pattern

Every Directus MCP tool uses a **unified action-based CRUD pattern**. Instead of separate tools per operation, each tool accepts an `action` parameter:

```
action: "create" | "read" | "update" | "delete"
```

Always include the `action` parameter. This is different from platforms with separate `list_*`, `create_*`, `get_*` tools.

## Getting Started

Always begin a session with these two calls:

1. Call `system-prompt` (no parameters) — returns the AI usage guidance the project administrator configured (it can be empty). It is not a generic Directus reference, so read it for instance rules and follow them
2. Call `schema` (no parameters) — discovers all collections (discovery mode)

## Tool Reference

| Tool | Actions | Purpose |
|------|---------|---------|
| `system-prompt` | — | Administrator-configured AI usage guidance. Call first. |
| `schema` | read | Explore data model — collections, fields, relations |
| `collections` | create, read, update, delete | Manage collections (tables) |
| `fields` | create, read, update, delete | Manage fields (columns) |
| `relations` | create, read, update, delete | Define relationships between collections |
| `items` | create, read, update, delete | CRUD data within collections |
| `files` | read, update, delete, import | File metadata and URL imports |
| `assets` | — | Retrieve base64 file content by ID |
| `folders` | create, read, update, delete | Virtual folders for files **and** for flows (`type: "files"` default, or `"flows"`) |
| `flows` | create, read, update, delete | Automation flow definitions (`folder` places a flow in a flow folder) |
| `operations` | create, read, update, delete | Operations within flows |
| `trigger-flow` | — | Execute flows programmatically |

## Schema Discovery

### Discovery Mode (list all collections)

```json
Tool: schema
Input: {}
```

Returns: `collections` (names), `collection_folders` (UI grouping), `notes` (descriptions).

### Detailed Mode (specific collections)

```json
Tool: schema
Input: { "keys": ["posts", "categories"] }
```

Returns: field definitions (type, validation, defaults) and relationship mappings.

## Items Tool — The Workhorse

### Read with Query

```json
Tool: items
Input: {
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["id", "title", "status", "author.name"],
    "filter": { "status": { "_eq": "published" } },
    "sort": ["-date_created"],
    "limit": 25
  }
}
```

### Create Items

**Critical: `data` is ALWAYS an array**, even for a single item.

```json
Tool: items
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "title": "New Post",
    "status": "draft",
    "content": "Post content here"
  }]
}
```

### Update Items

```json
Tool: items
Input: {
  "action": "update",
  "collection": "posts",
  "keys": ["uuid-1"],
  "data": { "status": "published" }
}
```

### Delete Items

```json
Tool: items
Input: {
  "action": "delete",
  "collection": "posts",
  "keys": ["uuid-1", "uuid-2"]
}
```

## Collections Tool

### Create Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "articles",
    "schema": {},
    "meta": {
      "icon": "article",
      "note": "Blog articles",
      "color": "#2196F3"
    }
  }]
}
```

Use `"schema": {}` for real tables, `"schema": null` for folder-only collections.

## Fields Tool

### Create Fields

**Critical: `data` is ALWAYS an array** of field objects.

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "articles",
  "data": [{
    "field": "title",
    "type": "string",
    "meta": { "interface": "input", "note": "Article title" },
    "schema": { "is_nullable": false }
  }]
}
```

### Field Types

`string` (max 255), `text` (unlimited), `uuid`, `hash`, `integer`, `bigInteger`, `float`, `decimal`, `timestamp`, `datetime`, `date`, `time`, `boolean`, `json`, `csv`, `alias` (virtual/relational).

## Relations Tool

### Create M2O Relation

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "author",
  "data": {
    "collection": "posts",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

## Query System

Shared across `items`, `files`, `folders`, `flows`, `operations`:

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | string[] | Field selection. Supports dot notation: `["title", "author.name"]`, wildcard: `["*"]` |
| `filter` | object | Filter operators (see below) |
| `sort` | string[] | Sort fields. Prefix `-` for descending: `["-date_created"]` |
| `limit` | number | Max results |
| `offset` | number | Skip N results |
| `page` | number | Page number (with limit) |
| `search` | string | Full-text search |
| `deep` | object | Nested relation filtering/sorting/limiting |
| `aggregate` | object | Aggregation: `{ count: ["*"], sum: ["price"], avg: ["rating"] }` |
| `groupBy` | string[] | Group results |
| `version` | string | Read a content version of a versioned collection: `"draft"`, `"published"` or a custom version key (`"main"` still works as an alias for `"published"`) |
| `versionRaw` | boolean | With `version`, return the raw relational delta of the version instead of the merged item. Single-item reads only |

### Reading Content Versions

For collections with `versioning: true`, read the pending draft of an item instead of the published item:

```json
Tool: items
Input: {
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["id", "title", "status"],
    "filter": { "id": { "_eq": "uuid-1" } },
    "version": "draft"
  }
}
```

Versioned items carry a `$meta` field with the version id. Relational data of a version must be requested with explicit field expansion (`"tags.*"`). Requesting a version that does not exist returns Forbidden (403), it does not fall back to the published item. That includes `"draft"` for an item with no saved draft. Publishing a version (promote) is a REST call, see `api-reference`.

### Filter Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `_eq` | Equals | `{ "status": { "_eq": "active" } }` |
| `_neq` | Not equals | `{ "status": { "_neq": "draft" } }` |
| `_in` | In array | `{ "status": { "_in": ["active", "published"] } }` |
| `_nin` | Not in array | `{ "role": { "_nin": ["admin"] } }` |
| `_null` | Is null | `{ "deleted_at": { "_null": true } }` |
| `_nnull` | Is not null | `{ "author": { "_nnull": true } }` |
| `_gt` / `_gte` | Greater than | `{ "price": { "_gt": 100 } }` |
| `_lt` / `_lte` | Less than | `{ "price": { "_lt": 50 } }` |
| `_between` | Between | `{ "price": { "_between": [10, 100] } }` |
| `_contains` | Contains (case-sensitive) | `{ "title": { "_contains": "Guide" } }` |
| `_icontains` | Contains (case-insensitive) | `{ "title": { "_icontains": "guide" } }` |
| `_starts_with` | Starts with | `{ "name": { "_starts_with": "A" } }` |
| `_ends_with` | Ends with | `{ "email": { "_ends_with": ".com" } }` |
| `_empty` / `_nempty` | Empty / not empty | `{ "tags": { "_empty": false } }` |
| `_some` / `_none` | O2M: some/none match | `{ "comments": { "_some": { "status": { "_eq": "approved" } } } }` |

### Logical Operators

```json
{
  "_and": [
    { "status": { "_eq": "published" } },
    { "date": { "_gte": "2024-01-01" } }
  ]
}
```

```json
{
  "_or": [
    { "role": { "_eq": "admin" } },
    { "role": { "_eq": "editor" } }
  ]
}
```

### Deep Queries

Filter/sort/limit nested relations:

```json
{
  "fields": ["title", "comments.text", "comments.author.name"],
  "deep": {
    "comments": {
      "_filter": { "status": { "_eq": "approved" } },
      "_sort": ["-date_created"],
      "_limit": 5
    }
  }
}
```

## Best Practices

- Always call `schema` before write operations to understand field requirements
- Use `fields` parameter to reduce response size — avoid fetching `["*"]` on large collections
- Filter server-side rather than fetching everything
- Paginate large datasets with `limit` and `offset`
- Process batch creates in groups of 10-25 items
- Check results after write operations
- Use `search` for full-text queries, `filter` for precise matching

## Error Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| "action is required" | Missing action parameter | Add `"action": "read"` (or create/update/delete) |
| "collection is required" | Missing collection name | Add `"collection": "your_collection"` |
| "data must be an array" | `data` passed as object instead of array | Wrap in array: `"data": [{ ... }]` — even for a single item |
| 404 Not Found | Item/collection doesn't exist | Verify name with `schema` tool |
| 403 Forbidden | Insufficient permissions | Check the policies attached to the MCP user, directly or through its role (`troubleshoot` skill) |
| 403 `COLLECTION_INACTIVE` | The collection status is Inactive (Directus 12.4+) | Set it back to Active in the collection settings |
| 422 Validation | Required field missing or wrong type | Read schema first, check field types |
