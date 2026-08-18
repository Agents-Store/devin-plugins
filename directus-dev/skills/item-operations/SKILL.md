---
name: item-operations
description: Item CRUD operations — create, read, update, delete items, filtering, sorting, deep queries, aggregation, batch operations. This skill should be used when the user asks to create, read, update, or delete items, filter or search data, query with relations, aggregate values, or perform batch operations in Directus.
---

# Item Operations

Complete reference for the `items` MCP tool — the most frequently used Directus tool.

## The Items Tool

Single tool with action parameter for all CRUD operations:

```
action: "create" | "read" | "update" | "delete"
```

**Critical rules:**
- `data` for create is ALWAYS an array, even for a single item
- Always read the schema before creating items (to know required fields and types)
- Use `fields` in queries to control response size

## Reading Items

### Basic List

```json
{
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["id", "title", "status", "date_created"],
    "limit": 25
  }
}
```

### With Filters

```json
{
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["*"],
    "filter": {
      "status": { "_eq": "published" },
      "date_created": { "_gte": "2024-01-01" }
    },
    "sort": ["-date_created"],
    "limit": 50
  }
}
```

### Complex Filter (AND/OR)

```json
{
  "action": "read",
  "collection": "products",
  "query": {
    "filter": {
      "_and": [
        { "status": { "_eq": "active" } },
        { "_or": [
          { "price": { "_lt": 50 } },
          { "featured": { "_eq": true } }
        ]}
      ]
    }
  }
}
```

### With Relations (dot notation)

```json
{
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["title", "author.first_name", "author.last_name", "category.name"],
    "limit": 10
  }
}
```

### Deep Queries (nested relation filtering)

```json
{
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["title", "comments.text", "comments.user.name"],
    "deep": {
      "comments": {
        "_filter": { "status": { "_eq": "approved" } },
        "_sort": ["-date_created"],
        "_limit": 5
      }
    }
  }
}
```

### Full-Text Search

```json
{
  "action": "read",
  "collection": "articles",
  "query": {
    "search": "machine learning",
    "fields": ["id", "title", "excerpt"],
    "limit": 20
  }
}
```

### Aggregation

```json
{
  "action": "read",
  "collection": "orders",
  "query": {
    "aggregate": {
      "count": ["*"],
      "sum": ["total"],
      "avg": ["total"]
    }
  }
}
```

### Aggregation with GroupBy

```json
{
  "action": "read",
  "collection": "orders",
  "query": {
    "aggregate": { "count": ["*"], "sum": ["total"] },
    "groupBy": ["status"]
  }
}
```

### Pagination

```json
{
  "action": "read",
  "collection": "products",
  "query": {
    "fields": ["id", "name", "price"],
    "limit": 25,
    "offset": 50
  }
}
```

Or page-based:

```json
{
  "action": "read",
  "collection": "products",
  "query": {
    "fields": ["id", "name", "price"],
    "limit": 25,
    "page": 3
  }
}
```

### M2A Field Selection

For Many-to-Any (polymorphic) relations, select fields per type:

```json
{
  "action": "read",
  "collection": "pages",
  "query": {
    "fields": [
      "title",
      "sections.item:headings.title",
      "sections.item:paragraphs.body",
      "sections.item:images.file"
    ]
  }
}
```

## Creating Items

### Single Item

```json
{
  "action": "create",
  "collection": "posts",
  "data": [{
    "title": "Getting Started with Directus",
    "content": "Directus is an open-source headless CMS...",
    "status": "draft"
  }]
}
```

### Batch Create

```json
{
  "action": "create",
  "collection": "tags",
  "data": [
    { "name": "JavaScript", "color": "#F7DF1E" },
    { "name": "TypeScript", "color": "#3178C6" },
    { "name": "Python", "color": "#3776AB" }
  ]
}
```

### Create with Inline Relations

Create related items in the same call:

```json
{
  "action": "create",
  "collection": "posts",
  "data": [{
    "title": "New Post",
    "author": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "categories": [1, 2, { "name": "New Category" }],
    "status": "draft"
  }]
}
```

This creates the post, a new author, and a new category — linking existing categories 1 and 2 and the new one.

## Updating Items

### Update by Keys

```json
{
  "action": "update",
  "collection": "posts",
  "keys": ["550e8400-e29b-41d4-a716-446655440000"],
  "data": {
    "status": "published",
    "date_published": "2024-06-15"
  }
}
```

### Batch Update (same changes to multiple items)

```json
{
  "action": "update",
  "collection": "posts",
  "keys": ["uuid-1", "uuid-2", "uuid-3"],
  "data": { "status": "archived" }
}
```

## Deleting Items

```json
{
  "action": "delete",
  "collection": "posts",
  "keys": ["uuid-1", "uuid-2"]
}
```

**Note:** Delete must be enabled in Directus MCP settings (Settings > AI > MCP > Allow Deletes). It is disabled by default.

## Common Workflows

### Search and Update

1. Find items matching criteria:
```json
{ "action": "read", "collection": "products", "query": { "filter": { "stock": { "_lt": 5 } }, "fields": ["id", "name", "stock"] } }
```

2. Update found items:
```json
{ "action": "update", "collection": "products", "keys": ["id-1", "id-2"], "data": { "status": "low_stock" } }
```

### Import External Data

1. Read schema to understand fields: `schema` tool with `keys: ["target_collection"]`
2. Map external data to Directus fields
3. Batch create in groups of 25:
```json
{ "action": "create", "collection": "products", "data": [/* batch of items */] }
```

### Filtered Report

```json
{
  "action": "read",
  "collection": "orders",
  "query": {
    "filter": {
      "date_created": { "_between": ["2024-01-01", "2024-03-31"] }
    },
    "aggregate": { "count": ["*"], "sum": ["total"], "avg": ["total"] },
    "groupBy": ["status"]
  }
}
```

## Best Practices

- Always read the collection schema before creating items
- Use `fields` to select only needed data — never fetch `["*"]` on large collections
- Filter and sort server-side, not after fetching
- Paginate results: use `limit: 25` as default, increase only when needed
- For batch operations, process 10-25 items per call
- Verify write results by reading back the created/updated items
- Use `search` for user-facing text search, `filter` for programmatic queries
- Use `deep` for filtering nested relation data instead of filtering in code
