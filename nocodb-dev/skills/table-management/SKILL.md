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

All operations on tables go through the **REST API** or the **`nc` CLI**. The MCP server has no schema-write tools.

## Discover First

Before creating or changing a table, snapshot the base:

```
mcp__nocodb__getBaseInfo                        ← confirm working base
mcp__nocodb__getTablesList                      ← collect existing table titles & IDs
```

Avoid name collisions and unintended duplicates. NocoDB does not enforce title uniqueness within a base — duplicates are accepted but cause downstream confusion.

## Create a Table

### CLI

```bash
nc table:create <baseId> '{"title":"Customers"}'
```

With initial fields (preferred — saves a roundtrip per field):

```bash
nc table:create <baseId> '{
  "title": "Customers",
  "description": "Master customer list",
  "fields": [
    { "title": "Name",      "type": "SingleLineText" },
    { "title": "Email",     "type": "Email" },
    { "title": "Phone",     "type": "PhoneNumber" },
    { "title": "Status",    "type": "SingleSelect",
      "colOptions": { "options": [
        {"title":"New"}, {"title":"Active"}, {"title":"Archived"}
      ]}},
    { "title": "Joined",    "type": "Date" }
  ]
}'
```

### REST API

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @new-table.json \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables"
```

Response includes the new `tableId` (prefix `m`).

### Verify

```
mcp__nocodb__getTableSchema  tableId: <newTableId>
```

The response should list every field you created, with auto-assigned column IDs and the first non-system field as the display field.

## Rename a Table

```bash
nc table:update <baseId> <tableId> '{"title":"NewName"}'
```

API:

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"NewName"}' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID"
```

Renaming a table does **not** rename references in formulas, lookups, or rollups — but those references use IDs internally so they keep working. Visible names in formulas stay as the original; refresh formulas explicitly if you want them to reflect the new name.

## Update Description

```bash
nc table:update <baseId> <tableId> '{"description":"New description"}'
```

## Set the Display Field

The display field is what shows up in linked-record dropdowns and lookup card titles. By default, NocoDB picks the first non-system column — usually a SingleLineText named "Title" or similar. Override:

```bash
nc table:update <baseId> <tableId> '{"display_field_id":"<columnId>"}'
```

Allowed display field types: `SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email`, `Number`, `Decimal`, `Currency`, `Percent`, `Date`, `DateTime`, `Time`, `Year`, `Formula`, `SingleSelect`, `Rating`. Other types are rejected.

## Duplicate a Table

NocoDB's CLI doesn't expose a single duplicate command. To clone:

1. Read the source schema:

```
mcp__nocodb__getTableSchema  tableId: <sourceTableId>
```

2. Strip IDs from the response and POST as a new table:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @duplicated-table.json \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables"
```

Note: this clones the schema only. To copy data, see the `import-export` skill in `nocodb-ops`.

## Delete a Table

**Destructive — confirm with the user first.** Print the table title, base, record count, and any dependent fields (Lookups / Rollups / Links from other tables) before asking for approval.

```bash
nc table:delete <baseId> <tableId>
```

API:

```bash
curl -sS -X DELETE \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID"
```

Pre-delete audit:

```
mcp__nocodb__countRecords  tableId: <tableId>
```

Then `getTablesList` and `getTableSchema` for every other table in the base, and grep the JSON for `linked_table_id == <tableId>` or `parentId/childId == <tableId>` — those are the relations that will break.

## Pre-Flight Checklist for New Tables

Before running `table:create`:

1. **Title.** Distinct from existing tables. Use TitleCase or sentence-case consistently within a base.
2. **Display field.** Plan to have a `SingleLineText` early in the field list — it auto-becomes the display field.
3. **Required fields.** NocoDB doesn't enforce required at schema level (validation is per-view in Forms); decide if you need form-level required or webhook-driven validation later.
4. **Relations.** If this table will hold link fields, create the parent tables first.
5. **Naming convention.** Use kebab-case or camelCase for column titles? Pick one. NocoDB stores titles verbatim; the API matches by exact title (case-sensitive).

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on create with `fields` | One field's payload doesn't match its type | Check `field-types.md` for the exact required keys |
| 400 "title required" | Empty title or whitespace-only | Title is mandatory |
| Display field not what you expected | NocoDB picked the first non-system column | Set `display_field_id` explicitly via `table:update` |
| Delete returns 200 but table still visible | Schema cache | Force-refresh in NocoDB UI or wait ~30s |
| Cannot delete table | A link field on another table points to it | Delete the link field on the other side first |
