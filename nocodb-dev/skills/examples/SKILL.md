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

Practical end-to-end scenarios. Each example follows the discover → plan → apply → verify loop using MCP for discovery/verification and CLI/API for writes.

## Quick Examples

### Create a table from scratch

```bash
nc table:create $BASE_ID '{
  "title": "Tasks",
  "fields": [
    { "title": "Title",     "type": "SingleLineText" },
    { "title": "Status",    "type": "SingleSelect",
      "colOptions": { "options":[
        {"title":"Todo"},{"title":"Doing"},{"title":"Done"}
      ]}},
    { "title": "Due",       "type": "Date" },
    { "title": "Notes",     "type": "LongText" }
  ]
}'
```

### Add a field to an existing table

```bash
nc field:create $BASE_ID $TASKS_TABLE_ID '{"title":"Priority","type":"Rating","max":3}'
```

### Rename a field

```bash
nc field:update $BASE_ID $TASKS_TABLE_ID $COLUMN_ID '{"title":"Stars"}'
```

### Build a Kanban view

```bash
nc view:create:kanban $BASE_ID $TASKS_TABLE_ID '{
  "title": "Board",
  "fk_grp_col_id": "<statusColumnId>"
}'
```

### Add a Formula

```bash
nc field:create $BASE_ID $TASKS_TABLE_ID '{
  "title": "Days Until Due",
  "type": "Formula",
  "formula": "DATETIME_DIFF({Due}, NOW(), \"days\")"
}'
```

### Wire a Slack webhook on insert

```bash
nc hook:create $BASE_ID $TASKS_TABLE_ID '{
  "title": "Slack on new task",
  "event": "after",
  "operation": "insert",
  "notification": {
    "type": "Messaging",
    "payload": {
      "channel": "Slack",
      "webhook_url": "https://hooks.slack.com/services/T0/B0/XXX",
      "body": ":pencil: New task: {{record.Title}}"
    }
  },
  "active": true,
  "version": "v3"
}'
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
- **Webhook conditions match field titles, case-sensitive.** Mistyped column references render literally instead of erroring.
