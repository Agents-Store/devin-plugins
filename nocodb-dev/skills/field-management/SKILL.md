---
name: field-management
description: Create, update and delete NocoDB fields across all 35 types, including select options, formulas, links with lookups and rollups, attachments, barcode and button fields, plus safe type changes and deletes. Use when a NocoDB table needs a new or changed column. Creating the table itself is table-management, hiding or ordering columns in a view is view-management.
---

# Field Management — All 35 Types

Field writes go through the MCP schema tools on **Cloud / licensed** self-hosted (called by name on `/mcp` since 2026.10.1; `listTools` category `fields`, then `callTool` on `/mcp-discovery` and older servers) and through the **REST API** (`curl` on Meta API v3) on **Community Edition** or as a fallback. Both surfaces take the same v3 keys: `title`, `type`, `description`, `default_value`, `unique`, and a type-specific `options` object. See **mcp-patterns** for the contract.

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

```jsonc
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

### Dry run before a destructive change (MCP, 2026.10.0)

`updateField` and `removeFieldOptions` take `dryRun: true`. Nothing is written; the answer reports how many cell values the change would clear (`cleared_rows`) or round (`rounded_rows`), with up to five record ids for each, and for a select field the count per removed choice (`cleared_by_choice`). For a link field converted to `SingleLineText` it also lists the text the cells would get, the reverse link field that would be deleted, and the lookup, rollup and formula fields that would break. Run it first on every type change and on every choice rewrite or removal, show the numbers to the user, then repeat the call without `dryRun`.

```
updateField  fieldId: "<fieldId>"  field: { type: "Number" }  dryRun: true
```

The counts are exact only for a type conversion on PostgreSQL. On another database, and for a conversion to a link field, they come back as `null` with a warning that says why — fall back to `countRecords` as in **mcp-patterns**. REST has no dry run (source: https://nocodb.com/docs/mcp/schema, updated 2026-11-18; the `dryRun` argument in the server's own tool schema).

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

### Newer field options (2026.10.0)

- **Rollup that counts every linked record.** `rollup_function: "countAll"` counts all linked records; `count` counts only those whose rolled-up value is not empty. Date-like targets accept `count`, `countAll`, `min`, `max` and `countDistinct`; numeric targets also take `sum`, `avg`, `sumDistinct` and `avgDistinct` (source: OpenAPI spec at tag 2026.10.2, `FieldOptions_Rollup`; release 2026.10.0).
- **Formula shown as a colored single select.** A text formula can render its result as a single-select chip; filters and sorts still treat it as text. It is a formatting choice in the field editor (the Formatting tab): add the values the formula can return, each with a color; a result matches an option by exact, case-sensitive title, and an unmatched result shows as a gray chip unless a fallback option is chosen. Over the API the formula keeps its `display_type` / `display_column_meta` keys (see `field-types.md`) — create the formula, set the format in the UI, then read it back with `getField` to see how the server stores it (source: https://nocodb.com/docs/product/tables/fields/field-types/formula/formula-result-formatting, 2026-10-19; release 2026.10.0).
- **Conditional links.** A link field (`Links` / `LinkToAnotherRecord`) and a rollup take `options.enable_conditions: true` to apply the configured filters when resolving linked records; `getField` on a link field returns the conditions as `options.record_selection_filter` (MCP). The release adds a dynamic condition that matches linked records sharing a link with the current record. The v3 options schema only carries the boolean — set the condition itself in the field editor (source: OpenAPI spec at tag 2026.10.2; https://nocodb.com/docs/mcp/schema; release 2026.10.0).
- **Button that runs an automation.** The Button field's *On click* action *Run automation* starts a workflow whose trigger is *When a button is clicked*; the workflow receives the clicked record. Cloud and licensed self-hosted only; one workflow can be bound to one button; the workflow must be enabled before the button works, and each click counts as one run against the plan's limit. The v3 Button `options` schema has only `url`, `webhook`, `script`, `ai` and `formula` — there is no automation type, so create this button in the UI (*Create new automation* builds the workflow with the trigger already attached). See **workflows** (source: https://nocodb.com/docs/product/tables/fields/field-types/custom-types/button, 2026-10-21; https://nocodb.com/docs/workflows/nodes/trigger-nodes/button-clicked; the server's `getFieldOptionsSchema("Button")`).

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
