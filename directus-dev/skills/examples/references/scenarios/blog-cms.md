# Scenario: Blog CMS

Complete schema build for a blog CMS with posts, authors, categories, and tags.

## Collections

| Collection | Purpose | Type |
|-----------|---------|------|
| `authors` | Blog authors | Independent |
| `categories` | Post categories | Independent |
| `tags` | Content tags | Independent |
| `posts` | Blog posts | Dependent (has relations) |
| `posts_categories` | Junction: posts ↔ categories | Junction (M2M) |
| `posts_tags` | Junction: posts ↔ tags | Junction (M2M) |

## Step 1: Create Independent Collections

```json
Tool: collections
Input: {
  "action": "create",
  "data": [
    {
      "collection": "authors",
      "schema": {},
      "meta": { "icon": "person", "display_template": "{{first_name}} {{last_name}}" }
    },
    {
      "collection": "categories",
      "schema": {},
      "meta": { "icon": "category", "display_template": "{{name}}" }
    },
    {
      "collection": "tags",
      "schema": {},
      "meta": { "icon": "label", "display_template": "{{name}}" }
    }
  ]
}
```

## Step 2: Add Fields to Authors

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "authors",
  "data": [
    { "field": "first_name", "type": "string", "meta": { "interface": "input", "width": "half" }, "schema": { "is_nullable": false } },
    { "field": "last_name", "type": "string", "meta": { "interface": "input", "width": "half" }, "schema": { "is_nullable": false } },
    { "field": "email", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "bio", "type": "text", "meta": { "interface": "input-rich-text-md" } },
    { "field": "avatar", "type": "uuid", "meta": { "interface": "file-image", "special": ["file"], "display": "image" } }
  ]
}
```

Create file relation for avatar:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "authors",
  "field": "avatar",
  "data": {
    "collection": "authors",
    "field": "avatar",
    "related_collection": "directus_files",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

## Step 3: Add Fields to Categories

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "categories",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "slug", "type": "string", "meta": { "interface": "input", "options": { "slug": true } }, "schema": { "is_unique": true } },
    { "field": "description", "type": "text", "meta": { "interface": "input-multiline" } }
  ]
}
```

## Step 4: Add Fields to Tags

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "tags",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false, "is_unique": true } },
    { "field": "slug", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } }
  ]
}
```

## Step 5: Create Posts Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "posts",
    "schema": {},
    "meta": {
      "icon": "article",
      "display_template": "{{title}}",
      "sort_field": "sort",
      "archive_field": "status",
      "archive_value": "archived",
      "unarchive_value": "draft",
      "versioning": true
    }
  }]
}
```

## Step 6: Add Fields to Posts

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [
    { "field": "title", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "slug", "type": "string", "meta": { "interface": "input", "options": { "slug": true } }, "schema": { "is_unique": true } },
    { "field": "excerpt", "type": "text", "meta": { "interface": "input-multiline" } },
    { "field": "content", "type": "text", "meta": { "interface": "input-rich-text-md" } },
    { "field": "featured_image", "type": "uuid", "meta": { "interface": "file-image", "special": ["file"], "display": "image" } },
    { "field": "status", "type": "string", "meta": { "interface": "select-dropdown", "options": { "choices": [{"text": "Draft", "value": "draft"}, {"text": "Published", "value": "published"}, {"text": "Archived", "value": "archived"}] } }, "schema": { "default_value": "draft" } },
    { "field": "published_date", "type": "datetime", "meta": { "interface": "datetime", "display": "datetime" } },
    { "field": "sort", "type": "integer", "meta": { "interface": "input", "hidden": true } },
    { "field": "user_created", "type": "uuid", "meta": { "special": ["user-created"], "interface": "select-dropdown-m2o", "readonly": true, "hidden": true } },
    { "field": "date_created", "type": "timestamp", "meta": { "special": ["date-created"], "interface": "datetime", "readonly": true, "hidden": true } },
    { "field": "user_updated", "type": "uuid", "meta": { "special": ["user-updated"], "interface": "select-dropdown-m2o", "readonly": true, "hidden": true } },
    { "field": "date_updated", "type": "timestamp", "meta": { "special": ["date-updated"], "interface": "datetime", "readonly": true, "hidden": true } }
  ]
}
```

## Step 7: Add M2O Relation (Posts → Authors)

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "field": "author",
    "type": "uuid",
    "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"], "display": "related-values", "display_options": { "template": "{{first_name}} {{last_name}}" } }
  }]
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "author",
  "data": {
    "collection": "posts",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

Featured image relation:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "featured_image",
  "data": {
    "collection": "posts",
    "field": "featured_image",
    "related_collection": "directus_files",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

## Step 8: Create M2M Junction Tables

### posts_categories

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{ "collection": "posts_categories", "schema": {}, "meta": { "hidden": true, "icon": "import_export" } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts_categories",
  "data": [
    { "field": "posts_id", "type": "uuid", "meta": { "hidden": true } },
    { "field": "categories_id", "type": "uuid", "meta": { "hidden": true } }
  ]
}
```

Add alias fields:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{ "field": "categories", "type": "alias", "meta": { "interface": "list-m2m", "special": ["m2m"], "display": "related-values", "display_options": { "template": "{{categories_id.name}}" } } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "categories",
  "data": [{ "field": "posts", "type": "alias", "meta": { "interface": "list-m2m", "special": ["m2m"], "display": "related-values" } }]
}
```

Create relations:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_categories",
  "field": "posts_id",
  "data": { "collection": "posts_categories", "field": "posts_id", "related_collection": "posts", "schema": { "on_delete": "CASCADE" }, "meta": { "one_field": "categories", "junction_field": "categories_id" } }
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_categories",
  "field": "categories_id",
  "data": { "collection": "posts_categories", "field": "categories_id", "related_collection": "categories", "schema": { "on_delete": "CASCADE" }, "meta": { "one_field": "posts", "junction_field": "posts_id" } }
}
```

### posts_tags (same pattern)

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{ "collection": "posts_tags", "schema": {}, "meta": { "hidden": true, "icon": "import_export" } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts_tags",
  "data": [
    { "field": "posts_id", "type": "uuid", "meta": { "hidden": true } },
    { "field": "tags_id", "type": "uuid", "meta": { "hidden": true } }
  ]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{ "field": "tags", "type": "alias", "meta": { "interface": "list-m2m", "special": ["m2m"], "display": "related-values", "display_options": { "template": "{{tags_id.name}}" } } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "tags",
  "data": [{ "field": "posts", "type": "alias", "meta": { "interface": "list-m2m", "special": ["m2m"], "display": "related-values" } }]
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_tags",
  "field": "posts_id",
  "data": { "collection": "posts_tags", "field": "posts_id", "related_collection": "posts", "schema": { "on_delete": "CASCADE" }, "meta": { "one_field": "tags", "junction_field": "tags_id" } }
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_tags",
  "field": "tags_id",
  "data": { "collection": "posts_tags", "field": "tags_id", "related_collection": "tags", "schema": { "on_delete": "CASCADE" }, "meta": { "one_field": "posts", "junction_field": "posts_id" } }
}
```

## Step 9: Create Sample Data

```json
Tool: items
Input: {
  "action": "create",
  "collection": "authors",
  "data": [
    { "first_name": "Jane", "last_name": "Doe", "email": "jane@example.com", "bio": "Senior tech writer." },
    { "first_name": "John", "last_name": "Smith", "email": "john@example.com", "bio": "Full-stack developer and blogger." }
  ]
}
```

```json
Tool: items
Input: {
  "action": "create",
  "collection": "categories",
  "data": [
    { "name": "Technology", "slug": "technology" },
    { "name": "Design", "slug": "design" },
    { "name": "Business", "slug": "business" }
  ]
}
```

```json
Tool: items
Input: {
  "action": "create",
  "collection": "tags",
  "data": [
    { "name": "JavaScript", "slug": "javascript" },
    { "name": "CSS", "slug": "css" },
    { "name": "API", "slug": "api" }
  ]
}
```

```json
Tool: items
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "title": "Getting Started with Directus",
    "slug": "getting-started-directus",
    "excerpt": "Learn how to set up and use Directus as your headless CMS.",
    "content": "# Getting Started\n\nDirectus is an open-source headless CMS...",
    "status": "published",
    "published_date": "2024-06-15T10:00:00",
    "author": "AUTHOR_UUID_HERE"
  }]
}
```

## Step 10: Verify

```json
Tool: items
Input: {
  "action": "read",
  "collection": "posts",
  "query": {
    "fields": ["title", "status", "author.first_name", "author.last_name", "categories.categories_id.name", "tags.tags_id.name"],
    "limit": 10
  }
}
```
