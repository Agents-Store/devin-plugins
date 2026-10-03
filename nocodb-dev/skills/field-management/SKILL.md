---
name: field-management
description: |
  Create, update, and delete NocoDB fields across all 35 supported types — text, numeric, date, select, attachment, JSON, geometry, links, lookup, rollup, formula, button, barcode/QR, system fields. Use when:
  - "add a field"
  - "create a column"
  - "rename a field"
  - "change field type"
  - "delete a column"
  - "add a formula"
  - "set up lookup or rollup"
  - "link two tables"
  - "add a select option"
---

# Field Management — All 35 Types

Field writes go through the MCP schema tools on **Cloud / licensed** self-hosted (`listTools` category `fields`, then `callTool`) and through the **REST API** (`curl` on Meta API v3) on **Community Edition** or as a fallback. Both surfaces take the same v3 keys: `title`, `type`, `description`, `default_value`, `unique`, and a type-specific `options` object. See **mcp-patterns** for the contract.

For per-type payload examples, see **`api-reference/references/field-types.md`** — that file is the authoritative catalog. This skill focuses on **the workflow**: how to plan, apply, and verify a field change.

## Workflow

```
1. mcp__plugin_nocodb-dev_nocodb__getTableSchema  ← snapshot existing fields
2. Plan the new field (title, type, options)
3. callTool createField (Cloud/licensed)  OR  POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields
4. mcp__plugin_nocodb-dev_nocodb__getTableSchema  ← confirm field appeared
5. (optional) mcp__plugin_nocodb-dev_nocodb__queryRecords ← spot-check record render
```

## Field Types Cheat Sheet

| Category | Types |
|----------|-------|
| Text | `SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email` |
| Numeric | `Number`, `Decimal`, `Currency`, `Percent`, `Duration`, `AutoNumber` |
| Date / Time | `Date`, `DateTime`, `Time`, `Year` |
| Selection | `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox`, `User` |
| Files & Structured | `Attachment`, `JSON`, `Geometry` |
| Relations | `LinkToAnotherRecord` (REST alias `Links`), `Lookup`, `Rollup` |
| Computed | `Formula`, `Button`, `Barcode`, `QrCode` |
| System (auto-managed) | `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy` |

## Create a Field — General Pattern

MCP (Cloud / licensed):

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "fields"
mcp__plugin_nocodb-dev_nocodb__callTool   name: "createField"
  arguments: { tableId: "<tableId>", field: { title: "Phone", type: "PhoneNumber" } }
```

REST:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '<JSON payload>' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/fields"
```

### Quick examples (one per category)

Text:

```json
{ "title": "Description", "type": "LongText" }
```

Numeric:

```json
{ "title": "Price", "type": "Currency", "options": { "currency_code": "USD" } }
```

Date:

```json
{ "title": "Due", "type": "Date", "options": { "date_format": "YYYY-MM-DD" } }
```

Selection:

```json
{
  "title": "Priority",
  "type": "SingleSelect",
  "options": { "choices": [
    {"title":"Low"}, {"title":"Medium"}, {"title":"High"}
  ]}
}
```

Attachment:

```json
{ "title": "Files", "type": "Attachment" }
```

Link (create it first; NocoDB adds the inverse on the other table):

```json
{
  "title": "Orders",
  "type": "LinkToAnotherRecord",
  "options": { "relation_type": "hm", "related_table_id": "<otherTableId>" }
}
```

Lookup (after a link exists):

```json
{
  "title": "Customer Name",
  "type": "Lookup",
  "options": {
    "related_field_id": "<linkFieldId>",
    "related_table_lookup_field_id": "<fieldIdOnLinkedTable>"
  }
}
```

Rollup:

```json
{
  "title": "Order Total",
  "type": "Rollup",
  "options": {
    "related_field_id": "<linkFieldId>",
    "related_table_rollup_field_id": "<numericFieldIdOnLinkedTable>",
    "rollup_function": "sum"
  }
}
```

Formula:

```json
{
  "title": "Days Open",
  "type": "Formula",
  "options": { "formula": "DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")" }
}
```

Button (URL action — the URL is produced by a formula):

```json
{
  "title": "Open Doc",
  "type": "Button",
  "options": { "type": "url", "formula": "CONCAT(\"https://docs.example.com/\", {Id})", "label": "Open" }
}
```

Barcode / QrCode (refer to another field):

```json
{ "title": "SKU Barcode", "type": "Barcode", "options": { "barcode_value_field_id": "<sourceFieldId>", "barcode_format": "CODE128" } }
{ "title": "Order QR",    "type": "QrCode",  "options": { "qrcode_value_field_id": "<sourceFieldId>" } }
```

(Over MCP the barcode format key is `format` — call `getFieldOptionsSchema("Barcode")` when unsure.)

## Rename a Field

REST:

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"NewName"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}"
```

MCP: `callTool name: "updateField"  arguments: { fieldId: "<fieldId>", field: { title: "NewName" } }`.

Renames are by ID, so existing Lookups / Rollups / Formulas referencing this field keep working. Formulas displayed by-name (`{Name}`) update to use the new title automatically.

## Change Field Type

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type":"LongText"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}"
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

Always count records first to gauge impact — see **mcp-patterns** "Audit Scope Before a Destructive Change". Over MCP, changing `type` in `updateField` replaces the stored `options`; changing only `options` merges.

## Update Field Options (select choices)

Do **not** resend the whole choice list. Add or remove individual choices:

```bash
# Add — idempotent: titles that already exist are skipped
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "choices": [ { "title": "Blocked", "color": "#fee2d5" } ] }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}/options"

# Remove — by exact title; clears that value from existing records; at least one choice must remain
curl -sS -X DELETE \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "choices": [ { "title": "Archived" } ] }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}/options"
```

MCP: `callTool name: "addFieldOptions"  arguments: { fieldId, choices: [{ title, color? }] }` and `name: "removeFieldOptions"  arguments: { fieldId, choices: [{ title }] }`.

The options endpoint only adds and removes. To **rename** a choice, read the field (`getField` / `GET …/fields/{fieldId}`) and `PATCH` it with the changed `options.choices` — try it on a throwaway field first, because a title that disappears from the list is cleared from the records that held it.

## Delete a Field

**Destructive — confirm with the user first.** Print the field title, type, and any dependents (Lookups / Rollups / Formulas referencing it).

```bash
curl -sS -X DELETE \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}"
```

MCP: `callTool name: "deleteField"  arguments: { fieldId: "<fieldId>" }`. On Cloud / licensed the deleted field lands in the base trash (`listTrash`, `restoreFromTrash`) until the retention window ends; do not count on that for external sources.

Pre-delete audit (find dependents):

```
mcp__plugin_nocodb-dev_nocodb__getBaseSchema
# Look at every other field's options for related_table_lookup_field_id / related_table_rollup_field_id == <fieldId>
# And every Formula's `formula` string for {<fieldTitle>}
```

If the field is used as a `display_field` for a linked table, NocoDB will pick a new display field automatically — but the linked-record dropdowns will show the new value.

## Field-Specific Workflows

### Setting up a Link → Lookup → Rollup chain

The classic CRM pattern: each Order has one Customer; surface customer name on the Order; sum order totals back on the Customer.

```
1. createField on Orders:     { "title":"Customer", "type":"LinkToAnotherRecord",
                                "options":{ "relation_type":"bt", "related_table_id":"<customersTableId>" } }
2. getTableSchema(Orders)     # find the new link's fieldId          → c_link
3. getTableSchema(Customers)  # find Customer.Name's fieldId         → c_name
4. createField on Orders:     { "title":"Customer Name", "type":"Lookup",
                                "options":{ "related_field_id":"c_link", "related_table_lookup_field_id":"c_name" } }

# Inverse rollup (on Customers, summing Orders.Amount)
5. getTableSchema(Customers)  # find auto-created inverse link       → c_orders_link
6. getTableSchema(Orders)     # find Orders.Amount                   → c_amount
7. createField on Customers:  { "title":"Lifetime Value", "type":"Rollup",
                                "options":{ "related_field_id":"c_orders_link", "related_table_rollup_field_id":"c_amount", "rollup_function":"sum" } }
```

Each `createField` is one MCP `callTool` (`arguments: { tableId, field: {…} }`) or one REST `POST …/tables/{tableId}/fields` with the same object as the body.

### Formula validation

Formula errors appear at create time but also at runtime per-row. After creating a Formula, query 2–3 records to spot-check:

```
mcp__plugin_nocodb-dev_nocodb__queryRecords
  tableId: <tableId>
  fields: ["Title", "<formulaFieldName>"]
  pageSize: 3
```

If a row's formula returns `ERR`, the formula references a nullable field or has a type mismatch — `IF(ISBLANK({Field}), "", calculation)` is the standard guard.

### System fields

`CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy` can be added to any table but are populated automatically. They are read-only via the Data API. Use them for audit columns; do not try to seed them from a CSV import.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 "title already exists" | Another field on the same table has the same title | Pick a distinct title |
| 422 "type X requires option Y" | Lookup / Rollup / Barcode / QR missing a required `options` key | Add the required key (see `field-types.md`) |
| 400 "related_field_id not found" | Lookup created before the link, or wrong field ID | Create the link first; verify the ID with `getTableSchema` |
| Unknown key rejected | A flat or renamed key outside `options` | Move type-specific keys into `options`; check `getFieldOptionsSchema(type)` |
| Formula returns `ERR` for some rows | Null value or type mismatch | Wrap in `IF(ISBLANK({...}), default, expr)` |
| Type change rejected with 422 | Existing values incompatible with new type | Audit and clean values first; or recreate the field |
| New SingleSelect option not visible | UI cache | Hard-refresh; the API write succeeded |
