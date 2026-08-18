# NocoDB Field Types — Catalog and Payloads

All 30 field types from `components.schemas.FieldOptions_*` in `nocodb-meta-openapi.json`. Each entry shows the minimal create payload sent to `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields`.

The `type` value is the NocoDB internal type name (matches the OpenAPI schema). Display labels in the NocoDB UI may differ slightly.

> Tip: probe the spec for full per-type option shapes:
> ```
> jq '.components.schemas.FieldOptions_<TypeName>' skills/api-reference/references/nocodb-openapi.json
> ```

## Text

### SingleLineText

```json
{ "title": "Name", "type": "SingleLineText" }
```

### LongText

Free-form text. Optional rich-text mode.

```json
{ "title": "Notes", "type": "LongText" }
{ "title": "Notes", "type": "LongText", "rich_text": true }
```

### PhoneNumber

```json
{ "title": "Phone", "type": "PhoneNumber" }
```

### URL

```json
{ "title": "Website", "type": "URL" }
```

### Email

```json
{ "title": "Email", "type": "Email" }
```

## Numeric

### Number

Integer. Optional default.

```json
{ "title": "Count", "type": "Number" }
{ "title": "Count", "type": "Number", "cdf": "0" }
```

### Decimal

Fixed-precision decimal.

```json
{ "title": "Weight", "type": "Decimal", "precision": 2 }
```

### Currency

```json
{ "title": "Price", "type": "Currency", "currency_code": "USD", "currency_locale": "en-US" }
```

### Percent

```json
{ "title": "Discount", "type": "Percent", "precision": 1 }
```

### Duration

ISO 8601 duration display.

```json
{ "title": "Elapsed", "type": "Duration", "duration": "h:mm" }
```

## Date & Time

### Date

```json
{ "title": "Due", "type": "Date", "date_format": "YYYY-MM-DD" }
```

### DateTime

```json
{ "title": "ScheduledAt", "type": "DateTime", "date_format": "YYYY-MM-DD", "time_format": "HH:mm" }
```

### Time

```json
{ "title": "OpensAt", "type": "Time", "time_format": "HH:mm" }
```

### Year

```json
{ "title": "ModelYear", "type": "Year" }
```

## Selection

### SingleSelect

Choices have `title` (label) and an optional `color`.

```json
{
  "title": "Status",
  "type": "SingleSelect",
  "colOptions": {
    "options": [
      { "title": "New",      "color": "#cfdffe" },
      { "title": "Active",   "color": "#d1f7c4" },
      { "title": "Archived", "color": "#fee2d5" }
    ]
  }
}
```

### MultiSelect

Same options structure as SingleSelect.

```json
{
  "title": "Tags",
  "type": "MultiSelect",
  "colOptions": {
    "options": [
      { "title": "vip" },
      { "title": "lead" },
      { "title": "partner" }
    ]
  }
}
```

### Rating

```json
{ "title": "Stars", "type": "Rating", "max": 5, "icon": "star", "color": "#fcb400" }
```

### Checkbox

```json
{ "title": "Done", "type": "Checkbox", "icon": "check", "color": "#0acf83" }
```

## Files & Structured

### Attachment

```json
{ "title": "Files", "type": "Attachment" }
```

### JSON

```json
{ "title": "Metadata", "type": "JSON" }
```

### Geometry

For Map view; stores GeoJSON-style point.

```json
{ "title": "Location", "type": "Geometry" }
```

## Relations

### Links

Newer simplified link field (v0.200+).

```json
{
  "title": "Orders",
  "type": "Links",
  "linked_table_id": "m_orders_id",
  "type_of_relation": "hm"
}
```

`type_of_relation`: `hm` (has-many), `bt` (belongs-to), `mm` (many-to-many).

### LinkToAnotherRecord

Classic link field. Same semantics as `Links`, slightly different option shape.

```json
{
  "title": "Customer",
  "type": "LinkToAnotherRecord",
  "parentId": "m_customers_id",
  "childId": "m_orders_id",
  "type_of_relation": "bt"
}
```

### Lookup

Surfaces a column value from a linked table. Requires an existing link field.

```json
{
  "title": "Customer Name",
  "type": "Lookup",
  "fk_relation_column_id": "c_customer_link_id",
  "fk_lookup_column_id":  "c_customer_name_id"
}
```

### Rollup

Aggregates a column from linked records.

```json
{
  "title": "Total Orders",
  "type": "Rollup",
  "fk_relation_column_id": "c_orders_link_id",
  "fk_rollup_column_id":   "c_amount_id",
  "rollup_function":       "sum"
}
```

`rollup_function`: `sum`, `min`, `max`, `avg`, `count`, `countDistinct`, `countEmpty`, `countNotEmpty`.

## Computed

### Formula

```json
{
  "title": "Days Open",
  "type": "Formula",
  "formula": "DATETIME_DIFF(NOW(), {CreatedAt}, \"days\")"
}
```

### Button

Triggers a Script (Enterprise) or webhook on click.

```json
{
  "title": "Send Welcome",
  "type": "Button",
  "label": "Send",
  "action": { "type": "url", "url": "https://hooks.example.com/welcome" }
}
```

### Barcode

Renders a barcode of another column's value.

```json
{
  "title": "SKU Barcode",
  "type": "Barcode",
  "fk_column_id": "c_sku_id",
  "barcode_format": "CODE128"
}
```

`barcode_format`: `CODE128`, `EAN13`, `EAN8`, `UPC`, `CODE39`, `ITF14`, `MSI`, `pharmacode`, `codabar`.

### QrCode

```json
{
  "title": "Order QR",
  "type": "QrCode",
  "fk_column_id": "c_order_id_id"
}
```

## System (auto-populated, but addable)

### CreatedTime

```json
{ "title": "CreatedAt", "type": "CreatedTime" }
```

### LastModifiedTime

```json
{ "title": "UpdatedAt", "type": "LastModifiedTime" }
```

### CreatedBy

```json
{ "title": "CreatedBy", "type": "CreatedBy" }
```

### LastModifiedBy

```json
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
| File / image upload | `Attachment` |
| Arbitrary JSON | `JSON` |
| Lat/long coordinates | `Geometry` |
| Link to another table | `Links` (modern) or `LinkToAnotherRecord` (classic) |
| Show a column from a linked record | `Lookup` |
| Aggregate from linked records | `Rollup` |
| Computed formula | `Formula` |
| Click-to-trigger | `Button` |
| Barcode display | `Barcode` |
| QR-code display | `QrCode` |
| Auto created/updated metadata | `CreatedTime` / `LastModifiedTime` / `CreatedBy` / `LastModifiedBy` |

## Notes on Type Changes

- Lossless changes (e.g. `SingleLineText` → `LongText`) succeed instantly.
- Lossy changes (e.g. `LongText` → `Number` when values aren't numeric) are rejected.
- Changing a `SingleSelect` option list **does not** rewrite existing values that no longer match — they remain but are flagged invalid in the UI.
- `Lookup` and `Rollup` cannot be created until the underlying link field exists.
