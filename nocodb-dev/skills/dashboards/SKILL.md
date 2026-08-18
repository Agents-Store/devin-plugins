---
name: dashboards
description: |
  Create and manage NocoDB Dashboards and Widgets via Meta API v3. Use when:
  - "create a dashboard"
  - "add a chart / metric / KPI widget"
  - "list widgets on a dashboard"
  - "fetch widget data"
  - "update a dashboard"
  - "delete a widget"
---

# Dashboards & Widgets

NocoDB v3 has a built-in dashboarding layer. A **Dashboard** is a container; **Widgets** are the individual tiles inside it (charts, KPIs, text blocks, iframes). All operations are Meta API v3.

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/dashboards` | `GET` | List dashboards |
| `/api/v3/meta/bases/{base_id}/dashboards` | `POST` | Create dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `GET` | Get dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `PATCH` | Update dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `DELETE` | Delete dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/data` | `GET` | Fetch all widget data for the dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets` | `GET` | List widgets |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets` | `POST` | Create widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `GET` | Get widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `PATCH` | Update widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `DELETE` | Delete widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}/data` | `GET` | Fetch widget data |

## Widget Types

Per the OpenAPI `WidgetOptions*` schemas:

| `type` | Schema | Use case |
|--------|--------|----------|
| `metric` | `WidgetOptionsMetric` | Single KPI tile (count / sum / avg) |
| `bar_chart` | `WidgetOptionsBarChart` | Categorical bar chart |
| `line_chart` | `WidgetOptionsLineChart` | Time-series line |
| `pie_chart` | `WidgetOptionsPieChart` | Proportional pie |
| `donut_chart` | `WidgetOptionsDonutChart` | Like pie, with hole |
| `text` | `WidgetOptionsText` | Markdown content block |
| `iframe` | `WidgetOptionsIframe` | Embedded URL |

## Create a Dashboard

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Sales Overview", "description": "Daily KPIs" }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards"
```

Response includes the new `dashboard_id`.

## Add a Metric Widget

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":  "Active Customers",
    "type":   "metric",
    "options": {
      "table_id":     "<customersTableId>",
      "aggregation":  "count",
      "filter":       "(Status,eq,Active)"
    }
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets"
```

## Add a Bar Chart Widget

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":  "Revenue by Region",
    "type":   "bar_chart",
    "options": {
      "table_id":     "<ordersTableId>",
      "x_axis":       { "field_id": "<regionFieldId>" },
      "y_axis":       { "field_id": "<amountFieldId>", "aggregation": "sum" }
    }
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets"
```

> Probe the spec for the exact options shape per widget type:
> ```bash
> jq '.components.schemas.WidgetOptionsBarChart' \
>    skills/api-reference/references/nocodb-meta-openapi.json
> ```

## Fetch Widget Data

For one widget:

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID/data"
```

For an entire dashboard (all widgets in one call):

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/data"
```

The dashboard-level `/data` endpoint runs every widget's query in parallel server-side and returns the consolidated payload — prefer this over N individual widget calls when rendering a dashboard view.

## Update a Widget

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Renamed", "options": { "filter": "(Status,eq,Premium)" } }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID"
```

Type-specific `options` keys depend on the widget kind — refer to the matching `WidgetOptions*` schema.

## Delete a Widget / Dashboard

```bash
# Widget
curl -sS -X DELETE -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID"

# Dashboard (deletes all widgets too)
curl -sS -X DELETE -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID"
```

**Confirm with the user before deleting** — both operations are unrecoverable.

## Pre-Flight Checklist

| Widget kind | Pre-flight |
|-------------|-----------|
| `metric` | `table_id` set; `aggregation` is one of `count` / `sum` / `avg` / `min` / `max`; numeric `field_id` for non-count aggregations |
| `bar_chart` / `line_chart` | `x_axis.field_id` and `y_axis.field_id` reference existing columns; `y_axis.aggregation` matches the field type |
| `pie_chart` / `donut_chart` | One categorical `field_id`; one numeric `field_id` (or count) |
| `text` | Body markdown ≤ NocoDB's text limit |
| `iframe` | URL allowed by NocoDB's iframe-source allowlist (admin-controlled) |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on widget create | `options` missing required fields for that type | Probe `WidgetOptions<Type>` schema and add the missing keys |
| Widget shows no data | `filter` excludes everything; `field_id` deleted | Verify the field still exists and the filter matches some records |
| Widget on `iframe` blocks loading | URL not in allowlist | Admin must add the host to allowed iframe sources |
| Data endpoint slow | Many large widgets querying simultaneously | Reduce widget count or widen filters |
| 404 on widget | Widget deleted or wrong `dashboard_id` | List widgets to confirm |

## See Also

- **api-reference** skill — full Meta API v3 path reference
- `references/nocodb-meta-openapi.json` — OpenAPI source of truth for `WidgetOptions*` schemas
- **field-management** skill — fields used as widget axes / metrics must exist on the source table
