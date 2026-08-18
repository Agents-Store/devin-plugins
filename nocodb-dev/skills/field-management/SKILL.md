---
name: field-management
description: |
  Create, update, and delete NocoDB fields across all 30 supported types — text, numeric, date, select, attachment, JSON, geometry, links, lookup, rollup, formula, button, barcode/QR, system fields. Use when:
  - "add a field"
  - "create a column"
  - "rename a field"
  - "change field type"
  - "delete a column"
  - "add a formula"
  - "set up lookup or rollup"
  - "link two tables"
---

# Field Management — All 30 Types

Every field-modification operation goes through the REST API or the `nc` CLI. MCP only reads schema (`getTableSchema`).

For per-type payload examples, see **`api-reference/references/field-types.md`** — that file is the authoritative catalog. This skill focuses on **the workflow**: how to plan, apply, and verify a field change.

## Workflow

```
1. mcp__nocodb__getTableSchema  ← snapshot existing columns
2. Plan the new field (title, type, options)
3. nc field:create   OR   POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields
4. mcp__nocodb__getTableSchema  ← confirm field appeared
5. (optional) mcp__nocodb__queryRecords ← spot-check record render
```

## Field Types Cheat Sheet

| Category | Types |
|----------|-------|
| Text | `SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email` |
| Numeric | `Number`, `Decimal`, `Currency`, `Percent`, `Duration` |
| Date / Time | `Date`, `DateTime`, `Time`, `Year` |
| Selection | `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox` |
| Files & Structured | `Attachment`, `JSON`, `Geometry` |
| Relations | `Links`, `LinkToAnotherRecord`, `Lookup`, `Rollup` |
| Computed | `Formula`, `Button`, `Barcode`, `QrCode` |
| System (auto-managed) | `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy` |

## Create a Field — General Pattern

CLI:

```bash
nc field:create <baseId> <tableId> '<JSON payload>'
```

API:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '<JSON payload>' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/fields"
```

### Quick examples (one per category)

Text:

```json
{ "title": "Description", "type": "LongText" }
```

Numeric:

```json
{ "title": "Price", "type": "Currency", "currency_code": "USD" }
```

Date:

```json
{ "title": "Due", "type": "Date", "date_format": "YYYY-MM-DD" }
```

Selection:

```json
{
  "title": "Priority",
  "type": "SingleSelect",
  "colOptions": { "options": [
    {"title":"Low"}, {"title":"Medium"}, {"title":"High"}
  ]}
}
```

Attachment:

```json
{ "title": "Files", "type": "Attachment" }
```

Link (modern):

```json
{
  "title": "Orders",
  "type": "Links",
  "linked_table_id": "<otherTableId>",
  "type_of_relation": "hm"
}
```

Lookup (after a link exists):

```json
{
  "title": "Customer Name",
  "type": "Lookup",
  "fk_relation_column_id": "<linkColumnId>",
  "fk_lookup_column_id":   "<columnIdOnLinkedTable>"
}
```

Rollup:

```json
{
  "title": "Order Total",
  "type": "Rollup",
  "fk_relation_column_id": "<linkColumnId>",
  "fk_rollup_column_id":   "<numericColumnIdOnLinkedTable>",
  "rollup_function":       "sum"
}
```

Formula:

```json
{
  "title": "Days Open",
  "type": "Formula",
  "formula": "DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")"
}
```

Button (URL action):

```json
{
  "title": "Open Doc",
  "type": "Button",
  "label": "Open",
  "action": { "type": "url", "url": "https://docs.example.com/{Id}" }
}
```

Barcode / QrCode (refer to another column):

```json
{ "title": "SKU Barcode", "type": "Barcode", "fk_column_id": "<sourceColumnId>", "barcode_format": "CODE128" }
{ "title": "Order QR",    "type": "QrCode",  "fk_column_id": "<sourceColumnId>" }
```

## Rename a Field

```bash
nc field:update <baseId> <tableId> <columnId> '{"title":"NewName"}'
```

API:

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"NewName"}' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/fields/$FIELD_ID"
```

Renames are by ID, so existing Lookups / Rollups / Formulas referencing this column keep working. Formulas displayed by-name (`{Name}`) update to use the new title automatically.

## Change Field Type

```bash
nc field:update <baseId> <tableId> <columnId> '{"type":"LongText"}'
```

NocoDB validates the change against existing data:

| Change | Outcome |
|--------|---------|
| `SingleLineText` → `LongText` | Always allowed |
| `LongText` → `SingleLineText` | Allowed; long values are truncated in the UI but kept in DB |
| `Number` → `Decimal` | Allowed |
| `Decimal` → `Number` | Allowed; fractions truncated |
| `SingleSelect` → `MultiSelect` | Allowed; existing values become single-element multi-selects |
| `MultiSelect` → `SingleSelect` | Allowed only if every record has at most one value; otherwise 422 |
| `LongText` → `Number` | Rejected if any value isn't numeric |
| `Lookup` / `Rollup` → anything | Generally rejected; recreate the field instead |

Always count records first to gauge impact — see **mcp-patterns** "Audit Scope Before a Bulk Migration".

## Update Field Options

For SingleSelect / MultiSelect, send the full options array (NocoDB diffs it):

```bash
nc field:update <baseId> <tableId> <columnId> '{
  "colOptions": {
    "options": [
      {"id":"<existingOptionId>","title":"Existing"},
      {"title":"NewOption"}
    ]
  }
}'
```

To **rename** an option, keep its `id`. To **delete** an option, omit it from the array — but NocoDB does not migrate records that hold the deleted value; they keep showing it as invalid.

## Delete a Field

**Destructive — confirm with the user first.** Print the field title, type, and any dependents (Lookups / Rollups / Formulas referencing it).

```bash
nc field:delete <baseId> <tableId> <columnId>
```

API:

```bash
curl -sS -X DELETE \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/fields/$FIELD_ID"
```

Pre-delete audit (find dependents):

```
mcp__nocodb__getTableSchema  tableId: <tableId>
# Look at every other field's options for fk_lookup_column_id / fk_rollup_column_id == <columnId>
# And every Formula's `formula` string for {<columnTitle>}
```

If the field is used as a `display_field` for a linked table, NocoDB will pick a new display field automatically — but the linked-record dropdowns will show the new value.

## Field-Specific Workflows

### Setting up a Link → Lookup → Rollup chain

The classic CRM pattern: each Order has one Customer; surface customer name on the Order; sum order totals back on the Customer.

```
1. nc field:create <base> <ordersTableId>     '{"title":"Customer", "type":"Links", "linked_table_id":"<customersTableId>", "type_of_relation":"bt"}'
2. nc field:list   <base> <ordersTableId>     # find the new link's columnId   → c_link
3. nc field:list   <base> <customersTableId>  # find Customer.Name's columnId  → c_name
4. nc field:create <base> <ordersTableId>     '{"title":"Customer Name", "type":"Lookup", "fk_relation_column_id":"c_link", "fk_lookup_column_id":"c_name"}'

# Inverse rollup (on Customers, summing Orders.Amount)
5. nc field:list   <base> <customersTableId>  # find auto-created inverse link → c_orders_link
6. nc field:list   <base> <ordersTableId>     # find Orders.Amount             → c_amount
7. nc field:create <base> <customersTableId>  '{"title":"Lifetime Value", "type":"Rollup", "fk_relation_column_id":"c_orders_link", "fk_rollup_column_id":"c_amount", "rollup_function":"sum"}'
```

### Formula validation

Formula errors appear at create time but also at runtime per-row. After creating a Formula, query 2–3 records to spot-check:

```
mcp__nocodb__queryRecords
  tableId: <tableId>
  fields: ["Title", "<formulaFieldName>"]
  pageSize: 3
```

If a row's formula returns `ERR`, the formula references a nullable column or has a type mismatch — `IF(ISBLANK({Field}), "", calculation)` is the standard guard.

### System fields

`CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy` can be added to any table but are populated automatically. They are read-only via the Data API. Use them for audit columns; do not try to seed them from a CSV import.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 "title already exists" | Another column on the same table has the same title | Pick a distinct title |
| 422 "type X requires field Y" | Lookup / Rollup / Barcode / QR missing a required `fk_*_column_id` | Add the required option |
| 400 "fk_relation_column_id not found" | Lookup created before link, or wrong column ID | Create the link first; verify the ID with `nc field:list` |
| Formula returns `ERR` for some rows | Null value or type mismatch | Wrap in `IF(ISBLANK({...}), default, expr)` |
| Type change rejected with 422 | Existing values incompatible with new type | Audit and clean values first; or recreate the field |
| New SingleSelect option not visible | UI cache | Hard-refresh; the API write succeeded |
