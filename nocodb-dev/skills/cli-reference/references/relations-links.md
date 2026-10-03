# Relations, Links, Lookups, Rollups — curl Recipes

The hardest part of NocoDB schema work is relations between tables. This reference covers the canonical REST patterns on the Meta API v3. The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md`. On Cloud / licensed the same objects can be sent as `field` to the MCP `createField` tool (`tableId` + `field`).

## Relation Types

| `relation_type` | Cardinality | Example |
|-----------------|-------------|---------|
| `bt` | Belongs-to (many-to-one) | An Order belongs to one Customer |
| `hm` | Has-many (one-to-many) | A Customer has many Orders |
| `mm` | Many-to-many | A Tag is on many Articles; an Article has many Tags |
| `oo` | One-to-one | A User has one Profile |
| `om` / `mo` | One-to-many / many-to-one | Listed separately in the spec; this plugin uses `hm` / `bt` |

A link on one table automatically creates the inverse link on the other table. NocoDB names the inverse field after the source table by default — rename it to your taste.

## Create a Link

`options` needs **both** `relation_type` and `related_table_id`:

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/fields '{
  "title": "Orders",
  "type": "LinkToAnotherRecord",
  "options": { "relation_type": "hm", "related_table_id": "<otherTableId>" }
}'
```

Many-to-many:

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/fields '{
  "title": "Tags",
  "type": "LinkToAnotherRecord",
  "options": { "relation_type": "mm", "related_table_id": "<tagsTableId>" }
}'
```

NocoDB creates the join table automatically for `mm`. `Links` is accepted as an alias of `LinkToAnotherRecord` over REST (same `options`); the MCP tools accept `LinkToAnotherRecord` only.

## Lookup — Show a Linked Field

A Lookup field surfaces a field value from a linked record. It requires an existing link field on the same table.

Setup sequence:

```bash
# 1) The link field must already exist — read the table and find it
nocodb_api GET /meta/bases/$BASE_ID/tables/$ORDERS_TABLE_ID | jq '.fields[] | {id, title, type}'
# → suppose: c_customer_link_id  (LinkToAnotherRecord → Customers)

# 2) Find the field to look up on the Customers side
nocodb_api GET /meta/bases/$BASE_ID/tables/$CUSTOMERS_TABLE_ID | jq '.fields[] | {id, title, type}'
# → suppose: c_customer_name_id  (SingleLineText "Name")

# 3) Create the Lookup
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TABLE_ID/fields '{
  "title": "Customer Name",
  "type":  "Lookup",
  "options": {
    "related_field_id": "c_customer_link_id",
    "related_table_lookup_field_id": "c_customer_name_id"
  }
}'
```

Lookups are read-only; they update automatically when the linked record's value changes.

## Rollup — Aggregate Linked Records

A Rollup aggregates a numeric field across all linked records.

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$CUSTOMERS_TABLE_ID/fields '{
  "title": "Lifetime Value",
  "type":  "Rollup",
  "options": {
    "related_field_id": "c_orders_link_id",
    "related_table_rollup_field_id": "c_amount_id",
    "rollup_function": "sum"
  }
}'
```

`rollup_function` values:

| Function | Meaning |
|----------|---------|
| `sum` | Sum of values |
| `min` / `max` | Smallest / largest value |
| `avg` | Mean |
| `count` | Number of linked records |
| `countDistinct` | Distinct values |
| `sumDistinct` / `avgDistinct` | Sum / mean over distinct values |

## Verifying a Relation

After creating a link, verify both ends:

```bash
nocodb_api GET /meta/bases/$BASE_ID/tables/$ORDERS_TABLE_ID    | jq '.fields[].title'   # includes the new link field
nocodb_api GET /meta/bases/$BASE_ID/tables/$CUSTOMERS_TABLE_ID | jq '.fields[].title'   # includes the auto-created inverse
```

Then test linking via the Data API:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[ {"id": "<orderRecordId>"} ]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${CUSTOMERS_TABLE_ID}/links/${LINK_FIELD_ID}/${CUSTOMER_RECORD_ID}"
```

Then re-read:

```bash
curl -sS \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${CUSTOMERS_TABLE_ID}/links/${LINK_FIELD_ID}/${CUSTOMER_RECORD_ID}"
```

## Pitfalls

- **Lookup before link.** A Lookup created before its link field exists fails with `related_field_id not found`. Create the link first.
- **Rollup on non-numeric field.** `sum` / `avg` against a text field returns an error. Use `count` / `countDistinct` for non-numeric aggregation.
- **Cycles.** NocoDB allows circular links (A→B and B→A) but not on the *same* base fields. Renaming the inverse field is OK; deleting one side does not auto-delete the other — clean up explicitly.
- **m2m join table is hidden by default.** It exists as a hidden table; it does not appear in the normal table list.
- **Display field on the linked side.** Lookups and link-card displays render the linked table's display field — set it with `PATCH /meta/bases/$BASE_ID/tables/$TABLE_ID '{"display_field_id":"..."}'` if the default first-non-system field isn't useful.
