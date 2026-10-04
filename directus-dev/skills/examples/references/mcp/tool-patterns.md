# MCP Tool Patterns — Exact JSON Reference

Complete parameter reference for every Directus MCP tool and action.

## system-prompt

```text
Tool: system-prompt
Input: {}
```

No parameters. Returns role context and instance-specific guidance.

## schema

### Discovery Mode

```text
Tool: schema
Input: {}
```

Returns: `{ collections: [...], collection_folders: [...], notes: {...} }`

### Detailed Mode

```text
Tool: schema
Input: { "keys": ["posts", "categories"] }
```

Returns: field definitions, types, validation rules, defaults, and relationship mappings.

## collections

### Create

```text
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "articles",
    "schema": {},
    "meta": {
      "icon": "article",
      "note": "Blog articles",
      "color": "#2196F3",
      "display_template": "{{title}}",
      "sort_field": "sort",
      "accountability": "all",
      "archive_field": "status",
      "archive_value": "archived",
      "unarchive_value": "draft"
    }
  }]
}
```

### Create Folder (no table)

```text
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "content_group",
    "schema": null,
    "meta": { "icon": "folder", "color": "#4CAF50" }
  }]
}
```

### Read

```text
Tool: collections
Input: { "action": "read" }
```

### Read Specific

```text
Tool: collections
Input: { "action": "read", "keys": ["articles"] }
```

### Update

```text
Tool: collections
Input: {
  "action": "update",
  "data": [{
    "collection": "articles",
    "meta": { "icon": "newspaper", "singleton": false, "versioning": true }
  }]
}
```

### Delete

```text
Tool: collections
Input: { "action": "delete", "keys": ["old_collection"] }
```

## fields

### Create

```text
Tool: fields
Input: {
  "action": "create",
  "collection": "articles",
  "data": [
    {
      "field": "title",
      "type": "string",
      "meta": { "interface": "input", "required": true, "note": "Article title" },
      "schema": { "is_nullable": false }
    },
    {
      "field": "content",
      "type": "text",
      "meta": { "interface": "input-rich-text-md" }
    },
    {
      "field": "published_date",
      "type": "datetime",
      "meta": { "interface": "datetime", "display": "datetime", "width": "half" }
    },
    {
      "field": "featured",
      "type": "boolean",
      "meta": { "interface": "boolean", "width": "half" },
      "schema": { "default_value": false }
    },
    {
      "field": "tags",
      "type": "json",
      "meta": { "interface": "tags" }
    }
  ]
}
```

### Read All Fields for Collection

```text
Tool: fields
Input: { "action": "read", "collection": "articles" }
```

### Read Specific Field

```text
Tool: fields
Input: { "action": "read", "collection": "articles", "field": "title" }
```

### Update

```text
Tool: fields
Input: {
  "action": "update",
  "collection": "articles",
  "data": [{
    "field": "title",
    "meta": { "note": "Updated note", "width": "full" }
  }]
}
```

### Delete

```text
Tool: fields
Input: { "action": "delete", "collection": "articles", "field": "deprecated_field" }
```

## relations

### Create M2O

```text
Tool: relations
Input: {
  "action": "create",
  "collection": "articles",
  "field": "author",
  "data": {
    "collection": "articles",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

### Create M2M (junction)

```text
Tool: relations
Input: {
  "action": "create",
  "collection": "articles_tags",
  "field": "articles_id",
  "data": {
    "collection": "articles_tags",
    "field": "articles_id",
    "related_collection": "articles",
    "schema": { "on_delete": "CASCADE" },
    "meta": { "one_field": "tags", "junction_field": "tags_id" }
  }
}
```

### Read

```text
Tool: relations
Input: { "action": "read" }
```

### Read for Specific Collection

```text
Tool: relations
Input: { "action": "read", "collection": "articles" }
```

### Delete

```text
Tool: relations
Input: { "action": "delete", "collection": "articles", "field": "author" }
```

## items

### Create

```text
Tool: items
Input: {
  "action": "create",
  "collection": "articles",
  "data": [
    { "title": "Article 1", "content": "Content...", "status": "draft" },
    { "title": "Article 2", "content": "Content...", "status": "published" }
  ]
}
```

### Read (with full query)

```text
Tool: items
Input: {
  "action": "read",
  "collection": "articles",
  "query": {
    "fields": ["id", "title", "status", "author.first_name", "tags.tags_id.name"],
    "filter": {
      "_and": [
        { "status": { "_eq": "published" } },
        { "date_created": { "_gte": "2024-01-01" } }
      ]
    },
    "sort": ["-date_created"],
    "limit": 25,
    "offset": 0,
    "search": "optional search term",
    "deep": {
      "tags": { "_limit": 10 }
    }
  }
}
```

### Update

```text
Tool: items
Input: {
  "action": "update",
  "collection": "articles",
  "keys": ["uuid-1", "uuid-2"],
  "data": { "status": "archived" }
}
```

### Delete

```text
Tool: items
Input: {
  "action": "delete",
  "collection": "articles",
  "keys": ["uuid-1"]
}
```

### Aggregate

```text
Tool: items
Input: {
  "action": "read",
  "collection": "orders",
  "query": {
    "aggregate": { "count": ["*"], "sum": ["total"], "avg": ["total"], "min": ["total"], "max": ["total"] },
    "groupBy": ["status"],
    "filter": { "date_created": { "_gte": "2024-01-01" } }
  }
}
```

## files

### Import

```text
Tool: files
Input: {
  "action": "import",
  "data": [{
    "url": "https://example.com/image.jpg",
    "file": {
      "title": "Hero Image",
      "description": "Homepage hero",
      "tags": ["hero", "homepage"],
      "folder": "folder-uuid"
    }
  }]
}
```

### Read

```text
Tool: files
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "title", "type", "filesize", "width", "height"],
    "filter": { "type": { "_starts_with": "image/" } },
    "sort": ["-uploaded_on"],
    "limit": 25
  }
}
```

### Update

```text
Tool: files
Input: {
  "action": "update",
  "keys": ["file-uuid"],
  "data": [{ "title": "New Title", "tags": ["updated"] }]
}
```

### Delete

```text
Tool: files
Input: { "action": "delete", "keys": ["file-uuid"] }
```

## assets

```text
Tool: assets
Input: { "id": "file-uuid" }
```

Returns: `{ "data": "base64...", "mimeType": "image/jpeg" }`

## folders

### Create

```text
Tool: folders
Input: {
  "action": "create",
  "data": [
    { "name": "Images", "parent": null },
    { "name": "Documents", "parent": null }
  ]
}
```

### Read

```text
Tool: folders
Input: { "action": "read", "query": { "fields": ["id", "name", "parent"], "sort": ["name"] } }
```

## flows

### Create

```text
Tool: flows
Input: {
  "action": "create",
  "data": {
    "name": "On New Post",
    "trigger": "event",
    "status": "active",
    "options": {
      "type": "action",
      "scope": ["items.create"],
      "collections": ["posts"]
    }
  }
}
```

### Read

```text
Tool: flows
Input: {
  "action": "read",
  "query": { "fields": ["id", "name", "status", "trigger", "description"] }
}
```

## operations

### Create

```text
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "flow-uuid",
    "key": "log_event",
    "type": "log",
    "name": "Log Trigger Data",
    "options": { "message": "Trigger: {{ $trigger }}" },
    "position_x": 20,
    "position_y": 1,
    "resolve": null,
    "reject": null
  }
}
```

## trigger-flow

```text
Tool: trigger-flow
Input: {
  "id": "flow-uuid",
  "collection": "posts",
  "keys": ["item-uuid"],
  "data": { "custom": "payload" }
}
```
