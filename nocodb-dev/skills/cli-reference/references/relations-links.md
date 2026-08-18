# Relations, Links, Lookups, Rollups — CLI Reference

The hardest part of NocoDB schema work is relations between tables. This reference covers the canonical CLI patterns.

## Three Relation Cardinalities

| Code | Cardinality | Example |
|------|-------------|---------|
| `bt` | Belongs-to (many-to-one) | An Order belongs to one Customer |
| `hm` | Has-many (one-to-many) | A Customer has many Orders |
| `mm` | Many-to-many | A Tag is on many Articles; an Article has many Tags |

A `hm` link automatically creates the inverse `bt` link on the other table. NocoDB names the inverse field after the source table by default — rename it to your taste.

## Create a Link with `Links` (modern, v0.200+)

```bash
nc field:create <baseId> <tableId> '{
  "title": "Orders",
  "type": "Links",
  "linked_table_id": "<otherTableId>",
  "type_of_relation": "hm"
}'
```

Many-to-many:

```bash
nc field:create <baseId> <tableId> '{
  "title": "Tags",
  "type": "Links",
  "linked_table_id": "<tagsTableId>",
  "type_of_relation": "mm"
}'
```

NocoDB creates the join table automatically for `mm`.

## Create a Link with `LinkToAnotherRecord` (classic)

The classic field works on every NocoDB version. Slightly different option shape:

```bash
nc field:create <baseId> <ordersTableId> '{
  "title": "Customer",
  "type": "LinkToAnotherRecord",
  "parentId": "<customersTableId>",
  "childId":  "<ordersTableId>",
  "type_of_relation": "bt"
}'
```

`parentId` is the "one" side; `childId` is the "many" side.

## Lookup — Show a Linked Column

A Lookup field surfaces a column value from a linked record. It requires an existing link field on the same table.

Setup sequence:

```bash
# 1) The link field must already exist
nc field:list <baseId> <ordersTableId>
# → suppose: c_customer_link_id  (Links → Customers)

# 2) Find the column to look up on the Customers side
nc field:list <baseId> <customersTableId>
# → suppose: c_customer_name_id  (SingleLineText "Name")

# 3) Create the Lookup
nc field:create <baseId> <ordersTableId> '{
  "title": "Customer Name",
  "type":  "Lookup",
  "fk_relation_column_id": "c_customer_link_id",
  "fk_lookup_column_id":   "c_customer_name_id"
}'
```

Lookups are read-only; they update automatically when the linked record's value changes.

## Rollup — Aggregate Linked Records

A Rollup aggregates a numeric column across all linked records.

```bash
nc field:create <baseId> <customersTableId> '{
  "title": "Lifetime Value",
  "type":  "Rollup",
  "fk_relation_column_id": "c_orders_link_id",
  "fk_rollup_column_id":   "c_amount_id",
  "rollup_function":       "sum"
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
| `countEmpty` / `countNotEmpty` | Empty vs non-empty |

## Verifying a Relation

After creating a link, verify both ends:

```bash
nc field:list <baseId> <ordersTableId>     # should include the new link field
nc field:list <baseId> <customersTableId>  # should include the auto-created inverse
```

Then test linking via the Data API:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[ {"id": "<orderRecordId>"} ]' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$CUSTOMERS_TABLE_ID/links/$LINK_FIELD_ID/$CUSTOMER_RECORD_ID"
```

Then re-read:

```bash
curl -sS \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$CUSTOMERS_TABLE_ID/links/$LINK_FIELD_ID/$CUSTOMER_RECORD_ID"
```

## Pitfalls

- **Lookup before link.** A Lookup created before its link field exists fails with `fk_relation_column_id not found`. Create the link first.
- **Rollup on non-numeric column.** Rollup with `sum` / `avg` against a text field returns an error. Use `count` / `countDistinct` / `countEmpty` for non-numeric aggregation.
- **Cycles.** NocoDB allows circular links (A→B and B→A) but not on the *same* base columns. Renaming the inverse field is OK; deleting one side does not auto-delete the other — clean up explicitly.
- **m2m join table is hidden by default.** It exists as a hidden table; access it via `nc table:list` with the unhide flag (`?includeHidden=1` on the API).
- **Display field on the linked side.** Lookups and link-card displays render the linked table's `display_field` — set it via `nc table:update ... '{"display_field_id":"..."}'` if the default first-non-system column isn't useful.
