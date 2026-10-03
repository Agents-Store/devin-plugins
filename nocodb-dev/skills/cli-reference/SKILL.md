---
name: cli-reference
description: |
  Command-line access to NocoDB for schema work — curl recipes on Meta API v3 by resource, mapped to the commands of the official nocodb.sh script (installed with npx skills add nocodb/agent-skills). Loaded only on explicit cite. Use when:
  - "NocoDB CLI"
  - "NocoDB command line schema commands"
  - "how do I create a table with curl"
  - "nocodb.sh commands"
  - "NocoDB agent-skills CLI"
disable-model-invocation: true
---

# NocoDB from the Command Line — curl Recipes and the Official Script

NocoDB has **no standalone `nc` binary** — on Linux and macOS `nc` is the netcat utility and must not be used. The official command-line tool is the Bash script `nocodb.sh` (needs `curl` and `jq`), published as an agent skill. This plugin does **not** bundle it; every recipe here is plain `curl` on the Meta API v3, and each is mapped to the script command that does the same job.

Prefer the MCP schema tools on Cloud / licensed self-hosted (see **mcp-patterns**); use these recipes on Community Edition, in scripts, and as the fallback.

## The Official Script (optional)

```bash
npx skills add nocodb/agent-skills
```

- The script is `scripts/nocodb.sh` inside the installed `nocodb` skill directory; that skill's README gives the exact path for your agent. Run it by that path, for example `"$NOCODB_SH" table:list <baseId>` after `export NOCODB_SH=<path to nocodb.sh>`.
- It reads `NOCODB_TOKEN`, `NOCODB_URL` (default `https://app.nocodb.com`) and `NOCODB_VERBOSE`.
- It accepts **names** or **IDs** for bases, tables and views; set `NOCODB_VERBOSE=1` to see how names resolve.
- It has no commands for hooks, select-choice options or view field lists — use the recipes below for those.

## Setup for the curl Recipes

```bash
export NOCODB_URL="https://your-instance.example.com"   # required for self-hosted
export NOCODB_TOKEN="your-api-token"                    # NocoDB → Team & Settings → API Tokens → Add New Token
```

A one-line wrapper keeps repeated calls short (paths are under `/api/v3`):

```bash
nocodb_api() {   # nocodb_api METHOD /meta/... ['{"json":"body"}']
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}
# nocodb_api GET /meta/bases/$BASE_ID/tables
```

## Plan Requirements

- **All plans:** Base, Table, Field, Filter, Sort, Record, Link, Attachment APIs.
- **Cloud Business and above / licensed self-hosted:** Hooks, Comments, Workflows, Documents, Base collaboration.
- **Cloud Enterprise / licensed self-hosted:** Views, Dashboards, Scripts.
- **Workspace** list/create is open; per-workspace changes, Teams and Tokens depend on the plan (see **api-reference** → Plan Availability).

## ID Prefixes

| Prefix | Meaning |
|--------|---------|
| `w...` | Workspace |
| `p...` | Base (project) |
| `m...` | Table (model) |
| `c...` | Field (column) |
| `vw...` | View |

Hierarchy: `WORKSPACE → BASE → TABLE → VIEW/FIELD → RECORD`.

## Command Map — `nocodb.sh` → REST (Meta API v3)

Paths are relative to `${NOCODB_URL}/api/v3`.

| Resource | Script command | REST call |
|----------|----------------|-----------|
| Workspaces | `workspace:list` / `workspace:get` | `GET /meta/workspaces`, `GET /meta/workspaces/{workspaceId}` |
| Bases | `base:list <ws>` | `GET /meta/workspaces/{workspaceId}/bases` |
| | `base:get` / `base:update` / `base:delete` | `GET` / `PATCH` / `DELETE /meta/bases/{baseId}` |
| | `base:create <ws> '{…}'` | `POST /meta/workspaces/{workspaceId}/bases` |
| Tables | `table:list` / `table:create` | `GET` / `POST /meta/bases/{baseId}/tables` |
| | `table:get` / `table:update` / `table:delete` | `GET` / `PATCH` / `DELETE /meta/bases/{baseId}/tables/{tableId}` |
| Fields | `field:list` | `GET /meta/bases/{baseId}/tables/{tableId}` — the `fields` array |
| | `field:create` | `POST /meta/bases/{baseId}/tables/{tableId}/fields` |
| | `field:get` / `field:update` / `field:delete` | `GET` / `PATCH` / `DELETE /meta/bases/{baseId}/fields/{fieldId}` |
| | *(none)* add / remove select choices | `POST` / `DELETE /meta/bases/{baseId}/fields/{fieldId}/options` |
| Views | `view:list` / `view:create` | `GET` / `POST /meta/bases/{baseId}/tables/{tableId}/views` (type in the body: `{"title":"…","type":"grid"}`) |
| | `view:get` / `view:update` / `view:delete` | `GET` / `PATCH` / `DELETE /meta/bases/{baseId}/views/{viewId}` |
| | *(none)* show / hide / order fields | `PATCH …/views/{viewId}` with the complete ordered `fields` list |
| Filters | `filter:list` / `filter:create` | `GET` / `POST /meta/bases/{baseId}/views/{viewId}/filters` (`PUT` replaces the set) |
| | *(update / delete)* | `PATCH` / `DELETE /meta/bases/{baseId}/filters/{filterId}` |
| Sorts | `sort:list` / `sort:create` | `GET` / `POST /meta/bases/{baseId}/views/{viewId}/sorts` |
| | *(update / delete)* | `PATCH` / `DELETE /meta/bases/{baseId}/sorts/{sortId}` |
| Hooks | *(none)* | `GET` / `POST /meta/bases/{baseId}/tables/{tableId}/hooks`; `GET` / `PATCH` / `DELETE /meta/bases/{baseId}/hooks/{hookId}` |
| Scripts | `script:list` / `script:create` | `GET` / `POST /meta/bases/{baseId}/scripts` |
| Teams | `team:list` / `team:create` | `GET` / `POST /meta/workspaces/{workspaceId}/teams` |
| Tokens | `token:list` / `token:create` / `token:delete` | `GET` / `POST /meta/tokens`, `DELETE /meta/tokens/{tokenId}` |
| Links | `link:list` / `link:add` / `link:remove` | `GET` / `POST` / `DELETE /data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` |
| Attachments | `attachment:upload` | `POST /data/{baseId}/{modelId}/records/{recordId}/fields/{fieldId}/upload` |
| Public view links | *(none)* | not in the REST spec — MCP `shareView` on Cloud / licensed, or the UI |

## Schema Quick Reference (curl)

```bash
# Bases
nocodb_api GET    /meta/workspaces/$WORKSPACE_ID/bases
nocodb_api POST   /meta/workspaces/$WORKSPACE_ID/bases '{"title":"New Base"}'
nocodb_api GET    /meta/bases/$BASE_ID
nocodb_api PATCH  /meta/bases/$BASE_ID '{"title":"Renamed"}'

# Tables
nocodb_api GET    /meta/bases/$BASE_ID/tables
nocodb_api POST   /meta/bases/$BASE_ID/tables '{"title":"Customers"}'
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID
nocodb_api PATCH  /meta/bases/$BASE_ID/tables/$TABLE_ID '{"title":"Renamed"}'
nocodb_api DELETE /meta/bases/$BASE_ID/tables/$TABLE_ID

# Fields
nocodb_api POST   /meta/bases/$BASE_ID/tables/$TABLE_ID/fields '{"title":"Phone","type":"PhoneNumber"}'
nocodb_api PATCH  /meta/bases/$BASE_ID/fields/$FIELD_ID '{"title":"Mobile"}'
nocodb_api DELETE /meta/bases/$BASE_ID/fields/$FIELD_ID

# Views (cloud Enterprise / licensed self-hosted)
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID/views
nocodb_api POST   /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{"title":"All","type":"grid"}'
nocodb_api POST   /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{"title":"Pipeline","type":"kanban","options":{"stack_by":{"field_id":"<singleSelectFieldId>"}}}'
nocodb_api PATCH  /meta/bases/$BASE_ID/views/$VIEW_ID '{"title":"Renamed"}'
nocodb_api DELETE /meta/bases/$BASE_ID/views/$VIEW_ID

# Sorts & Filters (per view)
nocodb_api POST   /meta/bases/$BASE_ID/views/$VIEW_ID/sorts   '{"field_id":"<fieldId>","direction":"desc"}'
nocodb_api POST   /meta/bases/$BASE_ID/views/$VIEW_ID/filters '{"field_id":"<fieldId>","operator":"eq","value":"Active"}'

# Webhooks
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID/hooks
nocodb_api POST   /meta/bases/$BASE_ID/tables/$TABLE_ID/hooks '<HookV3Create JSON>'
nocodb_api PATCH  /meta/bases/$BASE_ID/hooks/$HOOK_ID '{"active":false}'
nocodb_api DELETE /meta/bases/$BASE_ID/hooks/$HOOK_ID
```

## See Reference Files

- **`references/base-table-field.md`** — bases, tables, fields, select options, field types
- **`references/view-filter-sort.md`** — views, filters, sorts, field lists per view
- **`references/relations-links.md`** — link / lookup / rollup setup

## Filter Syntax in Record Queries

The `where` grammar `(field,operator,value)` for the Data API and for MCP `queryRecords` is documented in `nocodb-ops/skills/cli-reference/references/filter-syntax.md`. View filters (this plugin) use structured `{field_id, operator, value}` objects instead.

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `nc` hangs or prints a netcat error | `nc` is netcat, not a NocoDB tool | Use `curl` (this skill) or `nocodb.sh` |
| `NOCODB_TOKEN required` / empty `xc-token` header | Token env-var missing | `export NOCODB_TOKEN=...` |
| 401 Unauthorized | Token wrong or revoked | Regenerate in NocoDB → Team & Settings → API Tokens |
| 403 Forbidden | Token lacks permission for that base, or the plan lacks the API | Share the base with the token's user; check **api-reference** → Plan Availability |
| `Could not resolve name "X"` (script) | Name not unique or wrong scope | Pass IDs instead of names; set `NOCODB_VERBOSE=1` |
| `Field type X not supported` | Type spelling | Check `field-types.md` for the canonical names — CamelCase, e.g. `LinkToAnotherRecord`, not `link_to_another_record` |

## When to Use What

| Situation | Use |
|-----------|-----|
| Cloud / licensed, interactive work in Claude | MCP `listTools` → `callTool` |
| One-off table or field tweak from a shell | `nocodb.sh` (names resolve for you) or `curl` |
| Scripted multi-step migration | `curl` / the `nocodb_api` wrapper with IDs |
| Community Edition | `curl` — the MCP server has record tools only |
| Webhook config | `curl` (the script has no hook commands) or MCP `createHook` |
