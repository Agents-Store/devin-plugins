---
name: schema-design
description: Schema design best practices — data modeling, collection planning, system fields, display templates, singletons, folders, versioning. This skill should be used when the user asks to design a data model, plan collections, create a database schema, or build a CMS/e-commerce/project database structure in Directus.
---

# Schema Design

Best practices for designing Directus data models using the `collections`, `fields`, and `schema` MCP tools.

## Design Approach

1. **Explore first** — Use `schema` tool (discovery mode) to see existing collections
2. **Plan on paper** — List entities, fields, and relationships before building
3. **Build in order** — Follow the creation order below strictly
4. **Verify** — Use `schema` tool (detailed mode) to confirm structure

## Creation Order (Critical)

Build schema in this exact order to avoid dependency errors:

1. **Collection folders** — UI-only grouping (optional)
2. **Independent collections** — No foreign key dependencies (categories, tags, statuses)
3. **Dependent collections** — Main entities that reference other collections (posts, products)
4. **Junction collections** — For M2M relationships (posts_tags, product_categories)
5. **Basic fields** — Non-relational fields (string, text, integer, boolean, etc.)
6. **Relational fields** — M2O uuid fields, O2M/M2M alias fields
7. **Relations** — Define relationships after both collections and fields exist
8. **Sample data** — Create test items to verify schema

## Creating a Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "articles",
    "schema": {},
    "meta": {
      "icon": "article",
      "note": "Blog articles collection",
      "color": "#2196F3",
      "sort_field": "sort",
      "archive_field": "status",
      "archive_value": "archived",
      "unarchive_value": "draft",
      "display_template": "{{title}}",
      "accountability": "all"
    }
  }]
}
```

### Schema Rules

- `"schema": {}` — real database table
- `"schema": null` — folder-only (no table, just UI grouping)

### Collection Folders

Group collections in the sidebar:

```json
{
  "action": "create",
  "data": [{
    "collection": "content",
    "schema": null,
    "meta": {
      "icon": "folder",
      "note": "Content-related collections",
      "color": "#4CAF50"
    }
  }]
}
```

Then assign collections to the folder:

```json
Tool: collections
Input: {
  "action": "update",
  "data": [{
    "collection": "articles",
    "meta": { "group": "content" }
  }]
}
```

## System Fields

Add these recommended fields to every content collection:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `uuid` | Primary key (auto-generated on collection create) |
| `status` | `string` | Workflow status (draft/published/archived) |
| `sort` | `integer` | Manual sort order |
| `user_created` | `uuid` | Auto-tracked creator (system field) |
| `user_updated` | `uuid` | Auto-tracked last editor (system field) |
| `date_created` | `timestamp` | Auto-tracked creation date (system field) |
| `date_updated` | `timestamp` | Auto-tracked update date (system field) |

### Adding System Fields

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "articles",
  "data": [
    {
      "field": "status",
      "type": "string",
      "meta": {
        "interface": "select-dropdown",
        "options": {
          "choices": [
            { "text": "Draft", "value": "draft" },
            { "text": "Published", "value": "published" },
            { "text": "Archived", "value": "archived" }
          ]
        },
        "display": "labels",
        "width": "half"
      },
      "schema": { "default_value": "draft", "is_nullable": false }
    },
    {
      "field": "sort",
      "type": "integer",
      "meta": { "interface": "input", "hidden": true }
    },
    {
      "field": "user_created",
      "type": "uuid",
      "meta": {
        "special": ["user-created"],
        "interface": "select-dropdown-m2o",
        "display": "user",
        "readonly": true,
        "hidden": true,
        "width": "half"
      }
    },
    {
      "field": "date_created",
      "type": "timestamp",
      "meta": {
        "special": ["date-created"],
        "interface": "datetime",
        "display": "datetime",
        "readonly": true,
        "hidden": true,
        "width": "half"
      }
    },
    {
      "field": "user_updated",
      "type": "uuid",
      "meta": {
        "special": ["user-updated"],
        "interface": "select-dropdown-m2o",
        "display": "user",
        "readonly": true,
        "hidden": true,
        "width": "half"
      }
    },
    {
      "field": "date_updated",
      "type": "timestamp",
      "meta": {
        "special": ["date-updated"],
        "interface": "datetime",
        "display": "datetime",
        "readonly": true,
        "hidden": true,
        "width": "half"
      }
    }
  ]
}
```

## Singleton Collections

For global settings, site config, or any single-record collection:

```json
{
  "action": "create",
  "data": [{
    "collection": "site_settings",
    "schema": {},
    "meta": {
      "singleton": true,
      "icon": "settings",
      "note": "Global site configuration"
    }
  }]
}
```

Singletons show as a single form (no list view) in the Directus app.

## Content Versioning

Enable version tracking for editorial workflows:

```json
Tool: collections
Input: {
  "action": "update",
  "data": [{
    "collection": "articles",
    "meta": { "versioning": true }
  }]
}
```

Allows creating content versions (drafts) before publishing changes.

## Display Templates

Control how items appear in relation dropdowns and lists:

```json
"meta": {
  "display_template": "{{title}} — {{author.first_name}} {{author.last_name}}"
}
```

Supports field references with `{{field_name}}` and relation traversal with dot notation.

## Archive Pattern

Soft-delete pattern using archive fields:

```json
"meta": {
  "archive_field": "status",
  "archive_value": "archived",
  "unarchive_value": "draft",
  "archive_app_filter": true
}
```

When `archive_app_filter: true`, archived items are hidden by default in the app.

## Common Design Patterns

### Blog CMS

| Collection | Key Fields | Relations |
|-----------|------------|-----------|
| `authors` | name, bio, avatar, email | — |
| `categories` | name, slug, description | — |
| `tags` | name, slug | — |
| `posts` | title, slug, content, excerpt, featured_image, status | M2O → authors, M2M ↔ categories, M2M ↔ tags |
| `posts_categories` | (junction) | M2O → posts, M2O → categories |
| `posts_tags` | (junction) | M2O → posts, M2O → tags |

### E-Commerce

| Collection | Key Fields | Relations |
|-----------|------------|-----------|
| `brands` | name, logo, description | — |
| `categories` | name, slug, parent | Self-referencing M2O |
| `products` | name, sku, price, description, status | M2O → brands, M2M ↔ categories |
| `variants` | sku, price, stock, attributes | M2O → products |
| `orders` | number, total, status, customer_email | — |
| `order_items` | quantity, price | M2O → orders, M2O → variants |

### Project Management

| Collection | Key Fields | Relations |
|-----------|------------|-----------|
| `projects` | name, description, status, deadline | — |
| `tasks` | title, description, priority, status, due_date | M2O → projects, M2O → directus_users (assignee) |
| `comments` | text, date | M2O → tasks, M2O → directus_users |
| `labels` | name, color | — |
| `tasks_labels` | (junction) | M2O → tasks, M2O → labels |

## Primary Key Guidance

- **UUID** (recommended) — Generated automatically, globally unique, best for distributed systems
- **Auto-increment integer** — Simpler, readable IDs, but less portable

Directus creates a UUID `id` field by default when you create a collection.

## Common Mistakes

1. **Creating relations before collections exist** — Both collections must exist first
2. **Wrong creation order** — Independent collections first, then dependent, then junction
3. **Everything in one collection** — Normalize data; use relations instead of JSON fields for structured data
4. **Missing system fields** — Always add status, user_created, date_created for content collections
5. **No display templates** — Set `display_template` so items are recognizable in relation dropdowns
6. **Forgetting archive pattern** — Use archive fields for soft-delete instead of actual deletion
7. **Not using collection folders** — Organize collections in folders for large projects
