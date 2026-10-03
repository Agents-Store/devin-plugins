---
name: mcp-patterns
description: |
  NocoDB MCP tools reference for data work -- which tools the server lists, which sit behind listTools/callTool, the Community vs Cloud/licensed contract, and the exact parameter shapes (100-record batches, sort objects, filter vs where, date sub-operators). Use when:
  - "what NocoDB tools are available?"
  - "how do I query records?"
  - "show me NocoDB MCP parameters"
  - "which tool do I use for..."
  - "NocoDB tool reference"
  - "listTools / callTool"
---

# NocoDB MCP Tools Reference

All tools use the `mcp__plugin_nocodb-ops_nocodb__` prefix (the server is declared in this plugin's `.mcp.json`). Every tool call goes through the NocoDB MCP server.

## The Contract: Community vs Cloud / Licensed

| Edition | What the MCP server offers |
|---------|----------------------------|
| **Community Edition** | The record tools only -- the original eleven: `getBaseInfo`, `getTablesList`, `getTableSchema`, `queryRecords`, `getRecord`, `countRecords`, `aggregate`, `createRecords`, `updateRecords`, `deleteRecords`, `readAttachment`. No `listTools`, no hidden tools. The connection is created per base. |
| **Cloud / licensed self-hosted** | The same tools plus many more (about 200 in 2026.09). Read tools and record create/update/delete are **listed directly**; schema, view, automation, permission and interface *write* tools stay out of the tool list and are reached with `listTools(category)` then `callTool(name, arguments)`. |

Rule of thumb: use the listed tools for everything in this plugin; when a capability seems missing, check `listTools` before concluding it is unsupported. If `listTools` is absent, errors, or does not name the tool, the instance does not offer it.

Start every session with `whoami`: it names the user and base the MCP credential is pinned to and which permissions it carries. Effective authority is the intersection of that grant and the user's role on each resource, so a 403 on a write usually means a read-only role, not a missing tool.

## Discovery Tools

Use these first to understand what data is available.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `whoami` | Who the credential acts as, which base it is pinned to, what it may do (Cloud / licensed) | None |
| `getBaseInfo` | Base name, ID, and metadata | None |
| `getTablesList` | List all tables you can access | None |
| `getTableSchema` | Columns, types, and views for one table | `tableId` |
| `getBaseSchema` | Every table with fields and views in one call (Cloud / licensed) | None |
| `listFields`, `listViews`, `listFilters`, `listSorts` | Read-only structure lookups (Cloud / licensed) | `tableId` / `viewId` |

**Always start with `getTablesList`** to get table IDs. You need a `tableId` for almost every other tool.

## Read Tools

Retrieve data without changing anything.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `queryRecords` | Search and list records with filters, sorting, and pagination | `tableId`, `filter` (preferred) or `where`, `fields`, `sort[{field, direction}]`, `page`, `pageSize`, `viewId` |
| `getRecord` | Fetch one specific record by its ID | `tableId`, `recordId`, `fields` |
| `countRecords` | Count how many records match a filter | `tableId`, `filter` or `where`, `viewId` |
| `groupByRecords` | Count records per distinct value of one field ("appointments per status") | `tableId`, `fieldId`, `filter` or `where`, `sort`, `limit`, `offset` |
| `listLinkedRecords` | Page through the records linked to one row | `tableId`, `fieldId`, `recordId`, `limit`, `offset` |
| `exportCsv` | CSV text of a table or view (capped by `maxRows`, default 1000, max 10000) | `tableId` or `viewId`, `maxRows`, `delimiter` |

## Write Tools

Create, change, or remove data. **Every record-array tool takes at most 100 records per call** -- a longer array is rejected outright (the whole call fails, nothing is truncated), so split larger writes into batches of 100 or fewer.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `createRecords` | Add new records (up to 100 per call) | `tableId`, `records[{fields:{}}]` |
| `updateRecords` | Change existing records (send only changed fields; up to 100 per call). A link field is **replaced**, not appended to -- pass the complete list, `[]` to clear | `tableId`, `records[{id, fields:{}}]` |
| `deleteRecords` | Remove records (up to 100 per call) | `tableId`, `records[{id}]` |
| `linkRecords` / `unlinkRecords` | Add or remove individual links without restating the set (up to 100 records, 100 links per record) | `tableId`, `fieldId`, `records[{id, links:[{id}]}]` |

## Record Tools Behind `listTools` (Cloud / licensed)

Call `listTools` with a category, read the argument schemas it returns, then run the tool with `callTool`:

```
mcp__plugin_nocodb-ops_nocodb__listTools  category: "records"
   -> upsertRecords, updateRecordsByCondition, linkRecordsByDisplayValue

mcp__plugin_nocodb-ops_nocodb__callTool   name: "upsertRecords"
   arguments: { tableId: "<tableId>",
                fieldsToMergeOn: ["Email"],
                records: [ { "fields": { "Email": "jane@example.com", "Status": "Active" } } ] }
```

| Category | Tools | Use for |
|----------|-------|---------|
| `records` | `upsertRecords` | Insert-or-update on a business key -- up to 100 records and 3 merge fields per call, each result says `inserted` or `updated`. Replaces "query, then create or update" |
| | `updateRecordsByCondition` | Set the same field values on **every** record matching a condition -- **not** capped at 100, the condition is required, answers with a count only. Run `countRecords` with the same condition first |
| | `linkRecordsByDisplayValue` | Link by what rows are called instead of by id; unmatched and ambiguous titles are reported back |
| `data-io` | `exportExcel` | `.xlsx` download link, signed for 3 hours (hand a spreadsheet to a person) |
| | `importCsv` | Load CSV text into an existing table (`tableId`) or a new one (`tableName` -- every field becomes `SingleLineText`) |
| `trash` | `listTrash`, `restoreFromTrash`, `restoreRecords` | Undo a delete (see **record-management**) |

`callTool` validates `arguments` against the same schema `listTools` returned -- read the names there, do not guess.

## Analytics Tools

Run calculations across your data.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `aggregate` | Sum, count, average, min, max, median, std_dev, and more | `tableId`, `aggregations[{field, type}]`, `filterGroups[{alias, filter or where}]` -- **both arrays are required** |

`aggregate` does not group by a field: each `filterGroups` entry produces one result block keyed by its `alias`. For one overall number use `filterGroups: [{ "alias": "All" }]`. To count per distinct value use `groupByRecords`.

## File Tools

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `readAttachment` | Read files attached to a record | `files[]` (the attachment objects from `getRecord` / `queryRecords`) |

---

## Filters: `filter` (preferred) and `where` (fallback)

`queryRecords`, `countRecords`, `groupByRecords`, `updateRecordsByCondition` and each `aggregate.filterGroups[]` entry accept the same two forms. **Pass only one of the two.**

**Structured `filter`** -- field names and values are quoted for you, so commas, parentheses and quotes in values are safe:

```
filter: { "field": "Status", "operator": "eq", "value": "Active" }

filter: { "group_operator": "AND",
          "filters": [ { "field": "Status",   "operator": "eq", "value": "Active" },
                       { "field": "Priority", "operator": "in", "value": ["High", "Urgent"] } ] }
```

A group's `group_operator` is `AND` or `OR`; its members may be conditions or nested groups. Field titles are case-insensitive here.

**String `where`** -- `(field,operator,value)` joined with `~and`, `~or`, `~not`:

```
where: "(Status,eq,Active)~and(Priority,in,High,Urgent)"
```

Field names in `where` are **case-sensitive**. See **search-filter** for the full operator list.

**Operators:**

| Category | Operators |
|----------|----------|
| Comparison | `eq`, `neq`, `gt`, `lt`, `gte`, `lte` |
| Range | `btw`, `nbtw` -- **Time and text fields only** (see below) |
| Text | `like`, `nlike` |
| List | `in`, `allof`, `anyof`, `nallof`, `nanyof` |
| Empty checks | `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty` |
| Checkbox | `checked`, `notchecked` |
| Date | `isWithin` plus a `sub_operator` |

**Two traps the server rejects:**

1. **Dates need a sub-operator.** On Date / DateTime fields every comparison needs `sub_operator` -- `exactDate` with the value `YYYY-MM-DD` for a calendar date. A bare date is read as the sub-operator and fails with `'2026-06-01' is not supported`.

   ```
   filter: { "field": "Due Date", "operator": "gte", "sub_operator": "exactDate", "value": "2026-06-01" }
   where:  "(Due Date,gte,exactDate,2026-06-01)"
   ```

2. **`btw` / `nbtw` are rejected** on Number, Decimal, Currency, Percent, Rating, Duration, Date / DateTime and Checkbox fields (`Operation btw is not supported for type <T>`). Express every range as two bounds:

   ```
   where: "(Due Date,gte,exactDate,2026-01-01)~and(Due Date,lte,exactDate,2026-12-31)"
   ```

---

## Common Patterns

### Pattern 1 -- List with filter and sort

Find all active orders, newest first, showing only key fields:

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Params:
  tableId: <orders_table_id>
  filter: { "field": "Status", "operator": "eq", "value": "Active" }
  fields: ["Order Number", "Customer", "Total", "Date"]
  sort: [{ "field": "Date", "direction": "desc" }]
  pageSize: 50
```

`sort` is an **array of objects** `{ "field": "<name>", "direction": "asc" | "desc" }`, applied in array order (first entry = highest priority). A string such as `"-Date"` or `["-Date"]` is rejected (`Expected object, received string at sort[0]`). The one exception is `groupByRecords`, whose `sort` is a single field title with an optional `-` prefix for descending.

### Pattern 2 -- Create and verify

Add a new record, then confirm it was saved:

```
Step 1 - Tool: mcp__plugin_nocodb-ops_nocodb__createRecords
Params:
  tableId: <contacts_table_id>
  records: [{ "fields": { "Name": "Jane Smith", "Email": "jane@example.com" } }]

Step 2 - Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Params:
  tableId: <contacts_table_id>
  filter: { "field": "Email", "operator": "eq", "value": "jane@example.com" }
```

### Pattern 3 -- Aggregate report

Get total revenue and order count, split by status:

```
Tool: mcp__plugin_nocodb-ops_nocodb__aggregate
Params:
  tableId: <orders_table_id>
  aggregations: [
    { "field": "Total", "type": "sum" },
    { "field": "Id", "type": "count" }
  ]
  filterGroups: [
    { "alias": "Active",    "filter": { "field": "Status", "operator": "eq", "value": "Active" } },
    { "alias": "Completed", "filter": { "field": "Status", "operator": "eq", "value": "Completed" } }
  ]
```

The result is one block per alias: `{ "Active": { "Total": 1200, "Id": 7 }, "Completed": { ... } }`. When a field carries two or more aggregations the keys become `"<field>.<type>"` (for example `Total.sum`).

### Pattern 4 -- Count per value

How many records sit in each status?

```
Tool: mcp__plugin_nocodb-ops_nocodb__groupByRecords
Params:
  tableId: <orders_table_id>
  fieldId: <status_field_id>        (from getTableSchema)
```

---

## Best Practices

1. **Resolve table IDs first** -- always call `getTablesList` before operating on data. Never guess IDs.
2. **Check the schema** -- call `getTableSchema` to confirm exact field names and types before querying.
3. **Use pagination** -- `pageSize` defaults to 50 and is capped at 200 (the deployment may cap it lower; the response reports the `page_size` actually applied). Use `page` for large datasets and stop when a page comes back shorter than `page_size`.
4. **Filter on the server** -- apply `filter` (or `where`) instead of fetching all records and filtering locally.
5. **Request only needed fields** -- use `fields` to limit returned data and keep responses fast.
6. **Bulk operations in batches of 100** -- prefer one 100-record call over 100 single calls, never more than 100. For changes by condition use `updateRecordsByCondition`; for a long CSV use `importCsv`.

## Error Handling

| Error | Meaning | What to Do |
|-------|---------|-----------|
| "Table not found" | Wrong `tableId` | Re-run `getTablesList` and use the correct ID |
| "Field not found" / `Column alias '<name>' not found` | Typo or wrong case in a `where` field name | Run `getTableSchema` to see exact field names |
| "Invalid filter" | Bad `where` syntax | Check parentheses and operator spelling, or switch to the structured `filter` |
| `'<date>' is not supported` | Bare date in a date filter | Add `exactDate`: `(Field,gte,exactDate,2026-06-01)` |
| `Operation btw is not supported for type <T>` | `btw` / `nbtw` on a numeric, date or checkbox field | Use two bounds with `gte` and `lte` |
| `Expected object, received string at sort[0]` | `sort` was given as strings | Send `[{ "field": "<name>", "direction": "asc" \| "desc" }]` |
| Input validation error on `records` | More than 100 records in one write call | Split into batches of 100 or fewer |
| "Record not found" | Wrong `recordId` | Query first to confirm the record exists |
| 401 / 403 | Auth or permission issue | See the **setup** and **troubleshoot** skills |
