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
├── Products    (Links → Products, type: mm)
├── Subtotal    (Rollup of Products.Price, sum)
├── Status      (SingleSelect: Pending / Paid / Shipped / Refunded)
└── CreatedAt   (CreatedTime)

Customers (assumed pre-existing)
└── (auto inverse "Orders" link)
```

## Step 1 — Create Products

```bash
nc table:create $BASE_ID '{
  "title": "Products",
  "fields": [
    { "title":"Name",  "type":"SingleLineText" },
    { "title":"Price", "type":"Currency", "currency_code":"USD" }
  ]
}'
# capture PRODUCTS_TID
```

## Step 2 — Create Orders

```bash
nc table:create $BASE_ID '{
  "title": "Orders",
  "fields": [
    { "title":"OrderNo",   "type":"SingleLineText" },
    { "title":"Status",    "type":"SingleSelect",
      "colOptions": { "options":[
        {"title":"Pending"},{"title":"Paid"},{"title":"Shipped"},{"title":"Refunded"}
      ]}},
    { "title":"CreatedAt", "type":"CreatedTime" }
  ]
}'
# capture ORDERS_TID
```

## Step 3 — Customer link (belongs-to on Orders)

```bash
nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Customer",
  "type":  "Links",
  "linked_table_id": "'"$CUSTOMERS_TID"'",
  "type_of_relation": "bt"
}'
# verify: nc field:list $BASE_ID $ORDERS_TID — capture LINK_CUST_ON_ORDERS
```

## Step 4 — Products link (many-to-many)

```bash
nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Products",
  "type":  "Links",
  "linked_table_id": "'"$PRODUCTS_TID"'",
  "type_of_relation": "mm"
}'
# verify both sides:
# nc field:list $BASE_ID $ORDERS_TID    → "Products"   (LINK_PROD_ON_ORDERS)
# nc field:list $BASE_ID $PRODUCTS_TID  → "Orders"     (auto inverse)
```

NocoDB creates the m2m join table automatically and hides it.

## Step 5 — Subtotal rollup

```bash
# Find Products.Price column ID
nc field:list $BASE_ID $PRODUCTS_TID
# capture PRICE_COL

nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Subtotal",
  "type":  "Rollup",
  "fk_relation_column_id": "'"$LINK_PROD_ON_ORDERS"'",
  "fk_rollup_column_id":   "'"$PRICE_COL"'",
  "rollup_function":       "sum"
}'
```

## Step 6 — Customer-name Lookup on Orders

```bash
# Customers.Name column ID
nc field:list $BASE_ID $CUSTOMERS_TID
# capture NAME_COL

nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Customer Name",
  "type":  "Lookup",
  "fk_relation_column_id": "'"$LINK_CUST_ON_ORDERS"'",
  "fk_lookup_column_id":   "'"$NAME_COL"'"
}'
```

## Step 7 — Sanity check

```
mcp__nocodb__getTableSchema  tableId: $ORDERS_TID
```

Expected fields on Orders: `OrderNo`, `Status`, `CreatedAt`, `Customer`, `Products`, `Subtotal`, `Customer Name`.

## Step 8 — Insert and link sample data

```bash
# Three products
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"records":[
        {"fields":{"Name":"Widget A","Price":29.99}},
        {"fields":{"Name":"Widget B","Price":49.99}},
        {"fields":{"Name":"Widget C","Price":19.99}}
      ]}' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$PRODUCTS_TID/records"
# → capture three product record IDs PA, PB, PC

# One order
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"records":[{"fields":{"OrderNo":"ORD-1","Status":"Pending"}}]}' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/records"
# → capture ORDER_ID

# Link order → customer
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '[{"id":"'"$ACME_ID"'"}]' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/links/$LINK_CUST_ON_ORDERS/$ORDER_ID"

# Link order → products (many-to-many)
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '[{"id":"'"$PA"'"},{"id":"'"$PB"'"}]' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/links/$LINK_PROD_ON_ORDERS/$ORDER_ID"

# Read Order back
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/records/$ORDER_ID" | jq
# expect: Subtotal == 79.98 ; Customer Name == "Acme Corp"
```

## Common Mistakes

- **m2m without specifying `type_of_relation`.** Defaults to `hm`, which is not what you want for tags / products / categories. Always set `type_of_relation` explicitly.
- **Rollup on a non-numeric.** `sum` against `Name` returns 0. Make sure the rollup column is numeric.
- **Forgetting that the m2m join table is hidden.** If you need to attach metadata to the relationship (e.g. quantity, line price), don't use `mm` — make an explicit `OrderLines` table with `bt` links to both Orders and Products.

## When to Choose an Explicit Join Table

Many real e-commerce schemas need per-line-item attributes (quantity, unit price snapshot, discount). Use:

```
OrderLines
├── Order      (Links → Orders, bt)
├── Product    (Links → Products, bt)
├── Quantity   (Number)
├── UnitPrice  (Currency)        ← snapshot at time of order
└── LineTotal  (Formula: {Quantity} * {UnitPrice})
```

Then `Orders.Subtotal` becomes a Rollup of `OrderLines.LineTotal` (sum), and the m2m `Products` link on Orders is dropped.
