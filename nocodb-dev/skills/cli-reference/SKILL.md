---
name: cli-reference
description: |
  NocoDB `nc` CLI reference — schema-focused commands for tables, fields, views, links, hooks. Loaded only on explicit cite. Use when:
  - "nc CLI commands"
  - "NocoDB CLI schema commands"
  - "how do I create a table from the CLI"
  - "nc field:create reference"
  - "NocoDB agent-skills CLI"
disable-model-invocation: true
---

# NocoDB CLI — Schema Commands

Imported from the official `nocodb/agent-skills` CLI. Schema-focused (table / field / view / link / hook). Record-CRUD commands are documented in `nocodb-ops/cli-reference` if you need them in a dev workflow.

## Platform Support

- **Linux / macOS**: `scripts/nocodb.sh` (Bash, requires `curl` and `jq`)
- **Windows**: PowerShell 5.1+

## Plan Requirements

- **FREE**: Base, Table, Field, Filter, Sort, Record, Link, Attachment APIs
- **ENTERPRISE** (self-hosted or cloud): Workspace + Workspace Collaboration, Base Collaboration, View, Script, Team, API Token, Hook config UI

## Setup

```bash
export NOCODB_URL="https://your-instance.com"     # required for self-hosted
export NOCODB_API_TOKEN="your-api-token"
export NOCODB_VERBOSE=1                            # optional — print resolved IDs
```

Get an API token at NocoDB → Account Settings → API Tokens → Add New Token.

## Installation

```bash
npx skills add nocodb/agent-skills
```

## Argument Order & ID Prefixes

Commands follow a hierarchical pattern: `WORKSPACE → BASE → TABLE → VIEW/FIELD → RECORD`.

Pass **names** (human-readable) or **IDs** (faster, from NocoDB). Set `NOCODB_VERBOSE=1` to see how the CLI resolves a name to an ID.

| Prefix | Meaning |
|--------|---------|
| `w...` | Workspace |
| `p...` | Base (project) |
| `m...` | Table (model) |
| `c...` | Column / field |
| `vw...` | View |

## Schema Quick Reference

```bash
# Bases
nc base:list <workspaceId>
nc base:create <workspaceId> '{"title":"New Base"}'
nc base:get <baseId>
nc base:update <baseId> '{"title":"Renamed"}'
nc base:delete <baseId>

# Tables
nc table:list <baseId>
nc table:create <baseId> '{"title":"Customers"}'
nc table:get <baseId> <tableId>
nc table:update <baseId> <tableId> '{"title":"Renamed"}'
nc table:delete <baseId> <tableId>

# Fields
nc field:list <baseId> <tableId>
nc field:get <baseId> <tableId> <columnId>
nc field:create <baseId> <tableId> '{"title":"Phone","type":"PhoneNumber"}'
nc field:update <baseId> <tableId> <columnId> '{"title":"Mobile"}'
nc field:delete <baseId> <tableId> <columnId>

# Views (Enterprise)
nc view:list <baseId> <tableId>
nc view:create:grid     <baseId> <tableId> '{"title":"All"}'
nc view:create:kanban   <baseId> <tableId> '{"title":"Pipeline","fk_grp_col_id":"<columnId>"}'
nc view:create:gallery  <baseId> <tableId> '{"title":"Catalog","fk_cover_image_col_id":"<columnId>"}'
nc view:create:form     <baseId> <tableId> '{"title":"Intake"}'
nc view:create:calendar <baseId> <tableId> '{"title":"Schedule","calendar_range":[{"fk_from_column_id":"<columnId>"}]}'
nc view:update <viewId> '{"title":"Renamed"}'
nc view:delete <viewId>

# Sorts & Filters (per view)
nc sort:list   <viewId>
nc sort:create <viewId> '{"fk_column_id":"<columnId>","direction":"desc"}'
nc filter:list   <viewId>
nc filter:create <viewId> '{"fk_column_id":"<columnId>","comparison_op":"eq","value":"Active"}'

# Webhooks
nc hook:list   <baseId> <tableId>
nc hook:create <baseId> <tableId> '<HookV3Create JSON>'
nc hook:update <hookId> '<HookV3Update JSON>'
nc hook:delete <hookId>
```

## See Reference Files

- **`references/base-table-field.md`** — bases, tables, fields, all 30 supported field types
- **`references/view-filter-sort.md`** — views, filters, sorts (Enterprise)
- **`references/relations-links.md`** — link / lookup / rollup setup via CLI

## Filter Syntax in CLI

Same `(field,operator,value)` grammar as MCP queries — see `nocodb-ops/skills/cli-reference/references/filter-syntax.md` if you need the operator catalog.

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `nc: command not found` | CLI not installed | `npx skills add nocodb/agent-skills` |
| `Error: NOCODB_API_TOKEN is not set` | Token env-var missing | `export NOCODB_API_TOKEN=...` |
| 401 Unauthorized | Token wrong or revoked | Regenerate in NocoDB → Account Settings → API Tokens |
| 403 Forbidden | Token lacks permission for that base | Share the base with the token's user |
| `Could not resolve name "X"` | Name not unique or wrong scope | Pass IDs instead of names; or set `NOCODB_VERBOSE=1` to see what's being resolved |
| `Field type X not supported` | Type spelling | Check `field-types.md` for canonical names — they're CamelCase, e.g. `LinkToAnotherRecord`, not `link_to_another_record` |

## Why Use the CLI Over the API

| When | Use |
|------|-----|
| One-off table or field tweak | CLI |
| Scripted multi-step migration | API (or shell loop over CLI) |
| Discoverability & verbosity | CLI with `NOCODB_VERBOSE=1` |
| Embedding in another binary | API |
| Webhook / Hook config | Either — CLI is faster to type, API gives structured errors |
