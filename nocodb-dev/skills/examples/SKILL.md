---
name: examples
description: |
  End-to-end NocoDB schema-development walkthroughs. Use when:
  - "show me a schema example"
  - "how do I build a CRM in NocoDB?"
  - "e-commerce schema example"
  - "schema design walkthrough"
  - "NocoDB dev scenarios"
---

# NocoDB Dev — Worked Examples

Practical end-to-end scenarios. Each example follows the discover → plan → apply → verify loop using MCP for discovery/verification and REST (`curl`) — or, on Cloud / licensed, the MCP `callTool` schema tools — for writes.

The examples use the small `nocodb_api` wrapper from the **cli-reference** skill (`nocodb_api METHOD /path ['body']`, paths under `${NOCODB_URL}/api/v3`, token from `NOCODB_TOKEN`):

```bash
nocodb_api() {
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}
```

## Quick Examples

### Create a table from scratch

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Tasks",
  "fields": [
    { "title": "Title",     "type": "SingleLineText" },
    { "title": "Status",    "type": "SingleSelect",
      "options": { "choices":[
        {"title":"Todo"},{"title":"Doing"},{"title":"Done"}
      ]}},
    { "title": "Due",       "type": "Date" },
    { "title": "Notes",     "type": "LongText" }
  ]
}'
```

### Add a field to an existing table

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TASKS_TABLE_ID/fields '{"title":"Priority","type":"Rating","options":{"max_value":3}}'
```

### Rename a field

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/fields/$FIELD_ID '{"title":"Stars"}'
```

### Build a Kanban view

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TASKS_TABLE_ID/views '{
  "title": "Board",
  "type": "kanban",
  "options": { "stack_by": { "field_id": "<statusFieldId>" } }
}'
```

### Add a Formula

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TASKS_TABLE_ID/fields '{
  "title": "Days Until Due",
  "type": "Formula",
  "options": { "formula": "DATETIME_DIFF({Due}, NOW(), \"days\")" }
}'
```

### Wire a Slack webhook on insert

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TASKS_TABLE_ID/hooks '{
  "title": "Slack on new task",
  "event": "record",
  "operation": ["insert"],
  "notification": {
    "type": "Slack",
    "payload": { "body": ":pencil: New task: {{record.Title}}" }
  },
  "active": true
}'
```

### The same on Cloud / licensed, over MCP

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "fields"
mcp__plugin_nocodb-dev_nocodb__callTool   name: "createField"
  arguments: { tableId: "<tasksTableId>",
               field: { title: "Priority", type: "Rating", options: { max_value: 3 } } }
```

## Full Scenario Walkthroughs

See `references/scenarios/`:

- **crm-schema-buildout.md** — Build a CRM from zero: Customers, Orders (with link to Customers), Products (m2m to Orders), plus Lookup of customer name on Order and Rollup of order totals on Customer.
- **ecommerce-relations.md** — E-commerce schema with many-to-many Products↔Orders, Lookup customer name onto Order line items, computed Order Total formula.

## Tips

- **Always `getTableSchema` after every write.** Schema responses are your audit trail.
- **Build relations bottom-up.** Create the "many" tables (Orders) before the "one" tables (Customers) only if the link is `bt`. For `hm` and `mm`, either order works.
- **Lookups need links first.** Don't try to PATCH a Lookup config to point at a not-yet-existing link — NocoDB rejects with 400.
- **System fields are write-once.** `CreatedTime` etc. populate themselves; don't try to seed them from imports.
- **Webhook templates match field titles, case-sensitive.** Mistyped `{{record.<Field>}}` references render literally instead of erroring.
