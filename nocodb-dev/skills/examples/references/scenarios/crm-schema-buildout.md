# Scenario — Build a CRM Schema From Zero

End-to-end build of a small CRM: **Customers**, **Orders** (with belongs-to link to Customers), and a Lookup + Rollup so each side sees the other usefully.

## Goal

After this walkthrough you will have:

```
Customers
├── Name              (SingleLineText, display field)
├── Email             (Email)
├── Status            (SingleSelect: Lead / Active / Churned)
├── Lifetime Value    (Rollup of Orders.Amount, sum)
└── (auto inverse link "Orders")

Orders
├── OrderNo           (SingleLineText, display field)
├── Customer          (Links → Customers, type: bt)
├── Customer Name     (Lookup of Customers.Name through Customer link)
├── Amount            (Currency)
├── Status            (SingleSelect: Pending / Paid / Refunded)
└── CreatedAt         (CreatedTime)
```

Plus one Kanban view on Orders grouped by Status.

## Prereqs

```bash
export NOCODB_URL=...
export NOCODB_API_TOKEN=...
export NOCODB_VERBOSE=1
BASE_ID=<your base id>
```

## Step 1 — Create Customers

```bash
nc table:create $BASE_ID '{
  "title": "Customers",
  "fields": [
    { "title":"Name",   "type":"SingleLineText" },
    { "title":"Email",  "type":"Email" },
    { "title":"Status", "type":"SingleSelect",
      "colOptions": { "options":[
        {"title":"Lead"}, {"title":"Active"}, {"title":"Churned"}
      ]}}
  ]
}'
```

Capture the new `tableId` (prefix `m`) — call it `CUSTOMERS_TID`.

## Step 2 — Create Orders

```bash
nc table:create $BASE_ID '{
  "title": "Orders",
  "fields": [
    { "title":"OrderNo",   "type":"SingleLineText" },
    { "title":"Amount",    "type":"Currency", "currency_code":"USD" },
    { "title":"Status",    "type":"SingleSelect",
      "colOptions": { "options":[
        {"title":"Pending"}, {"title":"Paid"}, {"title":"Refunded"}
      ]}},
    { "title":"CreatedAt", "type":"CreatedTime" }
  ]
}'
```

Capture as `ORDERS_TID`.

## Step 3 — Add the link

On Orders, add a belongs-to link to Customers:

```bash
nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Customer",
  "type":  "Links",
  "linked_table_id": "'"$CUSTOMERS_TID"'",
  "type_of_relation": "bt"
}'
```

Verify both sides:

```bash
nc field:list $BASE_ID $ORDERS_TID    # should show "Customer"
nc field:list $BASE_ID $CUSTOMERS_TID # should show auto-inverse "Orders"
```

Capture column IDs:

- `ORDERS.Customer` link → `LINK_ON_ORDERS`
- `ORDERS.OrderNo` → `ORDERNO_COL`
- `CUSTOMERS.Name` → `NAME_COL`
- `CUSTOMERS.Orders` (auto inverse) → `LINK_ON_CUSTOMERS`
- `ORDERS.Amount` → `AMOUNT_COL`

## Step 4 — Lookup customer name on Order

```bash
nc field:create $BASE_ID $ORDERS_TID '{
  "title": "Customer Name",
  "type":  "Lookup",
  "fk_relation_column_id": "'"$LINK_ON_ORDERS"'",
  "fk_lookup_column_id":   "'"$NAME_COL"'"
}'
```

## Step 5 — Rollup lifetime value on Customer

```bash
nc field:create $BASE_ID $CUSTOMERS_TID '{
  "title": "Lifetime Value",
  "type":  "Rollup",
  "fk_relation_column_id": "'"$LINK_ON_CUSTOMERS"'",
  "fk_rollup_column_id":   "'"$AMOUNT_COL"'",
  "rollup_function":       "sum"
}'
```

## Step 6 — Set display fields

OrderNo on Orders, Name on Customers (Name is auto-picked, but make it explicit):

```bash
nc table:update $BASE_ID $ORDERS_TID    '{"display_field_id":"'"$ORDERNO_COL"'"}'
nc table:update $BASE_ID $CUSTOMERS_TID '{"display_field_id":"'"$NAME_COL"'"}'
```

## Step 7 — Kanban view on Orders

Find Orders.Status column ID:

```bash
nc field:list $BASE_ID $ORDERS_TID
# capture STATUS_COL
```

```bash
nc view:create:kanban $BASE_ID $ORDERS_TID '{
  "title": "Board",
  "fk_grp_col_id": "'"$STATUS_COL"'"
}'
```

## Step 8 — Verify end-to-end

```
mcp__nocodb__getTablesList                        # both tables visible
mcp__nocodb__getTableSchema  tableId: $ORDERS_TID
# expected: OrderNo, Customer (Links), Customer Name (Lookup), Amount, Status, CreatedAt
mcp__nocodb__getTableSchema  tableId: $CUSTOMERS_TID
# expected: Name, Email, Status, Orders (auto inverse), Lifetime Value (Rollup)
```

Insert one Customer + one Order, link them, and confirm:

- Order.`Customer Name` populates with the Customer's Name.
- Customer.`Lifetime Value` shows the order's Amount.

```bash
# Create a customer
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"records":[{"fields":{"Name":"Acme Corp","Email":"info@acme.com","Status":"Active"}}]}' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$CUSTOMERS_TID/records"
# capture acme record id → ACME_ID

# Create an order
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"records":[{"fields":{"OrderNo":"ACM-1001","Amount":1500,"Status":"Paid"}}]}' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/records"
# capture order record id → ORDER_ID

# Link order → customer
curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" -H "Content-Type: application/json" \
  -d '[{"id":"'"$ACME_ID"'"}]' \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/links/$LINK_ON_ORDERS/$ORDER_ID"

# Read the order back
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$ORDERS_TID/records/$ORDER_ID" | jq
# expect: Customer Name == "Acme Corp"

# Read the customer back
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$CUSTOMERS_TID/records/$ACME_ID" | jq
# expect: Lifetime Value == 1500
```

## Cleanup (if you were rehearsing)

```bash
nc table:delete $BASE_ID $ORDERS_TID
nc table:delete $BASE_ID $CUSTOMERS_TID
```

(Delete Orders first; the link on Customers is auto-removed when its source link is gone.)
