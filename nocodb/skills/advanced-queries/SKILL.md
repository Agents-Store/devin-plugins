---
name: advanced-queries
description: Advanced data queries — search, aggregate, group by, complex filters. This skill should be used when the user asks to perform complex queries, aggregate data, group records, or search with advanced filter logic.
---

# Advanced Queries

Guide for advanced NocoDB data operations — full-text search, aggregation, grouping, and raw queries.

## Available Tools

| Tool | Purpose |
|------|---------|
| `search_records` | Full-text search across table fields |
| `query` | Execute raw query on table data |
| `aggregate` | Aggregate functions (sum, count, avg, min, max) |
| `group_by` | Group records by a field with counts |

## Full-Text Search

```
Tool: search_records
Input: {
  "table_id": "tbl_abc123",
  "query": "john doe"
}

Returns: Records matching the search query across all text fields.
```

Useful for:
- Finding records without knowing exact field
- Quick lookup by name, email, or any text content
- Building search interfaces

## Aggregation

### Sum
```
Tool: aggregate
Input: {
  "table_id": "tbl_orders",
  "column": "Amount",
  "function": "sum"
}
→ { "value": 125000 }
```

### Count
```
Tool: aggregate
Input: {
  "table_id": "tbl_contacts",
  "column": "Id",
  "function": "count"
}
→ { "value": 342 }
```

### Average
```
Tool: aggregate
Input: {
  "table_id": "tbl_products",
  "column": "Price",
  "function": "avg"
}
→ { "value": 49.99 }
```

### Min / Max
```
Tool: aggregate
Input: {
  "table_id": "tbl_orders",
  "column": "Amount",
  "function": "max"
}
→ { "value": 15000 }
```

### Aggregation Functions
| Function | Description |
|----------|-------------|
| `sum` | Total of all values |
| `count` | Number of records |
| `avg` | Average value |
| `min` | Minimum value |
| `max` | Maximum value |

## Group By

```
Tool: group_by
Input: {
  "table_id": "tbl_contacts",
  "column": "Status"
}

Returns:
[
  { "Status": "Active", "count": 150 },
  { "Status": "Lead", "count": 85 },
  { "Status": "Inactive", "count": 42 }
]
```

Useful for:
- Pipeline distribution (deals by stage)
- Status summaries
- Category breakdowns

## Raw Query

```
Tool: query
Input: {
  "table_id": "tbl_orders",
  "where": "(Status,eq,Active)~and(Amount,gt,5000)",
  "sort": "-Amount",
  "fields": "Name,Amount,Status",
  "limit": 50
}
```

### Where Clause Syntax

Operators: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `like`, `is`, `isnot`, `null`, `notnull`

Combinators: `~and`, `~or`

Examples:
```
(Status,eq,Active)
(Amount,gt,1000)~and(Status,eq,Active)
(Name,like,John)~or(Email,like,john)
(DueDate,lt,2024-01-01)~and(Status,neq,Done)
(Category,is,null)
```

## Workflows

### Sales Dashboard Data
```
1. aggregate(orders, Amount, sum) → Total revenue
2. aggregate(orders, Id, count) → Total orders
3. aggregate(orders, Amount, avg) → Average order value
4. group_by(orders, Status) → Orders by status
5. group_by(deals, Stage) → Deal pipeline distribution
```

### Data Quality Audit
```
1. aggregate(contacts, Id, count) → Total records
2. search_records(contacts, query="test") → Find test data
3. query(contacts, where="(Email,is,null)") → Find records missing email
4. query(contacts, where="(Status,is,null)") → Find records missing status
```

### Duplicate Detection
```
1. search_records(table, query="john@example.com") → Search for potential duplicates
2. If multiple results: review and merge/delete duplicates
```

## Complex Query Patterns

### Nested AND/OR Logic
Find records where (Status = "Active" AND Priority = "High") OR (Status = "Pending" AND Amount > 5000):
```
query({
  table_id: "tbl_xxx",
  where: "(Status,eq,Active)~and(Priority,eq,High)~or((Status,eq,Pending)~and(Amount,gt,5000))"
})
```

### Date Range Queries
Records created in the last 7 days with status "Open":
```
query({
  table_id: "tbl_xxx",
  where: "(CreatedAt,gte,2024-01-01)~and(CreatedAt,lte,2024-01-07)~and(Status,eq,Open)",
  sort: "-CreatedAt"
})
```

### Aggregation with Filters
Count records grouped by Status, only for Amount > 1000:
```
1. aggregate(table_id, column="Amount", function="sum", where="(Status,eq,Active)") → sum for active
2. group_by(table_id, column="Status", where="(Amount,gt,1000)") → distribution of high-value records
```

### Pagination for Large Datasets
```
1. query(table_id, limit=100, offset=0) → first page
2. query(table_id, limit=100, offset=100) → second page
3. Continue until response returns fewer records than limit
```

### Multi-field Search with Sorting
```
query({
  table_id: "tbl_xxx",
  where: "(Name,like,%john%)~or(Email,like,%john%)",
  sort: "Name",
  fields: "Name,Email,Status",
  limit: 25
})
```

## Best Practices

1. **Use search for fuzzy lookups** — when you don't know exact field or value
2. **Use aggregate for dashboards** — faster than fetching all records and computing locally
3. **Use group_by for distributions** — understand data breakdown by category
4. **Combine where clauses** — use ~and/~or for complex filters
5. **Limit raw queries** — always set a reasonable limit
6. **Use fields parameter** — request only needed columns for better performance
7. **Paginate large results** — use limit + offset instead of fetching everything at once
