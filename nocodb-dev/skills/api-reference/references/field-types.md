# NocoDB Field Types — Catalog and Payloads

All 35 field types of the Meta API v3 (`FieldBase.type`), with the `options` schemas from `components.schemas.FieldOptions_*` in `nocodb-meta-openapi.json`. Each entry shows the minimal create payload sent to `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields` (or, on Cloud / licensed, passed as `field` to the MCP `createField` tool via `callTool`).

The `type` value is the NocoDB internal type name (matches the OpenAPI schema). Display labels in the NocoDB UI may differ slightly.

## Payload Shape

```json
{
  "title": "Price",
  "type": "Currency",
  "description": "optional",
  "default_value": "0",
  "unique": false,
  "options": { "currency_code": "USD" }
}
```

- Only `title`, `type`, `description`, `default_value` and `unique` sit at the top level. **Every type-specific setting lives inside `options`.** Payloads written for older NocoDB versions or older tooling use flat or differently-named keys; NocoDB v3 rejects them — see the 2026-10 entry in `LEARNINGS.md` for the old-to-new key map.
- Some types take no options at all (`SingleLineText`, `Year`, `JSON`, `Geometry`, `AutoNumber`); omit `options` for them.
- To read the exact JSON Schema of one type over MCP, call `getFieldOptionsSchema(type)` — the MCP tools validate against it and reject unknown keys. The MCP schemas are narrower than the REST ones in places (for example no options for `Attachment`, `CreatedBy`, `LastModifiedBy`; the Barcode format key is `format` there).

> Tip: probe the spec for full per-type option shapes:
> ```
> jq '.components.schemas.FieldOptions_<TypeName>' skills/api-reference/references/nocodb-meta-openapi.json
> ```

## Text

### SingleLineText

```json
{ "title": "Name", "type": "SingleLineText" }
```

### LongText

Free-form text. Optional rich-text mode.

```jsonc
{ "title": "Notes", "type": "LongText" }
{ "title": "Notes", "type": "LongText", "options": { "rich_text": true } }
```

Other `options`: `generate_text_using_ai`, `smart_mode`.

### PhoneNumber / URL / Email

```jsonc
{ "title": "Phone",   "type": "PhoneNumber" }
{ "title": "Website", "type": "URL",   "options": { "validate": true } }
{ "title": "Email",   "type": "Email", "options": { "validate": true } }
```

## Numeric

### Number

Integer. The default goes in the top-level `default_value`.

```jsonc
{ "title": "Count", "type": "Number" }
{ "title": "Count", "type": "Number", "default_value": "0", "options": { "separator": "comma_period" } }
```

`separator`: `locale`, `none_period`, `none_comma`, `comma_period`, `period_comma`, `space_period`, `space_comma`.

### Decimal

```json
{ "title": "Weight", "type": "Decimal", "options": { "precision": 2 } }
```

### Currency

```json
{ "title": "Price", "type": "Currency", "options": { "currency_code": "USD", "currency_locale": "en-US", "precision": 2 } }
```

`precision` 0-5, default 2.

### Percent

```jsonc
{ "title": "Discount", "type": "Percent", "options": { "precision": 1 } }
{ "title": "Progress", "type": "Percent", "options": { "show_as_progress": true, "shape": "bar" } }
```

`shape`: `bar` (default) or `circle`.

### Duration

```json
{ "title": "Elapsed", "type": "Duration", "options": { "duration_format": "h:mm" } }
```

`duration_format`: `h:mm`, `h:mm:ss`, `h:mm:ss.S`, `h:mm:ss.SS`, `h:mm:ss.SSS`.

## Date & Time

### Date

```json
{ "title": "Due", "type": "Date", "options": { "date_format": "YYYY-MM-DD" } }
```

`date_format`: `YYYY/MM/DD`, `YYYY-MM-DD`, `YYYY MM DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `DD MM YYYY`, `MM/DD/YYYY`, `MM-DD-YYYY`, `MM DD YYYY`, `YYYY-MM`, `YYYY MM`, and weekday-prefixed variants (`dddd YYYY-MM-DD`, `ddd DD/MM/YYYY`, …).

### DateTime

```json
{ "title": "ScheduledAt", "type": "DateTime",
  "options": { "date_format": "YYYY-MM-DD", "time_format": "HH:mm", "12hr_format": false, "timezone": "Europe/Berlin", "display_timezone": true } }
```

`time_format`: `HH:mm`, `HH:mm:ss`, `HH:mm:ss.SSS`. Other `options`: `use_same_timezone_for_all`.

### Time

```json
{ "title": "OpensAt", "type": "Time", "options": { "12hr_format": false } }
```

### Year

```json
{ "title": "ModelYear", "type": "Year" }
```

## Selection

### SingleSelect

Choices have `title` (label) and an optional hex `color` (`#RRGGBB`); titles must be unique.

```json
{
  "title": "Status",
  "type": "SingleSelect",
  "options": {
    "choices": [
      { "title": "New",      "color": "#cfdffe" },
      { "title": "Active",   "color": "#d1f7c4" },
      { "title": "Archived", "color": "#fee2d5" }
    ]
  }
}
```

Add or remove choices later without resending the list: `POST` / `DELETE /api/v3/meta/bases/{baseId}/fields/{fieldId}/options` (MCP: `addFieldOptions`, `removeFieldOptions`).

### MultiSelect

Same options structure as SingleSelect.

```json
{
  "title": "Tags",
  "type": "MultiSelect",
  "options": { "choices": [ { "title": "vip" }, { "title": "lead" }, { "title": "partner" } ] }
}
```

### Rating

```json
{ "title": "Stars", "type": "Rating", "options": { "max_value": 5, "icon": "star", "color": "#fcb400" } }
```

`icon`: `star`, `heart`, `circle-filled`, `thumbs-up`, `flag`; `max_value` 1-10.

### Checkbox

```json
{ "title": "Done", "type": "Checkbox", "options": { "icon": "circle-check", "color": "#0acf83" } }
```

`icon`: `square`, `circle-check`, `circle-filled`, `star`, `heart`, `thumbs-up`, `flag`.

### User

```json
{ "title": "Owner", "type": "User", "options": { "allow_multiple_users": false, "notify": true } }
```

## Files & Structured

### Attachment

```jsonc
{ "title": "Files", "type": "Attachment" }
{ "title": "Files", "type": "Attachment", "options": { "max_number_of_attachments": 5, "max_attachment_size": 10485760 } }
```

Other `options`: `supported_attachment_mime_types` (array).

### JSON

```json
{ "title": "Metadata", "type": "JSON" }
```

### Geometry

For Map view; stores a geographic point.

```json
{ "title": "Location", "type": "Geometry" }
```

## Relations

### LinkToAnotherRecord (and its alias `Links`)

Both type names take the same `options`; `LinkToAnotherRecord` is also accepted by the MCP tools, `Links` only by REST. `options` needs both `relation_type` and `related_table_id`.

```json
{
  "title": "Customer",
  "type": "LinkToAnotherRecord",
  "options": { "relation_type": "bt", "related_table_id": "m_customers_id" }
}
```

`relation_type`:

| Value | Meaning |
|-------|---------|
| `bt` | belongs-to (many-to-one) |
| `hm` | has-many (one-to-many) |
| `mm` | many-to-many |
| `oo` | one-to-one |
| `om` / `mo` | one-to-many / many-to-one (listed separately in the spec; this plugin uses `hm` / `bt`) |

`enable_conditions: true` turns on conditional links (filter which records are linkable).

### Lookup

Surfaces a field value from a linked table. Requires an existing link field on the same table.

```json
{
  "title": "Customer Name",
  "type": "Lookup",
  "options": {
    "related_field_id": "c_customer_link_id",
    "related_table_lookup_field_id": "c_customer_name_id"
  }
}
```

Other `options`: `enable_conditions`, `lookup_limit`, `use_recursive_evaluation`, `display_type`, `display_column_meta`.

### Rollup

Aggregates a field from linked records.

```json
{
  "title": "Total Orders",
  "type": "Rollup",
  "options": {
    "related_field_id": "c_orders_link_id",
    "related_table_rollup_field_id": "c_amount_id",
    "rollup_function": "sum"
  }
}
```

`rollup_function`: `count`, `min`, `max`, `avg`, `sum`, `countDistinct`, `sumDistinct`, `avgDistinct`. Other `options`: `precision`, `separator`, `enable_conditions`.

## Computed

### Formula

```json
{
  "title": "Days Open",
  "type": "Formula",
  "options": { "formula": "DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")" }
}
```

Other `options`: `display_type`, `display_column_meta` (how the result is rendered).

### Button

`options.type` selects the action: `url`, `webhook`, `script`, `ai` or `formula`.

```jsonc
{ "title": "Open Doc", "type": "Button",
  "options": { "type": "url", "formula": "CONCAT(\"https://docs.example.com/\", {Id})", "label": "Open", "color": "brand", "theme": "solid" } }

{ "title": "Notify", "type": "Button",
  "options": { "type": "webhook", "webhook_id": "<hookId>", "label": "Notify" } }

{ "title": "Run script", "type": "Button",
  "options": { "type": "script", "script_id": "<scriptId>", "label": "Run" } }
```

`ai` buttons take `prompt`, `integration_id` and `output_column_ids`; `formula` buttons take a `formula`. `color`: `brand`, `red`, `green`, `maroon`, `blue`, `orange`, `pink`, `purple`, `yellow`, `gray`; `theme`: `solid`, `light`, `text`.

### Barcode

Renders a barcode of another field's value.

```json
{
  "title": "SKU Barcode",
  "type": "Barcode",
  "options": { "barcode_value_field_id": "c_sku_id", "barcode_format": "CODE128" }
}
```

(Over MCP the format key is `format` — check `getFieldOptionsSchema("Barcode")`.)

### QrCode

```json
{
  "title": "Order QR",
  "type": "QrCode",
  "options": { "qrcode_value_field_id": "c_order_id_id" }
}
```

### AutoNumber

Auto-incrementing integer; no options.

```json
{ "title": "Seq", "type": "AutoNumber" }
```

## System (auto-populated, but addable)

### CreatedTime / LastModifiedTime

```jsonc
{ "title": "CreatedAt", "type": "CreatedTime" }
{ "title": "UpdatedAt", "type": "LastModifiedTime" }
```

### CreatedBy / LastModifiedBy

```jsonc
{ "title": "CreatedBy", "type": "CreatedBy" }
{ "title": "UpdatedBy", "type": "LastModifiedBy" }
```

System fields are populated automatically — they cannot be written via `createRecords` or `updateRecords`.

## Field-Type Decision Cheatsheet

| Need | Field type |
|------|------------|
| Free-form short text | `SingleLineText` |
| Multi-paragraph notes / rich text | `LongText` |
| Validated phone / URL / email | `PhoneNumber` / `URL` / `Email` |
| Whole-number quantity | `Number` |
| Money | `Currency` |
| Fractional measurement | `Decimal` |
| Percentage | `Percent` |
| Time-of-day or date | `Time` / `Date` / `DateTime` |
| One choice from a list | `SingleSelect` |
| Multiple choices from a list | `MultiSelect` |
| Star rating | `Rating` |
| Yes/No flag | `Checkbox` |
| A workspace user | `User` |
| File / image upload | `Attachment` |
| Arbitrary JSON | `JSON` |
| Lat/long coordinates | `Geometry` |
| Link to another table | `LinkToAnotherRecord` (or the REST alias `Links`) |
| Show a field from a linked record | `Lookup` |
| Aggregate from linked records | `Rollup` |
| Computed formula | `Formula` |
| Click-to-trigger | `Button` |
| Barcode display | `Barcode` |
| QR-code display | `QrCode` |
| Auto-incrementing number | `AutoNumber` |
| Auto created/updated metadata | `CreatedTime` / `LastModifiedTime` / `CreatedBy` / `LastModifiedBy` |

## Notes on Type Changes

- Lossless changes (e.g. `SingleLineText` → `LongText`) succeed instantly.
- Lossy changes (e.g. `LongText` → `Number` when values aren't numeric) are rejected.
- Changing a `SingleSelect` option list **does not** rewrite existing values that no longer match — they remain but are flagged invalid in the UI; removing a choice through the `/options` endpoint clears it from existing records.
- `Lookup` and `Rollup` cannot be created until the underlying link field exists.
- Over MCP, `updateField` merges `options` keys onto the stored options; changing `type` replaces them.
