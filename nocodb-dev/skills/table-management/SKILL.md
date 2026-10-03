---
name: table-management
description: |
  Create, update, rename, duplicate, and delete NocoDB tables. Use when:
  - "create a new NocoDB table"
  - "rename a table"
  - "delete a NocoDB table"
  - "set the display field"
  - "duplicate a table"
  - "add a table with initial fields"
---

# Table Management

Table writes go through the MCP schema tools on **Cloud / licensed** self-hosted (`listTools` category `tables`, then `callTool`) and through the **REST API** (`curl` on Meta API v3) on **Community Edition** or as a fallback. See **mcp-patterns** for the contract and **api-reference** for the REST surface.

## Discover First

Before creating or changing a table, snapshot the base:

```
mcp__plugin_nocodb-dev_nocodb__getBaseInfo                        ← confirm working base
mcp__plugin_nocodb-dev_nocodb__getBaseSchema                      ← every table with its fields and views, one call
mcp__plugin_nocodb-dev_nocodb__getTablesList                      ← or just titles & IDs
```

Avoid name collisions and unintended duplicates. NocoDB does not enforce title uniqueness within a base — duplicates are accepted but cause downstream confusion.

## Create a Table

### MCP (Cloud / licensed)

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "tables"      ← once per session: confirms createTable is offered
mcp__plugin_nocodb-dev_nocodb__callTool   name: "createTable"
  arguments: { title: "Customers", description: "Master customer list",
               fields: [ { title: "Name",  type: "SingleLineText" },
                         { title: "Email", type: "Email" } ] }
```

### REST

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Customers" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables"
```

With initial fields (preferred — saves a roundtrip per field; type-specific settings go inside `options`):

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customers",
    "description": "Master customer list",
    "fields": [
      { "title": "Name",   "type": "SingleLineText" },
      { "title": "Email",  "type": "Email" },
      { "title": "Phone",  "type": "PhoneNumber" },
      { "title": "Status", "type": "SingleSelect",
        "options": { "choices": [
          { "title": "New" }, { "title": "Active" }, { "title": "Archived" }
        ]}},
      { "title": "Joined", "type": "Date" }
    ]
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables"
```

The response includes the new `tableId` (prefix `m`). For a source other than the default, add `source_id`.

### Verify

```
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: <newTableId>
```

The response should list every field you created, with auto-assigned field IDs and the first non-system field as the display field.

## Rename a Table

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"NewName"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}"
```

MCP: `callTool name: "updateTable"  arguments: { tableId: "<tableId>", title: "NewName" }`.

Renaming a table does **not** rename references in formulas, lookups, or rollups — but those references use IDs internally so they keep working. Visible names in formulas stay as the original; refresh formulas explicitly if you want them to reflect the new name.

## Update Description

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"description":"New description"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}"
```

## Set the Display Field

The display field is what shows up in linked-record dropdowns and lookup card titles. By default, NocoDB picks the first non-system column — usually a SingleLineText named "Title" or similar. Override:

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_field_id":"<fieldId>"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}"
```

MCP: `callTool name: "setDisplayField"  arguments: { fieldId: "<fieldId>" }` (category `fields`), or `updateTable` with `display_field_id`.

Allowed display field types: text, number, date/time, duration, autonumber and formula fields. `LongText`, select, link and attachment fields are rejected.

## Duplicate a Table

There is no single duplicate call in the REST API (on Cloud / licensed the MCP `duplicates` category may offer one — check `listTools`). To clone by hand:

1. Read the source schema:

```
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: <sourceTableId>
```

2. Strip IDs from the response and POST as a new table:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @duplicated-table.json \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables"
```

Note: this clones the schema only. To copy data, see the `import-export` skill in `nocodb-ops`.

## Delete a Table

**Destructive — confirm with the user first.** Print the table title, base, record count, and any dependent fields (Lookups / Rollups / Links from other tables) before asking for approval.

```bash
curl -sS -X DELETE \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}"
```

MCP: `callTool name: "deleteTable"  arguments: { tableId: "<tableId>" }`.

On Cloud / licensed the deleted table goes to the base trash: `listTrash` (read-only, lists `cleanup_due_at`) and `restoreFromTrash(trashId)` bring it back until the retention window ends. An external source deletes for good.

Pre-delete audit:

```
mcp__plugin_nocodb-dev_nocodb__countRecords  tableId: <tableId>
```

Then read `getBaseSchema` and look in every other table's fields for `options.related_table_id == <tableId>` — those are the relations that will break.

## Pre-Flight Checklist for New Tables

Before creating:

1. **Title.** Distinct from existing tables. Use TitleCase or sentence-case consistently within a base.
2. **Display field.** Plan to have a `SingleLineText` early in the field list — it auto-becomes the display field.
3. **Required fields.** NocoDB doesn't enforce required at schema level (validation is per-view in Forms); decide if you need form-level required or webhook-driven validation later.
4. **Relations.** If this table will hold link fields, create the parent tables first.
5. **Naming convention.** Use kebab-case or camelCase for field titles? Pick one. NocoDB stores titles verbatim; the API matches by exact title (case-sensitive).

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on create with `fields` | One field's payload doesn't match its type | Check `field-types.md` for the exact `options` keys |
| 400 "title required" | Empty title or whitespace-only | Title is mandatory |
| Display field not what you expected | NocoDB picked the first non-system column | Set `display_field_id` explicitly |
| Delete returns 200 but table still visible | Schema cache | Force-refresh in NocoDB UI or wait ~30s |
| Cannot delete table | A link field on another table points to it | Delete the link field on the other side first |
| `createTable` is not offered by `listTools` | Community Edition | Use the REST recipes above |
