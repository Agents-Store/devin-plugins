# Scenario — E-commerce Schema with Many-to-Many

Many-to-many between Products and Orders (each Order can have many Products; each Product can be on many Orders), with a Lookup and a Rollup to compute Order totals.

## Goal

```
Products
├── Name        (SingleLineText, display field)
├── Price       (Currency)
└── (auto inverse link "Orders")

Orders
├── OrderNo     (SingleLineText, display field)
├── Customer    (LinkToAnotherRecord → Customers, bt)
├── Products    (LinkToAnotherRecord → Products, relation_type: mm)
├── Subtotal    (Rollup of Products.Price, sum)
├── Status      (SingleSelect: Pending / Paid / Shipped / Refunded)
└── CreatedAt   (CreatedTime)

Customers (assumed pre-existing)
└── (auto inverse "Orders" link)
```

## Prereqs

Same environment as the CRM scenario — `NOCODB_URL`, `NOCODB_TOKEN`, `BASE_ID`, plus the two helpers:

```bash
nocodb_api() {   # paths are under /api/v3
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}
field_id() { nocodb_api GET "/meta/bases/$BASE_ID/tables/$1" | jq -r --arg t "$2" '.fields[] | select(.title==$t) | .id'; }
```

## Step 1 — Create Products

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Products",
  "fields": [
    { "title":"Name",  "type":"SingleLineText" },
    { "title":"Price", "type":"Currency", "options": { "currency_code":"USD" } }
  ]
}'
# capture PRODUCTS_TID
```

## Step 2 — Create Orders

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Orders",
  "fields": [
    { "title":"OrderNo",   "type":"SingleLineText" },
    { "title":"Status",    "type":"SingleSelect",
      "options": { "choices":[
        {"title":"Pending"},{"title":"Paid"},{"title":"Shipped"},{"title":"Refunded"}
      ]}},
    { "title":"CreatedAt", "type":"CreatedTime" }
  ]
}'
# capture ORDERS_TID
```

## Step 3 — Customer link (belongs-to on Orders)

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Customer",
  "type":  "LinkToAnotherRecord",
  "options": { "relation_type": "bt", "related_table_id": "'"$CUSTOMERS_TID"'" }
}'
LINK_CUST_ON_ORDERS=$(field_id $ORDERS_TID Customer)
```

## Step 4 — Products link (many-to-many)

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Products",
  "type":  "LinkToAnotherRecord",
  "options": { "relation_type": "mm", "related_table_id": "'"$PRODUCTS_TID"'" }
}'
LINK_PROD_ON_ORDERS=$(field_id $ORDERS_TID Products)
# verify both sides:
# nocodb_api GET /meta/bases/$BASE_ID/tables/$PRODUCTS_TID | jq '.fields[].title'   → "Orders" (auto inverse)
```

NocoDB creates the m2m join table automatically and hides it.

## Step 5 — Subtotal rollup

```bash
PRICE_COL=$(field_id $PRODUCTS_TID Price)

nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Subtotal",
  "type":  "Rollup",
  "options": {
    "related_field_id": "'"$LINK_PROD_ON_ORDERS"'",
    "related_table_rollup_field_id": "'"$PRICE_COL"'",
    "rollup_function": "sum"
  }
}'
```

## Step 6 — Customer-name Lookup on Orders

```bash
NAME_COL=$(field_id $CUSTOMERS_TID Name)

nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Customer Name",
  "type":  "Lookup",
  "options": {
    "related_field_id": "'"$LINK_CUST_ON_ORDERS"'",
    "related_table_lookup_field_id": "'"$NAME_COL"'"
  }
}'
```

## Step 7 — Sanity check

```
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: $ORDERS_TID
```

Expected fields on Orders: `OrderNo`, `Status`, `CreatedAt`, `Customer`, `Products`, `Subtotal`, `Customer Name`.

## Step 8 — Insert and link sample data

```bash
# Three products. The request body is an array of { "fields": {...} } (DataInsertRequestV3);
# the response is { "records": [ { "id", "fields" } ] } in the same order
curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[
        {"fields":{"Name":"Widget A","Price":29.99}},
        {"fields":{"Name":"Widget B","Price":49.99}},
        {"fields":{"Name":"Widget C","Price":19.99}}
      ]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${PRODUCTS_TID}/records"
# → capture three product record IDs PA, PB, PC from .records[].id

# One order
ORDER_ID=$(curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"fields":{"OrderNo":"ORD-1","Status":"Pending"}}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/records" | jq -r '.records[0].id')

# Link order → customer
curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"id":"'"$ACME_ID"'"}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/links/${LINK_CUST_ON_ORDERS}/${ORDER_ID}"

# Link order → products (many-to-many)
curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"id":"'"$PA"'"},{"id":"'"$PB"'"}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/links/${LINK_PROD_ON_ORDERS}/${ORDER_ID}"

# Read Order back
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/records/${ORDER_ID}" | jq
# expect: Subtotal == 79.98 ; Customer Name == "Acme Corp"
```

## Common Mistakes

- **m2m without specifying `relation_type`.** `options` requires both `relation_type` and `related_table_id`; leaving the type off is rejected. Always set `relation_type` explicitly (`mm` for tags / products / categories).
- **Rollup on a non-numeric.** `sum` against `Name` returns 0. Make sure the rollup field is numeric.
- **Forgetting that the m2m join table is hidden.** If you need to attach metadata to the relationship (e.g. quantity, line price), don't use `mm` — make an explicit `OrderLines` table with `bt` links to both Orders and Products.

## When to Choose an Explicit Join Table

Many real e-commerce schemas need per-line-item attributes (quantity, unit price snapshot, discount). Use:

```
OrderLines
├── Order      (LinkToAnotherRecord → Orders, bt)
├── Product    (LinkToAnotherRecord → Products, bt)
├── Quantity   (Number)
├── UnitPrice  (Currency)        ← snapshot at time of order
└── LineTotal  (Formula: {Quantity} * {UnitPrice})
```

Then `Orders.Subtotal` becomes a Rollup of `OrderLines.LineTotal` (sum), and the m2m `Products` link on Orders is dropped.
