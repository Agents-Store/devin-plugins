---
name: cli-reference
description: |
  Command-line access to NocoDB data -- curl recipes on the Data API v3 (records, links, attachments) and Meta API v3, mapped to the commands of the official nocodb.sh script (installed with npx skills add nocodb/agent-skills). Loaded only on explicit cite. Use when:
  - "NocoDB CLI commands"
  - "NocoDB curl recipes"
  - "NocoDB agent-skills"
  - "what CLI commands are available"
  - "nocodb.sh commands"
disable-model-invocation: true
---

# NocoDB from the Command Line -- curl Recipes and the Official Script

NocoDB has **no standalone `nc` binary** -- on Linux and macOS `nc` is the netcat utility and must not be used for NocoDB. The official command-line tool is the Bash script `nocodb.sh` (needs `curl` and `jq`), published as an agent skill. This plugin does **not** bundle it; every recipe here is plain `curl` on the NocoDB v3 REST API, and each one is mapped to the script command that does the same job.

Prefer the MCP tools (see **mcp-patterns**) for interactive work; use these recipes in scripts, on a machine without the MCP connection, and for the few things MCP does not cover (such as attachment upload).

## The Official Script (optional)

```bash
npx skills add nocodb/agent-skills
```

- The script is `scripts/nocodb.sh` inside the installed `nocodb` skill directory; that skill's README gives the exact path for your agent. Run it by that path, for example `"$NOCODB_SH" record:list <baseId> <tableId>` after `export NOCODB_SH=<path to nocodb.sh>`.
- It reads `NOCODB_TOKEN`, `NOCODB_URL` (default `https://app.nocodb.com`) and `NOCODB_VERBOSE`.
- It accepts **names** or **IDs** for bases, tables and views; set `NOCODB_VERBOSE=1` to see how names resolve.

## Setup for the curl Recipes

```bash
export NOCODB_URL="https://your-instance.example.com"   # required for self-hosted
export NOCODB_TOKEN="your-api-token"                    # NocoDB → Team & Settings → API Tokens → Add New Token
```

A one-line wrapper keeps repeated calls short (paths are under `/api/v3`):

```bash
nocodb_api() {   # nocodb_api METHOD /path ['{"json":"body"}']
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}
# nocodb_api GET /data/$BASE_ID/$TABLE_ID/count
```

`NOCODB_TOKEN` is the **API token**. It is distinct from `NOCODB_MCP_TOKEN` (the MCP connection token, used only by `.mcp.json`).

## Plan Requirements

- **All plans:** Base, Table, Field, Filter, Sort, Record, Link, Attachment APIs.
- **Cloud Business and above / licensed self-hosted:** Hooks, Comments, Workflows, Documents, Base collaboration.
- **Cloud Enterprise / licensed self-hosted:** Views, Dashboards, Scripts.
- **Workspace** list/create is open; per-workspace changes, Teams and Tokens depend on the plan.

## ID Prefixes

| Prefix | Meaning |
|--------|---------|
| `w...` | Workspace |
| `p...` | Base (project) |
| `m...` | Table (model) |
| `c...` | Field (column) |
| `vw...` | View |

Hierarchy: `WORKSPACE → BASE → TABLE → VIEW/FIELD → RECORD`. Record paths take the base **and** the table ID: `/data/{baseId}/{tableId}/...`.

## Command Map -- `nocodb.sh` → REST (v3)

Paths are relative to `${NOCODB_URL}/api/v3`.

| Resource | Script command | REST call |
|----------|----------------|-----------|
| Workspaces | `workspace:list` / `workspace:get` | `GET /meta/workspaces`, `GET /meta/workspaces/{workspaceId}` |
| Bases | `base:list <ws>` / `base:get` | `GET /meta/workspaces/{workspaceId}/bases`, `GET /meta/bases/{baseId}` |
| Tables | `table:list` / `table:get` | `GET /meta/bases/{baseId}/tables`, `GET /meta/bases/{baseId}/tables/{tableId}` |
| Fields | `field:list` | `GET /meta/bases/{baseId}/tables/{tableId}` -- the `fields` array |
| Records | `record:list` | `GET /data/{baseId}/{tableId}/records` (`where`, `sort`, `fields`, `page`, `pageSize`, `viewId` query parameters) |
| | `record:get` | `GET /data/{baseId}/{tableId}/records/{recordId}` |
| | `record:create` | `POST /data/{baseId}/{tableId}/records` -- body `[{"fields":{…}}]` |
| | `record:update` / `record:update-many` | `PATCH /data/{baseId}/{tableId}/records` -- body `[{"id":…,"fields":{…}}]` |
| | `record:delete` | `DELETE /data/{baseId}/{tableId}/records` -- body `[{"id":…}]` |
| | `record:count` | `GET /data/{baseId}/{tableId}/count` (`where`, `viewId`) |
| | *(none)* upsert | `POST /data/{baseId}/{tableId}/records/upsert` |
| Links | `link:list` / `link:add` / `link:remove` | `GET` / `POST` / `DELETE /data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` |
| Attachments | `attachment:upload` | `POST /data/{baseId}/{tableId}/records/{recordId}/fields/{fieldId}/upload` |
| Buttons | `action:trigger` | `POST /data/{baseId}/{tableId}/actions/{buttonFieldId}` |
| Views | `view:list` / `view:get` | `GET /meta/bases/{baseId}/tables/{tableId}/views`, `GET /meta/bases/{baseId}/views/{viewId}` |
| Filters | `filter:list` | `GET /meta/bases/{baseId}/views/{viewId}/filters` |
| Sorts | `sort:list` | `GET /meta/bases/{baseId}/views/{viewId}/sorts` |
| Where help | `where:help` | see `references/filter-syntax.md` |

Schema writes (create / change tables, fields, views, hooks) are the job of the **nocodb-dev** plugin; its `cli-reference` skill carries the full write-side command map.

## Data Quick Reference (curl)

```bash
# List — page 1, 50 per page, sorted, filtered (URL-encode the JSON and the where string)
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records?pageSize=50&page=1&sort=%5B%7B%22field%22%3A%22Name%22%2C%22direction%22%3A%22asc%22%7D%5D"

# One record, a count
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records/31"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/count"

# Create / update / delete — bodies are arrays
nocodb_api POST   /data/$BASE_ID/$TABLE_ID/records '[{"fields":{"Name":"Alice"}}]'
nocodb_api PATCH  /data/$BASE_ID/$TABLE_ID/records '[{"id":31,"fields":{"Status":"Done"}}]'
nocodb_api DELETE /data/$BASE_ID/$TABLE_ID/records '[{"id":31}]'
```

`sort` is a JSON array of `{"field","direction"}` objects (`asc` | `desc`), exactly as in the MCP `queryRecords` tool. The `where` string uses the grammar in `references/filter-syntax.md` -- dates carry a sub-operator (`exactDate`) and ranges are two bounds, on REST as on MCP.

## See Reference Files

- **`references/record-link.md`** -- records, linked records, attachments, button actions (curl)
- **`references/filter-syntax.md`** -- the complete `where` filter syntax for REST and MCP queries
- **`references/view-filter-sort.md`** -- reading views, filters and sorts (curl)
- **`references/base-table-field.md`** -- reading workspaces, bases, tables and fields (curl)

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `nc` hangs or prints a netcat error | `nc` is netcat, not a NocoDB tool | Use `curl` (this skill) or `nocodb.sh` |
| `NOCODB_TOKEN required` / empty `xc-token` header | Token env var missing | `export NOCODB_TOKEN=...` |
| 401 Unauthorized | Token wrong or revoked | Regenerate in NocoDB → Team & Settings → API Tokens |
| 403 Forbidden | Token lacks permission for that base, or the plan lacks the API | Share the base with the token's user; check the plan list above |
| `Could not resolve name "X"` (script) | Name not unique or wrong scope | Pass IDs instead of names; set `NOCODB_VERBOSE=1` |
| Error on a date filter | Bare date in `where`, or `btw` on a date | `(Date,gte,exactDate,2026-06-01)~and(Date,lte,exactDate,2026-06-30)` |
