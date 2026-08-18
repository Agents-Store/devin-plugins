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
4. **Create records in batches** -- send data in groups using `createRecords`.

## Step 1 -- Get the Table Schema

Before importing anything, retrieve the target table's structure:

```
mcp__nocodb__getTableSchema  tableId: "tbl_abc123"
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

Send records in batches of 100 to 500. Larger batches (up to 2000) are possible but risk timeouts on slower connections.

```
mcp__nocodb__createRecords
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
| Simple records (few fields, no attachments) | 500 |
| Records with many fields or long text | 200 |
| First import (testing) | 10-20 |
| Large dataset (1000+ records) | 200-500 |

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
mcp__nocodb__createRecords
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

### Export All Records

Use pagination to fetch every record:

```
mcp__nocodb__queryRecords
  tableId: "tbl_abc123"
  page: 1
  pageSize: 200
```

If the table has more than 200 records, continue with page 2, 3, and so on until the response returns fewer records than the page size.

### Export with Filters

Export only a subset:

```
mcp__nocodb__queryRecords
  tableId: "tbl_orders"
  where: "(Status,eq,Completed)~and(OrderDate,isWithin,pastMonth)"
  page: 1
  pageSize: 200
```

### Export Specific Fields

Select only the columns needed:

```
mcp__nocodb__queryRecords
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

Always state the total record count. Use `mcp__nocodb__countRecords` to get the total before paginating, so you can tell the user how many pages to expect.

## Deduplication Before Import

Before importing records that might already exist, check for duplicates:

1. Identify the field that should be unique (e.g., Email, SKU, Order ID).
2. Query the table for existing values:

```
mcp__nocodb__queryRecords
  tableId: "tbl_contacts"
  where: "(Email,eq,alice@example.com)"
  fields: ["Email"]
  pageSize: 1
```

3. If a match is found, skip that record (or ask the user whether to update or skip).
4. For bulk deduplication, query all existing values first:

```
mcp__nocodb__queryRecords
  tableId: "tbl_contacts"
  fields: ["Email"]
  pageSize: 1000
```

Then compare your import list against the results and remove matches before creating.

## Cross-Table Data Migration

To move or copy data from one table to another within NocoDB:

1. **Query the source table:**

```
mcp__nocodb__queryRecords
  tableId: "tbl_source"
  page: 1
  pageSize: 200
```

2. **Transform the data** to match the target table's schema. Rename fields, convert types, and add any required default values.

3. **Create records in the target table:**

```
mcp__nocodb__createRecords
  tableId: "tbl_target"
  records: [ ... transformed records ... ]
```

4. **Verify** by counting records in the target:

```
mcp__nocodb__countRecords  tableId: "tbl_target"
```

## Best Practices

- **Always check the schema first.** Field names must match exactly. A single typo means the data goes into the wrong column or gets rejected.
- **Start with a small test batch.** Import 5-10 records first, verify they look correct in the table, then import the rest.
- **Use batches of 200-500.** This balances speed with reliability. If a batch fails, you lose fewer records.
- **Verify after import.** Count the records and spot-check a few to confirm data landed correctly.
- **Handle errors per batch.** If one batch fails, log which records were in it and retry just that batch. Do not re-import everything.
- **Report progress.** For large imports, tell the user after each batch: "Imported 200 of 1,400 records (batch 1 of 7)."
- **Never skip validation.** Importing bad data is worse than a slow import. Check types, required fields, and select options before sending.
