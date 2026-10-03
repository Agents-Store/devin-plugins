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
├── Customer          (LinkToAnotherRecord → Customers, relation_type: bt)
├── Customer Name     (Lookup of Customers.Name through Customer link)
├── Amount            (Currency)
├── Status            (SingleSelect: Pending / Paid / Refunded)
└── CreatedAt         (CreatedTime)
```

Plus one Kanban view on Orders grouped by Status.

## Prereqs

```bash
export NOCODB_URL=...        # instance URL, no trailing slash
export NOCODB_TOKEN=...      # API token
BASE_ID=<your base id>

# tiny wrapper — paths are under /api/v3
nocodb_api() {
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}

# field id by title:  field_id <tableId> <title>
field_id() { nocodb_api GET "/meta/bases/$BASE_ID/tables/$1" | jq -r --arg t "$2" '.fields[] | select(.title==$t) | .id'; }
```

On Cloud / licensed every `POST …/tables` and `POST …/fields` below can instead be one MCP `callTool` (`createTable { title, fields }`, `createField { tableId, field }`) — the objects are the same.

## Step 1 — Create Customers

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Customers",
  "fields": [
    { "title":"Name",   "type":"SingleLineText" },
    { "title":"Email",  "type":"Email" },
    { "title":"Status", "type":"SingleSelect",
      "options": { "choices":[
        {"title":"Lead"}, {"title":"Active"}, {"title":"Churned"}
      ]}}
  ]
}'
```

Capture the new `tableId` (prefix `m`) — call it `CUSTOMERS_TID`.

## Step 2 — Create Orders

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Orders",
  "fields": [
    { "title":"OrderNo",   "type":"SingleLineText" },
    { "title":"Amount",    "type":"Currency", "options": { "currency_code":"USD" } },
    { "title":"Status",    "type":"SingleSelect",
      "options": { "choices":[
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
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Customer",
  "type":  "LinkToAnotherRecord",
  "options": { "relation_type": "bt", "related_table_id": "'"$CUSTOMERS_TID"'" }
}'
```

Verify both sides:

```bash
nocodb_api GET /meta/bases/$BASE_ID/tables/$ORDERS_TID    | jq '.fields[].title'   # should show "Customer"
nocodb_api GET /meta/bases/$BASE_ID/tables/$CUSTOMERS_TID | jq '.fields[].title'   # should show auto-inverse "Orders"
```

Capture field IDs:

```bash
LINK_ON_ORDERS=$(field_id $ORDERS_TID Customer)
ORDERNO_COL=$(field_id $ORDERS_TID OrderNo)
NAME_COL=$(field_id $CUSTOMERS_TID Name)
LINK_ON_CUSTOMERS=$(field_id $CUSTOMERS_TID Orders)     # auto inverse
AMOUNT_COL=$(field_id $ORDERS_TID Amount)
```

## Step 4 — Lookup customer name on Order

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/fields '{
  "title": "Customer Name",
  "type":  "Lookup",
  "options": {
    "related_field_id": "'"$LINK_ON_ORDERS"'",
    "related_table_lookup_field_id": "'"$NAME_COL"'"
  }
}'
```

## Step 5 — Rollup lifetime value on Customer

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$CUSTOMERS_TID/fields '{
  "title": "Lifetime Value",
  "type":  "Rollup",
  "options": {
    "related_field_id": "'"$LINK_ON_CUSTOMERS"'",
    "related_table_rollup_field_id": "'"$AMOUNT_COL"'",
    "rollup_function": "sum"
  }
}'
```

## Step 6 — Set display fields

OrderNo on Orders, Name on Customers (Name is auto-picked, but make it explicit):

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/tables/$ORDERS_TID    '{"display_field_id":"'"$ORDERNO_COL"'"}'
nocodb_api PATCH /meta/bases/$BASE_ID/tables/$CUSTOMERS_TID '{"display_field_id":"'"$NAME_COL"'"}'
```

## Step 7 — Kanban view on Orders

Find Orders.Status field ID:

```bash
STATUS_COL=$(field_id $ORDERS_TID Status)
```

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$ORDERS_TID/views '{
  "title": "Board",
  "type": "kanban",
  "options": { "stack_by": { "field_id": "'"$STATUS_COL"'" } }
}'
```

(Views need cloud Enterprise or a licensed self-hosted deployment.)

## Step 8 — Verify end-to-end

```
mcp__plugin_nocodb-dev_nocodb__getTablesList                        # both tables visible
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: $ORDERS_TID
# expected: OrderNo, Customer (link), Customer Name (Lookup), Amount, Status, CreatedAt
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: $CUSTOMERS_TID
# expected: Name, Email, Status, Orders (auto inverse), Lifetime Value (Rollup)
```

Insert one Customer + one Order, link them, and confirm:

- Order.`Customer Name` populates with the Customer's Name.
- Customer.`Lifetime Value` shows the order's Amount.

```bash
# Create a customer. The request body is { "fields": {...} } or an array of those (DataInsertRequestV3);
# the response is { "records": [ { "id", "fields" } ] }
ACME_ID=$(curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"fields":{"Name":"Acme Corp","Email":"info@example.com","Status":"Active"}}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${CUSTOMERS_TID}/records" | jq -r '.records[0].id')

# Create an order
ORDER_ID=$(curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"fields":{"OrderNo":"ACM-1001","Amount":1500,"Status":"Paid"}}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/records" | jq -r '.records[0].id')

# Link order → customer
curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '[{"id":"'"$ACME_ID"'"}]' \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/links/${LINK_ON_ORDERS}/${ORDER_ID}"

# Read the order back
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${ORDERS_TID}/records/${ORDER_ID}" | jq
# expect: Customer Name == "Acme Corp"

# Read the customer back
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${CUSTOMERS_TID}/records/${ACME_ID}" | jq
# expect: Lifetime Value == 1500
```

## Cleanup (if you were rehearsing)

```bash
nocodb_api DELETE /meta/bases/$BASE_ID/tables/$ORDERS_TID
nocodb_api DELETE /meta/bases/$BASE_ID/tables/$CUSTOMERS_TID
```

(Delete Orders first; the link on Customers is auto-removed when its source link is gone.) On Cloud / licensed the deleted tables sit in the base trash until the retention window ends (`listTrash`, `restoreFromTrash`).
