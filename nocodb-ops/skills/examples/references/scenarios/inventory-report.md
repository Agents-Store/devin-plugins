# Inventory Reporting

Step-by-step scenario for stock management and reporting with a NocoDB-backed inventory system.

## Scenario Overview

You have two tables in your NocoDB base:
- **Products** -- catalog of items with stock levels, categories, and pricing
- **Stock Movements** -- inbound and outbound stock transactions

## Step 1 -- Discover the schema

Confirm table structure before running queries.

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTablesList
Parameters: (none)
```

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTableSchema
Parameters:
  tableId: "m_products"
```

## Step 2 -- Query current inventory

List all products with their stock levels, sorted by quantity ascending (lowest stock first).

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_products"
  fields: ["Name", "SKU", "Category", "Quantity", "ReorderLevel", "Price"]
  sort: [{ "field": "Quantity", "direction": "asc" }]
  pageSize: 100
```

## Step 3 -- Count low-stock items

Find how many products are below their reorder level. Use a filter to compare quantity against a threshold.

```
Tool: mcp__plugin_nocodb-ops_nocodb__countRecords
Parameters:
  tableId: "m_products"
  where: "(Quantity,lte,10)"
```

For a more precise check against each product's own reorder level, query and compare:

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_products"
  where: "(Quantity,lte,10)"
  fields: ["Name", "SKU", "Quantity", "ReorderLevel", "Category"]
  sort: [{ "field": "Quantity", "direction": "asc" }]
```

## Step 4 -- Aggregate stock value by category

Calculate total inventory value per product category -- one `aggregate` call with one filter group per category:

```
Tool: mcp__plugin_nocodb-ops_nocodb__aggregate
Parameters:
  tableId: "m_products"
  aggregations: [{ "field": "Price", "type": "sum" }]
  filterGroups: [
    { "alias": "Electronics", "filter": { "field": "Category", "operator": "eq", "value": "Electronics" } },
    { "alias": "Clothing",    "filter": { "field": "Category", "operator": "eq", "value": "Clothing" } },
    { "alias": "Food",        "filter": { "field": "Category", "operator": "eq", "value": "Food" } }
  ]
```

Add one group per remaining category (Office Supplies, ...). The result is one block per alias.

## Step 5 -- Count products per category

Get the number of products in each category with one call:

```
Tool: mcp__plugin_nocodb-ops_nocodb__groupByRecords
Parameters:
  tableId: "m_products"
  fieldId: "<Category field id from getTableSchema>"
```

Each distinct category comes back with its count.

## Step 6 -- Review recent stock movements

Pull the last 50 stock transactions to check for anomalies.

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_stock_movements"
  fields: ["Product", "Type", "Quantity", "Date", "Reference", "Notes"]
  sort: [{ "field": "Date", "direction": "desc" }]
  pageSize: 50
```

## Step 7 -- Find items with no recent movement

Identify dead stock -- products that have not had any movement in 90 days.

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_products"
  where: "(LastMovement,lt,daysAgo,90)"
  fields: ["Name", "SKU", "Category", "Quantity", "LastMovement"]
  sort: [{ "field": "LastMovement", "direction": "asc" }]
```

Note: `(LastMovement,lt,daysAgo,90)` keeps products whose last movement is **before** 90 days ago; ascending order surfaces the most stagnant items first. Products with an empty `LastMovement` are not matched -- query them separately with `(LastMovement,blank)` and review them manually.

## Step 8 -- Build a summary report

Combine the results from previous steps into a structured report:

1. **Total products:** Use `countRecords` with no filter
2. **Low-stock alerts:** Count and list items below reorder level
3. **Category breakdown:** Aggregate counts and values per category
4. **Dead stock:** List items with no movement in 90+ days
5. **Recent activity:** Summarize last 7 days of stock movements

```
Tool: mcp__plugin_nocodb-ops_nocodb__countRecords
Parameters:
  tableId: "m_products"
```

```
Tool: mcp__plugin_nocodb-ops_nocodb__countRecords
Parameters:
  tableId: "m_stock_movements"
  where: "(Date,isWithin,pastWeek)"
```

## Summary

This workflow covers the inventory reporting cycle:

1. Discover tables and field structure
2. Query stock levels sorted by quantity
3. Count and list low-stock items
4. Aggregate value by category
5. Count products per category
6. Review recent stock movements
7. Identify dead stock
8. Compile the summary report
