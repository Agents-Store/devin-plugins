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

NocoDB v3 has a built-in dashboarding layer. A **Dashboard** is a container; **Widgets** are the individual tiles inside it (charts, KPIs, text blocks, iframes). All operations are Meta API v3 (cloud-hosted Enterprise or licensed self-hosted, Business plan and above); on Cloud / licensed the MCP `dashboards` category (`listTools`, then `callTool`) offers the same writes.

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

A widget's `type` is one of `chart`, `metric`, `text`, `iframe`. Charts are selected by `options.chart_type`. Per the OpenAPI `WidgetOptions*` schemas:

| `type` | `options` schema | Use case |
|--------|------------------|----------|
| `metric` | `WidgetOptionsMetric` | Single KPI tile (count / sum / avg / min / max) |
| `chart` | `WidgetOptionsBarChart` (`chart_type: "bar"`) | Categorical bar chart |
| `chart` | `WidgetOptionsLineChart` (`"line"`) | Time-series line |
| `chart` | `WidgetOptionsPieChart` (`"pie"`) | Proportional pie |
| `chart` | `WidgetOptionsDonutChart` (`"donut"`) | Like pie, with hole |
| `chart` | `WidgetOptionsScatter` (`"scatter"`) | Scatter plot |
| `text` | `WidgetOptionsText` | Markdown / plain text block |
| `iframe` | `WidgetOptionsIframe` | Embedded URL |

Top-level keys of a widget: `title`, `type`, `options`, `table_id` / `view_id` (the data source), `position` (`x`, `y`, `w`, `h` on a 12-column grid).

## Create a Dashboard

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Sales Overview", "description": "Daily KPIs" }' \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards"
```

Response includes the new `dashboard_id`.

## Add a Metric Widget

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title":    "Customers",
    "type":     "metric",
    "table_id": "<customersTableId>",
    "options": {
      "data_source": "table",
      "metric":      { "type": "count", "aggregation": "count" }
    }
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/dashboards/${DASHBOARD_ID}/widgets"
```

`metric.type` is `count` (all rows) or `summary` (aggregate a field — then `metric.field_id` is required and `aggregation` is `sum`, `avg`, `count`, `min` or `max`). To count a filtered subset, point the widget at a view that carries the filter (`view_id`, `data_source: "view"`).

## Add a Bar Chart Widget

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title":    "Revenue by Region",
    "type":     "chart",
    "table_id": "<ordersTableId>",
    "options": {
      "chart_type":  "bar",
      "data_source": "table",
      "data": {
        "x_axis": { "field_id": "<regionFieldId>" },
        "y_axis": { "fields": [ { "field_id": "<amountFieldId>", "aggregation": "sum" } ] }
      }
    }
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/dashboards/${DASHBOARD_ID}/widgets"
```

Pie and donut charts use `data.category.field_id` plus `data.value` (`{ "type": "count" }` or `{ "type": "summary", "field_id", "aggregation" }`) instead of axes.

> Probe the spec for the exact options shape per widget type:
> ```bash
> jq '.components.schemas.WidgetOptionsBarChart' \
>    skills/api-reference/references/nocodb-meta-openapi.json
> ```

## Fetch Widget Data

For one widget:

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID/data"
```

For an entire dashboard (all widgets in one call):

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/data"
```

The dashboard-level `/data` endpoint runs every widget's query in parallel server-side and returns the consolidated payload — prefer this over N individual widget calls when rendering a dashboard view.

## Update a Widget

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Renamed" }' \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID"
```

Type-specific `options` keys depend on the widget kind — refer to the matching `WidgetOptions*` schema (`appearance` carries colours, legend and size settings).

## Delete a Widget / Dashboard

```bash
# Widget
curl -sS -X DELETE -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID/widgets/$WIDGET_ID"

# Dashboard (deletes all widgets too)
curl -sS -X DELETE -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/dashboards/$DASHBOARD_ID"
```

**Confirm with the user before deleting** — both operations are unrecoverable.

## Pre-Flight Checklist

| Widget kind | Pre-flight |
|-------------|-----------|
| `metric` | `table_id` (or `view_id`) set; `metric.type` and `aggregation` set; a numeric `metric.field_id` for `summary` metrics |
| `chart` (bar / line / scatter) | `data.x_axis.field_id` and `data.y_axis.fields[].field_id` reference existing fields; `aggregation` matches the field type |
| `chart` (pie / donut) | One categorical `data.category.field_id`; `data.value` as `count` or a numeric `summary` |
| `text` | `content` set; `type` is `markdown` or `text` |
| `iframe` | `url` allowed by NocoDB's iframe-source allowlist (admin-controlled) |

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
