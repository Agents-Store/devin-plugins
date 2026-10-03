---
name: import-export
description: |
  Import data into NocoDB tables and export records out. Use when:
  - "import CSV into NocoDB"
  - "load data into this table"
  - "bulk create records"
  - "export records to CSV"
  - "migrate data between tables"
  - "import JSON data"
  - "extract all records"
  - "download table data"
---

# Import and Export Data

## Import Workflow Overview

Every import follows the same four steps:

1. **Get the table schema** -- confirm field names, types, and required fields.
2. **Prepare the data** -- map your source columns to the table's field names.
3. **Validate** -- check that values match expected types and required fields are present.
4. **Create records in batches of 100 or fewer** -- send data in groups using `createRecords` (100 records per call is the server's hard limit).

## Step 1 -- Get the Table Schema

Before importing anything, retrieve the target table's structure:

```
mcp__plugin_nocodb-ops_nocodb__getTableSchema  tableId: "tbl_abc123"
```

From the response, note:
- **Field names** (exact spelling and capitalization)
- **Field types** (text, number, date, single-select, etc.)
- **Required fields** (fields that cannot be left empty)
- **Unique fields** (fields that reject duplicate values)
- **Select options** (allowed values for single-select and multi-select fields)

## Step 2 -- CSV Import Pattern

When the user provides a CSV file or CSV-formatted text:

1. Read the CSV content (from a file or pasted text).
2. Parse the header row to get column names.
3. Map each CSV column to the corresponding NocoDB field name. If names differ, create a mapping (e.g., "customer_name" in CSV maps to "Customer Name" in NocoDB).
4. Convert values to the correct type:
   - Numbers: remove currency symbols, commas, and whitespace.
   - Dates: convert to ISO format (YYYY-MM-DD).
   - Booleans: convert "yes/no/true/false" to true/false.
   - Single-select: verify the value is one of the allowed options.
5. Build record objects with `fields` matching the schema.

### Batch Creation

`createRecords`, `updateRecords`, `deleteRecords` and `upsertRecords` accept **at most 100 records per call**. A longer array is rejected outright -- the whole call fails with an input validation error and nothing is written -- so always chunk the data into batches of 100 or fewer.

```
mcp__plugin_nocodb-ops_nocodb__createRecords
  tableId: "tbl_abc123"
  records: [
    { "fields": { "Name": "Alice", "Email": "alice@example.com", "Amount": 150 } },
    { "fields": { "Name": "Bob", "Email": "bob@example.com", "Amount": 200 } },
    { "fields": { "Name": "Carol", "Email": "carol@example.com", "Amount": 175 } }
  ]
```

Repeat for each batch until all records are imported.

### Recommended Batch Sizes

| Scenario | Batch Size |
|----------|-----------|
| Simple records (few fields, no attachments) | 100 (the maximum) |
| Records with many fields, long text or link fields | 25-50 |
| First import (testing) | 10-20 |
| Large dataset (1000+ records) | 100 per call -- 1,000 records is 10 calls, 10,000 is 100 calls |

### CSV Text in One Call (`importCsv`)

On Cloud / licensed servers the `data-io` category has `importCsv`, which takes the CSV text itself and writes the rows server-side, without 100-record batching:

```
mcp__plugin_nocodb-ops_nocodb__listTools  category: "data-io"       <- read the argument schema first

mcp__plugin_nocodb-ops_nocodb__callTool   name: "importCsv"
  arguments: { csv: "<header row + data rows>", tableId: "<existing table id>" }
```

- With `tableId` the rows are **appended** to that table: headers are matched to fields by title, unmatched headers are skipped and reported, and values are coerced to the destination field type.
- With `tableName` instead a **new table** is created in which every field is `SingleLineText` (type detection is off) -- creating a typed table first (a provision / dev task, see `nocodb-dev`) and importing with `tableId` is preferred.
- The CSV travels inside the tool call, so use it for files that fit comfortably in the conversation; for very large files import through the NocoDB web interface.
- On Community Edition `importCsv` does not exist -- batch with `createRecords`.

## Step 3 -- JSON Import Pattern

When the user provides JSON data (an array of objects):

1. Read the JSON array.
2. Map each object's keys to NocoDB field names.
3. Wrap each object in a `{ "fields": { ... } }` structure.
4. Send in batches using `createRecords`.

Example -- source JSON:

```json
[
  { "name": "Widget A", "price": 29.99, "category": "Tools" },
  { "name": "Widget B", "price": 49.99, "category": "Parts" }
]
```

Mapped for NocoDB:

```
mcp__plugin_nocodb-ops_nocodb__createRecords
  tableId: "tbl_products"
  records: [
    { "fields": { "Product Name": "Widget A", "Price": 29.99, "Category": "Tools" } },
    { "fields": { "Product Name": "Widget B", "Price": 49.99, "Category": "Parts" } }
  ]
```

## Data Validation Before Import

Run these checks before sending any records:

| Check | How | What to Do If It Fails |
|-------|-----|----------------------|
| Required fields present | Compare source columns to schema | Ask the user for missing data or set a default |
| Value types match | Compare source values to field types | Convert or flag mismatches |
| Select options valid | Compare values to allowed options | List invalid values and ask the user to correct them |
| Unique fields have no duplicates | Query existing records for matches | Skip duplicates or ask the user |
| Date format correct | Check for YYYY-MM-DD or ISO 8601 | Convert dates before import |

## Export Workflow

To export records from a NocoDB table:

| Need | Tool |
|------|------|
| Read rows in the conversation | `queryRecords` (pages of up to 200) |
| CSV text inline | `exportCsv` -- shaped by a view (its fields, filters, sorts), capped by `maxRows` (default 1000, max 10000); narrow with a filtered view instead of raising the cap |
| A spreadsheet to hand to a person | `exportExcel` (Cloud / licensed, `data-io` category) -- returns a download link signed for 3 hours; the bytes are not returned |

### Export All Records

Use pagination to fetch every record:

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_abc123"
  page: 1
  pageSize: 200
```

If the table has more than 200 records, continue with page 2, 3, and so on until the response returns fewer records than the page size.

### Export with Filters

Export only a subset:

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_orders"
  where: "(Status,eq,Completed)~and(OrderDate,isWithin,pastMonth)"
  page: 1
  pageSize: 200
```

### Export Specific Fields

Select only the columns needed:

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_contacts"
  fields: ["Name", "Email", "Phone"]
  page: 1
  pageSize: 200
```

### Presenting Exported Data

After fetching records, present them in the format the user needs:

- **Table** -- formatted markdown table for quick viewing.
- **CSV** -- comma-separated values the user can copy-paste or save.
- **Summary** -- bullet points or grouped lists for reports.

Always state the total record count. Use `mcp__plugin_nocodb-ops_nocodb__countRecords` to get the total before paginating, so you can tell the user how many pages to expect.

## Deduplication Before Import

If a business key (email, SKU, order number -- at most 3 fields) identifies each row, the simplest route on Cloud / licensed servers is `upsertRecords` (category `records`, via `callTool`): it inserts new rows and updates existing ones in one call of up to 100 records and reports `inserted` or `updated` per row. Merge fields cannot be computed, link or attachment fields, and the record `fields` must not name a primary key.

On Community Edition, or when you must review matches before writing, check for duplicates yourself:

1. Identify the field that should be unique (e.g., Email, SKU, Order ID).
2. Query the table for existing values:

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_contacts"
  where: "(Email,eq,alice@example.com)"
  fields: ["Email"]
  pageSize: 1
```

3. If a match is found, skip that record (or ask the user whether to update or skip).
4. For bulk deduplication, query all existing values first, page by page (the page cap is 200):

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_contacts"
  fields: ["Email"]
  pageSize: 200
  page: 1
```

Continue with `page: 2, 3, ...` until a page comes back shorter than `page_size`, then compare your import list against the collected values and remove matches before creating.

## Cross-Table Data Migration

To move or copy data from one table to another within NocoDB:

1. **Query the source table:**

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_source"
  page: 1
  pageSize: 200
```

2. **Transform the data** to match the target table's schema. Rename fields, convert types, and add any required default values.

3. **Create records in the target table:**

```
mcp__plugin_nocodb-ops_nocodb__createRecords
  tableId: "tbl_target"
  records: [ ... transformed records ... ]
```

4. **Verify** by counting records in the target:

```
mcp__plugin_nocodb-ops_nocodb__countRecords  tableId: "tbl_target"
```

## Best Practices

- **Always check the schema first.** Field names must match exactly. A single typo means the data goes into the wrong column or gets rejected.
- **Start with a small test batch.** Import 5-10 records first, verify they look correct in the table, then import the rest.
- **Use batches of 100 or fewer.** 100 is the server's ceiling for one call; smaller batches (25-50) suit rows with many fields or links. If a batch fails, you lose fewer records.
- **Verify after import.** Count the records and spot-check a few to confirm data landed correctly.
- **Handle errors per batch.** If one batch fails, log which records were in it and retry just that batch. Do not re-import everything.
- **Report progress.** For large imports, tell the user after each batch: "Imported 100 of 1,400 records (batch 1 of 14)."
- **Never skip validation.** Importing bad data is worse than a slow import. Check types, required fields, and select options before sending.
