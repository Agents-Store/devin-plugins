---
name: mcp-patterns
description: |
  NocoDB MCP tools usable for schema-development work. Use when:
  - "what MCP tools can I use for schema?"
  - "how do I discover NocoDB structure?"
  - "MCP for nocodb-dev"
  - "can MCP create tables?"
  - "NocoDB MCP discovery"
---

# NocoDB MCP — Discovery for Dev Work

All tools use the `mcp__nocodb__` prefix. **The shared NocoDB MCP server has no schema-write tools.** Use it strictly for discovering state before and verifying state after changes made through the REST API or CLI.

## What the MCP Can Do (for dev workflows)

| Tool | Purpose | Key parameters | Typical dev use |
|------|---------|----------------|-----------------|
| `getBaseInfo` | Get base name, ID, metadata | none | Identify the working base |
| `getTablesList` | List all accessible tables | none | Resolve table IDs before any change |
| `getTableSchema` | Get columns, types, views, links | `tableId` | Inspect the current schema before modifying it |
| `queryRecords` | List records | `tableId`, `where`, `fields[]`, `pageSize` | Sanity-check that records still parse after a field change |
| `getRecord` | Read one record | `tableId`, `recordId` | Verify a Formula / Lookup / Rollup result |
| `countRecords` | Count records | `tableId`, `where` | Confirm impact scope before bulk migrations |

## What the MCP CANNOT Do

There are no MCP tools for any of the following — they all require **REST API** or **`nc` CLI**:

- Create / update / delete a **table** — see `table-management`
- Create / update / delete a **field** (any of the 30 types) — see `field-management`
- Create / update / delete a **view** — see `view-management`
- Configure a **link** between tables, **lookup**, **rollup**, or **formula** — see `field-management`
- Create / update / delete a **webhook** — see `webhooks`
- Create / update / delete a **base**, **source**, **script**, or **dashboard**

If you find yourself reaching for an MCP tool that doesn't exist for one of the above — switch to the API or CLI.

## The Discovery → Change → Verify Loop

Every schema change should follow this loop:

```
1. getTablesList                                      ← resolve target table ID
2. getTableSchema(tableId)                            ← snapshot current shape
3. plan the change (table/field/view payload)
4. execute the change via REST API or `nc` CLI         ← see api-reference / cli-reference
5. getTableSchema(tableId)                            ← confirm the new shape landed
6. queryRecords / getRecord (optional)                ← confirm data is still readable
```

## Pattern — Discover Before Adding a Field

```
Step 1: mcp__nocodb__getTablesList
        → find the table you want to extend, note its ID

Step 2: mcp__nocodb__getTableSchema  tableId: m_abc123
        → confirm a field with the new title doesn't already exist
        → confirm field type compatibility (e.g. don't add a Lookup until the link exists)

Step 3: nc field:create <baseId> <tableId> '{"title":"Phone","type":"PhoneNumber"}'
        ← actual write happens here, not in MCP

Step 4: mcp__nocodb__getTableSchema  tableId: m_abc123
        → the new field appears in the columns array
```

## Pattern — Verify a Formula After Creation

A Formula field is computed server-side; only one way to know it works is to read records.

```
Step 1: nc field:create <baseId> <tableId> '{"title":"Days Open","type":"Formula","formula":"DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")"}'

Step 2: mcp__nocodb__queryRecords
          tableId: m_abc123
          fields: ["Title", "CreatedAt", "Days Open"]
          pageSize: 5
        → spot-check that Days Open holds plausible numbers
```

## Pattern — Audit Scope Before a Bulk Migration

Before changing a SingleSelect → MultiSelect, or before deleting a column, audit the data.

```
Step 1: mcp__nocodb__countRecords
          tableId: m_abc123
        → total record count

Step 2: mcp__nocodb__countRecords
          tableId: m_abc123
          where: "(Status,blank,)"
        → records that have an empty value in the target column
        → compare these counts before and after the change
```

## Best Practices

1. **Resolve IDs first.** Never pass a guessed `tableId`. Always run `getTablesList` first.
2. **Snapshot the schema.** Call `getTableSchema` before *and* after every change — a diff of the responses is your audit trail.
3. **Don't fight the limits.** If you need a write tool that the MCP doesn't expose, switch to the API or CLI. Don't try to `createRecords` your way around schema modification.
4. **Verify with reads.** A successful API response doesn't always mean the change took effect — the schema cache can lag. Re-read with `getTableSchema` to confirm.
5. **Watch for view-filter blindness.** `queryRecords` with a `viewId` returns only records visible through that view's filters. Omit `viewId` for raw audits.

## Error Handling

| Error | Meaning | What to do |
|-------|---------|------------|
| "Table not found" | Wrong `tableId` | Re-run `getTablesList` |
| "Field not found" | Schema cache stale or wrong field name | Re-run `getTableSchema`; field names are case-sensitive |
| 401 / 403 from MCP | `xc-mcp-token` invalid or no access | See **setup** → MCP rows |
| Tool not found `mcp__nocodb__createTable` (etc.) | You reached for a write tool that doesn't exist | Switch to **api-reference** or **cli-reference** |
