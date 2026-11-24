---
name: mcp-patterns
description: |
  NocoDB MCP for schema-development work — what the server lists directly, which schema tools need listTools/callTool (/mcp-discovery and servers before 2026.10.1), and the Community vs Cloud/licensed contract. Use when:
  - "what MCP tools can I use for schema?"
  - "can MCP create tables / fields / views?"
  - "listTools / callTool"
  - "how do I discover NocoDB structure?"
  - "MCP for nocodb-dev"
---

# NocoDB MCP — Discovery and Schema Writes

All tools use the `mcp__plugin_nocodb-dev_nocodb__` prefix (the server is declared in this plugin's `.mcp.json`).

## The Contract: Community vs Cloud / Licensed

| Edition | What the MCP server offers | Schema writes go through |
|---------|----------------------------|--------------------------|
| **Community Edition** | Record tools and read tools only | **REST** (`curl` on Meta API v3) — see **api-reference** |
| **Cloud / licensed self-hosted** | The same read and record tools, plus schema, view, hook, workflow, dashboard, script, permission, RLS, classic-app and docs **write** tools. From **2026.10.1** the `/mcp` endpoint lists every tool; on `/mcp-discovery` (the endpoint for clients that cap the tool list at 100) and on servers older than 2026.10.1 the write tools stay out of the list | **MCP first**: call the tool when it is listed, otherwise `listTools(category)` → `callTool(name, arguments)`; REST is the fallback |

Rule of thumb for every skill in this plugin: **on Cloud/licensed, prefer the MCP write tools; on Community Edition — or when a tool is neither listed nor in the `listTools` answer — use REST.**

Which endpoint the plugin talks to is set by `NOCODB_MCP_URL`. The default `/mcp` URL gives every tool directly. Point it at `/mcp-discovery` only for a client that cannot take more than 100 tools (source: https://nocodb.com/docs/mcp, 2026-11-05).

### Detect the edition once per session

Look at the tools the server lists. If `createTable` is among them, this is Cloud/licensed on the full endpoint — call the write tools directly. Otherwise ask for the hidden ones:

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "tables"
```

- `createTable` is listed, or the answer names `createTable` / `updateTable` / `deleteTable` → Cloud/licensed. Use MCP-first.
- `createTable` is not listed, and `listTools` is absent, errors, or the `tables` category is empty → Community Edition. Use REST.

`whoami` shows which user and which base the MCP credential is pinned to; effective authority is the intersection of that grant and the user's role on each resource — a 403 on a write usually means the role is not an editor/creator, not a missing tool.

## Two Kinds of Tools

On the full `/mcp` endpoint (2026.10.1 and later) every tool is listed and the second table below is only a map of what exists — call each tool by its name. The split matters on `/mcp-discovery`, on servers older than 2026.10.1 and on Community Edition.

**Listed directly** (read tools and record CRUD — visible on every endpoint):

| Group | Tools |
|-------|-------|
| Orientation | `whoami`, `getBaseInfo`, `getBaseSchema` (every table with fields, options and views in **one** call), `getTablesList`, `getTableSchema` |
| Schema reads | `listFields`, `getField`, `getFieldOptionsSchema(type)`, `listViews`, `getView`, `listFilters`, `listSorts`, `listHooks`, `getHook`, `listWorkflows`, `getWorkflow`, `listDashboards`, `listScripts`, `listBaseMembers` |
| Records | `queryRecords`, `getRecord`, `countRecords`, `createRecords`, `updateRecords`, `deleteRecords`, `aggregate`, `groupByRecords`, `linkRecords`, `unlinkRecords`, `listLinkedRecords` |

**Behind `listTools(category)`** (Cloud/licensed on `/mcp-discovery` or an older server): call `listTools` with one category, read the names and argument schemas it returns, then invoke the tool through `callTool`. Categories:

`workspaces`, `members`, `links`, `tables`, `fields`, `filters`, `sorts`, `views`, `shared-views`, `data-io`, `record-templates`, `date-dependencies`, `duplicates`, `audits`, `dashboards`, `comments`, `records`, `attachments`, `trash`, `permissions`, `row-colors`, `scripts`, `hooks`, `view-sections`, `base-sections`, `automation-sections`, `workflows`, `workflow-nodes`, `rls`, `interfaces`, `docs`, `form-fields`.

The ones this plugin uses most:

| Category | Tools | Skill |
|----------|-------|-------|
| `tables` | `createTable`, `updateTable`, `deleteTable` | table-management |
| `fields` | `createField`, `updateField`, `deleteField`, `addFieldOptions`, `removeFieldOptions`, `setDisplayField` | field-management |
| `views` | `createView`, `updateView`, `deleteView` | view-management |
| `filters` | `createFilter`, `updateFilter`, `replaceFilters`, `deleteFilter` | view-management |
| `sorts` | `addSort`, `updateSort`, `deleteSort` | view-management |
| `shared-views` | `shareView`, `unshareView` | view-management |
| `hooks` | `createHook`, `updateHook`, `deleteHook` | webhooks |
| `workflows` / `workflow-nodes` | `createWorkflow`, `updateWorkflow`, `publishWorkflow`, `deleteWorkflow`, node and edge tools, `validateWorkflowNode` | workflows |
| `trash` | `listTrash`, `restoreFromTrash`, `restoreRecords` | table-management |
| `audits` | `listBaseAudits`, `listRecordAudits` | troubleshoot |
| `docs` | `createDocument`, `updateDocument`, `patchDocument`, `moveDocument`, `deleteDocument`, `shareDocument` | api-reference |

### Calling a hidden tool (`/mcp-discovery` or a server older than 2026.10.1)

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "fields"
   → names + argument schemas — read them, do not guess key names

mcp__plugin_nocodb-dev_nocodb__callTool   name: "createField"
   arguments: { tableId: "<tableId>",
                field: { title: "Phone", type: "PhoneNumber" } }
```

`callTool` validates `arguments` against the same schema `listTools` returned. If a hidden tool name is not in the answer for its category, the instance does not offer it — fall back to REST. On the full `/mcp` endpoint call the tool by name with the same `arguments`.

## MCP Payloads vs REST Payloads

The two surfaces share the v3 key names, but the MCP tools wrap or split them differently:

| Topic | MCP | REST (Meta API v3) |
|-------|-----|--------------------|
| Create a field | `createField {tableId, field:{title, type, options}}` | `POST /tables/{tableId}/fields` body `{title, type, options}` |
| Update a field | `updateField {fieldId, field:{…}}` — `options` keys **merge** onto the stored ones; changing `type` replaces them | `PATCH /fields/{fieldId}` |
| Select choices | `addFieldOptions` / `removeFieldOptions` (`choices:[{title,color?}]`) | `POST` / `DELETE /fields/{fieldId}/options` |
| Field `options` shape | `getFieldOptionsSchema(type)` returns the exact JSON Schema; unknown keys are rejected | `FieldOptions_*` schemas in `nocodb-meta-openapi.json` |
| Create a view | `createView {tableId, title, type, lock_type?, options?, fields?}` — filters and sorts are separate tools | `POST /tables/{tableId}/views` also accepts `filters`, `sorts`, `row_coloring` |
| Filters | `createFilter {viewId, filter}`, groups use `group_operator: "AND"\|"OR"` | `POST /views/{viewId}/filters` |
| Update a hook | `updateHook` is a **full replacement** — read with `getHook` and resend every key | `PATCH /hooks/{hookId}` |
| Barcode format key | `options.format` (per `getFieldOptionsSchema("Barcode")`) | `options.barcode_format` |
| `Links` type | not in the MCP enum — use `LinkToAnotherRecord` | both `Links` and `LinkToAnotherRecord` |

When the two disagree, the MCP tool's own schema wins for MCP calls and the bundled OpenAPI spec wins for REST calls.

Record tools write at most **100 records per call** — chunk bulk loads (see **nocodb-ops**).

## The Discovery → Change → Verify Loop

```
1. getBaseSchema  (or getTablesList + getTableSchema)   ← one-call orientation / snapshot
2. plan the change (table / field / view / hook payload)
3. confirm destructive steps with the user
4. apply:  createField (directly, or via callTool on /mcp-discovery)  on Cloud/licensed
           curl … /api/v3/meta/…    on Community, or as fallback
5. getTableSchema(tableId)                              ← confirm the new shape landed
6. queryRecords / getRecord (optional)                  ← confirm data is still readable
```

## Pattern — Add a Field (MCP-first)

```
Step 1: mcp__plugin_nocodb-dev_nocodb__getTablesList
        → find the table, note its ID

Step 2: mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: <tableId>
        → confirm the title is free; for Lookup/Rollup confirm the link field exists

Step 3: mcp__plugin_nocodb-dev_nocodb__callTool  name: "createField"      (full /mcp endpoint: call createField directly)
          arguments: { tableId: "<tableId>", field: { title: "Phone", type: "PhoneNumber" } }
        (Community Edition: POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields)

Step 4: mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: <tableId>
        → the new field appears in `fields`
```

## Pattern — Verify a Formula After Creation

A Formula is computed server-side; the only proof is reading records.

```
Step 1: createField via callTool, or the REST recipe in field-management
          field: { title: "Days Open", type: "Formula",
                   options: { formula: "DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")" } }

Step 2: mcp__plugin_nocodb-dev_nocodb__queryRecords
          tableId: <tableId>
          fields: ["Title", "CreatedAt", "Days Open"]
          pageSize: 5
        → spot-check that Days Open holds plausible numbers
```

## Pattern — Audit Scope Before a Destructive Change

```
Step 1: mcp__plugin_nocodb-dev_nocodb__countRecords  tableId: <tableId>
Step 2: mcp__plugin_nocodb-dev_nocodb__countRecords  tableId: <tableId>
          filter: { field: "Status", operator: "blank" }
        → rows that hold no value in the column you are about to change
```

For a field type change or a select-choice removal, `updateField` / `removeFieldOptions` with `dryRun: true` give the cleared and rounded counts directly, with sample record ids and no write (2026.10.0) — see **field-management** → "Dry run before a destructive change". The counts are exact for type conversions on PostgreSQL only; elsewhere they are `null`, so use the `countRecords` audit above.

Deleted tables, fields and views go to the base **trash** on Cloud/licensed: `listTrash` shows the entry (with `cleanup_due_at`), `restoreFromTrash(trashId)` puts it back. Deleted records can be restored with `restoreRecords` only on a NocoDB-managed source — an external source deletes for good. Still confirm before every delete.

## Best Practices

1. **Resolve IDs first.** Never pass a guessed `tableId`/`fieldId`; read `getBaseSchema` or `getTablesList` first.
2. **Snapshot before and after.** A diff of two `getTableSchema` answers is your audit trail.
3. **Read the argument schema.** `listTools(category)` and `getFieldOptionsSchema(type)` tell you the exact keys; the servers reject unknown ones.
4. **Check the edition before choosing the path.** MCP-first only where the tool is listed or `listTools` offers it; otherwise REST.
5. **Verify with reads.** A successful write response does not always mean the schema cache has caught up — re-read with `getTableSchema`.
6. **Watch for view-filter blindness.** `queryRecords` with a `viewId` returns only rows visible through that view's filters. Omit `viewId` for raw audits.

## Error Handling

| Error | Meaning | What to do |
|-------|---------|------------|
| "Table not found" | Wrong `tableId` | Re-run `getTablesList` |
| "Field not found" | Stale schema cache or wrong name (names are case-sensitive) | Re-run `getTableSchema` |
| Unknown key rejected on a field/view payload | `options` key not in that type's schema | `getFieldOptionsSchema(type)` / `listTools` for the exact keys |
| `listTools` or `callTool` not found, or tool missing from the category | Community Edition, or an older server | If `createTable` is in the tool list, call the tool by name; otherwise use the REST recipes in **api-reference** |
| Rate-limit answer that names a wait time | MCP has its own per-account limit since 2026.10.1 | Wait as long as the answer says, then retry; batch the reads (`getBaseSchema`) |
| 401 / 403 from MCP | Token invalid, or the role cannot write schema | See **setup** → MCP rows; check `whoami` |
